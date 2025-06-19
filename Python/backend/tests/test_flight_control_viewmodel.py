"""Unit-Tests für das Flugsteuerungs-ViewModel."""

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
from flight_control.viewmodels.flight_control_viewmodel import FlightControlViewModel

class TestFlightControlViewModel(unittest.TestCase):
    """Testfälle für das Flugsteuerungs-ViewModel."""
    
    def setUp(self):
        """Testumgebung vorbereiten."""
        self.service = FlightControlService()
        self.viewmodel = FlightControlViewModel(self.service)
    
    def test_initial_state(self):
        """Test des initialen Zustands."""
        # ViewModel-Status
        self.assertFalse(self.viewmodel.is_active)
        self.assertFalse(self.viewmodel.is_error)
        self.assertEqual(self.viewmodel.error_message, "")
        self.assertEqual(self.viewmodel.mode, FlightMode.MANUAL.value)
        self.assertEqual(self.viewmodel.status, FlightStatus.DISARMED.value)
        self.assertFalse(self.viewmodel.is_armed)
        self.assertFalse(self.viewmodel.is_flying)
        self.assertEqual(self.viewmodel.last_update, "")
        
        # Statistiken
        self.assertEqual(self.viewmodel.total_flight_time, "0.0")
        self.assertEqual(self.viewmodel.total_distance, "0.0")
        self.assertEqual(self.viewmodel.max_altitude, "0.0")
        self.assertEqual(self.viewmodel.max_speed, "0.0")
        self.assertEqual(self.viewmodel.total_commands, "0")
        self.assertEqual(self.viewmodel.successful_commands, "0")
        self.assertEqual(self.viewmodel.failed_commands, "0")
        self.assertEqual(self.viewmodel.total_errors, "0")
        self.assertEqual(self.viewmodel.mode_changes, "0")
        self.assertEqual(self.viewmodel.status_changes, "0")
        
        # Log
        self.assertEqual(len(self.viewmodel.log_events), 0)
    
    def test_activation(self):
        """Test der Aktivierung."""
        # ViewModel aktivieren
        self.viewmodel.activate()
        
        # Überprüfung
        self.assertTrue(self.viewmodel.is_active)
        self.assertFalse(self.viewmodel.is_error)
        self.assertEqual(self.viewmodel.error_message, "")
        self.assertEqual(self.viewmodel.mode, FlightMode.MANUAL.value)
        self.assertEqual(self.viewmodel.status, FlightStatus.DISARMED.value)
        self.assertFalse(self.viewmodel.is_armed)
        self.assertFalse(self.viewmodel.is_flying)
        self.assertNotEqual(self.viewmodel.last_update, "")
        
        # Log überprüfen
        self.assertEqual(len(self.viewmodel.log_events), 1)
        self.assertEqual(self.viewmodel.log_events[0]["type"], "ACTIVATION")
    
    def test_deactivation(self):
        """Test der Deaktivierung."""
        # ViewModel aktivieren und deaktivieren
        self.viewmodel.activate()
        self.viewmodel.deactivate()
        
        # Überprüfung
        self.assertFalse(self.viewmodel.is_active)
        self.assertFalse(self.viewmodel.is_error)
        self.assertEqual(self.viewmodel.error_message, "")
        
        # Log überprüfen
        self.assertEqual(len(self.viewmodel.log_events), 2)
        self.assertEqual(self.viewmodel.log_events[1]["type"], "DEACTIVATION")
    
    def test_arming(self):
        """Test des Arming."""
        # ViewModel aktivieren und armen
        self.viewmodel.activate()
        self.viewmodel.arm()
        
        # Überprüfung
        self.assertTrue(self.viewmodel.is_armed)
        self.assertEqual(self.viewmodel.status, FlightStatus.ARMED.value)
        
        # Log überprüfen
        self.assertEqual(len(self.viewmodel.log_events), 2)
        self.assertEqual(self.viewmodel.log_events[1]["type"], "ARMING")
    
    def test_disarming(self):
        """Test des Disarming."""
        # ViewModel aktivieren, armen und disarmen
        self.viewmodel.activate()
        self.viewmodel.arm()
        self.viewmodel.disarm()
        
        # Überprüfung
        self.assertFalse(self.viewmodel.is_armed)
        self.assertEqual(self.viewmodel.status, FlightStatus.DISARMED.value)
        
        # Log überprüfen
        self.assertEqual(len(self.viewmodel.log_events), 3)
        self.assertEqual(self.viewmodel.log_events[2]["type"], "DISARMING")
    
    def test_mode_changes(self):
        """Test der Modusänderungen."""
        # ViewModel aktivieren
        self.viewmodel.activate()
        
        # Modus ändern
        self.viewmodel.set_mode(FlightMode.STABILIZE.value)
        
        # Überprüfung
        self.assertEqual(self.viewmodel.mode, FlightMode.STABILIZE.value)
        self.assertEqual(self.viewmodel.mode_changes, "1")
        
        # Log überprüfen
        self.assertEqual(len(self.viewmodel.log_events), 2)
        self.assertEqual(self.viewmodel.log_events[1]["type"], "MODE_CHANGE")
        
        # Ungültiger Modus
        with self.assertRaises(FlightValidationError):
            self.viewmodel.set_mode("INVALID")
    
    def test_takeoff(self):
        """Test des Takeoffs."""
        # ViewModel aktivieren und armen
        self.viewmodel.activate()
        self.viewmodel.arm()
        
        # Takeoff durchführen
        self.viewmodel.takeoff(10.0)  # 10m Höhe
        
        # Überprüfung
        self.assertTrue(self.viewmodel.is_flying)
        self.assertEqual(self.viewmodel.status, FlightStatus.TAKEOFF.value)
        
        # Log überprüfen
        self.assertEqual(len(self.viewmodel.log_events), 3)
        self.assertEqual(self.viewmodel.log_events[2]["type"], "TAKEOFF")
    
    def test_landing(self):
        """Test der Landung."""
        # ViewModel aktivieren, armen und takeoff
        self.viewmodel.activate()
        self.viewmodel.arm()
        self.viewmodel.takeoff(10.0)
        
        # Landen
        self.viewmodel.land()
        
        # Überprüfung
        self.assertFalse(self.viewmodel.is_flying)
        self.assertEqual(self.viewmodel.status, FlightStatus.LANDING.value)
        
        # Log überprüfen
        self.assertEqual(len(self.viewmodel.log_events), 4)
        self.assertEqual(self.viewmodel.log_events[3]["type"], "LANDING")
    
    def test_error_handling(self):
        """Test der Fehlerbehandlung."""
        # ViewModel aktivieren
        self.viewmodel.activate()
        
        # Fehler simulieren
        self.viewmodel._handle_error("Test error")
        
        # Überprüfung
        self.assertTrue(self.viewmodel.is_error)
        self.assertEqual(self.viewmodel.error_message, "Test error")
        self.assertEqual(self.viewmodel.total_errors, "1")
        
        # Log überprüfen
        self.assertEqual(len(self.viewmodel.log_events), 2)
        self.assertEqual(self.viewmodel.log_events[1]["type"], "ERROR")
        
        # Fehler zurücksetzen
        self.viewmodel._reset_error()
        
        # Überprüfung
        self.assertFalse(self.viewmodel.is_error)
        self.assertEqual(self.viewmodel.error_message, "")
    
    def test_statistics_updates(self):
        """Test der Statistikaktualisierungen."""
        # ViewModel aktivieren
        self.viewmodel.activate()
        
        # Statistiken aktualisieren
        self.service._statistics.total_flight_time = 3600.0
        self.service._statistics.total_distance = 10000.0
        self.service._statistics.max_altitude = 100.0
        self.service._statistics.max_speed = 20.0
        self.service._statistics.total_commands = 100
        self.service._statistics.successful_commands = 95
        self.service._statistics.failed_commands = 5
        self.service._statistics.total_errors = 3
        self.service._statistics.mode_changes = 10
        self.service._statistics.status_changes = 5
        
        # Statistiken aktualisieren
        self.viewmodel._update_statistics()
        
        # Überprüfung
        self.assertEqual(self.viewmodel.total_flight_time, "3600.0")
        self.assertEqual(self.viewmodel.total_distance, "10000.0")
        self.assertEqual(self.viewmodel.max_altitude, "100.0")
        self.assertEqual(self.viewmodel.max_speed, "20.0")
        self.assertEqual(self.viewmodel.total_commands, "100")
        self.assertEqual(self.viewmodel.successful_commands, "95")
        self.assertEqual(self.viewmodel.failed_commands, "5")
        self.assertEqual(self.viewmodel.total_errors, "3")
        self.assertEqual(self.viewmodel.mode_changes, "10")
        self.assertEqual(self.viewmodel.status_changes, "5")
    
    def test_log_updates(self):
        """Test der Log-Aktualisierungen."""
        # ViewModel aktivieren
        self.viewmodel.activate()
        
        # Events hinzufügen
        event1 = FlightEvent(
            timestamp=datetime.now(),
            event_type="MODE_CHANGE",
            description="Mode changed to STABILIZE",
            data={"old_mode": "MANUAL", "new_mode": "STABILIZE"}
        )
        self.service._log.add_event(event1)
        
        event2 = FlightEvent(
            timestamp=datetime.now(),
            event_type="STATUS_CHANGE",
            description="Status changed to ARMED",
            data={"old_status": "DISARMED", "new_status": "ARMED"}
        )
        self.service._log.add_event(event2)
        
        # Log aktualisieren
        self.viewmodel._update_log()
        
        # Überprüfung
        self.assertEqual(len(self.viewmodel.log_events), 3)  # 2 Events + Aktivierung
        self.assertEqual(self.viewmodel.log_events[1]["type"], "MODE_CHANGE")
        self.assertEqual(self.viewmodel.log_events[2]["type"], "STATUS_CHANGE")
    
    def test_inactive_operations(self):
        """Test von Operationen im inaktiven Zustand."""
        # Ungültige Operationen
        with self.assertRaises(FlightCommandError):
            self.viewmodel.arm()
        
        with self.assertRaises(FlightCommandError):
            self.viewmodel.disarm()
        
        with self.assertRaises(FlightCommandError):
            self.viewmodel.set_mode(FlightMode.STABILIZE.value)
        
        with self.assertRaises(FlightCommandError):
            self.viewmodel.takeoff(10.0)
        
        with self.assertRaises(FlightCommandError):
            self.viewmodel.land()
        
        # Überprüfung
        self.assertFalse(self.viewmodel.is_active)
        self.assertFalse(self.viewmodel.is_error)
        self.assertEqual(self.viewmodel.error_message, "")
        self.assertEqual(self.viewmodel.mode, FlightMode.MANUAL.value)
        self.assertEqual(self.viewmodel.status, FlightStatus.DISARMED.value)
        self.assertFalse(self.viewmodel.is_armed)
        self.assertFalse(self.viewmodel.is_flying)
        self.assertEqual(self.viewmodel.last_update, "")
        
        # Log überprüfen
        self.assertEqual(len(self.viewmodel.log_events), 0)

if __name__ == "__main__":
    unittest.main() 