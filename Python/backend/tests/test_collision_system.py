"""
Systemtests für die Kollisionsvermeidung.

Diese Tests prüfen das Gesamtsystem unter realen Bedingungen,
einschließlich End-to-End-Szenarien, Fehlerszenarien und Performance-Tests.
"""

import unittest
import time
from datetime import datetime
from PySide6.QtCore import QCoreApplication, QTimer
from PySide6.QtQml import QQmlApplicationEngine
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
from flight_control.viewmodels.collision_viewmodel import CollisionViewModel

class TestCollisionSystem(unittest.TestCase):
    """Testfälle für das Gesamtsystem der Kollisionsvermeidung."""

    @classmethod
    def setUpClass(cls):
        """Initialisiere die Testumgebung."""
        cls.app = QCoreApplication([])
        cls.engine = QQmlApplicationEngine()

    def setUp(self):
        """Initialisiere jeden Testfall."""
        self.service = CollisionService()
        self.viewmodel = CollisionViewModel()
        
        # Verbinde Service mit ViewModel
        self.service.state_changed.connect(self.viewmodel._on_state_changed)
        self.service.object_detected.connect(self.viewmodel._on_object_detected)
        self.service.strategy_changed.connect(self.viewmodel._on_strategy_changed)
        self.service.avoidance_started.connect(self.viewmodel._on_avoidance_started)
        self.service.avoidance_completed.connect(self.viewmodel._on_avoidance_completed)
        self.service.error_occurred.connect(self.viewmodel._on_error_occurred)
        self.service.event_occurred.connect(self.viewmodel._on_event_occurred)
        self.service.statistics_updated.connect(self.viewmodel._on_statistics_updated)
        self.service.log_updated.connect(self.viewmodel._on_log_updated)
        
        # Initialisiere Testvariablen
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

    def test_end_to_end_scenario(self):
        """Teste ein vollständiges End-to-End-Szenario."""
        # 1. Aktiviere das System
        self.service.activate()
        self.assertTrue(self.service._state.is_active)
        self.assertTrue(self.viewmodel.is_active)
        
        # 2. Simuliere Objekterkennung
        objects = [
            DetectedObject(
                id="static1",
                type=ObjectType.STATIC,
                position={"lat": 48.123, "lon": 11.456, "alt": 100.0},
                velocity={"vx": 0.0, "vy": 0.0, "vz": 0.0},
                size={"length": 5.0, "width": 3.0, "height": 2.0},
                confidence=0.95,
                detection_method=DetectionMethod.LIDAR
            ),
            DetectedObject(
                id="dynamic1",
                type=ObjectType.DYNAMIC,
                position={"lat": 48.124, "lon": 11.457, "alt": 101.0},
                velocity={"vx": 1.0, "vy": 1.0, "vz": 0.0},
                size={"length": 2.0, "width": 2.0, "height": 1.0},
                confidence=0.85,
                detection_method=DetectionMethod.RADAR
            )
        ]
        self.service.update_detected_objects(objects)
        
        # 3. Prüfe Objekterkennung
        self.assertEqual(len(self.service._state.detected_objects), 2)
        self.assertEqual(len(self.viewmodel.detected_objects), 2)
        
        # 4. Führe Ausweichmanöver aus
        self.service.execute_avoidance(AvoidanceStrategy.STOP)
        
        # 5. Prüfe Ausweichmanöver
        self.assertEqual(self.service._state.current_strategy, AvoidanceStrategy.STOP)
        self.assertEqual(self.viewmodel.current_strategy, "stop")
        
        # 6. Prüfe Statistiken
        self.assertEqual(self.service._statistics.total_detections, 2)
        self.assertEqual(self.service._statistics.avoidance_maneuvers, 1)
        self.assertEqual(self.service._statistics.successful_avoidance, 1)
        
        # 7. Deaktiviere das System
        self.service.deactivate()
        self.assertFalse(self.service._state.is_active)
        self.assertFalse(self.viewmodel.is_active)
        
        # 8. Prüfe Log
        self.assertEqual(len(self.service._log.events), 4)  # activation, detection, avoidance, deactivation

    def test_error_scenarios(self):
        """Teste verschiedene Fehlerszenarien."""
        # 1. Teste Aktivierung im Fehlerzustand
        self.service._handle_error("Test error")
        self.service.activate()
        self.assertTrue(self.service._state.is_error)
        self.assertEqual(self.service._state.error_message, "Test error")
        
        # 2. Teste ungültige Objekterkennung
        self.service._state.is_error = False
        self.service._state.error_message = None
        self.service.activate()
        self.service.update_detected_objects([])  # Leere Liste sollte keinen Fehler verursachen
        
        # 3. Teste ungültige Ausweichstrategie
        with self.assertRaises(ValueError):
            self.service.execute_avoidance("invalid_strategy")
        
        # 4. Teste Ausweichmanöver im inaktiven Zustand
        self.service.deactivate()
        self.service.execute_avoidance(AvoidanceStrategy.STOP)
        self.assertIsNone(self.service._state.current_strategy)

    def test_performance(self):
        """Teste die Performance des Systems."""
        # 1. Aktiviere das System
        self.service.activate()
        
        # 2. Messung der Objekterkennungs-Performance
        start_time = time.time()
        for _ in range(100):
            objects = [
                DetectedObject(
                    id=f"obj_{_}",
                    type=ObjectType.STATIC,
                    position={"lat": 48.123, "lon": 11.456, "alt": 100.0},
                    velocity={"vx": 0.0, "vy": 0.0, "vz": 0.0},
                    size={"length": 5.0, "width": 3.0, "height": 2.0},
                    confidence=0.95,
                    detection_method=DetectionMethod.LIDAR
                )
            ]
            self.service.update_detected_objects(objects)
        end_time = time.time()
        
        # Prüfe Verarbeitungszeit
        processing_time = end_time - start_time
        self.assertLess(processing_time, 1.0)  # Sollte weniger als 1 Sekunde dauern
        
        # 3. Messung der Ausweichmanöver-Performance
        start_time = time.time()
        for _ in range(10):
            self.service.execute_avoidance(AvoidanceStrategy.STOP)
        end_time = time.time()
        
        # Prüfe Verarbeitungszeit
        processing_time = end_time - start_time
        self.assertLess(processing_time, 0.5)  # Sollte weniger als 0.5 Sekunden dauern

    def test_concurrent_operations(self):
        """Teste gleichzeitige Operationen."""
        # 1. Aktiviere das System
        self.service.activate()
        
        # 2. Simuliere gleichzeitige Objekterkennung und Ausweichmanöver
        def update_objects():
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
        
        def execute_avoidance():
            self.service.execute_avoidance(AvoidanceStrategy.STOP)
        
        # Führe Operationen in schneller Folge aus
        for _ in range(10):
            update_objects()
            execute_avoidance()
        
        # Prüfe Systemzustand
        self.assertTrue(self.service._state.is_active)
        self.assertFalse(self.service._state.is_error)
        self.assertEqual(self.service._state.current_strategy, AvoidanceStrategy.STOP)

    def test_recovery_scenarios(self):
        """Teste Wiederherstellungsszenarien."""
        # 1. Teste Wiederherstellung nach Fehler
        self.service._handle_error("Test error")
        self.service.activate()
        self.assertFalse(self.service._state.is_error)
        self.assertIsNone(self.service._state.error_message)
        
        # 2. Teste Wiederherstellung nach Ausweichmanöver
        self.service.execute_avoidance(AvoidanceStrategy.STOP)
        self.service.deactivate()
        self.service.activate()
        self.assertIsNone(self.service._state.current_strategy)
        self.assertFalse(self.service._state.avoidance_in_progress)
        
        # 3. Teste Wiederherstellung nach Objekterkennung
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
        self.service.deactivate()
        self.service.activate()
        self.assertEqual(len(self.service._state.detected_objects), 0)

if __name__ == '__main__':
    unittest.main() 