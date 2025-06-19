"""
Telemetrie Service für die Flugsteuerung.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import math
from dataclasses import dataclass
from enum import Enum

from PySide6.QtCore import QObject, Signal, Slot, QTimer

from ..models.flight_data import Position, Waypoint, Mission, ControlCommand, MissionPlan, FlightState
from ..enums import FlightStatus, FlightMode, ControlMode, CommandType, EmergencyProcedure
from ..telemetry.telemetry_manager import TelemetryManager
from ..connection.connection_manager import ConnectionManager

@dataclass
class TelemetryState:
    """Telemetrie-Zustand"""
    mode: FlightMode
    control_mode: ControlMode
    armed: bool
    position: Dict[str, float]
    attitude: Dict[str, float]
    velocity: Dict[str, float]
    battery: Dict[str, float]
    gps: Dict[str, Any]
    rc: Dict[str, float]
    gps_fix: bool
    gps_satellites: int
    gps_hdop: float
    gps_altitude: float
    gps_ground_speed: float
    gps_ground_course: float
    gps_vertical_speed: float
    gps_eph: float
    gps_epv: float
    gps_velocity: Position
    gps_position: Position
    gps_home: Position
    gps_origin: Position
    gps_waypoint: Position
    gps_target: Position
    gps_obstacle: Position
    gps_geofence: Position
    gps_landing: Position
    gps_takeoff: Position
    gps_mission: Position
    gps_emergency: Position
    gps_collision: Position
    gps_flight: Position
    gps_control: Position
    gps_safety: Position

class TelemetryService(QObject):
    """Service für Telemetrie-Daten"""
    
    # Signale
    stateChanged = Signal(TelemetryState)
    errorOccurred = Signal(str)
    modeChanged = Signal(FlightMode)
    commandExecuted = Signal(ControlCommand)
    missionStarted = Signal(Mission)
    missionCompleted = Signal(Mission)
    missionAborted = Signal(Mission)
    emergencyTriggered = Signal(EmergencyProcedure)
    telemetryUpdated = Signal(dict)  # Neues Signal für Telemetrie-Updates
    connectionLost = Signal()  # Neues Signal für Verbindungsverlust
    connectionRestored = Signal()  # Neues Signal für wiederhergestellte Verbindung
    
    def __init__(self, telemetry_manager: TelemetryManager, connection_manager: ConnectionManager):
        """Initialisiert den Telemetrie Service"""
        super().__init__()
        self.telemetry_manager = telemetry_manager
        self.connection_manager = connection_manager
        
        # Initialisiere den Flugzustand
        self._state = FlightState(
            position=Position(x=0.0, y=0.0, z=0.0),
            mode=FlightMode.MANUAL,
            armed=False,
            status=FlightStatus.DISCONNECTED,
            parameters={}
        )
        
        # Timer für Status-Updates
        self._status_timer = QTimer()
        self._status_timer.timeout.connect(self._update_status)
        self._status_timer.start(100)  # 100ms Update-Intervall
        
        # Verbindungsstatus
        self._connection_lost = False
        
        # Telemetrie-Historie
        self._telemetry_history = []
        self._max_history_size = 1000
        
        # Signal-Slot Verbindungen einrichten
        if hasattr(self.telemetry_manager, 'telemetryUpdated'):
            self.telemetry_manager.telemetryUpdated.connect(self.on_telemetry_updated)
        
        if hasattr(self.telemetry_manager, 'stateChanged'):
            self.telemetry_manager.stateChanged.connect(self.on_state_changed)
            
        if hasattr(self.telemetry_manager, 'modeChanged'):
            self.telemetry_manager.modeChanged.connect(self.on_mode_changed)
        
        # Initialisiere Zeitstempel für Verbindungsüberwachung
        self._last_telemetry_update = None
        
    def get_state(self) -> TelemetryState:
        """Gibt den aktuellen Telemetrie-Zustand zurück"""
        return self._state
        
    def get_position(self) -> Dict[str, float]:
        """Gibt die aktuelle Position zurück"""
        return {
            'x': self._state.position.x,
            'y': self._state.position.y,
            'z': self._state.position.z
        }
        
    def get_attitude(self) -> Dict[str, float]:
        """Gibt die aktuelle Attitude zurück"""
        return {
            'roll': self._state.attitude.x,
            'pitch': self._state.attitude.y,
            'yaw': self._state.attitude.z
        }
        
    def get_velocity(self) -> Dict[str, float]:
        """Gibt die aktuelle Geschwindigkeit zurück"""
        return {
            'x': self._state.velocity.x,
            'y': self._state.velocity.y,
            'z': self._state.velocity.z
        }
        
    def get_battery(self) -> Dict[str, float]:
        """Gibt die aktuellen Batterie-Daten zurück"""
        return {
            'level': self._state.battery_level,
            'voltage': self._state.parameters.get('battery_voltage', 0.0),
            'current': self._state.parameters.get('battery_current', 0.0)
        }
        
    def get_gps(self) -> Dict[str, Any]:
        """Gibt die aktuellen GPS-Daten zurück"""
        return {
            'fix': self._state.gps_fix,
            'satellites': self._state.gps_satellites,
            'hdop': self._state.gps_hdop,
            'altitude': self._state.gps_altitude,
            'ground_speed': self._state.gps_ground_speed,
            'ground_course': self._state.gps_ground_course,
            'vertical_speed': self._state.gps_vertical_speed,
            'eph': self._state.gps_eph,
            'epv': self._state.gps_epv,
            'velocity': {
                'x': self._state.gps_velocity.x,
                'y': self._state.gps_velocity.y,
                'z': self._state.gps_velocity.z
            },
            'position': {
                'x': self._state.gps_position.x,
                'y': self._state.gps_position.y,
                'z': self._state.gps_position.z
            }
        }
        
    def get_rc(self) -> Dict[str, float]:
        """Gibt die aktuellen RC-Daten zurück"""
        return {
            'roll': self._state.parameters.get('rc_roll', 0.0),
            'pitch': self._state.parameters.get('rc_pitch', 0.0),
            'yaw': self._state.parameters.get('rc_yaw', 0.0),
            'throttle': self._state.parameters.get('rc_throttle', 0.0),
            'mode': self._state.parameters.get('rc_mode', 0.0)
        }
        
    def set_telemetry_parameters(self, update_interval: int, connection_timeout: float,
                               max_history_size: int) -> None:
        """
        Setzt die Telemetrie-Parameter.
        
        Args:
            update_interval: Update-Intervall in ms
            connection_timeout: Verbindungs-Timeout in Sekunden
            max_history_size: Maximale Größe der Telemetrie-Historie
        """
        self._update_interval = update_interval
        self._connection_timeout = connection_timeout
        self._max_history_size = max_history_size
        
        # Timer aktualisieren
        self._status_timer.setInterval(update_interval)
        
    def get_telemetry_history(self) -> List[Dict[str, Any]]:
        """
        Gibt die Telemetrie-Historie zurück.
        
        Returns:
            Telemetrie-Historie
        """
        return self._telemetry_history.copy()
        
    def clear_telemetry_history(self) -> None:
        """
        Löscht die Telemetrie-Historie.
        """
        self._telemetry_history.clear()
        
    @Slot()
    def _update_status(self) -> None:
        """
        Überwacht den Verbindungsstatus basierend auf den letzten empfangenen Telemetriedaten.
        Diese Methode wird regelmäßig durch einen Timer aufgerufen.
        
        Die eigentlichen Telemetriedaten werden nicht hier aktualisiert, sondern direkt durch 
        die Signale vom MAVLinkTelemetryAdapter (stateChanged, modeChanged, telemetryUpdated),
        die an die entsprechenden Slot-Methoden angebunden sind.
        """
        if not self.telemetry_manager:
            return
        
        # Prüfen, ob die Verbindung aktiv ist anhand des Zeitstempels des letzten Updates
        current_time = datetime.now()
        timeout_seconds = 3  # 3 Sekunden ohne Update = Verbindung verloren
        
        if hasattr(self, '_last_telemetry_update') and self._last_telemetry_update:
            time_since_update = (current_time - self._last_telemetry_update).total_seconds()
            if time_since_update > timeout_seconds:
                self._handle_connection_lost()
            elif self._connection_lost:
                # Verbindung wiederhergestellt
                self._handle_connection_restored()
        else:
            # Noch kein Update empfangen
            self._last_telemetry_update = current_time
        
        # --- Automatische Phasenübergänge ---
        status_before = self._state.status
        # Nach TAKEOFF: Wenn Höhe erreicht, auf FLYING wechseln
        if self._state.status == FlightStatus.TAKEOFF:
            if self._state.position.z >= self._state.parameters.get('takeoff_altitude', 1.0):
                self._state.status = FlightStatus.FLYING
        # Nach LANDING: Wenn Höhe ~0, auf LANDED wechseln
        if self._state.status == FlightStatus.LANDING:
            if self._state.position.z <= 0.1:
                self._state.status = FlightStatus.LANDED
                self._state.armed = False
        # Nach RTL: Wenn zurück und gelandet, auf LANDED wechseln
        if self._state.status == FlightStatus.RTL:
            if self._state.position.z <= 0.1:
                self._state.status = FlightStatus.LANDED
                self._state.armed = False
        # Nach ERROR: Reset möglich (hier nur als Beispiel, ggf. eigene Methode)
        # ...
        # Status-Änderung signalisieren, wenn sich etwas geändert hat
        if self._state.status != status_before:
            self.stateChanged.emit(self._state)
        
    def _update_telemetry_history(self, telemetry_data: Dict[str, Any]) -> None:
        """
        Aktualisiert die Telemetrie-Historie.
        
        Args:
            telemetry_data: Telemetrie-Daten
        """
        # Zeitstempel hinzufügen
        telemetry_data['timestamp'] = datetime.now()
        
        # Zur Historie hinzufügen
        self._telemetry_history.append(telemetry_data)
        
        # Historie auf maximale Größe begrenzen
        if len(self._telemetry_history) > self._max_history_size:
            self._telemetry_history.pop(0)
            
    def _handle_connection_lost(self) -> None:
        """
        Behandelt den Verbindungsverlust.
        """
        if not self._connection_lost:
            self._connection_lost = True
            self.connectionLost.emit()
            
    def _handle_connection_restored(self) -> None:
        """
        Behandelt die wiederhergestellte Verbindung.
        """
        if self._connection_lost:
            self._connection_lost = False
            self._state.status = FlightStatus.IDLE
            self.connectionRestored.emit()
            
    @Slot(dict)
    def on_telemetry_updated(self, telemetry_data: Dict[str, Any]) -> None:
        """
        Wird aufgerufen, wenn neue Telemetriedaten vom MAVLinkTelemetryAdapter empfangen werden.
        Aktualisiert den Zeitstempel des letzten Updates für die Verbindungsüberwachung.
        
        Args:
            telemetry_data: Die empfangenen Telemetriedaten
        """
        # Zeitstempel des letzten Updates setzen für die Verbindungsüberwachung
        self._last_telemetry_update = datetime.now()
        
        # Telemetrie-Historie aktualisieren
        self._update_telemetry_history(telemetry_data)
        
        # Signal weiterleiten
        self.telemetryUpdated.emit(telemetry_data)
        
    @Slot(FlightState)
    def on_state_changed(self, flight_state: FlightState) -> None:
        """
        Wird aufgerufen, wenn sich der Flugzustand vom MAVLinkTelemetryAdapter ändert.
        
        Args:
            flight_state: Der neue Flugzustand
        """
        # Flugzustand aktualisieren
        self._state = flight_state
        
        # Zeitstempel des letzten Updates setzen für die Verbindungsüberwachung
        self._last_telemetry_update = datetime.now()
        
    @Slot(FlightMode)
    def on_mode_changed(self, mode: FlightMode) -> None:
        """
        Wird aufgerufen, wenn sich der Flugmodus vom MAVLinkTelemetryAdapter ändert.
        
        Args:
            mode: Der neue Flugmodus
        """
        # Flugmodus aktualisieren
        self._state.mode = mode
        
        # Zeitstempel des letzten Updates setzen für die Verbindungsüberwachung
        self._last_telemetry_update = datetime.now()
        
        # Signal weiterleiten
        self.modeChanged.emit(mode)
            
    @Slot(FlightMode)
    def set_mode(self, mode: FlightMode) -> bool:
        """
        Setzt den Flugmodus.
        
        Args:
            mode: Neuer Flugmodus
            
        Returns:
            True wenn erfolgreich, sonst False
        """
        if not self._can_change_mode(mode):
            return False
            
        # Modus ändern
        self._state.mode = mode
        
        # Status-Änderung signalisieren
        self.modeChanged.emit(mode)
        
        return True
        
    @Slot(ControlCommand)
    def execute_command(self, command: ControlCommand) -> bool:
        """
        Führt einen Steuerungsbefehl aus.
        
        Args:
            command: Der auszuführende Befehl
            
        Returns:
            True wenn erfolgreich, sonst False
        """
        if not self._can_execute_command(command):
            return False
            
        # Befehl ausführen
        if not self._execute_command(command):
            return False
            
        # Befehl ausgeführt signalisieren
        self.commandExecuted.emit(command)
        
        return True
        
    def _can_change_mode(self, mode: FlightMode) -> bool:
        """
        Prüft, ob der Flugmodus geändert werden kann.
        
        Args:
            mode: Neuer Flugmodus
            
        Returns:
            True wenn möglich, sonst False
        """
        # Prüfen, ob der aktuelle Status einen Moduswechsel erlaubt
        if self._state.status == FlightStatus.ERROR:
            return False
            
        # Prüfen, ob der neue Modus gültig ist
        if mode not in FlightMode:
            return False
            
        return True
        
    def _can_execute_command(self, command: ControlCommand) -> bool:
        """
        Prüft, ob ein Steuerungsbefehl ausgeführt werden kann.
        
        Args:
            command: Der zu prüfende Befehl
            
        Returns:
            True wenn möglich, sonst False
        """
        # Prüfen, ob der aktuelle Status einen Befehl erlaubt
        if self._state.status == FlightStatus.ERROR:
            return False
            
        # Prüfen, ob der Befehl gültig ist
        if command.type not in CommandType:
            return False
            
        return True
        
    def _execute_command(self, command: ControlCommand) -> bool:
        """
        Führt einen Steuerungsbefehl aus.
        
        Args:
            command: Der auszuführende Befehl
            
        Returns:
            True wenn erfolgreich, sonst False
        """
        try:
            # Befehl ausführen
            if command.type == CommandType.TAKEOFF:
                self._handle_takeoff(command)
            elif command.type == CommandType.LAND:
                self._handle_landing(command)
            elif command.type == CommandType.RTL:
                self._handle_rtl(command)
            elif command.type == CommandType.HOLD:
                self._handle_hold(command)
            elif command.type == CommandType.SET_ALTITUDE:
                self._handle_set_altitude(command)
            elif command.type == CommandType.SET_HEADING:
                self._handle_set_heading(command)
            elif command.type == CommandType.SET_SPEED:
                self._handle_set_speed(command)
            elif command.type == CommandType.FOLLOW_PATH:
                self._handle_follow_path(command)
            elif command.type == CommandType.ORBIT:
                self._handle_orbit(command)
            elif command.type == CommandType.MANEUVER:
                self._handle_maneuver(command)
            elif command.type == CommandType.FORMATION:
                self._handle_formation(command)
            elif command.type == CommandType.EMERGENCY:
                self._handle_emergency(command)
            else:
                return False
                
            return True
            
        except Exception as e:
            self._set_error(str(e))
            return False
            
    def _handle_takeoff(self, command: ControlCommand) -> None:
        """
        Behandelt den Start-Befehl.
        
        Args:
            command: Der Start-Befehl
        """
        # Prüfen, ob der Start möglich ist
        if self._state.status != FlightStatus.DISARMED:
            raise ValueError("Cannot take off when not disarmed")
            
        # Start-Parameter prüfen
        altitude = command.parameters.get('altitude', 0.0)
        if altitude <= 0.0:
            raise ValueError("Invalid takeoff altitude")
            
        # Start durchführen
        self._state.status = FlightStatus.TAKEOFF
        self._state.armed = True
        
    def _handle_landing(self, command: ControlCommand) -> None:
        """
        Behandelt den Lande-Befehl.
        
        Args:
            command: Der Lande-Befehl
        """
        # Prüfen, ob die Landung möglich ist
        if self._state.status != FlightStatus.FLYING:
            raise ValueError("Cannot land when not flying")
            
        # Landung durchführen
        self._state.status = FlightStatus.LANDING
        
    def _handle_rtl(self, command: ControlCommand) -> None:
        """
        Behandelt den RTL-Befehl.
        
        Args:
            command: Der RTL-Befehl
        """
        # Prüfen, ob RTL möglich ist
        if self._state.status != FlightStatus.FLYING:
            raise ValueError("Cannot RTL when not flying")
            
        # RTL durchführen
        self._state.status = FlightStatus.RTL
        
    def _handle_hold(self, command: ControlCommand) -> None:
        """
        Behandelt den Halt-Befehl.
        
        Args:
            command: Der Halt-Befehl
        """
        # Prüfen, ob Halt möglich ist
        if self._state.status != FlightStatus.FLYING:
            raise ValueError("Cannot hold when not flying")
            
        # Halt durchführen
        self._state.status = FlightStatus.HOLD
        
    def _handle_set_altitude(self, command: ControlCommand) -> None:
        """
        Behandelt den Höhen-Befehl.
        
        Args:
            command: Der Höhen-Befehl
        """
        # Prüfen, ob Höhenänderung möglich ist
        if self._state.status != FlightStatus.FLYING:
            raise ValueError("Cannot set altitude when not flying")
            
        # Höhen-Parameter prüfen
        altitude = command.parameters.get('altitude', 0.0)
        if altitude < 0.0:
            raise ValueError("Invalid altitude")
            
        # Höhe setzen
        self._state.position.z = altitude
        
    def _handle_set_heading(self, command: ControlCommand) -> None:
        """
        Behandelt den Kurs-Befehl.
        
        Args:
            command: Der Kurs-Befehl
        """
        # Prüfen, ob Kursänderung möglich ist
        if self._state.status != FlightStatus.FLYING:
            raise ValueError("Cannot set heading when not flying")
            
        # Kurs-Parameter prüfen
        heading = command.parameters.get('heading', 0.0)
        if heading < 0.0 or heading > 360.0:
            raise ValueError("Invalid heading")
            
        # Kurs setzen
        self._state.attitude.z = heading
        
    def _handle_set_speed(self, command: ControlCommand) -> None:
        """
        Behandelt den Geschwindigkeits-Befehl.
        
        Args:
            command: Der Geschwindigkeits-Befehl
        """
        # Prüfen, ob Geschwindigkeitsänderung möglich ist
        if self._state.status != FlightStatus.FLYING:
            raise ValueError("Cannot set speed when not flying")
            
        # Geschwindigkeits-Parameter prüfen
        speed = command.parameters.get('speed', 0.0)
        if speed < 0.0:
            raise ValueError("Invalid speed")
            
        # Geschwindigkeit setzen
        self._state.velocity.x = speed * math.cos(math.radians(self._state.attitude.z))
        self._state.velocity.y = speed * math.sin(math.radians(self._state.attitude.z))
        
    def _handle_follow_path(self, command: ControlCommand) -> None:
        """
        Behandelt den Pfad-Befehl.
        
        Args:
            command: Der Pfad-Befehl
        """
        # Prüfen, ob Pfadfolge möglich ist
        if self._state.status != FlightStatus.FLYING:
            raise ValueError("Cannot follow path when not flying")
            
        # Pfad-Parameter prüfen
        path = command.parameters.get('path', [])
        if not path:
            raise ValueError("Invalid path")
            
        # Pfad folgen
        self._state.status = FlightStatus.FOLLOW_PATH
        
    def _handle_orbit(self, command: ControlCommand) -> None:
        """
        Behandelt den Orbit-Befehl.
        
        Args:
            command: Der Orbit-Befehl
        """
        # Prüfen, ob Orbit möglich ist
        if self._state.status != FlightStatus.FLYING:
            raise ValueError("Cannot orbit when not flying")
            
        # Orbit-Parameter prüfen
        center = command.parameters.get('center', None)
        radius = command.parameters.get('radius', 0.0)
        if not center or radius <= 0.0:
            raise ValueError("Invalid orbit parameters")
            
        # Orbit fliegen
        self._state.status = FlightStatus.ORBIT
        
    def _handle_maneuver(self, command: ControlCommand) -> None:
        """
        Behandelt den Manöver-Befehl.
        
        Args:
            command: Der Manöver-Befehl
        """
        # Prüfen, ob Manöver möglich ist
        if self._state.status != FlightStatus.FLYING:
            raise ValueError("Cannot maneuver when not flying")
            
        # Manöver-Parameter prüfen
        maneuver = command.parameters.get('maneuver', None)
        if not maneuver:
            raise ValueError("Invalid maneuver")
            
        # Manöver ausführen
        self._state.status = FlightStatus.MANEUVER
        
    def _handle_formation(self, command: ControlCommand) -> None:
        """
        Behandelt den Formations-Befehl.
        
        Args:
            command: Der Formations-Befehl
        """
        # Prüfen, ob Formation möglich ist
        if self._state.status != FlightStatus.FLYING:
            raise ValueError("Cannot form formation when not flying")
            
        # Formations-Parameter prüfen
        formation = command.parameters.get('formation', None)
        if not formation:
            raise ValueError("Invalid formation")
            
        # Formation setzen
        self._state.status = FlightStatus.FORMATION
        
    def _handle_emergency(self, command: ControlCommand) -> None:
        """
        Behandelt den Notfall-Befehl.
        
        Args:
            command: Der Notfall-Befehl
        """
        # Notfall-Parameter prüfen
        procedure = command.parameters.get('procedure', None)
        if not procedure:
            raise ValueError("Invalid emergency procedure")
            
        # Notfall durchführen
        self._state.status = FlightStatus.EMERGENCY
        
        # Notfall signalisieren
        self.emergencyTriggered.emit(procedure)
        
    def _set_error(self, message: str) -> None:
        """
        Setzt einen Fehler.
        
        Args:
            message: Fehlermeldung
        """
        self._state.status = FlightStatus.ERROR
        self._state.parameters['error_message'] = message
        
        # Fehler signalisieren
        self.errorOccurred.emit(message) 