"""Integrationstests für die Missionsplanung."""

import unittest
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

class MockView(QObject):
    """Mock-View für Tests."""
    
    # Signale
    activation_requested = Signal()
    deactivation_requested = Signal()
    waypoints_changed = Signal(list)
    parameters_changed = Signal(dict)
    
    def __init__(self):
        """Initialisierung."""
        super().__init__()
        self._is_active = False
        self._is_error = False
        self._error_message = ""
        self._type = MissionType.WAYPOINT.value
        self._status = MissionStatus.IDLE.value
        self._current_waypoint = 0
        self._total_waypoints = 0
        self._progress = 0.0
        self._remaining_time = 0.0
        self._remaining_distance = 0.0
        self._parameters = {}
        self._waypoints = []
        self._current_position = {"lat": 0.0, "lon": 0.0, "alt": 0.0}
        self._target_position = {"lat": 0.0, "lon": 0.0, "alt": 0.0}
        self._current_heading = 0.0
        self._target_heading = 0.0
        self._current_speed = 0.0
        self._target_speed = 0.0
        self._current_altitude = 0.0
        self._target_altitude = 0.0
        self._statistics = {}
        self._log = []

class TestMissionIntegration(unittest.TestCase):
    """Testfälle für die Integration der Missionsplanung."""
    
    @classmethod
    def setUpClass(cls):
        """Testumgebung vorbereiten."""
        cls.app = QCoreApplication([])
        cls.engine = QQmlApplicationEngine()
    
    def setUp(self):
        """Testumgebung vorbereiten."""
        self.service = MissionService()
        self.viewmodel = MissionViewModel(self.service)
        self.view = MockView()
        
        # Verbindungen herstellen
        self.view.activation_requested.connect(self.viewmodel.activate)
        self.view.deactivation_requested.connect(self.viewmodel.deactivate)
        self.view.waypoints_changed.connect(self.viewmodel.set_waypoints)
        self.view.parameters_changed.connect(self.viewmodel.set_parameters)
        
        self.viewmodel.state_changed.connect(self._handle_state_changed)
        self.viewmodel.mode_changed.connect(self._handle_mode_changed)
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
        self.view._current_waypoint = state["current_waypoint"]
        self.view._total_waypoints = state["total_waypoints"]
        self.view._progress = state["progress"]
        self.view._remaining_time = state["remaining_time"]
        self.view._remaining_distance = state["remaining_distance"]
        self.view._parameters = state["parameters"]
        self.view._waypoints = state["waypoints"]
        self.view._current_position = state["current_position"]
        self.view._target_position = state["target_position"]
        self.view._current_heading = state["current_heading"]
        self.view._target_heading = state["target_heading"]
        self.view._current_speed = state["current_speed"]
        self.view._target_speed = state["target_speed"]
        self.view._current_altitude = state["current_altitude"]
        self.view._target_altitude = state["target_altitude"]
    
    def _handle_mode_changed(self, mode):
        """Modusänderung verarbeiten."""
        self.view._type = mode
    
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
    
    def test_activation_flow(self):
        """Test des Aktivierungsflusses."""
        # 1. Aktivierung anfordern
        self.view.activation_requested.emit()
        
        # 2. Zustand überprüfen
        self.assertTrue(self.service._state.is_active)
        self.assertTrue(self.viewmodel.is_active)
        self.assertTrue(self.view._is_active)
        self.assertEqual(self.service._state.status, MissionStatus.PREPARING)
        self.assertEqual(self.viewmodel.status, MissionStatus.PREPARING.value)
        self.assertEqual(self.view._status, MissionStatus.PREPARING.value)
    
    def test_deactivation_flow(self):
        """Test des Deaktivierungsflusses."""
        # 1. Aktivieren
        self.view.activation_requested.emit()
        
        # 2. Deaktivierung anfordern
        self.view.deactivation_requested.emit()
        
        # 3. Zustand überprüfen
        self.assertFalse(self.service._state.is_active)
        self.assertFalse(self.viewmodel.is_active)
        self.assertFalse(self.view._is_active)
        self.assertEqual(self.service._state.status, MissionStatus.IDLE)
        self.assertEqual(self.viewmodel.status, MissionStatus.IDLE.value)
        self.assertEqual(self.view._status, MissionStatus.IDLE.value)
    
    def test_waypoint_flow(self):
        """Test des Wegpunktflusses."""
        # 1. Wegpunkte setzen
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
        self.view.waypoints_changed.emit(waypoints)
        
        # 2. Zustand überprüfen
        self.assertEqual(len(self.service._state.waypoints), 2)
        self.assertEqual(len(self.viewmodel.waypoints), 2)
        self.assertEqual(len(self.view._waypoints), 2)
        self.assertEqual(self.service._state.total_waypoints, 2)
        self.assertEqual(self.viewmodel.total_waypoints, 2)
        self.assertEqual(self.view._total_waypoints, 2)
    
    def test_parameter_flow(self):
        """Test des Parameterflusses."""
        # 1. Parameter setzen
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
        self.view.parameters_changed.emit(parameters)
        
        # 2. Zustand überprüfen
        self.assertEqual(self.service._state.parameters, parameters)
        self.assertEqual(self.viewmodel.parameters, parameters)
        self.assertEqual(self.view._parameters, parameters)
    
    def test_error_flow(self):
        """Test des Fehlerflusses."""
        # 1. Ungültige Wegpunkte setzen
        invalid_waypoints = [{"id": 1}]  # Fehlende erforderliche Felder
        self.view.waypoints_changed.emit(invalid_waypoints)
        
        # 2. Zustand überprüfen
        self.assertTrue(self.service._state.is_error)
        self.assertTrue(self.viewmodel.is_error)
        self.assertTrue(self.view._is_error)
        self.assertIsNotNone(self.service._state.error_message)
        self.assertIsNotNone(self.viewmodel.error_message)
        self.assertIsNotNone(self.view._error_message)
    
    def test_statistics_flow(self):
        """Test des Statistikflusses."""
        # 1. Aktivieren
        self.view.activation_requested.emit()
        self.service._state.start_time = datetime.now()
        
        # 2. Simuliere Flugzeit
        self.service._state.end_time = datetime.now()
        self.service._state.total_distance = 1000.0
        self.service._state.waypoints_completed = 5
        self.service._state.waypoints_failed = 1
        
        # 3. Statistiken aktualisieren
        self.service._update_statistics()
        
        # 4. Zustand überprüfen
        self.assertGreater(self.service._statistics.total_flight_time, 0.0)
        self.assertGreater(self.viewmodel.statistics["total_flight_time"], 0.0)
        self.assertGreater(self.view._statistics["total_flight_time"], 0.0)
        self.assertEqual(self.service._statistics.total_distance, 1000.0)
        self.assertEqual(self.viewmodel.statistics["total_distance"], 1000.0)
        self.assertEqual(self.view._statistics["total_distance"], 1000.0)
    
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

if __name__ == "__main__":
    unittest.main() 