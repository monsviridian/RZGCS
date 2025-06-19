"""Integrationstests für die Flugsteuerung.

Diese Tests überprüfen die Integration zwischen:
- Service und ViewModel
- ViewModel und View
- Datenmodellen und Service
- Service und Logging
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

class TestFlightControlIntegration(unittest.TestCase):
    """Integrationstests für die Flugsteuerung."""
    
    def setUp(self):
        """Test-Setup."""
        self.service = FlightControlService()
        self.viewmodel = FlightControlViewModel()
        self.viewmodel.set_service(self.service)
    
    def test_service_viewmodel_integration(self):
        """Teste Service-ViewModel-Integration."""
        # Service-Status ändern
        self.service.activate()
        
        # ViewModel-Status prüfen
        self.assertTrue(self.viewmodel.is_active)
        self.assertEqual(self.viewmodel.status, FlightStatus.READY.value)
        
        # Service-Status ändern
        self.service.arm()
        
        # ViewModel-Status prüfen
        self.assertTrue(self.viewmodel.is_armed)
        self.assertEqual(self.viewmodel.status, FlightStatus.ARMED.value)
    
    def test_viewmodel_service_integration(self):
        """Teste ViewModel-Service-Integration."""
        # ViewModel-Befehl ausführen
        self.viewmodel.activate()
        
        # Service-Status prüfen
        self.assertTrue(self.service._state.is_active)
        self.assertEqual(self.service._state.status, FlightStatus.READY)
        
        # ViewModel-Befehl ausführen
        self.viewmodel.arm()
        
        # Service-Status prüfen
        self.assertTrue(self.service._state.is_armed)
        self.assertEqual(self.service._state.status, FlightStatus.ARMED)
    
    def test_data_service_integration(self):
        """Teste Daten-Service-Integration."""
        # Service-Status ändern
        self.service.activate()
        
        # Daten-Status prüfen
        self.assertTrue(self.service._state.is_active)
        self.assertEqual(self.service._state.status, FlightStatus.READY)
        
        # Service-Status ändern
        self.service.arm()
        
        # Daten-Status prüfen
        self.assertTrue(self.service._state.is_armed)
        self.assertEqual(self.service._state.status, FlightStatus.ARMED)
    
    def test_service_logging_integration(self):
        """Teste Service-Logging-Integration."""
        # Service-Operationen ausführen
        self.service.activate()
        self.service.arm()
        self.service.takeoff()
        self.service.land()
        self.service.disarm()
        
        # Logging prüfen
        self.assertGreater(len(self.service._log.events), 0)
        self.assertIsNotNone(self.service._log.last_event)
        
        # Event-Typen prüfen
        event_types = [event.event_type for event in self.service._log.events]
        self.assertIn("ACTIVATE", event_types)
        self.assertIn("ARM", event_types)
        self.assertIn("TAKEOFF", event_types)
        self.assertIn("LAND", event_types)
        self.assertIn("DISARM", event_types)
    
    def test_complete_flow(self):
        """Teste kompletten Flugablauf."""
        # Aktivierung
        self.viewmodel.activate()
        self.assertTrue(self.viewmodel.is_active)
        self.assertEqual(self.viewmodel.status, FlightStatus.READY.value)
        
        # Arming
        self.viewmodel.arm()
        self.assertTrue(self.viewmodel.is_armed)
        self.assertEqual(self.viewmodel.status, FlightStatus.ARMED.value)
        
        # Start
        self.viewmodel.takeoff()
        self.assertTrue(self.viewmodel.is_taking_off)
        self.assertEqual(self.viewmodel.status, FlightStatus.TAKING_OFF.value)
        
        # Flug
        self.assertTrue(self.viewmodel.is_flying)
        self.assertEqual(self.viewmodel.status, FlightStatus.FLYING.value)
        
        # Landung
        self.viewmodel.land()
        self.assertTrue(self.viewmodel.is_landing)
        self.assertEqual(self.viewmodel.status, FlightStatus.LANDING.value)
        
        # Disarming
        self.viewmodel.disarm()
        self.assertFalse(self.viewmodel.is_armed)
        self.assertEqual(self.viewmodel.status, FlightStatus.READY.value)
        
        # Deaktivierung
        self.viewmodel.deactivate()
        self.assertFalse(self.viewmodel.is_active)
        self.assertEqual(self.viewmodel.status, FlightStatus.INACTIVE.value)
        
        # Statistiken prüfen
        self.assertEqual(self.viewmodel.total_flights, "1")
        self.assertEqual(self.viewmodel.total_landings, "1")
        self.assertEqual(self.viewmodel.total_takeoffs, "1")
        
        # Logging prüfen
        self.assertGreater(len(self.viewmodel.log_events), 0)
        self.assertNotEqual(self.viewmodel.last_event, "")
    
    def test_error_flow(self):
        """Teste Fehlerablauf."""
        # Ungültige Operation
        with self.assertRaises(FlightValidationError):
            self.viewmodel.arm()  # Arming ohne Aktivierung
        
        # Fehlerstatus prüfen
        self.assertTrue(self.viewmodel.is_error)
        self.assertNotEqual(self.viewmodel.error_message, "")
        self.assertEqual(self.viewmodel.status, FlightStatus.ERROR.value)
        
        # Logging prüfen
        self.assertGreater(len(self.viewmodel.log_events), 0)
        self.assertNotEqual(self.viewmodel.last_event, "")
        
        # Fehler beheben
        self.viewmodel.activate()
        self.viewmodel.arm()
        
        # Fehlerstatus prüfen
        self.assertFalse(self.viewmodel.is_error)
        self.assertEqual(self.viewmodel.error_message, "")
        self.assertEqual(self.viewmodel.status, FlightStatus.ARMED.value)

if __name__ == '__main__':
    unittest.main() 