"""Unit-Tests für die Geofencing-Datenmodelle."""

import unittest
from datetime import datetime
from flight_control.models.geofence_data import (
    GeofenceType,
    GeofenceAction,
    GeofenceStatus,
    GeofenceState,
    GeofenceStatistics,
    GeofenceEvent,
    GeofenceLog,
    GeofenceError,
    GeofenceValidationError,
    GeofenceCommandError,
    GeofenceTypeError
)

class TestGeofenceData(unittest.TestCase):
    """Testfälle für die Geofencing-Datenmodelle."""
    
    def test_geofence_type(self):
        """Test der Geofence-Typen."""
        # Gültige Typen
        self.assertEqual(GeofenceType.POLYGON.value, "POLYGON")
        self.assertEqual(GeofenceType.CIRCLE.value, "CIRCLE")
        self.assertEqual(GeofenceType.RECTANGLE.value, "RECTANGLE")
        
        # Ungültige Typen
        with self.assertRaises(ValueError):
            GeofenceType("INVALID")
    
    def test_geofence_action(self):
        """Test der Geofence-Aktionen."""
        # Gültige Aktionen
        self.assertEqual(GeofenceAction.WARN.value, "WARN")
        self.assertEqual(GeofenceAction.RETURN.value, "RETURN")
        self.assertEqual(GeofenceAction.LAND.value, "LAND")
        
        # Ungültige Aktionen
        with self.assertRaises(ValueError):
            GeofenceAction("INVALID")
    
    def test_geofence_status(self):
        """Test der Geofence-Status."""
        # Gültige Status
        self.assertEqual(GeofenceStatus.INACTIVE.value, "INACTIVE")
        self.assertEqual(GeofenceStatus.ACTIVE.value, "ACTIVE")
        self.assertEqual(GeofenceStatus.WARNING.value, "WARNING")
        self.assertEqual(GeofenceStatus.VIOLATION.value, "VIOLATION")
        self.assertEqual(GeofenceStatus.ERROR.value, "ERROR")
        
        # Ungültige Status
        with self.assertRaises(ValueError):
            GeofenceStatus("INVALID")
    
    def test_geofence_state(self):
        """Test des Geofence-Zustands."""
        # Initialisierung
        state = GeofenceState()
        
        # Standardwerte
        self.assertFalse(state.is_active)
        self.assertFalse(state.is_error)
        self.assertIsNone(state.error_message)
        self.assertEqual(state.type, GeofenceType.POLYGON)
        self.assertEqual(state.status, GeofenceStatus.INACTIVE)
        self.assertFalse(state.is_warning)
        self.assertFalse(state.is_violation)
        self.assertIsNone(state.last_update)
        
        # Aktualisierung
        state.is_active = True
        state.type = GeofenceType.CIRCLE
        state.status = GeofenceStatus.ACTIVE
        state.is_warning = True
        state.is_violation = False
        state.last_update = datetime.now()
        
        # Überprüfung
        self.assertTrue(state.is_active)
        self.assertEqual(state.type, GeofenceType.CIRCLE)
        self.assertEqual(state.status, GeofenceStatus.ACTIVE)
        self.assertTrue(state.is_warning)
        self.assertFalse(state.is_violation)
        self.assertIsNotNone(state.last_update)
        
        # Validierung
        with self.assertRaises(GeofenceValidationError):
            state.type = "INVALID"
        
        with self.assertRaises(GeofenceValidationError):
            state.status = "INVALID"
    
    def test_geofence_statistics(self):
        """Test der Geofence-Statistiken."""
        # Initialisierung
        stats = GeofenceStatistics()
        
        # Standardwerte
        self.assertEqual(stats.total_warnings, 0)
        self.assertEqual(stats.total_violations, 0)
        self.assertEqual(stats.total_actions, 0)
        self.assertEqual(stats.warn_actions, 0)
        self.assertEqual(stats.return_actions, 0)
        self.assertEqual(stats.land_actions, 0)
        self.assertEqual(stats.total_errors, 0)
        self.assertEqual(stats.total_distance, 0.0)
        self.assertEqual(stats.max_altitude, 0.0)
        self.assertEqual(stats.max_speed, 0.0)
        
        # Aktualisierung
        stats.total_warnings = 10
        stats.total_violations = 5
        stats.total_actions = 15
        stats.warn_actions = 10
        stats.return_actions = 3
        stats.land_actions = 2
        stats.total_errors = 1
        stats.total_distance = 10000.0
        stats.max_altitude = 100.0
        stats.max_speed = 20.0
        
        # Überprüfung
        self.assertEqual(stats.total_warnings, 10)
        self.assertEqual(stats.total_violations, 5)
        self.assertEqual(stats.total_actions, 15)
        self.assertEqual(stats.warn_actions, 10)
        self.assertEqual(stats.return_actions, 3)
        self.assertEqual(stats.land_actions, 2)
        self.assertEqual(stats.total_errors, 1)
        self.assertEqual(stats.total_distance, 10000.0)
        self.assertEqual(stats.max_altitude, 100.0)
        self.assertEqual(stats.max_speed, 20.0)
        
        # Berechnungen
        self.assertEqual(stats.warning_rate, 0.67)  # 10/15
        self.assertEqual(stats.violation_rate, 0.33)  # 5/15
        self.assertEqual(stats.action_success_rate, 0.93)  # 14/15
    
    def test_geofence_event(self):
        """Test der Geofence-Ereignisse."""
        # Erstellung
        event = GeofenceEvent(
            timestamp=datetime.now(),
            event_type="WARNING",
            description="Approaching geofence boundary",
            data={"distance": 10.0, "action": "WARN"}
        )
        
        # Überprüfung
        self.assertIsNotNone(event.timestamp)
        self.assertEqual(event.event_type, "WARNING")
        self.assertEqual(event.description, "Approaching geofence boundary")
        self.assertEqual(event.data["distance"], 10.0)
        self.assertEqual(event.data["action"], "WARN")
        
        # Validierung
        with self.assertRaises(GeofenceValidationError):
            GeofenceEvent(
                timestamp=datetime.now(),
                event_type="",
                description="Invalid event",
                data={}
            )
    
    def test_geofence_log(self):
        """Test der Geofence-Protokolle."""
        # Initialisierung
        log = GeofenceLog()
        
        # Standardwerte
        self.assertEqual(len(log.events), 0)
        self.assertIsNone(log.last_event)
        
        # Event hinzufügen
        event1 = GeofenceEvent(
            timestamp=datetime.now(),
            event_type="WARNING",
            description="Approaching geofence boundary",
            data={"distance": 10.0, "action": "WARN"}
        )
        log.add_event(event1)
        
        # Überprüfung
        self.assertEqual(len(log.events), 1)
        self.assertEqual(log.last_event, event1)
        
        # Weitere Events
        event2 = GeofenceEvent(
            timestamp=datetime.now(),
            event_type="VIOLATION",
            description="Geofence boundary violated",
            data={"distance": -5.0, "action": "RETURN"}
        )
        log.add_event(event2)
        
        # Überprüfung
        self.assertEqual(len(log.events), 2)
        self.assertEqual(log.last_event, event2)
        
        # Log bereinigen
        log.clear()
        self.assertEqual(len(log.events), 0)
        self.assertIsNone(log.last_event)
    
    def test_geofence_error(self):
        """Test der Geofence-Fehler."""
        # Validierungsfehler
        validation_error = GeofenceValidationError("Invalid parameter")
        self.assertEqual(str(validation_error), "Invalid parameter")
        self.assertIsInstance(validation_error, GeofenceError)
        
        # Befehlsfehler
        command_error = GeofenceCommandError("Command failed")
        self.assertEqual(str(command_error), "Command failed")
        self.assertIsInstance(command_error, GeofenceError)
        
        # Typfehler
        type_error = GeofenceTypeError("Invalid type")
        self.assertEqual(str(type_error), "Invalid type")
        self.assertIsInstance(type_error, GeofenceError)

if __name__ == "__main__":
    unittest.main() 