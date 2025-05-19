from PySide6.QtCore import QObject, Signal
from abc import ABC, ABCMeta, abstractmethod
from typing import Dict, Any, Optional

class DroneConnectorMeta(type(QObject), ABCMeta):
    """Metaclass that combines QObject and ABCMeta"""
    pass

class DroneConnectorBase(QObject, ABC, metaclass=DroneConnectorMeta):
    """Basis-Klasse für Drohnen-Verbindungen"""
    
    # Signale für UI-Updates
    log_received = Signal(str)
    gps_msg = Signal(float, float)
    attitude_msg = Signal(float, float, float)
    sensor_data = Signal(str, float)
    connection_status = Signal(bool)
    
    def __init__(self):
        """Initialisiert die Basisklasse"""
        super().__init__()
        self.running = False
        self.debug = True
        self._is_connecting = False

    @abstractmethod
    def connect_to_drone(self) -> bool:
        """
        Stellt eine Verbindung zur Drohne her.
        Returns:
            bool: True wenn die Verbindung erfolgreich war, False sonst
        """
        pass

    @abstractmethod
    def disconnect_from_drone(self):
        """Trennt die Verbindung zur Drohne"""
        pass

    @abstractmethod
    def start_monitoring(self):
        """Startet das Monitoring der Drohnendaten"""
        pass

    @abstractmethod
    def stop(self):
        """Beendet die Verbindung synchron"""
        pass

    def _emit_log(self, message: str):
        """Sendet eine Log-Nachricht"""
        self.log_received.emit(message)

    def _emit_connection_status(self, connected: bool):
        """Aktualisiert den Verbindungsstatus"""
        self.connection_status.emit(connected)
