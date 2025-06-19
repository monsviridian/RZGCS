"""Integrationstests für die autonomen Flugmodi."""

import unittest
from datetime import datetime
from PySide6.QtCore import QObject, Signal, Slot, QTimer, QCoreApplication
from PySide6.QtQml import QQmlApplicationEngine
from flight_control.models.autonomous_data import (
    AutonomousMode,
    AutonomousStatus,
    AutonomousState,
    AutonomousStatistics,
    AutonomousEvent,
    AutonomousLog,
    AutonomousError,
    AutonomousValidationError,
    AutonomousCommandError,
    AutonomousModeError
)
from flight_control.services.autonomous_service import AutonomousService
from flight_control.viewmodels.autonomous_viewmodel import AutonomousViewModel

class MockView(QObject):
    """Mock-View für die Integrationstests."""
    
    # Signale
    modeChanged = Signal(str)
    statusChanged = Signal(str)
    positionChanged = Signal(float, float, float)
    courseChanged = Signal(float)
    speedChanged = Signal(float)
    altitudeChanged = Signal(float)
    progressChanged = Signal(float)
    remainingTimeChanged = Signal(float)
    remainingDistanceChanged = Signal(float)
    statisticsChanged = Signal()
    logChanged = Signal()
    errorChanged = Signal(str)
    
    def __init__(self):
        """Initialisierung."""
        super().__init__()
        self.mode = AutonomousMode.POSITION_HOLD.value
        self.status = AutonomousStatus.INACTIVE.value
        self.position = {"lat": 0.0, "lon": 0.0, "alt": 0.0}
        self.course = 0.0
        self.speed = 0.0
        self.altitude = 0.0
        self.progress = 0.0
        self.remaining_time = 0.0
        self.remaining_distance = 0.0
        self.statistics = {}
        self.log_events = []
        self.error_message = ""
    
    @Slot(str)
    def set_mode(self, mode):
        """Modus setzen."""
        self.mode = mode
        self.modeChanged.emit(mode)
    
    @Slot(str)
    def set_status(self, status):
        """Status setzen."""
        self.status = status
        self.statusChanged.emit(status)
    
    @Slot(float, float, float)
    def set_position(self, lat, lon, alt):
        """Position setzen."""
        self.position = {"lat": lat, "lon": lon, "alt": alt}
        self.positionChanged.emit(lat, lon, alt)
    
    @Slot(float)
    def set_course(self, course):
        """Kurs setzen."""
        self.course = course
        self.courseChanged.emit(course)
    
    @Slot(float)
    def set_speed(self, speed):
        """Geschwindigkeit setzen."""
        self.speed = speed
        self.speedChanged.emit(speed)
    
    @Slot(float)
    def set_altitude(self, altitude):
        """Höhe setzen."""
        self.altitude = altitude
        self.altitudeChanged.emit(altitude)
    
    @Slot(float)
    def set_progress(self, progress):
        """Fortschritt setzen."""
        self.progress = progress
        self.progressChanged.emit(progress)
    
    @Slot(float)
    def set_remaining_time(self, time):
        """Verbleibende Zeit setzen."""
        self.remaining_time = time
        self.remainingTimeChanged.emit(time)
    
    @Slot(float)
    def set_remaining_distance(self, distance):
        """Verbleibende Distanz setzen."""
        self.remaining_distance = distance
        self.remainingDistanceChanged.emit(distance)
    
    @Slot()
    def update_statistics(self):
        """Statistiken aktualisieren."""
        self.statisticsChanged.emit()
    
    @Slot()
    def update_log(self):
        """Log aktualisieren."""
        self.logChanged.emit()
    
    @Slot(str)
    def set_error(self, message):
        """Fehler setzen."""
        self.error_message = message
        self.errorChanged.emit(message)

class TestAutonomousIntegration(unittest.TestCase):
    """Testfälle für die Integration der autonomen Flugmodi."""
    
    @classmethod
    def setUpClass(cls):
        """Testumgebung vorbereiten."""
        cls.app = QCoreApplication([])
        cls.engine = QQmlApplicationEngine()
    
    def setUp(self):
        """Testumgebung vorbereiten."""
        self.service = AutonomousService()
        self.viewmodel = AutonomousViewModel(self.service)
        self.view = MockView()
        
        # Signale verbinden
        self.viewmodel.modeChanged.connect(self.view.set_mode)
        self.viewmodel.statusChanged.connect(self.view.set_status)
        self.viewmodel.positionChanged.connect(self.view.set_position)
        self.viewmodel.courseChanged.connect(self.view.set_course)
        self.viewmodel.speedChanged.connect(self.view.set_speed)
        self.viewmodel.altitudeChanged.connect(self.view.set_altitude)
        self.viewmodel.progressChanged.connect(self.view.set_progress)
        self.viewmodel.remainingTimeChanged.connect(self.view.set_remaining_time)
        self.viewmodel.remainingDistanceChanged.connect(self.view.set_remaining_distance)
        self.viewmodel.statisticsChanged.connect(self.view.update_statistics)
        self.viewmodel.logChanged.connect(self.view.update_log)
        self.viewmodel.errorChanged.connect(self.view.set_error)
    
    def test_activation_flow(self):
        """Test des Aktivierungsflusses."""
        # Service aktivieren
        self.service.activate()
        
        # Überprüfung
        self.assertTrue(self.service._state.is_active)
        self.assertEqual(self.service._state.mode, AutonomousMode.POSITION_HOLD)
        self.assertEqual(self.service._state.status, AutonomousStatus.ACTIVE)
        
        # ViewModel überprüfen
        self.assertTrue(self.viewmodel.is_active)
        self.assertEqual(self.viewmodel.mode, AutonomousMode.POSITION_HOLD.value)
        self.assertEqual(self.viewmodel.status, AutonomousStatus.ACTIVE.value)
        
        # View überprüfen
        self.assertEqual(self.view.mode, AutonomousMode.POSITION_HOLD.value)
        self.assertEqual(self.view.status, AutonomousStatus.ACTIVE.value)
    
    def test_deactivation_flow(self):
        """Test des Deaktivierungsflusses."""
        # Service aktivieren und deaktivieren
        self.service.activate()
        self.service.deactivate()
        
        # Überprüfung
        self.assertFalse(self.service._state.is_active)
        self.assertEqual(self.service._state.status, AutonomousStatus.INACTIVE)
        
        # ViewModel überprüfen
        self.assertFalse(self.viewmodel.is_active)
        self.assertEqual(self.viewmodel.status, AutonomousStatus.INACTIVE.value)
        
        # View überprüfen
        self.assertEqual(self.view.status, AutonomousStatus.INACTIVE.value)
    
    def test_mode_change_flow(self):
        """Test des Modusänderungsflusses."""
        # Service aktivieren
        self.service.activate()
        
        # Modus ändern
        self.service.set_mode(AutonomousMode.RTL)
        
        # Überprüfung
        self.assertEqual(self.service._state.mode, AutonomousMode.RTL)
        self.assertEqual(self.service._statistics.mode_changes, 1)
        
        # ViewModel überprüfen
        self.assertEqual(self.viewmodel.mode, AutonomousMode.RTL.value)
        
        # View überprüfen
        self.assertEqual(self.view.mode, AutonomousMode.RTL.value)
    
    def test_position_update_flow(self):
        """Test des Positionsaktualisierungsflusses."""
        # Service aktivieren
        self.service.activate()
        
        # Position aktualisieren
        position = {"lat": 48.123, "lon": 11.456, "alt": 100.0}
        self.service.update_position(position)
        
        # Überprüfung
        self.assertEqual(self.service._state.position, position)
        
        # ViewModel überprüfen
        self.assertEqual(self.viewmodel.position["lat"], 48.123)
        self.assertEqual(self.viewmodel.position["lon"], 11.456)
        self.assertEqual(self.viewmodel.position["alt"], 100.0)
        
        # View überprüfen
        self.assertEqual(self.view.position["lat"], 48.123)
        self.assertEqual(self.view.position["lon"], 11.456)
        self.assertEqual(self.view.position["alt"], 100.0)
    
    def test_course_update_flow(self):
        """Test des Kursaktualisierungsflusses."""
        # Service aktivieren
        self.service.activate()
        
        # Kurs aktualisieren
        self.service.update_course(90.0)
        
        # Überprüfung
        self.assertEqual(self.service._state.course, 90.0)
        
        # ViewModel überprüfen
        self.assertEqual(self.viewmodel.course, 90.0)
        
        # View überprüfen
        self.assertEqual(self.view.course, 90.0)
    
    def test_speed_update_flow(self):
        """Test des Geschwindigkeitsaktualisierungsflusses."""
        # Service aktivieren
        self.service.activate()
        
        # Geschwindigkeit aktualisieren
        self.service.update_speed(10.0)
        
        # Überprüfung
        self.assertEqual(self.service._state.speed, 10.0)
        
        # ViewModel überprüfen
        self.assertEqual(self.viewmodel.speed, 10.0)
        
        # View überprüfen
        self.assertEqual(self.view.speed, 10.0)
    
    def test_altitude_update_flow(self):
        """Test des Höhenaktualisierungsflusses."""
        # Service aktivieren
        self.service.activate()
        
        # Höhe aktualisieren
        self.service.update_altitude(50.0)
        
        # Überprüfung
        self.assertEqual(self.service._state.altitude, 50.0)
        
        # ViewModel überprüfen
        self.assertEqual(self.viewmodel.altitude, 50.0)
        
        # View überprüfen
        self.assertEqual(self.view.altitude, 50.0)
    
    def test_progress_update_flow(self):
        """Test des Fortschrittsaktualisierungsflusses."""
        # Service aktivieren
        self.service.activate()
        
        # Fortschritt aktualisieren
        self.service.update_progress(0.5)
        
        # Überprüfung
        self.assertEqual(self.service._state.progress, 0.5)
        
        # ViewModel überprüfen
        self.assertEqual(self.viewmodel.progress, 0.5)
        
        # View überprüfen
        self.assertEqual(self.view.progress, 0.5)
    
    def test_remaining_time_update_flow(self):
        """Test des Aktualisierungsflusses für verbleibende Zeit."""
        # Service aktivieren
        self.service.activate()
        
        # Verbleibende Zeit aktualisieren
        self.service.update_remaining_time(300.0)
        
        # Überprüfung
        self.assertEqual(self.service._state.remaining_time, 300.0)
        
        # ViewModel überprüfen
        self.assertEqual(self.viewmodel.remaining_time, 300.0)
        
        # View überprüfen
        self.assertEqual(self.view.remaining_time, 300.0)
    
    def test_remaining_distance_update_flow(self):
        """Test des Aktualisierungsflusses für verbleibende Distanz."""
        # Service aktivieren
        self.service.activate()
        
        # Verbleibende Distanz aktualisieren
        self.service.update_remaining_distance(1000.0)
        
        # Überprüfung
        self.assertEqual(self.service._state.remaining_distance, 1000.0)
        
        # ViewModel überprüfen
        self.assertEqual(self.viewmodel.remaining_distance, 1000.0)
        
        # View überprüfen
        self.assertEqual(self.view.remaining_distance, 1000.0)
    
    def test_statistics_update_flow(self):
        """Test des Statistikaktualisierungsflusses."""
        # Service aktivieren
        self.service.activate()
        
        # Statistiken aktualisieren
        self.service._statistics.total_distance = 10000.0
        self.service._statistics.max_speed = 20.0
        self.service._statistics.total_commands = 100
        self.service._statistics.successful_commands = 95
        
        # Statistiken aktualisieren
        self.viewmodel._update_statistics()
        
        # View überprüfen
        self.view.update_statistics()
        self.assertIsNotNone(self.view.statistics)
    
    def test_log_update_flow(self):
        """Test des Log-Aktualisierungsflusses."""
        # Service aktivieren
        self.service.activate()
        
        # Events hinzufügen
        event = AutonomousEvent(
            timestamp=datetime.now(),
            event_type="MODE_CHANGE",
            description="Mode changed to RTL",
            data={"old_mode": "POSITION_HOLD", "new_mode": "RTL"}
        )
        self.service._log.add_event(event)
        
        # Log aktualisieren
        self.viewmodel._update_log()
        
        # View überprüfen
        self.view.update_log()
        self.assertEqual(len(self.view.log_events), 2)  # 1 Event + Aktivierung
    
    def test_error_flow(self):
        """Test des Fehlerflusses."""
        # Service aktivieren
        self.service.activate()
        
        # Fehler simulieren
        self.service._handle_error("Test error")
        
        # Überprüfung
        self.assertTrue(self.service._state.is_error)
        self.assertEqual(self.service._state.error_message, "Test error")
        
        # ViewModel überprüfen
        self.assertTrue(self.viewmodel.is_error)
        self.assertEqual(self.viewmodel.error_message, "Test error")
        
        # View überprüfen
        self.assertEqual(self.view.error_message, "Test error")

if __name__ == "__main__":
    unittest.main() 