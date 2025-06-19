# Flugplanungs-API

## Übersicht

Die Flugplanungs-API bietet Schnittstellen für die Erstellung, Verwaltung und Ausführung von Flugmissionen.

## Model

### Waypoint

```python
class Waypoint:
    def __init__(self, id: str, type: str, position: Dict[str, float], action: str = "NONE"):
        """
        Erstellt einen neuen Wegpunkt.

        Args:
            id: Eindeutige ID des Wegpunkts
            type: Typ des Wegpunkts (TAKEOFF, LANDING, WAYPOINT, HOLD, SURVEY, ACTION)
            position: Position des Wegpunkts (latitude, longitude, altitude)
            action: Aktion am Wegpunkt (NONE, PHOTO, VIDEO, SCAN, DROP, PICKUP)
        """
```

### Route

```python
class Route:
    def __init__(self, id: str, name: str, waypoints: List[Waypoint] = None):
        """
        Erstellt eine neue Route.

        Args:
            id: Eindeutige ID der Route
            name: Name der Route
            waypoints: Liste der Wegpunkte
        """

    def add_waypoint(self, waypoint: Waypoint):
        """
        Fügt einen Wegpunkt zur Route hinzu.

        Args:
            waypoint: Der hinzuzufügende Wegpunkt
        """

    def remove_waypoint(self, waypoint_id: str):
        """
        Entfernt einen Wegpunkt aus der Route.

        Args:
            waypoint_id: ID des zu entfernenden Wegpunkts
        """
```

### Mission

```python
class Mission:
    def __init__(self, id: str, name: str, status: MissionStatus = MissionStatus.INACTIVE, routes: List[Route] = None):
        """
        Erstellt eine neue Mission.

        Args:
            id: Eindeutige ID der Mission
            name: Name der Mission
            status: Status der Mission
            routes: Liste der Routen
        """

    def add_route(self, route: Route):
        """
        Fügt eine Route zur Mission hinzu.

        Args:
            route: Die hinzuzufügende Route
        """

    def remove_route(self, route_id: str):
        """
        Entfernt eine Route aus der Mission.

        Args:
            route_id: ID der zu entfernenden Route
        """

    def start(self):
        """Startet die Mission."""

    def pause(self):
        """Pausiert die Mission."""

    def resume(self):
        """Setzt die Mission fort."""

    def complete(self):
        """Schließt die Mission ab."""

    def set_error(self, error_message: str):
        """
        Setzt die Mission auf Fehlerstatus.

        Args:
            error_message: Fehlermeldung
        """
```

### MissionLog

```python
class MissionLog:
    def __init__(self):
        """Erstellt ein neues Missions-Log."""

    def add_event(self, event: MissionEvent):
        """
        Fügt ein Event zum Log hinzu.

        Args:
            event: Das hinzuzufügende Event
        """

    @property
    def last_event(self) -> MissionEvent:
        """Gibt das letzte Event zurück."""
```

## Service

### FlightPlanningService

```python
class FlightPlanningService:
    def create_mission(self, name: str, parameters: Dict[str, Any] = None) -> Mission:
        """
        Erstellt eine neue Mission.

        Args:
            name: Name der Mission
            parameters: Zusätzliche Parameter

        Returns:
            Die erstellte Mission
        """

    def add_route(self, name: str, parameters: Dict[str, Any] = None) -> Route:
        """
        Fügt eine Route zur aktuellen Mission hinzu.

        Args:
            name: Name der Route
            parameters: Zusätzliche Parameter

        Returns:
            Die erstellte Route
        """

    def add_waypoint(
        self,
        route_id: str,
        waypoint_type: str,
        position: Dict[str, float],
        action: str = "NONE",
        parameters: Dict[str, Any] = None
    ) -> Waypoint:
        """
        Fügt einen Wegpunkt zur Route hinzu.

        Args:
            route_id: ID der Route
            waypoint_type: Typ des Wegpunkts
            position: Position des Wegpunkts
            action: Aktion am Wegpunkt
            parameters: Zusätzliche Parameter

        Returns:
            Der erstellte Wegpunkt
        """

    def update_waypoint(
        self,
        waypoint_id: str,
        position: Dict[str, float] = None,
        action: str = None,
        parameters: Dict[str, Any] = None
    ):
        """
        Aktualisiert einen Wegpunkt.

        Args:
            waypoint_id: ID des Wegpunkts
            position: Neue Position
            action: Neue Aktion
            parameters: Neue Parameter
        """

    def delete_waypoint(self, waypoint_id: str):
        """
        Löscht einen Wegpunkt.

        Args:
            waypoint_id: ID des zu löschenden Wegpunkts
        """

    def start_mission(self):
        """Startet die aktuelle Mission."""

    def pause_mission(self):
        """Pausiert die aktuelle Mission."""

    def resume_mission(self):
        """Setzt die aktuelle Mission fort."""

    def complete_mission(self):
        """Schließt die aktuelle Mission ab."""

    def abort_mission(self):
        """Bricht die aktuelle Mission ab."""

    def next_waypoint(self):
        """Geht zum nächsten Wegpunkt."""

    @property
    def mission(self) -> Mission:
        """Gibt die aktuelle Mission zurück."""

    @property
    def current_route(self) -> Route:
        """Gibt die aktuelle Route zurück."""

    @property
    def current_waypoint(self) -> Waypoint:
        """Gibt den aktuellen Wegpunkt zurück."""

    @property
    def log(self) -> MissionLog:
        """Gibt das aktuelle Log zurück."""
```

## ViewModel

### FlightPlanningViewModel

```python
class FlightPlanningViewModel(QObject):
    def set_service(self, service: FlightPlanningService):
        """
        Setzt den Service.

        Args:
            service: Der zu setzende Service
        """

    def create_mission(self, name: str, parameters: Dict[str, Any] = None):
        """
        Erstellt eine neue Mission.

        Args:
            name: Name der Mission
            parameters: Zusätzliche Parameter
        """

    def add_route(self, name: str, parameters: Dict[str, Any] = None):
        """
        Fügt eine Route zur Mission hinzu.

        Args:
            name: Name der Route
            parameters: Zusätzliche Parameter
        """

    def add_waypoint(
        self,
        route_id: str,
        waypoint_type: str,
        position: Dict[str, float],
        action: str = "NONE",
        parameters: Dict[str, Any] = None
    ):
        """
        Fügt einen Wegpunkt zur Route hinzu.

        Args:
            route_id: ID der Route
            waypoint_type: Typ des Wegpunkts
            position: Position des Wegpunkts
            action: Aktion am Wegpunkt
            parameters: Zusätzliche Parameter
        """

    def update_waypoint(
        self,
        waypoint_id: str,
        position: Dict[str, float] = None,
        action: str = None,
        parameters: Dict[str, Any] = None
    ):
        """
        Aktualisiert einen Wegpunkt.

        Args:
            waypoint_id: ID des Wegpunkts
            position: Neue Position
            action: Neue Aktion
            parameters: Neue Parameter
        """

    def delete_waypoint(self, waypoint_id: str):
        """
        Löscht einen Wegpunkt.

        Args:
            waypoint_id: ID des zu löschenden Wegpunkts
        """

    def start_mission(self):
        """Startet die Mission."""

    def pause_mission(self):
        """Pausiert die Mission."""

    def resume_mission(self):
        """Setzt die Mission fort."""

    def complete_mission(self):
        """Schließt die Mission ab."""

    def abort_mission(self):
        """Bricht die Mission ab."""

    def next_waypoint(self):
        """Geht zum nächsten Wegpunkt."""

    # Properties
    has_mission: bool
    mission_id: str
    mission_name: str
    mission_status: str
    is_mission_active: bool
    is_mission_paused: bool
    is_mission_completed: bool
    is_mission_error: bool
    has_route: bool
    route_id: str
    route_name: str
    has_waypoint: bool
    waypoint_id: str
    waypoint_type: str
    waypoint_action: str
    waypoint_position: List[float]
    log_events: List[str]
    last_event: str
```

## Fehler

### FlightPlanningError

```python
class FlightPlanningError(Exception):
    """Basis-Fehlerklasse für Flugplanung."""
```

### FlightPlanningValidationError

```python
class FlightPlanningValidationError(FlightPlanningError):
    """Fehler bei der Validierung."""
```

### FlightPlanningCommandError

```python
class FlightPlanningCommandError(FlightPlanningError):
    """Fehler bei der Ausführung eines Befehls."""
```

### FlightPlanningMissionError

```python
class FlightPlanningMissionError(FlightPlanningError):
    """Fehler bei der Ausführung einer Mission."""
``` 