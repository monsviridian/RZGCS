"""Unit-Tests für den Geofencing-Service."""

import unittest
from datetime import datetime
from PySide6.QtCore import QObject, Signal, Slot, QTimer
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
from flight_control.services.geofence_service import GeofenceService

class TestGeofenceService(unittest.TestCase):
    """Testfälle für den Geofencing-Service."""
    
    def setUp(self):
        """Testumgebung vorbereiten."""
        self.service = GeofenceService()
    
    def test_initial_state(self):
        """Test des initialen Zustands."""
        # Service-Status
        self.assertFalse(self.service._state.is_active)
        self.assertFalse(self.service._state.is_error)
        self.assertIsNone(self.service._state.error_message)
        self.assertEqual(self.service._state.type, GeofenceType.POLYGON)
        self.assertEqual(self.service._state.status, GeofenceStatus.INACTIVE)
        self.assertFalse(self.service._state.is_warning)
        self.assertFalse(self.service._state.is_violation)
        self.assertIsNone(self.service._state.last_update)
        
        # Statistiken
        self.assertEqual(self.service._statistics.total_warnings, 0)
        self.assertEqual(self.service._statistics.total_violations, 0)
        self.assertEqual(self.service._statistics.total_actions, 0)
        self.assertEqual(self.service._statistics.warn_actions, 0)
        self.assertEqual(self.service._statistics.return_actions, 0)
        self.assertEqual(self.service._statistics.land_actions, 0)
        self.assertEqual(self.service._statistics.total_errors, 0)
        self.assertEqual(self.service._statistics.total_distance, 0.0)
        self.assertEqual(self.service._statistics.max_altitude, 0.0)
        self.assertEqual(self.service._statistics.max_speed, 0.0)
        
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
        self.assertEqual(self.service._state.type, GeofenceType.POLYGON)
        self.assertEqual(self.service._state.status, GeofenceStatus.ACTIVE)
        self.assertFalse(self.service._state.is_warning)
        self.assertFalse(self.service._state.is_violation)
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
    
    def test_polygon_geofence(self):
        """Test der Polygon-Geofence."""
        # Service aktivieren
        self.service.activate()
        
        # Polygon-Geofence konfigurieren
        vertices = [
            {"lat": 48.123, "lon": 11.456},
            {"lat": 48.124, "lon": 11.456},
            {"lat": 48.124, "lon": 11.457},
            {"lat": 48.123, "lon": 11.457}
        ]
        self.service.set_polygon_geofence(vertices, 100.0, 10.0, GeofenceAction.WARN)
        
        # Überprüfung
        self.assertEqual(self.service._state.type, GeofenceType.POLYGON)
        self.assertEqual(len(self.service._state.vertices), 4)
        self.assertEqual(self.service._state.max_altitude, 100.0)
        self.assertEqual(self.service._state.buffer_zone, 10.0)
        self.assertEqual(self.service._state.action, GeofenceAction.WARN)
        
        # Log überprüfen
        self.assertEqual(len(self.service._log.events), 2)
        self.assertEqual(self.service._log.last_event.event_type, "CONFIGURATION")
    
    def test_circle_geofence(self):
        """Test der Circle-Geofence."""
        # Service aktivieren
        self.service.activate()
        
        # Circle-Geofence konfigurieren
        center = {"lat": 48.123, "lon": 11.456}
        self.service.set_circle_geofence(center, 1000.0, 100.0, 10.0, GeofenceAction.RETURN)
        
        # Überprüfung
        self.assertEqual(self.service._state.type, GeofenceType.CIRCLE)
        self.assertEqual(self.service._state.center, center)
        self.assertEqual(self.service._state.radius, 1000.0)
        self.assertEqual(self.service._state.max_altitude, 100.0)
        self.assertEqual(self.service._state.buffer_zone, 10.0)
        self.assertEqual(self.service._state.action, GeofenceAction.RETURN)
        
        # Log überprüfen
        self.assertEqual(len(self.service._log.events), 2)
        self.assertEqual(self.service._log.last_event.event_type, "CONFIGURATION")
    
    def test_rectangle_geofence(self):
        """Test der Rectangle-Geofence."""
        # Service aktivieren
        self.service.activate()
        
        # Rectangle-Geofence konfigurieren
        corners = {
            "north": 48.124,
            "south": 48.123,
            "east": 11.457,
            "west": 11.456
        }
        self.service.set_rectangle_geofence(corners, 100.0, 10.0, GeofenceAction.LAND)
        
        # Überprüfung
        self.assertEqual(self.service._state.type, GeofenceType.RECTANGLE)
        self.assertEqual(self.service._state.corners, corners)
        self.assertEqual(self.service._state.max_altitude, 100.0)
        self.assertEqual(self.service._state.buffer_zone, 10.0)
        self.assertEqual(self.service._state.action, GeofenceAction.LAND)
        
        # Log überprüfen
        self.assertEqual(len(self.service._log.events), 2)
        self.assertEqual(self.service._log.last_event.event_type, "CONFIGURATION")
    
    def test_position_updates(self):
        """Test der Positionsaktualisierungen."""
        # Service aktivieren und Circle-Geofence konfigurieren
        self.service.activate()
        center = {"lat": 48.123, "lon": 11.456}
        self.service.set_circle_geofence(center, 1000.0, 100.0, 10.0, GeofenceAction.WARN)
        
        # Position innerhalb der Geofence
        position = {"lat": 48.123, "lon": 11.456, "alt": 50.0}
        self.service.update_position(position)
        self.assertFalse(self.service._state.is_warning)
        self.assertFalse(self.service._state.is_violation)
        
        # Position in der Pufferzone
        position = {"lat": 48.123, "lon": 11.466, "alt": 50.0}
        self.service.update_position(position)
        self.assertTrue(self.service._state.is_warning)
        self.assertFalse(self.service._state.is_violation)
        
        # Position außerhalb der Geofence
        position = {"lat": 48.123, "lon": 11.476, "alt": 50.0}
        self.service.update_position(position)
        self.assertTrue(self.service._state.is_warning)
        self.assertTrue(self.service._state.is_violation)
        
        # Log überprüfen
        self.assertEqual(len(self.service._log.events), 4)  # Aktivierung + 3 Positionen
        self.assertEqual(self.service._log.last_event.event_type, "VIOLATION")
    
    def test_action_execution(self):
        """Test der Aktionsausführung."""
        # Service aktivieren und Circle-Geofence konfigurieren
        self.service.activate()
        center = {"lat": 48.123, "lon": 11.456}
        self.service.set_circle_geofence(center, 1000.0, 100.0, 10.0, GeofenceAction.WARN)
        
        # Position in der Pufferzone
        position = {"lat": 48.123, "lon": 11.466, "alt": 50.0}
        self.service.update_position(position)
        
        # Aktion ausführen
        self.service.execute_action()
        
        # Überprüfung
        self.assertEqual(self.service._statistics.warn_actions, 1)
        self.assertEqual(self.service._statistics.total_actions, 1)
        
        # Log überprüfen
        self.assertEqual(len(self.service._log.events), 3)
        self.assertEqual(self.service._log.last_event.event_type, "ACTION")
    
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
        with self.assertRaises(GeofenceCommandError):
            self.service.set_polygon_geofence([], 100.0, 10.0, GeofenceAction.WARN)
        
        with self.assertRaises(GeofenceCommandError):
            self.service.set_circle_geofence({}, 1000.0, 100.0, 10.0, GeofenceAction.RETURN)
        
        with self.assertRaises(GeofenceCommandError):
            self.service.set_rectangle_geofence({}, 100.0, 10.0, GeofenceAction.LAND)
        
        with self.assertRaises(GeofenceCommandError):
            self.service.update_position({})
        
        with self.assertRaises(GeofenceCommandError):
            self.service.execute_action()
        
        # Überprüfung
        self.assertFalse(self.service._state.is_active)
        self.assertFalse(self.service._state.is_error)
        self.assertIsNone(self.service._state.error_message)
        self.assertEqual(self.service._state.type, GeofenceType.POLYGON)
        self.assertEqual(self.service._state.status, GeofenceStatus.INACTIVE)
        self.assertFalse(self.service._state.is_warning)
        self.assertFalse(self.service._state.is_violation)
        self.assertIsNone(self.service._state.last_update)
        
        # Log überprüfen
        self.assertEqual(len(self.service._log.events), 0)
        self.assertIsNone(self.service._log.last_event)

if __name__ == "__main__":
    unittest.main() 