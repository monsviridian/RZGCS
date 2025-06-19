"""
Notfall-Service.
Implementiert die Geschäftslogik für Notfall-Operationen.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import math

from PySide6.QtCore import QObject, Signal, Slot, QTimer

from flight_control.models.flight_data import Position, Waypoint, Mission, FlightState, ControlCommand, MissionPlan
from flight_control.enums import FlightStatus, FlightMode, ControlMode, CommandType, EmergencyProcedure
from flight_control.telemetry.telemetry_manager import TelemetryManager
from flight_control.connection.connection_manager import ConnectionManager

class EmergencyService(QObject):
    """Implementiert die Geschäftslogik für Notfall-Operationen"""
    
    # Signale
    state_changed = Signal(FlightState)
    mode_changed = Signal(FlightMode)
    error_occurred = Signal(str)
    command_executed = Signal(ControlCommand)
    mission_started = Signal(Mission)
    mission_completed = Signal(Mission)
    mission_aborted = Signal(Mission)
    emergency_triggered = Signal(EmergencyProcedure)
    emergency_resolved = Signal(EmergencyProcedure)  # Neues Signal für behobene Notfälle
    
    def __init__(self, telemetry_manager: Optional[TelemetryManager] = None,
                 connection_manager: Optional[ConnectionManager] = None):
        """
        Initialisiert den Notfall-Service.
        
        Args:
            telemetry_manager: Optional: Telemetrie-Manager
            connection_manager: Optional: Verbindungs-Manager
        """
        super().__init__()
        
        # Manager setzen
        self._telemetry = telemetry_manager
        self._connection = connection_manager
        
        # Status und Modus
        self._state = FlightState(
            position=Position(0.0, 0.0, 0.0),
            mode=FlightMode.MANUAL,
            armed=False,
            status=FlightStatus.DISARMED,
            parameters={}
        )
        self._mode = FlightMode.MANUAL
        self._control_mode = ControlMode.BASIC
        
        # Notfall-Parameter
        self._emergency_active = False
        self._current_procedure: Optional[EmergencyProcedure] = None
        self._emergency_start_time: Optional[datetime] = None
        self._home_position = Position()  # Home-Position für RTH
        self._safe_altitude = 20.0  # Sichere Höhe in Metern
        self._max_emergency_duration = 300  # Maximale Notfall-Dauer in Sekunden
        
        # Timer für Statusaktualisierungen
        self._status_timer = QTimer()
        self._status_timer.timeout.connect(self._update_status)
        self._status_timer.start(100)  # 100ms
        
    def set_telemetry_manager(self, telemetry_manager: TelemetryManager) -> None:
        """
        Setzt den Telemetrie-Manager.
        
        Args:
            telemetry_manager: Telemetrie-Manager
        """
        self._telemetry = telemetry_manager
        
    def set_connection_manager(self, connection_manager: ConnectionManager) -> None:
        """
        Setzt den Verbindungs-Manager.
        
        Args:
            connection_manager: Verbindungs-Manager
        """
        self._connection = connection_manager
        
    @Slot(FlightMode)
    def set_mode(self, mode: FlightMode) -> bool:
        """
        Setzt den Flugmodus.
        
        Args:
            mode: Flugmodus
            
        Returns:
            True wenn erfolgreich, sonst False
        """
        # Prüfen ob Modus-Änderung erlaubt ist
        if not self._can_change_mode(mode):
            self._set_error(f"Modus-Änderung nicht erlaubt: {mode.name}")
            return False
            
        # Modus setzen
        self._mode = mode
        self.mode_changed.emit(mode)
        return True
        
    @Slot(ControlCommand)
    def execute_command(self, command: ControlCommand) -> bool:
        """
        Führt einen Steuerungsbefehl aus.
        
        Args:
            command: Steuerungsbefehl
            
        Returns:
            True wenn erfolgreich, sonst False
        """
        # Prüfen ob Befehl ausgeführt werden darf
        if not self._can_execute_command(command):
            self._set_error(f"Befehl nicht erlaubt: {command.type.name}")
            return False
            
        # Befehl ausführen
        success = self._execute_command(command)
        
        if success:
            self.command_executed.emit(command)
            
        return success
        
    def set_emergency_parameters(self, safe_altitude: float, max_duration: int) -> None:
        """
        Setzt die Notfall-Parameter.
        
        Args:
            safe_altitude: Sichere Höhe in Metern
            max_duration: Maximale Notfall-Dauer in Sekunden
        """
        self._safe_altitude = safe_altitude
        self._max_emergency_duration = max_duration
        
    def set_home_position(self, position: Position) -> None:
        """
        Setzt die Home-Position.
        
        Args:
            position: Home-Position
        """
        self._home_position = position
        
    @Slot(EmergencyProcedure)
    def execute_emergency_procedure(self, procedure: EmergencyProcedure) -> bool:
        """
        Führt eine Notfallprozedur aus.
        
        Args:
            procedure: Notfallprozedur
            
        Returns:
            True wenn erfolgreich, sonst False
        """
        if self._emergency_active:
            self._set_error("Notfall bereits aktiv")
            return False
            
        # Notfall starten
        self._emergency_active = True
        self._current_procedure = procedure
        self._emergency_start_time = datetime.now()
        
        # Status aktualisieren
        self._set_state(FlightStatus.EMERGENCY)
        self.emergency_triggered.emit(procedure)
        
        # Prozedur ausführen
        return self._execute_procedure(procedure)
        
    def resolve_emergency(self) -> bool:
        """
        Behebt den aktuellen Notfall.
        
        Returns:
            True wenn erfolgreich, sonst False
        """
        if not self._emergency_active:
            self._set_error("Kein aktiver Notfall")
            return False
            
        # Notfall beenden
        self._emergency_active = False
        procedure = self._current_procedure
        self._current_procedure = None
        self._emergency_start_time = None
        
        # Status aktualisieren
        self._set_state(FlightStatus.ARMED)
        self.emergency_resolved.emit(procedure)
        
        return True
        
    @Slot()
    def _update_status(self) -> None:
        """
        Aktualisiert den Flugzustand.
        """
        if not self._telemetry:
            return
            
        # Telemetrie-Daten abrufen
        telemetry_data = self._telemetry.get_telemetry_data()
        
        if not telemetry_data:
            return
            
        # Status aktualisieren
        self._state.position = telemetry_data.get("position", Position())
        self._state.velocity = telemetry_data.get("velocity", Position())
        self._state.acceleration = telemetry_data.get("acceleration", Position())
        self._state.attitude = telemetry_data.get("attitude", Position())
        self._state.angular_velocity = telemetry_data.get("angular_velocity", Position())
        self._state.battery_level = telemetry_data.get("battery_level", 0.0)
        self._state.signal_strength = telemetry_data.get("signal_strength", 0.0)
        
        # Status-Änderung signalisieren
        self.state_changed.emit(self._state)
        
        # Notfall prüfen
        if self._emergency_active:
            self._check_emergency()
            
    def _check_emergency(self) -> None:
        """
        Prüft den aktuellen Notfall-Status.
        """
        if not self._emergency_start_time:
            return
            
        # Zeit seit Notfallbeginn
        duration = (datetime.now() - self._emergency_start_time).total_seconds()
        
        # Maximale Dauer prüfen
        if duration > self._max_emergency_duration:
            self._handle_emergency_timeout()
            return
            
        # Prozedur-Status prüfen
        if self._current_procedure:
            self._check_procedure_status()
            
    def _check_procedure_status(self) -> None:
        """
        Prüft den Status der aktuellen Notfallprozedur.
        """
        if not self._current_procedure:
            return
            
        # Prozedur-spezifische Prüfungen
        if self._current_procedure == EmergencyProcedure.RETURN_TO_HOME:
            self._check_rth_status()
        elif self._current_procedure == EmergencyProcedure.LAND:
            self._check_landing_status()
        elif self._current_procedure == EmergencyProcedure.HOVER:
            self._check_hover_status()
            
    def _check_rth_status(self) -> None:
        """
        Prüft den Status der RTH-Prozedur.
        """
        # Distanz zur Home-Position
        dx = self._state.position.x - self._home_position.x
        dy = self._state.position.y - self._home_position.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Wenn nahe genug an Home-Position
        if distance < 1.0:  # 1 Meter Toleranz
            self.resolve_emergency()
            
    def _check_landing_status(self) -> None:
        """
        Prüft den Status der Lande-Prozedur.
        """
        # Wenn am Boden
        if self._state.position.z < 0.1:  # 10cm Toleranz
            self.resolve_emergency()
            
    def _check_hover_status(self) -> None:
        """
        Prüft den Status der Hover-Prozedur.
        """
        # Wenn in sicherer Höhe
        if self._state.position.z >= self._safe_altitude:
            self.resolve_emergency()
            
    def _handle_emergency_timeout(self) -> None:
        """
        Behandelt einen Notfall-Timeout.
        """
        # Notfall beenden
        self.resolve_emergency()
        
        # Notfall-Landung einleiten
        self.execute_emergency_procedure(EmergencyProcedure.LAND)
        
    def _execute_procedure(self, procedure: EmergencyProcedure) -> bool:
        """
        Führt eine Notfallprozedur aus.
        
        Args:
            procedure: Notfallprozedur
            
        Returns:
            True wenn erfolgreich, sonst False
        """
        if procedure == EmergencyProcedure.RETURN_TO_HOME:
            return self._execute_rth()
        elif procedure == EmergencyProcedure.LAND:
            return self._execute_landing()
        elif procedure == EmergencyProcedure.HOVER:
            return self._execute_hover()
        else:
            self._set_error(f"Unbekannte Notfallprozedur: {procedure.name}")
            return False
            
    def _execute_rth(self) -> bool:
        """
        Führt die RTH-Prozedur aus.
        
        Returns:
            True wenn erfolgreich, sonst False
        """
        # RTH-Befehl erstellen
        command = ControlCommand(
            type=CommandType.MOVE_TO,
            parameters={
                "x": self._home_position.x,
                "y": self._home_position.y,
                "z": self._safe_altitude
            }
        )
        
        # Befehl ausführen
        return self.execute_command(command)
        
    def _execute_landing(self) -> bool:
        """
        Führt die Lande-Prozedur aus.
        
        Returns:
            True wenn erfolgreich, sonst False
        """
        # Lande-Befehl erstellen
        command = ControlCommand(
            type=CommandType.LAND,
            parameters={}
        )
        
        # Befehl ausführen
        return self.execute_command(command)
        
    def _execute_hover(self) -> bool:
        """
        Führt die Hover-Prozedur aus.
        
        Returns:
            True wenn erfolgreich, sonst False
        """
        # Hover-Befehl erstellen
        command = ControlCommand(
            type=CommandType.HOVER,
            parameters={
                "altitude": self._safe_altitude
            }
        )
        
        # Befehl ausführen
        return self.execute_command(command)
        
    def _can_change_mode(self, mode: FlightMode) -> bool:
        """
        Prüft ob ein Modus-Wechsel erlaubt ist.
        
        Args:
            mode: Neuer Modus
            
        Returns:
            True wenn erlaubt, sonst False
        """
        # Im Notfall nur bestimmte Modus-Wechsel erlauben
        if self._emergency_active:
            return mode in [FlightMode.EMERGENCY, FlightMode.MANUAL]
            
        return True
        
    def _can_execute_command(self, command: ControlCommand) -> bool:
        """
        Prüft ob ein Befehl ausgeführt werden darf.
        
        Args:
            command: Zu prüfender Befehl
            
        Returns:
            True wenn erlaubt, sonst False
        """
        # Im Notfall nur Notfall-Befehle erlauben
        if self._emergency_active:
            return command.type in [
                CommandType.MOVE_TO,
                CommandType.LAND,
                CommandType.HOVER
            ]
            
        return True
        
    def _execute_command(self, command: ControlCommand) -> bool:
        """
        Führt einen Steuerungsbefehl aus.
        
        Args:
            command: Steuerungsbefehl
            
        Returns:
            True wenn erfolgreich, sonst False
        """
        if not self._connection:
            return False
            
        # Befehl senden
        return self._connection.send_command(command)
        
    def _set_state(self, status: FlightStatus) -> None:
        """
        Setzt den Flugzustand.
        
        Args:
            status: Neuer Status
        """
        if self._state.status != status:
            self._state.status = status
            self.state_changed.emit(self._state)
            
    def _set_error(self, message: str) -> None:
        """
        Setzt eine Fehlermeldung.
        
        Args:
            message: Fehlermeldung
        """
        self.error_occurred.emit(message) 