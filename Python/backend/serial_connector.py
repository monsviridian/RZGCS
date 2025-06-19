"""
Serial Connector für MAVLink-Verbindungen und Simulatoren.
Verwaltet die Verbindung zum Fluggerät oder Simulator.

Verwendet den neuen MAVLinkHandler für eine saubere MAVLink-Kommunikation.
"""

import sys
import os
import platform
from PySide6.QtCore import QObject, Signal, Slot, Property, QTimer
import serial.tools.list_ports
import math
from PySide6.QtSerialPort import QSerialPort, QSerialPortInfo
import time
import asyncio
from typing import Dict, Any, List, Optional
from PySide6.QtQml import QmlElement

# Importiere den neuen MAVLinkHandler für die MAVLink-Kommunikation
from backend.mavlink_handler import MAVLinkHandler

# Telemetrie-Logger-Integration importieren
from backend.telemetry_logger_integration import TelemetryLoggerIntegration

# Erweiterte Connection-Management-Komponenten
from backend.connection.connection_security import ConnectionSecurity
from backend.connection.connection_manager import ConnectionManager
from backend.connection.connection_types import ConnectionType
from backend.connection.bandwidth_manager import BandwidthManager

# MVVM Services importieren
from backend.connection.services.connection_service import ConnectionService
from backend.flight_control.services.telemetry_service import TelemetryService
from backend.telemetry_logger_integration import TelemetryLoggerIntegration
from backend.logger import Logger
from backend.parameter_model import ParameterTableModel
from backend.parameter_manager import ParameterManager

# QML Import Definitionen
QML_IMPORT_NAME = "SerialConnector"
QML_IMPORT_MAJOR_VERSION = 1

@QmlElement
class SerialConnector(QObject):
    # Signals
    connectedChanged = Signal(bool)
    connectionStatusChanged = Signal(int)  # 0=disconnected, 1=connecting, 2=connected
    errorOccurred = Signal(str)
    availablePortsChanged = Signal(list)
    availableBaudRatesChanged = Signal(list)
    attitudeUpdated = Signal(float, float, float)  # roll, pitch, yaw
    gpsUpdated = Signal(float, float, float)  # lat, lon, alt
    batteryUpdated = Signal(float, float, float)  # voltage, current, remaining

    def __init__(self, sensor_model=None, logger=None, parameter_model=None):
        super().__init__()
        self._sensor_model = sensor_model
        self._parameter_model = parameter_model
        self._logger = logger or Logger()
        self._connected = False
        self._connecting = False
        self._port = ""
        self._baud_rate = 115200
        self._available_ports = ["Simulator"]
        self._available_baud_rates = [1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600]
        
        # MAVLink-Handler initialisieren
        self._mavlink_handler = MAVLinkHandler()
        
        # Verbinde MAVLink-Handler Signale
        self._mavlink_handler.connection_state_changed.connect(self._on_connection_status_changed)
        
        # Weitere Komponenten
        self._connection_manager = ConnectionManager()
        self._connection_security = ConnectionSecurity()
        self._bandwidth_manager = BandwidthManager()
        self._connection_service = ConnectionService()
        # TelemetryService benötigt Parameter, die wir aktuell nicht bereitstellen können
        # TODO: TelemetryService mit korrekten Parametern initialisieren
        self._telemetry_service = None
        self._telemetry_logger_integration = TelemetryLoggerIntegration()
        self._parameter_manager = ParameterManager(self._parameter_model, self._logger)

        # Lade initial die verfügbaren Ports
        self.load_ports()

    @Slot(str, result=bool)
    def establish_serial_connection(self, conn_string=None):
        """Establishes a MAVLink connection to the selected port."""
        if self._connecting:
            self._logger.addLog("Ein Verbindungsversuch läuft bereits. Bitte warten...")
            return False
            
        self._connecting = True
        self.connectionStatusChanged.emit(1)  # connecting
        
        try:
            # Parse connection parameters
            if conn_string and isinstance(conn_string, str):
                if ':' in conn_string:
                    parts = conn_string.split(':', 1)
                    self._port = parts[0].strip()
                    try:
                        self._baud_rate = int(parts[1].strip())
                    except ValueError:
                        self._baud_rate = 115200
                else:
                    self._port = conn_string.strip()
            
            if not self._port:
                self._logger.addLog("[ERR] Kein Port ausgewählt")
                self._connecting = False
                return False

            # Prüfe ob der Port verfügbar ist
            if self._port != "Simulator" and self._port not in self._available_ports:
                self._logger.addLog(f"[ERR] Port {self._port} nicht verfügbar")
                return False

            # Verbindung über MAVLink-Handler herstellen
            success = self._mavlink_handler.connect(self._port, self._baud_rate)
            if success:
                self._connected = True
                self.connectedChanged.emit(True)
                self.connectionStatusChanged.emit(2)  # connected
                self._logger.addLog(f"[OK] Verbunden mit {self._port}")
            return success
                
        except Exception as e:
            error_msg = f"Verbindungsfehler: {str(e)}"
            self._logger.addLog(f"[ERR] {error_msg}")
            self.errorOccurred.emit(error_msg)
            self._connected = False
            self.connectedChanged.emit(False)
            self.connectionStatusChanged.emit(0)  # disconnected
            return False
            
        finally:
            self._connecting = False

    @Slot()
    def disconnect(self):
        """Trennt die MAVLink-Verbindung"""
        self._mavlink_handler.disconnect()
        self._connected = False
        self.connectedChanged.emit(False)
        self.connectionStatusChanged.emit(0)  # disconnected
        self._logger.addLog("[INFO] Verbindung getrennt")

    @Slot()
    def load_ports(self):
        """Lädt die verfügbaren seriellen Ports"""
        try:
            self._logger.addLog("[DEBUG] Starte Port-Scan...")
            ports = ["Simulator"]  # Simulator immer als erste Option
            
            # Verwende QSerialPortInfo für die Port-Erkennung
            self._logger.addLog("[DEBUG] Suche Ports mit QSerialPortInfo...")
            try:
                for port in QSerialPortInfo.availablePorts():
                    port_name = port.portName()
                    if port_name not in ports:
                        ports.append(port_name)
                        self._logger.addLog(f"[PORT-DEBUG] Port gefunden (QSerialPortInfo): {port_name} ({port.description()})")
            except Exception as e:
                self._logger.addLog(f"[WARN] Fehler bei QSerialPortInfo: {str(e)}")
            
            # Zusätzlich auch serial.tools.list_ports verwenden
            self._logger.addLog("[DEBUG] Suche Ports mit serial.tools.list_ports...")
            try:
                for port in serial.tools.list_ports.comports():
                    if port.device not in ports:
                        ports.append(port.device)
                        self._logger.addLog(f"[PORT-DEBUG] Port gefunden (serial.tools): {port.device} ({port.description})")
            except Exception as e:
                self._logger.addLog(f"[WARN] Fehler bei serial.tools.list_ports: {str(e)}")
            
            # Prüfe auf leere Port-Liste
            if len(ports) == 1 and ports[0] == "Simulator":
                self._logger.addLog("[WARN] Keine seriellen Ports gefunden")
            
            self._logger.addLog(f"[PORT-DEBUG] Alle gefundenen Ports: {ports}")
            self._available_ports = ports
            self.availablePortsChanged.emit(ports)
            
        except Exception as e:
            self._logger.addLog(f"[ERR] Fehler beim Laden der Ports: {str(e)}")
            import traceback
            self._logger.addLog(f"[ERR] Stacktrace: {traceback.format_exc()}")

    # Properties
    @Property(bool, notify=connectedChanged)
    def connected(self):
        return self._connected
        
    @Property(str)
    def port(self):
        return self._port
    
    @Slot(str)
    def setPort(self, port):
        """Setzt den zu verwendenden Port"""
        self._port = port
        self._logger.addLog(f"Port gesetzt auf: {port}")
        
    @Property(int)
    def baud_rate(self):
        return self._baud_rate
    
    @Slot(int)
    def setBaudRate(self, baud_rate):
        """Setzt die zu verwendende Baudrate"""
        self._baud_rate = baud_rate
        self._logger.addLog(f"Baudrate gesetzt auf: {baud_rate}")

    @Property('QVariantList', notify=availablePortsChanged)
    def availablePorts(self):
        return self._available_ports

    @Property('QVariantList', notify=availableBaudRatesChanged)
    def availableBaudRates(self):
        return self._available_baud_rates
        
    def get_message_handler(self):
        """Gibt den MAVLinkHandler zurück für externe Komponenten"""
        return self._mavlink_handler
        
    def get_mavlink_connection(self):
        """Gibt die MAVLink-Verbindung (mavutil.mavlink_connection) zurück für externe Komponenten"""
        if self._mavlink_handler:
            return self._mavlink_handler.get_mavlink_connection()
        return None

    def _on_connection_status_changed(self, connected: bool):
        """Handler für MAVLink-Verbindungsstatus-Änderungen"""
        self._connected = connected
        self.connectedChanged.emit(connected)
        self.connectionStatusChanged.emit(2 if connected else 0)
        if connected:
            self._logger.addLog("[OK] MAVLink-Verbindung hergestellt")
        else:
            self._logger.addLog("[INFO] MAVLink-Verbindung getrennt")

    def _on_error_occurred(self, error_msg: str):
        """Handler für MAVLink-Fehler"""
        self._logger.addLog(f"[ERR] {error_msg}")
        self.errorOccurred.emit(error_msg)
    
    def register_telemetry_viewmodel(self, telemetry_viewmodel):
        """Registriert ein TelemetryViewModel für Telemetrie-Updates
        
        Args:
            telemetry_viewmodel: Eine Instanz von TelemetryViewModel
            
        Returns:
            bool: True wenn erfolgreich registriert, False sonst
        """
        try:
            self._logger.addLog("[INFO] Registriere TelemetryViewModel")
            
            # Verbinde die Signale des MAVLinkHandlers mit dem TelemetryViewModel
            if self._mavlink_handler:
                # Verbinde Attitude-Signal
                self.attitudeUpdated.connect(telemetry_viewmodel.set_attitude)
                
                # Verbinde GPS-Signal
                self.gpsUpdated.connect(telemetry_viewmodel.set_gps_position)
                
                # Verbinde Battery-Signal
                self.batteryUpdated.connect(telemetry_viewmodel.set_battery_status)
                
                self._logger.addLog("[INFO] TelemetryViewModel erfolgreich registriert")
                return True
            else:
                self._logger.addLog("[WARN] Kein MAVLinkHandler verfügbar für TelemetryViewModel")
                return False
        except Exception as e:
            self._logger.addLog(f"[ERR] Fehler bei der Registrierung des TelemetryViewModel: {str(e)}")
            return False
