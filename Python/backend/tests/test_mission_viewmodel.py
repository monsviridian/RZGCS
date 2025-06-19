"""Unit Tests für das Missions-ViewModel."""

import unittest
from datetime import datetime
from PySide6.QtCore import QObject, Signal, Slot, QTimer
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
from flight_control.viewmodels.mission_viewmodel import MissionViewModel
from flight_control.services.mission_service import MissionService

class TestMissionViewModel(unittest.TestCase):
    """Testfälle für das Missions-ViewModel."""
    
    def setUp(self):
        """Testumgebung vorbereiten."""
        self.service = MissionService()
        self.viewmodel = MissionViewModel(self.service)
    
    def test_initial_state(self):
        """Test des initialen Zustands."""
        self.assertFalse(self.viewmodel.is_active)
        self.assertFalse(self.viewmodel.is_error)
        self.assertEqual(self.viewmodel.error_message, "")
        self.assertEqual(self.viewmodel.type, MissionType.WAYPOINT.value)
        self.assertEqual(self.viewmodel.status, MissionStatus.IDLE.value)
        self.assertEqual(self.viewmodel.current_waypoint, 0)
        self.assertEqual(self.viewmodel.total_waypoints, 0)
        self.assertEqual(self.viewmodel.progress, 0.0)
        self.assertEqual(self.viewmodel.remaining_time, 0.0)
        self.assertEqual(self.viewmodel.remaining_distance, 0.0)
        self.assertEqual(self.viewmodel.parameters, {})
        self.assertEqual(self.viewmodel.waypoints, [])
        self.assertEqual(self.viewmodel.current_position, {"lat": 0.0, "lon": 0.0, "alt": 0.0})
        self.assertEqual(self.viewmodel.target_position, {"lat": 0.0, "lon": 0.0, "alt": 0.0})
        self.assertEqual(self.viewmodel.current_heading, 0.0)
        self.assertEqual(self.viewmodel.target_heading, 0.0)
        self.assertEqual(self.viewmodel.current_speed, 0.0)
        self.assertEqual(self.viewmodel.target_speed, 0.0)
        self.assertEqual(self.viewmodel.current_altitude, 0.0)
        self.assertEqual(self.viewmodel.target_altitude, 0.0)
    
    def test_activation(self):
        """Test der Aktivierung."""
        self.viewmodel.activate()
        self.assertTrue(self.viewmodel.is_active)
        self.assertFalse(self.viewmodel.is_error)
        self.assertEqual(self.viewmodel.error_message, "")
        self.assertEqual(self.viewmodel.status, MissionStatus.PREPARING.value)
    
    def test_deactivation(self):
        """Test der Deaktivierung."""
        self.viewmodel.activate()
        self.viewmodel.deactivate()
        self.assertFalse(self.viewmodel.is_active)
        self.assertFalse(self.viewmodel.is_error)
        self.assertEqual(self.viewmodel.error_message, "")
        self.assertEqual(self.viewmodel.status, MissionStatus.IDLE.value)
    
    def test_waypoint_management(self):
        """Test der Wegpunktverwaltung."""
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
        
        self.viewmodel.set_waypoints(waypoints)
        self.assertEqual(len(self.viewmodel.waypoints), 2)
        self.assertEqual(self.viewmodel.total_waypoints, 2)
        self.assertEqual(self.viewmodel.current_waypoint, 0)
    
    def test_parameter_management(self):
        """Test der Parameterverwaltung."""
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
        
        self.viewmodel.set_parameters(parameters)
        self.assertEqual(self.viewmodel.parameters, parameters)
    
    def test_position_update(self):
        """Test der Positionsaktualisierung."""
        position = {"lat": 48.123, "lon": 11.456, "alt": 100.0}
        self.viewmodel.update_position(position)
        self.assertEqual(self.viewmodel.current_position, position)
    
    def test_heading_update(self):
        """Test der Kursaktualisierung."""
        heading = 90.0
        self.viewmodel.update_heading(heading)
        self.assertEqual(self.viewmodel.current_heading, heading)
    
    def test_speed_update(self):
        """Test der Geschwindigkeitsaktualisierung."""
        speed = 10.0
        self.viewmodel.update_speed(speed)
        self.assertEqual(self.viewmodel.current_speed, speed)
    
    def test_altitude_update(self):
        """Test der Höhenaktualisierung."""
        altitude = 100.0
        self.viewmodel.update_altitude(altitude)
        self.assertEqual(self.viewmodel.current_altitude, altitude)
    
    def test_error_handling(self):
        """Test der Fehlerbehandlung."""
        # Aktivierung im Fehlerzustand
        self.service._state.is_error = True
        self.service._state.error_message = "Test error"
        self.viewmodel.activate()
        self.assertTrue(self.viewmodel.is_error)
        self.assertEqual(self.viewmodel.error_message, "Test error")
        
        # Ungültige Wegpunkte
        invalid_waypoints = [{"id": 1}]  # Fehlende erforderliche Felder
        self.viewmodel.set_waypoints(invalid_waypoints)
        self.assertTrue(self.viewmodel.is_error)
        self.assertIsNotNone(self.viewmodel.error_message)
        
        # Ungültige Parameter
        invalid_parameters = {"invalid": "parameter"}
        self.viewmodel.set_parameters(invalid_parameters)
        self.assertTrue(self.viewmodel.is_error)
        self.assertIsNotNone(self.viewmodel.error_message)
    
    def test_statistics_tracking(self):
        """Test der Statistikverfolgung."""
        self.viewmodel.activate()
        self.service._state.start_time = datetime.now()
        
        # Simuliere Flugzeit
        self.service._state.end_time = datetime.now()
        self.service._state.total_distance = 1000.0
        self.service._state.waypoints_completed = 5
        self.service._state.waypoints_failed = 1
        
        self.service._update_statistics()
        
        self.assertGreater(self.viewmodel.statistics["total_flight_time"], 0.0)
        self.assertEqual(self.viewmodel.statistics["total_distance"], 1000.0)
        self.assertGreater(self.viewmodel.statistics["average_speed"], 0.0)
        self.assertEqual(self.viewmodel.statistics["waypoints_completed"], 5)
        self.assertEqual(self.viewmodel.statistics["waypoints_failed"], 1)
    
    def test_logging(self):
        """Test der Protokollierung."""
        # Ereignisprotokollierung
        self.service._log_event("test_event", "Test event", {"key": "value"})
        self.assertEqual(len(self.viewmodel.log), 1)
        self.assertEqual(self.viewmodel.log[0]["type"], "test_event")
        self.assertEqual(self.viewmodel.log[0]["description"], "Test event")
        self.assertEqual(self.viewmodel.log[0]["data"], {"key": "value"})
        
        # Fehlerprotokollierung
        self.service._log_error("Test error", {"key": "value"})
        self.assertEqual(len(self.viewmodel.log), 2)
        self.assertEqual(self.viewmodel.log[1]["level"], "ERROR")
        self.assertEqual(self.viewmodel.log[1]["message"], "Test error")
        self.assertEqual(self.viewmodel.log[1]["data"], {"key": "value"})
    
    def test_inactive_operations(self):
        """Test von Operationen im inaktiven Zustand."""
        # Wegpunkte setzen
        self.viewmodel.set_waypoints([{"id": 1}])
        self.assertFalse(self.viewmodel.is_error)
        
        # Parameter setzen
        self.viewmodel.set_parameters({"altitude_mode": "relative"})
        self.assertFalse(self.viewmodel.is_error)
        
        # Position aktualisieren
        self.viewmodel.update_position({"lat": 48.123, "lon": 11.456, "alt": 100.0})
        self.assertFalse(self.viewmodel.is_error)
        
        # Kurs aktualisieren
        self.viewmodel.update_heading(90.0)
        self.assertFalse(self.viewmodel.is_error)
        
        # Geschwindigkeit aktualisieren
        self.viewmodel.update_speed(10.0)
        self.assertFalse(self.viewmodel.is_error)
        
        # Höhe aktualisieren
        self.viewmodel.update_altitude(100.0)
        self.assertFalse(self.viewmodel.is_error)

if __name__ == "__main__":
    unittest.main() 