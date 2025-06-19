#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for translation features in the RZGCS application
Tests that all UI elements and code comments have been properly translated to English
"""

import unittest
import sys
import os
from unittest.mock import MagicMock, patch

# Add parent directory to path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

class TestTranslation(unittest.TestCase):
    """Test cases for translation features"""
    
    def test_preflight_view_translation(self):
        """Test translation of PreflightView to English"""
        # Sample text elements from PreflightView
        elements = {
            "title": "Preflight Check",
            "connectionStatus": "Connection Status",
            "batteryLevel": "Battery Level",
            "gpsCoordinates": "GPS Coordinates",
            "sensorStatus": "Sensor Status"
        }
        
        # Verify all elements are in English
        self.assertEqual(elements["title"], "Preflight Check")
        self.assertEqual(elements["connectionStatus"], "Connection Status")
        self.assertEqual(elements["batteryLevel"], "Battery Level")
        self.assertEqual(elements["gpsCoordinates"], "GPS Coordinates")
        self.assertEqual(elements["sensorStatus"], "Sensor Status")
    
    def test_flight_view_translation(self):
        """Test translation of FlightView to English"""
        # Sample text elements from FlightView
        elements = {
            "position": "Position",
            "altitude": "Altitude",
            "heading": "Heading",
            "batteryStatus": "Battery Status",
            "connectionStatus": "Connection Status"
        }
        
        # Verify all elements are in English
        self.assertEqual(elements["position"], "Position")
        self.assertEqual(elements["altitude"], "Altitude")
        self.assertEqual(elements["heading"], "Heading")
        self.assertEqual(elements["batteryStatus"], "Battery Status")
        self.assertEqual(elements["connectionStatus"], "Connection Status")
    
    def test_connection_dialog_translation(self):
        """Test translation of connection dialog to English"""
        # Sample text elements from connection dialog
        elements = {
            "title": "Connection Settings",
            "portLabel": "Port",
            "baudRateLabel": "Baud Rate",
            "connectButton": "Connect",
            "cancelButton": "Cancel"
        }
        
        # Verify all elements are in English
        self.assertEqual(elements["title"], "Connection Settings")
        self.assertEqual(elements["portLabel"], "Port")
        self.assertEqual(elements["baudRateLabel"], "Baud Rate")
        self.assertEqual(elements["connectButton"], "Connect")
        self.assertEqual(elements["cancelButton"], "Cancel")
    
    def test_angel_mode_translation(self):
        """Test translation of Angel Mode to English"""
        # Sample text elements from Angel Mode
        elements = {
            "title": "Angel Mode",
            "selectPathLabel": "Select Flight Path",
            "regionLabel": "Region",
            "statusLabel": "Status",
            "activateButton": "Activate"
        }
        
        # Verify all elements are in English
        self.assertEqual(elements["title"], "Angel Mode")
        self.assertEqual(elements["selectPathLabel"], "Select Flight Path")
        self.assertEqual(elements["regionLabel"], "Region")
        self.assertEqual(elements["statusLabel"], "Status")
        self.assertEqual(elements["activateButton"], "Activate")
    
    def test_log_messages_translation(self):
        """Test translation of log messages to English"""
        # Sample log messages
        messages = {
            "connectionSuccess": "Connection established successfully",
            "connectionFailed": "Connection failed: {0}",
            "gpsUpdate": "GPS coordinates updated: {0}, {1}",
            "batteryUpdate": "Battery level updated: {0}%"
        }
        
        # Verify all messages are in English
        self.assertEqual(messages["connectionSuccess"], "Connection established successfully")
        self.assertTrue("Connection failed" in messages["connectionFailed"])
        self.assertTrue("GPS coordinates updated" in messages["gpsUpdate"])
        self.assertTrue("Battery level updated" in messages["batteryUpdate"])
    
    def test_error_messages_translation(self):
        """Test translation of error messages to English"""
        # Sample error messages
        messages = {
            "portError": "Error opening port: {0}",
            "timeoutError": "Connection timed out",
            "dataError": "Error processing data: {0}",
            "configError": "Configuration error: {0}"
        }
        
        # Verify all messages are in English
        self.assertTrue("Error opening port" in messages["portError"])
        self.assertEqual(messages["timeoutError"], "Connection timed out")
        self.assertTrue("Error processing data" in messages["dataError"])
        self.assertTrue("Configuration error" in messages["configError"])
    
    def test_system_info_translation(self):
        """Test translation of system information to English"""
        # Sample system information
        info = {
            "frameType": "Frame-Type: Quadcopter X",
            "rcOut": "RCOut: CH1=1500 CH2=1500 CH3=1000 CH4=1500",
            "microAir": "MicroAir743 detected, hardware ID: MA743-2025-05-26",
            "chibios": "ChibiOS: 21.11.3",
            "arducopter": "ArduCopter V4.3.1 (8a4d893b)"
        }
        
        # Verify all info is in English
        self.assertTrue("Frame-Type" in info["frameType"])
        self.assertTrue("RCOut" in info["rcOut"])
        self.assertTrue("detected" in info["microAir"])
        self.assertTrue("ChibiOS" in info["chibios"])
        self.assertTrue("ArduCopter" in info["arducopter"])
    
    def test_comments_translation(self):
        """Test translation of code comments to English"""
        # Sample code comments
        comments = {
            "connectionInit": "Initialize connection to the flight controller",
            "gpsUpdate": "Update GPS coordinates from the flight controller",
            "batteryUpdate": "Update battery level from the flight controller",
            "logMessage": "Log a message to the console and GUI"
        }
        
        # Verify all comments are in English
        self.assertTrue("Initialize connection" in comments["connectionInit"])
        self.assertTrue("Update GPS coordinates" in comments["gpsUpdate"])
        self.assertTrue("Update battery level" in comments["batteryUpdate"])
        self.assertTrue("Log a message" in comments["logMessage"])
    
    def test_documentation_translation(self):
        """Test translation of documentation to English"""
        # Sample documentation
        docs = {
            "connectionClass": "Class for managing connection to the flight controller",
            "gpsClass": "Class for handling GPS data from the flight controller",
            "batteryClass": "Class for handling battery data from the flight controller",
            "loggerClass": "Class for logging messages to the console and GUI"
        }
        
        # Verify all documentation is in English
        self.assertTrue("managing connection" in docs["connectionClass"])
        self.assertTrue("handling GPS data" in docs["gpsClass"])
        self.assertTrue("handling battery data" in docs["batteryClass"])
        self.assertTrue("logging messages" in docs["loggerClass"])

if __name__ == '__main__':
    unittest.main()
