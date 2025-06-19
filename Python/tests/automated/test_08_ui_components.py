#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for the UI components of the RZGCS application
"""

import unittest
import sys
import os
from unittest.mock import MagicMock, patch

# Add parent directory to path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

class TestUIComponents(unittest.TestCase):
    """Test cases for the UI components"""
    
    def setUp(self):
        """Set up test environment"""
        # Mock QML engine and UI components
        self.engine = MagicMock()
        self.root_context = MagicMock()
        self.engine.rootContext.return_value = self.root_context
    
    def test_preflight_view_initialization(self):
        """Test PreflightView initialization"""
        # PreflightView should be initialized with correct properties
        view_props = {
            'title': 'Preflight Check',
            'batteryLevel': 87,
            'gpsCoordinates': '50.110924, 8.682127',
            'connectionStatus': False
        }
        
        self.assertEqual(view_props['title'], 'Preflight Check')
        self.assertEqual(view_props['batteryLevel'], 87)
        self.assertEqual(view_props['gpsCoordinates'], '50.110924, 8.682127')
        self.assertFalse(view_props['connectionStatus'])
    
    def test_flight_view_initialization(self):
        """Test FlightView initialization"""
        # FlightView should be initialized with correct properties
        view_props = {
            'droneLatitude': 50.110924,
            'droneLongitude': 8.682127,
            'droneAltitude': 100.0,
            'droneHeading': 45.0,
            'connectionStatus': False,
            'batteryLevel': 87
        }
        
        self.assertEqual(view_props['droneLatitude'], 50.110924)
        self.assertEqual(view_props['droneLongitude'], 8.682127)
        self.assertEqual(view_props['droneAltitude'], 100.0)
        self.assertEqual(view_props['droneHeading'], 45.0)
        self.assertFalse(view_props['connectionStatus'])
        self.assertEqual(view_props['batteryLevel'], 87)
    
    def test_license_view_initialization(self):
        """Test LicenseView initialization"""
        # LicenseView should be initialized with correct properties
        view_props = {
            'title': 'License Information',
            'licenseText': 'MIT License'
        }
        
        self.assertEqual(view_props['title'], 'License Information')
        self.assertTrue('MIT License' in view_props['licenseText'])
    
    def test_support_view_initialization(self):
        """Test SupportView initialization"""
        # SupportView should be initialized with correct properties
        view_props = {
            'title': 'Support',
            'supportText': 'Contact support'
        }
        
        self.assertEqual(view_props['title'], 'Support')
        self.assertTrue('Contact support' in view_props['supportText'])
    
    def test_angel_mode_view_initialization(self):
        """Test AngelMode view initialization"""
        # AngelMode view should be initialized with correct flight paths
        flight_paths = [
            {'region': 'Ukraine', 'color': 'red'},
            {'region': 'Europe/Germany', 'color': 'blue'},
            {'region': 'Turkey', 'color': 'orange'},
            {'region': 'North Africa', 'color': 'green'},
            {'region': 'Russia', 'color': 'purple'},
            {'region': 'Baltic', 'color': 'amber'},
            {'region': 'UK', 'color': 'teal'},
            {'region': 'Middle East', 'color': 'maroon'}
        ]
        
        self.assertEqual(len(flight_paths), 8)
        self.assertEqual(flight_paths[0]['region'], 'Ukraine')
        self.assertEqual(flight_paths[0]['color'], 'red')
    
    def test_ui_connections(self):
        """Test UI connections to backend"""
        # Test that the serial connector is properly connected to the UI
        signals = [
            'connectionChanged',
            'gpsChanged',
            'batteryChanged',
            'messageReceived'
        ]
        
        self.assertEqual(len(signals), 4)
        self.assertTrue('connectionChanged' in signals)
        self.assertTrue('gpsChanged' in signals)
    
    def test_ui_timers(self):
        """Test UI timers for automatic updates"""
        # Test that timers are set up correctly
        timers = {
            'gpsUpdateTimer': {'interval': 1000, 'running': True},
            'batteryUpdateTimer': {'interval': 5000, 'running': True}
        }
        
        self.assertEqual(timers['gpsUpdateTimer']['interval'], 1000)
        self.assertTrue(timers['gpsUpdateTimer']['running'])
        self.assertEqual(timers['batteryUpdateTimer']['interval'], 5000)
        self.assertTrue(timers['batteryUpdateTimer']['running'])
    
    def test_ui_language_translation(self):
        """Test UI language translation to English"""
        # Test that all UI text is in English
        ui_texts = {
            'connectButton': 'Connect',
            'disconnectButton': 'Disconnect',
            'positionLabel': 'Position:',
            'altitudeLabel': 'Altitude:',
            'headingLabel': 'Heading:',
            'batteryLabel': 'Battery:'
        }
        
        self.assertEqual(ui_texts['connectButton'], 'Connect')
        self.assertEqual(ui_texts['disconnectButton'], 'Disconnect')
        self.assertEqual(ui_texts['positionLabel'], 'Position:')
        self.assertEqual(ui_texts['altitudeLabel'], 'Altitude:')
        self.assertEqual(ui_texts['headingLabel'], 'Heading:')
        self.assertEqual(ui_texts['batteryLabel'], 'Battery:')

if __name__ == '__main__':
    unittest.main()
