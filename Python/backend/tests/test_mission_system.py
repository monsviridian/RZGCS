"""Systemtests für die Missionsplanung."""

import unittest
import time
from datetime import datetime
from PySide6.QtCore import QObject, Signal, Slot, QTimer, QCoreApplication
from PySide6.QtQml import QQmlApplicationEngine
from flight_control.models.mission_data import (
    MissionType,
    MissionStatus,
    MissionState,
    MissionStatistics,
    MissionEvent,
    MissionLog,
    MissionError,
    MissionValidationError,
    MissionExecutionError,
    MissionParameterError
)
from flight_control.services.mission_service import MissionService
from flight_control.viewmodels.mission_viewmodel import MissionViewModel

class TestMissionSystem(unittest.TestCase):
    """Testfälle für das Missionssystem."""
    
    @classmethod
    def setUpClass(cls):
        """Testumgebung vorbereiten."""
        cls.app = QCoreApplication([])
        cls.engine = QQmlApplicationEngine()
    
    def setUp(self):
        """Testumgebung vorbereiten."""
        self.service = MissionService()
        self.viewmodel = MissionViewModel(self.service)
    
    def test_end_to_end_scenario(self):
        """Test eines End-to-End-Szenarios."""
        # 1. Mission konfigurieren
        waypoints = [
            {
                "id": 1,
                "type": "waypoint",
                "position": {"lat": 48.123, "lon": 11.456, "alt": 100.0},
                "heading": 90.0,
                "speed": 10.0,
                "altitude": 100.0,
                "actions": ["take_photo", "start_recording"]
            },
            {
                "id": 2,
                "type": "waypoint",
                "position": {"lat": 48.124, "lon": 11.457, "alt": 150.0},
                "heading": 180.0,
                "speed": 15.0,
                "altitude": 150.0,
                "actions": ["stop_recording"]
            }
        ]
        
        parameters = {
            "altitude_mode": "relative",
            "speed_mode": "auto",
            "heading_mode": "auto",
            "return_on_completion": True,
            "return_on_failure": True,
            "return_altitude": 50.0,
            "max_speed": 20.0,
            "max_altitude": 200.0,
            "min_altitude": 10.0,
            "max_distance": 1000.0,
            "max_flight_time": 3600.0,
            "battery_threshold": 20.0
        }
        
        # 2. Mission starten
        self.service.set_waypoints(waypoints)
        self.service.set_parameters(parameters)
        self.service.activate()
        
        # 3. Flug simulieren
        for i in range(len(waypoints)):
            # Position aktualisieren
            position = waypoints[i]["position"]
            self.service.update_position(position)
            
            # Kurs aktualisieren
            heading = waypoints[i]["heading"]
            self.service.update_heading(heading)
            
            # Geschwindigkeit aktualisieren
            speed = waypoints[i]["speed"]
            self.service.update_speed(speed)
            
            # Höhe aktualisieren
            altitude = waypoints[i]["altitude"]
            self.service.update_altitude(altitude)
            
            # Kurze Pause für Simulation
            time.sleep(0.1)
        
        # 4. Mission beenden
        self.service.deactivate()
        
        # 5. Ergebnisse überprüfen
        self.assertFalse(self.service._state.is_active)
        self.assertFalse(self.service._state.is_error)
        self.assertIsNone(self.service._state.error_message)
        self.assertEqual(self.service._state.status, MissionStatus.COMPLETED)
        self.assertEqual(self.service._state.current_waypoint, len(waypoints))
        self.assertEqual(self.service._state.total_waypoints, len(waypoints))
        self.assertEqual(self.service._state.progress, 100.0)
        self.assertIsNotNone(self.service._state.start_time)
        self.assertIsNotNone(self.service._state.end_time)
        self.assertGreater(self.service._statistics.total_flight_time, 0.0)
        self.assertGreater(self.service._statistics.total_distance, 0.0)
        self.assertGreater(self.service._statistics.average_speed, 0.0)
        self.assertEqual(self.service._statistics.waypoints_completed, len(waypoints))
        self.assertEqual(self.service._statistics.waypoints_failed, 0)
    
    def test_error_scenarios(self):
        """Test von Fehlerszenarien."""
        # 1. Aktivierung im Fehlerzustand
        self.service._state.is_error = True
        self.service._state.error_message = "Test error"
        self.service.activate()
        self.assertTrue(self.service._state.is_error)
        self.assertEqual(self.service._state.error_message, "Test error")
        
        # 2. Ungültige Wegpunkte
        invalid_waypoints = [{"id": 1}]  # Fehlende erforderliche Felder
        self.service.set_waypoints(invalid_waypoints)
        self.assertTrue(self.service._state.is_error)
        self.assertIsNotNone(self.service._state.error_message)
        
        # 3. Ungültige Parameter
        invalid_parameters = {"invalid": "parameter"}
        self.service.set_parameters(invalid_parameters)
        self.assertTrue(self.service._state.is_error)
        self.assertIsNotNone(self.service._state.error_message)
        
        # 4. Aktivierung ohne Wegpunkte
        self.service._state.is_error = False
        self.service._state.error_message = None
        self.service.activate()
        self.assertTrue(self.service._state.is_error)
        self.assertIsNotNone(self.service._state.error_message)
    
    def test_performance(self):
        """Test der Performance."""
        # 1. Wegpunkte erstellen
        waypoints = []
        for i in range(100):
            waypoints.append({
                "id": i + 1,
                "type": "waypoint",
                "position": {"lat": 48.123 + i * 0.001, "lon": 11.456 + i * 0.001, "alt": 100.0 + i * 1.0},
                "heading": i * 3.6,
                "speed": 10.0 + i * 0.1,
                "altitude": 100.0 + i * 1.0,
                "actions": []
            })
        
        # 2. Performance messen
        start_time = time.time()
        
        # Wegpunkte setzen
        self.service.set_waypoints(waypoints)
        
        # Mission starten
        self.service.activate()
        
        # Flug simulieren
        for waypoint in waypoints:
            self.service.update_position(waypoint["position"])
            self.service.update_heading(waypoint["heading"])
            self.service.update_speed(waypoint["speed"])
            self.service.update_altitude(waypoint["altitude"])
        
        # Mission beenden
        self.service.deactivate()
        
        end_time = time.time()
        
        # 3. Ergebnisse überprüfen
        total_time = end_time - start_time
        self.assertLess(total_time, 1.0)  # Sollte weniger als 1 Sekunde dauern
        self.assertEqual(self.service._state.current_waypoint, len(waypoints))
        self.assertEqual(self.service._state.total_waypoints, len(waypoints))
        self.assertEqual(self.service._state.progress, 100.0)
    
    def test_concurrent_operations(self):
        """Test von gleichzeitigen Operationen."""
        # 1. Mission konfigurieren
        waypoints = [
            {
                "id": 1,
                "type": "waypoint",
                "position": {"lat": 48.123, "lon": 11.456, "alt": 100.0},
                "heading": 90.0,
                "speed": 10.0,
                "altitude": 100.0,
                "actions": []
            },
            {
                "id": 2,
                "type": "waypoint",
                "position": {"lat": 48.124, "lon": 11.457, "alt": 150.0},
                "heading": 180.0,
                "speed": 15.0,
                "altitude": 150.0,
                "actions": []
            }
        ]
        
        # 2. Mission starten
        self.service.set_waypoints(waypoints)
        self.service.activate()
        
        # 3. Gleichzeitige Operationen
        for _ in range(100):
            # Position aktualisieren
            self.service.update_position({"lat": 48.123, "lon": 11.456, "alt": 100.0})
            
            # Kurs aktualisieren
            self.service.update_heading(90.0)
            
            # Geschwindigkeit aktualisieren
            self.service.update_speed(10.0)
            
            # Höhe aktualisieren
            self.service.update_altitude(100.0)
        
        # 4. Mission beenden
        self.service.deactivate()
        
        # 5. Ergebnisse überprüfen
        self.assertFalse(self.service._state.is_error)
        self.assertIsNone(self.service._state.error_message)
        self.assertEqual(self.service._state.status, MissionStatus.COMPLETED)
    
    def test_recovery_scenarios(self):
        """Test von Wiederherstellungsszenarien."""
        # 1. Mission konfigurieren
        waypoints = [
            {
                "id": 1,
                "type": "waypoint",
                "position": {"lat": 48.123, "lon": 11.456, "alt": 100.0},
                "heading": 90.0,
                "speed": 10.0,
                "altitude": 100.0,
                "actions": []
            },
            {
                "id": 2,
                "type": "waypoint",
                "position": {"lat": 48.124, "lon": 11.457, "alt": 150.0},
                "heading": 180.0,
                "speed": 15.0,
                "altitude": 150.0,
                "actions": []
            }
        ]
        
        # 2. Mission starten
        self.service.set_waypoints(waypoints)
        self.service.activate()
        
        # 3. Fehler simulieren
        self.service._state.is_error = True
        self.service._state.error_message = "Test error"
        
        # 4. Wiederherstellung
        self.service._state.is_error = False
        self.service._state.error_message = None
        
        # 5. Mission fortsetzen
        self.service.update_position(waypoints[0]["position"])
        self.service.update_heading(waypoints[0]["heading"])
        self.service.update_speed(waypoints[0]["speed"])
        self.service.update_altitude(waypoints[0]["altitude"])
        
        # 6. Mission beenden
        self.service.deactivate()
        
        # 7. Ergebnisse überprüfen
        self.assertFalse(self.service._state.is_error)
        self.assertIsNone(self.service._state.error_message)
        self.assertEqual(self.service._state.status, MissionStatus.COMPLETED)

if __name__ == "__main__":
    unittest.main() 