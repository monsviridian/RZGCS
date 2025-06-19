"""
Connection Manager für das RZGCS.
Verwaltet und koordiniert alle Verbindungskomponenten.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import time
from PySide6.QtCore import QObject, Signal, Property, Slot, QTimer
from PySide6.QtQml import QmlElement
import serial
import serial.tools.list_ports
import socket
import sys
import logging
import threading
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

from .connection_types import (
    BaseConnection,
    SerialConnection,
    UDPConnection,
    TCPConnection,
    SimulatorConnection
)
from .connection_logger import ConnectionLogger
from .connection_security import ConnectionSecurity
from .bandwidth_manager import BandwidthManager
from .enums import ConnectionType, ConnectionStatus

QML_IMPORT_NAME = "RZGCS.Connection"
QML_IMPORT_MAJOR_VERSION = 1

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

@QmlElement
class ConnectionManager(QObject):
    """Hauptklasse für die Verbindungsverwaltung"""
    
    # Signale
    statusChanged = Signal(ConnectionStatus)
    errorOccurred = Signal(str)
    messageReceived = Signal(bytes)
    messageSent = Signal(bytes)
    bandwidthChanged = Signal(float)  # bytes/s
    availablePortsChanged = Signal(list)
    
    def __init__(self, parent=None):
        """Initialisiert den Connection Manager"""
        super().__init__(parent)
        
        # Komponenten initialisieren
        self._logger = ConnectionLogger()
        self._security = ConnectionSecurity()
        self._bandwidth = BandwidthManager()
        
        # Verbindungsstatus
        self._status = ConnectionStatus.DISCONNECTED
        self._error_message = ""
        
        # Aktuelle Verbindung
        self._current_connection = None
        
        # Telemetrie Manager
        from ..telemetry.telemetry_manager import TelemetryManager
        self._telemetry_manager = TelemetryManager()
        self._telemetry_manager.set_connection_manager(self)
        
        # Timer für Status-Updates
        self._status_timer = QTimer()
        self._status_timer.timeout.connect(self._check_connection)
        self._status_timer.start(1000)  # 1 Sekunde Update-Intervall
        
        # Port-Scan Timer
        self._last_port_list = []
        self._port_scan_timer = QTimer()
        self._port_scan_timer.timeout.connect(self._scan_ports)
        self._port_scan_timer.start(1000)  # alle 1 s
        
    @Property(ConnectionStatus, notify=statusChanged)
    def status(self) -> ConnectionStatus:
        """Gibt den aktuellen Status zurück"""
        return self._status
        
    @Property(str, notify=errorOccurred)
    def error_message(self) -> str:
        """Gibt die letzte Fehlermeldung zurück"""
        return self._error_message
        
    @Property(float, notify=bandwidthChanged)
    def bandwidth_usage(self) -> float:
        """Gibt die aktuelle Bandbreitennutzung zurück"""
        return self._bandwidth.current_usage
        
    @Slot(dict)
    def establish_connection(self, settings: Dict[str, Any] = None) -> bool:
        """Stellt eine Verbindung her"""
        try:
            # Debug-Ausgabe
            print("[DEBUG] ConnectionManager.establish_connection: Verbindungseinstellungen:", settings)
            
            # Verbindungseinstellungen laden
            if settings is None:
                settings = self._load_connection_settings()
            
            # Verbindungstyp ermitteln
            connection_type = ConnectionType(settings.get('type', 'Serial'))
            print("[DEBUG] ConnectionManager.establish_connection: Verbindungstyp:", connection_type)
            
            # Prüfe ob bereits eine Verbindung besteht
            if self._current_connection and self._current_connection.is_connected():
                print("[DEBUG] Bereits verbunden, trenne zuerst...")
                self.disconnect()
            
            # Verbindung erstellen
            print("[DEBUG] ConnectionManager.establish_connection: Erstelle SerialConnection")
            self._current_connection = SerialConnection()
            
            # Verbindungsparameter validieren
            port = settings.get('port')
            baudrate = settings.get('baudrate', 115200)
            
            if not port:
                print("[ERROR] Kein Port angegeben")
                return False
                
            if connection_type == ConnectionType.SERIAL and port != "Simulator":
                try:
                    # Prüfe ob der serielle Port existiert
                    available_ports = [p.device for p in serial.tools.list_ports.comports()]
                    if port not in available_ports:
                        print(f"[ERROR] Port {port} nicht gefunden. Verfügbare Ports: {available_ports}")
                        return False
                except Exception as e:
                    print(f"[ERROR] Fehler beim Prüfen der verfügbaren Ports: {str(e)}")
                    return False
            
            # Verbindung herstellen
            print("[DEBUG] ConnectionManager.establish_connection: Verbinde SerialConnection mit Port und Baudrate")
            result = self._current_connection.establish_connection(
                port=port,
                baudrate=baudrate
            )
            
            if not result:
                print("[ERROR] Connection Manager: SerialConnection konnte nicht verbinden")
                return False
                
            # Verbindung erfolgreich
            print("[DEBUG] ConnectionManager.establish_connection: Verbindung erfolgreich")
            
            # Telemetrie starten
            if hasattr(self, '_telemetry_manager') and self._telemetry_manager:
                print("[DEBUG] Starte Telemetriedienst")
                self._telemetry_manager.start_telemetry()
            
            return True
            
        except Exception as e:
            print(f"[ERROR] ConnectionManager.establish_connection: {str(e)}")
            return False
            
    @Slot()
    def disconnect(self) -> None:
        """Trennt die aktuelle Verbindung"""
        if self._current_connection and self._current_connection.is_connected():
            self._current_connection.disconnect()
            
        self._current_connection = None
        self._set_status(ConnectionStatus.DISCONNECTED)
        self._logger.stop_logging()
        
    @Slot(bytes)
    def send_message(self, message: bytes) -> bool:
        """
        Sendet eine Nachricht.
        
        Args:
            message: Zu sendende Nachricht
            
        Returns:
            True wenn erfolgreich, sonst False
        """
        try:
            if not self._current_connection or not self._current_connection.is_connected():
                raise ConnectionError("Nicht verbunden")
                
            # Nachricht verschlüsseln
            if self._security.is_encryption_enabled():
                message = self._security.encrypt_message(message)
                
            # Nachricht senden
            if not self._current_connection.send_message(message):
                raise ConnectionError("Senden fehlgeschlagen")
                
            # Bandbreite aktualisieren
            self._bandwidth.add_sent_bytes(len(message))
            
            # Logging
            self._logger.log_message(message, True)
            
            # Signal senden
            self.messageSent.emit(message)
            
            return True
            
        except Exception as e:
            self._set_error(f"Fehler beim Senden: {str(e)}")
            return False
            
    @Slot()
    def enable_encryption(self) -> None:
        """Aktiviert die Verschlüsselung"""
        self._security.enable_encryption()
        
    @Slot()
    def disable_encryption(self) -> None:
        """Deaktiviert die Verschlüsselung"""
        self._security.disable_encryption()
        
    @Slot()
    def reset_bandwidth(self) -> None:
        """Setzt die Bandbreitennutzung zurück"""
        self._bandwidth.reset_usage()
        
    @Slot(str)
    def export_log(self, file_path: str) -> bool:
        """
        Exportiert das Log.
        
        Args:
            file_path: Pfad zur Export-Datei
            
        Returns:
            True wenn erfolgreich, sonst False
        """
        try:
            self._logger.export_log(file_path)
            return True
        except Exception as e:
            self._set_error(f"Fehler beim Exportieren: {str(e)}")
            return False
            
    def _check_connection(self) -> None:
        """Prüft die Verbindung"""
        if self._current_connection and self._status == ConnectionStatus.CONNECTED:
            if not self._current_connection.is_alive():
                self._set_error("Verbindung verloren")
                self.disconnect()
                
    def _handle_message(self, message: bytes) -> None:
        """
        Verarbeitet eingehende Nachrichten.
        
        Args:
            message: Eingehende Nachricht
        """
        try:
            # Nachricht entschlüsseln
            if self._security.is_encryption_enabled():
                message = self._security.decrypt_message(message)
                
            # Bandbreite aktualisieren
            self._bandwidth.add_received_bytes(len(message))
            
            # Logging
            self._logger.log_message(message, False)
            
            # Signal senden
            self.messageReceived.emit(message)
            
        except Exception as e:
            self._set_error(f"Fehler bei der Nachrichtenverarbeitung: {str(e)}")
            
    def _set_status(self, status: ConnectionStatus) -> None:
        """
        Setzt den Status.
        
        Args:
            status: Neuer Status
        """
        if self._status != status:
            self._status = status
            self.statusChanged.emit(status)
            
    def _set_error(self, message: str) -> None:
        """
        Setzt eine Fehlermeldung.
        
        Args:
            message: Fehlermeldung
        """
        self._error_message = message
        self.errorOccurred.emit(message)
        self._set_status(ConnectionStatus.ERROR)
    
    def get_available_ports(self) -> List[dict]:
        """
        Gibt eine Liste aller verfügbaren seriellen Ports zurück.
        
        Returns:
            Eine Liste von Dictionaries mit Port-Informationen
        """
        from PySide6.QtSerialPort import QSerialPortInfo
        import platform
        
        ports = []
        
        # QSerialPortInfo für Hardwareport-Erkennung verwenden
        for port_info in QSerialPortInfo.availablePorts():
            port_data = {
                'port': port_info.portName(),
                'description': port_info.description(),
                'manufacturer': port_info.manufacturer(),
                'serial': port_info.serialNumber(),
                'system_location': port_info.systemLocation()
            }
            ports.append(port_data)
            
        # Wenn keine Ports gefunden wurden, Standard-Port hinzufügen
        if not ports:
            default_port = "COM1" if platform.system().lower() == "windows" else "/dev/ttyACM0"
            ports.append({
                'port': default_port,
                'description': "Default port",
                'manufacturer': "",
                'serial': "",
                'system_location': default_port
            })
            
        return ports
        
    def get_connection_config_for_deployment(self) -> dict:
        """
        Gibt Konfigurationsinformationen für das Deployment zurück.
        
        Returns:
            Ein Dictionary mit Konfigurationsinformationen
        """
        import platform
        system = platform.system().lower()
        
        config = {
            'platform': system,
            'special_instructions': [],
            'default_baudrate': 115200  # Standard-Baudrate für alle Verbindungen
        }
        
        if system == 'windows':
            config['special_instructions'].append("Auf Windows müssen COM-Ports installiert sein")
        elif system == 'linux':
            config['special_instructions'].append("Auf Linux benötigen /dev/tty* Geräte die entsprechenden Berechtigungen")
        elif system == 'darwin':  # macOS
            config['special_instructions'].append("Auf macOS werden Ports als /dev/cu.* erkannt")
            
        return config

    def _scan_ports(self):
        """Emit availablePortsChanged when port list changes"""
        try:
            ports = []
            # Nur SerialConnection benötigt Ports
            serial_conn = SerialConnection()
            port_infos = serial_conn.get_available_ports(force_refresh=True)
            for p in port_infos:
                ports.append(p.device if hasattr(p, 'device') else p['port'])
            if ports != self._last_port_list:
                self._last_port_list = ports
                self.availablePortsChanged.emit(ports)
        except Exception:
            pass
