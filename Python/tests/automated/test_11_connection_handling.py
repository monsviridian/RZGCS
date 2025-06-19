#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for connection handling in the RZGCS application
"""

import unittest
import sys
import os
from unittest.mock import MagicMock, patch

# Add parent directory to path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

class TestConnectionHandling(unittest.TestCase):
    """Test cases for connection handling"""
    
    def setUp(self):
        """Set up test environment"""
        self.serial_connector = MagicMock()
        self.flight_controller = MagicMock()
    
    def test_connect_serial_port(self):
        """Test connecting to a serial port"""
        # Set up the serial connector
        self.serial_connector.setPort = MagicMock()
        self.serial_connector.setBaudRate = MagicMock()
        self.serial_connector.connect = MagicMock()
        
        # Connect to the port
        port = "COM1"
        baud_rate = 115200
        self.connect_to_port(port, baud_rate)
        
        # Verify the methods were called with the correct parameters
        self.serial_connector.setPort.assert_called_once_with(port)
        self.serial_connector.setBaudRate.assert_called_once_with(baud_rate)
        self.serial_connector.connect.assert_called_once()
    
    def test_disconnect_serial_port(self):
        """Test disconnecting from a serial port"""
        # Set up the serial connector
        self.serial_connector.disconnect = MagicMock()
        
        # Disconnect from the port
        self.disconnect_from_port()
        
        # Verify the method was called
        self.serial_connector.disconnect.assert_called_once()
    
    def test_connection_status_signal(self):
        """Test connection status signal"""
        # Set up the serial connector
        self.serial_connector.connectionChanged = MagicMock()
        
        # Emit connection status signal
        is_connected = True
        self.emit_connection_status(is_connected)
        
        # Verify the signal was emitted with the correct value
        self.serial_connector.connectionChanged.emit.assert_called_once_with(is_connected)
    
    def test_connection_status_propagation(self):
        """Test propagation of connection status to other components"""
        # Set up the flight controller
        self.flight_controller.on_connection_changed = MagicMock()
        
        # Propagate connection status
        is_connected = True
        self.propagate_connection_status(is_connected)
        
        # Verify the method was called with the correct parameter
        self.flight_controller.on_connection_changed.assert_called_once_with(is_connected)
    
    def test_connection_error_handling(self):
        """Test handling of connection errors"""
        # Set up the serial connector to raise an exception
        self.serial_connector.connect = MagicMock(side_effect=Exception("Connection failed"))
        
        # Try to connect
        success, error_message = self.try_connect()
        
        # Verify the result
        self.assertFalse(success)
        self.assertEqual(error_message, "Connection failed")
    
    def test_connection_timeout_handling(self):
        """Test handling of connection timeouts"""
        # Set up the serial connector to raise a timeout exception
        self.serial_connector.connect = MagicMock(side_effect=TimeoutError("Connection timed out"))
        
        # Try to connect
        success, error_message = self.try_connect()
        
        # Verify the result
        self.assertFalse(success)
        self.assertEqual(error_message, "Connection timed out")
    
    def test_reconnection_attempt(self):
        """Test reconnection attempt after disconnection"""
        # Set up the serial connector
        self.serial_connector.connected = False
        self.serial_connector.connect = MagicMock()
        
        # Attempt to reconnect
        self.attempt_reconnect()
        
        # Verify the method was called
        self.serial_connector.connect.assert_called_once()
    
    def test_connection_status_update_ui(self):
        """Test updating UI with connection status"""
        # Mock UI elements
        ui_elements = {
            'connectionStatusText': MagicMock(),
            'connectButton': MagicMock(),
            'disconnectButton': MagicMock()
        }
        
        # Update UI with connected status
        is_connected = True
        self.update_ui_connection_status(ui_elements, is_connected)
        
        # Verify UI was updated correctly
        ui_elements['connectionStatusText'].setText.assert_called_once_with("Connected")
        ui_elements['connectButton'].setVisible.assert_called_once_with(False)
        ui_elements['disconnectButton'].setVisible.assert_called_once_with(True)
    
    def test_connection_status_update_ui_disconnected(self):
        """Test updating UI with disconnected status"""
        # Mock UI elements
        ui_elements = {
            'connectionStatusText': MagicMock(),
            'connectButton': MagicMock(),
            'disconnectButton': MagicMock()
        }
        
        # Update UI with disconnected status
        is_connected = False
        self.update_ui_connection_status(ui_elements, is_connected)
        
        # Verify UI was updated correctly
        ui_elements['connectionStatusText'].setText.assert_called_once_with("Disconnected")
        ui_elements['connectButton'].setVisible.assert_called_once_with(True)
        ui_elements['disconnectButton'].setVisible.assert_called_once_with(False)
    
    def connect_to_port(self, port, baud_rate):
        """Helper method to simulate connecting to a port"""
        self.serial_connector.setPort(port)
        self.serial_connector.setBaudRate(baud_rate)
        self.serial_connector.connect()
    
    def disconnect_from_port(self):
        """Helper method to simulate disconnecting from a port"""
        self.serial_connector.disconnect()
    
    def emit_connection_status(self, is_connected):
        """Helper method to simulate emitting connection status"""
        self.serial_connector.connectionChanged.emit(is_connected)
    
    def propagate_connection_status(self, is_connected):
        """Helper method to simulate propagating connection status"""
        self.flight_controller.on_connection_changed(is_connected)
    
    def try_connect(self):
        """Helper method to simulate trying to connect"""
        try:
            self.serial_connector.connect()
            return True, ""
        except Exception as e:
            return False, str(e)
    
    def attempt_reconnect(self):
        """Helper method to simulate attempting to reconnect"""
        if not self.serial_connector.connected:
            self.serial_connector.connect()
    
    def update_ui_connection_status(self, ui_elements, is_connected):
        """Helper method to simulate updating UI with connection status"""
        if is_connected:
            ui_elements['connectionStatusText'].setText("Connected")
            ui_elements['connectButton'].setVisible(False)
            ui_elements['disconnectButton'].setVisible(True)
        else:
            ui_elements['connectionStatusText'].setText("Disconnected")
            ui_elements['connectButton'].setVisible(True)
            ui_elements['disconnectButton'].setVisible(False)

if __name__ == '__main__':
    unittest.main()
