"""
Kollisionsvermeidungs-Service.
Implementiert die Geschäftslogik für Kollisionsvermeidungs-Operationen.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import math

from PySide6.QtCore import QObject, Signal, Slot, QTimer

from ..models.flight_data import Position, Waypoint, Mission, FlightState, ControlCommand, MissionPlan
from ..enums import FlightStatus, FlightMode, ControlMode, CommandType, EmergencyProcedure
from ..telemetry.telemetry_manager import TelemetryManager
from ..connection.connection_manager import ConnectionManager

class Obstacle:
    """Repräsentiert ein Hindernis"""
    
    def __init__(self, id: str, position: Position, velocity: Position, size: float):
        """
        Initialisiert ein Hindernis.
        
        Args:
            id: Eindeutige ID
            position: Position
            velocity: Geschwindigkeit
            size: Größe in Metern
        """
        self.id = id
        self.position = position
        self.velocity = velocity
        self.size = size
        self.last_update = datetime.now()

class CollisionService(QObject):
    """Implementiert die Geschäftslogik für Kollisionsvermeidungs-Operationen"""
    
    # Signale
    state_changed = Signal(FlightState)
    mode_changed = Signal(FlightMode)
    error_occurred = Signal(str)
    command_executed = Signal(ControlCommand)
    mission_started = Signal(Mission)
    mission_completed = Signal(Mission)
    mission_aborted = Signal(Mission)
    emergency_triggered = Signal(EmergencyProcedure)
    obstacle_detected = Signal(Obstacle)  # Neues Signal für erkannte Hindernisse
    collision_warning = Signal(Position)  # Neues Signal für Kollisionswarnungen
    
    def __init__(self, telemetry_manager: Optional[TelemetryManager] = None,
                 connection_manager: Optional[ConnectionManager] = None):
        """
        Initialisiert den Kollisionsvermeidungs-Service.
        
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
        
        # Kollisionsvermeidungs-Parameter
        self._collision_avoidance_active = False
        self._safety_distance = 10.0  # Sicherheitsabstand in Metern
        self._reaction_time = 1.0  # Reaktionszeit in Sekunden
        self._obstacles: Dict[str, Obstacle] = {}  # Erkannte Hindernisse
        
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
        
    def set_collision_parameters(self, safety_distance: float, reaction_time: float) -> None:
        """
        Setzt die Kollisionsvermeidungs-Parameter.
        
        Args:
            safety_distance: Sicherheitsabstand in Metern
            reaction_time: Reaktionszeit in Sekunden
        """
        self._safety_distance = safety_distance
        self._reaction_time = reaction_time
        
    def enable_collision_avoidance(self) -> bool:
        """
        Aktiviert die Kollisionsvermeidung.
        
        Returns:
            True wenn erfolgreich, sonst False
        """
        if self._collision_avoidance_active:
            self._set_error("Kollisionsvermeidung bereits aktiv")
            return False
            
        self._collision_avoidance_active = True
        return True
        
    def disable_collision_avoidance(self) -> bool:
        """
        Deaktiviert die Kollisionsvermeidung.
        
        Returns:
            True wenn erfolgreich, sonst False
        """
        if not self._collision_avoidance_active:
            self._set_error("Kollisionsvermeidung nicht aktiv")
            return False
            
        self._collision_avoidance_active = False
        return True
        
    def add_obstacle(self, obstacle: Obstacle) -> None:
        """
        Fügt ein Hindernis hinzu.
        
        Args:
            obstacle: Hindernis
        """
        self._obstacles[obstacle.id] = obstacle
        self.obstacle_detected.emit(obstacle)
        
    def remove_obstacle(self, obstacle_id: str) -> None:
        """
        Entfernt ein Hindernis.
        
        Args:
            obstacle_id: ID des Hindernisses
        """
        if obstacle_id in self._obstacles:
            del self._obstacles[obstacle_id]
            
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
        
        # Kollisionsvermeidung prüfen
        if self._collision_avoidance_active:
            self._check_collisions()
            
    def _check_collisions(self) -> None:
        """
        Prüft auf mögliche Kollisionen.
        """
        # Hindernisse prüfen
        for obstacle in self._obstacles.values():
            # Distanz berechnen
            dx = self._state.position.x - obstacle.position.x
            dy = self._state.position.y - obstacle.position.y
            dz = self._state.position.z - obstacle.position.z
            distance = math.sqrt(dx*dx + dy*dy + dz*dz)
            
            # Kollisionsabstand berechnen
            collision_distance = self._safety_distance + obstacle.size
            
            # Kollision prüfen
            if distance < collision_distance:
                self._handle_collision_warning(obstacle)
                return
                
            # Kollisionskurs prüfen
            if self._is_collision_course(obstacle):
                self._handle_collision_warning(obstacle)
                return
                
    def _is_collision_course(self, obstacle: Obstacle) -> bool:
        """
        Prüft ob ein Kollisionskurs vorliegt.
        
        Args:
            obstacle: Hindernis
            
        Returns:
            True wenn Kollisionskurs, sonst False
        """
        # Relativgeschwindigkeit berechnen
        vx = self._state.velocity.x - obstacle.velocity.x
        vy = self._state.velocity.y - obstacle.velocity.y
        vz = self._state.velocity.z - obstacle.velocity.z
        
        # Distanz berechnen
        dx = self._state.position.x - obstacle.position.x
        dy = self._state.position.y - obstacle.position.y
        dz = self._state.position.z - obstacle.position.z
        
        # Skalarprodukt für Bewegungsrichtung
        dot_product = vx*dx + vy*dy + vz*dz
        
        # Wenn negativ, bewegen sich die Objekte aufeinander zu
        return dot_product < 0
        
    def _handle_collision_warning(self, obstacle: Obstacle) -> None:
        """
        Behandelt eine Kollisionswarnung.
        
        Args:
            obstacle: Hindernis
        """
        # Warnung signalisieren
        self.collision_warning.emit(obstacle.position)
        
        # Ausweichmanöver einleiten
        self._execute_avoidance_maneuver(obstacle)
        
    def _execute_avoidance_maneuver(self, obstacle: Obstacle) -> None:
        """
        Führt ein Ausweichmanöver aus.
        
        Args:
            obstacle: Hindernis
        """
        # Ausweichrichtung berechnen
        dx = self._state.position.x - obstacle.position.x
        dy = self._state.position.y - obstacle.position.y
        dz = self._state.position.z - obstacle.position.z
        
        # Normalisieren
        length = math.sqrt(dx*dx + dy*dy + dz*dz)
        if length > 0:
            dx /= length
            dy /= length
            dz /= length
            
        # Ausweichbefehl erstellen
        command = ControlCommand(
            type=CommandType.MOVE_TO,
            parameters={
                "x": self._state.position.x + dx * self._safety_distance,
                "y": self._state.position.y + dy * self._safety_distance,
                "z": self._state.position.z + dz * self._safety_distance
            }
        )
        
        # Befehl ausführen
        self.execute_command(command)
        
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