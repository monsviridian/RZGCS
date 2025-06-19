"""Unit-Tests für den Flugsteuerungs-Service."""

import unittest
from datetime import datetime
from PySide6.QtCore import QObject, Signal, Slot, QTimer
from flight_control.models.flight_control_data import (
    FlightMode,
    FlightStatus,
    FlightState,
    FlightStatistics,
    FlightEvent,
    FlightLog,
    FlightError,
    FlightValidationError,
    FlightCommandError,
    FlightModeError
)
from flight_control.services.flight_control_service import FlightControlService

class TestFlightControlService(unittest.TestCase):
    """Testfälle für den Flugsteuerungs-Service."""
    
    def setUp(self):
        """Testumgebung vorbereiten."""
        self.service = FlightControlService()
    
    def test_initial_state(self):
        """Test des initialen Zustands."""
        # Service-Status
        self.assertFalse(self.service._state.is_active)
        self.assertFalse(self.service._state.is_error)
        self.assertIsNone(self.service._state.error_message)
        self.assertEqual(self.service._state.mode, FlightMode.MANUAL)
        self.assertEqual(self.service._state.status, FlightStatus.DISARMED)
        self.assertFalse(self.service._state.is_armed)
        self.assertFalse(self.service._state.is_flying)
        self.assertIsNone(self.service._state.last_update)
        
        # Statistiken
        self.assertEqual(self.service._statistics.total_flight_time, 0.0)
        self.assertEqual(self.service._statistics.total_distance, 0.0)
        self.assertEqual(self.service._statistics.max_altitude, 0.0)
        self.assertEqual(self.service._statistics.max_speed, 0.0)
        self.assertEqual(self.service._statistics.total_commands, 0)
        self.assertEqual(self.service._statistics.successful_commands, 0)
        self.assertEqual(self.service._statistics.failed_commands, 0)
        self.assertEqual(self.service._statistics.total_errors, 0)
        self.assertEqual(self.service._statistics.mode_changes, 0)
        self.assertEqual(self.service._statistics.status_changes, 0)
        
        # Log
        self.assertEqual(len(self.service._log.events), 0)
        self.assertIsNone(self.service._log.last_event)
    
    def test_activation(self):
        """Test der Aktivierung."""
        # Service aktivieren
        self.service.activate()
        
        # Überprüfung
        self.assertTrue(self.service._state.is_active)
        self.assertFalse(self.service._state.is_error)
        self.assertIsNone(self.service._state.error_message)
        self.assertEqual(self.service._state.mode, FlightMode.MANUAL)
        self.assertEqual(self.service._state.status, FlightStatus.DISARMED)
        self.assertFalse(self.service._state.is_armed)
        self.assertFalse(self.service._state.is_flying)
        self.assertIsNotNone(self.service._state.last_update)
        
        # Log überprüfen
        self.assertEqual(len(self.service._log.events), 1)
        self.assertEqual(self.service._log.last_event.event_type, "ACTIVATION")
    
    def test_deactivation(self):
        """Test der Deaktivierung."""
        # Service aktivieren und deaktivieren
        self.service.activate()
        self.service.deactivate()
        
        # Überprüfung
        self.assertFalse(self.service._state.is_active)
        self.assertFalse(self.service._state.is_error)
        self.assertIsNone(self.service._state.error_message)
        
        # Log überprüfen
        self.assertEqual(len(self.service._log.events), 2)
        self.assertEqual(self.service._log.last_event.event_type, "DEACTIVATION")
    
    def test_arming(self):
        """Test des Arming."""
        # Service aktivieren und armen
        self.service.activate()
        self.service.arm()
        
        # Überprüfung
        self.assertTrue(self.service._state.is_armed)
        self.assertEqual(self.service._state.status, FlightStatus.ARMED)
        
        # Log überprüfen
        self.assertEqual(len(self.service._log.events), 2)
        self.assertEqual(self.service._log.last_event.event_type, "ARMING")
    
    def test_disarming(self):
        """Test des Disarming."""
        # Service aktivieren, armen und disarmen
        self.service.activate()
        self.service.arm()
        self.service.disarm()
        
        # Überprüfung
        self.assertFalse(self.service._state.is_armed)
        self.assertEqual(self.service._state.status, FlightStatus.DISARMED)
        
        # Log überprüfen
        self.assertEqual(len(self.service._log.events), 3)
        self.assertEqual(self.service._log.last_event.event_type, "DISARMING")
    
    def test_mode_changes(self):
        """Test der Modusänderungen."""
        # Service aktivieren
        self.service.activate()
        
        # Modus ändern
        self.service.set_mode(FlightMode.STABILIZE)
        
        # Überprüfung
        self.assertEqual(self.service._state.mode, FlightMode.STABILIZE)
        self.assertEqual(self.service._statistics.mode_changes, 1)
        
        # Log überprüfen
        self.assertEqual(len(self.service._log.events), 2)
        self.assertEqual(self.service._log.last_event.event_type, "MODE_CHANGE")
        
        # Ungültiger Modus
        with self.assertRaises(FlightValidationError):
            self.service.set_mode("INVALID")
    
    def test_takeoff(self):
        """Test des Takeoffs."""
        # Service aktivieren und armen
        self.service.activate()
        self.service.arm()
        
        # Takeoff durchführen
        self.service.takeoff(10.0)  # 10m Höhe
        
        # Überprüfung
        self.assertTrue(self.service._state.is_flying)
        self.assertEqual(self.service._state.status, FlightStatus.TAKEOFF)
        
        # Log überprüfen
        self.assertEqual(len(self.service._log.events), 3)
        self.assertEqual(self.service._log.last_event.event_type, "TAKEOFF")
    
    def test_landing(self):
        """Test der Landung."""
        # Service aktivieren, armen und takeoff
        self.service.activate()
        self.service.arm()
        self.service.takeoff(10.0)
        
        # Landen
        self.service.land()
        
        # Überprüfung
        self.assertFalse(self.service._state.is_flying)
        self.assertEqual(self.service._state.status, FlightStatus.LANDING)
        
        # Log überprüfen
        self.assertEqual(len(self.service._log.events), 4)
        self.assertEqual(self.service._log.last_event.event_type, "LANDING")
    
    def test_error_handling(self):
        """Test der Fehlerbehandlung."""
        # Service aktivieren
        self.service.activate()
        
        # Fehler simulieren
        self.service._handle_error("Test error")
        
        # Überprüfung
        self.assertTrue(self.service._state.is_error)
        self.assertEqual(self.service._state.error_message, "Test error")
        self.assertEqual(self.service._statistics.total_errors, 1)
        
        # Log überprüfen
        self.assertEqual(len(self.service._log.events), 2)
        self.assertEqual(self.service._log.last_event.event_type, "ERROR")
        
        # Fehler zurücksetzen
        self.service._reset_error()
        
        # Überprüfung
        self.assertFalse(self.service._state.is_error)
        self.assertIsNone(self.service._state.error_message)
    
    def test_inactive_operations(self):
        """Test von Operationen im inaktiven Zustand."""
        # Ungültige Operationen
        with self.assertRaises(FlightCommandError):
            self.service.arm()
        
        with self.assertRaises(FlightCommandError):
            self.service.disarm()
        
        with self.assertRaises(FlightCommandError):
            self.service.set_mode(FlightMode.STABILIZE)
        
        with self.assertRaises(FlightCommandError):
            self.service.takeoff(10.0)
        
        with self.assertRaises(FlightCommandError):
            self.service.land()
        
        # Überprüfung
        self.assertFalse(self.service._state.is_active)
        self.assertFalse(self.service._state.is_error)
        self.assertIsNone(self.service._state.error_message)
        self.assertEqual(self.service._state.mode, FlightMode.MANUAL)
        self.assertEqual(self.service._state.status, FlightStatus.DISARMED)
        self.assertFalse(self.service._state.is_armed)
        self.assertFalse(self.service._state.is_flying)
        self.assertIsNone(self.service._state.last_update)
        
        # Log überprüfen
        self.assertEqual(len(self.service._log.events), 0)
        self.assertIsNone(self.service._log.last_event)

if __name__ == "__main__":
    unittest.main() 