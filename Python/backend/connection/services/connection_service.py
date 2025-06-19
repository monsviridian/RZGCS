"""
Connection-Service für die Verbindungsverwaltung.
Implementiert die Service-Schicht der MVVM-Architektur.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import json
from PySide6.QtCore import QObject, Signal, Slot, QTimer
from ..models.connection_data import (
    ConnectionType,
    ConnectionStatus,
    ConnectionParameters,
    ConnectionState,
    ConnectionStatistics,
    ConnectionInfo
)

class ConnectionService(QObject):
    """Service für die Verbindungsverwaltung."""
    
    # Signale
    status_changed = Signal(ConnectionStatus)
    type_changed = Signal(ConnectionType)
    parameters_changed = Signal(ConnectionParameters)
    state_updated = Signal(ConnectionState)
    statistics_updated = Signal(ConnectionStatistics)
    error_occurred = Signal(str)
    
    def __init__(self):
        """Initialisiert den Connection-Service."""
        super().__init__()
        
        # Initialisiere Verbindungsmanager
        self._connection_manager = None
        
        # Initialisiere Verbindungszustand
        self._state = ConnectionState(
            status=ConnectionStatus.DISCONNECTED,
            type=ConnectionType.MAVLINK,
            parameters=ConnectionParameters(type=ConnectionType.MAVLINK)
        )
        
        # Initialisiere Statistiken
        self._statistics = ConnectionStatistics()
        
        # Initialisiere Timer für Status-Updates
        self._update_timer = QTimer()
        self._update_timer.timeout.connect(self._update_state)
        self._update_timer.start(1000)  # Update alle 1 Sekunde
        
    def set_connection_manager(self, manager: Any) -> None:
        """Setzt den Verbindungsmanager.
        
        Args:
            manager: Der Verbindungsmanager
        """
        self._connection_manager = manager
        
    def get_state(self) -> ConnectionState:
        """Gibt den aktuellen Verbindungszustand zurück.
        
        Returns:
            ConnectionState: Der aktuelle Verbindungszustand
        """
        return self._state
        
    def get_statistics(self) -> ConnectionStatistics:
        """Gibt die aktuellen Verbindungsstatistiken zurück.
        
        Returns:
            ConnectionStatistics: Die aktuellen Verbindungsstatistiken
        """
        return self._statistics
        
    def get_parameters(self) -> ConnectionParameters:
        """Gibt die aktuellen Verbindungsparameter zurück.
        
        Returns:
            ConnectionParameters: Die aktuellen Verbindungsparameter
        """
        return self._state.parameters
        
    @Slot()
    def connect(self) -> bool:
        """Stellt eine Verbindung her"""
        try:
            # Verbindung herstellen
            success = self._connection_manager.establish_connection()
            
            if success:
                self._state.status = ConnectionStatus.CONNECTED
                self._state.is_connected = True
                self._state.is_connecting = False
                self.status_changed.emit(self._state.status)
                return True
            else:
                self._state.status = ConnectionStatus.ERROR
                self._state.is_error = True
                self._state.is_connecting = False
                self.status_changed.emit(self._state.status)
                return False
                
        except Exception as e:
            self._state.status = ConnectionStatus.ERROR
            self._state.is_error = True
            self._state.is_connecting = False
            self._state.error_message = str(e)
            self.status_changed.emit(self._state.status)
            self.error_occurred.emit(str(e))
            return False
            
    @Slot()
    def disconnect(self) -> bool:
        """Trennt die Verbindung.
        
        Returns:
            bool: True wenn erfolgreich, sonst False
        """
        if not self._connection_manager:
            self.error_occurred.emit("Kein Verbindungsmanager verfügbar")
            return False
            
        try:
            # Trenne Verbindung
            success = self._connection_manager.disconnect()
            
            if success:
                self._state.status = ConnectionStatus.DISCONNECTED
                self._state.is_connected = False
                self._state.is_error = False
                self.status_changed.emit(self._state.status)
                return True
            else:
                self._state.status = ConnectionStatus.ERROR
                self._state.is_error = True
                self.status_changed.emit(self._state.status)
                return False
                
        except Exception as e:
            self._state.status = ConnectionStatus.ERROR
            self._state.is_error = True
            self._state.error_message = str(e)
            self.status_changed.emit(self._state.status)
            self.error_occurred.emit(str(e))
            return False
            
    @Slot(ConnectionParameters)
    def set_parameters(self, parameters: ConnectionParameters) -> bool:
        """Setzt die Verbindungsparameter.
        
        Args:
            parameters: Die neuen Verbindungsparameter
            
        Returns:
            bool: True wenn erfolgreich, sonst False
        """
        if not self._connection_manager:
            self.error_occurred.emit("Kein Verbindungsmanager verfügbar")
            return False
            
        try:
            # Setze Parameter
            success = self._connection_manager.set_parameters(parameters)
            
            if success:
                self._state.parameters = parameters
                self.parameters_changed.emit(parameters)
                return True
            else:
                self.error_occurred.emit("Fehler beim Setzen der Parameter")
                return False
                
        except Exception as e:
            self.error_occurred.emit(str(e))
            return False
            
    @Slot(str)
    def export_connection_data(self, file_path: str) -> bool:
        """Exportiert die Verbindungsdaten in eine JSON-Datei.
        
        Args:
            file_path: Der Pfad zur JSON-Datei
            
        Returns:
            bool: True wenn erfolgreich, sonst False
        """
        try:
            # Erstelle Daten
            data = {
                "state": {
                    "status": self._state.status.value,
                    "type": self._state.type.value,
                    "parameters": {
                        "type": self._state.parameters.type.value,
                        "port": self._state.parameters.port,
                        "baudrate": self._state.parameters.baudrate,
                        "host": self._state.parameters.host,
                        "port_number": self._state.parameters.port_number,
                        "timeout": self._state.parameters.timeout,
                        "retry_count": self._state.parameters.retry_count,
                        "auto_reconnect": self._state.parameters.auto_reconnect
                    },
                    "last_heartbeat": self._state.last_heartbeat.isoformat() if self._state.last_heartbeat else None,
                    "error_message": self._state.error_message,
                    "is_connected": self._state.is_connected,
                    "is_connecting": self._state.is_connecting,
                    "is_error": self._state.is_error
                },
                "statistics": {
                    "bytes_sent": self._statistics.bytes_sent,
                    "bytes_received": self._statistics.bytes_received,
                    "packets_sent": self._statistics.packets_sent,
                    "packets_received": self._statistics.packets_received,
                    "errors": self._statistics.errors,
                    "connection_time": self._statistics.connection_time,
                    "last_error_time": self._statistics.last_error_time.isoformat() if self._statistics.last_error_time else None,
                    "last_error_message": self._statistics.last_error_message
                }
            }
            
            # Schreibe Datei
            with open(file_path, "w") as f:
                json.dump(data, f, indent=4)
                
            return True
            
        except Exception as e:
            self.error_occurred.emit(str(e))
            return False
            
    @Slot(str)
    def import_connection_data(self, file_path: str) -> bool:
        """Importiert die Verbindungsdaten aus einer JSON-Datei.
        
        Args:
            file_path: Der Pfad zur JSON-Datei
            
        Returns:
            bool: True wenn erfolgreich, sonst False
        """
        try:
            # Lese Datei
            with open(file_path, "r") as f:
                data = json.load(f)
                
            # Aktualisiere State
            state_data = data["state"]
            self._state = ConnectionState(
                status=ConnectionStatus(state_data["status"]),
                type=ConnectionType(state_data["type"]),
                parameters=ConnectionParameters(
                    type=ConnectionType(state_data["parameters"]["type"]),
                    port=state_data["parameters"]["port"],
                    baudrate=state_data["parameters"]["baudrate"],
                    host=state_data["parameters"]["host"],
                    port_number=state_data["parameters"]["port_number"],
                    timeout=state_data["parameters"]["timeout"],
                    retry_count=state_data["parameters"]["retry_count"],
                    auto_reconnect=state_data["parameters"]["auto_reconnect"]
                ),
                last_heartbeat=datetime.fromisoformat(state_data["last_heartbeat"]) if state_data["last_heartbeat"] else None,
                error_message=state_data["error_message"],
                is_connected=state_data["is_connected"],
                is_connecting=state_data["is_connecting"],
                is_error=state_data["is_error"]
            )
            
            # Aktualisiere Statistiken
            stats_data = data["statistics"]
            self._statistics = ConnectionStatistics(
                bytes_sent=stats_data["bytes_sent"],
                bytes_received=stats_data["bytes_received"],
                packets_sent=stats_data["packets_sent"],
                packets_received=stats_data["packets_received"],
                errors=stats_data["errors"],
                connection_time=stats_data["connection_time"],
                last_error_time=datetime.fromisoformat(stats_data["last_error_time"]) if stats_data["last_error_time"] else None,
                last_error_message=stats_data["last_error_message"]
            )
            
            # Emitte Signale
            self.state_updated.emit(self._state)
            self.statistics_updated.emit(self._statistics)
            
            return True
            
        except Exception as e:
            self.error_occurred.emit(str(e))
            return False
            
    def _update_state(self) -> None:
        """Aktualisiert den Verbindungszustand."""
        if not self._connection_manager:
            return
            
        try:
            # Hole Status
            status = self._connection_manager.get_status()
            
            # Aktualisiere State
            self._state.status = status
            self._state.is_connected = status == ConnectionStatus.CONNECTED
            self._state.is_error = status == ConnectionStatus.ERROR
            self._state.last_heartbeat = datetime.now()
            
            # Hole Statistiken
            stats = self._connection_manager.get_statistics()
            
            # Aktualisiere Statistiken
            self._statistics.bytes_sent = stats.get("bytes_sent", 0)
            self._statistics.bytes_received = stats.get("bytes_received", 0)
            self._statistics.packets_sent = stats.get("packets_sent", 0)
            self._statistics.packets_received = stats.get("packets_received", 0)
            self._statistics.errors = stats.get("errors", 0)
            self._statistics.connection_time = stats.get("connection_time", 0.0)
            
            # Emitte Signale
            self.state_updated.emit(self._state)
            self.statistics_updated.emit(self._statistics)
            
        except Exception as e:
            self.error_occurred.emit(str(e)) 