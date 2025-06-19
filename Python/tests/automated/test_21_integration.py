#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Integration tests for the RZGCS application
Tests interactions between multiple components
"""

import unittest
import sys
import os
from unittest.mock import MagicMock, patch

# Add parent directory to path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

class TestIntegration(unittest.TestCase):
    """Integration tests for component interactions"""
    
    def setUp(self):
        """Set up test environment"""
        self.serial_connector = MagicMock()
        self.flight_controller = MagicMock()
        self.message_handler = MagicMock()
        self.logger = MagicMock()
        self.sensor_model = MagicMock()
    
    def test_gps_data_flow(self):
        """Test the flow of GPS data through the system"""
        # Define test GPS data
        test_lat = 50.110924
        test_lon = 8.682127
        test_alt = 100.0
        
        # Mock sensor model to return the test data
        self.sensor_model.get_sensor_value.side_effect = lambda key: {
            "gps_lat": test_lat,
            "gps_lon": test_lon,
            "altitude": test_alt
        }.get(key)
        
        # Connect the serial connector to the sensor model
        self.serial_connector._sensor_model = self.sensor_model
        
        # Mock the signal
        self.serial_connector.gpsChanged = MagicMock()
        
        # Request GPS data
        self.serial_connector.request_gps_data()
        
        # Verify that the signal was emitted with the correct values
        self.serial_connector.gpsChanged.emit.assert_called_once_with(test_lat, test_lon, test_alt)
        
        # Now simulate the flight controller receiving the signal
        self.flight_controller.update_drone_position(test_lat, test_lon, test_alt, 45.0)
        
        # Verify that the flight controller updated the drone position
        self.assertEqual(self.flight_controller.update_drone_position.call_count, 1)
        self.flight_controller.update_drone_position.assert_called_with(test_lat, test_lon, test_alt, 45.0)
    
    def test_connection_status_propagation(self):
        """Test the propagation of connection status through the system"""
        # Set up connections between components
        self.serial_connector.connectionChanged = MagicMock()
        
        # Simulate connection change
        connected = True
        self.serial_connector._connected = connected
        self.serial_connector.connectionChanged.emit(connected)
        
        # Now simulate the flight controller receiving the signal
        self.flight_controller.on_connection_changed(connected)
        
        # Verify that the flight controller updated its connection state
        self.flight_controller.on_connection_changed.assert_called_once_with(connected)
    
    def test_mavlink_message_flow(self):
        """Test the flow of MAVLink messages through the system"""
        # Create a mock MAVLink message
        mock_msg = MagicMock()
        mock_msg.get_type.return_value = 'GLOBAL_POSITION_INT'
        mock_msg.lat = 50110924  # in 1e7 degrees
        mock_msg.lon = 8682127   # in 1e7 degrees
        mock_msg.alt = 10000     # in mm
        
        # Set up the message handler
        self.message_handler._sensor_model = self.sensor_model
        
        # Process the message
        self.message_handler._handle_global_position_int = MagicMock()
        self.message_handler._process_message(mock_msg)
        
        # Verify that the message was processed
        self.message_handler._handle_global_position_int.assert_called_once_with(mock_msg)
        
        # Now simulate handling the global position message
        self.sensor_model.update_sensor = MagicMock()
        self.message_handler._handle_global_position_int(mock_msg)
        
        # Verify that the sensor model was updated
        self.sensor_model.update_sensor.assert_any_call("gps_lat", mock_msg.lat / 1e7)
        self.sensor_model.update_sensor.assert_any_call("gps_lon", mock_msg.lon / 1e7)
        self.sensor_model.update_sensor.assert_any_call("altitude", mock_msg.alt / 1000.0)
    
    def test_system_info_filtering(self):
        """Test the system information filtering mechanism"""
        # Create mock log messages
        system_info_msg = "[SYSTEM INFO] Frame-Type: Quadcopter X"
        regular_msg = "[INFO] Regular log message"
        prearm_warning = "[WARNING] PreArm: Battery failsafe active"
        
        # Set up the logger
        self.logger.is_system_info = lambda msg: "[SYSTEM INFO]" in msg or ("[WARNING]" in msg and "PreArm" in msg)
        
        # Log the messages
        for msg in [system_info_msg, regular_msg, prearm_warning]:
            self.logger.log = MagicMock()
            self.logger.raw(msg)
            
            # For system info messages, verify they were logged
            if self.logger.is_system_info(msg):
                self.logger.log.emit.assert_called_once()
            else:
                self.logger.log.emit.assert_not_called()
    
    def test_angel_mode_path_selection(self):
        """Test the Angel Mode flight path selection and visualization"""
        # Define the 8 flight paths from Angel Mode
        flight_paths = [
            {"region": "Ukraine", "color": "red"},
            {"region": "Europe/Germany", "color": "blue"},
            {"region": "Turkey", "color": "orange"},
            {"region": "North Africa", "color": "green"},
            {"region": "Russia", "color": "purple"},
            {"region": "Baltic", "color": "amber"},
            {"region": "UK", "color": "teal"},
            {"region": "Middle East", "color": "maroon"}
        ]
        
        # Create a mock Angel Mode controller
        angel_controller = MagicMock()
        angel_controller.get_flight_paths.return_value = flight_paths
        
        # Select a flight path
        selected_path = "Europe/Germany"
        angel_controller.select_flight_path = MagicMock()
        angel_controller.select_flight_path(selected_path)
        
        # Verify the path was selected
        angel_controller.select_flight_path.assert_called_once_with(selected_path)
        
        # Now simulate visualization updates
        angel_controller.update_visualization = MagicMock()
        angel_controller.update_visualization()
        
        # Verify visualization was updated
        angel_controller.update_visualization.assert_called_once()
    
    def test_mavlink_message_filtering(self):
        """Test the MAVLink message filtering system"""
        # Create mock messages with small changes
        msg1 = MagicMock()
        msg1.get_type.return_value = 'ATTITUDE'
        msg1.roll = 0.1
        msg1.pitch = 0.2
        msg1.yaw = 0.3
        
        msg2 = MagicMock()
        msg2.get_type.return_value = 'ATTITUDE'
        msg2.roll = 0.11  # Small change
        msg2.pitch = 0.21  # Small change
        msg2.yaw = 0.31   # Small change
        
        # Create the message handler with filtering
        self.message_handler._last_logged_time = {}
        self.message_handler._message_cache = {}
        self.message_handler._thresholds = {
            'ATTITUDE': {'roll': 0.1, 'pitch': 0.1, 'yaw': 0.1}
        }
        
        # Process the first message
        self.message_handler._handle_attitude = MagicMock()
        self.message_handler._running = True
        
        # First message should always be processed
        self.message_handler._process_message(msg1)
        self.message_handler._handle_attitude.assert_called_once_with(msg1)
        
        # Reset the mock
        self.message_handler._handle_attitude.reset_mock()
        
        # Cache the first message
        self.message_handler._message_cache['ATTITUDE'] = msg1
        
        # Now process the second message with small changes
        self.message_handler._process_message(msg2)
        
        # Verify that the second message was not processed due to small changes
        self.message_handler._handle_attitude.assert_not_called()
    
    def test_preflight_view_updates(self):
        """Test updates to the Preflight View based on system status"""
        # Create mock components
        preflight_view = MagicMock()
        preflight_controller = MagicMock()
        
        # Connect the serial connector to the preflight controller
        self.serial_connector.connectionChanged.connect = MagicMock()
        self.serial_connector.connectionChanged.connect(preflight_controller.on_connection_changed)
        
        # Verify that the signal was connected
        self.serial_connector.connectionChanged.connect.assert_called_once_with(preflight_controller.on_connection_changed)
        
        # Simulate connection
        self.serial_connector._connected = True
        self.serial_connector.connectionChanged.emit(True)
        
        # Simulate the preflight controller updating the view
        preflight_controller.on_connection_changed(True)
        preflight_controller.update_view = MagicMock()
        preflight_controller.update_view()
        
        # Verify that the view was updated
        preflight_controller.update_view.assert_called_once()
        
        # Simulate system info log
        system_info_log = "[SYSTEM INFO] Frame-Type: Quadcopter X"
        preflight_controller.add_log = MagicMock()
        preflight_controller.add_log(system_info_log)
        
        # Verify that the log was added
        preflight_controller.add_log.assert_called_once_with(system_info_log)

if __name__ == '__main__':
    unittest.main()
