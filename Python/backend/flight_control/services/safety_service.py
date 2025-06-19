"""
Sicherheits-Service.
Implementiert die Geschäftslogik für Sicherheits-Operationen.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import math

from PySide6.QtCore import QObject, Signal, Slot, QTimer

from ..models.flight_data import Position, Waypoint, Mission, FlightState, ControlCommand, MissionPlan
from ..enums import FlightStatus, FlightMode, ControlMode, CommandType, EmergencyProcedure
from ..telemetry.telemetry_manager import TelemetryManager
from ..connection.connection_manager import ConnectionManager

class SafetyService(QObject):
    """Implementiert die Geschäftslogik für Sicherheits-Operationen"""
    
    # Signale
    state_changed = Signal(FlightState)
    mode_changed = Signal(FlightMode)
    error_occurred = Signal(str)
    command_executed = Signal(ControlCommand)
    mission_started = Signal(Mission)
    mission_completed = Signal(Mission)
    mission_aborted = Signal(Mission)
    emergency_triggered = Signal(EmergencyProcedure)
    safety_violation = Signal(str)  # Neues Signal für Sicherheitsverletzungen
    safety_warning = Signal(str)  # Neues Signal für Sicherheitswarnungen
    safety_cleared = Signal(str)  # Neues Signal für behobene Sicherheitsprobleme
    
    def __init__(self, telemetry_manager: Optional[TelemetryManager] = None,
                 connection_manager: Optional[ConnectionManager] = None):
        """
        Initialisiert den Sicherheits-Service.
        
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
        
        # Sicherheits-Parameter
        self._safety_active = False
        self._min_battery_level = 0.2  # Minimaler Batteriestand (20%)
        self._min_signal_strength = 0.3  # Minimale Signalstärke (30%)
        self._max_velocity = 10.0  # Maximale Geschwindigkeit in m/s
        self._max_acceleration = 5.0  # Maximale Beschleunigung in m/s²
        self._max_angular_velocity = 2.0  # Maximale Winkelgeschwindigkeit in rad/s
        self._max_altitude = 100.0  # Maximale Höhe in m
        self._min_altitude = 0.5  # Minimale Höhe in m
        self._safety_radius = 50.0  # Sicherheitsradius in m
        self._home_position = Position(0.0, 0.0, 0.0)  # Home-Position
        
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
        
    def set_safety_parameters(self, min_battery: float, min_signal: float,
                            max_velocity: float, max_acceleration: float,
                            max_angular_velocity: float, max_altitude: float,
                            min_altitude: float, safety_radius: float) -> None:
        """
        Setzt die Sicherheits-Parameter.
        
        Args:
            min_battery: Minimaler Batteriestand
            min_signal: Minimale Signalstärke
            max_velocity: Maximale Geschwindigkeit in m/s
            max_acceleration: Maximale Beschleunigung in m/s²
            max_angular_velocity: Maximale Winkelgeschwindigkeit in rad/s
            max_altitude: Maximale Höhe in m
            min_altitude: Minimale Höhe in m
            safety_radius: Sicherheitsradius in m
        """
        self._min_battery_level = min_battery
        self._min_signal_strength = min_signal
        self._max_velocity = max_velocity
        self._max_acceleration = max_acceleration
        self._max_angular_velocity = max_angular_velocity
        self._max_altitude = max_altitude
        self._min_altitude = min_altitude
        self._safety_radius = safety_radius
        
    def set_home_position(self, position: Position) -> None:
        """
        Setzt die Home-Position.
        
        Args:
            position: Home-Position
        """
        self._home_position = position
        
    def enable_safety(self) -> bool:
        """
        Aktiviert die Sicherheitsüberwachung.
        
        Returns:
            True wenn erfolgreich, sonst False
        """
        if self._safety_active:
            self._set_error("Sicherheitsüberwachung bereits aktiv")
            return False
            
        self._safety_active = True
        return True
        
    def disable_safety(self) -> bool:
        """
        Deaktiviert die Sicherheitsüberwachung.
        
        Returns:
            True wenn erfolgreich, sonst False
        """
        if not self._safety_active:
            self._set_error("Sicherheitsüberwachung nicht aktiv")
            return False
            
        self._safety_active = False
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
        
        # Sicherheit prüfen
        if self._safety_active:
            self._check_safety()
            
    def _check_safety(self) -> None:
        """
        Prüft die Sicherheitsbedingungen.
        """
        # Batteriestand prüfen
        if self._state.battery_level < self._min_battery_level:
            self._handle_safety_violation("Niedriger Batteriestand")
            return
            
        # Signalstärke prüfen
        if self._state.signal_strength < self._min_signal_strength:
            self._handle_safety_violation("Schwaches Signal")
            return
            
        # Geschwindigkeit prüfen
        velocity = math.sqrt(
            self._state.velocity.x**2 +
            self._state.velocity.y**2 +
            self._state.velocity.z**2
        )
        if velocity > self._max_velocity:
            self._handle_safety_violation("Geschwindigkeit zu hoch")
            return
            
        # Beschleunigung prüfen
        acceleration = math.sqrt(
            self._state.acceleration.x**2 +
            self._state.acceleration.y**2 +
            self._state.acceleration.z**2
        )
        if acceleration > self._max_acceleration:
            self._handle_safety_violation("Beschleunigung zu hoch")
            return
            
        # Winkelgeschwindigkeit prüfen
        angular_velocity = math.sqrt(
            self._state.angular_velocity.x**2 +
            self._state.angular_velocity.y**2 +
            self._state.angular_velocity.z**2
        )
        if angular_velocity > self._max_angular_velocity:
            self._handle_safety_violation("Winkelgeschwindigkeit zu hoch")
            return
            
        # Höhe prüfen
        if self._state.position.z > self._max_altitude:
            self._handle_safety_violation("Höhe zu hoch")
            return
            
        if self._state.position.z < self._min_altitude:
            self._handle_safety_violation("Höhe zu niedrig")
            return
            
        # Sicherheitsradius prüfen
        dx = self._state.position.x - self._home_position.x
        dy = self._state.position.y - self._home_position.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > self._safety_radius:
            self._handle_safety_violation("Außerhalb des Sicherheitsradius")
            return
            
    def _handle_safety_violation(self, message: str) -> None:
        """
        Behandelt eine Sicherheitsverletzung.
        
        Args:
            message: Verletzungsmeldung
        """
        # Verletzung signalisieren
        self.safety_violation.emit(message)
        
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