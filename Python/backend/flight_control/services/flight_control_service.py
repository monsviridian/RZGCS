"""Flugsteuerungs-Service.

Dieser Service implementiert die Flugsteuerungslogik für das UAV-System. Er verwaltet
den Flugzustand, führt Befehle aus und überwacht den Flugbetrieb.

Funktionen:
- Flugmodus-Verwaltung
- Arming/Disarming
- Start/Landung
- Flugsteuerung
- Fehlerbehandlung
- Statistiken-Tracking
- Logging

Beispiel:
    service = FlightControlService()
    service.activate()
    service.arm()
    service.set_mode(FlightMode.STABILIZE)
    service.takeoff()
    service.land()
    service.disarm()
    service.deactivate()
"""

from datetime import datetime
from typing import Optional, Dict, Any
from PySide6.QtCore import QObject, Signal, Slot

from ..models.flight_control_data import (
    FlightMode,
    FlightStatus,
    FlightStatistics,
    FlightEvent,
    FlightLog,
    FlightError,
    FlightValidationError,
    FlightCommandError,
    FlightModeError,
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
    FlightControlStateError,
)
from ..models.flight_data import Position, Waypoint, Mission, FlightState, ControlCommand, MissionPlan

class FlightControlService(QObject):
    """Flugsteuerungs-Service.
    
    Dieser Service implementiert die Flugsteuerungslogik für das UAV-System.
    
    Attributes:
        state (FlightState): Aktueller Flugzustand
        statistics (FlightStatistics): Flugstatistiken
        log (FlightLog): Fluglog
        
    Signals:
        state_changed: Wird ausgelöst, wenn sich der Flugzustand ändert
        statistics_changed: Wird ausgelöst, wenn sich die Statistiken ändern
        log_changed: Wird ausgelöst, wenn sich das Log ändert
    """
    
    # Signale
    state_changed = Signal()
    statistics_changed = Signal()
    log_changed = Signal()
    
    def __init__(self):
        """Initialisierung."""
        super().__init__()
        self._state = FlightState(
            position=Position(0.0, 0.0, 0.0),
            mode=FlightMode.MANUAL,
            armed=False,
            status=FlightStatus.DISARMED,
            parameters={}
        )
        self._statistics = FlightStatistics()
        self._log = FlightLog()
    
    def activate(self):
        """Service aktivieren.
        
        Raises:
            FlightCommandError: Wenn der Service bereits aktiv ist
        """
        if self._state.is_active:
            raise FlightCommandError("Service is already active")
        
        self._state.update(
            is_active=True,
            status=FlightStatus.ACTIVE
        )
        self._add_event(FlightEvent("ACTIVATION", "Service activated"))
        self.state_changed.emit()
    
    def deactivate(self):
        """Service deaktivieren.
        
        Raises:
            FlightCommandError: Wenn der Service nicht aktiv ist
        """
        if not self._state.is_active:
            raise FlightCommandError("Service is not active")
        
        if self._state.is_armed:
            self.disarm()
        
        self._state.update(
            is_active=False,
            status=FlightStatus.INACTIVE
        )
        self._add_event(FlightEvent("DEACTIVATION", "Service deactivated"))
        self.state_changed.emit()
    
    def arm(self):
        """UAV scharfschalten.
        
        Raises:
            FlightCommandError: Wenn der Service nicht aktiv ist
            FlightCommandError: Wenn das UAV bereits scharfgeschaltet ist
        """
        if not self._state.is_active:
            raise FlightCommandError("Service is not active")
        
        if self._state.is_armed:
            raise FlightCommandError("UAV is already armed")
        
        self._state.update(
            is_armed=True,
            status=FlightStatus.ARMED
        )
        self._add_event(FlightEvent("ARMING", "UAV armed"))
        self.state_changed.emit()
    
    def disarm(self):
        """UAV entschärfen.
        
        Raises:
            FlightCommandError: Wenn der Service nicht aktiv ist
            FlightCommandError: Wenn das UAV nicht scharfgeschaltet ist
        """
        if not self._state.is_active:
            raise FlightCommandError("Service is not active")
        
        if not self._state.is_armed:
            raise FlightCommandError("UAV is not armed")
        
        if self._state.is_flying:
            self.land()
        
        self._state.update(
            is_armed=False,
            status=FlightStatus.DISARMED
        )
        self._add_event(FlightEvent("DISARMING", "UAV disarmed"))
        self.state_changed.emit()
    
    def set_mode(self, mode: FlightMode):
        """Flugmodus setzen.
        
        Args:
            mode: Neuer Flugmodus
            
        Raises:
            FlightCommandError: Wenn der Service nicht aktiv ist
            FlightModeError: Wenn der Modus ungültig ist
        """
        if not self._state.is_active:
            raise FlightCommandError("Service is not active")
        
        if not isinstance(mode, FlightMode):
            raise FlightModeError(f"Invalid flight mode: {mode}")
        
        old_mode = self._state.mode
        self._state.update(mode=mode)
        self._statistics.mode_changes += 1
        self._statistics.calculate()
        
        self._add_event(FlightEvent(
            "MODE_CHANGE",
            f"Flight mode changed from {old_mode} to {mode}"
        ))
        
        self.state_changed.emit()
        self.statistics_changed.emit()
    
    def takeoff(self):
        """Start durchführen.
        
        Raises:
            FlightCommandError: Wenn der Service nicht aktiv ist
            FlightCommandError: Wenn das UAV nicht scharfgeschaltet ist
            FlightCommandError: Wenn das UAV bereits fliegt
        """
        if not self._state.is_active:
            raise FlightCommandError("Service is not active")
        
        if not self._state.is_armed:
            raise FlightCommandError("UAV is not armed")
        
        if self._state.is_flying:
            raise FlightCommandError("UAV is already flying")
        
        self._state.update(
            is_flying=True,
            is_taking_off=True,
            status=FlightStatus.TAKEOFF
        )
        self._statistics.total_takeoffs += 1
        self._statistics.calculate()
        
        self._add_event(FlightEvent("TAKEOFF", "UAV taking off"))
        
        self.state_changed.emit()
        self.statistics_changed.emit()
    
    def land(self):
        """Landung durchführen.
        
        Raises:
            FlightCommandError: Wenn der Service nicht aktiv ist
            FlightCommandError: Wenn das UAV nicht fliegt
        """
        if not self._state.is_active:
            raise FlightCommandError("Service is not active")
        
        if not self._state.is_flying:
            raise FlightCommandError("UAV is not flying")
        
        self._state.update(
            is_landing=True,
            status=FlightStatus.LANDING
        )
        
        self._add_event(FlightEvent("LANDING", "UAV landing"))
        self.state_changed.emit()
    
    def update_position(self, position: Dict[str, float]):
        """Position aktualisieren.
        
        Args:
            position: Neue Position (lat, lon, alt)
            
        Raises:
            FlightCommandError: Wenn der Service nicht aktiv ist
            FlightValidationError: Wenn die Position ungültig ist
        """
        if not self._state.is_active:
            raise FlightCommandError("Service is not active")
        
        if not isinstance(position, dict):
            raise FlightValidationError("Position must be a dictionary")
        
        required_keys = {"lat", "lon", "alt"}
        if not all(key in position for key in required_keys):
            raise FlightValidationError("Position must contain lat, lon, and alt")
        
        if not all(isinstance(position[key], (int, float)) for key in required_keys):
            raise FlightValidationError("Position values must be numeric")
        
        if position["alt"] < 0:
            raise FlightValidationError("Altitude cannot be negative")
        
        # Position aktualisieren und Statistiken berechnen
        self._statistics.max_altitude = max(self._statistics.max_altitude, position["alt"])
        self._statistics.calculate()
        
        self._add_event(FlightEvent(
            "POSITION_UPDATE",
            "Position updated",
            data=position
        ))
        
        self.statistics_changed.emit()
    
    def update_velocity(self, velocity: Dict[str, float]):
        """Geschwindigkeit aktualisieren.
        
        Args:
            velocity: Neue Geschwindigkeit (vx, vy, vz)
            
        Raises:
            FlightCommandError: Wenn der Service nicht aktiv ist
            FlightValidationError: Wenn die Geschwindigkeit ungültig ist
        """
        if not self._state.is_active:
            raise FlightCommandError("Service is not active")
        
        if not isinstance(velocity, dict):
            raise FlightValidationError("Velocity must be a dictionary")
        
        required_keys = {"vx", "vy", "vz"}
        if not all(key in velocity for key in required_keys):
            raise FlightValidationError("Velocity must contain vx, vy, and vz")
        
        if not all(isinstance(velocity[key], (int, float)) for key in required_keys):
            raise FlightValidationError("Velocity values must be numeric")
        
        # Geschwindigkeit berechnen und Statistiken aktualisieren
        speed = (velocity["vx"]**2 + velocity["vy"]**2 + velocity["vz"]**2)**0.5
        self._statistics.max_speed = max(self._statistics.max_speed, speed)
        self._statistics.calculate()
        
        self._add_event(FlightEvent(
            "VELOCITY_UPDATE",
            "Velocity updated",
            data=velocity
        ))
        
        self.statistics_changed.emit()
    
    def _handle_error(self, error_message: str):
        """Fehler behandeln.
        
        Args:
            error_message: Fehlermeldung
        """
        self._state.update(
            is_error=True,
            error_message=error_message,
            status=FlightStatus.ERROR
        )
        self._statistics.total_errors += 1
        self._statistics.calculate()
        
        self._add_event(FlightEvent("ERROR", error_message))
        
        self.state_changed.emit()
        self.statistics_changed.emit()
    
    def _reset_error(self):
        """Fehler zurücksetzen."""
        self._state.update(
            is_error=False,
            error_message=None
        )
        
        self._add_event(FlightEvent("ERROR_RESET", "Error state reset"))
        self.state_changed.emit()
    
    def _add_event(self, event: FlightEvent):
        """Event zum Log hinzufügen.
        
        Args:
            event: Event
        """
        self._log.add_event(event)
        self.log_changed.emit()

    def set_control_mode(self, control_mode: ControlMode):
        """Setzt den Steuerungsmodus.
        
        Args:
            control_mode: Der zu setzende Steuerungsmodus
        """
        try:
            self._state.control_mode = control_mode
            self._state.timestamp = datetime.now()
            self._log.add_event(ControlEvent(
                event_type="CONTROL_MODE_CHANGE",
                description=f"Control mode changed to {control_mode.value}",
                timestamp=datetime.now()
            ))
        except Exception as e:
            raise FlightControlStateError(f"Failed to set control mode: {str(e)}")
    
    def set_status(self, status: ControlStatus):
        """Setzt den Steuerungsstatus.
        
        Args:
            status: Der zu setzende Steuerungsstatus
        """
        try:
            self._state.status = status
            self._state.timestamp = datetime.now()
            self._log.add_event(ControlEvent(
                event_type="STATUS_CHANGE",
                description=f"Control status changed to {status.value}",
                timestamp=datetime.now()
            ))
        except Exception as e:
            raise FlightControlStateError(f"Failed to set control status: {str(e)}")
    
    def add_input(self, input: ControlInput):
        """Fügt eine Steuerungseingabe hinzu.
        
        Args:
            input: Die hinzuzufügende Steuerungseingabe
        """
        try:
            self._state.inputs.append(input)
            self._state.timestamp = datetime.now()
            self._log.add_event(ControlEvent(
                event_type="INPUT_ADDED",
                description=f"Control input added: {input.command.value} on {input.axis.value}",
                timestamp=datetime.now()
            ))
        except Exception as e:
            raise FlightControlStateError(f"Failed to add control input: {str(e)}")
    
    def add_output(self, output: ControlOutput):
        """Fügt eine Steuerungsausgabe hinzu.
        
        Args:
            output: Die hinzuzufügende Steuerungsausgabe
        """
        try:
            self._state.outputs.append(output)
            self._state.timestamp = datetime.now()
            self._log.add_event(ControlEvent(
                event_type="OUTPUT_ADDED",
                description=f"Control output added: {output.value} on {output.axis.value}",
                timestamp=datetime.now()
            ))
        except Exception as e:
            raise FlightControlStateError(f"Failed to add control output: {str(e)}")
    
    def clear_inputs(self):
        """Löscht alle Steuerungseingaben."""
        try:
            self._state.inputs.clear()
            self._state.timestamp = datetime.now()
            self._log.add_event(ControlEvent(
                event_type="INPUTS_CLEARED",
                description="All control inputs cleared",
                timestamp=datetime.now()
            ))
        except Exception as e:
            raise FlightControlStateError(f"Failed to clear control inputs: {str(e)}")
    
    def clear_outputs(self):
        """Löscht alle Steuerungsausgaben."""
        try:
            self._state.outputs.clear()
            self._state.timestamp = datetime.now()
            self._log.add_event(ControlEvent(
                event_type="OUTPUTS_CLEARED",
                description="All control outputs cleared",
                timestamp=datetime.now()
            ))
        except Exception as e:
            raise FlightControlStateError(f"Failed to clear control outputs: {str(e)}")
    
    def hold_position(self):
        """Hält die aktuelle Position."""
        try:
            if self._state.mode == FlightMode.MANUAL:
                raise FlightControlCommandError("Cannot hold position in manual mode")
            
            for axis in ControlAxis:
                self.add_input(ControlInput(
                    axis=axis,
                    command=ControlCommand.HOLD,
                    value=0.0,
                    timestamp=datetime.now()
                ))
            
            self._log.add_event(ControlEvent(
                event_type="POSITION_HOLD",
                description="Holding current position",
                timestamp=datetime.now()
            ))
        except Exception as e:
            raise FlightControlCommandError(f"Failed to hold position: {str(e)}")
    
    def move_to_position(self, position: Dict[str, float]):
        """Bewegt sich zu einer Position.
        
        Args:
            position: Die Zielposition (latitude, longitude, altitude)
        """
        try:
            if self._state.mode == FlightMode.MANUAL:
                raise FlightControlCommandError("Cannot move to position in manual mode")
            
            # Validierung
            if not all(key in position for key in ['latitude', 'longitude', 'altitude']):
                raise FlightControlValidationError("Invalid position format")
            
            # Steuerungseingaben
            self.add_input(ControlInput(
                axis=ControlAxis.ROLL,
                command=ControlCommand.MOVE,
                value=position['longitude'],
                timestamp=datetime.now()
            ))
            self.add_input(ControlInput(
                axis=ControlAxis.PITCH,
                command=ControlCommand.MOVE,
                value=position['latitude'],
                timestamp=datetime.now()
            ))
            self.add_input(ControlInput(
                axis=ControlAxis.THRUST,
                command=ControlCommand.MOVE,
                value=position['altitude'],
                timestamp=datetime.now()
            ))
            
            self._log.add_event(ControlEvent(
                event_type="POSITION_MOVE",
                description=f"Moving to position: {position}",
                timestamp=datetime.now()
            ))
        except Exception as e:
            raise FlightControlCommandError(f"Failed to move to position: {str(e)}")
    
    def rotate_to_attitude(self, attitude: Dict[str, float]):
        """Rotiert zu einer Attitude.
        
        Args:
            attitude: Die Zielattitude (roll, pitch, yaw)
        """
        try:
            if self._state.mode == FlightMode.MANUAL:
                raise FlightControlCommandError("Cannot rotate to attitude in manual mode")
            
            # Validierung
            if not all(key in attitude for key in ['roll', 'pitch', 'yaw']):
                raise FlightControlValidationError("Invalid attitude format")
            
            # Steuerungseingaben
            self.add_input(ControlInput(
                axis=ControlAxis.ROLL,
                command=ControlCommand.ROTATE,
                value=attitude['roll'],
                timestamp=datetime.now()
            ))
            self.add_input(ControlInput(
                axis=ControlAxis.PITCH,
                command=ControlCommand.ROTATE,
                value=attitude['pitch'],
                timestamp=datetime.now()
            ))
            self.add_input(ControlInput(
                axis=ControlAxis.YAW,
                command=ControlCommand.ROTATE,
                value=attitude['yaw'],
                timestamp=datetime.now()
            ))
            
            self._log.add_event(ControlEvent(
                event_type="ATTITUDE_ROTATE",
                description=f"Rotating to attitude: {attitude}",
                timestamp=datetime.now()
            ))
        except Exception as e:
            raise FlightControlCommandError(f"Failed to rotate to attitude: {str(e)}")
    
    def set_thrust(self, thrust: float):
        """Setzt den Schub.
        
        Args:
            thrust: Der zu setzende Schub (0.0 bis 1.0)
        """
        try:
            # Validierung
            if not 0.0 <= thrust <= 1.0:
                raise FlightControlValidationError("Invalid thrust value")
            
            # Steuerungseingabe
            self.add_input(ControlInput(
                axis=ControlAxis.THRUST,
                command=ControlCommand.THRUST,
                value=thrust,
                timestamp=datetime.now()
            ))
            
            self._log.add_event(ControlEvent(
                event_type="THRUST_SET",
                description=f"Setting thrust to {thrust}",
                timestamp=datetime.now()
            ))
        except Exception as e:
            raise FlightControlCommandError(f"Failed to set thrust: {str(e)}")
    
    def emergency_stop(self):
        """Führt einen Notstopp durch."""
        try:
            # Notfallmodus setzen
            self.set_mode(FlightMode.EMERGENCY)
            
            # Schub auf 0 setzen
            self.set_thrust(0.0)
            
            # Status auf Fehler setzen
            self.set_status(ControlStatus.ERROR)
            
            self._log.add_event(ControlEvent(
                event_type="EMERGENCY_STOP",
                description="Emergency stop executed",
                timestamp=datetime.now()
            ))
        except Exception as e:
            raise FlightControlCommandError(f"Failed to execute emergency stop: {str(e)}")
    
    @property
    def state(self) -> FlightState:
        """Gibt den aktuellen Flugzustand zurück.
        
        Returns:
            Der aktuelle Flugzustand
        """
        return self._state
    
    @property
    def log(self) -> FlightLog:
        """Gibt das aktuelle Log zurück.
        
        Returns:
            Das aktuelle Log
        """
        return self._log 