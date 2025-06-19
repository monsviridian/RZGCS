"""
Integrationstests für die Kollisionsvermeidung.

Diese Tests prüfen die Interaktion zwischen Service, ViewModel und View.
"""

import unittest
from datetime import datetime
from PySide6.QtCore import QCoreApplication, QObject, Signal, Slot
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

class MockView(QObject):
    """Mock-View für die Integrationstests."""
    
    # Signale
    activation_requested = Signal()
    deactivation_requested = Signal()
    avoidance_requested = Signal(str)
    
    # Slots
    @Slot(bool)
    def update_active_state(self, is_active: bool) -> None:
        """Aktualisiere den Aktivitätsstatus."""
        self._is_active = is_active
    
    @Slot(bool)
    def update_error_state(self, is_error: bool) -> None:
        """Aktualisiere den Fehlerstatus."""
        self._is_error = is_error
    
    @Slot(str)
    def update_error_message(self, message: str) -> None:
        """Aktualisiere die Fehlermeldung."""
        self._error_message = message
    
    @Slot(list)
    def update_detected_objects(self, objects: list) -> None:
        """Aktualisiere die erkannten Objekte."""
        self._detected_objects = objects
    
    @Slot(str)
    def update_current_strategy(self, strategy: str) -> None:
        """Aktualisiere die aktuelle Strategie."""
        self._current_strategy = strategy
    
    @Slot(bool)
    def update_avoidance_progress(self, in_progress: bool) -> None:
        """Aktualisiere den Fortschritt des Ausweichmanövers."""
        self._avoidance_in_progress = in_progress
    
    @Slot(dict)
    def update_statistics(self, statistics: dict) -> None:
        """Aktualisiere die Statistiken."""
        self._statistics = statistics
    
    @Slot(list)
    def update_log_events(self, events: list) -> None:
        """Aktualisiere die Log-Ereignisse."""
        self._log_events = events

class TestCollisionIntegration(unittest.TestCase):
    """Testfälle für die Integration der Kollisionsvermeidung."""

    @classmethod
    def setUpClass(cls):
        """Initialisiere die Testumgebung."""
        cls.app = QCoreApplication([])
        cls.engine = QQmlApplicationEngine()

    def setUp(self):
        """Initialisiere jeden Testfall."""
        self.service = CollisionService()
        self.viewmodel = CollisionViewModel()
        self.view = MockView()
        
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
        
        # Verbinde ViewModel mit View
        self.viewmodel.state_changed.connect(self.view.update_active_state)
        self.viewmodel.state_changed.connect(self.view.update_error_state)
        self.viewmodel.error_occurred.connect(self.view.update_error_message)
        self.viewmodel.object_detected.connect(self.view.update_detected_objects)
        self.viewmodel.strategy_changed.connect(self.view.update_current_strategy)
        self.viewmodel.avoidance_started.connect(self.view.update_avoidance_progress)
        self.viewmodel.statistics_updated.connect(self.view.update_statistics)
        self.viewmodel.log_updated.connect(self.view.update_log_events)
        
        # Verbinde View mit ViewModel
        self.view.activation_requested.connect(self.viewmodel.activate)
        self.view.deactivation_requested.connect(self.viewmodel.deactivate)
        self.view.avoidance_requested.connect(self.viewmodel.execute_avoidance)

    def test_activation_flow(self):
        """Teste den Aktivierungsfluss."""
        # Simuliere Aktivierungsanfrage von der View
        self.view.activation_requested.emit()
        
        # Prüfe Service
        self.assertTrue(self.service._state.is_active)
        
        # Prüfe ViewModel
        self.assertTrue(self.viewmodel.is_active)
        
        # Prüfe View
        self.assertTrue(self.view._is_active)

    def test_deactivation_flow(self):
        """Teste den Deaktivierungsfluss."""
        # Aktiviere zuerst
        self.service.activate()
        
        # Simuliere Deaktivierungsanfrage von der View
        self.view.deactivation_requested.emit()
        
        # Prüfe Service
        self.assertFalse(self.service._state.is_active)
        
        # Prüfe ViewModel
        self.assertFalse(self.viewmodel.is_active)
        
        # Prüfe View
        self.assertFalse(self.view._is_active)

    def test_object_detection_flow(self):
        """Teste den Objekterkennungsfluss."""
        # Aktiviere zuerst
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
            )
        ]
        
        # Aktualisiere Objekte im Service
        self.service.update_detected_objects(objects)
        
        # Prüfe Service
        self.assertEqual(len(self.service._state.detected_objects), 1)
        
        # Prüfe ViewModel
        self.assertEqual(len(self.viewmodel.detected_objects), 1)
        
        # Prüfe View
        self.assertEqual(len(self.view._detected_objects), 1)

    def test_avoidance_flow(self):
        """Teste den Ausweichmanöver-Fluss."""
        # Aktiviere zuerst
        self.service.activate()
        
        # Simuliere Ausweichanfrage von der View
        self.view.avoidance_requested.emit("stop")
        
        # Prüfe Service
        self.assertEqual(self.service._state.current_strategy, AvoidanceStrategy.STOP)
        
        # Prüfe ViewModel
        self.assertEqual(self.viewmodel.current_strategy, "stop")
        
        # Prüfe View
        self.assertEqual(self.view._current_strategy, "stop")

    def test_error_flow(self):
        """Teste den Fehlerfluss."""
        # Simuliere einen Fehler im Service
        self.service._handle_error("Test error")
        
        # Prüfe Service
        self.assertTrue(self.service._state.is_error)
        self.assertEqual(self.service._state.error_message, "Test error")
        
        # Prüfe ViewModel
        self.assertTrue(self.viewmodel.is_error)
        self.assertEqual(self.viewmodel.error_message, "Test error")
        
        # Prüfe View
        self.assertTrue(self.view._is_error)
        self.assertEqual(self.view._error_message, "Test error")

    def test_statistics_flow(self):
        """Teste den Statistikfluss."""
        # Aktiviere zuerst
        self.service.activate()
        
        # Führe einige Aktionen aus
        self.service.execute_avoidance(AvoidanceStrategy.STOP)
        
        # Prüfe Service
        self.assertEqual(self.service._statistics.avoidance_maneuvers, 1)
        
        # Prüfe ViewModel
        self.assertEqual(self.viewmodel.statistics["avoidance_maneuvers"], 1)
        
        # Prüfe View
        self.assertEqual(self.view._statistics["avoidance_maneuvers"], 1)

    def test_log_flow(self):
        """Teste den Log-Fluss."""
        # Aktiviere und deaktiviere
        self.service.activate()
        self.service.deactivate()
        
        # Prüfe Service
        self.assertEqual(len(self.service._log.events), 2)
        
        # Prüfe ViewModel
        self.assertEqual(len(self.viewmodel.log_events), 2)
        
        # Prüfe View
        self.assertEqual(len(self.view._log_events), 2)

if __name__ == '__main__':
    unittest.main() 