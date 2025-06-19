"""
Control Service für die Flugsteuerung.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import math
from dataclasses import dataclass
from enum import Enum

from PySide6.QtCore import QObject, Signal, Slot, QTimer

from ..models.flight_data import Position, Waypoint, Mission, FlightState, ControlCommand, MissionPlan
from ..enums import FlightStatus, FlightMode, ControlMode, CommandType, EmergencyProcedure
from ..telemetry.telemetry_manager import TelemetryManager
from ..connection.connection_manager import ConnectionManager

class ControlService(QObject):
    """Implementiert die Geschäftslogik für Steuerungs-Operationen"""
    
    # Signale
    state_changed = Signal(FlightState)
    mode_changed = Signal(FlightMode)
    error_occurred = Signal(str)
    command_executed = Signal(ControlCommand)
    mission_started = Signal(Mission)
    mission_completed = Signal(Mission)
    mission_aborted = Signal(Mission)
    emergency_triggered = Signal(EmergencyProcedure)
    control_mode_changed = Signal(ControlMode)  # Neues Signal für Steuerungsmodus-Änderungen
    control_parameters_updated = Signal(dict)  # Neues Signal für Steuerungsparameter-Updates
    
    def __init__(self, telemetry_manager: Optional[TelemetryManager] = None,
                 connection_manager: Optional[ConnectionManager] = None):
        """
        Initialisiert den Steuerungs-Service.
        
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
        
        # Steuerungs-Parameter
        self._control_active = False
        self._control_parameters: Dict[str, float] = {
            "pitch_rate": 0.0,  # Nickrate in rad/s
            "roll_rate": 0.0,   # Rollrate in rad/s
            "yaw_rate": 0.0,    # Gierrate in rad/s
            "thrust": 0.0,      # Schub in N
            "max_velocity": 5.0,  # Maximale Geschwindigkeit in m/s
            "max_acceleration": 2.0,  # Maximale Beschleunigung in m/s²
            "max_angular_velocity": 1.0,  # Maximale Winkelgeschwindigkeit in rad/s
            "position_tolerance": 0.1,  # Positions-Toleranz in m
            "attitude_tolerance": 0.05  # Attitude-Toleranz in rad
        }
        
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
        
    def set_control_mode(self, mode: ControlMode) -> bool:
        """
        Setzt den Steuerungsmodus.
        
        Args:
            mode: Steuerungsmodus
            
        Returns:
            True wenn erfolgreich, sonst False
        """
        if self._control_mode == mode:
            return True
            
        # Modus setzen
        self._control_mode = mode
        self.control_mode_changed.emit(mode)
        return True
        
    def set_control_parameters(self, parameters: Dict[str, float]) -> bool:
        """
        Setzt die Steuerungsparameter.
        
        Args:
            parameters: Steuerungsparameter
            
        Returns:
            True wenn erfolgreich, sonst False
        """
        # Parameter prüfen
        for name, value in parameters.items():
            if name not in self._control_parameters:
                self._set_error(f"Unbekannter Parameter: {name}")
                return False
                
            if not isinstance(value, (int, float)):
                self._set_error(f"Ungültiger Wert für Parameter {name}")
                return False
                
        # Parameter setzen
        self._control_parameters.update(parameters)
        self.control_parameters_updated.emit(self._control_parameters)
        return True
        
    def get_control_parameters(self) -> Dict[str, float]:
        """
        Gibt die aktuellen Steuerungsparameter zurück.
        
        Returns:
            Steuerungsparameter
        """
        return self._control_parameters.copy()
        
    def set_control_input(self, pitch_rate: float, roll_rate: float,
                         yaw_rate: float, thrust: float) -> bool:
        """
        Setzt die Steuerungseingaben.
        
        Args:
            pitch_rate: Nickrate in rad/s
            roll_rate: Rollrate in rad/s
            yaw_rate: Gierrate in rad/s
            thrust: Schub in N
            
        Returns:
            True wenn erfolgreich, sonst False
        """
        # Eingaben prüfen
        if not self._check_control_inputs(pitch_rate, roll_rate, yaw_rate, thrust):
            return False
            
        # Steuerungsbefehl erstellen
        command = ControlCommand(
            type=CommandType.CONTROL,
            parameters={
                "pitch_rate": pitch_rate,
                "roll_rate": roll_rate,
                "yaw_rate": yaw_rate,
                "thrust": thrust
            }
        )
        
        # Befehl ausführen
        return self.execute_command(command)
        
    def set_position_target(self, position: Position) -> bool:
        """
        Setzt eine Zielposition.
        
        Args:
            position: Zielposition
            
        Returns:
            True wenn erfolgreich, sonst False
        """
        # Steuerungsbefehl erstellen
        command = ControlCommand(
            type=CommandType.MOVE_TO,
            parameters={
                "x": position.x,
                "y": position.y,
                "z": position.z
            }
        )
        
        # Befehl ausführen
        return self.execute_command(command)
        
    def set_attitude_target(self, attitude: Position) -> bool:
        """
        Setzt eine Zielattitude.
        
        Args:
            attitude: Zielattitude
            
        Returns:
            True wenn erfolgreich, sonst False
        """
        # Steuerungsbefehl erstellen
        command = ControlCommand(
            type=CommandType.ATTITUDE,
            parameters={
                "pitch": attitude.x,
                "roll": attitude.y,
                "yaw": attitude.z
            }
        )
        
        # Befehl ausführen
        return self.execute_command(command)
        
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
        
    def _check_control_inputs(self, pitch_rate: float, roll_rate: float,
                            yaw_rate: float, thrust: float) -> bool:
        """
        Prüft die Steuerungseingaben.
        
        Args:
            pitch_rate: Nickrate in rad/s
            roll_rate: Rollrate in rad/s
            yaw_rate: Gierrate in rad/s
            thrust: Schub in N
            
        Returns:
            True wenn gültig, sonst False
        """
        # Maximale Winkelgeschwindigkeit prüfen
        max_rate = self._control_parameters["max_angular_velocity"]
        
        if abs(pitch_rate) > max_rate:
            self._set_error(f"Nickrate zu hoch: {pitch_rate}")
            return False
            
        if abs(roll_rate) > max_rate:
            self._set_error(f"Rollrate zu hoch: {roll_rate}")
            return False
            
        if abs(yaw_rate) > max_rate:
            self._set_error(f"Gierrate zu hoch: {yaw_rate}")
            return False
            
        # Schub prüfen
        if thrust < 0.0 or thrust > 1.0:
            self._set_error(f"Ungültiger Schub: {thrust}")
            return False
            
        return True
        
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