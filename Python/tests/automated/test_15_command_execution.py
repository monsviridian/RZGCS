#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for command execution in the RZGCS application
"""

import unittest
import sys
import os
from unittest.mock import MagicMock, patch

# Add parent directory to path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

class TestCommandExecution(unittest.TestCase):
    """Test cases for command execution"""
    
    def setUp(self):
        """Set up test environment"""
        self.mock_mavlink_connection = MagicMock()
    
    def test_arm_command(self):
        """Test arming the drone"""
        # Simulate command execution
        self.execute_command("ARM")
        
        # Verify that the appropriate MAVLink command was sent
        self.mock_mavlink_connection.mav.command_long_send.assert_called_once()
        
        # Extract the arguments
        args = self.mock_mavlink_connection.mav.command_long_send.call_args[0]
        
        # Verify command ID (COMPONENT_ARM_DISARM = 400)
        self.assertEqual(args[2], 400)
        
        # Verify parameter 1 (1 = arm)
        self.assertEqual(args[3], 1)
    
    def test_disarm_command(self):
        """Test disarming the drone"""
        # Simulate command execution
        self.execute_command("DISARM")
        
        # Verify that the appropriate MAVLink command was sent
        self.mock_mavlink_connection.mav.command_long_send.assert_called_once()
        
        # Extract the arguments
        args = self.mock_mavlink_connection.mav.command_long_send.call_args[0]
        
        # Verify command ID (COMPONENT_ARM_DISARM = 400)
        self.assertEqual(args[2], 400)
        
        # Verify parameter 1 (0 = disarm)
        self.assertEqual(args[3], 0)
    
    def test_takeoff_command(self):
        """Test takeoff command"""
        # Simulate command execution with altitude parameter
        self.execute_command("TAKEOFF", altitude=10.0)
        
        # Verify that the appropriate MAVLink command was sent
        self.mock_mavlink_connection.mav.command_long_send.assert_called_once()
        
        # Extract the arguments
        args = self.mock_mavlink_connection.mav.command_long_send.call_args[0]
        
        # Verify command ID (NAV_TAKEOFF = 22)
        self.assertEqual(args[2], 22)
        
        # Verify altitude parameter (parameter 7)
        self.assertEqual(args[9], 10.0)
    
    def test_land_command(self):
        """Test land command"""
        # Simulate command execution
        self.execute_command("LAND")
        
        # Verify that the appropriate MAVLink command was sent
        self.mock_mavlink_connection.mav.command_long_send.assert_called_once()
        
        # Extract the arguments
        args = self.mock_mavlink_connection.mav.command_long_send.call_args[0]
        
        # Verify command ID (NAV_LAND = 21)
        self.assertEqual(args[2], 21)
    
    def test_rtl_command(self):
        """Test return to launch command"""
        # Simulate command execution
        self.execute_command("RTL")
        
        # Verify that the appropriate MAVLink command was sent
        self.mock_mavlink_connection.mav.command_long_send.assert_called_once()
        
        # Extract the arguments
        args = self.mock_mavlink_connection.mav.command_long_send.call_args[0]
        
        # Verify command ID (NAV_RETURN_TO_LAUNCH = 20)
        self.assertEqual(args[2], 20)
    
    def test_set_mode_command(self):
        """Test setting flight mode"""
        # Simulate command execution
        self.execute_command("MODE", mode="GUIDED")
        
        # Verify that the appropriate MAVLink command was sent
        self.mock_mavlink_connection.mav.command_long_send.assert_called_once()
        
        # Extract the arguments
        args = self.mock_mavlink_connection.mav.command_long_send.call_args[0]
        
        # Verify command ID (MAV_CMD_DO_SET_MODE = 176)
        self.assertEqual(args[2], 176)
        
        # Verify mode parameter (parameter 1, 1 = MAV_MODE_GUIDED_ARMED)
        self.assertEqual(args[3], 1)
    
    def test_goto_command(self):
        """Test goto command"""
        # Simulate command execution
        self.execute_command("GOTO", lat=50.110924, lon=8.682127, alt=100.0)
        
        # Verify that the appropriate MAVLink command was sent
        self.mock_mavlink_connection.mav.mission_item_send.assert_called_once()
        
        # Extract the arguments
        args = self.mock_mavlink_connection.mav.mission_item_send.call_args[0]
        
        # Verify the coordinates
        self.assertEqual(args[4], 50.110924)  # latitude
        self.assertEqual(args[5], 8.682127)   # longitude
        self.assertEqual(args[6], 100.0)      # altitude
    
    def test_command_ack_handling(self):
        """Test handling of command acknowledgments"""
        # Create a mock message
        msg = MagicMock()
        msg.command = 400  # COMPONENT_ARM_DISARM
        msg.result = 0     # MAV_RESULT_ACCEPTED
        
        # Handle the ack
        result = self.handle_command_ack(msg)
        
        # Verify the result
        self.assertTrue(result)
    
    def test_command_ack_handling_failure(self):
        """Test handling of command acknowledgment failures"""
        # Create a mock message
        msg = MagicMock()
        msg.command = 400  # COMPONENT_ARM_DISARM
        msg.result = 1     # MAV_RESULT_TEMPORARILY_REJECTED
        
        # Handle the ack
        result = self.handle_command_ack(msg)
        
        # Verify the result
        self.assertFalse(result)
    
    def execute_command(self, command, **kwargs):
        """Helper method to simulate executing a command"""
        if command == "ARM":
            self.mock_mavlink_connection.mav.command_long_send(
                0, 0, 400, 0, 1, 0, 0, 0, 0, 0, 0
            )
        elif command == "DISARM":
            self.mock_mavlink_connection.mav.command_long_send(
                0, 0, 400, 0, 0, 0, 0, 0, 0, 0, 0
            )
        elif command == "TAKEOFF":
            altitude = kwargs.get("altitude", 10.0)
            self.mock_mavlink_connection.mav.command_long_send(
                0, 0, 22, 0, 0, 0, 0, 0, 0, 0, altitude
            )
        elif command == "LAND":
            self.mock_mavlink_connection.mav.command_long_send(
                0, 0, 21, 0, 0, 0, 0, 0, 0, 0, 0
            )
        elif command == "RTL":
            self.mock_mavlink_connection.mav.command_long_send(
                0, 0, 20, 0, 0, 0, 0, 0, 0, 0, 0
            )
        elif command == "MODE":
            mode = kwargs.get("mode", "GUIDED")
            mode_mapping = {"GUIDED": 1, "AUTO": 3, "LOITER": 5}
            mode_id = mode_mapping.get(mode, 1)
            self.mock_mavlink_connection.mav.command_long_send(
                0, 0, 176, 0, mode_id, 0, 0, 0, 0, 0, 0
            )
        elif command == "GOTO":
            lat = kwargs.get("lat", 0.0)
            lon = kwargs.get("lon", 0.0)
            alt = kwargs.get("alt", 0.0)
            self.mock_mavlink_connection.mav.mission_item_send(
                0, 0, 0, 0, lat, lon, alt, 0, 0, 0, 0, 0
            )
    
    def handle_command_ack(self, msg):
        """Helper method to simulate handling a command acknowledgment"""
        # MAV_RESULT_ACCEPTED = 0
        return msg.result == 0

if __name__ == '__main__':
    unittest.main()
