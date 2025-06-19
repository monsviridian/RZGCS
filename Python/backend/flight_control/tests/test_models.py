"""Unit-Tests für die Flugsteuerungs-Datenmodelle.

Diese Tests überprüfen die Funktionalität der Datenmodelle:
- FlightMode
- FlightStatus
- FlightState
- FlightStatistics
- FlightEvent
- FlightLog
- Fehlerklassen
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
    FlightModeError,
    Position
)

class TestFlightMode(unittest.TestCase):
    """Tests für FlightMode."""
    
    def test_valid_modes(self):
        """Teste gültige Flugmodi."""
        self.assertEqual(FlightMode.STABILIZE.value, "STABILIZE")
        self.assertEqual(FlightMode.ALTHOLD.value, "ALTHOLD")
        self.assertEqual(FlightMode.LOITER.value, "LOITER")
        self.assertEqual(FlightMode.RTL.value, "RTL")
        self.assertEqual(FlightMode.AUTO.value, "AUTO")
        self.assertEqual(FlightMode.GUIDED.value, "GUIDED")
        self.assertEqual(FlightMode.MANUAL.value, "MANUAL")
    
    def test_invalid_mode(self):
        """Teste ungültigen Flugmodus."""
        with self.assertRaises(ValueError):
            FlightMode("INVALID")

class TestFlightStatus(unittest.TestCase):
    """Tests für FlightStatus."""
    
    def test_valid_statuses(self):
        """Teste gültige Flugstatus."""
        self.assertEqual(FlightStatus.INACTIVE.value, "INACTIVE")
        self.assertEqual(FlightStatus.READY.value, "READY")
        self.assertEqual(FlightStatus.ARMING.value, "ARMING")
        self.assertEqual(FlightStatus.ARMED.value, "ARMED")
        self.assertEqual(FlightStatus.TAKING_OFF.value, "TAKING_OFF")
        self.assertEqual(FlightStatus.FLYING.value, "FLYING")
        self.assertEqual(FlightStatus.LANDING.value, "LANDING")
        self.assertEqual(FlightStatus.ERROR.value, "ERROR")
    
    def test_invalid_status(self):
        """Teste ungültigen Flugstatus."""
        with self.assertRaises(ValueError):
            FlightStatus("INVALID")

class TestFlightState(unittest.TestCase):
    """Tests für FlightState."""
    
    def setUp(self):
        """Test-Setup."""
        self.state = FlightState(
            position=Position(0.0, 0.0, 0.0),
            mode=FlightMode.MANUAL,
            armed=False,
            status=FlightStatus.DISARMED,
            parameters={}
        )
    
    def test_initial_state(self):
        """Teste Initialzustand."""
        self.assertFalse(self.state.is_active)
        self.assertFalse(self.state.is_error)
        self.assertIsNone(self.state.error_message)
        self.assertEqual(self.state.mode, FlightMode.MANUAL)
        self.assertEqual(self.state.status, FlightStatus.DISARMED)
        self.assertFalse(self.state.is_armed)
        self.assertFalse(self.state.is_flying)
        self.assertFalse(self.state.is_landing)
        self.assertFalse(self.state.is_taking_off)
    
    def test_update_state(self):
        """Teste Zustandsaktualisierung."""
        self.state.update(
            is_active=True,
            is_error=False,
            error_message=None,
            mode=FlightMode.ALTHOLD,
            status=FlightStatus.READY,
            is_armed=True,
            is_flying=False,
            is_landing=False,
            is_taking_off=False
        )
        
        self.assertTrue(self.state.is_active)
        self.assertFalse(self.state.is_error)
        self.assertIsNone(self.state.error_message)
        self.assertEqual(self.state.mode, FlightMode.ALTHOLD)
        self.assertEqual(self.state.status, FlightStatus.READY)
        self.assertTrue(self.state.is_armed)
        self.assertFalse(self.state.is_flying)
        self.assertFalse(self.state.is_landing)
        self.assertFalse(self.state.is_taking_off)
    
    def test_error_state(self):
        """Teste Fehlerzustand."""
        self.state.update(
            is_error=True,
            error_message="Test Error",
            status=FlightStatus.ERROR
        )
        
        self.assertTrue(self.state.is_error)
        self.assertEqual(self.state.error_message, "Test Error")
        self.assertEqual(self.state.status, FlightStatus.ERROR)

class TestFlightStatistics(unittest.TestCase):
    """Tests für FlightStatistics."""
    
    def setUp(self):
        """Test-Setup."""
        self.stats = FlightStatistics()
    
    def test_initial_stats(self):
        """Teste Initialstatistiken."""
        self.assertEqual(self.stats.total_flights, 0)
        self.assertEqual(self.stats.total_flight_time, 0.0)
        self.assertEqual(self.stats.total_distance, 0.0)
        self.assertEqual(self.stats.max_altitude, 0.0)
        self.assertEqual(self.stats.max_speed, 0.0)
        self.assertEqual(self.stats.total_landings, 0)
        self.assertEqual(self.stats.total_takeoffs, 0)
        self.assertEqual(self.stats.total_errors, 0)
        self.assertEqual(self.stats.mode_changes, 0)
    
    def test_update_stats(self):
        """Teste Statistikaktualisierung."""
        self.stats.update(
            total_flights=1,
            total_flight_time=100.0,
            total_distance=1000.0,
            max_altitude=100.0,
            max_speed=20.0,
            total_landings=1,
            total_takeoffs=1,
            total_errors=0,
            mode_changes=2
        )
        
        self.assertEqual(self.stats.total_flights, 1)
        self.assertEqual(self.stats.total_flight_time, 100.0)
        self.assertEqual(self.stats.total_distance, 1000.0)
        self.assertEqual(self.stats.max_altitude, 100.0)
        self.assertEqual(self.stats.max_speed, 20.0)
        self.assertEqual(self.stats.total_landings, 1)
        self.assertEqual(self.stats.total_takeoffs, 1)
        self.assertEqual(self.stats.total_errors, 0)
        self.assertEqual(self.stats.mode_changes, 2)

class TestFlightEvent(unittest.TestCase):
    """Tests für FlightEvent."""
    
    def test_event_creation(self):
        """Teste Event-Erstellung."""
        event = FlightEvent(
            timestamp=datetime.now(),
            event_type="TEST",
            description="Test Event"
        )
        
        self.assertIsInstance(event.timestamp, datetime)
        self.assertEqual(event.event_type, "TEST")
        self.assertEqual(event.description, "Test Event")

class TestFlightLog(unittest.TestCase):
    """Tests für FlightLog."""
    
    def setUp(self):
        """Test-Setup."""
        self.log = FlightLog()
    
    def test_initial_log(self):
        """Teste Initial-Log."""
        self.assertEqual(len(self.log.events), 0)
        self.assertIsNone(self.log.last_event)
    
    def test_add_event(self):
        """Teste Event-Hinzufügung."""
        event = FlightEvent(
            timestamp=datetime.now(),
            event_type="TEST",
            description="Test Event"
        )
        
        self.log.add_event(event)
        
        self.assertEqual(len(self.log.events), 1)
        self.assertEqual(self.log.last_event, event)
    
    def test_clear_log(self):
        """Teste Log-Löschung."""
        event = FlightEvent(
            timestamp=datetime.now(),
            event_type="TEST",
            description="Test Event"
        )
        
        self.log.add_event(event)
        self.log.clear()
        
        self.assertEqual(len(self.log.events), 0)
        self.assertIsNone(self.log.last_event)

class TestFlightErrors(unittest.TestCase):
    """Tests für Flugfehler."""
    
    def test_flight_error(self):
        """Teste FlightError."""
        error = FlightError("Test Error")
        self.assertEqual(str(error), "Test Error")
    
    def test_validation_error(self):
        """Teste FlightValidationError."""
        error = FlightValidationError("Validation Error")
        self.assertEqual(str(error), "Validation Error")
    
    def test_command_error(self):
        """Teste FlightCommandError."""
        error = FlightCommandError("Command Error")
        self.assertEqual(str(error), "Command Error")
    
    def test_mode_error(self):
        """Teste FlightModeError."""
        error = FlightModeError("Mode Error")
        self.assertEqual(str(error), "Mode Error")

if __name__ == '__main__':
    unittest.main() 