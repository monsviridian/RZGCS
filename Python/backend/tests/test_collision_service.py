"""
Unit Tests für den Service der Kollisionsvermeidung.
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
from flight_control.services.collision_service import CollisionService

class TestCollisionService(unittest.TestCase):
    """Testfälle für den Service der Kollisionsvermeidung."""

    @classmethod
    def setUpClass(cls):
        """Initialisiere die Testumgebung."""
        cls.app = QCoreApplication([])

    def setUp(self):
        """Initialisiere jeden Testfall."""
        self.service = CollisionService()
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
        self.service.state_changed.connect(lambda state: self.state_changes.append(state))
        self.service.object_detected.connect(lambda obj: self.object_detections.append(obj))
        self.service.strategy_changed.connect(lambda strategy: self.strategy_changes.append(strategy))
        self.service.avoidance_started.connect(lambda strategy: self.avoidance_starts.append(strategy))
        self.service.avoidance_completed.connect(lambda success: self.avoidance_completions.append(success))
        self.service.error_occurred.connect(lambda error: self.errors.append(error))
        self.service.event_occurred.connect(lambda event: self.events.append(event))
        self.service.statistics_updated.connect(lambda stats: self.statistics_updates.append(stats))
        self.service.log_updated.connect(lambda log: self.log_updates.append(log))

    def test_initial_state(self):
        """Teste den initialen Zustand."""
        self.assertFalse(self.service._state.is_active)
        self.assertFalse(self.service._state.is_error)
        self.assertIsNone(self.service._state.error_message)
        self.assertEqual(len(self.service._state.detected_objects), 0)
        self.assertIsNone(self.service._state.current_strategy)
        self.assertFalse(self.service._state.avoidance_in_progress)

    def test_activation(self):
        """Teste die Aktivierung."""
        self.service.activate()
        
        self.assertTrue(self.service._state.is_active)
        self.assertFalse(self.service._state.is_error)
        self.assertIsNone(self.service._state.error_message)
        
        # Prüfe Signale
        self.assertEqual(len(self.state_changes), 1)
        self.assertEqual(len(self.events), 1)
        self.assertEqual(self.events[0].type, "activation")

    def test_deactivation(self):
        """Teste die Deaktivierung."""
        self.service.activate()
        self.service.deactivate()
        
        self.assertFalse(self.service._state.is_active)
        self.assertFalse(self.service._state.is_error)
        self.assertIsNone(self.service._state.error_message)
        self.assertIsNone(self.service._state.current_strategy)
        self.assertFalse(self.service._state.avoidance_in_progress)
        
        # Prüfe Signale
        self.assertEqual(len(self.state_changes), 2)
        self.assertEqual(len(self.events), 2)
        self.assertEqual(self.events[1].type, "deactivation")

    def test_object_detection(self):
        """Teste die Objekterkennung."""
        self.service.activate()
        
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
        
        self.service.update_detected_objects(objects)
        
        # Prüfe Zustand
        self.assertEqual(len(self.service._state.detected_objects), 2)
        
        # Prüfe Statistiken
        self.assertEqual(self.service._statistics.total_detections, 2)
        self.assertEqual(self.service._statistics.static_detections, 1)
        self.assertEqual(self.service._statistics.dynamic_detections, 1)
        
        # Prüfe Signale
        self.assertEqual(len(self.state_changes), 2)
        self.assertEqual(len(self.statistics_updates), 1)
        self.assertEqual(len(self.events), 2)
        self.assertEqual(self.events[1].type, "detection_update")

    def test_avoidance_maneuver(self):
        """Teste die Ausweichmanöver."""
        self.service.activate()
        
        # Führe ein Ausweichmanöver aus
        self.service.execute_avoidance(AvoidanceStrategy.STOP)
        
        # Prüfe Zustand
        self.assertEqual(self.service._state.current_strategy, AvoidanceStrategy.STOP)
        self.assertFalse(self.service._state.avoidance_in_progress)
        
        # Prüfe Statistiken
        self.assertEqual(self.service._statistics.avoidance_maneuvers, 1)
        self.assertEqual(self.service._statistics.successful_avoidance, 1)
        
        # Prüfe Signale
        self.assertEqual(len(self.state_changes), 2)
        self.assertEqual(len(self.avoidance_starts), 1)
        self.assertEqual(len(self.avoidance_completions), 1)
        self.assertEqual(len(self.events), 2)
        self.assertEqual(self.events[0].type, "avoidance_start")
        self.assertEqual(self.events[1].type, "avoidance_complete")

    def test_error_handling(self):
        """Teste die Fehlerbehandlung."""
        # Simuliere einen Fehler
        self.service._handle_error("Test error")
        
        # Prüfe Zustand
        self.assertTrue(self.service._state.is_error)
        self.assertEqual(self.service._state.error_message, "Test error")
        
        # Prüfe Signale
        self.assertEqual(len(self.state_changes), 1)
        self.assertEqual(len(self.errors), 1)
        self.assertEqual(len(self.events), 1)
        self.assertEqual(self.events[0].type, "error")

    def test_inactive_operations(self):
        """Teste Operationen im inaktiven Zustand."""
        # Versuche Objekte zu aktualisieren
        objects = [
            DetectedObject(
                id="test1",
                type=ObjectType.STATIC,
                position={"lat": 48.123, "lon": 11.456, "alt": 100.0},
                velocity={"vx": 0.0, "vy": 0.0, "vz": 0.0},
                size={"length": 5.0, "width": 3.0, "height": 2.0},
                confidence=0.95,
                detection_method=DetectionMethod.LIDAR
            )
        ]
        
        self.service.update_detected_objects(objects)
        
        # Prüfe, dass keine Änderungen vorgenommen wurden
        self.assertEqual(len(self.service._state.detected_objects), 0)
        self.assertEqual(len(self.state_changes), 0)
        self.assertEqual(len(self.events), 0)

if __name__ == '__main__':
    unittest.main() 