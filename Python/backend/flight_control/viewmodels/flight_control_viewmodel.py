"""Flugsteuerungs-ViewModel.

Dieses ViewModel stellt die Verbindung zwischen dem Flugsteuerungs-Service und der View her.
Es verwaltet den UI-Zustand und leitet Benutzerinteraktionen an den Service weiter.

Funktionen:
- Service-Integration
- UI-Zustandsverwaltung
- Benutzerinteraktionen
- Datenaktualisierungen
- Fehlerbehandlung

Beispiel:
    viewmodel = FlightControlViewModel()
    viewmodel.set_service(service)
    viewmodel.activate()
    viewmodel.arm()
    viewmodel.set_mode(FlightMode.STABILIZE)
    viewmodel.takeoff()
    viewmodel.land()
    viewmodel.disarm()
    viewmodel.deactivate()
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
from PySide6.QtCore import QObject, Signal, Slot, Property

from ..models.flight_control_data import (
    FlightMode,
    ControlMode,
    ControlAxis,
    ControlCommand,
    ControlStatus,
    ControlInput,
    ControlOutput,
    ControlState,
    ControlEvent,
    ControlLog,
    FlightControlError,
    FlightControlValidationError,
    FlightControlCommandError,
    FlightControlStateError
)
from ..services.flight_control_service import FlightControlService

class FlightControlViewModel(QObject):
    """Flugsteuerungs-ViewModel.
    
    Dieses ViewModel stellt die Verbindung zwischen dem Flugsteuerungs-Service und der View her.
    
    Attributes:
        _service: Flugsteuerungs-Service
        _state: Aktueller Steuerungszustand
        _log: Steuerungslog
        
    Signals:
        state_changed: Wird ausgelöst, wenn sich der Steuerungszustand ändert
        log_changed: Wird ausgelöst, wenn sich das Log ändert
    """
    
    # Signale
    state_changed = Signal()
    log_changed = Signal()
    
    def __init__(self):
        """Initialisierung."""
        super().__init__()
        self._service = None
        self._state = None
        self._log = None
    
    def set_service(self, service: FlightControlService):
        """Service setzen.
        
        Args:
            service: Flugsteuerungs-Service
        """
        self._service = service
        
        # Service-Signale verbinden
        self._service.state_changed.connect(self._update_state)
        self._service.log_changed.connect(self._update_log)
    
    @Property(str, notify=state_changed)
    def flight_mode(self) -> str:
        """Flugmodus."""
        return self._state.mode.value if self._state else FlightMode.MANUAL.value
    
    @Property(str, notify=state_changed)
    def control_mode(self) -> str:
        """Steuerungsmodus."""
        return self._state.control_mode.value if self._state else ControlMode.POSITION.value
    
    @Property(str, notify=state_changed)
    def control_status(self) -> str:
        """Steuerungsstatus."""
        return self._state.status.value if self._state else ControlStatus.IDLE.value
    
    @Property(bool, notify=state_changed)
    def is_manual_mode(self) -> bool:
        """Manueller Modus aktiv."""
        return self._state and self._state.mode == FlightMode.MANUAL
    
    @Property(bool, notify=state_changed)
    def is_assisted_mode(self) -> bool:
        """Unterstützter Modus aktiv."""
        return self._state and self._state.mode == FlightMode.ASSISTED
    
    @Property(bool, notify=state_changed)
    def is_autonomous_mode(self) -> bool:
        """Autonomer Modus aktiv."""
        return self._state and self._state.mode == FlightMode.AUTONOMOUS
    
    @Property(bool, notify=state_changed)
    def is_emergency_mode(self) -> bool:
        """Notfallmodus aktiv."""
        return self._state and self._state.mode == FlightMode.EMERGENCY
    
    @Property(bool, notify=state_changed)
    def is_idle(self) -> bool:
        """Inaktiv."""
        return self._state and self._state.status == ControlStatus.IDLE
    
    @Property(bool, notify=state_changed)
    def is_active(self) -> bool:
        """Aktiv."""
        return self._state and self._state.status == ControlStatus.ACTIVE
    
    @Property(bool, notify=state_changed)
    def is_completed(self) -> bool:
        """Abgeschlossen."""
        return self._state and self._state.status == ControlStatus.COMPLETED
    
    @Property(bool, notify=state_changed)
    def is_error(self) -> bool:
        """Fehler."""
        return self._state and self._state.status == ControlStatus.ERROR
    
    @Property(list, notify=log_changed)
    def log_events(self) -> List[str]:
        """Log-Events."""
        return [event.description for event in self._log.events] if self._log else []
    
    @Property(str, notify=log_changed)
    def last_event(self) -> str:
        """Letztes Event."""
        return self._log.last_event.description if self._log and self._log.last_event else ""
    
    def set_mode(self, mode: str):
        """Flugmodus setzen.
        
        Args:
            mode: Der zu setzende Flugmodus
        """
        if not self._service:
            raise FlightControlCommandError("No service set")
        
        try:
            self._service.set_mode(FlightMode(mode))
        except FlightControlError as e:
            self._handle_error(str(e))
    
    def set_control_mode(self, control_mode: str):
        """Steuerungsmodus setzen.
        
        Args:
            control_mode: Der zu setzende Steuerungsmodus
        """
        if not self._service:
            raise FlightControlCommandError("No service set")
        
        try:
            self._service.set_control_mode(ControlMode(control_mode))
        except FlightControlError as e:
            self._handle_error(str(e))
    
    def hold_position(self):
        """Hält die aktuelle Position."""
        if not self._service:
            raise FlightControlCommandError("No service set")
        
        try:
            self._service.hold_position()
        except FlightControlError as e:
            self._handle_error(str(e))
    
    def move_to_position(self, position: Dict[str, float]):
        """Bewegt sich zu einer Position.
        
        Args:
            position: Die Zielposition (latitude, longitude, altitude)
        """
        if not self._service:
            raise FlightControlCommandError("No service set")
        
        try:
            self._service.move_to_position(position)
        except FlightControlError as e:
            self._handle_error(str(e))
    
    def set_velocity(self, velocity: Dict[str, float]):
        """Setzt die Geschwindigkeit.
        
        Args:
            velocity: Die Zielgeschwindigkeit (vx, vy, vz)
        """
        if not self._service:
            raise FlightControlCommandError("No service set")
        
        try:
            self._service.set_velocity(velocity)
        except FlightControlError as e:
            self._handle_error(str(e))
    
    def rotate_to_attitude(self, attitude: Dict[str, float]):
        """Rotiert zu einer Attitude.
        
        Args:
            attitude: Die Zielattitude (roll, pitch, yaw)
        """
        if not self._service:
            raise FlightControlCommandError("No service set")
        
        try:
            self._service.rotate_to_attitude(attitude)
        except FlightControlError as e:
            self._handle_error(str(e))
    
    def set_rate(self, rate: Dict[str, float]):
        """Setzt die Rotationsrate.
        
        Args:
            rate: Die Zielrotationsrate (roll_rate, pitch_rate, yaw_rate)
        """
        if not self._service:
            raise FlightControlCommandError("No service set")
        
        try:
            self._service.set_rate(rate)
        except FlightControlError as e:
            self._handle_error(str(e))
    
    def set_thrust(self, thrust: float):
        """Setzt den Schub.
        
        Args:
            thrust: Der zu setzende Schub (0.0 bis 1.0)
        """
        if not self._service:
            raise FlightControlCommandError("No service set")
        
        try:
            self._service.set_thrust(thrust)
        except FlightControlError as e:
            self._handle_error(str(e))
    
    def emergency_stop(self):
        """Führt einen Notstopp durch."""
        if not self._service:
            raise FlightControlCommandError("No service set")
        
        try:
            self._service.emergency_stop()
        except FlightControlError as e:
            self._handle_error(str(e))
    
    def _update_state(self):
        """Steuerungszustand aktualisieren."""
        self._state = self._service.state
        self.state_changed.emit()
    
    def _update_log(self):
        """Log aktualisieren."""
        self._log = self._service.log
        self.log_changed.emit()
    
    def _handle_error(self, error_message: str):
        """Fehler behandeln.
        
        Args:
            error_message: Fehlermeldung
        """
        if self._state:
            self._state.status = ControlStatus.ERROR
            self.state_changed.emit() 