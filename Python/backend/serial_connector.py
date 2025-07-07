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
    velocityUpdated = Signal(float, float, float)  # groundspeed, airspeed, vertical_speed
    vfrHudUpdated = Signal(float, float, float, float)  # groundspeed, airspeed, heading, throttle

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
        self._mavlink_handler = MAVLinkHandler(logger=self._logger)
        
        # Verbinde MAVLink-Handler Signale
        self._mavlink_handler.connection_state_changed.connect(self._on_connection_status_changed)
        self._mavlink_handler.attitude_updated.connect(self._on_attitude_updated)
        self._mavlink_handler.gps_updated.connect(self._on_gps_updated)
        self._mavlink_handler.battery_updated.connect(self._on_battery_updated)
        self._mavlink_handler.velocity_updated.connect(self._on_velocity_updated)
        self._mavlink_handler.vfr_hud_updated.connect(self._on_vfr_hud_updated)
        self._mavlink_handler.status_text_received.connect(self._on_status_text_received)
        self._mavlink_handler.error_occurred.connect(self._on_error_occurred)
        
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

    def set_message_manager(self, message_manager):
        """Setzt den MessageManager für die Weiterleitung von Logger-Nachrichten"""
        if hasattr(self._logger, 'set_message_callback'):
            self._logger.set_message_callback(message_manager.addMessage)
            self._logger.addLog("[DEBUG] SerialConnector: MessageManager-Callback gesetzt")
        else:
            print("[WARN] Logger hat keine set_message_callback Methode")

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
            if self._port != "Simulator":
                # Aktualisiere die verfügbaren Ports vor der Verbindung
                self.load_ports()
                
                # Extrahiere den reinen Port-Namen aus dem Display-Namen
                selected_port_name = self._port
                if "(" in self._port:
                    selected_port_name = self._port.split("(")[0].strip()
                
                # Prüfe ob der Port in der Liste ist
                port_found = False
                for port_display in self._available_ports:
                    if port_display == self._port or port_display.startswith(selected_port_name + " "):
                        port_found = True
                        break
                
                if not port_found:
                    available_ports_clean = []
                    for port in self._available_ports:
                        if port != "Simulator":
                            clean_port = port.split("(")[0].strip()
                            available_ports_clean.append(clean_port)
                    
                    error_msg = f"Port {self._port} ist nicht verfügbar. Verfügbare Ports: {', '.join(available_ports_clean)}"
                    self._logger.addLog(f"[ERR] {error_msg}")
                    self.errorOccurred.emit(error_msg)
                    self._connecting = False
                    self.connectionStatusChanged.emit(0)  # disconnected
                    return False
                
                # Zusätzliche Prüfung: Teste ob der Port wirklich existiert
                try:
                    import serial.tools.list_ports
                    available_ports = [p.device for p in serial.tools.list_ports.comports()]
                    if selected_port_name not in available_ports:
                        error_msg = f"Port {selected_port_name} existiert nicht auf diesem System. Verfügbare Ports: {', '.join(available_ports)}"
                        self._logger.addLog(f"[ERR] {error_msg}")
                        self.errorOccurred.emit(error_msg)
                        self._connecting = False
                        self.connectionStatusChanged.emit(0)  # disconnected
                        return False
                except Exception as e:
                    self._logger.addLog(f"[WARN] Konnte Port-Validierung nicht durchführen: {str(e)}")
            
            # Verbindung über MAVLink-Handler herstellen
            # Verwende den reinen Port-Namen für die Verbindung
            connection_port = selected_port_name if 'selected_port_name' in locals() else self._port
            success = self._mavlink_handler.connect(connection_port, self._baud_rate)
            if success:
                self._connected = True
                self.connectedChanged.emit(True)
                self.connectionStatusChanged.emit(2)  # connected
                self._logger.addLog(f"[OK] Verbunden mit {connection_port}")
            else:
                error_msg = f"Verbindung zu {connection_port} fehlgeschlagen"
                self._logger.addLog(f"[ERR] {error_msg}")
                self.errorOccurred.emit(error_msg)
                self._connected = False
                self.connectedChanged.emit(False)
                self.connectionStatusChanged.emit(0)  # disconnected
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
            
            # Sammle alle verfügbaren Ports mit Beschreibungen
            port_info_list = []
            
            # Verwende QSerialPortInfo für die Port-Erkennung
            self._logger.addLog("[DEBUG] Suche Ports mit QSerialPortInfo...")
            try:
                for port in QSerialPortInfo.availablePorts():
                    port_name = port.portName()
                    port_desc = port.description()
                    port_info_list.append({
                        'name': port_name,
                        'description': port_desc,
                        'source': 'QSerialPortInfo'
                    })
                    self._logger.addLog(f"[PORT-DEBUG] Port gefunden (QSerialPortInfo): {port_name} ({port_desc})")
            except Exception as e:
                self._logger.addLog(f"[WARN] Fehler bei QSerialPortInfo: {str(e)}")
            
            # Zusätzlich auch serial.tools.list_ports verwenden
            self._logger.addLog("[DEBUG] Suche Ports mit serial.tools.list_ports...")
            try:
                for port in serial.tools.list_ports.comports():
                    port_name = port.device
                    port_desc = port.description
                    
                    # Prüfe ob Port bereits in der Liste ist
                    existing_port = next((p for p in port_info_list if p['name'] == port_name), None)
                    if not existing_port:
                        port_info_list.append({
                            'name': port_name,
                            'description': port_desc,
                            'source': 'serial.tools'
                        })
                        self._logger.addLog(f"[PORT-DEBUG] Port gefunden (serial.tools): {port_name} ({port_desc})")
                    else:
                        # Aktualisiere Beschreibung falls nötig
                        if not existing_port['description'] and port_desc:
                            existing_port['description'] = port_desc
                            self._logger.addLog(f"[PORT-DEBUG] Beschreibung aktualisiert für {port_name}: {port_desc}")
            except Exception as e:
                self._logger.addLog(f"[WARN] Fehler bei serial.tools.list_ports: {str(e)}")
            
            # Sortiere Ports: COM-Ports zuerst, dann andere
            def sort_ports(port_info):
                name = port_info['name']
                # COM-Ports nach Nummer sortieren
                if name.upper().startswith('COM'):
                    try:
                        com_num = int(name[3:])  # Extrahiere Nummer aus COM
                        return (0, com_num)  # COM-Ports zuerst, sortiert nach Nummer
                    except ValueError:
                        return (0, 999)  # Ungültige COM-Ports ans Ende
                else:
                    return (1, name)  # Andere Ports nach dem Namen
            
            # Sortiere die Port-Liste
            port_info_list.sort(key=sort_ports)
            
            # Erstelle finale Port-Liste mit Beschreibungen
            final_ports = ["Simulator"]
            for port_info in port_info_list:
                port_name = port_info['name']
                port_desc = port_info['description']
                
                # Füge Port mit Beschreibung hinzu
                if port_desc and "ArduPilot" in port_desc:
                    # ArduPilot-Ports bevorzugen
                    display_name = f"{port_name} (ArduPilot)"
                elif port_desc:
                    display_name = f"{port_name} ({port_desc})"
                else:
                    display_name = port_name
                
                final_ports.append(display_name)
                self._logger.addLog(f"[PORT-DEBUG] Port hinzugefügt: {display_name}")
            
            # Prüfe auf leere Port-Liste
            if len(final_ports) == 1 and final_ports[0] == "Simulator":
                self._logger.addLog("[WARN] Keine seriellen Ports gefunden")
            
            self._logger.addLog(f"[PORT-DEBUG] Finale Port-Liste: {final_ports}")
            self._available_ports = final_ports
            self.availablePortsChanged.emit(final_ports)
            
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

    def _on_attitude_updated(self, roll, pitch, yaw):
        """Handler für Attitude-Updates vom MAVLinkHandler"""
        self._logger.addLog(f"[SIGNAL] SerialConnector: Received attitude - roll={roll}, pitch={pitch}, yaw={yaw}")
        self.attitudeUpdated.emit(roll, pitch, yaw)

    def _on_gps_updated(self, lat, lon, alt):
        """Handler für GPS-Updates vom MAVLinkHandler"""
        self._logger.addLog(f"[SIGNAL] SerialConnector: Received GPS - lat={lat}, lon={lon}, alt={alt}")
        self.gpsUpdated.emit(lat, lon, alt)

    def _on_battery_updated(self, voltage, current, remaining):
        """Handler für Battery-Updates vom MAVLinkHandler"""
        self._logger.addLog(f"[SIGNAL] SerialConnector: Received battery - voltage={voltage}, current={current}, remaining={remaining}")
        self.batteryUpdated.emit(voltage, current, remaining)

    def _on_velocity_updated(self, groundspeed, airspeed, vertical_speed):
        """Handler für Velocity-Updates vom MAVLinkHandler"""
        self._logger.addLog(f"[SIGNAL] SerialConnector: Received velocity - groundspeed={groundspeed}, airspeed={airspeed}, vertical_speed={vertical_speed}")
        self.velocityUpdated.emit(groundspeed, airspeed, vertical_speed)

    def _on_vfr_hud_updated(self, groundspeed, airspeed, heading, throttle):
        """Handler für VFR_HUD-Updates vom MAVLinkHandler"""
        self._logger.addLog(f"[SIGNAL] SerialConnector: Received VFR_HUD - groundspeed={groundspeed}, airspeed={airspeed}, heading={heading}, throttle={throttle}")
        self.vfrHudUpdated.emit(groundspeed, airspeed, heading, throttle)

    def _on_status_text_received(self, text):
        """Wird aufgerufen, wenn eine STATUSTEXT-Nachricht vom Fluggerät empfangen wird"""
        self._logger.addLog(f"[FC] {text}")

    def _on_error_occurred(self, error_message):
        """Wird aufgerufen, wenn ein Fehler im MAVLink-Handler auftritt"""
        self._logger.addLog(f"[FEHLER] {error_message}")

        self.errorOccurred.emit(error_message)

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
                # Verbinde Battery-Signal - prüfe ob set_battery_status existiert, sonst verwende set_battery
                if hasattr(telemetry_viewmodel, 'set_battery_status'):
                    self.batteryUpdated.connect(telemetry_viewmodel.set_battery_status)
                elif hasattr(telemetry_viewmodel, 'set_battery'):
                    self.batteryUpdated.connect(telemetry_viewmodel.set_battery)
                else:
                    self._logger.addLog("[WARN] TelemetryViewModel hat keine set_battery_status oder set_battery Methode")
                # Verbinde Velocity-Signal
                if hasattr(telemetry_viewmodel, 'set_velocity'):
                    self.velocityUpdated.connect(telemetry_viewmodel.set_velocity)
                # Verbinde VFR_HUD-Signal
                if hasattr(telemetry_viewmodel, 'set_vfr_hud'):
                    self.vfrHudUpdated.connect(telemetry_viewmodel.set_vfr_hud)
                self._logger.addLog("[INFO] TelemetryViewModel erfolgreich registriert")
                return True
            else:
                self._logger.addLog("[WARN] Kein MAVLinkHandler verfügbar für TelemetryViewModel")
                return False
        except Exception as e:
            self._logger.addLog(f"[ERR] Fehler bei der Registrierung des TelemetryViewModel: {str(e)}")
            return False

    def __del__(self):
        """Destruktor - stellt sicher, dass alle Ressourcen korrekt freigegeben werden"""
        self.cleanup()
        
    def cleanup(self):
        """Saubere Bereinigung aller Ressourcen"""
        try:
            # MAVLink-Handler sauber beenden
            if hasattr(self, '_mavlink_handler') and self._mavlink_handler:
                self._mavlink_handler.cleanup()
                self._mavlink_handler = None
                
            # Verbindungsstatus zurücksetzen
            self._connected = False
            self._connecting = False
            
            # Logger-Nachricht
            if hasattr(self, '_logger') and self._logger:
                self._logger.addLog("[INFO] SerialConnector cleanup completed")
                        
        except Exception as e:
            print(f"WARNING: Error during SerialConnector cleanup: {e}")
