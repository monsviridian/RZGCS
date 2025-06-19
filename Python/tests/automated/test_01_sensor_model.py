#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for the Sensor Model component
"""

import unittest
import sys
import os
from unittest.mock import MagicMock, patch

# Add parent directory to path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.sensorviewmodel import SensorViewModel

class TestSensorViewModel(unittest.TestCase):
    """Test cases for the SensorViewModel class"""
    
    def setUp(self):
        """Set up test environment"""
        self.model = SensorViewModel()
    
    def test_add_sensor(self):
        """Test adding a sensor to the model"""
        self.model.add_sensor("test_sensor", "Test Sensor", "unit")
        self.assertEqual(self.model.count, 1)
    
    def test_add_duplicate_sensor(self):
        """Test adding a duplicate sensor"""
        self.model.add_sensor("test_sensor", "Test Sensor", "unit")
        with self.assertRaises(ValueError):
            self.model.add_sensor("test_sensor", "Test Sensor", "unit")
    
    def test_update_sensor(self):
        """Test updating a sensor value"""
        self.model.add_sensor("test_sensor", "Test Sensor", "unit")
        self.model.update_sensor("test_sensor", 42.0)
        value = self.model.get_sensor_value("test_sensor")
        self.assertEqual(value, 42.0)
    
    def test_update_nonexistent_sensor(self):
        """Test updating a sensor that doesn't exist"""
        with self.assertRaises(KeyError):
            self.model.update_sensor("nonexistent", 42.0)
    
    def test_get_nonexistent_sensor(self):
        """Test getting a sensor that doesn't exist"""
        value = self.model.get_sensor_value("nonexistent")
        self.assertIsNone(value)
    
    def test_remove_sensor(self):
        """Test removing a sensor"""
        self.model.add_sensor("test_sensor", "Test Sensor", "unit")
        self.model.remove_sensor("test_sensor")
        self.assertEqual(self.model.count, 0)
    
    def test_remove_nonexistent_sensor(self):
        """Test removing a sensor that doesn't exist"""
        with self.assertRaises(KeyError):
            self.model.remove_sensor("nonexistent")
    
    def test_clear_sensors(self):
        """Test clearing all sensors"""
        self.model.add_sensor("test1", "Test 1", "unit")
        self.model.add_sensor("test2", "Test 2", "unit")
        self.model.clear_sensors()
        self.assertEqual(self.model.count, 0)
    
    def test_get_all_sensors(self):
        """Test getting all sensors"""
        self.model.add_sensor("test1", "Test 1", "unit")
        self.model.add_sensor("test2", "Test 2", "unit")
        self.model.update_sensor("test1", 42.0)
        self.model.update_sensor("test2", 43.0)
        sensors = self.model.get_all_sensors()
        self.assertEqual(len(sensors), 2)
        self.assertEqual(sensors[0]["value"], 42.0)
        self.assertEqual(sensors[1]["value"], 43.0)

if __name__ == '__main__':
    unittest.main()
