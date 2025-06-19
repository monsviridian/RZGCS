"""
Unit Tests für das ViewModel der Kollisionsvermeidung.
"""

import unittest
from datetime import datetime
from PySide6.QtCore import QCoreApplication
from flight_control.models.collision_data import (
    ObjectType,
    DetectionMethod,
    AvoidanceStrategy,
    DetectedObject,
    CollisionState,
    CollisionStatistics,
    CollisionEvent
)
from flight_control.viewmodels.collision_viewmodel import CollisionViewModel

class TestCollisionViewModel(unittest.TestCase):
    """Testfälle für das ViewModel der Kollisionsvermeidung."""

    @classmethod
    def setUpClass(cls):
        """Initialisiere die Testumgebung."""
        cls.app = QCoreApplication([])

    def setUp(self):
        """Initialisiere jeden Testfall."""
        self.viewmodel = CollisionViewModel()
        self.state_changes = []
        self.object_detections = []
        self.strategy_changes = []
        self.avoidance_starts = []
        self.avoidance_completions = []
        self.errors = []
        self.events = []
        self.statistics_updates = []
        self.log_updates = []

        # Verbinde Signale
        self.viewmodel.state_changed.connect(lambda state: self.state_changes.append(state))
        self.viewmodel.object_detected.connect(lambda obj: self.object_detections.append(obj))
        self.viewmodel.strategy_changed.connect(lambda strategy: self.strategy_changes.append(strategy))
        self.viewmodel.avoidance_started.connect(lambda strategy: self.avoidance_starts.append(strategy))
        self.viewmodel.avoidance_completed.connect(lambda success: self.avoidance_completions.append(success))
        self.viewmodel.error_occurred.connect(lambda error: self.errors.append(error))
        self.viewmodel.event_occurred.connect(lambda event: self.events.append(event))
        self.viewmodel.statistics_updated.connect(lambda stats: self.statistics_updates.append(stats))
        self.viewmodel.log_updated.connect(lambda log: self.log_updates.append(log))

    def test_initial_state(self):
        """Teste den initialen Zustand."""
        self.assertFalse(self.viewmodel.is_active)
        self.assertFalse(self.viewmodel.is_error)
        self.assertEqual(self.viewmodel.error_message, "")
        self.assertEqual(len(self.viewmodel.detected_objects), 0)
        self.assertEqual(self.viewmodel.current_strategy, "")
        self.assertFalse(self.viewmodel.avoidance_in_progress)

    def test_activation(self):
        """Teste die Aktivierung."""
        self.viewmodel.activate()
        
        self.assertTrue(self.viewmodel.is_active)
        self.assertFalse(self.viewmodel.is_error)
        self.assertEqual(self.viewmodel.error_message, "")
        
        # Prüfe Signale
        self.assertEqual(len(self.state_changes), 1)
        self.assertEqual(len(self.events), 1)
        self.assertEqual(self.events[0].type, "activation")

    def test_deactivation(self):
        """Teste die Deaktivierung."""
        self.viewmodel.activate()
        self.viewmodel.deactivate()
        
        self.assertFalse(self.viewmodel.is_active)
        self.assertFalse(self.viewmodel.is_error)
        self.assertEqual(self.viewmodel.error_message, "")
        self.assertEqual(self.viewmodel.current_strategy, "")
        self.assertFalse(self.viewmodel.avoidance_in_progress)
        
        # Prüfe Signale
        self.assertEqual(len(self.state_changes), 2)
        self.assertEqual(len(self.events), 2)
        self.assertEqual(self.events[1].type, "deactivation")

    def test_object_detection(self):
        """Teste die Objekterkennung."""
        self.viewmodel.activate()
        
        # Erstelle Testobjekte
        objects = [
            DetectedObject(
                id="test1",
                type=ObjectType.STATIC,
                position={"lat": 48.123, "lon": 11.456, "alt": 100.0},
                velocity={"vx": 0.0, "vy": 0.0, "vz": 0.0},
                size={"length": 5.0, "width": 3.0, "height": 2.0},
                confidence=0.95,
                detection_method=DetectionMethod.LIDAR
            ),
            DetectedObject(
                id="test2",
                type=ObjectType.DYNAMIC,
                position={"lat": 48.124, "lon": 11.457, "alt": 101.0},
                velocity={"vx": 1.0, "vy": 1.0, "vz": 0.0},
                size={"length": 2.0, "width": 2.0, "height": 1.0},
                confidence=0.85,
                detection_method=DetectionMethod.RADAR
            )
        ]
        
        self.viewmodel.update_detected_objects(objects)
        
        # Prüfe Properties
        self.assertEqual(len(self.viewmodel.detected_objects), 2)
        
        # Prüfe Statistiken
        stats = self.viewmodel.statistics
        self.assertEqual(stats["total_detections"], 2)
        self.assertEqual(stats["static_detections"], 1)
        self.assertEqual(stats["dynamic_detections"], 1)
        
        # Prüfe Signale
        self.assertEqual(len(self.state_changes), 2)
        self.assertEqual(len(self.statistics_updates), 1)
        self.assertEqual(len(self.events), 2)
        self.assertEqual(self.events[1].type, "detection_update")

    def test_avoidance_maneuver(self):
        """Teste die Ausweichmanöver."""
        self.viewmodel.activate()
        
        # Führe ein Ausweichmanöver aus
        self.viewmodel.execute_avoidance("stop")
        
        # Prüfe Properties
        self.assertEqual(self.viewmodel.current_strategy, "stop")
        self.assertFalse(self.viewmodel.avoidance_in_progress)
        
        # Prüfe Statistiken
        stats = self.viewmodel.statistics
        self.assertEqual(stats["avoidance_maneuvers"], 1)
        self.assertEqual(stats["successful_avoidance"], 1)
        
        # Prüfe Signale
        self.assertEqual(len(self.state_changes), 2)
        self.assertEqual(len(self.avoidance_starts), 1)
        self.assertEqual(len(self.avoidance_completions), 1)
        self.assertEqual(len(self.events), 2)
        self.assertEqual(self.events[0].type, "avoidance_start")
        self.assertEqual(self.events[1].type, "avoidance_complete")

    def test_invalid_avoidance_strategy(self):
        """Teste ungültige Ausweichstrategien."""
        self.viewmodel.activate()
        
        # Versuche eine ungültige Strategie
        self.viewmodel.execute_avoidance("invalid_strategy")
        
        # Prüfe Fehler
        self.assertEqual(len(self.errors), 1)
        self.assertTrue("ungültige Strategie" in self.errors[0].lower())

    def test_error_handling(self):
        """Teste die Fehlerbehandlung."""
        # Simuliere einen Fehler
        self.viewmodel._on_error_occurred("Test error")
        
        # Prüfe Properties
        self.assertTrue(self.viewmodel.is_error)
        self.assertEqual(self.viewmodel.error_message, "Test error")
        
        # Prüfe Signale
        self.assertEqual(len(self.errors), 1)
        self.assertEqual(len(self.events), 1)
        self.assertEqual(self.events[0].type, "error")

    def test_log_events(self):
        """Teste die Log-Ereignisse."""
        self.viewmodel.activate()
        self.viewmodel.deactivate()
        
        # Prüfe Log-Ereignisse
        events = self.viewmodel.log_events
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0]["type"], "activation")
        self.assertEqual(events[1]["type"], "deactivation")

if __name__ == '__main__':
    unittest.main() 