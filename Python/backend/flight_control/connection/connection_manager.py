"""
Connection Manager für die Flugsteuerung.
"""

from typing import Optional, List
from dataclasses import dataclass
from enum import Enum
from PySide6.QtCore import QObject, Signal

class ConnectionStatus(Enum):
    """Verbindungsstatus"""
    DISCONNECTED = "DISCONNECTED"
    CONNECTING = "CONNECTING"
    CONNECTED = "CONNECTED"
    ERROR = "ERROR"

class ConnectionType(Enum):
    """Verbindungstyp"""
    SERIAL = "SERIAL"
    UDP = "UDP"
    TCP = "TCP"

class ConnectionManager(QObject):
    """Manager für Verbindungen"""
    
    # Signale
    statusChanged = Signal(ConnectionStatus)
    availablePortsChanged = Signal(list)
    availableBaudRatesChanged = Signal(list)
    errorOccurred = Signal(str)
    
    def __init__(self):
        """Initialisiert den Connection Manager"""
        super().__init__()
        self._status = ConnectionStatus.DISCONNECTED
        self._port = ""
        self._baud_rate = 115200
        self._connection_type = ConnectionType.SERIAL
        self._available_ports = []
        self._available_baud_rates = [9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600]
        
    def get_status(self) -> ConnectionStatus:
        """Gibt den aktuellen Verbindungsstatus zurück"""
        return self._status
        
    def get_port(self) -> str:
        """Gibt den aktuellen Port zurück"""
        return self._port
        
    def get_baud_rate(self) -> int:
        """Gibt die aktuelle Baudrate zurück"""
        return self._baud_rate
        
    def get_connection_type(self) -> ConnectionType:
        """Gibt den aktuellen Verbindungstyp zurück"""
        return self._connection_type
        
    def get_available_ports(self) -> List[str]:
        """Gibt die verfügbaren Ports zurück"""
        return self._available_ports
        
    def get_available_baud_rates(self) -> List[int]:
        """Gibt die verfügbaren Baudraten zurück"""
        return self._available_baud_rates
        
    def set_port(self, port: str):
        """Setzt den Port"""
        self._port = port
        
    def set_baud_rate(self, baud_rate: int):
        """Setzt die Baudrate"""
        self._baud_rate = baud_rate
        
    def set_connection_type(self, connection_type: ConnectionType):
        """Setzt den Verbindungstyp"""
        self._connection_type = connection_type
        
    def connect(self):
        """Stellt die Verbindung her"""
        if self._status == ConnectionStatus.CONNECTED:
            return
            
        self._status = ConnectionStatus.CONNECTING
        self.statusChanged.emit(self._status)
        
        try:
            # TODO: Implementiere Verbindungsaufbau
            self._status = ConnectionStatus.CONNECTED
            self.statusChanged.emit(self._status)
        except Exception as e:
            self._status = ConnectionStatus.ERROR
            self.statusChanged.emit(self._status)
            self.errorOccurred.emit(str(e))
        
    def disconnect(self):
        """Trennt die Verbindung"""
        if self._status == ConnectionStatus.DISCONNECTED:
            return
            
        try:
            # TODO: Implementiere Verbindungsabbau
            self._status = ConnectionStatus.DISCONNECTED
            self.statusChanged.emit(self._status)
        except Exception as e:
            self._status = ConnectionStatus.ERROR
            self.statusChanged.emit(self._status)
            self.errorOccurred.emit(str(e))
        
    def load_ports(self):
        """Lädt die verfügbaren Ports"""
        try:
            # TODO: Implementiere Port-Scanning
            self._available_ports = ["COM1", "COM2", "COM3"]
            self.availablePortsChanged.emit(self._available_ports)
        except Exception as e:
            self.errorOccurred.emit(str(e))
            
    def is_connected(self) -> bool:
        """Prüft, ob eine Verbindung besteht"""
        return self._status == ConnectionStatus.CONNECTED 