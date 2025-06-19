"""
Flugcontroller für die Flugsteuerung.
Koordiniert alle Komponenten der Flugsteuerung.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
import math

from PySide6.QtCore import QObject, Signal, Slot, QTimer

from .enums import FlightStatus, FlightMode, ControlMode, CommandType, EmergencyProcedure
from .basic_control import BasicControl
from .advanced_control import AdvancedControl
from .flight_modes import FlightModes
from .waypoint_manager import WaypointManager, Waypoint, Mission
from .mission_planner import MissionPlanner, MissionPlan
from ..telemetry.telemetry_manager import TelemetryManager
from ..connection.connection_manager import ConnectionManager

class FlightController(QObject):
    """Koordiniert alle Komponenten der Flugsteuerung"""
    
    # Signale
    status_changed = Signal(FlightStatus)
    mode_changed = Signal(FlightMode)
    error_occurred = Signal(str)
    command_executed = Signal(CommandType, dict)
    mission_started = Signal(Mission)
    mission_completed = Signal(Mission)
    mission_aborted = Signal(Mission)
    emergency_triggered = Signal(EmergencyProcedure)
    
    def __init__(self, telemetry_manager: Optional[TelemetryManager] = None,
                 connection_manager: Optional[ConnectionManager] = None):
        """
        Initialisiert den Flugcontroller.
        
        Args:
            telemetry_manager: Optional: Telemetrie-Manager
            connection_manager: Optional: Verbindungs-Manager
        """
        super().__init__()
        
        # Manager setzen
        self._telemetry = telemetry_manager
        self._connection = connection_manager
        
        # Komponenten initialisieren
        self._basic_control = BasicControl(telemetry_manager)
        self._advanced_control = AdvancedControl(telemetry_manager)
        self._flight_modes = FlightModes(telemetry_manager)
        self._waypoint_manager = WaypointManager(telemetry_manager)
        self._mission_planner = MissionPlanner(self._waypoint_manager, telemetry_manager)
        
        # Status und Modus
        self._status = FlightStatus.DISCONNECTED
        self._mode = FlightMode.MANUAL
        self._control_mode = ControlMode.BASIC
        
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
        self._basic_control.set_telemetry_manager(telemetry_manager)
        self._advanced_control.set_telemetry_manager(telemetry_manager)
        self._flight_modes.set_telemetry_manager(telemetry_manager)
        self._waypoint_manager.set_telemetry_manager(telemetry_manager)
        self._mission_planner.set_telemetry_manager(telemetry_manager)
        
    def set_connection_manager(self, connection_manager: ConnectionManager) -> None:
        """
        Setzt den Verbindungs-Manager.
        
        Args:
            connection_manager: Verbindungs-Manager
        """
        self._connection = connection_manager
        
    @Slot()
    def connect(self) -> bool:
        """
        Stellt die Verbindung her.
        
        Returns:
            True wenn erfolgreich, sonst False
        """
        if not self._connection:
            self._set_error("Kein Verbindungs-Manager verfügbar")
            return False
            
        # Status aktualisieren
        self._set_status(FlightStatus.CONNECTING)
        
        # Verbindung herstellen
        if not self._connection.connect():
            self._set_error("Verbindungsaufbau fehlgeschlagen")
            return False
            
        # Status aktualisieren
        self._set_status(FlightStatus.CONNECTED)
        return True
        
    @Slot()
    def disconnect(self) -> bool:
        """
        Trennt die Verbindung.
        
        Returns:
            True wenn erfolgreich, sonst False
        """
        if not self._connection:
            self._set_error("Kein Verbindungs-Manager verfügbar")
            return False
            
        # Verbindung trennen
        if not self._connection.disconnect():
            self._set_error("Verbindungstrennung fehlgeschlagen")
            return False
            
        # Status aktualisieren
        self._set_status(FlightStatus.DISCONNECTED)
        return True
        
    @Slot()
    def arm(self) -> bool:
        """
        Schaltet das System scharf.
        
        Returns:
            True wenn erfolgreich, sonst False
        """
        if self._status != FlightStatus.CONNECTED:
            self._set_error("System nicht verbunden")
            return False
            
        # Status aktualisieren
        self._set_status(FlightStatus.ARMED)
        return True
        
    @Slot()
    def disarm(self) -> bool:
        """
        Schaltet das System unscharf.
        
        Returns:
            True wenn erfolgreich, sonst False
        """
        if self._status != FlightStatus.ARMED:
            self._set_error("System nicht scharf")
            return False
            
        # Status aktualisieren
        self._set_status(FlightStatus.DISARMED)
        return True
        
    @Slot(FlightMode)
    def set_mode(self, mode: FlightMode) -> bool:
        """
        Setzt den Flugmodus.
        
        Args:
            mode: Flugmodus
            
        Returns:
            True wenn erfolgreich, sonst False
        """
        if not self._flight_modes.is_mode_available(mode):
            self._set_error(f"Modus {mode.value} nicht verfügbar")
            return False
            
        # Modus setzen
        if not self._flight_modes.set_mode(mode):
            self._set_error(f"Moduswechsel zu {mode.value} fehlgeschlagen")
            return False
            
        # Status aktualisieren
        self._mode = mode
        self.mode_changed.emit(mode)
        return True
        
    @Slot(ControlMode)
    def set_control_mode(self, mode: ControlMode) -> bool:
        """
        Setzt den Steuerungsmodus.
        
        Args:
            mode: Steuerungsmodus
            
        Returns:
            True wenn erfolgreich, sonst False
        """
        self._control_mode = mode
        return True
        
    @Slot(Mission)
    def start_mission(self, mission: Mission) -> bool:
        """
        Startet eine Mission.
        
        Args:
            mission: Mission
            
        Returns:
            True wenn erfolgreich, sonst False
        """
        if self._status != FlightStatus.ARMED:
            self._set_error("System nicht scharf")
            return False
            
        # Missionsplan erstellen
        plan = self._mission_planner.create_mission_plan(mission)
        if not plan:
            self._set_error("Missionsplanung fehlgeschlagen")
            return False
            
        # Mission starten
        if not self._waypoint_manager.start_mission(mission.id):
            self._set_error("Missionsstart fehlgeschlagen")
            return False
            
        # Status aktualisieren
        self._set_status(FlightStatus.FLYING)
        self.mission_started.emit(mission)
        return True
        
    @Slot()
    def pause_mission(self) -> bool:
        """
        Pausiert die aktuelle Mission.
        
        Returns:
            True wenn erfolgreich, sonst False
        """
        if self._status != FlightStatus.FLYING:
            self._set_error("Keine aktive Mission")
            return False
            
        # Mission pausieren
        if not self._waypoint_manager.pause_mission():
            self._set_error("Missionspause fehlgeschlagen")
            return False
            
        return True
        
    @Slot()
    def resume_mission(self) -> bool:
        """
        Setzt die aktuelle Mission fort.
        
        Returns:
            True wenn erfolgreich, sonst False
        """
        if self._status != FlightStatus.FLYING:
            self._set_error("Keine aktive Mission")
            return False
            
        # Mission fortsetzen
        if not self._waypoint_manager.resume_mission():
            self._set_error("Missionsfortsetzung fehlgeschlagen")
            return False
            
        return True
        
    @Slot()
    def abort_mission(self) -> bool:
        """
        Bricht die aktuelle Mission ab.
        
        Returns:
            True wenn erfolgreich, sonst False
        """
        if self._status != FlightStatus.FLYING:
            self._set_error("Keine aktive Mission")
            return False
            
        # Mission abbrechen
        if not self._waypoint_manager.abort_mission():
            self._set_error("Missionsabbruch fehlgeschlagen")
            return False
            
        # Status aktualisieren
        self._set_status(FlightStatus.ARMED)
        self.mission_aborted.emit(self._waypoint_manager.get_current_mission())
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
        # Notfallprozedur ausführen
        if not self._advanced_control.execute_emergency_procedure(procedure):
            self._set_error("Notfallprozedur fehlgeschlagen")
            return False
            
        # Status aktualisieren
        self._set_status(FlightStatus.EMERGENCY)
        self.emergency_triggered.emit(procedure)
        return True
        
    @Slot()
    def _update_status(self) -> None:
        """
        Aktualisiert den Systemstatus.
        """
        if not self._telemetry:
            return
            
        # Status prüfen
        if self._status == FlightStatus.FLYING:
            # Mission prüfen
            mission = self._waypoint_manager.get_current_mission()
            if not mission:
                self._set_status(FlightStatus.ARMED)
                return
                
            # Wegpunkt prüfen
            waypoint = self._waypoint_manager.get_current_waypoint()
            if not waypoint:
                self._set_status(FlightStatus.ARMED)
                self.mission_completed.emit(mission)
                return
                
    def _set_status(self, status: FlightStatus) -> None:
        """
        Setzt den Systemstatus.
        
        Args:
            status: Neuer Status
        """
        if self._status != status:
            self._status = status
            self.status_changed.emit(status)
            
    def _set_error(self, message: str) -> None:
        """
        Setzt eine Fehlermeldung.
        
        Args:
            message: Fehlermeldung
        """
        self.error_occurred.emit(message) 