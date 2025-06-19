"""Unit-Tests für das Flugsteuerungs-ViewModel.

Diese Tests überprüfen die Funktionalität des Flugsteuerungs-ViewModels:
- Service-Integration
- UI-Zustandsverwaltung
- Benutzerinteraktionen
- Datenaktualisierungen
- Fehlerbehandlung
"""

import unittest
from datetime import datetime
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
    """Tests für FlightControlViewModel."""
    
    def setUp(self):
        """Test-Setup."""
        self.service = FlightControlService()
        self.viewmodel = FlightControlViewModel()
        self.viewmodel.set_service(self.service)
    
    def test_initial_state(self):
        """Teste Initialzustand."""
        self.assertFalse(self.viewmodel.is_active)
        self.assertFalse(self.viewmodel.is_error)
        self.assertEqual(self.viewmodel.error_message, "")
        self.assertEqual(self.viewmodel.mode, FlightMode.STABILIZE.value)
        self.assertEqual(self.viewmodel.status, FlightStatus.INACTIVE.value)
        self.assertFalse(self.viewmodel.is_armed)
        self.assertFalse(self.viewmodel.is_flying)
        self.assertFalse(self.viewmodel.is_landing)
        self.assertFalse(self.viewmodel.is_taking_off)
    
    def test_activate(self):
        """Teste Aktivierung."""
        self.viewmodel.activate()
        
        self.assertTrue(self.viewmodel.is_active)
        self.assertEqual(self.viewmodel.status, FlightStatus.READY.value)
    
    def test_deactivate(self):
        """Teste Deaktivierung."""
        self.viewmodel.activate()
        self.viewmodel.deactivate()
        
        self.assertFalse(self.viewmodel.is_active)
        self.assertEqual(self.viewmodel.status, FlightStatus.INACTIVE.value)
    
    def test_arm(self):
        """Teste Arming."""
        self.viewmodel.activate()
        self.viewmodel.arm()
        
        self.assertTrue(self.viewmodel.is_armed)
        self.assertEqual(self.viewmodel.status, FlightStatus.ARMED.value)
    
    def test_disarm(self):
        """Teste Disarming."""
        self.viewmodel.activate()
        self.viewmodel.arm()
        self.viewmodel.disarm()
        
        self.assertFalse(self.viewmodel.is_armed)
        self.assertEqual(self.viewmodel.status, FlightStatus.READY.value)
    
    def test_set_mode(self):
        """Teste Moduswechsel."""
        self.viewmodel.activate()
        self.viewmodel.set_mode(FlightMode.ALTHOLD.value)
        
        self.assertEqual(self.viewmodel.mode, FlightMode.ALTHOLD.value)
    
    def test_takeoff(self):
        """Teste Start."""
        self.viewmodel.activate()
        self.viewmodel.arm()
        self.viewmodel.takeoff()
        
        self.assertTrue(self.viewmodel.is_taking_off)
        self.assertEqual(self.viewmodel.status, FlightStatus.TAKING_OFF.value)
    
    def test_land(self):
        """Teste Landung."""
        self.viewmodel.activate()
        self.viewmodel.arm()
        self.viewmodel.takeoff()
        self.viewmodel.land()
        
        self.assertTrue(self.viewmodel.is_landing)
        self.assertEqual(self.viewmodel.status, FlightStatus.LANDING.value)
    
    def test_update_position(self):
        """Teste Positionsaktualisierung."""
        position = {
            'latitude': 48.137154,
            'longitude': 11.576124,
            'altitude': 100.0
        }
        
        self.viewmodel.activate()
        self.viewmodel.update_position(position)
        
        # Hier könnten weitere Assertions für die Positionsaktualisierung hinzugefügt werden
    
    def test_update_velocity(self):
        """Teste Geschwindigkeitsaktualisierung."""
        velocity = {
            'vx': 10.0,
            'vy': 0.0,
            'vz': 0.0
        }
        
        self.viewmodel.activate()
        self.viewmodel.update_velocity(velocity)
        
        # Hier könnten weitere Assertions für die Geschwindigkeitsaktualisierung hinzugefügt werden
    
    def test_statistics(self):
        """Teste Statistiken."""
        self.viewmodel.activate()
        self.viewmodel.arm()
        self.viewmodel.takeoff()
        self.viewmodel.land()
        self.viewmodel.disarm()
        
        self.assertEqual(self.viewmodel.total_flights, "1")
        self.assertEqual(self.viewmodel.total_landings, "1")
        self.assertEqual(self.viewmodel.total_takeoffs, "1")
    
    def test_logging(self):
        """Teste Logging."""
        self.viewmodel.activate()
        self.viewmodel.arm()
        self.viewmodel.takeoff()
        self.viewmodel.land()
        self.viewmodel.disarm()
        
        self.assertGreater(len(self.viewmodel.log_events), 0)
        self.assertNotEqual(self.viewmodel.last_event, "")
    
    def test_validation_errors(self):
        """Teste Validierungsfehler."""
        # Teste Arming ohne Aktivierung
        with self.assertRaises(FlightValidationError):
            self.viewmodel.arm()
        
        # Teste Start ohne Arming
        with self.assertRaises(FlightValidationError):
            self.viewmodel.takeoff()
        
        # Teste Landung ohne Flug
        with self.assertRaises(FlightValidationError):
            self.viewmodel.land()
    
    def test_command_errors(self):
        """Teste Befehlsfehler."""
        # Teste Deaktivierung ohne Aktivierung
        with self.assertRaises(FlightCommandError):
            self.viewmodel.deactivate()
        
        # Teste Disarming ohne Arming
        with self.assertRaises(FlightCommandError):
            self.viewmodel.disarm()
    
    def test_mode_errors(self):
        """Teste Modusfehler."""
        # Teste ungültigen Modus
        with self.assertRaises(FlightModeError):
            self.viewmodel.set_mode("INVALID")
    
    def test_error_handling(self):
        """Teste Fehlerbehandlung."""
        # Simuliere einen Fehler
        self.service._state.update(
            is_error=True,
            error_message="Test Error",
            status=FlightStatus.ERROR
        )
        
        self.assertTrue(self.viewmodel.is_error)
        self.assertEqual(self.viewmodel.error_message, "Test Error")
        self.assertEqual(self.viewmodel.status, FlightStatus.ERROR.value)

if __name__ == '__main__':
    unittest.main() 