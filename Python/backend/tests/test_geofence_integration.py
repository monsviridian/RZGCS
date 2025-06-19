"""Integrationstests für das Geofencing."""

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
from flight_control.viewmodels.geofence_viewmodel import GeofenceViewModel

class MockGeofenceView(QObject):
    """Mock-View für Geofencing-Tests."""
    
    # Signale
    activation_requested = Signal()
    deactivation_requested = Signal()
    polygon_geofence_requested = Signal(list, float, float, str)
    circle_geofence_requested = Signal(dict, float, float, float, str)
    rectangle_geofence_requested = Signal(dict, float, float, str)
    action_requested = Signal()
    
    def __init__(self):
        """Initialisierung."""
        super().__init__()
        self.is_active = False
        self.is_error = False
        self.error_message = ""
        self.type = GeofenceType.POLYGON
        self.status = GeofenceStatus.INACTIVE
        self.is_warning = False
        self.is_violation = False
        self.last_update = ""
        self.total_warnings = 0
        self.total_violations = 0
        self.total_actions = 0
        self.warn_actions = 0
        self.return_actions = 0
        self.land_actions = 0
        self.total_errors = 0
        self.total_distance = 0.0
        self.max_altitude = 0.0
        self.max_speed = 0.0
        self.log_events = []
        self.last_event = ""
    
    @Slot(bool)
    def update_active(self, is_active):
        """Aktiven Status aktualisieren."""
        self.is_active = is_active
    
    @Slot(bool, str)
    def update_error(self, is_error, error_message):
        """Fehlerstatus aktualisieren."""
        self.is_error = is_error
        self.error_message = error_message
    
    @Slot(str)
    def update_type(self, type):
        """Geofence-Typ aktualisieren."""
        self.type = type
    
    @Slot(str)
    def update_status(self, status):
        """Status aktualisieren."""
        self.status = status
    
    @Slot(bool)
    def update_warning(self, is_warning):
        """Warnstatus aktualisieren."""
        self.is_warning = is_warning
    
    @Slot(bool)
    def update_violation(self, is_violation):
        """Verletzungsstatus aktualisieren."""
        self.is_violation = is_violation
    
    @Slot(str)
    def update_last_update(self, last_update):
        """Letzte Aktualisierung aktualisieren."""
        self.last_update = last_update
    
    @Slot(int)
    def update_total_warnings(self, total_warnings):
        """Gesamtwarnungen aktualisieren."""
        self.total_warnings = total_warnings
    
    @Slot(int)
    def update_total_violations(self, total_violations):
        """Gesamtverletzungen aktualisieren."""
        self.total_violations = total_violations
    
    @Slot(int)
    def update_total_actions(self, total_actions):
        """Gesamtaktionen aktualisieren."""
        self.total_actions = total_actions
    
    @Slot(int)
    def update_warn_actions(self, warn_actions):
        """Warnaktionen aktualisieren."""
        self.warn_actions = warn_actions
    
    @Slot(int)
    def update_return_actions(self, return_actions):
        """Return-Aktionen aktualisieren."""
        self.return_actions = return_actions
    
    @Slot(int)
    def update_land_actions(self, land_actions):
        """Land-Aktionen aktualisieren."""
        self.land_actions = land_actions
    
    @Slot(int)
    def update_total_errors(self, total_errors):
        """Gesamtfehler aktualisieren."""
        self.total_errors = total_errors
    
    @Slot(float)
    def update_total_distance(self, total_distance):
        """Gesamtdistanz aktualisieren."""
        self.total_distance = total_distance
    
    @Slot(float)
    def update_max_altitude(self, max_altitude):
        """Maximale Höhe aktualisieren."""
        self.max_altitude = max_altitude
    
    @Slot(float)
    def update_max_speed(self, max_speed):
        """Maximale Geschwindigkeit aktualisieren."""
        self.max_speed = max_speed
    
    @Slot(list)
    def update_log_events(self, log_events):
        """Log-Events aktualisieren."""
        self.log_events = log_events
    
    @Slot(str)
    def update_last_event(self, last_event):
        """Letztes Event aktualisieren."""
        self.last_event = last_event

class TestGeofenceIntegration(unittest.TestCase):
    """Testfälle für die Geofencing-Integration."""
    
    def setUp(self):
        """Testumgebung vorbereiten."""
        self.service = GeofenceService()
        self.viewmodel = GeofenceViewModel()
        self.view = MockGeofenceView()
        
        # ViewModel mit Service verbinden
        self.viewmodel.set_service(self.service)
        
        # View mit ViewModel verbinden
        self.viewmodel.active_changed.connect(self.view.update_active)
        self.viewmodel.error_changed.connect(self.view.update_error)
        self.viewmodel.type_changed.connect(self.view.update_type)
        self.viewmodel.status_changed.connect(self.view.update_status)
        self.viewmodel.warning_changed.connect(self.view.update_warning)
        self.viewmodel.violation_changed.connect(self.view.update_violation)
        self.viewmodel.last_update_changed.connect(self.view.update_last_update)
        self.viewmodel.total_warnings_changed.connect(self.view.update_total_warnings)
        self.viewmodel.total_violations_changed.connect(self.view.update_total_violations)
        self.viewmodel.total_actions_changed.connect(self.view.update_total_actions)
        self.viewmodel.warn_actions_changed.connect(self.view.update_warn_actions)
        self.viewmodel.return_actions_changed.connect(self.view.update_return_actions)
        self.viewmodel.land_actions_changed.connect(self.view.update_land_actions)
        self.viewmodel.total_errors_changed.connect(self.view.update_total_errors)
        self.viewmodel.total_distance_changed.connect(self.view.update_total_distance)
        self.viewmodel.max_altitude_changed.connect(self.view.update_max_altitude)
        self.viewmodel.max_speed_changed.connect(self.view.update_max_speed)
        self.viewmodel.log_events_changed.connect(self.view.update_log_events)
        self.viewmodel.last_event_changed.connect(self.view.update_last_event)
        
        # View-Signale mit ViewModel verbinden
        self.view.activation_requested.connect(self.viewmodel.activate)
        self.view.deactivation_requested.connect(self.viewmodel.deactivate)
        self.view.polygon_geofence_requested.connect(self.viewmodel.set_polygon_geofence)
        self.view.circle_geofence_requested.connect(self.viewmodel.set_circle_geofence)
        self.view.rectangle_geofence_requested.connect(self.viewmodel.set_rectangle_geofence)
        self.view.action_requested.connect(self.viewmodel.execute_action)
    
    def test_activation_flow(self):
        """Test des Aktivierungsflusses."""
        # Service aktivieren
        self.view.activation_requested.emit()
        
        # Überprüfung
        self.assertTrue(self.service._state.is_active)
        self.assertTrue(self.viewmodel.is_active)
        self.assertTrue(self.view.is_active)
        self.assertFalse(self.service._state.is_error)
        self.assertFalse(self.viewmodel.is_error)
        self.assertFalse(self.view.is_error)
        self.assertEqual(self.service._state.status, GeofenceStatus.ACTIVE)
        self.assertEqual(self.viewmodel.status, GeofenceStatus.ACTIVE)
        self.assertEqual(self.view.status, GeofenceStatus.ACTIVE)
        
        # Log überprüfen
        self.assertEqual(len(self.service._log.events), 1)
        self.assertEqual(len(self.viewmodel.log_events), 1)
        self.assertEqual(len(self.view.log_events), 1)
        self.assertEqual(self.service._log.last_event.event_type, "ACTIVATION")
        self.assertIn("ACTIVATION", self.viewmodel.last_event)
        self.assertIn("ACTIVATION", self.view.last_event)
    
    def test_deactivation_flow(self):
        """Test des Deaktivierungsflusses."""
        # Service aktivieren und deaktivieren
        self.view.activation_requested.emit()
        self.view.deactivation_requested.emit()
        
        # Überprüfung
        self.assertFalse(self.service._state.is_active)
        self.assertFalse(self.viewmodel.is_active)
        self.assertFalse(self.view.is_active)
        self.assertFalse(self.service._state.is_error)
        self.assertFalse(self.viewmodel.is_error)
        self.assertFalse(self.view.is_error)
        self.assertEqual(self.service._state.status, GeofenceStatus.INACTIVE)
        self.assertEqual(self.viewmodel.status, GeofenceStatus.INACTIVE)
        self.assertEqual(self.view.status, GeofenceStatus.INACTIVE)
        
        # Log überprüfen
        self.assertEqual(len(self.service._log.events), 2)
        self.assertEqual(len(self.viewmodel.log_events), 2)
        self.assertEqual(len(self.view.log_events), 2)
        self.assertEqual(self.service._log.last_event.event_type, "DEACTIVATION")
        self.assertIn("DEACTIVATION", self.viewmodel.last_event)
        self.assertIn("DEACTIVATION", self.view.last_event)
    
    def test_polygon_geofence_flow(self):
        """Test des Polygon-Geofence-Flusses."""
        # Service aktivieren
        self.view.activation_requested.emit()
        
        # Polygon-Geofence konfigurieren
        vertices = [
            {"lat": 48.123, "lon": 11.456},
            {"lat": 48.124, "lon": 11.456},
            {"lat": 48.124, "lon": 11.457},
            {"lat": 48.123, "lon": 11.457}
        ]
        self.view.polygon_geofence_requested.emit(vertices, 100.0, 10.0, GeofenceAction.WARN)
        
        # Überprüfung
        self.assertEqual(self.service._state.type, GeofenceType.POLYGON)
        self.assertEqual(self.viewmodel.type, GeofenceType.POLYGON)
        self.assertEqual(self.view.type, GeofenceType.POLYGON)
        self.assertEqual(len(self.service._state.vertices), 4)
        self.assertEqual(len(self.viewmodel.vertices), 4)
        self.assertEqual(self.service._state.max_altitude, 100.0)
        self.assertEqual(self.viewmodel.max_altitude, 100.0)
        self.assertEqual(self.view.max_altitude, 100.0)
        self.assertEqual(self.service._state.buffer_zone, 10.0)
        self.assertEqual(self.viewmodel.buffer_zone, 10.0)
        self.assertEqual(self.service._state.action, GeofenceAction.WARN)
        self.assertEqual(self.viewmodel.action, GeofenceAction.WARN)
        
        # Log überprüfen
        self.assertEqual(len(self.service._log.events), 2)
        self.assertEqual(len(self.viewmodel.log_events), 2)
        self.assertEqual(len(self.view.log_events), 2)
        self.assertEqual(self.service._log.last_event.event_type, "CONFIGURATION")
        self.assertIn("CONFIGURATION", self.viewmodel.last_event)
        self.assertIn("CONFIGURATION", self.view.last_event)
    
    def test_circle_geofence_flow(self):
        """Test des Circle-Geofence-Flusses."""
        # Service aktivieren
        self.view.activation_requested.emit()
        
        # Circle-Geofence konfigurieren
        center = {"lat": 48.123, "lon": 11.456}
        self.view.circle_geofence_requested.emit(center, 1000.0, 100.0, 10.0, GeofenceAction.RETURN)
        
        # Überprüfung
        self.assertEqual(self.service._state.type, GeofenceType.CIRCLE)
        self.assertEqual(self.viewmodel.type, GeofenceType.CIRCLE)
        self.assertEqual(self.view.type, GeofenceType.CIRCLE)
        self.assertEqual(self.service._state.center, center)
        self.assertEqual(self.viewmodel.center, center)
        self.assertEqual(self.service._state.radius, 1000.0)
        self.assertEqual(self.viewmodel.radius, 1000.0)
        self.assertEqual(self.service._state.max_altitude, 100.0)
        self.assertEqual(self.viewmodel.max_altitude, 100.0)
        self.assertEqual(self.view.max_altitude, 100.0)
        self.assertEqual(self.service._state.buffer_zone, 10.0)
        self.assertEqual(self.viewmodel.buffer_zone, 10.0)
        self.assertEqual(self.service._state.action, GeofenceAction.RETURN)
        self.assertEqual(self.viewmodel.action, GeofenceAction.RETURN)
        
        # Log überprüfen
        self.assertEqual(len(self.service._log.events), 2)
        self.assertEqual(len(self.viewmodel.log_events), 2)
        self.assertEqual(len(self.view.log_events), 2)
        self.assertEqual(self.service._log.last_event.event_type, "CONFIGURATION")
        self.assertIn("CONFIGURATION", self.viewmodel.last_event)
        self.assertIn("CONFIGURATION", self.view.last_event)
    
    def test_rectangle_geofence_flow(self):
        """Test des Rectangle-Geofence-Flusses."""
        # Service aktivieren
        self.view.activation_requested.emit()
        
        # Rectangle-Geofence konfigurieren
        corners = {
            "north": 48.124,
            "south": 48.123,
            "east": 11.457,
            "west": 11.456
        }
        self.view.rectangle_geofence_requested.emit(corners, 100.0, 10.0, GeofenceAction.LAND)
        
        # Überprüfung
        self.assertEqual(self.service._state.type, GeofenceType.RECTANGLE)
        self.assertEqual(self.viewmodel.type, GeofenceType.RECTANGLE)
        self.assertEqual(self.view.type, GeofenceType.RECTANGLE)
        self.assertEqual(self.service._state.corners, corners)
        self.assertEqual(self.viewmodel.corners, corners)
        self.assertEqual(self.service._state.max_altitude, 100.0)
        self.assertEqual(self.viewmodel.max_altitude, 100.0)
        self.assertEqual(self.view.max_altitude, 100.0)
        self.assertEqual(self.service._state.buffer_zone, 10.0)
        self.assertEqual(self.viewmodel.buffer_zone, 10.0)
        self.assertEqual(self.service._state.action, GeofenceAction.LAND)
        self.assertEqual(self.viewmodel.action, GeofenceAction.LAND)
        
        # Log überprüfen
        self.assertEqual(len(self.service._log.events), 2)
        self.assertEqual(len(self.viewmodel.log_events), 2)
        self.assertEqual(len(self.view.log_events), 2)
        self.assertEqual(self.service._log.last_event.event_type, "CONFIGURATION")
        self.assertIn("CONFIGURATION", self.viewmodel.last_event)
        self.assertIn("CONFIGURATION", self.view.last_event)
    
    def test_position_update_flow(self):
        """Test des Positionsaktualisierungsflusses."""
        # Service aktivieren und Circle-Geofence konfigurieren
        self.view.activation_requested.emit()
        center = {"lat": 48.123, "lon": 11.456}
        self.view.circle_geofence_requested.emit(center, 1000.0, 100.0, 10.0, GeofenceAction.WARN)
        
        # Position innerhalb der Geofence
        position = {"lat": 48.123, "lon": 11.456, "alt": 50.0}
        self.viewmodel.update_position(position)
        self.assertFalse(self.service._state.is_warning)
        self.assertFalse(self.viewmodel.is_warning)
        self.assertFalse(self.view.is_warning)
        self.assertFalse(self.service._state.is_violation)
        self.assertFalse(self.viewmodel.is_violation)
        self.assertFalse(self.view.is_violation)
        
        # Position in der Pufferzone
        position = {"lat": 48.123, "lon": 11.466, "alt": 50.0}
        self.viewmodel.update_position(position)
        self.assertTrue(self.service._state.is_warning)
        self.assertTrue(self.viewmodel.is_warning)
        self.assertTrue(self.view.is_warning)
        self.assertFalse(self.service._state.is_violation)
        self.assertFalse(self.viewmodel.is_violation)
        self.assertFalse(self.view.is_violation)
        
        # Position außerhalb der Geofence
        position = {"lat": 48.123, "lon": 11.476, "alt": 50.0}
        self.viewmodel.update_position(position)
        self.assertTrue(self.service._state.is_warning)
        self.assertTrue(self.viewmodel.is_warning)
        self.assertTrue(self.view.is_warning)
        self.assertTrue(self.service._state.is_violation)
        self.assertTrue(self.viewmodel.is_violation)
        self.assertTrue(self.view.is_violation)
        
        # Log überprüfen
        self.assertEqual(len(self.service._log.events), 4)  # Aktivierung + 3 Positionen
        self.assertEqual(len(self.viewmodel.log_events), 4)
        self.assertEqual(len(self.view.log_events), 4)
        self.assertEqual(self.service._log.last_event.event_type, "VIOLATION")
        self.assertIn("VIOLATION", self.viewmodel.last_event)
        self.assertIn("VIOLATION", self.view.last_event)
    
    def test_action_flow(self):
        """Test des Aktionsflusses."""
        # Service aktivieren und Circle-Geofence konfigurieren
        self.view.activation_requested.emit()
        center = {"lat": 48.123, "lon": 11.456}
        self.view.circle_geofence_requested.emit(center, 1000.0, 100.0, 10.0, GeofenceAction.WARN)
        
        # Position in der Pufferzone
        position = {"lat": 48.123, "lon": 11.466, "alt": 50.0}
        self.viewmodel.update_position(position)
        
        # Aktion ausführen
        self.view.action_requested.emit()
        
        # Überprüfung
        self.assertEqual(self.service._statistics.warn_actions, 1)
        self.assertEqual(self.viewmodel.warn_actions, 1)
        self.assertEqual(self.view.warn_actions, 1)
        self.assertEqual(self.service._statistics.total_actions, 1)
        self.assertEqual(self.viewmodel.total_actions, 1)
        self.assertEqual(self.view.total_actions, 1)
        
        # Log überprüfen
        self.assertEqual(len(self.service._log.events), 3)
        self.assertEqual(len(self.viewmodel.log_events), 3)
        self.assertEqual(len(self.view.log_events), 3)
        self.assertEqual(self.service._log.last_event.event_type, "ACTION")
        self.assertIn("ACTION", self.viewmodel.last_event)
        self.assertIn("ACTION", self.view.last_event)
    
    def test_error_flow(self):
        """Test des Fehlerflusses."""
        # Service aktivieren
        self.view.activation_requested.emit()
        
        # Fehler simulieren
        self.service._handle_error("Test error")
        
        # Überprüfung
        self.assertTrue(self.service._state.is_error)
        self.assertTrue(self.viewmodel.is_error)
        self.assertTrue(self.view.is_error)
        self.assertEqual(self.service._state.error_message, "Test error")
        self.assertEqual(self.viewmodel.error_message, "Test error")
        self.assertEqual(self.view.error_message, "Test error")
        self.assertEqual(self.service._statistics.total_errors, 1)
        self.assertEqual(self.viewmodel.total_errors, 1)
        self.assertEqual(self.view.total_errors, 1)
        
        # Log überprüfen
        self.assertEqual(len(self.service._log.events), 2)
        self.assertEqual(len(self.viewmodel.log_events), 2)
        self.assertEqual(len(self.view.log_events), 2)
        self.assertEqual(self.service._log.last_event.event_type, "ERROR")
        self.assertIn("ERROR", self.viewmodel.last_event)
        self.assertIn("ERROR", self.view.last_event)
        
        # Fehler zurücksetzen
        self.service._reset_error()
        
        # Überprüfung
        self.assertFalse(self.service._state.is_error)
        self.assertFalse(self.viewmodel.is_error)
        self.assertFalse(self.view.is_error)
        self.assertIsNone(self.service._state.error_message)
        self.assertEqual(self.viewmodel.error_message, "")
        self.assertEqual(self.view.error_message, "")

if __name__ == "__main__":
    unittest.main() 