"""
Geofence-Service.
Implementiert die Geschäftslogik für Geofencing-Operationen.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import math

from PySide6.QtCore import QObject, Signal, Slot, QTimer

from ..models.flight_data import Position, Waypoint, Mission, FlightState, ControlCommand, MissionPlan
from ..enums import FlightStatus, FlightMode, ControlMode, CommandType, EmergencyProcedure
from ..telemetry.telemetry_manager import TelemetryManager
from ..connection.connection_manager import ConnectionManager

class GeofenceService(QObject):
    """Implementiert die Geschäftslogik für Geofencing-Operationen"""
    
    # Signale
    state_changed = Signal(FlightState)
    mode_changed = Signal(FlightMode)
    error_occurred = Signal(str)
    command_executed = Signal(ControlCommand)
    mission_started = Signal(Mission)
    mission_completed = Signal(Mission)
    mission_aborted = Signal(Mission)
    emergency_triggered = Signal(EmergencyProcedure)
    geofence_violation = Signal(Position)  # Neues Signal für Geofence-Verletzungen
    
    def __init__(self, telemetry_manager: Optional[TelemetryManager] = None,
                 connection_manager: Optional[ConnectionManager] = None):
        """
        Initialisiert den Geofence-Service.
        
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
        
        # Geofence-Parameter
        self._geofence_active = False
        self._geofence_center = Position()  # Zentrum des Geofence-Bereichs
        self._geofence_radius = 100.0  # Radius in Metern
        self._max_altitude = 50.0  # Maximale Höhe in Metern
        self._home_position = Position()  # Home-Position für RTH
        
        # Initialisiere die Position-Objekte mit Standardwerten
        self._state.gps_geofence = Position(x=0.0, y=0.0, z=0.0)
        self._state.gps_position = Position(x=0.0, y=0.0, z=0.0)
        self._state.gps_home = Position(x=0.0, y=0.0, z=0.0)
        self._state.gps_origin = Position(x=0.0, y=0.0, z=0.0)
        self._state.gps_waypoint = Position(x=0.0, y=0.0, z=0.0)
        self._state.gps_target = Position(x=0.0, y=0.0, z=0.0)
        self._state.gps_obstacle = Position(x=0.0, y=0.0, z=0.0)
        self._state.gps_landing = Position(x=0.0, y=0.0, z=0.0)
        self._state.gps_takeoff = Position(x=0.0, y=0.0, z=0.0)
        self._state.gps_mission = Position(x=0.0, y=0.0, z=0.0)
        self._state.gps_emergency = Position(x=0.0, y=0.0, z=0.0)
        self._state.gps_collision = Position(x=0.0, y=0.0, z=0.0)
        self._state.gps_flight = Position(x=0.0, y=0.0, z=0.0)
        self._state.gps_control = Position(x=0.0, y=0.0, z=0.0)
        self._state.gps_safety = Position(x=0.0, y=0.0, z=0.0)
        
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
        
    def set_geofence_parameters(self, center: Position, radius: float, max_altitude: float) -> None:
        """
        Setzt die Geofence-Parameter.
        
        Args:
            center: Zentrum des Geofence-Bereichs
            radius: Radius in Metern
            max_altitude: Maximale Höhe in Metern
        """
        self._geofence_center = center
        self._geofence_radius = radius
        self._max_altitude = max_altitude
        
    def set_home_position(self, position: Position) -> None:
        """
        Setzt die Home-Position.
        
        Args:
            position: Home-Position
        """
        self._home_position = position
        
    def enable_geofence(self) -> bool:
        """
        Aktiviert den Geofence.
        
        Returns:
            True wenn erfolgreich, sonst False
        """
        if self._geofence_active:
            self._set_error("Geofence bereits aktiv")
            return False
            
        self._geofence_active = True
        return True
        
    def disable_geofence(self) -> bool:
        """
        Deaktiviert den Geofence.
        
        Returns:
            True wenn erfolgreich, sonst False
        """
        if not self._geofence_active:
            self._set_error("Geofence nicht aktiv")
            return False
            
        self._geofence_active = False
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
        
        # Geofence prüfen
        if self._geofence_active:
            self._check_geofence()
            
    def _check_geofence(self) -> None:
        """
        Prüft ob der aktuelle Flugzustand den Geofence verletzt.
        """
        # Distanz zum Zentrum berechnen
        dx = self._state.position.x - self._geofence_center.x
        dy = self._state.position.y - self._geofence_center.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Höhe prüfen
        if self._state.position.z > self._max_altitude:
            self._handle_geofence_violation()
            return
            
        # Radius prüfen
        if distance > self._geofence_radius:
            self._handle_geofence_violation()
            return
            
    def _handle_geofence_violation(self) -> None:
        """
        Behandelt eine Geofence-Verletzung.
        """
        # Verletzung signalisieren
        self.geofence_violation.emit(self._state.position)
        
        # Notfall-Prozedur ausführen
        self.execute_emergency_procedure(EmergencyProcedure.RETURN_TO_HOME)
        
    def _can_change_mode(self, mode: FlightMode) -> bool:
        """
        Prüft ob ein Modus-Wechsel erlaubt ist.
        
        Args:
            mode: Neuer Modus
            
        Returns:
            True wenn erlaubt, sonst False
        """
        # TODO: Implementierung der Modus-Wechsel-Prüfung
        return True
        
    def _can_execute_command(self, command: ControlCommand) -> bool:
        """
        Prüft ob ein Befehl ausgeführt werden darf.
        
        Args:
            command: Zu prüfender Befehl
            
        Returns:
            True wenn erlaubt, sonst False
        """
        # TODO: Implementierung der Befehls-Prüfung
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
        
    @Slot(Mission)
    def start_mission(self, mission: Mission) -> bool:
        """
        Startet eine Mission.
        
        Args:
            mission: Mission
            
        Returns:
            True wenn erfolgreich, sonst False
        """
        if self._state.status != FlightStatus.ARMED:
            self._set_error("System nicht scharf")
            return False
            
        # Mission starten
        self._set_state(FlightStatus.FLYING)
        self.mission_started.emit(mission)
        return True
        
    @Slot()
    def pause_mission(self) -> bool:
        """
        Pausiert die aktuelle Mission.
        
        Returns:
            True wenn erfolgreich, sonst False
        """
        if self._state.status != FlightStatus.FLYING:
            self._set_error("Keine aktive Mission")
            return False
            
        return True
        
    @Slot()
    def resume_mission(self) -> bool:
        """
        Setzt die aktuelle Mission fort.
        
        Returns:
            True wenn erfolgreich, sonst False
        """
        if self._state.status != FlightStatus.FLYING:
            self._set_error("Keine aktive Mission")
            return False
            
        return True
        
    @Slot()
    def abort_mission(self) -> bool:
        """
        Bricht die aktuelle Mission ab.
        
        Returns:
            True wenn erfolgreich, sonst False
        """
        if self._state.status != FlightStatus.FLYING:
            self._set_error("Keine aktive Mission")
            return False
            
        # Status aktualisieren
        self._set_state(FlightStatus.ARMED)
        return True
        
    @Slot(EmergencyProcedure)
    def execute_emergency_procedure(self, procedure: EmergencyProcedure) -> bool:
        """
        Führt eine Notfallprozedur aus.
        
        Args:
            procedure: Notfallprozedur
            
        Returns:
            True wenn erfolgreich, sonst False
        """
        # Status aktualisieren
        self._set_state(FlightStatus.EMERGENCY)
        self.emergency_triggered.emit(procedure)
        return True 