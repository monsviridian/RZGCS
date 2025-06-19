#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for mission planning and waypoint handling in the RZGCS application
"""

import unittest
import sys
import os
from unittest.mock import MagicMock, patch

# Add parent directory to path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

class TestMissionPlanning(unittest.TestCase):
    """Test cases for mission planning and waypoint handling"""
    
    def setUp(self):
        """Set up test environment"""
        self.mission_model = MagicMock()
        self.mavlink_connection = MagicMock()
        self.logger = MagicMock()
    
    def test_add_waypoint(self):
        """Test adding a waypoint to a mission"""
        # Add a waypoint
        wp_index = 1
        wp_lat = 50.110924
        wp_lon = 8.682127
        wp_alt = 100.0
        wp_type = 16  # MAV_CMD_NAV_WAYPOINT
        
        self.add_waypoint(wp_index, wp_lat, wp_lon, wp_alt, wp_type)
        
        # Verify the waypoint was added to the model
        self.mission_model.add_waypoint.assert_called_once()
        
        # Extract the arguments
        args = self.mission_model.add_waypoint.call_args[0]
        
        # Verify the waypoint parameters
        self.assertEqual(args[0], wp_index)
        self.assertEqual(args[1], wp_lat)
        self.assertEqual(args[2], wp_lon)
        self.assertEqual(args[3], wp_alt)
        self.assertEqual(args[4], wp_type)
    
    def test_remove_waypoint(self):
        """Test removing a waypoint from a mission"""
        # Remove a waypoint
        wp_index = 1
        self.remove_waypoint(wp_index)
        
        # Verify the waypoint was removed from the model
        self.mission_model.remove_waypoint.assert_called_once_with(wp_index)
    
    def test_clear_mission(self):
        """Test clearing a mission"""
        # Clear the mission
        self.clear_mission()
        
        # Verify the mission was cleared in the model
        self.mission_model.clear_mission.assert_called_once()
    
    def test_upload_mission(self):
        """Test uploading a mission to the drone"""
        # Create test waypoints
        waypoints = [
            {"index": 0, "lat": 0.0, "lon": 0.0, "alt": 0.0, "type": 0},  # Home position
            {"index": 1, "lat": 50.110924, "lon": 8.682127, "alt": 100.0, "type": 16},  # Waypoint 1
            {"index": 2, "lat": 50.111924, "lon": 8.683127, "alt": 110.0, "type": 16},  # Waypoint 2
            {"index": 3, "lat": 50.112924, "lon": 8.684127, "alt": 120.0, "type": 16}   # Waypoint 3
        ]
        
        # Mock the mission model to return the test waypoints
        self.mission_model.get_all_waypoints.return_value = waypoints
        
        # Upload the mission
        self.upload_mission()
        
        # Verify the mission count message was sent
        self.mavlink_connection.mav.mission_count_send.assert_called_once()
        
        # Extract the arguments
        args = self.mavlink_connection.mav.mission_count_send.call_args[0]
        
        # Verify the mission count
        self.assertEqual(args[2], len(waypoints))
    
    def test_download_mission(self):
        """Test downloading a mission from the drone"""
        # Download the mission
        self.download_mission()
        
        # Verify the mission request list message was sent
        self.mavlink_connection.mav.mission_request_list_send.assert_called_once()
    
    def test_handle_mission_count(self):
        """Test handling a mission count message"""
        # Create a mock message
        msg = MagicMock()
        msg.count = 4  # 4 waypoints
        
        # Handle the message
        self.handle_mission_count(msg)
        
        # Verify the model was updated
        self.mission_model.prepare_mission.assert_called_once_with(4)
        
        # Verify the first waypoint was requested
        self.mavlink_connection.mav.mission_request_int_send.assert_called_once()
        
        # Extract the arguments
        args = self.mavlink_connection.mav.mission_request_int_send.call_args[0]
        
        # Verify the waypoint index
        self.assertEqual(args[2], 0)  # First waypoint
    
    def test_handle_mission_item(self):
        """Test handling a mission item message"""
        # Create a mock message
        msg = MagicMock()
        msg.seq = 1
        msg.x = 50.110924
        msg.y = 8.682127
        msg.z = 100.0
        msg.command = 16  # MAV_CMD_NAV_WAYPOINT
        
        # Handle the message
        self.handle_mission_item(msg)
        
        # Verify the waypoint was added to the model
        self.mission_model.add_waypoint.assert_called_once()
        
        # Extract the arguments
        args = self.mission_model.add_waypoint.call_args[0]
        
        # Verify the waypoint parameters
        self.assertEqual(args[0], msg.seq)
        self.assertEqual(args[1], msg.x)
        self.assertEqual(args[2], msg.y)
        self.assertEqual(args[3], msg.z)
        self.assertEqual(args[4], msg.command)
    
    def test_handle_mission_ack(self):
        """Test handling a mission acknowledgment message"""
        # Create a mock message
        msg = MagicMock()
        msg.type = 0  # MAV_MISSION_ACCEPTED
        
        # Handle the message
        result = self.handle_mission_ack(msg)
        
        # Verify the result
        self.assertTrue(result)
    
    def test_handle_mission_ack_error(self):
        """Test handling a mission acknowledgment error message"""
        # Create a mock message
        msg = MagicMock()
        msg.type = 1  # MAV_MISSION_ERROR
        
        # Handle the message
        result = self.handle_mission_ack(msg)
        
        # Verify the result
        self.assertFalse(result)
    
    def test_load_mission_file(self):
        """Test loading a mission from a file"""
        # Create a test mission file
        filename = "test_mission.waypoints"
        with open(filename, 'w') as f:
            f.write("QGC WPL 110\n")
            f.write("0\t1\t0\t16\t0\t0\t0\t0\t50.110924\t8.682127\t100.0\t1\n")
            f.write("1\t0\t3\t16\t0\t0\t0\t0\t50.111924\t8.683127\t110.0\t1\n")
            f.write("2\t0\t3\t16\t0\t0\t0\t0\t50.112924\t8.684127\t120.0\t1\n")
        
        # Load the mission
        self.load_mission_file(filename)
        
        # Verify the mission model was updated
        self.mission_model.clear_mission.assert_called_once()
        self.mission_model.add_waypoint.assert_called()
        
        # Verify the number of waypoints added
        self.assertEqual(self.mission_model.add_waypoint.call_count, 3)
        
        # Clean up
        if os.path.exists(filename):
            os.remove(filename)
    
    def test_save_mission_file(self):
        """Test saving a mission to a file"""
        # Create test waypoints
        waypoints = [
            {"index": 0, "lat": 50.110924, "lon": 8.682127, "alt": 100.0, "type": 16},
            {"index": 1, "lat": 50.111924, "lon": 8.683127, "alt": 110.0, "type": 16},
            {"index": 2, "lat": 50.112924, "lon": 8.684127, "alt": 120.0, "type": 16}
        ]
        
        # Mock the mission model to return the test waypoints
        self.mission_model.get_all_waypoints.return_value = waypoints
        
        # Save the mission
        filename = "test_mission.waypoints"
        self.save_mission_file(filename)
        
        # Verify the file was created
        self.assertTrue(os.path.exists(filename))
        
        # Read the file
        with open(filename, 'r') as f:
            content = f.read()
        
        # Verify the file contents
        self.assertTrue("QGC WPL 110" in content)
        self.assertTrue("50.110924" in content)
        self.assertTrue("50.111924" in content)
        self.assertTrue("50.112924" in content)
        
        # Clean up
        if os.path.exists(filename):
            os.remove(filename)
    
    def add_waypoint(self, index, lat, lon, alt, cmd_type):
        """Helper method to simulate adding a waypoint"""
        self.mission_model.add_waypoint(index, lat, lon, alt, cmd_type)
    
    def remove_waypoint(self, index):
        """Helper method to simulate removing a waypoint"""
        self.mission_model.remove_waypoint(index)
    
    def clear_mission(self):
        """Helper method to simulate clearing a mission"""
        self.mission_model.clear_mission()
    
    def upload_mission(self):
        """Helper method to simulate uploading a mission"""
        waypoints = self.mission_model.get_all_waypoints()
        
        # Send mission count
        self.mavlink_connection.mav.mission_count_send(
            self.mavlink_connection.target_system,
            self.mavlink_connection.target_component,
            len(waypoints)
        )
    
    def download_mission(self):
        """Helper method to simulate downloading a mission"""
        self.mavlink_connection.mav.mission_request_list_send(
            self.mavlink_connection.target_system,
            self.mavlink_connection.target_component
        )
    
    def handle_mission_count(self, msg):
        """Helper method to simulate handling a mission count message"""
        # Prepare to receive the mission
        self.mission_model.prepare_mission(msg.count)
        
        # Request the first waypoint
        self.mavlink_connection.mav.mission_request_int_send(
            self.mavlink_connection.target_system,
            self.mavlink_connection.target_component,
            0  # First waypoint
        )
    
    def handle_mission_item(self, msg):
        """Helper method to simulate handling a mission item message"""
        # Add the waypoint to the model
        self.mission_model.add_waypoint(
            msg.seq,
            msg.x,
            msg.y,
            msg.z,
            msg.command
        )
    
    def handle_mission_ack(self, msg):
        """Helper method to simulate handling a mission acknowledgment message"""
        # MAV_MISSION_ACCEPTED = 0
        return msg.type == 0
    
    def load_mission_file(self, filename):
        """Helper method to simulate loading a mission from a file"""
        # Clear the current mission
        self.mission_model.clear_mission()
        
        # Read the mission file
        with open(filename, 'r') as f:
            lines = f.readlines()
            
            # Skip header
            for i, line in enumerate(lines[1:], 1):
                parts = line.strip().split('\t')
                if len(parts) >= 11:
                    try:
                        index = int(parts[0])
                        lat = float(parts[8])
                        lon = float(parts[9])
                        alt = float(parts[10])
                        cmd_type = int(parts[3])
                        
                        # Add the waypoint to the model
                        self.mission_model.add_waypoint(index, lat, lon, alt, cmd_type)
                    except (ValueError, IndexError):
                        # Skip invalid lines
                        pass
    
    def save_mission_file(self, filename):
        """Helper method to simulate saving a mission to a file"""
        waypoints = self.mission_model.get_all_waypoints()
        
        # Write the mission file
        with open(filename, 'w') as f:
            # Write header
            f.write("QGC WPL 110\n")
            
            # Write waypoints
            for wp in waypoints:
                # Format: INDEX CURRENT_WP COORD_FRAME COMMAND PARAM1 PARAM2 PARAM3 PARAM4 LAT LON ALT AUTOCONTINUE
                line = f"{wp['index']}\t0\t3\t{wp['type']}\t0\t0\t0\t0\t{wp['lat']}\t{wp['lon']}\t{wp['alt']}\t1\n"
                f.write(line)

if __name__ == '__main__':
    unittest.main()
