"""Unit-Tests für das Geofencing-ViewModel."""

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
from flight_control.viewmodels.geofence_viewmodel import GeofenceViewModel

class TestGeofenceViewModel(unittest.TestCase):
    """Testfälle für das Geofencing-ViewModel."""
    
    def setUp(self):
        """Testumgebung vorbereiten."""
        self.viewmodel = GeofenceViewModel()
    
    def test_initial_state(self):
        """Test des initialen Zustands."""
        # ViewModel-Status
        self.assertFalse(self.viewmodel.is_active)
        self.assertFalse(self.viewmodel.is_error)
        self.assertEqual(self.viewmodel.error_message, "")
        self.assertEqual(self.viewmodel.type, GeofenceType.POLYGON)
        self.assertEqual(self.viewmodel.status, GeofenceStatus.INACTIVE)
        self.assertFalse(self.viewmodel.is_warning)
        self.assertFalse(self.viewmodel.is_violation)
        self.assertEqual(self.viewmodel.last_update, "")
        
        # Statistiken
        self.assertEqual(self.viewmodel.total_warnings, 0)
        self.assertEqual(self.viewmodel.total_violations, 0)
        self.assertEqual(self.viewmodel.total_actions, 0)
        self.assertEqual(self.viewmodel.warn_actions, 0)
        self.assertEqual(self.viewmodel.return_actions, 0)
        self.assertEqual(self.viewmodel.land_actions, 0)
        self.assertEqual(self.viewmodel.total_errors, 0)
        self.assertEqual(self.viewmodel.total_distance, 0.0)
        self.assertEqual(self.viewmodel.max_altitude, 0.0)
        self.assertEqual(self.viewmodel.max_speed, 0.0)
        
        # Log
        self.assertEqual(len(self.viewmodel.log_events), 0)
        self.assertEqual(self.viewmodel.last_event, "")
    
    def test_activation(self):
        """Test der Aktivierung."""
        # ViewModel aktivieren
        self.viewmodel.activate()
        
        # Überprüfung
        self.assertTrue(self.viewmodel.is_active)
        self.assertFalse(self.viewmodel.is_error)
        self.assertEqual(self.viewmodel.error_message, "")
        self.assertEqual(self.viewmodel.type, GeofenceType.POLYGON)
        self.assertEqual(self.viewmodel.status, GeofenceStatus.ACTIVE)
        self.assertFalse(self.viewmodel.is_warning)
        self.assertFalse(self.viewmodel.is_violation)
        self.assertNotEqual(self.viewmodel.last_update, "")
        
        # Log überprüfen
        self.assertEqual(len(self.viewmodel.log_events), 1)
        self.assertIn("ACTIVATION", self.viewmodel.last_event)
    
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
        self.assertIn("DEACTIVATION", self.viewmodel.last_event)
    
    def test_polygon_geofence(self):
        """Test der Polygon-Geofence."""
        # ViewModel aktivieren
        self.viewmodel.activate()
        
        # Polygon-Geofence konfigurieren
        vertices = [
            {"lat": 48.123, "lon": 11.456},
            {"lat": 48.124, "lon": 11.456},
            {"lat": 48.124, "lon": 11.457},
            {"lat": 48.123, "lon": 11.457}
        ]
        self.viewmodel.set_polygon_geofence(vertices, 100.0, 10.0, GeofenceAction.WARN)
        
        # Überprüfung
        self.assertEqual(self.viewmodel.type, GeofenceType.POLYGON)
        self.assertEqual(len(self.viewmodel.vertices), 4)
        self.assertEqual(self.viewmodel.max_altitude, 100.0)
        self.assertEqual(self.viewmodel.buffer_zone, 10.0)
        self.assertEqual(self.viewmodel.action, GeofenceAction.WARN)
        
        # Log überprüfen
        self.assertEqual(len(self.viewmodel.log_events), 2)
        self.assertIn("CONFIGURATION", self.viewmodel.last_event)
    
    def test_circle_geofence(self):
        """Test der Circle-Geofence."""
        # ViewModel aktivieren
        self.viewmodel.activate()
        
        # Circle-Geofence konfigurieren
        center = {"lat": 48.123, "lon": 11.456}
        self.viewmodel.set_circle_geofence(center, 1000.0, 100.0, 10.0, GeofenceAction.RETURN)
        
        # Überprüfung
        self.assertEqual(self.viewmodel.type, GeofenceType.CIRCLE)
        self.assertEqual(self.viewmodel.center, center)
        self.assertEqual(self.viewmodel.radius, 1000.0)
        self.assertEqual(self.viewmodel.max_altitude, 100.0)
        self.assertEqual(self.viewmodel.buffer_zone, 10.0)
        self.assertEqual(self.viewmodel.action, GeofenceAction.RETURN)
        
        # Log überprüfen
        self.assertEqual(len(self.viewmodel.log_events), 2)
        self.assertIn("CONFIGURATION", self.viewmodel.last_event)
    
    def test_rectangle_geofence(self):
        """Test der Rectangle-Geofence."""
        # ViewModel aktivieren
        self.viewmodel.activate()
        
        # Rectangle-Geofence konfigurieren
        corners = {
            "north": 48.124,
            "south": 48.123,
            "east": 11.457,
            "west": 11.456
        }
        self.viewmodel.set_rectangle_geofence(corners, 100.0, 10.0, GeofenceAction.LAND)
        
        # Überprüfung
        self.assertEqual(self.viewmodel.type, GeofenceType.RECTANGLE)
        self.assertEqual(self.viewmodel.corners, corners)
        self.assertEqual(self.viewmodel.max_altitude, 100.0)
        self.assertEqual(self.viewmodel.buffer_zone, 10.0)
        self.assertEqual(self.viewmodel.action, GeofenceAction.LAND)
        
        # Log überprüfen
        self.assertEqual(len(self.viewmodel.log_events), 2)
        self.assertIn("CONFIGURATION", self.viewmodel.last_event)
    
    def test_position_updates(self):
        """Test der Positionsaktualisierungen."""
        # ViewModel aktivieren und Circle-Geofence konfigurieren
        self.viewmodel.activate()
        center = {"lat": 48.123, "lon": 11.456}
        self.viewmodel.set_circle_geofence(center, 1000.0, 100.0, 10.0, GeofenceAction.WARN)
        
        # Position innerhalb der Geofence
        position = {"lat": 48.123, "lon": 11.456, "alt": 50.0}
        self.viewmodel.update_position(position)
        self.assertFalse(self.viewmodel.is_warning)
        self.assertFalse(self.viewmodel.is_violation)
        
        # Position in der Pufferzone
        position = {"lat": 48.123, "lon": 11.466, "alt": 50.0}
        self.viewmodel.update_position(position)
        self.assertTrue(self.viewmodel.is_warning)
        self.assertFalse(self.viewmodel.is_violation)
        
        # Position außerhalb der Geofence
        position = {"lat": 48.123, "lon": 11.476, "alt": 50.0}
        self.viewmodel.update_position(position)
        self.assertTrue(self.viewmodel.is_warning)
        self.assertTrue(self.viewmodel.is_violation)
        
        # Log überprüfen
        self.assertEqual(len(self.viewmodel.log_events), 4)  # Aktivierung + 3 Positionen
        self.assertIn("VIOLATION", self.viewmodel.last_event)
    
    def test_action_execution(self):
        """Test der Aktionsausführung."""
        # ViewModel aktivieren und Circle-Geofence konfigurieren
        self.viewmodel.activate()
        center = {"lat": 48.123, "lon": 11.456}
        self.viewmodel.set_circle_geofence(center, 1000.0, 100.0, 10.0, GeofenceAction.WARN)
        
        # Position in der Pufferzone
        position = {"lat": 48.123, "lon": 11.466, "alt": 50.0}
        self.viewmodel.update_position(position)
        
        # Aktion ausführen
        self.viewmodel.execute_action()
        
        # Überprüfung
        self.assertEqual(self.viewmodel.warn_actions, 1)
        self.assertEqual(self.viewmodel.total_actions, 1)
        
        # Log überprüfen
        self.assertEqual(len(self.viewmodel.log_events), 3)
        self.assertIn("ACTION", self.viewmodel.last_event)
    
    def test_error_handling(self):
        """Test der Fehlerbehandlung."""
        # ViewModel aktivieren
        self.viewmodel.activate()
        
        # Fehler simulieren
        self.viewmodel._handle_error("Test error")
        
        # Überprüfung
        self.assertTrue(self.viewmodel.is_error)
        self.assertEqual(self.viewmodel.error_message, "Test error")
        self.assertEqual(self.viewmodel.total_errors, 1)
        
        # Log überprüfen
        self.assertEqual(len(self.viewmodel.log_events), 2)
        self.assertIn("ERROR", self.viewmodel.last_event)
        
        # Fehler zurücksetzen
        self.viewmodel._reset_error()
        
        # Überprüfung
        self.assertFalse(self.viewmodel.is_error)
        self.assertEqual(self.viewmodel.error_message, "")
    
    def test_statistics_updates(self):
        """Test der Statistiken-Aktualisierungen."""
        # ViewModel aktivieren
        self.viewmodel.activate()
        
        # Statistiken aktualisieren
        statistics = GeofenceStatistics()
        statistics.total_warnings = 5
        statistics.total_violations = 2
        statistics.total_actions = 3
        statistics.warn_actions = 2
        statistics.return_actions = 1
        statistics.land_actions = 0
        statistics.total_errors = 1
        statistics.total_distance = 1000.0
        statistics.max_altitude = 100.0
        statistics.max_speed = 10.0
        
        self.viewmodel._update_statistics(statistics)
        
        # Überprüfung
        self.assertEqual(self.viewmodel.total_warnings, 5)
        self.assertEqual(self.viewmodel.total_violations, 2)
        self.assertEqual(self.viewmodel.total_actions, 3)
        self.assertEqual(self.viewmodel.warn_actions, 2)
        self.assertEqual(self.viewmodel.return_actions, 1)
        self.assertEqual(self.viewmodel.land_actions, 0)
        self.assertEqual(self.viewmodel.total_errors, 1)
        self.assertEqual(self.viewmodel.total_distance, 1000.0)
        self.assertEqual(self.viewmodel.max_altitude, 100.0)
        self.assertEqual(self.viewmodel.max_speed, 10.0)
    
    def test_log_updates(self):
        """Test der Log-Aktualisierungen."""
        # ViewModel aktivieren
        self.viewmodel.activate()
        
        # Event hinzufügen
        event = GeofenceEvent("TEST", "Test event")
        self.viewmodel._add_event(event)
        
        # Überprüfung
        self.assertEqual(len(self.viewmodel.log_events), 2)  # Aktivierung + Test
        self.assertIn("TEST", self.viewmodel.last_event)
    
    def test_inactive_operations(self):
        """Test von Operationen im inaktiven Zustand."""
        # Ungültige Operationen
        with self.assertRaises(GeofenceCommandError):
            self.viewmodel.set_polygon_geofence([], 100.0, 10.0, GeofenceAction.WARN)
        
        with self.assertRaises(GeofenceCommandError):
            self.viewmodel.set_circle_geofence({}, 1000.0, 100.0, 10.0, GeofenceAction.RETURN)
        
        with self.assertRaises(GeofenceCommandError):
            self.viewmodel.set_rectangle_geofence({}, 100.0, 10.0, GeofenceAction.LAND)
        
        with self.assertRaises(GeofenceCommandError):
            self.viewmodel.update_position({})
        
        with self.assertRaises(GeofenceCommandError):
            self.viewmodel.execute_action()
        
        # Überprüfung
        self.assertFalse(self.viewmodel.is_active)
        self.assertFalse(self.viewmodel.is_error)
        self.assertEqual(self.viewmodel.error_message, "")
        self.assertEqual(self.viewmodel.type, GeofenceType.POLYGON)
        self.assertEqual(self.viewmodel.status, GeofenceStatus.INACTIVE)
        self.assertFalse(self.viewmodel.is_warning)
        self.assertFalse(self.viewmodel.is_violation)
        self.assertEqual(self.viewmodel.last_update, "")
        
        # Log überprüfen
        self.assertEqual(len(self.viewmodel.log_events), 0)
        self.assertEqual(self.viewmodel.last_event, "")

if __name__ == "__main__":
    unittest.main() 