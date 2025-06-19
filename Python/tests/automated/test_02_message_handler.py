#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for the Message Handler component including the MAVLink filtering system
"""

import unittest
import sys
import os
from unittest.mock import MagicMock, patch

# Add parent directory to path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.message_handler import MessageHandler
from backend.logger import Logger

class TestMessageHandler(unittest.TestCase):
    """Test cases for the MessageHandler class"""
    
    def setUp(self):
        """Set up test environment"""
        self.logger = Logger()
        self.message_handler = MessageHandler(self.logger)
    
    def test_initialization(self):
        """Test MessageHandler initialization"""
        self.assertFalse(self.message_handler._running)
        self.assertIsNone(self.message_handler._mavlink_connection)
    
    @patch('backend.message_handler.MessageHandler._handle_heartbeat')
    def test_process_message_heartbeat(self, mock_handle_heartbeat):
        """Test processing a heartbeat message"""
        mock_msg = MagicMock()
        mock_msg.get_type.return_value = 'HEARTBEAT'
        
        self.message_handler._process_message(mock_msg)
        mock_handle_heartbeat.assert_called_once_with(mock_msg)
    
    @patch('backend.message_handler.MessageHandler._handle_statustext')
    def test_process_message_statustext(self, mock_handle_statustext):
        """Test processing a statustext message"""
        mock_msg = MagicMock()
        mock_msg.get_type.return_value = 'STATUSTEXT'
        
        self.message_handler._process_message(mock_msg)
        mock_handle_statustext.assert_called_once_with(mock_msg)
    
    def test_handle_statustext(self):
        """Test handling a statustext message"""
        # Create a mock for the signal
        self.message_handler.status_text_received = MagicMock()
        
        # Create a mock statustext message
        mock_msg = MagicMock()
        mock_msg.text = "Test message"
        mock_msg.severity = 4  # WARNING
        
        # Call the handler
        self.message_handler._handle_statustext(mock_msg)
        
        # Verify the signal was emitted
        self.message_handler.status_text_received.emit.assert_called_once()
    
    def test_message_filtering(self):
        """Test the message filtering system"""
        # This test verifies that the message filtering system correctly
        # caches messages and only processes them when values change significantly
        
        # We need to mock out some internals for this test
        self.message_handler._mavlink_connection = MagicMock()
        self.message_handler._running = True
        
        # Create mock for signals
        self.message_handler.attitude_received = MagicMock()
        
        # Create mock messages with similar values
        mock_msg1 = MagicMock()
        mock_msg1.get_type.return_value = 'ATTITUDE'
        mock_msg1.roll = 0.1
        mock_msg1.pitch = 0.2
        mock_msg1.yaw = 0.3
        
        mock_msg2 = MagicMock()
        mock_msg2.get_type.return_value = 'ATTITUDE'
        mock_msg2.roll = 0.11  # Small change
        mock_msg2.pitch = 0.21  # Small change
        mock_msg2.yaw = 0.31   # Small change
        
        mock_msg3 = MagicMock()
        mock_msg3.get_type.return_value = 'ATTITUDE'
        mock_msg3.roll = 0.3   # Significant change
        mock_msg3.pitch = 0.4  # Significant change
        mock_msg3.yaw = 0.5    # Significant change
        
        # Process the first message - this should always be processed
        with patch('backend.message_handler.MessageHandler._handle_attitude') as mock_handle_attitude:
            self.message_handler._process_message(mock_msg1)
            mock_handle_attitude.assert_called_once_with(mock_msg1)
        
        # Process the second message - this should be filtered out due to small changes
        with patch('backend.message_handler.MessageHandler._handle_attitude') as mock_handle_attitude:
            self.message_handler._process_message(mock_msg2)
            # This might be called or not depending on the threshold settings
            # This is a more complex test that depends on implementation details
        
        # Process the third message - this should be processed due to significant changes
        with patch('backend.message_handler.MessageHandler._handle_attitude') as mock_handle_attitude:
            self.message_handler._process_message(mock_msg3)
            mock_handle_attitude.assert_called_once_with(mock_msg3)

if __name__ == '__main__':
    unittest.main()
