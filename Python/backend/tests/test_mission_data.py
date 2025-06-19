"""Unit Tests für die Datenmodelle der Missionsplanung."""

import unittest
from datetime import datetime
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

class TestMissionData(unittest.TestCase):
    """Testfälle für die Datenmodelle der Missionsplanung."""
    
    def test_mission_types(self):
        """Test der Missionstypen."""
        self.assertEqual(MissionType.WAYPOINT.value, "waypoint")
        self.assertEqual(MissionType.SURVEY.value, "survey")
        self.assertEqual(MissionType.FOLLOW.value, "follow")
        self.assertEqual(MissionType.CUSTOM.value, "custom")
    
    def test_mission_status(self):
        """Test der Missionsstatus."""
        self.assertEqual(MissionStatus.IDLE.value, "idle")
        self.assertEqual(MissionStatus.PREPARING.value, "preparing")
        self.assertEqual(MissionStatus.RUNNING.value, "running")
        self.assertEqual(MissionStatus.PAUSED.value, "paused")
        self.assertEqual(MissionStatus.COMPLETED.value, "completed")
        self.assertEqual(MissionStatus.FAILED.value, "failed")
    
    def test_mission_state(self):
        """Test des Missionszustands."""
        state = MissionState(
            type=MissionType.WAYPOINT,
            status=MissionStatus.IDLE,
            is_active=False,
            is_error=False,
            error_message=None,
            current_waypoint=0,
            total_waypoints=0,
            progress=0.0,
            remaining_time=0.0,
            remaining_distance=0.0,
            start_time=None,
            end_time=None,
            parameters={},
            waypoints=[],
            current_position={"lat": 0.0, "lon": 0.0, "alt": 0.0},
            target_position={"lat": 0.0, "lon": 0.0, "alt": 0.0},
            current_heading=0.0,
            target_heading=0.0,
            current_speed=0.0,
            target_speed=0.0,
            current_altitude=0.0,
            target_altitude=0.0
        )
        
        self.assertEqual(state.type, MissionType.WAYPOINT)
        self.assertEqual(state.status, MissionStatus.IDLE)
        self.assertFalse(state.is_active)
        self.assertFalse(state.is_error)
        self.assertIsNone(state.error_message)
        self.assertEqual(state.current_waypoint, 0)
        self.assertEqual(state.total_waypoints, 0)
        self.assertEqual(state.progress, 0.0)
        self.assertEqual(state.remaining_time, 0.0)
        self.assertEqual(state.remaining_distance, 0.0)
        self.assertIsNone(state.start_time)
        self.assertIsNone(state.end_time)
        self.assertEqual(state.parameters, {})
        self.assertEqual(state.waypoints, [])
        self.assertEqual(state.current_position, {"lat": 0.0, "lon": 0.0, "alt": 0.0})
        self.assertEqual(state.target_position, {"lat": 0.0, "lon": 0.0, "alt": 0.0})
        self.assertEqual(state.current_heading, 0.0)
        self.assertEqual(state.target_heading, 0.0)
        self.assertEqual(state.current_speed, 0.0)
        self.assertEqual(state.target_speed, 0.0)
        self.assertEqual(state.current_altitude, 0.0)
        self.assertEqual(state.target_altitude, 0.0)
    
    def test_mission_statistics(self):
        """Test der Missionsstatistiken."""
        stats = MissionStatistics(
            total_flight_time=0.0,
            total_distance=0.0,
            average_speed=0.0,
            max_speed=0.0,
            min_speed=0.0,
            max_altitude=0.0,
            min_altitude=0.0,
            waypoints_completed=0,
            waypoints_failed=0,
            total_errors=0,
            total_warnings=0,
            battery_consumption=0.0,
            mission_success_rate=0.0
        )
        
        self.assertEqual(stats.total_flight_time, 0.0)
        self.assertEqual(stats.total_distance, 0.0)
        self.assertEqual(stats.average_speed, 0.0)
        self.assertEqual(stats.max_speed, 0.0)
        self.assertEqual(stats.min_speed, 0.0)
        self.assertEqual(stats.max_altitude, 0.0)
        self.assertEqual(stats.min_altitude, 0.0)
        self.assertEqual(stats.waypoints_completed, 0)
        self.assertEqual(stats.waypoints_failed, 0)
        self.assertEqual(stats.total_errors, 0)
        self.assertEqual(stats.total_warnings, 0)
        self.assertEqual(stats.battery_consumption, 0.0)
        self.assertEqual(stats.mission_success_rate, 0.0)
    
    def test_mission_event(self):
        """Test der Missionsereignisse."""
        event = MissionEvent(
            timestamp=datetime.now(),
            type="test_event",
            description="Test event",
            data={"key": "value"}
        )
        
        self.assertIsInstance(event.timestamp, datetime)
        self.assertEqual(event.type, "test_event")
        self.assertEqual(event.description, "Test event")
        self.assertEqual(event.data, {"key": "value"})
    
    def test_mission_log(self):
        """Test der Missionsprotokolle."""
        log = MissionLog(
            timestamp=datetime.now(),
            level="INFO",
            message="Test log message",
            data={"key": "value"}
        )
        
        self.assertIsInstance(log.timestamp, datetime)
        self.assertEqual(log.level, "INFO")
        self.assertEqual(log.message, "Test log message")
        self.assertEqual(log.data, {"key": "value"})
    
    def test_mission_errors(self):
        """Test der Missionsfehler."""
        # MissionError
        error = MissionError("Test error")
        self.assertEqual(str(error), "Test error")
        
        # MissionValidationError
        validation_error = MissionValidationError("Validation error")
        self.assertEqual(str(validation_error), "Validation error")
        
        # MissionExecutionError
        execution_error = MissionExecutionError("Execution error")
        self.assertEqual(str(execution_error), "Execution error")
        
        # MissionParameterError
        parameter_error = MissionParameterError("Parameter error")
        self.assertEqual(str(parameter_error), "Parameter error")

if __name__ == "__main__":
    unittest.main() 