"""
DroneKit Utilities - Hilfsfunktionen für DroneKit-Integration
"""

import math
import time
from typing import Tuple, Dict, Any, Optional
from enum import Enum

class FlightMode(Enum):
    """ArduPilot Flight Modes"""
    STABILIZED = 0
    ACRO = 1
    ALT_HOLD = 2
    AUTO = 3
    GUIDED = 4
    LOITER = 5
    RTL = 6
    CIRCLE = 7
    LAND = 8
    OF_LOITER = 9
    DRIFT = 10
    SPORT = 11
    FLIP = 13
    AUTOTUNE = 14
    POSHOLD = 15
    BRAKE = 16
    THROW = 17
    AVOID_ADSB = 18
    GUIDED_NOGPS = 19
    SMART_RTL = 20
    FLOWHOLD = 21
    FOLLOW = 22
    ZIGZAG = 23
    SYSTEMID = 24
    AUTOROTATE = 25
    AUTO_RTL = 26

class DroneKitUtils:
    """Utility-Klasse für DroneKit-Operationen"""
    
    @staticmethod
    def decode_flight_mode(custom_mode: int) -> str:
        """Decodiert custom_mode zu Flight-Mode-String"""
        try:
            return FlightMode(custom_mode).name
        except ValueError:
            return "UNKNOWN"
    
    @staticmethod
    def encode_flight_mode(mode_name: str) -> int:
        """Encodiert Flight-Mode-String zu custom_mode"""
        try:
            return FlightMode[mode_name.upper()].value
        except KeyError:
            return 0
    
    @staticmethod
    def validate_connection_string(connection_string: str) -> str:
        """Validiert und normalisiert Verbindungsstring"""
        if not connection_string:
            raise ValueError("Empty connection string")
        
        # COM-Port Format NICHT mehr verändern!
        # Unterstützte Formate prüfen
        valid_prefixes = ["udp://", "tcp://", "/dev/", "COM"]
        
        # Zusätzlich: TCP/UDP ohne Protokoll-Präfix erkennen
        if connection_string.startswith("tcp:") or connection_string.startswith("udp:"):
            # Entferne das Protokoll-Präfix für DroneKit
            if connection_string.startswith("tcp:"):
                return connection_string[4:]  # Entferne "tcp:"
            elif connection_string.startswith("udp:"):
                return connection_string[4:]  # Entferne "udp:"
        
        if not any(connection_string.startswith(prefix) for prefix in valid_prefixes):
            raise ValueError(f"Invalid connection string format: {connection_string}")
        
        return connection_string
    
    @staticmethod
    def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Berechnet Distanz zwischen zwei GPS-Koordinaten in Metern"""
        R = 6371000  # Erdradius in Metern
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat / 2) * math.sin(delta_lat / 2) +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lon / 2) * math.sin(delta_lon / 2))
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    @staticmethod
    def calculate_bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Berechnet Bearing zwischen zwei GPS-Koordinaten in Grad"""
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lon = math.radians(lon2 - lon1)
        
        y = math.sin(delta_lon) * math.cos(lat2_rad)
        x = (math.cos(lat1_rad) * math.sin(lat2_rad) -
             math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(delta_lon))
        
        bearing = math.degrees(math.atan2(y, x))
        return (bearing + 360) % 360
    
    @staticmethod
    def format_coordinate(lat: float, lon: float, precision: int = 6) -> str:
        """Formatiert GPS-Koordinaten für Anzeige"""
        lat_str = f"{lat:.{precision}f}"
        lon_str = f"{lon:.{precision}f}"
        return f"{lat_str}, {lon_str}"
    
    @staticmethod
    def format_altitude(altitude: float) -> str:
        """Formatiert Höhe für Anzeige"""
        if altitude >= 1000:
            return f"{altitude/1000:.1f} km"
        else:
            return f"{altitude:.1f} m"
    
    @staticmethod
    def format_speed(speed: float) -> str:
        """Formatiert Geschwindigkeit für Anzeige"""
        if speed >= 1:
            return f"{speed:.1f} m/s"
        else:
            return f"{speed*100:.0f} cm/s"
    
    @staticmethod
    def format_battery(battery_percent: float) -> str:
        """Formatiert Batterie-Level für Anzeige"""
        return f"{battery_percent:.0f}%"
    
    @staticmethod
    def is_connection_alive(last_heartbeat: float, timeout: float = 5.0) -> bool:
        """Prüft ob Verbindung noch aktiv ist basierend auf Heartbeat"""
        return (time.time() - last_heartbeat) < timeout
    
    @staticmethod
    def rate_limit(current_time: float, last_update: float, rate: float) -> bool:
        """Rate-Limiting für Updates"""
        return (current_time - last_update) >= (1.0 / rate)
    
    @staticmethod
    def create_waypoint(lat: float, lon: float, alt: float, 
                       command: int = 16,  # MAV_CMD_NAV_WAYPOINT
                       **kwargs) -> Dict[str, Any]:
        """Erstellt Waypoint-Dictionary"""
        waypoint = {
            'lat': lat,
            'lon': lon,
            'alt': alt,
            'command': command,
            'frame': 0,  # MAV_FRAME_GLOBAL
            'current': 0,
            'autocontinue': 1,
            'param1': kwargs.get('param1', 0),
            'param2': kwargs.get('param2', 0),
            'param3': kwargs.get('param3', 0),
            'param4': kwargs.get('param4', 0)
        }
        return waypoint
    
    @staticmethod
    def create_mission_from_waypoints(waypoints: list) -> list:
        """Erstellt Mission aus Waypoint-Liste"""
        mission = []
        for i, wp in enumerate(waypoints):
            mission_item = DroneKitUtils.create_waypoint(
                lat=wp['lat'],
                lon=wp['lon'],
                alt=wp['alt']
            )
            mission.append(mission_item)
        return mission 