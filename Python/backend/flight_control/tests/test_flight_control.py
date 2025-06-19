"""Flugsteuerungs-Tests.

Dieses Modul enthält die Tests für die Flugsteuerungskomponenten.
"""

import unittest
from unittest.mock import MagicMock, patch

from flight_control.models.flight_control_data import (
    FlightMode,
    ControlMode,
    ControlAxis,
    ControlCommand,
    ControlStatus,
    ControlInput,
    ControlOutput,
    ControlState,
    ControlEvent,
    ControlLog,
    FlightControlError,
    FlightControlValidationError,
    FlightControlCommandError,
    FlightControlStateError
)
from flight_control.services.flight_control_service import FlightControlService
from flight_control.viewmodels.flight_control_viewmodel import FlightControlViewModel
from flight_control.controllers.flight_control_controller import FlightControlController

class TestFlightControlService(unittest.TestCase):
    """Tests für den Flugsteuerungs-Service."""
    
    def setUp(self):
        """Test-Setup."""
        self.service = FlightControlService()
    
    def test_initial_state(self):
        """Test des initialen Zustands."""
        self.assertEqual(self.service.state.mode, FlightMode.MANUAL)
        self.assertEqual(self.service.state.control_mode, ControlMode.POSITION)
        self.assertEqual(self.service.state.status, ControlStatus.IDLE)
    
    def test_set_mode(self):
        """Test des Setzens des Flugmodus."""
        self.service.set_mode(FlightMode.ASSISTED)
        self.assertEqual(self.service.state.mode, FlightMode.ASSISTED)
    
    def test_set_control_mode(self):
        """Test des Setzens des Steuerungsmodus."""
        self.service.set_control_mode(ControlMode.VELOCITY)
        self.assertEqual(self.service.state.control_mode, ControlMode.VELOCITY)
    
    def test_hold_position(self):
        """Test des Haltens der Position."""
        self.service.hold_position()
        self.assertEqual(self.service.state.status, ControlStatus.ACTIVE)
    
    def test_move_to_position(self):
        """Test des Bewegens zu einer Position."""
        position = {
            'latitude': 48.137154,
            'longitude': 11.576124,
            'altitude': 100.0
        }
        self.service.move_to_position(position)
        self.assertEqual(self.service.state.status, ControlStatus.ACTIVE)
    
    def test_rotate_to_attitude(self):
        """Test des Rotierens zu einer Attitude."""
        attitude = {
            'roll': 0.0,
            'pitch': 0.0,
            'yaw': 0.0
        }
        self.service.rotate_to_attitude(attitude)
        self.assertEqual(self.service.state.status, ControlStatus.ACTIVE)
    
    def test_set_thrust(self):
        """Test des Setzens des Schubs."""
        self.service.set_thrust(0.5)
        self.assertEqual(self.service.state.status, ControlStatus.ACTIVE)
    
    def test_emergency_stop(self):
        """Test des Notstopps."""
        self.service.emergency_stop()
        self.assertEqual(self.service.state.mode, FlightMode.EMERGENCY)
        self.assertEqual(self.service.state.status, ControlStatus.ACTIVE)

class TestFlightControlViewModel(unittest.TestCase):
    """Tests für das Flugsteuerungs-ViewModel."""
    
    def setUp(self):
        """Test-Setup."""
        self.service = MagicMock(spec=FlightControlService)
        self.view_model = FlightControlViewModel()
        self.view_model.set_service(self.service)
    
    def test_initial_state(self):
        """Test des initialen Zustands."""
        self.assertIsNone(self.view_model._state)
        self.assertIsNone(self.view_model._log)
    
    def test_set_mode(self):
        """Test des Setzens des Flugmodus."""
        self.view_model.set_mode("ASSISTED")
        self.service.set_mode.assert_called_once_with(FlightMode.ASSISTED)
    
    def test_set_control_mode(self):
        """Test des Setzens des Steuerungsmodus."""
        self.view_model.set_control_mode("VELOCITY")
        self.service.set_control_mode.assert_called_once_with(ControlMode.VELOCITY)
    
    def test_hold_position(self):
        """Test des Haltens der Position."""
        self.view_model.hold_position()
        self.service.hold_position.assert_called_once()
    
    def test_move_to_position(self):
        """Test des Bewegens zu einer Position."""
        position = {
            'latitude': 48.137154,
            'longitude': 11.576124,
            'altitude': 100.0
        }
        self.view_model.move_to_position(position)
        self.service.move_to_position.assert_called_once_with(position)
    
    def test_rotate_to_attitude(self):
        """Test des Rotierens zu einer Attitude."""
        attitude = {
            'roll': 0.0,
            'pitch': 0.0,
            'yaw': 0.0
        }
        self.view_model.rotate_to_attitude(attitude)
        self.service.rotate_to_attitude.assert_called_once_with(attitude)
    
    def test_set_thrust(self):
        """Test des Setzens des Schubs."""
        self.view_model.set_thrust(0.5)
        self.service.set_thrust.assert_called_once_with(0.5)
    
    def test_emergency_stop(self):
        """Test des Notstopps."""
        self.view_model.emergency_stop()
        self.service.emergency_stop.assert_called_once()

class TestFlightControlController(unittest.TestCase):
    """Tests für den Flugsteuerungs-Controller."""
    
    def setUp(self):
        """Test-Setup."""
        self.controller = FlightControlController()
    
    def test_get_view_model(self):
        """Test des Abrufens des ViewModels."""
        view_model = self.controller.get_view_model()
        self.assertIsInstance(view_model, FlightControlViewModel)
        self.assertIsNotNone(view_model._service)

if __name__ == '__main__':
    unittest.main() 