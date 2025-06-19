#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for the Serial Connector component
"""

import unittest
import sys
import os
from unittest.mock import MagicMock, patch

# Add parent directory to path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.serial_connector import SerialConnector
from backend.sensorviewmodel import SensorViewModel
from backend.logger import Logger

class TestSerialConnector(unittest.TestCase):
    """Test cases for the SerialConnector class"""
    
    def setUp(self):
        """Set up test environment"""
        self.sensor_model = SensorViewModel()
        self.logger = Logger()
        self.parameter_model = MagicMock()
        self.serial_connector = SerialConnector(self.sensor_model, self.logger, self.parameter_model)
    
    def test_initialization(self):
        """Test SerialConnector initialization"""
        self.assertFalse(self.serial_connector.connected)
        self.assertEqual(self.serial_connector.port, "")
        self.assertEqual(self.serial_connector.baudRate, 115200)
    
    def test_set_port(self):
        """Test setting the port"""
        self.serial_connector.setPort("COM1")
        self.assertEqual(self.serial_connector.port, "COM1")
    
    def test_set_baud_rate(self):
        """Test setting the baud rate"""
        self.serial_connector.setBaudRate(9600)
        self.assertEqual(self.serial_connector.baudRate, 9600)
    
    @patch('backend.serial_connector.SerialConnector._open_connection')
    def test_connect(self, mock_open_connection):
        """Test connecting"""
        # Mock the _open_connection method to avoid actual hardware interaction
        mock_open_connection.return_value = True
        
        self.serial_connector.setPort("COM1")
        self.serial_connector.connect()
        mock_open_connection.assert_called_once()
    
    @patch('backend.serial_connector.SerialConnector._close_connection')
    def test_disconnect(self, mock_close_connection):
        """Test disconnecting"""
        # First set the connection state to True
        self.serial_connector._connected = True
        
        self.serial_connector.disconnect()
        mock_close_connection.assert_called_once()
        self.assertFalse(self.serial_connector.connected)
    
    def test_update_gps(self):
        """Test updating GPS coordinates"""
        # Add GPS sensors to the model
        self.sensor_model.add_sensor("gps_lat", "GPS Latitude", "°")
        self.sensor_model.add_sensor("gps_lon", "GPS Longitude", "°")
        
        # Mock the gps_msg signal
        self.serial_connector.gps_msg = MagicMock()
        
        # Update GPS coordinates
        self.serial_connector.update_gps(50.110924, 8.682127)
        
        # Check that the model was updated
        self.assertEqual(self.sensor_model.get_sensor_value("gps_lat"), 50.110924)
        self.assertEqual(self.sensor_model.get_sensor_value("gps_lon"), 8.682127)
        
        # Check that the signal was emitted
        self.serial_connector.gps_msg.emit.assert_called_once_with(50.110924, 8.682127)
    
    def test_request_gps_data(self):
        """Test requesting GPS data"""
        # Add GPS sensors to the model
        self.sensor_model.add_sensor("gps_lat", "GPS Latitude", "°")
        self.sensor_model.add_sensor("gps_lon", "GPS Longitude", "°")
        self.sensor_model.add_sensor("altitude", "Altitude", "m")
        
        # Update sensor values
        self.sensor_model.update_sensor("gps_lat", 50.110924)
        self.sensor_model.update_sensor("gps_lon", 8.682127)
        self.sensor_model.update_sensor("altitude", 100.0)
        
        # Mock the gpsChanged signal
        self.serial_connector.gpsChanged = MagicMock()
        
        # Set connected state
        self.serial_connector._connected = True
        
        # Request GPS data
        self.serial_connector.request_gps_data()
        
        # Check that the signal was emitted with the correct values
        self.serial_connector.gpsChanged.emit.assert_called_once_with(50.110924, 8.682127, 100.0)

if __name__ == '__main__':
    unittest.main()
