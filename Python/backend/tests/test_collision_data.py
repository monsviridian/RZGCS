"""
Unit Tests für die Datenmodelle der Kollisionsvermeidung.
"""

import unittest
from datetime import datetime
from flight_control.models.collision_data import (
    ObjectType,
    DetectionMethod,
    AvoidanceStrategy,
    DetectedObject,
    CollisionState,
    CollisionStatistics,
    CollisionEvent,
    CollisionLog,
    CollisionError,
    DetectionError,
    AvoidanceError,
    StrategyError
)

class TestCollisionData(unittest.TestCase):
    """Testfälle für die Datenmodelle der Kollisionsvermeidung."""

    def test_object_types(self):
        """Teste die Objekttypen."""
        self.assertEqual(ObjectType.STATIC.value, "static")
        self.assertEqual(ObjectType.DYNAMIC.value, "dynamic")
        self.assertEqual(ObjectType.UNKNOWN.value, "unknown")

    def test_detection_methods(self):
        """Teste die Erkennungsmethoden."""
        self.assertEqual(DetectionMethod.LIDAR.value, "lidar")
        self.assertEqual(DetectionMethod.RADAR.value, "radar")
        self.assertEqual(DetectionMethod.CAMERA.value, "camera")
        self.assertEqual(DetectionMethod.FUSION.value, "fusion")

    def test_avoidance_strategies(self):
        """Teste die Ausweichstrategien."""
        self.assertEqual(AvoidanceStrategy.STOP.value, "stop")
        self.assertEqual(AvoidanceStrategy.HOVER.value, "hover")
        self.assertEqual(AvoidanceStrategy.ALTITUDE.value, "altitude")
        self.assertEqual(AvoidanceStrategy.LATERAL.value, "lateral")
        self.assertEqual(AvoidanceStrategy.COMBINED.value, "combined")

    def test_detected_object(self):
        """Teste die DetectedObject-Klasse."""
        # Erstelle ein Testobjekt
        obj = DetectedObject(
            id="test1",
            type=ObjectType.STATIC,
            position={"lat": 48.123, "lon": 11.456, "alt": 100.0},
            velocity={"vx": 0.0, "vy": 0.0, "vz": 0.0},
            size={"length": 5.0, "width": 3.0, "height": 2.0},
            confidence=0.95,
            detection_method=DetectionMethod.LIDAR
        )

        # Teste die Attribute
        self.assertEqual(obj.id, "test1")
        self.assertEqual(obj.type, ObjectType.STATIC)
        self.assertEqual(obj.position["lat"], 48.123)
        self.assertEqual(obj.position["lon"], 11.456)
        self.assertEqual(obj.position["alt"], 100.0)
        self.assertEqual(obj.velocity["vx"], 0.0)
        self.assertEqual(obj.velocity["vy"], 0.0)
        self.assertEqual(obj.velocity["vz"], 0.0)
        self.assertEqual(obj.size["length"], 5.0)
        self.assertEqual(obj.size["width"], 3.0)
        self.assertEqual(obj.size["height"], 2.0)
        self.assertEqual(obj.confidence, 0.95)
        self.assertEqual(obj.detection_method, DetectionMethod.LIDAR)
        self.assertIsInstance(obj.timestamp, datetime)

    def test_collision_state(self):
        """Teste die CollisionState-Klasse."""
        # Erstelle einen Testzustand
        state = CollisionState(
            is_active=True,
            is_error=False,
            error_message=None,
            detected_objects=[],
            current_strategy=None,
            avoidance_in_progress=False
        )

        # Teste die Attribute
        self.assertTrue(state.is_active)
        self.assertFalse(state.is_error)
        self.assertIsNone(state.error_message)
        self.assertEqual(len(state.detected_objects), 0)
        self.assertIsNone(state.current_strategy)
        self.assertFalse(state.avoidance_in_progress)
        self.assertIsInstance(state.last_update, datetime)

    def test_collision_statistics(self):
        """Teste die CollisionStatistics-Klasse."""
        # Erstelle Teststatistiken
        stats = CollisionStatistics(
            total_detections=10,
            static_detections=5,
            dynamic_detections=3,
            unknown_detections=2,
            avoidance_maneuvers=4,
            successful_avoidance=3,
            failed_avoidance=1,
            average_response_time=50.0
        )

        # Teste die Attribute
        self.assertEqual(stats.total_detections, 10)
        self.assertEqual(stats.static_detections, 5)
        self.assertEqual(stats.dynamic_detections, 3)
        self.assertEqual(stats.unknown_detections, 2)
        self.assertEqual(stats.avoidance_maneuvers, 4)
        self.assertEqual(stats.successful_avoidance, 3)
        self.assertEqual(stats.failed_avoidance, 1)
        self.assertEqual(stats.average_response_time, 50.0)
        self.assertIsInstance(stats.last_update, datetime)

    def test_collision_event(self):
        """Teste die CollisionEvent-Klasse."""
        # Erstelle ein Testereignis
        event = CollisionEvent(
            type="test_event",
            description="Test Event",
            severity="info",
            data={"key": "value"}
        )

        # Teste die Attribute
        self.assertEqual(event.type, "test_event")
        self.assertEqual(event.description, "Test Event")
        self.assertEqual(event.severity, "info")
        self.assertEqual(event.data["key"], "value")
        self.assertIsInstance(event.timestamp, datetime)

    def test_collision_log(self):
        """Teste die CollisionLog-Klasse."""
        # Erstelle ein Testlog
        log = CollisionLog(max_events=2)

        # Füge Ereignisse hinzu
        event1 = CollisionEvent("event1", "Event 1", "info")
        event2 = CollisionEvent("event2", "Event 2", "info")
        event3 = CollisionEvent("event3", "Event 3", "info")

        log.add_event(event1)
        log.add_event(event2)
        log.add_event(event3)

        # Teste die Größenbegrenzung
        self.assertEqual(len(log.events), 2)
        self.assertEqual(log.events[0].type, "event2")
        self.assertEqual(log.events[1].type, "event3")

    def test_error_classes(self):
        """Teste die Fehlerklassen."""
        # Teste CollisionError
        with self.assertRaises(CollisionError):
            raise CollisionError("Test error")

        # Teste DetectionError
        with self.assertRaises(DetectionError):
            raise DetectionError("Detection error")

        # Teste AvoidanceError
        with self.assertRaises(AvoidanceError):
            raise AvoidanceError("Avoidance error")

        # Teste StrategyError
        with self.assertRaises(StrategyError):
            raise StrategyError("Strategy error")

if __name__ == '__main__':
    unittest.main() 