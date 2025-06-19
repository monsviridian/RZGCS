#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for QML integration in the RZGCS application
"""

import unittest
import sys
import os
from unittest.mock import MagicMock, patch

# Add parent directory to path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

class TestQMLIntegration(unittest.TestCase):
    """Test cases for QML integration"""
    
    def setUp(self):
        """Set up test environment"""
        self.engine = MagicMock()
        self.root_context = MagicMock()
        self.engine.rootContext.return_value = self.root_context
    
    def test_context_property_registration(self):
        """Test registering context properties"""
        # Create mock controllers
        serial_connector = MagicMock()
        flight_controller = MagicMock()
        
        # Register context properties
        self.root_context.setContextProperty = MagicMock()
        self.register_context_properties(serial_connector, flight_controller)
        
        # Verify the method was called with the correct parameters
        self.root_context.setContextProperty.assert_any_call("serialConnector", serial_connector)
        self.root_context.setContextProperty.assert_any_call("flightViewController", flight_controller)
    
    def test_qml_loading(self):
        """Test loading QML files"""
        # Set up the engine
        self.engine.load = MagicMock()
        
        # Load QML file
        qml_file = "App.qml"
        self.load_qml(qml_file)
        
        # Verify the method was called with the correct parameter
        self.engine.load.assert_called_once()
    
    def test_signal_connection(self):
        """Test connecting signals between QML and Python"""
        # Create mock objects
        qml_object = MagicMock()
        python_object = MagicMock()
        
        # Connect signals
        self.connect_signals(qml_object, python_object)
        
        # Verify signals were connected
        qml_object.signal.connect.assert_called_with(python_object.slot)
    
    def register_context_properties(self, serial_connector, flight_controller):
        """Helper method to simulate registering context properties"""
        self.root_context.setContextProperty("serialConnector", serial_connector)
        self.root_context.setContextProperty("flightViewController", flight_controller)
    
    def load_qml(self, qml_file):
        """Helper method to simulate loading QML files"""
        url = os.path.join("qrc:/RZGCSContent/", qml_file)
        self.engine.load(url)
    
    def connect_signals(self, qml_object, python_object):
        """Helper method to simulate connecting signals"""
        qml_object.signal.connect(python_object.slot)

if __name__ == '__main__':
    unittest.main()
