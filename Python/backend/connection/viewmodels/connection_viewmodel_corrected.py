"""
Connection-ViewModel für die Verbindungsverwaltung.
Implementiert die ViewModel-Schicht der MVVM-Architektur.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from PySide6.QtCore import QObject, Signal, Slot, Property
from ..models.connection_data import (
    ConnectionType,
    ConnectionStatus,
    ConnectionParameters,
    ConnectionState,
    ConnectionStatistics,
    ConnectionInfo
)
from ..services.connection_service import ConnectionService

class ConnectionViewModel(QObject):
    """ViewModel für die Verbindungsverwaltung."""
    
    # Signale
    status_changed = Signal(ConnectionStatus)
    type_changed = Signal(ConnectionType)
    parameters_changed = Signal(ConnectionParameters)
    state_updated = Signal(ConnectionState)
    statistics_updated = Signal(ConnectionStatistics)
    error_occurred = Signal(str)
    
    def __init__(self):
        """Initialisiert das Connection-ViewModel."""
        super().__init__()
        
        # Initialisiere Service
        self._service = ConnectionService()
        
        # Verbinde Service-Signale mit Handler-Methoden
        # WICHTIG: Wir verwenden eigene Handler-Methoden statt direkter Verbindung
        # um Namenskonflikte mit der connect() Methode zu vermeiden
        self._service.status_changed.connect(self._handle_status_changed)
        self._service.type_changed.connect(self._handle_type_changed)
        self._service.parameters_changed.connect(self._handle_parameters_changed)
        self._service.state_updated.connect(self._handle_state_updated)
        self._service.statistics_updated.connect(self._handle_statistics_updated)
        self._service.error_occurred.connect(self._handle_error_occurred)
        
    def set_service(self, service: ConnectionService) -> None:
        """Setzt den Connection-Service.
        
        Args:
            service: Der Connection-Service
        """
        # Alte Verbindungen trennen
        if self._service:
            self._service.status_changed.disconnect(self._handle_status_changed)
            self._service.type_changed.disconnect(self._handle_type_changed)
            self._service.parameters_changed.disconnect(self._handle_parameters_changed)
            self._service.state_updated.disconnect(self._handle_state_updated)
            self._service.statistics_updated.disconnect(self._handle_statistics_updated)
            self._service.error_occurred.disconnect(self._handle_error_occurred)
            
        # Neuen Service setzen
        self._service = service
        
        # Verbinde Service-Signale mit Handler-Methoden
        if self._service:
            self._service.status_changed.connect(self._handle_status_changed)
            self._service.type_changed.connect(self._handle_type_changed)
            self._service.parameters_changed.connect(self._handle_parameters_changed)
            self._service.state_updated.connect(self._handle_state_updated)
            self._service.statistics_updated.connect(self._handle_statistics_updated)
            self._service.error_occurred.connect(self._handle_error_occurred)

    # Signal-Handler
    def _handle_status_changed(self, status):
        """Behandelt Status-Änderungen vom Service."""
        self.status_changed.emit(status)
        
    def _handle_type_changed(self, connection_type):
        """Behandelt Verbindungstyp-Änderungen vom Service."""
        self.type_changed.emit(connection_type)
        
    def _handle_parameters_changed(self, parameters):
        """Behandelt Parameter-Änderungen vom Service."""
        self.parameters_changed.emit(parameters)
        
    def _handle_state_updated(self, state):
        """Behandelt State-Änderungen vom Service."""
        self.state_updated.emit(state)
        
    def _handle_statistics_updated(self, statistics):
        """Behandelt Statistik-Änderungen vom Service."""
        self.statistics_updated.emit(statistics)
        
    def _handle_error_occurred(self, error_message):
        """Behandelt Fehler vom Service."""
        self.error_occurred.emit(error_message)
        
    # Properties
    @Property(ConnectionStatus, notify=status_changed)
    def status(self) -> ConnectionStatus:
        """Gibt den aktuellen Verbindungsstatus zurück.
        
        Returns:
            ConnectionStatus: Der aktuelle Verbindungsstatus
        """
        return self._service.get_state().status
        
    @Property(ConnectionType, notify=type_changed)
    def type(self) -> ConnectionType:
        """Gibt den aktuellen Verbindungstyp zurück.
        
        Returns:
            ConnectionType: Der aktuelle Verbindungstyp
        """
        return self._service.get_state().type
        
    @Property(ConnectionParameters, notify=parameters_changed)
    def parameters(self) -> ConnectionParameters:
        """Gibt die aktuellen Verbindungsparameter zurück.
        
        Returns:
            ConnectionParameters: Die aktuellen Verbindungsparameter
        """
        return self._service.get_parameters()
        
    @Property(ConnectionState, notify=state_updated)
    def state(self) -> ConnectionState:
        """Gibt den aktuellen Verbindungszustand zurück.
        
        Returns:
            ConnectionState: Der aktuelle Verbindungszustand
        """
        return self._service.get_state()
        
    @Property(ConnectionStatistics, notify=statistics_updated)
    def statistics(self) -> ConnectionStatistics:
        """Gibt die aktuellen Verbindungsstatistiken zurück.
        
        Returns:
            ConnectionStatistics: Die aktuellen Verbindungsstatistiken
        """
        return self._service.get_statistics()
        
    # Slots
    @Slot()
    def connect_device(self) -> bool:
        """Stellt eine Verbindung her.
        
        Returns:
            bool: True wenn erfolgreich, sonst False
        """
        # Wir nennen die Methode connect_device statt connect,
        # um Namenskonflikte mit der Signal-Connect-Methode zu vermeiden
        return self._service.connect()
        
    @Slot()
    def disconnect(self) -> bool:
        """Trennt die Verbindung.
        
        Returns:
            bool: True wenn erfolgreich, sonst False
        """
        return self._service.disconnect()
        
    @Slot(ConnectionParameters)
    def set_parameters(self, parameters: ConnectionParameters) -> bool:
        """Setzt die Verbindungsparameter.
        
        Args:
            parameters: Die neuen Verbindungsparameter
            
        Returns:
            bool: True wenn erfolgreich, sonst False
        """
        return self._service.set_parameters(parameters)
        
    @Slot(str)
    def export_connection_data(self, file_path: str) -> bool:
        """Exportiert die Verbindungsdaten in eine JSON-Datei.
        
        Args:
            file_path: Der Pfad zur JSON-Datei
            
        Returns:
            bool: True wenn erfolgreich, sonst False
        """
        return self._service.export_connection_data(file_path)
        
    @Slot(str)
    def import_connection_data(self, file_path: str) -> bool:
        """Importiert die Verbindungsdaten aus einer JSON-Datei.
        
        Args:
            file_path: Der Pfad zur JSON-Datei
            
        Returns:
            bool: True wenn erfolgreich, sonst False
        """
        return self._service.import_connection_data(file_path)
