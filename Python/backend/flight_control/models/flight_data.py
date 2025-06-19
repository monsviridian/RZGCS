"""
Datenmodelle für die Flugsteuerung.
Definiert die Datenstrukturen für die Flugsteuerung.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from datetime import datetime

from ..enums import FlightStatus, FlightMode, WaypointType, MissionStatus

@dataclass
class Position:
    """Position im 3D-Raum"""
    x: float  # X-Koordinate
    y: float  # Y-Koordinate
    z: float  # Z-Koordinate
    
    def distance_to(self, other: 'Position') -> float:
        """
        Berechnet die Distanz zu einer anderen Position.
        
        Args:
            other: Andere Position
            
        Returns:
            Distanz in Metern
        """
        return ((self.x - other.x) ** 2 + 
                (self.y - other.y) ** 2 + 
                (self.z - other.z) ** 2) ** 0.5
                
@dataclass
class Waypoint:
    """Wegpunkt"""
    id: int                    # Eindeutige ID
    type: WaypointType        # Typ des Wegpunkts
    position: Position        # Position
    parameters: Dict[str, Any] # Parameter
    
@dataclass
class Mission:
    """Mission"""
    id: int                    # Eindeutige ID
    name: str                  # Name
    waypoints: List[Waypoint]  # Wegpunkte
    status: MissionStatus      # Status
    
@dataclass
class FlightState:
    """Flugzustand"""
    position: Position                # Aktuelle Position
    mode: FlightMode                 # Aktueller Flugmodus
    armed: bool                      # Scharf/Entscharft
    status: FlightStatus             # Aktueller Status
    parameters: Dict[str, Any]       # Parameter
    velocity: Position = None        # Aktuelle Geschwindigkeit
    acceleration: Position = None    # Aktuelle Beschleunigung
    attitude: Position = None        # Aktuelle Attitude
    angular_velocity: Position = None # Aktuelle Winkelgeschwindigkeit
    battery_level: float = 0.0       # Batteriestand
    signal_strength: float = 0.0     # Signalstärke
    gps_fix: bool = False           # GPS-Fix
    gps_satellites: int = 0         # Anzahl GPS-Satelliten
    gps_hdop: float = 0.0           # GPS HDOP
    gps_altitude: float = 0.0       # GPS-Höhe
    gps_ground_speed: float = 0.0   # GPS-Bodengeschwindigkeit
    gps_ground_course: float = 0.0  # GPS-Bodenkurs
    gps_vertical_speed: float = 0.0 # GPS-Vertikalgeschwindigkeit
    gps_eph: float = 0.0           # GPS EPH
    gps_epv: float = 0.0           # GPS EPV
    gps_velocity: Position = None   # GPS-Geschwindigkeit
    gps_position: Position = None   # GPS-Position
    gps_home: Position = None       # GPS-Heimposition
    gps_origin: Position = None     # GPS-Ursprungsposition
    gps_waypoint: Position = None   # GPS-Wegpunkt
    gps_target: Position = None     # GPS-Zielposition
    gps_obstacle: Position = None   # GPS-Hindernisposition
    gps_geofence: Position = None   # GPS-Geofence-Position
    gps_landing: Position = None    # GPS-Landeposition
    gps_takeoff: Position = None    # GPS-Startposition
    gps_mission: Position = None    # GPS-Missionsposition
    gps_emergency: Position = None  # GPS-Notfallposition
    gps_collision: Position = None  # GPS-Kollisionsposition
    gps_flight: Position = None     # GPS-Flugposition
    gps_control: Position = None    # GPS-Steuerungsposition
    gps_safety: Position = None     # GPS-Sicherheitsposition
    
    def __post_init__(self):
        """Nach der Initialisierung"""
        if self.velocity is None:
            self.velocity = Position(x=0.0, y=0.0, z=0.0)
        if self.acceleration is None:
            self.acceleration = Position(x=0.0, y=0.0, z=0.0)
        if self.attitude is None:
            self.attitude = Position(x=0.0, y=0.0, z=0.0)
        if self.angular_velocity is None:
            self.angular_velocity = Position(x=0.0, y=0.0, z=0.0)
        if self.gps_velocity is None:
            self.gps_velocity = Position(x=0.0, y=0.0, z=0.0)
        if self.gps_position is None:
            self.gps_position = Position(x=0.0, y=0.0, z=0.0)
        if self.gps_home is None:
            self.gps_home = Position(x=0.0, y=0.0, z=0.0)
        if self.gps_origin is None:
            self.gps_origin = Position(x=0.0, y=0.0, z=0.0)
        if self.gps_waypoint is None:
            self.gps_waypoint = Position(x=0.0, y=0.0, z=0.0)
        if self.gps_target is None:
            self.gps_target = Position(x=0.0, y=0.0, z=0.0)
        if self.gps_obstacle is None:
            self.gps_obstacle = Position(x=0.0, y=0.0, z=0.0)
        if self.gps_geofence is None:
            self.gps_geofence = Position(x=0.0, y=0.0, z=0.0)
        if self.gps_landing is None:
            self.gps_landing = Position(x=0.0, y=0.0, z=0.0)
        if self.gps_takeoff is None:
            self.gps_takeoff = Position(x=0.0, y=0.0, z=0.0)
        if self.gps_mission is None:
            self.gps_mission = Position(x=0.0, y=0.0, z=0.0)
        if self.gps_emergency is None:
            self.gps_emergency = Position(x=0.0, y=0.0, z=0.0)
        if self.gps_collision is None:
            self.gps_collision = Position(x=0.0, y=0.0, z=0.0)
        if self.gps_flight is None:
            self.gps_flight = Position(x=0.0, y=0.0, z=0.0)
        if self.gps_control is None:
            self.gps_control = Position(x=0.0, y=0.0, z=0.0)
        if self.gps_safety is None:
            self.gps_safety = Position(x=0.0, y=0.0, z=0.0)
    
@dataclass
class ControlCommand:
    """Steuerungsbefehl"""
    type: str                        # Befehlstyp
    parameters: Dict[str, Any]       # Parameter
    
@dataclass
class MissionPlan:
    """Flugplan"""
    mission: Mission                 # Mission
    estimated_duration: float        # Geschätzte Dauer in Sekunden
    estimated_distance: float        # Geschätzte Distanz in Metern
    estimated_energy: float          # Geschätzter Energieverbrauch in Wattstunden
    waypoint_sequence: List[int]     # Sequenz der Wegpunkte 