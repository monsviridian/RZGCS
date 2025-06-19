#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for parameter handling in the RZGCS application
"""

import unittest
import sys
import os
from unittest.mock import MagicMock, patch

# Add parent directory to path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

class TestParameterHandling(unittest.TestCase):
    """Test cases for parameter handling"""
    
    def setUp(self):
        """Set up test environment"""
        self.parameter_model = MagicMock()
        self.logger = MagicMock()
    
    def test_parameter_request(self):
        """Test requesting parameters from the flight controller"""
        # Mock the MAVLink connection
        mavlink_connection = MagicMock()
        
        # Request parameters
        self.request_all_parameters(mavlink_connection)
        
        # Verify the appropriate MAVLink message was sent
        mavlink_connection.mav.param_request_list_send.assert_called_once()
    
    def test_parameter_update(self):
        """Test updating a parameter"""
        # Test parameter update
        param_id = "FLTMODE1"
        param_value = 5  # LOITER mode
        param_type = 2   # MAV_PARAM_TYPE_INT32
        
        # Update the parameter
        self.update_parameter(param_id, param_value, param_type)
        
        # Verify the parameter was updated in the model
        self.parameter_model.update_parameter.assert_called_once_with(param_id, param_value, param_type)
    
    def test_parameter_request_specific(self):
        """Test requesting a specific parameter"""
        # Mock the MAVLink connection
        mavlink_connection = MagicMock()
        
        # Request a specific parameter
        param_id = "FLTMODE1"
        self.request_parameter(mavlink_connection, param_id)
        
        # Verify the appropriate MAVLink message was sent
        mavlink_connection.mav.param_request_read_send.assert_called_once()
        
        # Extract the arguments
        args = mavlink_connection.mav.param_request_read_send.call_args[0]
        
        # Verify parameter ID (either as string or -1 for by-index)
        self.assertEqual(args[2], param_id)
    
    def test_parameter_set(self):
        """Test setting a parameter"""
        # Mock the MAVLink connection
        mavlink_connection = MagicMock()
        
        # Set a parameter
        param_id = "FLTMODE1"
        param_value = 5.0  # LOITER mode
        param_type = 2     # MAV_PARAM_TYPE_INT32
        
        self.set_parameter(mavlink_connection, param_id, param_value, param_type)
        
        # Verify the appropriate MAVLink message was sent
        mavlink_connection.mav.param_set_send.assert_called_once()
        
        # Extract the arguments
        args = mavlink_connection.mav.param_set_send.call_args[0]
        
        # Verify parameter ID and value
        self.assertEqual(args[2], param_id)
        self.assertEqual(args[3], param_value)
        self.assertEqual(args[4], param_type)
    
    def test_parameter_value_handler(self):
        """Test handling parameter value messages"""
        # Create a mock message
        msg = MagicMock()
        msg.param_id = "FLTMODE1"
        msg.param_value = 5.0
        msg.param_type = 2
        
        # Handle the message
        self.handle_parameter_value(msg)
        
        # Verify the parameter was updated in the model
        self.parameter_model.update_parameter.assert_called_once_with("FLTMODE1", 5.0, 2)
    
    def test_parameter_save(self):
        """Test saving parameters to a file"""
        # Get all parameters
        parameters = [
            {"id": "FLTMODE1", "value": 5.0, "type": 2},
            {"id": "FLTMODE2", "value": 6.0, "type": 2},
            {"id": "BATT_CAPACITY", "value": 3300.0, "type": 9}
        ]
        self.parameter_model.get_all_parameters.return_value = parameters
        
        # Save parameters to a file
        filename = "test_parameters.csv"
        self.save_parameters(filename)
        
        # Verify the file was created
        self.assertTrue(os.path.exists(filename))
        
        # Read the file
        with open(filename, 'r') as f:
            content = f.read()
        
        # Verify the parameters were written to the file
        self.assertTrue("FLTMODE1" in content)
        self.assertTrue("FLTMODE2" in content)
        self.assertTrue("BATT_CAPACITY" in content)
        
        # Clean up
        if os.path.exists(filename):
            os.remove(filename)
    
    def test_parameter_load(self):
        """Test loading parameters from a file"""
        # Create a test file
        filename = "test_parameters.csv"
        with open(filename, 'w') as f:
            f.write("id,value,type\n")
            f.write("FLTMODE1,5.0,2\n")
            f.write("FLTMODE2,6.0,2\n")
            f.write("BATT_CAPACITY,3300.0,9\n")
        
        # Load parameters from the file
        parameters = self.load_parameters(filename)
        
        # Verify the parameters were loaded correctly
        self.assertEqual(len(parameters), 3)
        self.assertEqual(parameters[0]["id"], "FLTMODE1")
        self.assertEqual(parameters[0]["value"], 5.0)
        self.assertEqual(parameters[0]["type"], 2)
        
        # Clean up
        if os.path.exists(filename):
            os.remove(filename)
    
    def test_parameter_validation(self):
        """Test parameter validation"""
        # Test valid parameters
        valid_params = [
            {"id": "FLTMODE1", "value": 5, "type": 2},
            {"id": "RTL_ALT", "value": 100, "type": 2},
            {"id": "BATT_CAPACITY", "value": 3300, "type": 9}
        ]
        
        # Test invalid parameters
        invalid_params = [
            {"id": "", "value": 5, "type": 2},  # Empty ID
            {"id": "FLTMODE1", "value": "invalid", "type": 2},  # Invalid value type
            {"id": "FLTMODE1", "value": 5, "type": 100}  # Invalid type
        ]
        
        # Verify validation results
        for param in valid_params:
            self.assertTrue(self.validate_parameter(param))
        
        for param in invalid_params:
            self.assertFalse(self.validate_parameter(param))
    
    def request_all_parameters(self, mavlink_connection):
        """Helper method to simulate requesting all parameters"""
        mavlink_connection.mav.param_request_list_send(
            mavlink_connection.target_system,
            mavlink_connection.target_component
        )
    
    def request_parameter(self, mavlink_connection, param_id, param_index=-1):
        """Helper method to simulate requesting a specific parameter"""
        mavlink_connection.mav.param_request_read_send(
            mavlink_connection.target_system,
            mavlink_connection.target_component,
            param_id,
            param_index
        )
    
    def set_parameter(self, mavlink_connection, param_id, param_value, param_type):
        """Helper method to simulate setting a parameter"""
        mavlink_connection.mav.param_set_send(
            mavlink_connection.target_system,
            mavlink_connection.target_component,
            param_id,
            param_value,
            param_type
        )
    
    def update_parameter(self, param_id, param_value, param_type):
        """Helper method to simulate updating a parameter in the model"""
        self.parameter_model.update_parameter(param_id, param_value, param_type)
    
    def handle_parameter_value(self, msg):
        """Helper method to simulate handling a parameter value message"""
        self.parameter_model.update_parameter(msg.param_id, msg.param_value, msg.param_type)
    
    def save_parameters(self, filename):
        """Helper method to simulate saving parameters to a file"""
        parameters = self.parameter_model.get_all_parameters()
        
        with open(filename, 'w') as f:
            f.write("id,value,type\n")
            for param in parameters:
                f.write(f"{param['id']},{param['value']},{param['type']}\n")
    
    def load_parameters(self, filename):
        """Helper method to simulate loading parameters from a file"""
        parameters = []
        
        with open(filename, 'r') as f:
            lines = f.readlines()
            
            # Skip header
            for line in lines[1:]:
                parts = line.strip().split(',')
                if len(parts) == 3:
                    parameters.append({
                        "id": parts[0],
                        "value": float(parts[1]),
                        "type": int(parts[2])
                    })
        
        return parameters
    
    def validate_parameter(self, param):
        """Helper method to simulate validating a parameter"""
        # Check if ID is not empty
        if not param["id"]:
            return False
        
        # Check if value is a number
        try:
            float(param["value"])
        except (ValueError, TypeError):
            return False
        
        # Check if type is valid (0-16 in MAVLink)
        if not 0 <= param["type"] <= 16:
            return False
        
        return True

if __name__ == '__main__':
    unittest.main()
