"""Flugplanungs-Service.

Dieser Service implementiert die Geschäftslogik für die Flugplanung:
- Missionsverwaltung
- Routenverwaltung
- Wegpunktverwaltung
- Missionsausführung
- Missionsüberwachung
- Logging
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from PySide6.QtCore import QObject, Signal

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

class FlightPlanningService(QObject):
    """Flugplanungs-Service.
    
    Dieser Service implementiert die Geschäftslogik für die Flugplanung.
    
    Signals:
        state_changed: Wird ausgelöst, wenn sich der Zustand ändert
        mission_changed: Wird ausgelöst, wenn sich die Mission ändert
        route_changed: Wird ausgelöst, wenn sich die Route ändert
        waypoint_changed: Wird ausgelöst, wenn sich der Wegpunkt ändert
        log_changed: Wird ausgelöst, wenn sich das Log ändert
    """
    
    # Signale
    state_changed = Signal()
    mission_changed = Signal()
    route_changed = Signal()
    waypoint_changed = Signal()
    log_changed = Signal()
    
    def __init__(self):
        """Initialisierung."""
        super().__init__()
        self._mission = None
        self._current_route = None
        self._current_waypoint = None
        self._log = MissionLog()
    
    @property
    def mission(self) -> Optional[Mission]:
        """Aktuelle Mission."""
        return self._mission
    
    @property
    def current_route(self) -> Optional[Route]:
        """Aktuelle Route."""
        return self._current_route
    
    @property
    def current_waypoint(self) -> Optional[Waypoint]:
        """Aktueller Wegpunkt."""
        return self._current_waypoint
    
    @property
    def log(self) -> MissionLog:
        """Missions-Log."""
        return self._log
    
    def create_mission(self, name: str, parameters: Dict[str, Any] = None) -> Mission:
        """Erstelle neue Mission.
        
        Args:
            name: Name der Mission
            parameters: Zusätzliche Parameter
            
        Returns:
            Neue Mission
            
        Raises:
            FlightPlanningValidationError: Bei Validierungsfehlern
        """
        if not name:
            raise FlightPlanningValidationError("Mission-Name fehlt")
        
        mission = Mission(
            id=f"mission_{datetime.now().timestamp()}",
            name=name,
            parameters=parameters or {}
        )
        
        self._mission = mission
        self._log.add_event(MissionEvent(
            timestamp=datetime.now(),
            event_type="CREATE_MISSION",
            description=f"Mission '{name}' erstellt"
        ))
        
        self.mission_changed.emit()
        self.state_changed.emit()
        
        return mission
    
    def add_route(self, name: str, parameters: Dict[str, Any] = None) -> Route:
        """Füge Route zur Mission hinzu.
        
        Args:
            name: Name der Route
            parameters: Zusätzliche Parameter
            
        Returns:
            Neue Route
            
        Raises:
            FlightPlanningCommandError: Wenn keine Mission existiert
            FlightPlanningValidationError: Bei Validierungsfehlern
        """
        if not self._mission:
            raise FlightPlanningCommandError("Keine aktive Mission")
        
        if not name:
            raise FlightPlanningValidationError("Route-Name fehlt")
        
        route = Route(
            id=f"route_{datetime.now().timestamp()}",
            name=name,
            parameters=parameters or {}
        )
        
        self._mission.routes.append(route)
        self._log.add_event(MissionEvent(
            timestamp=datetime.now(),
            event_type="ADD_ROUTE",
            description=f"Route '{name}' hinzugefügt"
        ))
        
        self.route_changed.emit()
        self.mission_changed.emit()
        self.state_changed.emit()
        
        return route
    
    def add_waypoint(
        self,
        route_id: str,
        waypoint_type: str,
        position: Dict[str, float],
        action: str = "NONE",
        parameters: Dict[str, Any] = None
    ) -> Waypoint:
        """Füge Wegpunkt zur Route hinzu.
        
        Args:
            route_id: ID der Route
            waypoint_type: Typ des Wegpunkts
            position: Position (lat, lon, alt)
            action: Aktion am Wegpunkt
            parameters: Zusätzliche Parameter
            
        Returns:
            Neuer Wegpunkt
            
        Raises:
            FlightPlanningCommandError: Wenn keine Mission existiert
            FlightPlanningValidationError: Bei Validierungsfehlern
        """
        if not self._mission:
            raise FlightPlanningCommandError("Keine aktive Mission")
        
        route = next((r for r in self._mission.routes if r.id == route_id), None)
        if not route:
            raise FlightPlanningValidationError(f"Route '{route_id}' nicht gefunden")
        
        waypoint = Waypoint(
            id=f"waypoint_{datetime.now().timestamp()}",
            type=waypoint_type,
            position=position,
            action=action,
            parameters=parameters or {},
            order=len(route.waypoints)
        )
        
        route.waypoints.append(waypoint)
        self._log.add_event(MissionEvent(
            timestamp=datetime.now(),
            event_type="ADD_WAYPOINT",
            description=f"Wegpunkt {waypoint.id} hinzugefügt"
        ))
        
        self.waypoint_changed.emit()
        self.route_changed.emit()
        self.mission_changed.emit()
        self.state_changed.emit()
        
        return waypoint
    
    def update_waypoint(
        self,
        waypoint_id: str,
        position: Dict[str, float] = None,
        action: str = None,
        parameters: Dict[str, Any] = None
    ) -> Waypoint:
        """Aktualisiere Wegpunkt.
        
        Args:
            waypoint_id: ID des Wegpunkts
            position: Neue Position
            action: Neue Aktion
            parameters: Neue Parameter
            
        Returns:
            Aktualisierter Wegpunkt
            
        Raises:
            FlightPlanningCommandError: Wenn keine Mission existiert
            FlightPlanningValidationError: Bei Validierungsfehlern
        """
        if not self._mission:
            raise FlightPlanningCommandError("Keine aktive Mission")
        
        waypoint = None
        for route in self._mission.routes:
            waypoint = next((w for w in route.waypoints if w.id == waypoint_id), None)
            if waypoint:
                break
        
        if not waypoint:
            raise FlightPlanningValidationError(f"Wegpunkt '{waypoint_id}' nicht gefunden")
        
        if position:
            waypoint.position = position
        
        if action:
            waypoint.action = action
        
        if parameters:
            waypoint.parameters.update(parameters)
        
        self._log.add_event(MissionEvent(
            timestamp=datetime.now(),
            event_type="UPDATE_WAYPOINT",
            description=f"Wegpunkt {waypoint_id} aktualisiert"
        ))
        
        self.waypoint_changed.emit()
        self.route_changed.emit()
        self.mission_changed.emit()
        self.state_changed.emit()
        
        return waypoint
    
    def delete_waypoint(self, waypoint_id: str) -> None:
        """Lösche Wegpunkt.
        
        Args:
            waypoint_id: ID des Wegpunkts
            
        Raises:
            FlightPlanningCommandError: Wenn keine Mission existiert
            FlightPlanningValidationError: Bei Validierungsfehlern
        """
        if not self._mission:
            raise FlightPlanningCommandError("Keine aktive Mission")
        
        for route in self._mission.routes:
            waypoint = next((w for w in route.waypoints if w.id == waypoint_id), None)
            if waypoint:
                route.waypoints.remove(waypoint)
                self._log.add_event(MissionEvent(
                    timestamp=datetime.now(),
                    event_type="DELETE_WAYPOINT",
                    description=f"Wegpunkt {waypoint_id} gelöscht"
                ))
                
                self.waypoint_changed.emit()
                self.route_changed.emit()
                self.mission_changed.emit()
                self.state_changed.emit()
                return
        
        raise FlightPlanningValidationError(f"Wegpunkt '{waypoint_id}' nicht gefunden")
    
    def validate_mission(self) -> None:
        """Validiere Mission.
        
        Raises:
            FlightPlanningCommandError: Wenn keine Mission existiert
            FlightPlanningValidationError: Bei Validierungsfehlern
        """
        if not self._mission:
            raise FlightPlanningCommandError("Keine aktive Mission")
        
        self._mission.validate()
    
    def start_mission(self) -> None:
        """Starte Mission.
        
        Raises:
            FlightPlanningCommandError: Wenn keine Mission existiert
            FlightPlanningValidationError: Bei Validierungsfehlern
        """
        if not self._mission:
            raise FlightPlanningCommandError("Keine aktive Mission")
        
        self.validate_mission()
        
        self._mission.status = MissionStatus.ACTIVE
        self._current_route = self._mission.routes[0] if self._mission.routes else None
        self._current_waypoint = self._current_route.waypoints[0] if self._current_route else None
        
        self._log.add_event(MissionEvent(
            timestamp=datetime.now(),
            event_type="START_MISSION",
            description="Mission gestartet"
        ))
        
        self.mission_changed.emit()
        self.state_changed.emit()
    
    def pause_mission(self) -> None:
        """Pausiere Mission.
        
        Raises:
            FlightPlanningCommandError: Wenn keine Mission existiert
        """
        if not self._mission:
            raise FlightPlanningCommandError("Keine aktive Mission")
        
        self._mission.status = MissionStatus.PAUSED
        
        self._log.add_event(MissionEvent(
            timestamp=datetime.now(),
            event_type="PAUSE_MISSION",
            description="Mission pausiert"
        ))
        
        self.mission_changed.emit()
        self.state_changed.emit()
    
    def resume_mission(self) -> None:
        """Setze Mission fort.
        
        Raises:
            FlightPlanningCommandError: Wenn keine Mission existiert
        """
        if not self._mission:
            raise FlightPlanningCommandError("Keine aktive Mission")
        
        self._mission.status = MissionStatus.ACTIVE
        
        self._log.add_event(MissionEvent(
            timestamp=datetime.now(),
            event_type="RESUME_MISSION",
            description="Mission fortgesetzt"
        ))
        
        self.mission_changed.emit()
        self.state_changed.emit()
    
    def complete_mission(self) -> None:
        """Schließe Mission ab.
        
        Raises:
            FlightPlanningCommandError: Wenn keine Mission existiert
        """
        if not self._mission:
            raise FlightPlanningCommandError("Keine aktive Mission")
        
        self._mission.status = MissionStatus.COMPLETED
        self._current_route = None
        self._current_waypoint = None
        
        self._log.add_event(MissionEvent(
            timestamp=datetime.now(),
            event_type="COMPLETE_MISSION",
            description="Mission abgeschlossen"
        ))
        
        self.mission_changed.emit()
        self.state_changed.emit()
    
    def abort_mission(self) -> None:
        """Breche Mission ab.
        
        Raises:
            FlightPlanningCommandError: Wenn keine Mission existiert
        """
        if not self._mission:
            raise FlightPlanningCommandError("Keine aktive Mission")
        
        self._mission.status = MissionStatus.ERROR
        self._current_route = None
        self._current_waypoint = None
        
        self._log.add_event(MissionEvent(
            timestamp=datetime.now(),
            event_type="ABORT_MISSION",
            description="Mission abgebrochen"
        ))
        
        self.mission_changed.emit()
        self.state_changed.emit()
    
    def next_waypoint(self) -> Optional[Waypoint]:
        """Gehe zum nächsten Wegpunkt.
        
        Returns:
            Nächster Wegpunkt oder None
            
        Raises:
            FlightPlanningCommandError: Wenn keine Mission existiert
        """
        if not self._mission:
            raise FlightPlanningCommandError("Keine aktive Mission")
        
        if not self._current_route or not self._current_waypoint:
            return None
        
        current_index = self._current_route.waypoints.index(self._current_waypoint)
        if current_index + 1 < len(self._current_route.waypoints):
            self._current_waypoint = self._current_route.waypoints[current_index + 1]
        else:
            route_index = self._mission.routes.index(self._current_route)
            if route_index + 1 < len(self._mission.routes):
                self._current_route = self._mission.routes[route_index + 1]
                self._current_waypoint = self._current_route.waypoints[0]
            else:
                self.complete_mission()
                return None
        
        self._log.add_event(MissionEvent(
            timestamp=datetime.now(),
            event_type="NEXT_WAYPOINT",
            description=f"Wegpunkt {self._current_waypoint.id} erreicht"
        ))
        
        self.waypoint_changed.emit()
        self.route_changed.emit()
        self.mission_changed.emit()
        self.state_changed.emit()
        
        return self._current_waypoint 