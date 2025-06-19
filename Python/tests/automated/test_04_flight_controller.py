#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for the Flight View Controller component
"""

import unittest
import sys
import os
from unittest.mock import MagicMock, patch

# Add parent directory to path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.flight_view_controller import FlightViewController

class TestFlightViewController(unittest.TestCase):
    """Test cases for the FlightViewController class"""
    
    def setUp(self):
        """Set up test environment"""
        self.engine = MagicMock()
        self.controller = FlightViewController(self.engine)
    
    def test_initialization(self):
        """Test FlightViewController initialization"""
        # Check default drone position (Frankfurt coordinates)
        self.assertEqual(self.controller._drone_lat, 50.110924)
        self.assertEqual(self.controller._drone_lon, 8.682127)
        self.assertEqual(self.controller._drone_alt, 100.0)
        self.assertEqual(self.controller._drone_heading, 45.0)
        
        # Check other default values
        self.assertFalse(self.controller._is_connected)
        self.assertEqual(self.controller._map_type, 1)  # 3D view
    
    def test_update_drone_position(self):
        """Test updating drone position"""
        # Mock the signals
        self.controller.dronePositionChanged = MagicMock()
        self.controller.droneHeadingChanged = MagicMock()
        
        # Update drone position
        self.controller.update_drone_position(51.0, 9.0, 200.0, 90.0)
        
        # Check that the drone position was updated
        self.assertEqual(self.controller._drone_lat, 51.0)
        self.assertEqual(self.controller._drone_lon, 9.0)
        self.assertEqual(self.controller._drone_alt, 200.0)
        self.assertEqual(self.controller._drone_heading, 90.0)
        
        # Check that the signals were emitted
        self.controller.dronePositionChanged.emit.assert_called_once_with(51.0, 9.0, 200.0)
        self.controller.droneHeadingChanged.emit.assert_called_once_with(90.0)
    
    def test_on_connection_changed(self):
        """Test connection status change handling"""
        # Mock the signals
        self.controller.dronePositionChanged = MagicMock()
        self.controller.droneHeadingChanged = MagicMock()
        
        # Start with not connected
        self.assertFalse(self.controller._is_connected)
        
        # Connect
        self.controller.on_connection_changed(True)
        self.assertTrue(self.controller._is_connected)
        
        # Disconnect
        self.controller.on_connection_changed(False)
        self.assertFalse(self.controller._is_connected)
        
        # Check that the drone position was reset to Frankfurt coordinates
        self.assertEqual(self.controller._drone_lat, 50.110924)
        self.assertEqual(self.controller._drone_lon, 8.682127)
        self.assertEqual(self.controller._drone_alt, 100.0)
        self.assertEqual(self.controller._drone_heading, 45.0)
        
        # Check that the signals were emitted for the reset
        self.controller.dronePositionChanged.emit.assert_called_with(50.110924, 8.682127, 100.0)
        self.controller.droneHeadingChanged.emit.assert_called_with(45.0)
    
    @patch('backend.flight_view_controller.FlightViewController.update_drone_position')
    def test_simulate_drone_movement(self, mock_update_drone_position):
        """Test drone movement simulation"""
        # Set connected state
        self.controller._is_connected = True
        
        # Run simulation
        self.controller.simulate_drone_movement()
        
        # Check that update_drone_position was called
        mock_update_drone_position.assert_called_once()
    
    def test_set_map_type(self):
        """Test setting map type"""
        # Mock the signal
        self.controller.mapTypeChanged = MagicMock()
        
        # Set map type to 2D view
        self.controller.set_map_type(0)
        self.assertEqual(self.controller._map_type, 0)
        
        # Check that the signal was emitted
        self.controller.mapTypeChanged.emit.assert_called_once_with(0)

if __name__ == '__main__':
    unittest.main()
