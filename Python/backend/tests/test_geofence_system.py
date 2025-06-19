"""Systemtests für das Geofencing."""

import unittest
import time
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

class TestGeofenceSystem(unittest.TestCase):
    """Testfälle für das Geofencing-System."""
    
    def setUp(self):
        """Testumgebung vorbereiten."""
        self.service = GeofenceService()
        self.viewmodel = GeofenceViewModel()
        self.viewmodel.set_service(self.service)
    
    def test_end_to_end_scenario(self):
        """Test des End-to-End-Szenarios."""
        # Service aktivieren
        self.service.activate()
        self.assertTrue(self.service._state.is_active)
        self.assertEqual(self.service._state.status, GeofenceStatus.ACTIVE)
        
        # Circle-Geofence konfigurieren
        center = {"lat": 48.123, "lon": 11.456}
        self.service.set_circle_geofence(center, 1000.0, 100.0, 10.0, GeofenceAction.WARN)
        self.assertEqual(self.service._state.type, GeofenceType.CIRCLE)
        self.assertEqual(self.service._state.center, center)
        self.assertEqual(self.service._state.radius, 1000.0)
        self.assertEqual(self.service._state.max_altitude, 100.0)
        self.assertEqual(self.service._state.buffer_zone, 10.0)
        self.assertEqual(self.service._state.action, GeofenceAction.WARN)
        
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
        
        # Aktion ausführen
        self.service.execute_action()
        self.assertEqual(self.service._statistics.warn_actions, 1)
        self.assertEqual(self.service._statistics.total_actions, 1)
        
        # Service deaktivieren
        self.service.deactivate()
        self.assertFalse(self.service._state.is_active)
        self.assertEqual(self.service._state.status, GeofenceStatus.INACTIVE)
        
        # Ergebnis überprüfen
        self.assertEqual(self.service._statistics.total_warnings, 1)
        self.assertEqual(self.service._statistics.total_violations, 1)
        self.assertEqual(self.service._statistics.total_actions, 1)
        self.assertEqual(self.service._statistics.warn_actions, 1)
        self.assertEqual(self.service._statistics.return_actions, 0)
        self.assertEqual(self.service._statistics.land_actions, 0)
        self.assertEqual(self.service._statistics.total_errors, 0)
        self.assertEqual(len(self.service._log.events), 6)  # Aktivierung + Konfiguration + 3 Positionen + Aktion
    
    def test_error_scenarios(self):
        """Test der Fehlerszenarien."""
        # Aktivierung im Fehlerzustand
        self.service._handle_error("Test error")
        self.service.activate()
        self.assertFalse(self.service._state.is_active)
        self.assertTrue(self.service._state.is_error)
        self.assertEqual(self.service._state.error_message, "Test error")
        
        # Fehler zurücksetzen und aktivieren
        self.service._reset_error()
        self.service.activate()
        self.assertTrue(self.service._state.is_active)
        self.assertFalse(self.service._state.is_error)
        self.assertIsNone(self.service._state.error_message)
        
        # Ungültiger Geofence-Typ
        with self.assertRaises(GeofenceTypeError):
            self.service._state.type = "INVALID"
        
        # Ungültige Geofence-Aktion
        with self.assertRaises(GeofenceValidationError):
            self.service._state.action = "INVALID"
        
        # Ungültige Position
        with self.assertRaises(GeofenceValidationError):
            self.service.update_position({"lat": "invalid", "lon": 11.456, "alt": 50.0})
        
        # Ungültige Höhe
        with self.assertRaises(GeofenceValidationError):
            self.service.update_position({"lat": 48.123, "lon": 11.456, "alt": -50.0})
    
    def test_performance(self):
        """Test der Performance."""
        # Service aktivieren
        self.service.activate()
        
        # Circle-Geofence konfigurieren
        center = {"lat": 48.123, "lon": 11.456}
        self.service.set_circle_geofence(center, 1000.0, 100.0, 10.0, GeofenceAction.WARN)
        
        # Verarbeitungszeit messen
        start_time = time.time()
        
        # 1000 Positionsaktualisierungen
        for i in range(1000):
            position = {
                "lat": 48.123 + (i * 0.0001),
                "lon": 11.456 + (i * 0.0001),
                "alt": 50.0
            }
            self.service.update_position(position)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Überprüfung
        self.assertLess(processing_time, 1.0)  # Maximal 1 Sekunde für 1000 Aktualisierungen
        self.assertEqual(len(self.service._log.events), 1002)  # Aktivierung + Konfiguration + 1000 Positionen
    
    def test_concurrent_operations(self):
        """Test von gleichzeitigen Operationen."""
        # Service aktivieren
        self.service.activate()
        
        # Circle-Geofence konfigurieren
        center = {"lat": 48.123, "lon": 11.456}
        self.service.set_circle_geofence(center, 1000.0, 100.0, 10.0, GeofenceAction.WARN)
        
        # Timer für parallele Aktualisierungen
        timer = QTimer()
        timer.setInterval(10)  # 10ms Intervall
        
        update_count = 0
        max_updates = 100
        
        def update_position():
            nonlocal update_count
            if update_count < max_updates:
                position = {
                    "lat": 48.123 + (update_count * 0.0001),
                    "lon": 11.456 + (update_count * 0.0001),
                    "alt": 50.0
                }
                self.service.update_position(position)
                update_count += 1
            else:
                timer.stop()
        
        timer.timeout.connect(update_position)
        timer.start()
        
        # Warten bis alle Aktualisierungen abgeschlossen sind
        while update_count < max_updates:
            time.sleep(0.1)
        
        # Überprüfung
        self.assertEqual(update_count, max_updates)
        self.assertEqual(len(self.service._log.events), max_updates + 2)  # Aktivierung + Konfiguration + Updates
        self.assertFalse(self.service._state.is_error)
    
    def test_recovery_scenarios(self):
        """Test der Wiederherstellungsszenarien."""
        # Service aktivieren
        self.service.activate()
        
        # Circle-Geofence konfigurieren
        center = {"lat": 48.123, "lon": 11.456}
        self.service.set_circle_geofence(center, 1000.0, 100.0, 10.0, GeofenceAction.WARN)
        
        # Fehler simulieren
        self.service._handle_error("Test error")
        self.assertTrue(self.service._state.is_error)
        self.assertEqual(self.service._state.error_message, "Test error")
        
        # Fehler zurücksetzen
        self.service._reset_error()
        self.assertFalse(self.service._state.is_error)
        self.assertIsNone(self.service._state.error_message)
        
        # Position aktualisieren
        position = {"lat": 48.123, "lon": 11.456, "alt": 50.0}
        self.service.update_position(position)
        self.assertFalse(self.service._state.is_warning)
        self.assertFalse(self.service._state.is_violation)
        
        # Service deaktivieren
        self.service.deactivate()
        self.assertFalse(self.service._state.is_active)
        self.assertEqual(self.service._state.status, GeofenceStatus.INACTIVE)
        
        # Ergebnis überprüfen
        self.assertEqual(self.service._statistics.total_errors, 1)
        self.assertEqual(len(self.service._log.events), 4)  # Aktivierung + Konfiguration + Fehler + Position

if __name__ == "__main__":
    unittest.main() 