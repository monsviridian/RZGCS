"""Unit-Tests für die Flugsteuerungs-Datenmodelle."""

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

class TestFlightControlData(unittest.TestCase):
    """Testfälle für die Flugsteuerungs-Datenmodelle."""
    
    def test_flight_mode(self):
        """Test der Flugmodi."""
        # Gültige Modi
        self.assertEqual(FlightMode.MANUAL.value, "MANUAL")
        self.assertEqual(FlightMode.STABILIZE.value, "STABILIZE")
        self.assertEqual(FlightMode.ALTHOLD.value, "ALTHOLD")
        self.assertEqual(FlightMode.LOITER.value, "LOITER")
        self.assertEqual(FlightMode.RTL.value, "RTL")
        self.assertEqual(FlightMode.AUTO.value, "AUTO")
        self.assertEqual(FlightMode.GUIDED.value, "GUIDED")
        
        # Ungültige Modi
        with self.assertRaises(ValueError):
            FlightMode("INVALID")
    
    def test_flight_status(self):
        """Test der Flugstatus."""
        # Gültige Status
        self.assertEqual(FlightStatus.DISARMED.value, "DISARMED")
        self.assertEqual(FlightStatus.ARMED.value, "ARMED")
        self.assertEqual(FlightStatus.TAKEOFF.value, "TAKEOFF")
        self.assertEqual(FlightStatus.LANDING.value, "LANDING")
        self.assertEqual(FlightStatus.ERROR.value, "ERROR")
        
        # Ungültige Status
        with self.assertRaises(ValueError):
            FlightStatus("INVALID")
    
    def test_flight_state(self):
        """Test des Flugzustands."""
        # Initialisierung
        state = FlightState(
            position=Position(0.0, 0.0, 0.0),
            mode=FlightMode.MANUAL,
            armed=False,
            status=FlightStatus.DISARMED,
            parameters={}
        )
        
        # Standardwerte
        self.assertFalse(state.is_active)
        self.assertFalse(state.is_error)
        self.assertIsNone(state.error_message)
        self.assertEqual(state.mode, FlightMode.MANUAL)
        self.assertEqual(state.status, FlightStatus.DISARMED)
        self.assertFalse(state.is_armed)
        self.assertFalse(state.is_flying)
        self.assertIsNone(state.last_update)
        
        # Aktualisierung
        state.is_active = True
        state.mode = FlightMode.STABILIZE
        state.status = FlightStatus.ARMED
        state.is_armed = True
        state.is_flying = True
        state.last_update = datetime.now()
        
        # Überprüfung
        self.assertTrue(state.is_active)
        self.assertEqual(state.mode, FlightMode.STABILIZE)
        self.assertEqual(state.status, FlightStatus.ARMED)
        self.assertTrue(state.is_armed)
        self.assertTrue(state.is_flying)
        self.assertIsNotNone(state.last_update)
        
        # Validierung
        with self.assertRaises(FlightValidationError):
            state.mode = "INVALID"
        
        with self.assertRaises(FlightValidationError):
            state.status = "INVALID"
    
    def test_flight_statistics(self):
        """Test der Flugstatistiken."""
        # Initialisierung
        stats = FlightStatistics()
        
        # Standardwerte
        self.assertEqual(stats.total_flight_time, 0.0)
        self.assertEqual(stats.total_distance, 0.0)
        self.assertEqual(stats.max_altitude, 0.0)
        self.assertEqual(stats.max_speed, 0.0)
        self.assertEqual(stats.total_commands, 0)
        self.assertEqual(stats.successful_commands, 0)
        self.assertEqual(stats.failed_commands, 0)
        self.assertEqual(stats.total_errors, 0)
        self.assertEqual(stats.mode_changes, 0)
        self.assertEqual(stats.status_changes, 0)
        
        # Aktualisierung
        stats.total_flight_time = 3600.0
        stats.total_distance = 10000.0
        stats.max_altitude = 100.0
        stats.max_speed = 20.0
        stats.total_commands = 100
        stats.successful_commands = 95
        stats.failed_commands = 5
        stats.total_errors = 3
        stats.mode_changes = 10
        stats.status_changes = 5
        
        # Überprüfung
        self.assertEqual(stats.total_flight_time, 3600.0)
        self.assertEqual(stats.total_distance, 10000.0)
        self.assertEqual(stats.max_altitude, 100.0)
        self.assertEqual(stats.max_speed, 20.0)
        self.assertEqual(stats.total_commands, 100)
        self.assertEqual(stats.successful_commands, 95)
        self.assertEqual(stats.failed_commands, 5)
        self.assertEqual(stats.total_errors, 3)
        self.assertEqual(stats.mode_changes, 10)
        self.assertEqual(stats.status_changes, 5)
        
        # Berechnungen
        self.assertEqual(stats.command_success_rate, 0.95)
        self.assertEqual(stats.average_speed, 2.78)  # 10000m / 3600s
    
    def test_flight_event(self):
        """Test der Flugereignisse."""
        # Erstellung
        event = FlightEvent(
            timestamp=datetime.now(),
            event_type="MODE_CHANGE",
            description="Mode changed to STABILIZE",
            data={"old_mode": "MANUAL", "new_mode": "STABILIZE"}
        )
        
        # Überprüfung
        self.assertIsNotNone(event.timestamp)
        self.assertEqual(event.event_type, "MODE_CHANGE")
        self.assertEqual(event.description, "Mode changed to STABILIZE")
        self.assertEqual(event.data["old_mode"], "MANUAL")
        self.assertEqual(event.data["new_mode"], "STABILIZE")
        
        # Validierung
        with self.assertRaises(FlightValidationError):
            FlightEvent(
                timestamp=datetime.now(),
                event_type="",
                description="Invalid event",
                data={}
            )
    
    def test_flight_log(self):
        """Test der Flugprotokolle."""
        # Initialisierung
        log = FlightLog()
        
        # Standardwerte
        self.assertEqual(len(log.events), 0)
        self.assertIsNone(log.last_event)
        
        # Event hinzufügen
        event1 = FlightEvent(
            timestamp=datetime.now(),
            event_type="MODE_CHANGE",
            description="Mode changed to STABILIZE",
            data={"old_mode": "MANUAL", "new_mode": "STABILIZE"}
        )
        log.add_event(event1)
        
        # Überprüfung
        self.assertEqual(len(log.events), 1)
        self.assertEqual(log.last_event, event1)
        
        # Weitere Events
        event2 = FlightEvent(
            timestamp=datetime.now(),
            event_type="STATUS_CHANGE",
            description="Status changed to ARMED",
            data={"old_status": "DISARMED", "new_status": "ARMED"}
        )
        log.add_event(event2)
        
        # Überprüfung
        self.assertEqual(len(log.events), 2)
        self.assertEqual(log.last_event, event2)
        
        # Log bereinigen
        log.clear()
        self.assertEqual(len(log.events), 0)
        self.assertIsNone(log.last_event)
    
    def test_flight_error(self):
        """Test der Flugfehler."""
        # Validierungsfehler
        validation_error = FlightValidationError("Invalid parameter")
        self.assertEqual(str(validation_error), "Invalid parameter")
        self.assertIsInstance(validation_error, FlightError)
        
        # Befehlsfehler
        command_error = FlightCommandError("Command failed")
        self.assertEqual(str(command_error), "Command failed")
        self.assertIsInstance(command_error, FlightError)
        
        # Modusfehler
        mode_error = FlightModeError("Mode not available")
        self.assertEqual(str(mode_error), "Mode not available")
        self.assertIsInstance(mode_error, FlightError)

if __name__ == "__main__":
    unittest.main() 