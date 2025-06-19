"""Unit Tests für das Telemetrie-ViewModel."""

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
from flight_control.viewmodels.telemetry_viewmodel import TelemetryViewModel
from flight_control.services.telemetry_service import TelemetryService

class TestTelemetryViewModel(unittest.TestCase):
    """Testfälle für das Telemetrie-ViewModel."""
    
    def setUp(self):
        """Testumgebung vorbereiten."""
        self.service = TelemetryService()
        self.viewmodel = TelemetryViewModel(self.service)
    
    def test_initial_state(self):
        """Test des initialen Zustands."""
        self.assertFalse(self.viewmodel.is_active)
        self.assertFalse(self.viewmodel.is_error)
        self.assertEqual(self.viewmodel.error_message, "")
        self.assertEqual(self.viewmodel.type, TelemetryType.POSITION.value)
        self.assertEqual(self.viewmodel.status, TelemetryStatus.DISCONNECTED.value)
        self.assertFalse(self.viewmodel.is_connected)
        self.assertEqual(self.viewmodel.connection_quality, 0.0)
        self.assertEqual(self.viewmodel.update_rate, 0.0)
        self.assertEqual(self.viewmodel.position, {"lat": 0.0, "lon": 0.0, "alt": 0.0})
        self.assertEqual(self.viewmodel.attitude, {"roll": 0.0, "pitch": 0.0, "yaw": 0.0})
        self.assertEqual(self.viewmodel.velocity, {"vx": 0.0, "vy": 0.0, "vz": 0.0})
        self.assertEqual(self.viewmodel.acceleration, {"ax": 0.0, "ay": 0.0, "az": 0.0})
        self.assertEqual(self.viewmodel.battery, {"voltage": 0.0, "current": 0.0, "remaining": 0.0})
        self.assertEqual(self.viewmodel.sensors, {
            "gps": {"satellites": 0, "hdop": 0.0},
            "imu": {"temperature": 0.0, "pressure": 0.0},
            "compass": {"heading": 0.0, "declination": 0.0}
        })
        self.assertEqual(self.viewmodel.system, {
            "cpu_usage": 0.0,
            "memory_usage": 0.0,
            "temperature": 0.0,
            "uptime": 0.0
        })
    
    def test_connection(self):
        """Test der Verbindung."""
        # Verbindung herstellen
        self.viewmodel.connect()
        self.assertTrue(self.viewmodel.is_active)
        self.assertFalse(self.viewmodel.is_error)
        self.assertEqual(self.viewmodel.error_message, "")
        self.assertEqual(self.viewmodel.status, TelemetryStatus.CONNECTING.value)
        
        # Verbindung erfolgreich
        self.service._handle_connection_success()
        self.assertTrue(self.viewmodel.is_connected)
        self.assertEqual(self.viewmodel.status, TelemetryStatus.CONNECTED.value)
        self.assertGreater(self.viewmodel.connection_quality, 0.0)
        self.assertGreater(self.viewmodel.update_rate, 0.0)
        
        # Verbindung trennen
        self.viewmodel.disconnect()
        self.assertFalse(self.viewmodel.is_connected)
        self.assertEqual(self.viewmodel.status, TelemetryStatus.DISCONNECTED.value)
    
    def test_data_updates(self):
        """Test der Datenaktualisierungen."""
        # Position aktualisieren
        position = {"lat": 48.123, "lon": 11.456, "alt": 100.0}
        self.viewmodel.update_position(position)
        self.assertEqual(self.viewmodel.position, position)
        
        # Attitude aktualisieren
        attitude = {"roll": 10.0, "pitch": 5.0, "yaw": 90.0}
        self.viewmodel.update_attitude(attitude)
        self.assertEqual(self.viewmodel.attitude, attitude)
        
        # Geschwindigkeit aktualisieren
        velocity = {"vx": 5.0, "vy": 0.0, "vz": 1.0}
        self.viewmodel.update_velocity(velocity)
        self.assertEqual(self.viewmodel.velocity, velocity)
        
        # Beschleunigung aktualisieren
        acceleration = {"ax": 0.1, "ay": 0.0, "az": 0.1}
        self.viewmodel.update_acceleration(acceleration)
        self.assertEqual(self.viewmodel.acceleration, acceleration)
        
        # Batterie aktualisieren
        battery = {"voltage": 11.1, "current": 2.0, "remaining": 80.0}
        self.viewmodel.update_battery(battery)
        self.assertEqual(self.viewmodel.battery, battery)
        
        # Sensoren aktualisieren
        sensors = {
            "gps": {"satellites": 8, "hdop": 1.2},
            "imu": {"temperature": 35.0, "pressure": 1013.0},
            "compass": {"heading": 90.0, "declination": 2.0}
        }
        self.viewmodel.update_sensors(sensors)
        self.assertEqual(self.viewmodel.sensors, sensors)
        
        # System aktualisieren
        system = {
            "cpu_usage": 25.0,
            "memory_usage": 50.0,
            "temperature": 45.0,
            "uptime": 3600.0
        }
        self.viewmodel.update_system(system)
        self.assertEqual(self.viewmodel.system, system)
    
    def test_error_handling(self):
        """Test der Fehlerbehandlung."""
        # Verbindungsfehler
        self.service._handle_connection_error("Connection failed")
        self.assertTrue(self.viewmodel.is_error)
        self.assertEqual(self.viewmodel.error_message, "Connection failed")
        self.assertEqual(self.viewmodel.status, TelemetryStatus.ERROR.value)
        
        # Datenfehler
        self.service._handle_data_error("Invalid data")
        self.assertTrue(self.viewmodel.is_error)
        self.assertEqual(self.viewmodel.error_message, "Invalid data")
        self.assertEqual(self.viewmodel.status, TelemetryStatus.ERROR.value)
        
        # Fehler zurücksetzen
        self.service._reset_error()
        self.assertFalse(self.viewmodel.is_error)
        self.assertEqual(self.viewmodel.error_message, "")
    
    def test_statistics_tracking(self):
        """Test der Statistikverfolgung."""
        # Verbindung herstellen
        self.viewmodel.connect()
        self.service._handle_connection_success()
        
        # Daten aktualisieren
        for _ in range(10):
            self.viewmodel.update_position({"lat": 48.123, "lon": 11.456, "alt": 100.0})
        
        # Verbindung trennen
        self.viewmodel.disconnect()
        
        # Statistiken überprüfen
        self.assertGreater(self.viewmodel.statistics["total_connection_time"], 0.0)
        self.assertGreater(self.viewmodel.statistics["total_updates"], 0)
        self.assertGreater(self.viewmodel.statistics["average_update_rate"], 0.0)
        self.assertGreater(self.viewmodel.statistics["data_volume"], 0.0)
    
    def test_logging(self):
        """Test der Protokollierung."""
        # Ereignis protokollieren
        self.service._log_event("test_event", "Test event", {"key": "value"})
        self.assertEqual(len(self.viewmodel.log), 1)
        self.assertEqual(self.viewmodel.log[0]["type"], "test_event")
        self.assertEqual(self.viewmodel.log[0]["description"], "Test event")
        self.assertEqual(self.viewmodel.log[0]["data"], {"key": "value"})
        
        # Fehler protokollieren
        self.service._log_error("Test error", {"key": "value"})
        self.assertEqual(len(self.viewmodel.log), 2)
        self.assertEqual(self.viewmodel.log[1]["level"], "ERROR")
        self.assertEqual(self.viewmodel.log[1]["message"], "Test error")
        self.assertEqual(self.viewmodel.log[1]["data"], {"key": "value"})
    
    def test_inactive_operations(self):
        """Test von Operationen im inaktiven Zustand."""
        # Position aktualisieren
        self.viewmodel.update_position({"lat": 48.123, "lon": 11.456, "alt": 100.0})
        self.assertFalse(self.viewmodel.is_error)
        
        # Attitude aktualisieren
        self.viewmodel.update_attitude({"roll": 10.0, "pitch": 5.0, "yaw": 90.0})
        self.assertFalse(self.viewmodel.is_error)
        
        # Geschwindigkeit aktualisieren
        self.viewmodel.update_velocity({"vx": 5.0, "vy": 0.0, "vz": 1.0})
        self.assertFalse(self.viewmodel.is_error)
        
        # Beschleunigung aktualisieren
        self.viewmodel.update_acceleration({"ax": 0.1, "ay": 0.0, "az": 0.1})
        self.assertFalse(self.viewmodel.is_error)
        
        # Batterie aktualisieren
        self.viewmodel.update_battery({"voltage": 11.1, "current": 2.0, "remaining": 80.0})
        self.assertFalse(self.viewmodel.is_error)
        
        # Sensoren aktualisieren
        self.viewmodel.update_sensors({
            "gps": {"satellites": 8, "hdop": 1.2},
            "imu": {"temperature": 35.0, "pressure": 1013.0},
            "compass": {"heading": 90.0, "declination": 2.0}
        })
        self.assertFalse(self.viewmodel.is_error)
        
        # System aktualisieren
        self.viewmodel.update_system({
            "cpu_usage": 25.0,
            "memory_usage": 50.0,
            "temperature": 45.0,
            "uptime": 3600.0
        })
        self.assertFalse(self.viewmodel.is_error)

if __name__ == "__main__":
    unittest.main() 