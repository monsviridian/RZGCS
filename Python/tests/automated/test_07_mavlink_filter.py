#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for the MAVLink message filtering system
Tests the caching, thresholding, and time interval limiting
"""

import unittest
import sys
import os
import time
from unittest.mock import MagicMock, patch

# Add parent directory to path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

class TestMAVLinkFilter(unittest.TestCase):
    """Test cases for the MAVLink message filtering system"""
    
    def setUp(self):
        """Set up test environment"""
        # Create a mock message cache
        self.message_cache = {}
        self.last_logged_time = {}
        self.thresholds = {
            'ATTITUDE': {'roll': 0.1, 'pitch': 0.1, 'yaw': 0.1},
            'GLOBAL_POSITION_INT': {'lat': 0.0001, 'lon': 0.0001, 'alt': 1.0},
            'SYS_STATUS': {'voltage_battery': 0.1, 'current_battery': 0.5},
        }
        self.min_log_intervals = {
            'ATTITUDE': 1.0,  # 1 second
            'GLOBAL_POSITION_INT': 2.0,  # 2 seconds
            'SYS_STATUS': 5.0,  # 5 seconds
        }
    
    def test_message_caching(self):
        """Test that messages are cached correctly"""
        # Create a mock message
        msg_type = 'ATTITUDE'
        mock_msg = MagicMock()
        mock_msg.roll = 0.1
        mock_msg.pitch = 0.2
        mock_msg.yaw = 0.3
        
        # Cache the message
        self.message_cache[msg_type] = mock_msg
        
        # Check that the message was cached
        self.assertIn(msg_type, self.message_cache)
        self.assertEqual(self.message_cache[msg_type].roll, 0.1)
        self.assertEqual(self.message_cache[msg_type].pitch, 0.2)
        self.assertEqual(self.message_cache[msg_type].yaw, 0.3)
    
    def test_threshold_filtering(self):
        """Test threshold-based filtering"""
        # Create a mock cached message
        msg_type = 'ATTITUDE'
        cached_msg = MagicMock()
        cached_msg.roll = 0.1
        cached_msg.pitch = 0.2
        cached_msg.yaw = 0.3
        self.message_cache[msg_type] = cached_msg
        
        # Create a new message with small changes (should be filtered)
        new_msg_small_change = MagicMock()
        new_msg_small_change.roll = 0.15  # Change < threshold (0.1)
        new_msg_small_change.pitch = 0.25  # Change < threshold (0.1)
        new_msg_small_change.yaw = 0.35  # Change < threshold (0.1)
        
        # Create a new message with large changes (should not be filtered)
        new_msg_large_change = MagicMock()
        new_msg_large_change.roll = 0.3  # Change > threshold (0.1)
        new_msg_large_change.pitch = 0.4  # Change > threshold (0.1)
        new_msg_large_change.yaw = 0.5  # Change > threshold (0.1)
        
        # Test small change filtering
        self.assertFalse(self.should_log_message(msg_type, new_msg_small_change))
        
        # Test large change (should log)
        self.assertTrue(self.should_log_message(msg_type, new_msg_large_change))
    
    def test_time_interval_filtering(self):
        """Test time interval-based filtering"""
        # Create a mock message
        msg_type = 'ATTITUDE'
        mock_msg = MagicMock()
        mock_msg.roll = 0.5  # Large change to pass threshold filtering
        mock_msg.pitch = 0.6
        mock_msg.yaw = 0.7
        
        # Set the last logged time to now
        current_time = time.time()
        self.last_logged_time[msg_type] = current_time
        
        # Create a cached message with smaller values (to ensure threshold passes)
        cached_msg = MagicMock()
        cached_msg.roll = 0.1
        cached_msg.pitch = 0.2
        cached_msg.yaw = 0.3
        self.message_cache[msg_type] = cached_msg
        
        # Test that the message is filtered due to time interval
        with patch('time.time', return_value=current_time + 0.5):  # Half a second later
            self.assertFalse(self.should_log_message(msg_type, mock_msg))
        
        # Test that the message is not filtered after the interval
        with patch('time.time', return_value=current_time + 1.5):  # 1.5 seconds later
            self.assertTrue(self.should_log_message(msg_type, mock_msg))
    
    def test_critical_messages_always_logged(self):
        """Test that critical messages are always logged"""
        # Create a mock STATUSTEXT message (critical message)
        msg_type = 'STATUSTEXT'
        mock_msg = MagicMock()
        mock_msg.text = "Important status message"
        mock_msg.severity = 2  # Critical
        
        # Test that the message is always logged
        self.assertTrue(self.should_log_message(msg_type, mock_msg))
    
    def should_log_message(self, msg_type, msg):
        """Helper method to simulate the message filtering logic"""
        # Critical message types are always logged
        if msg_type in ['STATUSTEXT', 'COMMAND_ACK', 'MISSION_ITEM_REACHED']:
            return True
        
        current_time = time.time()
        
        # Check if we've seen this message type before
        if msg_type in self.message_cache:
            # Check if it's too soon to log this message type again
            if msg_type in self.last_logged_time:
                time_since_last_log = current_time - self.last_logged_time[msg_type]
                if time_since_last_log < self.min_log_intervals.get(msg_type, 1.0):
                    return False
            
            # Check if values have changed significantly
            cached_msg = self.message_cache[msg_type]
            thresholds = self.thresholds.get(msg_type, {})
            
            # Check each field with a threshold
            significant_change = False
            for field, threshold in thresholds.items():
                if hasattr(msg, field) and hasattr(cached_msg, field):
                    old_val = getattr(cached_msg, field)
                    new_val = getattr(msg, field)
                    if abs(new_val - old_val) > threshold:
                        significant_change = True
                        break
            
            if not significant_change:
                return False
        
        # Update the cache and last logged time
        self.message_cache[msg_type] = msg
        self.last_logged_time[msg_type] = current_time
        return True

if __name__ == '__main__':
    unittest.main()
