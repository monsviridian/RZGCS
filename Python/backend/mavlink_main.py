"""
MAVLink Main für die Flugsteuerung.
"""

import sys
import os
from pathlib import Path

# Füge das backend-Verzeichnis zum Python-Pfad hinzu
backend_dir = Path(__file__).parent
sys.path.append(str(backend_dir))

from flight_control.telemetry.telemetry_manager import TelemetryManager
from flight_control.connection.connection_manager import ConnectionManager
from flight_control.services.telemetry_service import TelemetryService
from flight_control.services.control_service import ControlService
from flight_control.services.safety_service import SafetyService
from flight_control.services.geofence_service import GeofenceService
from flight_control.services.mission_service import MissionService
from flight_control.services.emergency_service import EmergencyService
from flight_control.services.connection_service import ConnectionService
from flight_control.services.collision_service import CollisionService
from flight_control.services.flight_control_service import FlightControlService
from flight_control.models.flight_data import FlightState, Position

class MavlinkMain:
    """MAVLink Main Klasse."""
    
    def __init__(self):
        """Initialisiert die MAVLink Main Klasse."""
        # Manager initialisieren
        self.telemetry_manager = TelemetryManager()
        self.connection_manager = ConnectionManager()
        
        # Initialisiere die Services
        self.telemetry_service = TelemetryService(self.telemetry_manager, self.connection_manager)
        self.geofence_service = GeofenceService(self.telemetry_manager)
        self.obstacle_service = ObstacleService(self.telemetry_manager)
        self.landing_service = LandingService(self.telemetry_manager)
        self.takeoff_service = TakeoffService(self.telemetry_manager)
        self.mission_service = MissionService(self.telemetry_manager)
        self.emergency_service = EmergencyService(self.telemetry_manager)
        self.collision_service = CollisionService(self.telemetry_manager)
        self.flight_service = FlightService(self.telemetry_manager)
        self.control_service = ControlService(self.telemetry_manager)
        self.safety_service = SafetyService(self.telemetry_manager)
        
        # Initialisiere die Position-Objekte mit Standardwerten
        self._state.position = Position(x=0.0, y=0.0, z=0.0)
        self._state.velocity = Position(x=0.0, y=0.0, z=0.0)
        self._state.acceleration = Position(x=0.0, y=0.0, z=0.0)
        self._state.attitude = Position(x=0.0, y=0.0, z=0.0)
        self._state.angular_velocity = Position(x=0.0, y=0.0, z=0.0)
        self._state.gps_velocity = Position(x=0.0, y=0.0, z=0.0)
        self._state.gps_position = Position(x=0.0, y=0.0, z=0.0)
        self._state.gps_home = Position(x=0.0, y=0.0, z=0.0)
        self._state.gps_origin = Position(x=0.0, y=0.0, z=0.0)
        self._state.gps_waypoint = Position(x=0.0, y=0.0, z=0.0)
        self._state.gps_target = Position(x=0.0, y=0.0, z=0.0)
        self._state.gps_obstacle = Position(x=0.0, y=0.0, z=0.0)
        self._state.gps_geofence = Position(x=0.0, y=0.0, z=0.0)
        self._state.gps_landing = Position(x=0.0, y=0.0, z=0.0)
        self._state.gps_takeoff = Position(x=0.0, y=0.0, z=0.0)
        self._state.gps_mission = Position(x=0.0, y=0.0, z=0.0)
        self._state.gps_emergency = Position(x=0.0, y=0.0, z=0.0)
        self._state.gps_collision = Position(x=0.0, y=0.0, z=0.0)
        self._state.gps_flight = Position(x=0.0, y=0.0, z=0.0)
        self._state.gps_control = Position(x=0.0, y=0.0, z=0.0)
        self._state.gps_safety = Position(x=0.0, y=0.0, z=0.0)
        
    def start(self):
        """Startet die MAVLink Main Klasse."""
        # Services starten
        self.telemetry_service.start()
        self.control_service.start()
        self.safety_service.start()
        self.geofence_service.start()
        self.mission_service.start()
        self.emergency_service.start()
        self.connection_service.start()
        self.collision_service.start()
        self.flight_control_service.start()
        
    def stop(self):
        """Stoppt die MAVLink Main Klasse."""
        # Services stoppen
        self.telemetry_service.stop()
        self.control_service.stop()
        self.safety_service.stop()
        self.geofence_service.stop()
        self.mission_service.stop()
        self.emergency_service.stop()
        self.connection_service.stop()
        self.collision_service.stop()
        self.flight_control_service.stop()

def main():
    """Hauptfunktion."""
    # MAVLink Main initialisieren
    mavlink = MavlinkMain()
    
    try:
        # MAVLink Main starten
        mavlink.start()
        
        # Warten auf Benutzer-Eingabe
        input("Drücke Enter zum Beenden...")
        
    except KeyboardInterrupt:
        print("\nBeende...")
        
    finally:
        # MAVLink Main stoppen
        mavlink.stop()

if __name__ == "__main__":
    main() 