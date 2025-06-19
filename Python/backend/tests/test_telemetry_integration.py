"""Integrationstests für die Telemetrie."""

import unittest
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

class MockView(QObject):
    """Mock-View für Tests."""
    
    # Signale
    connection_requested = Signal()
    disconnection_requested = Signal()
    
    def __init__(self):
        """Initialisierung."""
        super().__init__()
        self._is_active = False
        self._is_error = False
        self._error_message = ""
        self._type = TelemetryType.POSITION.value
        self._status = TelemetryStatus.DISCONNECTED.value
        self._is_connected = False
        self._connection_quality = 0.0
        self._update_rate = 0.0
        self._position = {"lat": 0.0, "lon": 0.0, "alt": 0.0}
        self._attitude = {"roll": 0.0, "pitch": 0.0, "yaw": 0.0}
        self._velocity = {"vx": 0.0, "vy": 0.0, "vz": 0.0}
        self._acceleration = {"ax": 0.0, "ay": 0.0, "az": 0.0}
        self._battery = {"voltage": 0.0, "current": 0.0, "remaining": 0.0}
        self._sensors = {
            "gps": {"satellites": 0, "hdop": 0.0},
            "imu": {"temperature": 0.0, "pressure": 0.0},
            "compass": {"heading": 0.0, "declination": 0.0}
        }
        self._system = {
            "cpu_usage": 0.0,
            "memory_usage": 0.0,
            "temperature": 0.0,
            "uptime": 0.0
        }
        self._statistics = {}
        self._log = []

class TestTelemetryIntegration(unittest.TestCase):
    """Testfälle für die Integration der Telemetrie."""
    
    @classmethod
    def setUpClass(cls):
        """Testumgebung vorbereiten."""
        cls.app = QCoreApplication([])
        cls.engine = QQmlApplicationEngine()
    
    def setUp(self):
        """Testumgebung vorbereiten."""
        self.service = TelemetryService()
        self.viewmodel = TelemetryViewModel(self.service)
        self.view = MockView()
        
        # Verbindungen herstellen
        self.view.connection_requested.connect(self.viewmodel.connect)
        self.view.disconnection_requested.connect(self.viewmodel.disconnect)
        
        self.viewmodel.state_changed.connect(self._handle_state_changed)
        self.viewmodel.status_changed.connect(self._handle_status_changed)
        self.viewmodel.error_changed.connect(self._handle_error_changed)
        self.viewmodel.event_changed.connect(self._handle_event_changed)
        self.viewmodel.statistics_changed.connect(self._handle_statistics_changed)
        self.viewmodel.log_changed.connect(self._handle_log_changed)
    
    def _handle_state_changed(self, state):
        """Zustandsänderung verarbeiten."""
        self.view._is_active = state["is_active"]
        self.view._is_error = state["is_error"]
        self.view._error_message = state["error_message"]
        self.view._type = state["type"]
        self.view._status = state["status"]
        self.view._is_connected = state["is_connected"]
        self.view._connection_quality = state["connection_quality"]
        self.view._update_rate = state["update_rate"]
        self.view._position = state["position"]
        self.view._attitude = state["attitude"]
        self.view._velocity = state["velocity"]
        self.view._acceleration = state["acceleration"]
        self.view._battery = state["battery"]
        self.view._sensors = state["sensors"]
        self.view._system = state["system"]
    
    def _handle_status_changed(self, status):
        """Statusänderung verarbeiten."""
        self.view._status = status
    
    def _handle_error_changed(self, error):
        """Fehleränderung verarbeiten."""
        self.view._is_error = error["is_error"]
        self.view._error_message = error["message"]
    
    def _handle_event_changed(self, event):
        """Ereignisänderung verarbeiten."""
        self.view._log.append(event)
    
    def _handle_statistics_changed(self, statistics):
        """Statistikänderung verarbeiten."""
        self.view._statistics = statistics
    
    def _handle_log_changed(self, log):
        """Protokolländerung verarbeiten."""
        self.view._log = log
    
    def test_connection_flow(self):
        """Test des Verbindungsflusses."""
        # 1. Verbindung anfordern
        self.view.connection_requested.emit()
        
        # 2. Zustand überprüfen
        self.assertTrue(self.service._state.is_active)
        self.assertTrue(self.viewmodel.is_active)
        self.assertTrue(self.view._is_active)
        self.assertEqual(self.service._state.status, TelemetryStatus.CONNECTING)
        self.assertEqual(self.viewmodel.status, TelemetryStatus.CONNECTING.value)
        self.assertEqual(self.view._status, TelemetryStatus.CONNECTING.value)
        
        # 3. Verbindung erfolgreich
        self.service._handle_connection_success()
        self.assertTrue(self.service._state.is_connected)
        self.assertTrue(self.viewmodel.is_connected)
        self.assertTrue(self.view._is_connected)
        self.assertEqual(self.service._state.status, TelemetryStatus.CONNECTED)
        self.assertEqual(self.viewmodel.status, TelemetryStatus.CONNECTED.value)
        self.assertEqual(self.view._status, TelemetryStatus.CONNECTED.value)
        
        # 4. Verbindung trennen
        self.view.disconnection_requested.emit()
        self.assertFalse(self.service._state.is_connected)
        self.assertFalse(self.viewmodel.is_connected)
        self.assertFalse(self.view._is_connected)
        self.assertEqual(self.service._state.status, TelemetryStatus.DISCONNECTED)
        self.assertEqual(self.viewmodel.status, TelemetryStatus.DISCONNECTED.value)
        self.assertEqual(self.view._status, TelemetryStatus.DISCONNECTED.value)
    
    def test_data_flow(self):
        """Test des Datenflusses."""
        # 1. Verbindung herstellen
        self.view.connection_requested.emit()
        self.service._handle_connection_success()
        
        # 2. Daten aktualisieren
        position = {"lat": 48.123, "lon": 11.456, "alt": 100.0}
        self.service.update_position(position)
        self.assertEqual(self.service._state.position, position)
        self.assertEqual(self.viewmodel.position, position)
        self.assertEqual(self.view._position, position)
        
        attitude = {"roll": 10.0, "pitch": 5.0, "yaw": 90.0}
        self.service.update_attitude(attitude)
        self.assertEqual(self.service._state.attitude, attitude)
        self.assertEqual(self.viewmodel.attitude, attitude)
        self.assertEqual(self.view._attitude, attitude)
        
        velocity = {"vx": 5.0, "vy": 0.0, "vz": 1.0}
        self.service.update_velocity(velocity)
        self.assertEqual(self.service._state.velocity, velocity)
        self.assertEqual(self.viewmodel.velocity, velocity)
        self.assertEqual(self.view._velocity, velocity)
        
        acceleration = {"ax": 0.1, "ay": 0.0, "az": 0.1}
        self.service.update_acceleration(acceleration)
        self.assertEqual(self.service._state.acceleration, acceleration)
        self.assertEqual(self.viewmodel.acceleration, acceleration)
        self.assertEqual(self.view._acceleration, acceleration)
        
        battery = {"voltage": 11.1, "current": 2.0, "remaining": 80.0}
        self.service.update_battery(battery)
        self.assertEqual(self.service._state.battery, battery)
        self.assertEqual(self.viewmodel.battery, battery)
        self.assertEqual(self.view._battery, battery)
        
        sensors = {
            "gps": {"satellites": 8, "hdop": 1.2},
            "imu": {"temperature": 35.0, "pressure": 1013.0},
            "compass": {"heading": 90.0, "declination": 2.0}
        }
        self.service.update_sensors(sensors)
        self.assertEqual(self.service._state.sensors, sensors)
        self.assertEqual(self.viewmodel.sensors, sensors)
        self.assertEqual(self.view._sensors, sensors)
        
        system = {
            "cpu_usage": 25.0,
            "memory_usage": 50.0,
            "temperature": 45.0,
            "uptime": 3600.0
        }
        self.service.update_system(system)
        self.assertEqual(self.service._state.system, system)
        self.assertEqual(self.viewmodel.system, system)
        self.assertEqual(self.view._system, system)
    
    def test_error_flow(self):
        """Test des Fehlerflusses."""
        # 1. Verbindung herstellen
        self.view.connection_requested.emit()
        
        # 2. Verbindungsfehler
        self.service._handle_connection_error("Connection failed")
        self.assertTrue(self.service._state.is_error)
        self.assertTrue(self.viewmodel.is_error)
        self.assertTrue(self.view._is_error)
        self.assertEqual(self.service._state.error_message, "Connection failed")
        self.assertEqual(self.viewmodel.error_message, "Connection failed")
        self.assertEqual(self.view._error_message, "Connection failed")
        
        # 3. Fehler zurücksetzen
        self.service._reset_error()
        self.assertFalse(self.service._state.is_error)
        self.assertFalse(self.viewmodel.is_error)
        self.assertFalse(self.view._is_error)
        self.assertIsNone(self.service._state.error_message)
        self.assertEqual(self.viewmodel.error_message, "")
        self.assertEqual(self.view._error_message, "")
    
    def test_statistics_flow(self):
        """Test des Statistikflusses."""
        # 1. Verbindung herstellen
        self.view.connection_requested.emit()
        self.service._handle_connection_success()
        
        # 2. Daten aktualisieren
        for _ in range(10):
            self.service.update_position({"lat": 48.123, "lon": 11.456, "alt": 100.0})
        
        # 3. Verbindung trennen
        self.view.disconnection_requested.emit()
        
        # 4. Statistiken überprüfen
        self.assertGreater(self.service._statistics.total_connection_time, 0.0)
        self.assertGreater(self.viewmodel.statistics["total_connection_time"], 0.0)
        self.assertGreater(self.view._statistics["total_connection_time"], 0.0)
        self.assertGreater(self.service._statistics.total_updates, 0)
        self.assertGreater(self.viewmodel.statistics["total_updates"], 0)
        self.assertGreater(self.view._statistics["total_updates"], 0)
    
    def test_log_flow(self):
        """Test des Protokollflusses."""
        # 1. Ereignis protokollieren
        self.service._log_event("test_event", "Test event", {"key": "value"})
        
        # 2. Zustand überprüfen
        self.assertEqual(len(self.service._log), 1)
        self.assertEqual(len(self.viewmodel.log), 1)
        self.assertEqual(len(self.view._log), 1)
        self.assertEqual(self.service._log[0].type, "test_event")
        self.assertEqual(self.viewmodel.log[0]["type"], "test_event")
        self.assertEqual(self.view._log[0]["type"], "test_event")
        
        # 3. Fehler protokollieren
        self.service._log_error("Test error", {"key": "value"})
        
        # 4. Zustand überprüfen
        self.assertEqual(len(self.service._log), 2)
        self.assertEqual(len(self.viewmodel.log), 2)
        self.assertEqual(len(self.view._log), 2)
        self.assertEqual(self.service._log[1].level, "ERROR")
        self.assertEqual(self.viewmodel.log[1]["level"], "ERROR")
        self.assertEqual(self.view._log[1]["level"], "ERROR")

if __name__ == "__main__":
    unittest.main() 