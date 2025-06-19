"""Systemtests für die autonomen Flugmodi."""

import unittest
import time
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

class TestAutonomousSystem(unittest.TestCase):
    """Testfälle für das autonome Flugmodi-System."""
    
    @classmethod
    def setUpClass(cls):
        """Testumgebung vorbereiten."""
        cls.app = QCoreApplication([])
        cls.engine = QQmlApplicationEngine()
    
    def setUp(self):
        """Testumgebung vorbereiten."""
        self.service = AutonomousService()
        self.viewmodel = AutonomousViewModel(self.service)
    
    def test_end_to_end_scenario(self):
        """Test eines End-to-End-Szenarios."""
        # 1. Service aktivieren
        self.service.activate()
        self.assertTrue(self.service._state.is_active)
        self.assertEqual(self.service._state.mode, AutonomousMode.POSITION_HOLD)
        self.assertEqual(self.service._state.status, AutonomousStatus.ACTIVE)
        
        # 2. Position Hold Modus
        # Position setzen
        position = {"lat": 48.123, "lon": 11.456, "alt": 100.0}
        self.service.update_position(position)
        self.assertEqual(self.service._state.position, position)
        
        # Kurs setzen
        self.service.update_course(90.0)
        self.assertEqual(self.service._state.course, 90.0)
        
        # Geschwindigkeit setzen
        self.service.update_speed(5.0)
        self.assertEqual(self.service._state.speed, 5.0)
        
        # Höhe setzen
        self.service.update_altitude(100.0)
        self.assertEqual(self.service._state.altitude, 100.0)
        
        # 3. RTL Modus
        self.service.set_mode(AutonomousMode.RTL)
        self.assertEqual(self.service._state.mode, AutonomousMode.RTL)
        self.assertEqual(self.service._statistics.mode_changes, 1)
        
        # Startposition setzen
        start_position = {"lat": 48.123, "lon": 11.456, "alt": 0.0}
        self.service.set_start_position(start_position)
        
        # Position aktualisieren
        current_position = {"lat": 48.124, "lon": 11.457, "alt": 50.0}
        self.service.update_position(current_position)
        
        # Fortschritt aktualisieren
        self.service.update_progress(0.5)
        self.assertEqual(self.service._state.progress, 0.5)
        
        # Verbleibende Zeit aktualisieren
        self.service.update_remaining_time(300.0)
        self.assertEqual(self.service._state.remaining_time, 300.0)
        
        # Verbleibende Distanz aktualisieren
        self.service.update_remaining_distance(500.0)
        self.assertEqual(self.service._state.remaining_distance, 500.0)
        
        # 4. Service deaktivieren
        self.service.deactivate()
        self.assertFalse(self.service._state.is_active)
        self.assertEqual(self.service._state.status, AutonomousStatus.INACTIVE)
        
        # 5. Ergebnisse überprüfen
        self.assertFalse(self.service._state.is_error)
        self.assertIsNone(self.service._state.error_message)
        self.assertGreater(self.service._statistics.total_distance, 0.0)
        self.assertGreater(self.service._statistics.max_speed, 0.0)
        self.assertGreater(self.service._statistics.total_commands, 0)
        self.assertGreater(self.service._statistics.successful_commands, 0)
        self.assertEqual(self.service._statistics.failed_commands, 0)
        self.assertEqual(self.service._statistics.total_errors, 0)
        self.assertGreater(self.service._statistics.mode_changes, 0)
    
    def test_error_scenarios(self):
        """Test von Fehlerszenarien."""
        # 1. Aktivierung im Fehlerzustand
        self.service._state.is_error = True
        self.service._state.error_message = "Test error"
        self.service.activate()
        self.assertTrue(self.service._state.is_error)
        self.assertEqual(self.service._state.error_message, "Test error")
        
        # 2. Ungültiger Modus
        self.service._reset_error()
        self.service.activate()
        with self.assertRaises(AutonomousValidationError):
            self.service.set_mode("INVALID")
        
        # 3. Ungültige Position
        with self.assertRaises(AutonomousValidationError):
            self.service.update_position(None)
        
        # 4. Ungültiger Kurs
        with self.assertRaises(AutonomousValidationError):
            self.service.update_course(-1.0)
        
        # 5. Ungültige Geschwindigkeit
        with self.assertRaises(AutonomousValidationError):
            self.service.update_speed(-1.0)
        
        # 6. Ungültige Höhe
        with self.assertRaises(AutonomousValidationError):
            self.service.update_altitude(-1.0)
        
        # 7. Ungültiger Fortschritt
        with self.assertRaises(AutonomousValidationError):
            self.service.update_progress(1.5)
        
        # 8. Ungültige verbleibende Zeit
        with self.assertRaises(AutonomousValidationError):
            self.service.update_remaining_time(-1.0)
        
        # 9. Ungültige verbleibende Distanz
        with self.assertRaises(AutonomousValidationError):
            self.service.update_remaining_distance(-1.0)
    
    def test_performance(self):
        """Test der Performance."""
        # 1. Service aktivieren
        self.service.activate()
        
        # 2. Performance messen
        start_time = time.time()
        
        # Position Hold Modus
        for i in range(100):
            # Position aktualisieren
            position = {
                "lat": 48.123 + i * 0.001,
                "lon": 11.456 + i * 0.001,
                "alt": 100.0 + i * 0.1
            }
            self.service.update_position(position)
            
            # Kurs aktualisieren
            self.service.update_course(i * 1.0)
            
            # Geschwindigkeit aktualisieren
            self.service.update_speed(i * 0.1)
            
            # Höhe aktualisieren
            self.service.update_altitude(100.0 + i * 0.1)
            
            # Fortschritt aktualisieren
            self.service.update_progress(i / 100.0)
            
            # Verbleibende Zeit aktualisieren
            self.service.update_remaining_time(300.0 - i * 3.0)
            
            # Verbleibende Distanz aktualisieren
            self.service.update_remaining_distance(1000.0 - i * 10.0)
        
        end_time = time.time()
        
        # 3. Ergebnisse überprüfen
        total_time = end_time - start_time
        self.assertLess(total_time, 1.0)  # Sollte weniger als 1 Sekunde dauern
        self.assertGreater(self.service._statistics.total_commands, 0)
        self.assertGreater(self.service._statistics.successful_commands, 0)
        self.assertEqual(self.service._statistics.failed_commands, 0)
        self.assertEqual(self.service._statistics.total_errors, 0)
    
    def test_concurrent_operations(self):
        """Test von gleichzeitigen Operationen."""
        # 1. Service aktivieren
        self.service.activate()
        
        # 2. Gleichzeitige Operationen
        for _ in range(100):
            # Position aktualisieren
            self.service.update_position({"lat": 48.123, "lon": 11.456, "alt": 100.0})
            
            # Kurs aktualisieren
            self.service.update_course(90.0)
            
            # Geschwindigkeit aktualisieren
            self.service.update_speed(10.0)
            
            # Höhe aktualisieren
            self.service.update_altitude(100.0)
            
            # Fortschritt aktualisieren
            self.service.update_progress(0.5)
            
            # Verbleibende Zeit aktualisieren
            self.service.update_remaining_time(300.0)
            
            # Verbleibende Distanz aktualisieren
            self.service.update_remaining_distance(1000.0)
        
        # 3. Service deaktivieren
        self.service.deactivate()
        
        # 4. Ergebnisse überprüfen
        self.assertFalse(self.service._state.is_error)
        self.assertIsNone(self.service._state.error_message)
        self.assertGreater(self.service._statistics.total_commands, 0)
        self.assertGreater(self.service._statistics.successful_commands, 0)
        self.assertEqual(self.service._statistics.failed_commands, 0)
        self.assertEqual(self.service._statistics.total_errors, 0)
    
    def test_recovery_scenarios(self):
        """Test von Wiederherstellungsszenarien."""
        # 1. Service aktivieren
        self.service.activate()
        
        # 2. Fehler simulieren
        self.service._handle_error("Test error")
        self.assertTrue(self.service._state.is_error)
        self.assertEqual(self.service._state.error_message, "Test error")
        
        # 3. Wiederherstellung
        self.service._reset_error()
        self.assertFalse(self.service._state.is_error)
        self.assertIsNone(self.service._state.error_message)
        
        # 4. Service wiederherstellen
        self.service.activate()
        self.assertTrue(self.service._state.is_active)
        self.assertEqual(self.service._state.status, AutonomousStatus.ACTIVE)
        
        # 5. Daten aktualisieren
        self.service.update_position({"lat": 48.123, "lon": 11.456, "alt": 100.0})
        self.assertFalse(self.service._state.is_error)
        self.assertIsNone(self.service._state.error_message)
        
        # 6. Service deaktivieren
        self.service.deactivate()
        
        # 7. Ergebnisse überprüfen
        self.assertFalse(self.service._state.is_error)
        self.assertIsNone(self.service._state.error_message)
        self.assertEqual(self.service._state.status, AutonomousStatus.INACTIVE)

if __name__ == "__main__":
    unittest.main() 