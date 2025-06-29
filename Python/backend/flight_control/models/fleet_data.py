"""Flotten-Modelle.

Diese Module definieren die Datenmodelle für die Flottensteuerung.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum
from dataclasses import dataclass

class FleetStatus(Enum):
    """Flotten-Status."""
    INACTIVE = "inactive"
    ACTIVE = "active"
    ERROR = "error"

class FleetMode(Enum):
    """Flotten-Modus."""
    MANUAL = "manual"
    COORDINATED = "coordinated"
    AUTONOMOUS = "autonomous"

class UAVStatus(Enum):
    """UAV-Status."""
    INACTIVE = "inactive"
    ACTIVE = "active"
    ERROR = "error"

class UAVMode(Enum):
    """UAV-Modus."""
    MANUAL = "manual"
    AUTONOMOUS = "autonomous"

class NetworkTopology(Enum):
    """Netzwerk-Topologie."""
    STAR = "star"
    MESH = "mesh"
    TREE = "tree"

class EncryptionStatus(Enum):
    """Verschlüsselungs-Status."""
    DISABLED = "disabled"
    ENABLED = "enabled"

@dataclass
class PositionData:
    """Positionsdaten."""
    latitude: float
    longitude: float
    altitude: float

@dataclass
class VelocityData:
    """Geschwindigkeitsdaten."""
    vx: float
    vy: float
    vz: float

@dataclass
class AttitudeData:
    """Attitudedaten."""
    roll: float
    pitch: float
    yaw: float

@dataclass
class SensorData:
    """Sensordaten."""
    # Standard-Sensoren
    temperature: float = 0.0
    pressure: float = 0.0
    humidity: float = 0.0
    
    # Attitude-Daten
    roll: float = 0.0
    pitch: float = 0.0
    yaw: float = 0.0
    heading: float = 0.0
    
    # GPS-Daten
    gps_latitude: float = 0.0
    gps_longitude: float = 0.0
    gps_altitude: float = 0.0
    groundspeed: float = 0.0
    airspeed: float = 0.0
    vertical_speed: float = 0.0
    gps_satellites: float = 0
    
    # Batterie-Daten
    battery_voltage: float = 0.0
    battery_current: float = 0.0
    battery_remaining: float = 0.0
    battery_percentage: float = 0.0
    battery_temperature: float = 0.0
    
    # VFR HUD Daten
    throttle: float = 0.0
    
    # Erweiterte Sensordaten
    motor_temperature: float = 0.0
    esc_temperature: float = 0.0
    gps_signal_strength: float = 0.0
    gps_hdop: float = 0.0
    gps_vdop: float = 0.0
    gps_pdop: float = 0.0
    gps_fix_type: float = 0.0
    gps_fix_quality: float = 0.0
    gps_eph: float = 0.0
    gps_epv: float = 0.0
    gps_vel: float = 0.0
    gps_cog: float = 0.0
    gps_speed_accuracy: float = 0.0
    gps_horizontal_accuracy: float = 0.0
    gps_vertical_accuracy: float = 0.0
    gps_heading_accuracy: float = 0.0
    gps_yaw_accuracy: float = 0.0
    gps_altitude_accuracy: float = 0.0
    gps_speed_accuracy_estimate: float = 0.0
    gps_horizontal_accuracy_estimate: float = 0.0
    gps_vertical_accuracy_estimate: float = 0.0
    gps_heading_accuracy_estimate: float = 0.0
    gps_yaw_accuracy_estimate: float = 0.0
    gps_altitude_accuracy_estimate: float = 0.0

@dataclass
class ResourceData:
    """Ressourcendaten."""
    energy: float
    bandwidth: float
    load: float

@dataclass
class RoutingTable:
    """Routing-Tabelle."""
    routes: Dict[str, List[str]]

@dataclass
class BandwidthAllocation:
    """Bandbreiten-Allokation."""
    allocations: Dict[str, float]

@dataclass
class CommunicationData:
    """Kommunikationsdaten."""
    network_topology: NetworkTopology
    encryption_status: EncryptionStatus
    routing_table: RoutingTable
    bandwidth_allocation: BandwidthAllocation

@dataclass
class UAVData:
    """UAV-Daten."""
    uav_id: str
    uav_name: str
    uav_status: UAVStatus
    uav_mode: UAVMode
    position: PositionData
    velocity: VelocityData
    attitude: AttitudeData
    sensor_data: SensorData
    resources: ResourceData

@dataclass
class FleetData:
    """Flottendaten."""
    fleet_id: str
    fleet_name: str
    fleet_status: FleetStatus
    fleet_mode: FleetMode
    uavs: List[UAVData]
    resources: ResourceData
    communication: CommunicationData

class FleetError(Exception):
    """Basisklasse für Flotten-Fehler."""
    pass

class FleetValidationError(FleetError):
    """Validierungsfehler."""
    pass

class FleetCommandError(FleetError):
    """Befehlsfehler."""
    pass

class FleetStateError(FleetError):
    """Zustandsfehler."""
    pass 