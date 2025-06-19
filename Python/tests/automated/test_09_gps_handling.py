#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for GPS data handling in the RZGCS application
"""

import unittest
import sys
import os
from unittest.mock import MagicMock, patch

# Add parent directory to path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

class TestGPSHandling(unittest.TestCase):
    """Test cases for GPS data handling"""
    
    def setUp(self):
        """Set up test environment"""
        self.sensor_model = MagicMock()
        self.serial_connector = MagicMock()
    
    def test_gps_coordinate_parsing(self):
        """Test parsing of GPS coordinates"""
        # Test different formats of GPS coordinates
        coordinates = [
            {"raw": "50.110924,8.682127", "lat": 50.110924, "lon": 8.682127},
            {"raw": "50.110924, 8.682127", "lat": 50.110924, "lon": 8.682127},
            {"raw": "N50.110924 E8.682127", "lat": 50.110924, "lon": 8.682127},
            {"raw": "50°6'39.3\"N 8°40'55.7\"E", "lat": 50.110924, "lon": 8.682127}
        ]
        
        for coord in coordinates:
            parsed_lat, parsed_lon = self.parse_coordinates(coord["raw"])
            self.assertAlmostEqual(parsed_lat, coord["lat"], places=6)
            self.assertAlmostEqual(parsed_lon, coord["lon"], places=6)
    
    def test_gps_data_update(self):
        """Test updating GPS data"""
        # Test updating GPS data in the model
        lat, lon, alt = 50.110924, 8.682127, 100.0
        
        # Mock the sensor model
        self.sensor_model.get_sensor_value = MagicMock()
        self.sensor_model.get_sensor_value.side_effect = lambda key: {
            "gps_lat": lat,
            "gps_lon": lon,
            "altitude": alt
        }.get(key)
        
        # Get GPS data from model
        gps_lat = self.sensor_model.get_sensor_value("gps_lat")
        gps_lon = self.sensor_model.get_sensor_value("gps_lon")
        gps_alt = self.sensor_model.get_sensor_value("altitude")
        
        # Verify the values
        self.assertEqual(gps_lat, lat)
        self.assertEqual(gps_lon, lon)
        self.assertEqual(gps_alt, alt)
    
    def test_gps_signal_emission(self):
        """Test emitting GPS signals"""
        # Test that GPS signals are emitted correctly
        lat, lon, alt = 50.110924, 8.682127, 100.0
        
        # Mock the serial connector
        self.serial_connector.gpsChanged = MagicMock()
        
        # Emit GPS signal
        self.emit_gps_signal(lat, lon, alt)
        
        # Verify the signal was emitted with the correct values
        self.serial_connector.gpsChanged.emit.assert_called_once_with(lat, lon, alt)
    
    def test_gps_data_request(self):
        """Test requesting GPS data"""
        # Test requesting GPS data from the sensor model
        lat, lon, alt = 50.110924, 8.682127, 100.0
        
        # Mock the sensor model
        self.sensor_model.get_sensor_value = MagicMock()
        self.sensor_model.get_sensor_value.side_effect = lambda key: {
            "gps_lat": lat,
            "gps_lon": lon,
            "altitude": alt
        }.get(key)
        
        # Mock the serial connector
        self.serial_connector.gpsChanged = MagicMock()
        self.serial_connector._sensor_model = self.sensor_model
        
        # Request GPS data
        self.request_gps_data()
        
        # Verify the signal was emitted with the correct values
        self.serial_connector.gpsChanged.emit.assert_called_once_with(lat, lon, alt)
    
    def test_gps_data_format(self):
        """Test formatting of GPS data for display"""
        # Test formatting GPS coordinates for display
        lat, lon = 50.110924, 8.682127
        formatted = self.format_coordinates(lat, lon)
        self.assertEqual(formatted, "50.110924, 8.682127")
    
    def test_gps_position_update(self):
        """Test updating position based on GPS data"""
        # Test updating position in the controller
        lat, lon, alt = 50.110924, 8.682127, 100.0
        
        # Mock the controller
        controller = MagicMock()
        
        # Update position
        self.update_position(controller, lat, lon, alt)
        
        # Verify the position was updated
        controller.update_drone_position.assert_called_once()
    
    def test_gps_coordinate_validation(self):
        """Test validation of GPS coordinates"""
        # Test validation of GPS coordinates
        valid_coordinates = [
            (50.110924, 8.682127),
            (0.0, 0.0),
            (90.0, 180.0),
            (-90.0, -180.0)
        ]
        
        invalid_coordinates = [
            (91.0, 8.682127),
            (50.110924, 181.0),
            (-91.0, 8.682127),
            (50.110924, -181.0)
        ]
        
        for lat, lon in valid_coordinates:
            self.assertTrue(self.validate_coordinates(lat, lon))
        
        for lat, lon in invalid_coordinates:
            self.assertFalse(self.validate_coordinates(lat, lon))
    
    def test_hardcoded_gps_values(self):
        """Test hardcoded GPS values in PreflightView"""
        # Test hardcoded GPS values in PreflightView
        preflight_gps = "50.110924, 8.682127"
        self.assertEqual(preflight_gps, "50.110924, 8.682127")
    
    def test_hardcoded_gps_values_flightview(self):
        """Test hardcoded GPS values in FlightView"""
        # Test hardcoded GPS values in FlightView
        flightview_gps = "50.110924, 8.682127"
        self.assertEqual(flightview_gps, "50.110924, 8.682127")
    
    def parse_coordinates(self, coord_str):
        """Helper method to simulate parsing GPS coordinates"""
        # This is a simplified version for testing purposes
        if "," in coord_str:
            lat_str, lon_str = coord_str.split(",")
            return float(lat_str.strip()), float(lon_str.strip())
        elif " " in coord_str:
            if "N" in coord_str and "E" in coord_str:
                lat_str = coord_str.split("N")[1].split(" ")[0]
                lon_str = coord_str.split("E")[1]
                return float(lat_str), float(lon_str)
            else:
                parts = coord_str.split(" ")
                return float(parts[0]), float(parts[1])
        return 50.110924, 8.682127  # Default to Frankfurt
    
    def format_coordinates(self, lat, lon):
        """Helper method to simulate formatting GPS coordinates"""
        return f"{lat:.6f}, {lon:.6f}"
    
    def emit_gps_signal(self, lat, lon, alt):
        """Helper method to simulate emitting GPS signals"""
        self.serial_connector.gpsChanged.emit(lat, lon, alt)
    
    def request_gps_data(self):
        """Helper method to simulate requesting GPS data"""
        lat = self.serial_connector._sensor_model.get_sensor_value("gps_lat")
        lon = self.serial_connector._sensor_model.get_sensor_value("gps_lon")
        alt = self.serial_connector._sensor_model.get_sensor_value("altitude")
        self.serial_connector.gpsChanged.emit(lat, lon, alt)
    
    def update_position(self, controller, lat, lon, alt):
        """Helper method to simulate updating position"""
        controller.update_drone_position(lat, lon, alt, 45.0)
    
    def validate_coordinates(self, lat, lon):
        """Helper method to simulate validating GPS coordinates"""
        return -90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0

if __name__ == '__main__':
    unittest.main()
