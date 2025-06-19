"""
Autonomes Flug-ViewModel.
Implementiert die Präsentationslogik für autonome Flugoperationen.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime

from PySide6.QtCore import QObject, Signal, Slot, Property

from ..models.flight_data import Position, Waypoint, Mission, FlightState, ControlCommand, MissionPlan
from ..enums import FlightStatus, FlightMode, ControlMode, CommandType, EmergencyProcedure
from ..services.autonomous_service import AutonomousService

class AutonomousViewModel(QObject):
    """Implementiert die Präsentationslogik für autonome Flugoperationen"""
    
    # Signale
    state_changed = Signal(FlightState)
    mode_changed = Signal(FlightMode)
    error_occurred = Signal(str)
    command_executed = Signal(ControlCommand)
    mission_started = Signal(Mission)
    mission_completed = Signal(Mission)
    mission_aborted = Signal(Mission)
    emergency_triggered = Signal(EmergencyProcedure)
    
    def __init__(self, service: Optional[AutonomousService] = None):
        """
        Initialisiert das autonome Flug-ViewModel.
        
        Args:
            service: Optional: Autonomer Flug-Service
        """
        super().__init__()
        
        # Service setzen
        self._service = service
        
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
        
        # Signal-Verbindungen
        if self._service:
            self._service.state_changed.connect(self._on_state_changed)
            self._service.mode_changed.connect(self._on_mode_changed)
            self._service.error_occurred.connect(self._on_error)
            self._service.command_executed.connect(self._on_command_executed)
            self._service.mission_started.connect(self._on_mission_started)
            self._service.mission_completed.connect(self._on_mission_completed)
            self._service.mission_aborted.connect(self._on_mission_aborted)
            self._service.emergency_triggered.connect(self._on_emergency_triggered)
            
    def set_service(self, service: AutonomousService) -> None:
        """
        Setzt den autonomen Flug-Service.
        
        Args:
            service: Autonomer Flug-Service
        """
        self._service = service
        
        # Signal-Verbindungen
        if self._service:
            self._service.state_changed.connect(self._on_state_changed)
            self._service.mode_changed.connect(self._on_mode_changed)
            self._service.error_occurred.connect(self._on_error)
            self._service.command_executed.connect(self._on_command_executed)
            self._service.mission_started.connect(self._on_mission_started)
            self._service.mission_completed.connect(self._on_mission_completed)
            self._service.mission_aborted.connect(self._on_mission_aborted)
            self._service.emergency_triggered.connect(self._on_emergency_triggered)
            
    @Slot(FlightMode)
    def set_mode(self, mode: FlightMode) -> bool:
        """
        Setzt den Flugmodus.
        
        Args:
            mode: Flugmodus
            
        Returns:
            True wenn erfolgreich, sonst False
        """
        if not self._service:
            return False
            
        return self._service.set_mode(mode)
        
    @Slot(ControlCommand)
    def execute_command(self, command: ControlCommand) -> bool:
        """
        Führt einen Steuerungsbefehl aus.
        
        Args:
            command: Steuerungsbefehl
            
        Returns:
            True wenn erfolgreich, sonst False
        """
        if not self._service:
            return False
            
        return self._service.execute_command(command)
        
    @Slot(Mission)
    def start_mission(self, mission: Mission) -> bool:
        """
        Startet eine Mission.
        
        Args:
            mission: Mission
            
        Returns:
            True wenn erfolgreich, sonst False
        """
        if not self._service:
            return False
            
        return self._service.start_mission(mission)
        
    @Slot()
    def pause_mission(self) -> bool:
        """
        Pausiert die aktuelle Mission.
        
        Returns:
            True wenn erfolgreich, sonst False
        """
        if not self._service:
            return False
            
        return self._service.pause_mission()
        
    @Slot()
    def resume_mission(self) -> bool:
        """
        Setzt die aktuelle Mission fort.
        
        Returns:
            True wenn erfolgreich, sonst False
        """
        if not self._service:
            return False
            
        return self._service.resume_mission()
        
    @Slot()
    def abort_mission(self) -> bool:
        """
        Bricht die aktuelle Mission ab.
        
        Returns:
            True wenn erfolgreich, sonst False
        """
        if not self._service:
            return False
            
        return self._service.abort_mission()
        
    @Slot(EmergencyProcedure)
    def execute_emergency_procedure(self, procedure: EmergencyProcedure) -> bool:
        """
        Führt eine Notfallprozedur aus.
        
        Args:
            procedure: Notfallprozedur
            
        Returns:
            True wenn erfolgreich, sonst False
        """
        if not self._service:
            return False
            
        return self._service.execute_emergency_procedure(procedure)
        
    @Slot(FlightState)
    def _on_state_changed(self, state: FlightState) -> None:
        """
        Handler für Statusänderungen.
        
        Args:
            state: Neuer Status
        """
        self._state = state
        self.state_changed.emit(state)
        
    @Slot(FlightMode)
    def _on_mode_changed(self, mode: FlightMode) -> None:
        """
        Handler für Modusänderungen.
        
        Args:
            mode: Neuer Modus
        """
        self._mode = mode
        self.mode_changed.emit(mode)
        
    @Slot(str)
    def _on_error(self, message: str) -> None:
        """
        Handler für Fehler.
        
        Args:
            message: Fehlermeldung
        """
        self.error_occurred.emit(message)
        
    @Slot(ControlCommand)
    def _on_command_executed(self, command: ControlCommand) -> None:
        """
        Handler für ausgeführte Befehle.
        
        Args:
            command: Ausgeführter Befehl
        """
        self.command_executed.emit(command)
        
    @Slot(Mission)
    def _on_mission_started(self, mission: Mission) -> None:
        """
        Handler für gestartete Missionen.
        
        Args:
            mission: Gestartete Mission
        """
        self.mission_started.emit(mission)
        
    @Slot(Mission)
    def _on_mission_completed(self, mission: Mission) -> None:
        """
        Handler für abgeschlossene Missionen.
        
        Args:
            mission: Abgeschlossene Mission
        """
        self.mission_completed.emit(mission)
        
    @Slot(Mission)
    def _on_mission_aborted(self, mission: Mission) -> None:
        """
        Handler für abgebrochene Missionen.
        
        Args:
            mission: Abgebrochene Mission
        """
        self.mission_aborted.emit(mission)
        
    @Slot(EmergencyProcedure)
    def _on_emergency_triggered(self, procedure: EmergencyProcedure) -> None:
        """
        Handler für ausgelöste Notfallprozeduren.
        
        Args:
            procedure: Ausgelöste Notfallprozedur
        """
        self.emergency_triggered.emit(procedure) 