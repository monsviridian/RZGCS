"""
ViewModel für die Telemetrie.
Implementiert die Präsentationslogik für die Telemetrie.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime

from PySide6.QtCore import QObject, Signal, Slot, Property

from ..models.flight_data import Position, FlightState
from ..enums import FlightStatus, FlightMode
from ..services.telemetry_service import TelemetryService

class TelemetryViewModel(QObject):
    """Implementiert die Präsentationslogik für die Telemetrie"""
    
    # Signale
    state_updated = Signal(FlightState)
    position_updated = Signal(Position)
    mode_updated = Signal(FlightMode)
    status_updated = Signal(FlightStatus)
    parameters_updated = Signal(dict)
    error_occurred = Signal(str)
    
    def __init__(self):
        """Initialisiert das ViewModel"""
        super().__init__()
        
        # Service
        self._telemetry_service: Optional[TelemetryService] = None
        
        # Zustand
        self._state = FlightState(
            position=Position(0.0, 0.0, 0.0),
            mode=FlightMode.MANUAL,
            armed=False,
            status=FlightStatus.DISCONNECTED,
            parameters={}
        )
        
    def set_telemetry_service(self, service: TelemetryService) -> None:
        """
        Setzt den Telemetrie-Service.
        
        Args:
            service: Telemetrie-Service
        """
        self._telemetry_service = service
        
        # Signale verbinden (camelCase-Konvention)
        self._telemetry_service.stateChanged.connect(self._on_state_updated)
        self._telemetry_service.telemetryUpdated.connect(self._on_position_updated)
        self._telemetry_service.modeChanged.connect(self._on_mode_updated)
        # Hinweis: status_updated entspricht im TelemetryService stateChanged
        self._telemetry_service.stateChanged.connect(self._on_status_updated)
        # Hinweis: parameters_updated ist Teil der telemetryUpdated
        self._telemetry_service.telemetryUpdated.connect(self._on_parameters_updated)
        self._telemetry_service.errorOccurred.connect(self._on_error)
        
    # Properties
    @Property(FlightState, notify=state_updated)
    def state(self) -> FlightState:
        """Gibt den aktuellen Flugzustand zurück"""
        return self._state
        
    @Property(Position, notify=position_updated)
    def position(self) -> Position:
        """Gibt die aktuelle Position zurück"""
        return self._state.position
        
    @Property(FlightMode, notify=mode_updated)
    def mode(self) -> FlightMode:
        """Gibt den aktuellen Flugmodus zurück"""
        return self._state.mode
        
    @Property(FlightStatus, notify=status_updated)
    def status(self) -> FlightStatus:
        """Gibt den aktuellen Status zurück"""
        return self._state.status
        
    @Property(dict, notify=parameters_updated)
    def parameters(self) -> Dict[str, Any]:
        """Gibt die aktuellen Parameter zurück"""
        return self._state.parameters
        
    # Slots
    @Slot(str, object)
    def set_parameter(self, name: str, value: Any) -> bool:
        """
        Setzt einen Parameter.
        
        Args:
            name: Parametername
            value: Parameterwert
            
        Returns:
            True wenn erfolgreich, sonst False
        """
        if not self._telemetry_service:
            self._on_error("Kein Telemetrie-Service verfügbar")
            return False
            
        return self._telemetry_service.set_parameter(name, value)
        
    @Slot(str)
    def get_parameter(self, name: str) -> Optional[Any]:
        """
        Gibt einen Parameter zurück.
        
        Args:
            name: Parametername
            
        Returns:
            Parameterwert oder None wenn nicht gefunden
        """
        if not self._telemetry_service:
            self._on_error("Kein Telemetrie-Service verfügbar")
            return None
            
        return self._telemetry_service.get_parameter(name)
        
    @Slot(str)
    def export_telemetry(self, file_path: str) -> bool:
        """
        Exportiert die Telemetriedaten.
        
        Args:
            file_path: Dateipfad
            
        Returns:
            True wenn erfolgreich, sonst False
        """
        if not self._telemetry_service:
            self._on_error("Kein Telemetrie-Service verfügbar")
            return False
            
        return self._telemetry_service.export_telemetry(file_path)
        
    @Slot(str)
    def import_telemetry(self, file_path: str) -> bool:
        """
        Importiert Telemetriedaten.
        
        Args:
            file_path: Dateipfad
            
        Returns:
            True wenn erfolgreich, sonst False
        """
        if not self._telemetry_service:
            self._on_error("Kein Telemetrie-Service verfügbar")
            return False
            
        return self._telemetry_service.import_telemetry(file_path)
        
    # Signal-Handler
    def _on_state_updated(self, state: FlightState) -> None:
        """
        Handler für Zustandsaktualisierungen.
        
        Args:
            state: Neuer Zustand
        """
        self._state = state
        self.state_updated.emit(state)
        
    def _on_position_updated(self, position: Position) -> None:
        """
        Handler für Positionsaktualisierungen.
        
        Args:
            position: Neue Position
        """
        self._state.position = position
        self.position_updated.emit(position)
        
    def _on_mode_updated(self, mode: FlightMode) -> None:
        """
        Handler für Modusaktualisierungen.
        
        Args:
            mode: Neuer Modus
        """
        self._state.mode = mode
        self.mode_updated.emit(mode)
        
    def _on_status_updated(self, status: FlightStatus) -> None:
        """
        Handler für Statusaktualisierungen.
        
        Args:
            status: Neuer Status
        """
        self._state.status = status
        self.status_updated.emit(status)
        
    def _on_parameters_updated(self, parameters: Dict[str, Any]) -> None:
        """
        Handler für Parameteraktualisierungen.
        
        Args:
            parameters: Neue Parameter
        """
        self._state.parameters = parameters
        self.parameters_updated.emit(parameters)
        
    def _on_error(self, message: str) -> None:
        """
        Handler für Fehlermeldungen.
        
        Args:
            message: Fehlermeldung
        """
        self.error_occurred.emit(message) 
        
    # Direct sensor update methods for MAVLink integration
    @Slot(float, float, float)
    def set_attitude(self, roll: float, pitch: float, yaw: float) -> None:
        """
        Aktualisiert die Lage (Attitude) des Fluggeräts.
        
        Args:
            roll: Roll-Winkel in Grad
            pitch: Pitch-Winkel in Grad
            yaw: Yaw-Winkel in Grad (Heading)
        """
        if not hasattr(self._state, 'attitude'):
            self._state.attitude = {'roll': 0.0, 'pitch': 0.0, 'yaw': 0.0}
            
        self._state.attitude['roll'] = roll
        self._state.attitude['pitch'] = pitch
        self._state.attitude['yaw'] = yaw
        
        # Informiere die UI über Änderung
        self.state_updated.emit(self._state)
        
    @Slot(float, float, float)
    def set_gps_position(self, latitude: float, longitude: float, altitude: float) -> None:
        """
        Aktualisiert die GPS-Position.
        
        Args:
            latitude: Breitengrad
            longitude: Längengrad
            altitude: Höhe über Meeresspiegel
        """
        # Aktualisiere die Position im Zustand
        new_position = Position(latitude, longitude, altitude)
        self._state.position = new_position
        
        # Informiere die UI über Änderung
        self.position_updated.emit(new_position)
        
    @Slot(float, float, float)
    def set_battery_status(self, voltage: float, current: float, remaining: float) -> None:
        """
        Aktualisiert den Batteriestatus.
        
        Args:
            voltage: Batteriespannung in Volt
            current: Stromstärke in Ampere
            remaining: Verbleibende Kapazität in Prozent (0-100)
        """
        if not hasattr(self._state, 'battery'):
            self._state.battery = {'voltage': 0.0, 'current': 0.0, 'remaining': 0.0}
            
        self._state.battery['voltage'] = voltage
        self._state.battery['current'] = current
        self._state.battery['remaining'] = remaining
        
        # Hinweis: Kein dediziertes Signal für Battery-Updates, nutze state_updated
        self.state_updated.emit(self._state)
    