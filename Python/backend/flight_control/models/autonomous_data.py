"""
Datenmodelle für autonome Flugmodi.

Dieses Modul definiert die Datenmodelle für die verschiedenen autonomen Flugmodi,
einschließlich Position Hold, Return to Launch und Follow Me.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime

class AutonomousMode(Enum):
    """Enum für die verschiedenen autonomen Flugmodi."""
    POSITION_HOLD = "position_hold"
    RETURN_TO_LAUNCH = "return_to_launch"
    FOLLOW_ME = "follow_me"
    WAYPOINT = "waypoint"

class AutonomousStatus(Enum):
    """Enum für den Status der autonomen Flugmodi."""
    INACTIVE = "inactive"
    ACTIVE = "active"
    ERROR = "error"
    COMPLETED = "completed"

@dataclass
class PositionHoldParameters:
    """Parameter für den Position Hold Modus."""
    target_altitude: float
    target_heading: float
    position_tolerance: float
    heading_tolerance: float
    max_speed: float
    wind_compensation: bool

@dataclass
class ReturnToLaunchParameters:
    """Parameter für den Return to Launch Modus."""
    return_altitude: float
    approach_altitude: float
    approach_speed: float
    landing_speed: float
    max_speed: float
    abort_altitude: float

@dataclass
class FollowMeParameters:
    """Parameter für den Follow Me Modus."""
    target_distance: float
    target_altitude: float
    max_speed: float
    min_distance: float
    max_distance: float
    altitude_offset: float

@dataclass
class WaypointParameters:
    """Parameter für den Waypoint Modus."""
    waypoint_radius: float
    waypoint_speed: float
    waypoint_altitude: float
    waypoint_heading: float
    waypoint_loiter_time: float
    waypoint_loiter_radius: float

@dataclass
class AutonomousState:
    """Zustand der autonomen Flugmodi."""
    mode: AutonomousMode
    status: AutonomousStatus
    is_active: bool
    is_error: bool
    error_message: Optional[str]
    parameters: Dict[str, Any]
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    current_position: Dict[str, float]
    target_position: Dict[str, float]
    current_heading: float
    target_heading: float
    current_speed: float
    target_speed: float
    current_altitude: float
    target_altitude: float
    progress: float
    remaining_time: Optional[float]
    remaining_distance: Optional[float]

@dataclass
class AutonomousStatistics:
    """Statistiken für autonome Flugmodi."""
    total_flight_time: float
    total_distance: float
    average_speed: float
    max_speed: float
    min_speed: float
    average_altitude: float
    max_altitude: float
    min_altitude: float
    mode_changes: int
    error_count: int
    success_rate: float
    battery_usage: float
    wind_compensation_time: float
    position_hold_time: float
    return_to_launch_time: float
    follow_me_time: float
    waypoint_time: float

@dataclass
class AutonomousEvent:
    """Ereignis in einem autonomen Flugmodus."""
    timestamp: datetime
    event_type: str
    event_data: Dict[str, Any]
    mode: AutonomousMode
    status: AutonomousStatus
    position: Dict[str, float]
    heading: float
    speed: float
    altitude: float
    error_message: Optional[str]

@dataclass
class AutonomousLog:
    """Log für autonome Flugmodi."""
    events: List[AutonomousEvent]
    statistics: AutonomousStatistics
    start_time: datetime
    end_time: Optional[datetime]
    mode: AutonomousMode
    status: AutonomousStatus
    error_count: int
    warning_count: int
    info_count: int
    debug_count: int

class AutonomousError(Exception):
    """Basisklasse für Fehler in autonomen Flugmodi."""
    pass

class ModeActivationError(AutonomousError):
    """Fehler bei der Aktivierung eines Flugmodus."""
    pass

class ParameterError(AutonomousError):
    """Fehler bei den Parametern."""
    pass

class PositionError(AutonomousError):
    """Fehler bei der Positionsbestimmung."""
    pass

class HeadingError(AutonomousError):
    """Fehler bei der Kursbestimmung."""
    pass

class SpeedError(AutonomousError):
    """Fehler bei der Geschwindigkeitsbestimmung."""
    pass

class AltitudeError(AutonomousError):
    """Fehler bei der Höhenbestimmung."""
    pass 