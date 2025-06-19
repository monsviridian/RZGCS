#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for the Logger component in the RZGCS application
"""

import unittest
import sys
import os
import time
from unittest.mock import MagicMock, patch
from io import StringIO

# Add parent directory to path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.logger import Logger

class TestLogger(unittest.TestCase):
    """Test cases for the Logger class"""
    
    def setUp(self):
        """Set up test environment"""
        self.logger = Logger()
    
    def test_initialization(self):
        """Test Logger initialization"""
        self.assertIsNotNone(self.logger)
        self.assertTrue(hasattr(self.logger, 'log'))
    
    def test_log_info(self):
        """Test logging info messages"""
        # Mock the signal
        self.logger.log = MagicMock()
        
        # Log an info message
        self.logger.info("Test info message")
        
        # Verify the signal was emitted
        self.logger.log.emit.assert_called_once()
        # Extract the arguments
        args = self.logger.log.emit.call_args[0]
        # Verify the message contains the log level and message
        self.assertTrue("[INFO]" in args[0])
        self.assertTrue("Test info message" in args[0])
    
    def test_log_warning(self):
        """Test logging warning messages"""
        # Mock the signal
        self.logger.log = MagicMock()
        
        # Log a warning message
        self.logger.warning("Test warning message")
        
        # Verify the signal was emitted
        self.logger.log.emit.assert_called_once()
        # Extract the arguments
        args = self.logger.log.emit.call_args[0]
        # Verify the message contains the log level and message
        self.assertTrue("[WARNING]" in args[0])
        self.assertTrue("Test warning message" in args[0])
    
    def test_log_error(self):
        """Test logging error messages"""
        # Mock the signal
        self.logger.log = MagicMock()
        
        # Log an error message
        self.logger.error("Test error message")
        
        # Verify the signal was emitted
        self.logger.log.emit.assert_called_once()
        # Extract the arguments
        args = self.logger.log.emit.call_args[0]
        # Verify the message contains the log level and message
        self.assertTrue("[ERROR]" in args[0])
        self.assertTrue("Test error message" in args[0])
    
    def test_log_debug(self):
        """Test logging debug messages"""
        # Mock the signal
        self.logger.log = MagicMock()
        
        # Log a debug message
        self.logger.debug("Test debug message")
        
        # Verify the signal was emitted
        self.logger.log.emit.assert_called_once()
        # Extract the arguments
        args = self.logger.log.emit.call_args[0]
        # Verify the message contains the log level and message
        self.assertTrue("[DEBUG]" in args[0])
        self.assertTrue("Test debug message" in args[0])
    
    def test_log_system_info(self):
        """Test logging system info messages"""
        # Mock the signal
        self.logger.log = MagicMock()
        
        # Log a system info message
        self.logger.system_info("Test system info message")
        
        # Verify the signal was emitted
        self.logger.log.emit.assert_called_once()
        # Extract the arguments
        args = self.logger.log.emit.call_args[0]
        # Verify the message contains the log level and message
        self.assertTrue("[SYSTEM INFO]" in args[0])
        self.assertTrue("Test system info message" in args[0])
    
    def test_log_with_timestamp(self):
        """Test that log messages include timestamps"""
        # Mock the signal
        self.logger.log = MagicMock()
        
        # Log a message
        self.logger.info("Test message")
        
        # Verify the signal was emitted
        self.logger.log.emit.assert_called_once()
        # Extract the arguments
        args = self.logger.log.emit.call_args[0]
        # Verify the message contains a timestamp (format: [YYYY-MM-DD HH:MM:SS])
        self.assertRegex(args[0], r'\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\]')
    
    def test_log_file_output(self):
        """Test logging to a file"""
        # Create a temporary log file
        log_file = "test_log.txt"
        
        # Create a logger with file output
        logger_with_file = Logger(log_file=log_file)
        
        # Log some messages
        logger_with_file.info("Test info message")
        logger_with_file.warning("Test warning message")
        logger_with_file.error("Test error message")
        
        # Close the logger to ensure all data is written
        if hasattr(logger_with_file, 'file_handler'):
            logger_with_file.file_handler.close()
        
        # Check if the log file exists and contains the messages
        self.assertTrue(os.path.exists(log_file))
        
        # Read the log file
        with open(log_file, 'r') as f:
            log_content = f.read()
        
        # Verify the log file contains the messages
        self.assertTrue("Test info message" in log_content)
        self.assertTrue("Test warning message" in log_content)
        self.assertTrue("Test error message" in log_content)
        
        # Clean up
        if os.path.exists(log_file):
            os.remove(log_file)
    
    def test_system_info_filter(self):
        """Test that system info filter works correctly"""
        # Create mock messages
        system_info_msg = "[SYSTEM INFO] Test system info message"
        regular_info_msg = "[INFO] Test regular info message"
        
        # Check if the system info filter correctly identifies system info messages
        self.assertTrue(self.logger.is_system_info(system_info_msg))
        self.assertFalse(self.logger.is_system_info(regular_info_msg))
    
    def test_log_message_formatting(self):
        """Test that log messages are formatted correctly"""
        # Create different log messages
        info_msg = self.logger.format_message("INFO", "Test info message")
        warning_msg = self.logger.format_message("WARNING", "Test warning message")
        error_msg = self.logger.format_message("ERROR", "Test error message")
        debug_msg = self.logger.format_message("DEBUG", "Test debug message")
        system_info_msg = self.logger.format_message("SYSTEM INFO", "Test system info message")
        
        # Verify the messages are formatted correctly
        self.assertTrue("[INFO]" in info_msg)
        self.assertTrue("[WARNING]" in warning_msg)
        self.assertTrue("[ERROR]" in error_msg)
        self.assertTrue("[DEBUG]" in debug_msg)
        self.assertTrue("[SYSTEM INFO]" in system_info_msg)

if __name__ == '__main__':
    unittest.main()
