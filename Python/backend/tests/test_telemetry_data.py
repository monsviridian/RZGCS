"""Unit Tests für die Datenmodelle der Telemetrie."""

import unittest
from datetime import datetime
from flight_control.models.telemetry_data import (
    TelemetryType,
    TelemetryStatus,
    TelemetryState,
    TelemetryStatistics,
    TelemetryEvent,
    TelemetryLog,
    TelemetryError,
    TelemetryValidationError,
    TelemetryConnectionError,
    TelemetryDataError
)

class TestTelemetryData(unittest.TestCase):
    """Testfälle für die Datenmodelle der Telemetrie."""
    
    def test_telemetry_types(self):
        """Test der Telemetrietypen."""
        self.assertEqual(TelemetryType.POSITION.value, "position")
        self.assertEqual(TelemetryType.ATTITUDE.value, "attitude")
        self.assertEqual(TelemetryType.VELOCITY.value, "velocity")
        self.assertEqual(TelemetryType.ACCELERATION.value, "acceleration")
        self.assertEqual(TelemetryType.BATTERY.value, "battery")
        self.assertEqual(TelemetryType.SENSORS.value, "sensors")
        self.assertEqual(TelemetryType.SYSTEM.value, "system")
    
    def test_telemetry_status(self):
        """Test der Telemetriestatus."""
        self.assertEqual(TelemetryStatus.DISCONNECTED.value, "disconnected")
        self.assertEqual(TelemetryStatus.CONNECTING.value, "connecting")
        self.assertEqual(TelemetryStatus.CONNECTED.value, "connected")
        self.assertEqual(TelemetryStatus.DISCONNECTING.value, "disconnecting")
        self.assertEqual(TelemetryStatus.ERROR.value, "error")
    
    def test_telemetry_state(self):
        """Test des Telemetriezustands."""
        state = TelemetryState(
            type=TelemetryType.POSITION,
            status=TelemetryStatus.DISCONNECTED,
            is_active=False,
            is_error=False,
            error_message=None,
            is_connected=False,
            connection_quality=0.0,
            last_update=None,
            update_rate=0.0,
            position={"lat": 0.0, "lon": 0.0, "alt": 0.0},
            attitude={"roll": 0.0, "pitch": 0.0, "yaw": 0.0},
            velocity={"vx": 0.0, "vy": 0.0, "vz": 0.0},
            acceleration={"ax": 0.0, "ay": 0.0, "az": 0.0},
            battery={"voltage": 0.0, "current": 0.0, "remaining": 0.0},
            sensors={
                "gps": {"satellites": 0, "hdop": 0.0},
                "imu": {"temperature": 0.0, "pressure": 0.0},
                "compass": {"heading": 0.0, "declination": 0.0}
            },
            system={
                "cpu_usage": 0.0,
                "memory_usage": 0.0,
                "temperature": 0.0,
                "uptime": 0.0
            }
        )
        
        self.assertEqual(state.type, TelemetryType.POSITION)
        self.assertEqual(state.status, TelemetryStatus.DISCONNECTED)
        self.assertFalse(state.is_active)
        self.assertFalse(state.is_error)
        self.assertIsNone(state.error_message)
        self.assertFalse(state.is_connected)
        self.assertEqual(state.connection_quality, 0.0)
        self.assertIsNone(state.last_update)
        self.assertEqual(state.update_rate, 0.0)
        self.assertEqual(state.position, {"lat": 0.0, "lon": 0.0, "alt": 0.0})
        self.assertEqual(state.attitude, {"roll": 0.0, "pitch": 0.0, "yaw": 0.0})
        self.assertEqual(state.velocity, {"vx": 0.0, "vy": 0.0, "vz": 0.0})
        self.assertEqual(state.acceleration, {"ax": 0.0, "ay": 0.0, "az": 0.0})
        self.assertEqual(state.battery, {"voltage": 0.0, "current": 0.0, "remaining": 0.0})
        self.assertEqual(state.sensors, {
            "gps": {"satellites": 0, "hdop": 0.0},
            "imu": {"temperature": 0.0, "pressure": 0.0},
            "compass": {"heading": 0.0, "declination": 0.0}
        })
        self.assertEqual(state.system, {
            "cpu_usage": 0.0,
            "memory_usage": 0.0,
            "temperature": 0.0,
            "uptime": 0.0
        })
    
    def test_telemetry_statistics(self):
        """Test der Telemetriestatistiken."""
        stats = TelemetryStatistics(
            total_connection_time=0.0,
            total_disconnection_time=0.0,
            total_error_time=0.0,
            average_connection_quality=0.0,
            min_connection_quality=0.0,
            max_connection_quality=0.0,
            total_updates=0,
            average_update_rate=0.0,
            min_update_rate=0.0,
            max_update_rate=0.0,
            total_errors=0,
            total_warnings=0,
            battery_consumption=0.0,
            data_volume=0.0
        )
        
        self.assertEqual(stats.total_connection_time, 0.0)
        self.assertEqual(stats.total_disconnection_time, 0.0)
        self.assertEqual(stats.total_error_time, 0.0)
        self.assertEqual(stats.average_connection_quality, 0.0)
        self.assertEqual(stats.min_connection_quality, 0.0)
        self.assertEqual(stats.max_connection_quality, 0.0)
        self.assertEqual(stats.total_updates, 0)
        self.assertEqual(stats.average_update_rate, 0.0)
        self.assertEqual(stats.min_update_rate, 0.0)
        self.assertEqual(stats.max_update_rate, 0.0)
        self.assertEqual(stats.total_errors, 0)
        self.assertEqual(stats.total_warnings, 0)
        self.assertEqual(stats.battery_consumption, 0.0)
        self.assertEqual(stats.data_volume, 0.0)
    
    def test_telemetry_event(self):
        """Test der Telemetrieereignisse."""
        event = TelemetryEvent(
            timestamp=datetime.now(),
            type="test_event",
            description="Test event",
            data={"key": "value"}
        )
        
        self.assertIsInstance(event.timestamp, datetime)
        self.assertEqual(event.type, "test_event")
        self.assertEqual(event.description, "Test event")
        self.assertEqual(event.data, {"key": "value"})
    
    def test_telemetry_log(self):
        """Test der Telemetrieprotokolle."""
        log = TelemetryLog(
            timestamp=datetime.now(),
            level="INFO",
            message="Test log message",
            data={"key": "value"}
        )
        
        self.assertIsInstance(log.timestamp, datetime)
        self.assertEqual(log.level, "INFO")
        self.assertEqual(log.message, "Test log message")
        self.assertEqual(log.data, {"key": "value"})
    
    def test_telemetry_errors(self):
        """Test der Telemetriefehler."""
        # TelemetryError
        error = TelemetryError("Test error")
        self.assertEqual(str(error), "Test error")
        
        # TelemetryValidationError
        validation_error = TelemetryValidationError("Validation error")
        self.assertEqual(str(validation_error), "Validation error")
        
        # TelemetryConnectionError
        connection_error = TelemetryConnectionError("Connection error")
        self.assertEqual(str(connection_error), "Connection error")
        
        # TelemetryDataError
        data_error = TelemetryDataError("Data error")
        self.assertEqual(str(data_error), "Data error")

if __name__ == "__main__":
    unittest.main() 