"""Unit Tests für den Telemetrieservice."""

import unittest
from datetime import datetime
from PySide6.QtCore import QObject, Signal, Slot, QTimer
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
from flight_control.services.telemetry_service import TelemetryService

class TestTelemetryService(unittest.TestCase):
    """Testfälle für den Telemetrieservice."""
    
    def setUp(self):
        """Testumgebung vorbereiten."""
        self.service = TelemetryService()
    
    def test_initial_state(self):
        """Test des initialen Zustands."""
        self.assertFalse(self.service._state.is_active)
        self.assertFalse(self.service._state.is_error)
        self.assertIsNone(self.service._state.error_message)
        self.assertEqual(self.service._state.type, TelemetryType.POSITION)
        self.assertEqual(self.service._state.status, TelemetryStatus.DISCONNECTED)
        self.assertFalse(self.service._state.is_connected)
        self.assertEqual(self.service._state.connection_quality, 0.0)
        self.assertIsNone(self.service._state.last_update)
        self.assertEqual(self.service._state.update_rate, 0.0)
    
    def test_connection(self):
        """Test der Verbindung."""
        # Verbindung herstellen
        self.service.connect()
        self.assertTrue(self.service._state.is_active)
        self.assertFalse(self.service._state.is_error)
        self.assertIsNone(self.service._state.error_message)
        self.assertEqual(self.service._state.status, TelemetryStatus.CONNECTING)
        
        # Verbindung erfolgreich
        self.service._handle_connection_success()
        self.assertTrue(self.service._state.is_connected)
        self.assertEqual(self.service._state.status, TelemetryStatus.CONNECTED)
        self.assertGreater(self.service._state.connection_quality, 0.0)
        self.assertIsNotNone(self.service._state.last_update)
        
        # Verbindung trennen
        self.service.disconnect()
        self.assertFalse(self.service._state.is_connected)
        self.assertEqual(self.service._state.status, TelemetryStatus.DISCONNECTED)
    
    def test_data_updates(self):
        """Test der Datenaktualisierungen."""
        # Position aktualisieren
        position = {"lat": 48.123, "lon": 11.456, "alt": 100.0}
        self.service.update_position(position)
        self.assertEqual(self.service._state.position, position)
        
        # Attitude aktualisieren
        attitude = {"roll": 10.0, "pitch": 5.0, "yaw": 90.0}
        self.service.update_attitude(attitude)
        self.assertEqual(self.service._state.attitude, attitude)
        
        # Geschwindigkeit aktualisieren
        velocity = {"vx": 5.0, "vy": 0.0, "vz": 1.0}
        self.service.update_velocity(velocity)
        self.assertEqual(self.service._state.velocity, velocity)
        
        # Beschleunigung aktualisieren
        acceleration = {"ax": 0.1, "ay": 0.0, "az": 0.1}
        self.service.update_acceleration(acceleration)
        self.assertEqual(self.service._state.acceleration, acceleration)
        
        # Batterie aktualisieren
        battery = {"voltage": 11.1, "current": 2.0, "remaining": 80.0}
        self.service.update_battery(battery)
        self.assertEqual(self.service._state.battery, battery)
        
        # Sensoren aktualisieren
        sensors = {
            "gps": {"satellites": 8, "hdop": 1.2},
            "imu": {"temperature": 35.0, "pressure": 1013.0},
            "compass": {"heading": 90.0, "declination": 2.0}
        }
        self.service.update_sensors(sensors)
        self.assertEqual(self.service._state.sensors, sensors)
        
        # System aktualisieren
        system = {
            "cpu_usage": 25.0,
            "memory_usage": 50.0,
            "temperature": 45.0,
            "uptime": 3600.0
        }
        self.service.update_system(system)
        self.assertEqual(self.service._state.system, system)
    
    def test_error_handling(self):
        """Test der Fehlerbehandlung."""
        # Verbindungsfehler
        self.service._handle_connection_error("Connection failed")
        self.assertTrue(self.service._state.is_error)
        self.assertEqual(self.service._state.error_message, "Connection failed")
        self.assertEqual(self.service._state.status, TelemetryStatus.ERROR)
        
        # Datenfehler
        self.service._handle_data_error("Invalid data")
        self.assertTrue(self.service._state.is_error)
        self.assertEqual(self.service._state.error_message, "Invalid data")
        self.assertEqual(self.service._state.status, TelemetryStatus.ERROR)
        
        # Fehler zurücksetzen
        self.service._reset_error()
        self.assertFalse(self.service._state.is_error)
        self.assertIsNone(self.service._state.error_message)
    
    def test_statistics_tracking(self):
        """Test der Statistikverfolgung."""
        # Verbindung herstellen
        self.service.connect()
        self.service._handle_connection_success()
        
        # Daten aktualisieren
        for _ in range(10):
            self.service.update_position({"lat": 48.123, "lon": 11.456, "alt": 100.0})
        
        # Verbindung trennen
        self.service.disconnect()
        
        # Statistiken überprüfen
        self.assertGreater(self.service._statistics.total_connection_time, 0.0)
        self.assertGreater(self.service._statistics.total_updates, 0)
        self.assertGreater(self.service._statistics.average_update_rate, 0.0)
        self.assertGreater(self.service._statistics.data_volume, 0.0)
    
    def test_logging(self):
        """Test der Protokollierung."""
        # Ereignis protokollieren
        self.service._log_event("test_event", "Test event", {"key": "value"})
        self.assertEqual(len(self.service._log), 1)
        self.assertEqual(self.service._log[0].type, "test_event")
        self.assertEqual(self.service._log[0].description, "Test event")
        self.assertEqual(self.service._log[0].data, {"key": "value"})
        
        # Fehler protokollieren
        self.service._log_error("Test error", {"key": "value"})
        self.assertEqual(len(self.service._log), 2)
        self.assertEqual(self.service._log[1].level, "ERROR")
        self.assertEqual(self.service._log[1].message, "Test error")
        self.assertEqual(self.service._log[1].data, {"key": "value"})
    
    def test_inactive_operations(self):
        """Test von Operationen im inaktiven Zustand."""
        # Position aktualisieren
        self.service.update_position({"lat": 48.123, "lon": 11.456, "alt": 100.0})
        self.assertFalse(self.service._state.is_error)
        
        # Attitude aktualisieren
        self.service.update_attitude({"roll": 10.0, "pitch": 5.0, "yaw": 90.0})
        self.assertFalse(self.service._state.is_error)
        
        # Geschwindigkeit aktualisieren
        self.service.update_velocity({"vx": 5.0, "vy": 0.0, "vz": 1.0})
        self.assertFalse(self.service._state.is_error)
        
        # Beschleunigung aktualisieren
        self.service.update_acceleration({"ax": 0.1, "ay": 0.0, "az": 0.1})
        self.assertFalse(self.service._state.is_error)
        
        # Batterie aktualisieren
        self.service.update_battery({"voltage": 11.1, "current": 2.0, "remaining": 80.0})
        self.assertFalse(self.service._state.is_error)
        
        # Sensoren aktualisieren
        self.service.update_sensors({
            "gps": {"satellites": 8, "hdop": 1.2},
            "imu": {"temperature": 35.0, "pressure": 1013.0},
            "compass": {"heading": 90.0, "declination": 2.0}
        })
        self.assertFalse(self.service._state.is_error)
        
        # System aktualisieren
        self.service.update_system({
            "cpu_usage": 25.0,
            "memory_usage": 50.0,
            "temperature": 45.0,
            "uptime": 3600.0
        })
        self.assertFalse(self.service._state.is_error)

if __name__ == "__main__":
    unittest.main() 