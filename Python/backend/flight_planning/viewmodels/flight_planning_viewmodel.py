"""Flugplanungs-ViewModel.

Dieses ViewModel stellt die Verbindung zwischen dem Flugplanungs-Service und der View her.
Es verwaltet den UI-Zustand und leitet Benutzerinteraktionen an den Service weiter.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from PySide6.QtCore import QObject, Signal, Slot, Property

from backend.flight_planning.models.flight_planning_data import (
    Waypoint,
    Route,
    Mission,
    MissionStatus,
    MissionEvent,
    MissionLog,
    FlightPlanningError,
    FlightPlanningValidationError,
    FlightPlanningCommandError,
    FlightPlanningMissionError
)
from backend.flight_planning.services.flight_planning_service import FlightPlanningService

class FlightPlanningViewModel(QObject):
    """Flugplanungs-ViewModel.
    
    Dieses ViewModel stellt die Verbindung zwischen dem Flugplanungs-Service und der View her.
    
    Attributes:
        _service (FlightPlanningService): Flugplanungs-Service
        _mission (Mission): Aktuelle Mission
        _current_route (Route): Aktuelle Route
        _current_waypoint (Waypoint): Aktueller Wegpunkt
        _log (MissionLog): Missions-Log
        
    Signals:
        mission_changed: Wird ausgelöst, wenn sich die Mission ändert
        route_changed: Wird ausgelöst, wenn sich die Route ändert
        waypoint_changed: Wird ausgelöst, wenn sich der Wegpunkt ändert
        log_changed: Wird ausgelöst, wenn sich das Log ändert
    """
    
    # Signale
    mission_changed = Signal()
    route_changed = Signal()
    waypoint_changed = Signal()
    log_changed = Signal()
    
    def __init__(self):
        """Initialisierung."""
        super().__init__()
        self._service = None
        self._mission = None
        self._current_route = None
        self._current_waypoint = None
        self._log = None
    
    def set_service(self, service: FlightPlanningService):
        """Service setzen.
        
        Args:
            service: Flugplanungs-Service
        """
        self._service = service
        
        # Service-Signale verbinden
        self._service.mission_changed.connect(self._update_mission)
        self._service.route_changed.connect(self._update_route)
        self._service.waypoint_changed.connect(self._update_waypoint)
        self._service.log_changed.connect(self._update_log)
    
    @Property(bool, notify=mission_changed)
    def has_mission(self) -> bool:
        """Mission vorhanden."""
        return self._mission is not None
    
    @Property(str, notify=mission_changed)
    def mission_id(self) -> str:
        """Mission-ID."""
        return self._mission.id if self._mission else ""
    
    @Property(str, notify=mission_changed)
    def mission_name(self) -> str:
        """Mission-Name."""
        return self._mission.name if self._mission else ""
    
    @Property(str, notify=mission_changed)
    def mission_status(self) -> str:
        """Mission-Status."""
        return self._mission.status.value if self._mission else MissionStatus.INACTIVE.value
    
    @Property(bool, notify=mission_changed)
    def is_mission_active(self) -> bool:
        """Mission aktiv."""
        return self._mission and self._mission.status == MissionStatus.ACTIVE
    
    @Property(bool, notify=mission_changed)
    def is_mission_paused(self) -> bool:
        """Mission pausiert."""
        return self._mission and self._mission.status == MissionStatus.PAUSED
    
    @Property(bool, notify=mission_changed)
    def is_mission_completed(self) -> bool:
        """Mission abgeschlossen."""
        return self._mission and self._mission.status == MissionStatus.COMPLETED
    
    @Property(bool, notify=mission_changed)
    def is_mission_error(self) -> bool:
        """Mission fehlerhaft."""
        return self._mission and self._mission.status == MissionStatus.ERROR
    
    @Property(bool, notify=route_changed)
    def has_route(self) -> bool:
        """Route vorhanden."""
        return self._current_route is not None
    
    @Property(str, notify=route_changed)
    def route_id(self) -> str:
        """Route-ID."""
        return self._current_route.id if self._current_route else ""
    
    @Property(str, notify=route_changed)
    def route_name(self) -> str:
        """Route-Name."""
        return self._current_route.name if self._current_route else ""
    
    @Property(bool, notify=waypoint_changed)
    def has_waypoint(self) -> bool:
        """Wegpunkt vorhanden."""
        return self._current_waypoint is not None
    
    @Property(str, notify=waypoint_changed)
    def waypoint_id(self) -> str:
        """Wegpunkt-ID."""
        return self._current_waypoint.id if self._current_waypoint else ""
    
    @Property(str, notify=waypoint_changed)
    def waypoint_type(self) -> str:
        """Wegpunkt-Typ."""
        return self._current_waypoint.type.value if self._current_waypoint else ""
    
    @Property(str, notify=waypoint_changed)
    def waypoint_action(self) -> str:
        """Wegpunkt-Aktion."""
        return self._current_waypoint.action.value if self._current_waypoint else ""
    
    @Property(list, notify=waypoint_changed)
    def waypoint_position(self) -> List[float]:
        """Wegpunkt-Position."""
        if not self._current_waypoint:
            return [0.0, 0.0, 0.0]
        
        pos = self._current_waypoint.position
        return [pos['latitude'], pos['longitude'], pos['altitude']]
    
    @Property(list, notify=log_changed)
    def log_events(self) -> List[str]:
        """Log-Events."""
        return [event.description for event in self._log.events] if self._log else []
    
    @Property(str, notify=log_changed)
    def last_event(self) -> str:
        """Letztes Event."""
        return self._log.last_event.description if self._log and self._log.last_event else ""
    
    def create_mission(self, name: str, parameters: Dict[str, Any] = None):
        """Erstelle neue Mission.
        
        Args:
            name: Name der Mission
            parameters: Zusätzliche Parameter
        """
        if not self._service:
            raise FlightPlanningCommandError("No service set")
        
        try:
            self._service.create_mission(name, parameters)
        except FlightPlanningError as e:
            self._handle_error(str(e))
    
    def add_route(self, name: str, parameters: Dict[str, Any] = None):
        """Füge Route zur Mission hinzu.
        
        Args:
            name: Name der Route
            parameters: Zusätzliche Parameter
        """
        if not self._service:
            raise FlightPlanningCommandError("No service set")
        
        try:
            self._service.add_route(name, parameters)
        except FlightPlanningError as e:
            self._handle_error(str(e))
    
    def add_waypoint(
        self,
        route_id: str,
        waypoint_type: str,
        position: Dict[str, float],
        action: str = "NONE",
        parameters: Dict[str, Any] = None
    ):
        """Füge Wegpunkt zur Route hinzu.
        
        Args:
            route_id: ID der Route
            waypoint_type: Typ des Wegpunkts
            position: Position (lat, lon, alt)
            action: Aktion am Wegpunkt
            parameters: Zusätzliche Parameter
        """
        if not self._service:
            raise FlightPlanningCommandError("No service set")
        
        try:
            self._service.add_waypoint(route_id, waypoint_type, position, action, parameters)
        except FlightPlanningError as e:
            self._handle_error(str(e))
    
    def update_waypoint(
        self,
        waypoint_id: str,
        position: Dict[str, float] = None,
        action: str = None,
        parameters: Dict[str, Any] = None
    ):
        """Aktualisiere Wegpunkt.
        
        Args:
            waypoint_id: ID des Wegpunkts
            position: Neue Position
            action: Neue Aktion
            parameters: Neue Parameter
        """
        if not self._service:
            raise FlightPlanningCommandError("No service set")
        
        try:
            self._service.update_waypoint(waypoint_id, position, action, parameters)
        except FlightPlanningError as e:
            self._handle_error(str(e))
    
    def delete_waypoint(self, waypoint_id: str):
        """Lösche Wegpunkt.
        
        Args:
            waypoint_id: ID des Wegpunkts
        """
        if not self._service:
            raise FlightPlanningCommandError("No service set")
        
        try:
            self._service.delete_waypoint(waypoint_id)
        except FlightPlanningError as e:
            self._handle_error(str(e))
    
    def start_mission(self):
        """Starte Mission."""
        if not self._service:
            raise FlightPlanningCommandError("No service set")
        
        try:
            self._service.start_mission()
        except FlightPlanningError as e:
            self._handle_error(str(e))
    
    def pause_mission(self):
        """Pausiere Mission."""
        if not self._service:
            raise FlightPlanningCommandError("No service set")
        
        try:
            self._service.pause_mission()
        except FlightPlanningError as e:
            self._handle_error(str(e))
    
    def resume_mission(self):
        """Setze Mission fort."""
        if not self._service:
            raise FlightPlanningCommandError("No service set")
        
        try:
            self._service.resume_mission()
        except FlightPlanningError as e:
            self._handle_error(str(e))
    
    def complete_mission(self):
        """Schließe Mission ab."""
        if not self._service:
            raise FlightPlanningCommandError("No service set")
        
        try:
            self._service.complete_mission()
        except FlightPlanningError as e:
            self._handle_error(str(e))
    
    def abort_mission(self):
        """Breche Mission ab."""
        if not self._service:
            raise FlightPlanningCommandError("No service set")
        
        try:
            self._service.abort_mission()
        except FlightPlanningError as e:
            self._handle_error(str(e))
    
    def next_waypoint(self):
        """Gehe zum nächsten Wegpunkt."""
        if not self._service:
            raise FlightPlanningCommandError("No service set")
        
        try:
            self._service.next_waypoint()
        except FlightPlanningError as e:
            self._handle_error(str(e))
    
    def _update_mission(self):
        """Mission aktualisieren."""
        self._mission = self._service.mission
        self.mission_changed.emit()
    
    def _update_route(self):
        """Route aktualisieren."""
        self._current_route = self._service.current_route
        self.route_changed.emit()
    
    def _update_waypoint(self):
        """Wegpunkt aktualisieren."""
        self._current_waypoint = self._service.current_waypoint
        self.waypoint_changed.emit()
    
    def _update_log(self):
        """Log aktualisieren."""
        self._log = self._service.log
        self.log_changed.emit()
    
    def _handle_error(self, error_message: str):
        """Fehler behandeln.
        
        Args:
            error_message: Fehlermeldung
        """
        if self._mission:
            self._mission.status = MissionStatus.ERROR
            self.mission_changed.emit() 