"""Datenmodelle für die Flugplanung.

Diese Module definieren die Datenstrukturen für die Flugplanung:
- FlightPlan: Flugplan mit Waypoints und Routen
- Waypoint: Einzelner Wegpunkt mit Position und Aktionen
- Route: Route mit mehreren Waypoints
- Mission: Mission mit mehreren Routen
- MissionStatus: Status einer Mission
- MissionEvent: Event während einer Mission
- MissionLog: Log für Mission-Events
- Fehlerklassen für die Flugplanung
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime

class WaypointType(Enum):
    """Typ eines Wegpunkts."""
    TAKEOFF = "TAKEOFF"  # Startpunkt
    LANDING = "LANDING"  # Landepunkt
    WAYPOINT = "WAYPOINT"  # Normaler Wegpunkt
    HOLD = "HOLD"  # Wartepunkt
    SURVEY = "SURVEY"  # Vermessungspunkt
    ACTION = "ACTION"  # Aktionspunkt

class WaypointAction(Enum):
    """Aktion an einem Wegpunkt."""
    NONE = "NONE"  # Keine Aktion
    PHOTO = "PHOTO"  # Foto aufnehmen
    VIDEO = "VIDEO"  # Video aufnehmen
    SCAN = "SCAN"  # Scannen
    DROP = "DROP"  # Abwurf
    PICKUP = "PICKUP"  # Aufnahme

class MissionStatus(Enum):
    """Status einer Mission."""
    INACTIVE = "INACTIVE"  # Inaktiv
    PLANNING = "PLANNING"  # In Planung
    READY = "READY"  # Bereit
    ACTIVE = "ACTIVE"  # Aktiv
    PAUSED = "PAUSED"  # Pausiert
    COMPLETED = "COMPLETED"  # Abgeschlossen
    ERROR = "ERROR"  # Fehler

@dataclass
class Waypoint:
    """Wegpunkt in einem Flugplan.
    
    Attributes:
        id: Eindeutige ID
        type: Typ des Wegpunkts
        position: Position (lat, lon, alt)
        action: Aktion am Wegpunkt
        parameters: Zusätzliche Parameter
        order: Reihenfolge in der Route
    """
    id: str
    type: WaypointType
    position: Dict[str, float]  # lat, lon, alt
    action: WaypointAction = WaypointAction.NONE
    parameters: Dict[str, Any] = field(default_factory=dict)
    order: int = 0
    
    def validate(self) -> None:
        """Validiere den Wegpunkt.
        
        Raises:
            FlightPlanningValidationError: Bei Validierungsfehlern
        """
        if not self.id:
            raise FlightPlanningValidationError("Wegpunkt-ID fehlt")
        
        if not isinstance(self.type, WaypointType):
            raise FlightPlanningValidationError("Ungültiger Wegpunkt-Typ")
        
        if not isinstance(self.action, WaypointAction):
            raise FlightPlanningValidationError("Ungültige Wegpunkt-Aktion")
        
        if not isinstance(self.position, dict):
            raise FlightPlanningValidationError("Ungültige Position")
        
        required_keys = ['latitude', 'longitude', 'altitude']
        if not all(key in self.position for key in required_keys):
            raise FlightPlanningValidationError("Position unvollständig")
        
        if not isinstance(self.order, int) or self.order < 0:
            raise FlightPlanningValidationError("Ungültige Reihenfolge")

@dataclass
class Route:
    """Route mit mehreren Wegpunkten.
    
    Attributes:
        id: Eindeutige ID
        name: Name der Route
        waypoints: Liste der Wegpunkte
        parameters: Zusätzliche Parameter
    """
    id: str
    name: str
    waypoints: List[Waypoint] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    def validate(self) -> None:
        """Validiere die Route.
        
        Raises:
            FlightPlanningValidationError: Bei Validierungsfehlern
        """
        if not self.id:
            raise FlightPlanningValidationError("Route-ID fehlt")
        
        if not self.name:
            raise FlightPlanningValidationError("Route-Name fehlt")
        
        if not self.waypoints:
            raise FlightPlanningValidationError("Route hat keine Wegpunkte")
        
        # Validiere jeden Wegpunkt
        for waypoint in self.waypoints:
            waypoint.validate()
        
        # Prüfe Reihenfolge
        orders = [w.order for w in self.waypoints]
        if len(set(orders)) != len(orders):
            raise FlightPlanningValidationError("Doppelte Reihenfolge in Wegpunkten")

@dataclass
class Mission:
    """Mission mit mehreren Routen.
    
    Attributes:
        id: Eindeutige ID
        name: Name der Mission
        routes: Liste der Routen
        status: Status der Mission
        parameters: Zusätzliche Parameter
    """
    id: str
    name: str
    routes: List[Route] = field(default_factory=list)
    status: MissionStatus = MissionStatus.INACTIVE
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    def validate(self) -> None:
        """Validiere die Mission.
        
        Raises:
            FlightPlanningValidationError: Bei Validierungsfehlern
        """
        if not self.id:
            raise FlightPlanningValidationError("Mission-ID fehlt")
        
        if not self.name:
            raise FlightPlanningValidationError("Mission-Name fehlt")
        
        if not self.routes:
            raise FlightPlanningValidationError("Mission hat keine Routen")
        
        # Validiere jede Route
        for route in self.routes:
            route.validate()

@dataclass
class MissionEvent:
    """Event während einer Mission.
    
    Attributes:
        timestamp: Zeitstempel
        event_type: Typ des Events
        description: Beschreibung
        parameters: Zusätzliche Parameter
    """
    timestamp: datetime
    event_type: str
    description: str
    parameters: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MissionLog:
    """Log für Mission-Events.
    
    Attributes:
        events: Liste der Events
        max_events: Maximale Anzahl der Events
    """
    events: List[MissionEvent] = field(default_factory=list)
    max_events: int = 1000
    
    @property
    def last_event(self) -> Optional[MissionEvent]:
        """Letztes Event."""
        return self.events[-1] if self.events else None
    
    def add_event(self, event: MissionEvent) -> None:
        """Füge Event hinzu.
        
        Args:
            event: Neues Event
        """
        self.events.append(event)
        
        # Begrenze Anzahl der Events
        if len(self.events) > self.max_events:
            self.events = self.events[-self.max_events:]
    
    def clear(self) -> None:
        """Lösche alle Events."""
        self.events.clear()

class FlightPlanningError(Exception):
    """Basisklasse für Flugplanungs-Fehler."""
    pass

class FlightPlanningValidationError(FlightPlanningError):
    """Validierungsfehler bei der Flugplanung."""
    pass

class FlightPlanningCommandError(FlightPlanningError):
    """Befehlsfehler bei der Flugplanung."""
    pass

class FlightPlanningMissionError(FlightPlanningError):
    """Fehler bei der Mission."""
    pass 