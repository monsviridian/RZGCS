"""Systemtests für die Telemetrie."""

import unittest
import time
from datetime import datetime
from PySide6.QtCore import QObject, Signal, Slot, QTimer, QCoreApplication
from PySide6.QtQml import QQmlApplicationEngine
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
from flight_control.viewmodels.telemetry_viewmodel import TelemetryViewModel

class TestTelemetrySystem(unittest.TestCase):
    """Testfälle für das Telemetriesystem."""
    
    @classmethod
    def setUpClass(cls):
        """Testumgebung vorbereiten."""
        cls.app = QCoreApplication([])
        cls.engine = QQmlApplicationEngine()
    
    def setUp(self):
        """Testumgebung vorbereiten."""
        self.service = TelemetryService()
        self.viewmodel = TelemetryViewModel(self.service)
    
    def test_end_to_end_scenario(self):
        """Test eines End-to-End-Szenarios."""
        # 1. Verbindung herstellen
        self.service.connect()
        self.service._handle_connection_success()
        
        # 2. Daten aktualisieren
        for i in range(10):
            # Position aktualisieren
            position = {
                "lat": 48.123 + i * 0.001,
                "lon": 11.456 + i * 0.001,
                "alt": 100.0 + i * 10.0
            }
            self.service.update_position(position)
            
            # Attitude aktualisieren
            attitude = {
                "roll": i * 5.0,
                "pitch": i * 2.5,
                "yaw": i * 10.0
            }
            self.service.update_attitude(attitude)
            
            # Geschwindigkeit aktualisieren
            velocity = {
                "vx": i * 0.5,
                "vy": i * 0.25,
                "vz": i * 0.1
            }
            self.service.update_velocity(velocity)
            
            # Beschleunigung aktualisieren
            acceleration = {
                "ax": i * 0.01,
                "ay": i * 0.005,
                "az": i * 0.001
            }
            self.service.update_acceleration(acceleration)
            
            # Batterie aktualisieren
            battery = {
                "voltage": 11.1 - i * 0.1,
                "current": 2.0 + i * 0.1,
                "remaining": 80.0 - i * 5.0
            }
            self.service.update_battery(battery)
            
            # Sensoren aktualisieren
            sensors = {
                "gps": {
                    "satellites": 8 + i,
                    "hdop": 1.2 - i * 0.1
                },
                "imu": {
                    "temperature": 35.0 + i * 0.5,
                    "pressure": 1013.0 - i * 0.1
                },
                "compass": {
                    "heading": 90.0 + i * 5.0,
                    "declination": 2.0
                }
            }
            self.service.update_sensors(sensors)
            
            # System aktualisieren
            system = {
                "cpu_usage": 25.0 + i * 0.5,
                "memory_usage": 50.0 + i * 0.5,
                "temperature": 45.0 + i * 0.5,
                "uptime": 3600.0 + i * 60.0
            }
            self.service.update_system(system)
            
            # Kurze Pause für Simulation
            time.sleep(0.1)
        
        # 3. Verbindung trennen
        self.service.disconnect()
        
        # 4. Ergebnisse überprüfen
        self.assertFalse(self.service._state.is_active)
        self.assertFalse(self.service._state.is_error)
        self.assertIsNone(self.service._state.error_message)
        self.assertEqual(self.service._state.status, TelemetryStatus.DISCONNECTED)
        self.assertFalse(self.service._state.is_connected)
        self.assertIsNotNone(self.service._state.last_update)
        self.assertGreater(self.service._statistics.total_connection_time, 0.0)
        self.assertGreater(self.service._statistics.total_updates, 0)
        self.assertGreater(self.service._statistics.average_update_rate, 0.0)
        self.assertGreater(self.service._statistics.data_volume, 0.0)
    
    def test_error_scenarios(self):
        """Test von Fehlerszenarien."""
        # 1. Verbindungsfehler
        self.service.connect()
        self.service._handle_connection_error("Connection failed")
        self.assertTrue(self.service._state.is_error)
        self.assertEqual(self.service._state.error_message, "Connection failed")
        self.assertEqual(self.service._state.status, TelemetryStatus.ERROR)
        
        # 2. Datenfehler
        self.service._reset_error()
        self.service._handle_data_error("Invalid data")
        self.assertTrue(self.service._state.is_error)
        self.assertEqual(self.service._state.error_message, "Invalid data")
        self.assertEqual(self.service._state.status, TelemetryStatus.ERROR)
        
        # 3. Verbindung im Fehlerzustand
        self.service._reset_error()
        self.service._state.is_error = True
        self.service._state.error_message = "Test error"
        self.service.connect()
        self.assertTrue(self.service._state.is_error)
        self.assertEqual(self.service._state.error_message, "Test error")
        
        # 4. Ungültige Daten
        self.service._reset_error()
        self.service.update_position(None)
        self.assertTrue(self.service._state.is_error)
        self.assertIsNotNone(self.service._state.error_message)
    
    def test_performance(self):
        """Test der Performance."""
        # 1. Verbindung herstellen
        self.service.connect()
        self.service._handle_connection_success()
        
        # 2. Performance messen
        start_time = time.time()
        
        # Daten aktualisieren
        for _ in range(100):
            self.service.update_position({"lat": 48.123, "lon": 11.456, "alt": 100.0})
            self.service.update_attitude({"roll": 10.0, "pitch": 5.0, "yaw": 90.0})
            self.service.update_velocity({"vx": 5.0, "vy": 0.0, "vz": 1.0})
            self.service.update_acceleration({"ax": 0.1, "ay": 0.0, "az": 0.1})
            self.service.update_battery({"voltage": 11.1, "current": 2.0, "remaining": 80.0})
            self.service.update_sensors({
                "gps": {"satellites": 8, "hdop": 1.2},
                "imu": {"temperature": 35.0, "pressure": 1013.0},
                "compass": {"heading": 90.0, "declination": 2.0}
            })
            self.service.update_system({
                "cpu_usage": 25.0,
                "memory_usage": 50.0,
                "temperature": 45.0,
                "uptime": 3600.0
            })
        
        end_time = time.time()
        
        # 3. Ergebnisse überprüfen
        total_time = end_time - start_time
        self.assertLess(total_time, 1.0)  # Sollte weniger als 1 Sekunde dauern
        self.assertGreater(self.service._statistics.total_updates, 0)
        self.assertGreater(self.service._statistics.average_update_rate, 0.0)
        self.assertGreater(self.service._statistics.data_volume, 0.0)
    
    def test_concurrent_operations(self):
        """Test von gleichzeitigen Operationen."""
        # 1. Verbindung herstellen
        self.service.connect()
        self.service._handle_connection_success()
        
        # 2. Gleichzeitige Operationen
        for _ in range(100):
            # Position aktualisieren
            self.service.update_position({"lat": 48.123, "lon": 11.456, "alt": 100.0})
            
            # Attitude aktualisieren
            self.service.update_attitude({"roll": 10.0, "pitch": 5.0, "yaw": 90.0})
            
            # Geschwindigkeit aktualisieren
            self.service.update_velocity({"vx": 5.0, "vy": 0.0, "vz": 1.0})
            
            # Beschleunigung aktualisieren
            self.service.update_acceleration({"ax": 0.1, "ay": 0.0, "az": 0.1})
            
            # Batterie aktualisieren
            self.service.update_battery({"voltage": 11.1, "current": 2.0, "remaining": 80.0})
            
            # Sensoren aktualisieren
            self.service.update_sensors({
                "gps": {"satellites": 8, "hdop": 1.2},
                "imu": {"temperature": 35.0, "pressure": 1013.0},
                "compass": {"heading": 90.0, "declination": 2.0}
            })
            
            # System aktualisieren
            self.service.update_system({
                "cpu_usage": 25.0,
                "memory_usage": 50.0,
                "temperature": 45.0,
                "uptime": 3600.0
            })
        
        # 3. Verbindung trennen
        self.service.disconnect()
        
        # 4. Ergebnisse überprüfen
        self.assertFalse(self.service._state.is_error)
        self.assertIsNone(self.service._state.error_message)
        self.assertEqual(self.service._state.status, TelemetryStatus.DISCONNECTED)
        self.assertGreater(self.service._statistics.total_updates, 0)
        self.assertGreater(self.service._statistics.average_update_rate, 0.0)
        self.assertGreater(self.service._statistics.data_volume, 0.0)
    
    def test_recovery_scenarios(self):
        """Test von Wiederherstellungsszenarien."""
        # 1. Verbindung herstellen
        self.service.connect()
        self.service._handle_connection_success()
        
        # 2. Fehler simulieren
        self.service._handle_connection_error("Connection failed")
        self.assertTrue(self.service._state.is_error)
        self.assertEqual(self.service._state.error_message, "Connection failed")
        self.assertEqual(self.service._state.status, TelemetryStatus.ERROR)
        
        # 3. Wiederherstellung
        self.service._reset_error()
        self.assertFalse(self.service._state.is_error)
        self.assertIsNone(self.service._state.error_message)
        
        # 4. Verbindung wiederherstellen
        self.service.connect()
        self.service._handle_connection_success()
        self.assertTrue(self.service._state.is_connected)
        self.assertEqual(self.service._state.status, TelemetryStatus.CONNECTED)
        
        # 5. Daten aktualisieren
        self.service.update_position({"lat": 48.123, "lon": 11.456, "alt": 100.0})
        self.assertFalse(self.service._state.is_error)
        self.assertIsNone(self.service._state.error_message)
        
        # 6. Verbindung trennen
        self.service.disconnect()
        
        # 7. Ergebnisse überprüfen
        self.assertFalse(self.service._state.is_error)
        self.assertIsNone(self.service._state.error_message)
        self.assertEqual(self.service._state.status, TelemetryStatus.DISCONNECTED)

if __name__ == "__main__":
    unittest.main() 