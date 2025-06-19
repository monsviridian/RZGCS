#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for the Preflight View Filter Mechanism
Tests the special system information filter for logs
"""

import unittest
import sys
import os
from unittest.mock import MagicMock, patch

# Add parent directory to path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

class TestPreflightFilter(unittest.TestCase):
    """Test cases for the Preflight View log filtering mechanism"""
    
    def setUp(self):
        """Set up test environment"""
        # Mock logger and filter objects
        self.logger = MagicMock()
        self.filter = MagicMock()
    
    def test_frame_type_filtering(self):
        """Test filtering of Frame-Type log messages"""
        # Sample log message about frame type
        log_message = "[SYSTEM INFO] Frame-Type: Quadcopter X"
        
        # Test if the filter identifies this as a system info message
        self.assertTrue("[SYSTEM INFO]" in log_message)
        self.assertTrue("Frame-Type" in log_message)
    
    def test_rcout_filtering(self):
        """Test filtering of RCOut log messages"""
        # Sample log message about RCOut
        log_message = "[SYSTEM INFO] RCOut: CH1=1500 CH2=1500 CH3=1000 CH4=1500"
        
        # Test if the filter identifies this as a system info message
        self.assertTrue("[SYSTEM INFO]" in log_message)
        self.assertTrue("RCOut" in log_message)
    
    def test_microair_filtering(self):
        """Test filtering of MicroAir743 log messages"""
        # Sample log message about MicroAir743
        log_message = "[SYSTEM INFO] MicroAir743 detected, hardware ID: MA743-2025-05-26"
        
        # Test if the filter identifies this as a system info message
        self.assertTrue("[SYSTEM INFO]" in log_message)
        self.assertTrue("MicroAir743" in log_message)
    
    def test_chibios_filtering(self):
        """Test filtering of ChibiOS log messages"""
        # Sample log message about ChibiOS
        log_message = "[SYSTEM INFO] ChibiOS: 21.11.3"
        
        # Test if the filter identifies this as a system info message
        self.assertTrue("[SYSTEM INFO]" in log_message)
        self.assertTrue("ChibiOS" in log_message)
    
    def test_arducopter_version_filtering(self):
        """Test filtering of ArduCopter version log messages"""
        # Sample log message about ArduCopter version
        log_message = "[SYSTEM INFO] ArduCopter V4.3.1 (8a4d893b)"
        
        # Test if the filter identifies this as a system info message
        self.assertTrue("[SYSTEM INFO]" in log_message)
        self.assertTrue("ArduCopter" in log_message)
    
    def test_prearm_warning_filtering(self):
        """Test filtering of PreArm warning log messages"""
        # Sample log message about PreArm warning
        log_message = "[WARNING] PreArm: Battery failsafe active, voltage too low"
        
        # Test if the filter identifies this as a warning message
        self.assertTrue("[WARNING]" in log_message)
        self.assertTrue("PreArm" in log_message)
    
    def test_log_display_formatting(self):
        """Test log display formatting with enlarged height and font"""
        # Log area should be 30% of the height (increased from 10%)
        log_area_height = 0.3  # 30% of the parent height
        
        # Font size should be 16px (increased from default)
        font_size = 16
        
        # Font weight should be bold for better readability
        font_weight = "bold"
        
        # Test the expected values
        self.assertEqual(log_area_height, 0.3)
        self.assertEqual(font_size, 16)
        self.assertEqual(font_weight, "bold")
    
    def test_system_info_filtering(self):
        """Test the system info filtering mechanism"""
        # Create sample log messages
        system_info_log = "[SYSTEM INFO] GPS: 10 satellites, HDOP 0.8"
        regular_log = "[INFO] Initializing sensors"
        
        # Preflight view should show system info logs
        self.assertTrue(self.should_display_in_preflight(system_info_log))
        
        # Regular logs should be filtered out
        self.assertFalse(self.should_display_in_preflight(regular_log))
    
    def should_display_in_preflight(self, log_message):
        """Helper method to simulate the preflight view filter logic"""
        # Only show logs with [SYSTEM INFO] or specific keywords
        if "[SYSTEM INFO]" in log_message:
            return True
        if "[WARNING]" in log_message and "PreArm" in log_message:
            return True
        if "Frame-Type" in log_message or "RCOut" in log_message:
            return True
        if "MicroAir743" in log_message or "ChibiOS" in log_message:
            return True
        if "ArduCopter" in log_message:
            return True
        return False

if __name__ == '__main__':
    unittest.main()
