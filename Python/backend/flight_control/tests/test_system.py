"""Systemtests für die Flugsteuerung.

Diese Tests überprüfen das Gesamtsystem:
- Komponenten-Integration
- Datenfluss
- Fehlerbehandlung
- Performance
- Stabilität
"""

import unittest
import time
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

class TestFlightControlSystem(unittest.TestCase):
    """Systemtests für die Flugsteuerung."""
    
    def setUp(self):
        """Test-Setup."""
        self.service = FlightControlService()
        self.viewmodel = FlightControlViewModel()
        self.viewmodel.set_service(self.service)
    
    def test_component_integration(self):
        """Teste Komponenten-Integration."""
        # Service-Initialisierung
        self.assertIsNotNone(self.service)
        self.assertIsNotNone(self.service._state)
        self.assertIsNotNone(self.service._statistics)
        self.assertIsNotNone(self.service._log)
        
        # ViewModel-Initialisierung
        self.assertIsNotNone(self.viewmodel)
        self.assertIsNotNone(self.viewmodel._service)
        
        # Service-ViewModel-Verbindung
        self.assertEqual(self.viewmodel._service, self.service)
    
    def test_data_flow(self):
        """Teste Datenfluss."""
        # Service -> ViewModel
        self.service.activate()
        self.assertTrue(self.viewmodel.is_active)
        
        self.service.arm()
        self.assertTrue(self.viewmodel.is_armed)
        
        # ViewModel -> Service
        self.viewmodel.set_mode(FlightMode.ALTHOLD.value)
        self.assertEqual(self.service._state.mode, FlightMode.ALTHOLD)
        
        self.viewmodel.takeoff()
        self.assertTrue(self.service._state.is_taking_off)
    
    def test_error_handling(self):
        """Teste Fehlerbehandlung."""
        # Service-Fehler
        with self.assertRaises(FlightValidationError):
            self.service.arm()  # Arming ohne Aktivierung
        
        self.assertTrue(self.service._state.is_error)
        self.assertIsNotNone(self.service._state.error_message)
        
        # ViewModel-Fehler
        with self.assertRaises(FlightValidationError):
            self.viewmodel.arm()  # Arming ohne Aktivierung
        
        self.assertTrue(self.viewmodel.is_error)
        self.assertNotEqual(self.viewmodel.error_message, "")
        
        # Fehlerbehebung
        self.service.activate()
        self.service.arm()
        
        self.assertFalse(self.service._state.is_error)
        self.assertIsNone(self.service._state.error_message)
        
        self.assertFalse(self.viewmodel.is_error)
        self.assertEqual(self.viewmodel.error_message, "")
    
    def test_performance(self):
        """Teste Performance."""
        start_time = time.time()
        
        # Schnelle Operationen
        for _ in range(100):
            self.service.activate()
            self.service.deactivate()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Performance-Anforderung: < 1 Sekunde für 100 Operationen
        self.assertLess(duration, 1.0)
    
    def test_stability(self):
        """Teste Stabilität."""
        # Viele Operationen
        for _ in range(1000):
            try:
                self.service.activate()
                self.service.arm()
                self.service.takeoff()
                self.service.land()
                self.service.disarm()
                self.service.deactivate()
            except FlightError:
                self.fail("Stabilitätstest fehlgeschlagen")
        
        # Zustand prüfen
        self.assertFalse(self.service._state.is_active)
        self.assertFalse(self.service._state.is_error)
        self.assertIsNone(self.service._state.error_message)
        self.assertEqual(self.service._state.mode, FlightMode.STABILIZE)
        self.assertEqual(self.service._state.status, FlightStatus.INACTIVE)
        self.assertFalse(self.service._state.is_armed)
        self.assertFalse(self.service._state.is_flying)
        self.assertFalse(self.service._state.is_landing)
        self.assertFalse(self.service._state.is_taking_off)
    
    def test_concurrent_operations(self):
        """Teste gleichzeitige Operationen."""
        # Schnelle Moduswechsel
        self.service.activate()
        self.service.arm()
        
        for mode in [FlightMode.STABILIZE, FlightMode.ALTHOLD, FlightMode.LOITER]:
            self.service.set_mode(mode)
            self.assertEqual(self.service._state.mode, mode)
        
        # Schnelle Statusänderungen
        self.service.takeoff()
        self.service.land()
        self.service.disarm()
        
        # Zustand prüfen
        self.assertTrue(self.service._state.is_active)
        self.assertFalse(self.service._state.is_error)
        self.assertIsNone(self.service._state.error_message)
        self.assertEqual(self.service._state.mode, FlightMode.LOITER)
        self.assertEqual(self.service._state.status, FlightStatus.READY)
        self.assertFalse(self.service._state.is_armed)
        self.assertFalse(self.service._state.is_flying)
        self.assertFalse(self.service._state.is_landing)
        self.assertFalse(self.service._state.is_taking_off)
    
    def test_resource_management(self):
        """Teste Ressourcenverwaltung."""
        # Viele Events
        for _ in range(1000):
            self.service._log.add_event(FlightEvent(
                timestamp=datetime.now(),
                event_type="TEST",
                description="Test Event"
            ))
        
        # Speichernutzung prüfen
        self.assertLess(len(self.service._log.events), 1000)  # Log sollte begrenzt sein
        
        # Statistiken
        self.assertIsNotNone(self.service._statistics)
        self.assertIsInstance(self.service._statistics, FlightStatistics)
        
        # Zustand
        self.assertIsNotNone(self.service._state)
        self.assertIsInstance(self.service._state, FlightState)

if __name__ == '__main__':
    unittest.main() 