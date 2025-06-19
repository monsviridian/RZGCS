"""Unit-Tests für den Flugsteuerungs-Service.

Diese Tests überprüfen die Funktionalität des Flugsteuerungs-Services:
- Aktivierung/Deaktivierung
- Arming/Disarming
- Moduswechsel
- Start/Landung
- Positionsaktualisierungen
- Geschwindigkeitsaktualisierungen
- Statistiken
- Logging
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

class TestFlightControlService(unittest.TestCase):
    """Tests für FlightControlService."""
    
    def setUp(self):
        """Test-Setup."""
        self.service = FlightControlService()
    
    def test_initial_state(self):
        """Teste Initialzustand."""
        self.assertFalse(self.service._state.is_active)
        self.assertFalse(self.service._state.is_error)
        self.assertIsNone(self.service._state.error_message)
        self.assertEqual(self.service._state.mode, FlightMode.STABILIZE)
        self.assertEqual(self.service._state.status, FlightStatus.INACTIVE)
        self.assertFalse(self.service._state.is_armed)
        self.assertFalse(self.service._state.is_flying)
        self.assertFalse(self.service._state.is_landing)
        self.assertFalse(self.service._state.is_taking_off)
    
    def test_activate(self):
        """Teste Aktivierung."""
        self.service.activate()
        
        self.assertTrue(self.service._state.is_active)
        self.assertEqual(self.service._state.status, FlightStatus.READY)
    
    def test_deactivate(self):
        """Teste Deaktivierung."""
        self.service.activate()
        self.service.deactivate()
        
        self.assertFalse(self.service._state.is_active)
        self.assertEqual(self.service._state.status, FlightStatus.INACTIVE)
    
    def test_arm(self):
        """Teste Arming."""
        self.service.activate()
        self.service.arm()
        
        self.assertTrue(self.service._state.is_armed)
        self.assertEqual(self.service._state.status, FlightStatus.ARMED)
    
    def test_disarm(self):
        """Teste Disarming."""
        self.service.activate()
        self.service.arm()
        self.service.disarm()
        
        self.assertFalse(self.service._state.is_armed)
        self.assertEqual(self.service._state.status, FlightStatus.READY)
    
    def test_set_mode(self):
        """Teste Moduswechsel."""
        self.service.activate()
        self.service.set_mode(FlightMode.ALTHOLD)
        
        self.assertEqual(self.service._state.mode, FlightMode.ALTHOLD)
    
    def test_takeoff(self):
        """Teste Start."""
        self.service.activate()
        self.service.arm()
        self.service.takeoff()
        
        self.assertTrue(self.service._state.is_taking_off)
        self.assertEqual(self.service._state.status, FlightStatus.TAKING_OFF)
    
    def test_land(self):
        """Teste Landung."""
        self.service.activate()
        self.service.arm()
        self.service.takeoff()
        self.service.land()
        
        self.assertTrue(self.service._state.is_landing)
        self.assertEqual(self.service._state.status, FlightStatus.LANDING)
    
    def test_update_position(self):
        """Teste Positionsaktualisierung."""
        position = {
            'latitude': 48.137154,
            'longitude': 11.576124,
            'altitude': 100.0
        }
        
        self.service.activate()
        self.service.update_position(position)
        
        # Hier könnten weitere Assertions für die Positionsaktualisierung hinzugefügt werden
    
    def test_update_velocity(self):
        """Teste Geschwindigkeitsaktualisierung."""
        velocity = {
            'vx': 10.0,
            'vy': 0.0,
            'vz': 0.0
        }
        
        self.service.activate()
        self.service.update_velocity(velocity)
        
        # Hier könnten weitere Assertions für die Geschwindigkeitsaktualisierung hinzugefügt werden
    
    def test_statistics(self):
        """Teste Statistiken."""
        self.service.activate()
        self.service.arm()
        self.service.takeoff()
        self.service.land()
        self.service.disarm()
        
        self.assertEqual(self.service._statistics.total_flights, 1)
        self.assertEqual(self.service._statistics.total_landings, 1)
        self.assertEqual(self.service._statistics.total_takeoffs, 1)
    
    def test_logging(self):
        """Teste Logging."""
        self.service.activate()
        self.service.arm()
        self.service.takeoff()
        self.service.land()
        self.service.disarm()
        
        self.assertGreater(len(self.service._log.events), 0)
        self.assertIsNotNone(self.service._log.last_event)
    
    def test_validation_errors(self):
        """Teste Validierungsfehler."""
        # Teste Arming ohne Aktivierung
        with self.assertRaises(FlightValidationError):
            self.service.arm()
        
        # Teste Start ohne Arming
        with self.assertRaises(FlightValidationError):
            self.service.takeoff()
        
        # Teste Landung ohne Flug
        with self.assertRaises(FlightValidationError):
            self.service.land()
    
    def test_command_errors(self):
        """Teste Befehlsfehler."""
        # Teste Deaktivierung ohne Aktivierung
        with self.assertRaises(FlightCommandError):
            self.service.deactivate()
        
        # Teste Disarming ohne Arming
        with self.assertRaises(FlightCommandError):
            self.service.disarm()
    
    def test_mode_errors(self):
        """Teste Modusfehler."""
        # Teste ungültigen Modus
        with self.assertRaises(FlightModeError):
            self.service.set_mode("INVALID")

if __name__ == '__main__':
    unittest.main() 