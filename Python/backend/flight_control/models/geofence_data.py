"""
Datenmodelle für die Geofencing-Funktionalität.

Dieses Modul definiert die Datenmodelle für die verschiedenen Geofence-Typen,
Aktionen und Statistiken.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime

class GeofenceType(Enum):
    """Enum für die verschiedenen Geofence-Typen."""
    POLYGON = "polygon"
    CIRCLE = "circle"
    RECTANGLE = "rectangle"

class GeofenceAction(Enum):
    """Enum für die verschiedenen Aktionen bei Grenzüberschreitung."""
    WARN = "warn"
    RETURN = "return"
    LAND = "land"

class GeofenceStatus(Enum):
    """Enum für den Status der Geofence."""
    INACTIVE = "inactive"
    ACTIVE = "active"
    WARNING = "warning"
    ACTION = "action"
    ERROR = "error"

@dataclass
class GeofenceVertex:
    """Ein Vertex eines Geofence-Polygons."""
    lat: float
    lon: float
    alt: Optional[float] = None

@dataclass
class GeofenceParameters:
    """Basisklasse für Geofence-Parameter."""
    altitude_min: float
    altitude_max: float
    buffer_zone: float
    action: GeofenceAction

@dataclass
class PolygonGeofenceParameters(GeofenceParameters):
    """Parameter für einen Polygon-Geofence."""
    vertices: List[GeofenceVertex]

@dataclass
class CircleGeofenceParameters(GeofenceParameters):
    """Parameter für einen Kreis-Geofence."""
    center: GeofenceVertex
    radius: float

@dataclass
class RectangleGeofenceParameters(GeofenceParameters):
    """Parameter für einen Rechteck-Geofence."""
    north_west: GeofenceVertex
    south_east: GeofenceVertex

@dataclass
class WarnActionParameters:
    """Parameter für die WARN-Aktion."""
    warning_distance: float
    warning_altitude: float
    warning_interval: float
    warning_message: str

@dataclass
class ReturnActionParameters:
    """Parameter für die RETURN-Aktion."""
    return_altitude: float
    return_speed: float
    return_heading: float
    return_timeout: float

@dataclass
class LandActionParameters:
    """Parameter für die LAND-Aktion."""
    landing_speed: float
    landing_altitude: float
    landing_timeout: float
    emergency_landing: bool

@dataclass
class GeofenceState:
    """Zustand der Geofence."""
    type: GeofenceType
    status: GeofenceStatus
    is_active: bool
    is_error: bool
    error_message: Optional[str]
    parameters: Dict[str, Any]
    action_parameters: Dict[str, Any]
    current_position: Dict[str, float]
    distance_to_boundary: float
    altitude_violation: bool
    boundary_violation: bool
    last_warning_time: Optional[datetime]
    last_action_time: Optional[datetime]
    action_in_progress: bool
    action_timeout: bool

@dataclass
class GeofenceStatistics:
    """Statistiken für die Geofence."""
    total_violations: int
    altitude_violations: int
    boundary_violations: int
    warnings_issued: int
    actions_triggered: int
    timeouts_occurred: int
    total_flight_time: float
    time_inside: float
    time_outside: float
    min_distance_to_boundary: float
    max_distance_to_boundary: float
    average_distance_to_boundary: float
    min_altitude_violation: float
    max_altitude_violation: float
    average_altitude_violation: float

@dataclass
class GeofenceEvent:
    """Ereignis in der Geofence."""
    timestamp: datetime
    event_type: str
    event_data: Dict[str, Any]
    type: GeofenceType
    status: GeofenceStatus
    position: Dict[str, float]
    distance_to_boundary: float
    altitude_violation: bool
    boundary_violation: bool
    action_in_progress: bool
    error_message: Optional[str]

@dataclass
class GeofenceLog:
    """Log für die Geofence."""
    events: List[GeofenceEvent]
    statistics: GeofenceStatistics
    start_time: datetime
    end_time: Optional[datetime]
    type: GeofenceType
    status: GeofenceStatus
    error_count: int
    warning_count: int
    action_count: int
    timeout_count: int

class GeofenceError(Exception):
    """Basisklasse für Fehler in der Geofence."""
    pass

class GeofenceConfigError(GeofenceError):
    """Fehler bei der Konfiguration der Geofence."""
    pass

class GeofenceValidationError(GeofenceError):
    """Fehler bei der Validierung der Geofence."""
    pass

class GeofenceActionError(GeofenceError):
    """Fehler bei der Ausführung einer Aktion."""
    pass

class GeofenceTimeoutError(GeofenceError):
    """Fehler bei einem Timeout."""
    pass 