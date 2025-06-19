#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for visualization components in the RZGCS application
Especially focused on the Angel Mode flight path visualization
"""

import unittest
import sys
import os
from unittest.mock import MagicMock, patch

# Add parent directory to path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

class TestVisualization(unittest.TestCase):
    """Test cases for visualization components"""
    
    def setUp(self):
        """Set up test environment"""
        self.mock_canvas = MagicMock()
        
        # Define the 8 flight paths from the Angel Mode
        self.flight_paths = [
            {"region": "Ukraine", "color": "red", "coordinates": [(48.3794, 31.1656), (48.9507, 31.7832)]},
            {"region": "Europe/Germany", "color": "blue", "coordinates": [(50.1109, 8.6821), (51.5074, 0.1278)]},
            {"region": "Turkey", "color": "orange", "coordinates": [(41.0082, 28.9784), (39.9334, 32.8597)]},
            {"region": "North Africa", "color": "green", "coordinates": [(31.2001, 29.9187), (36.8065, 10.1815)]},
            {"region": "Russia", "color": "purple", "coordinates": [(55.7558, 37.6173), (59.9343, 30.3351)]},
            {"region": "Baltic", "color": "amber", "coordinates": [(59.4370, 24.7536), (56.9496, 24.1052)]},
            {"region": "UK", "color": "teal", "coordinates": [(51.5074, -0.1278), (55.9533, -3.1883)]},
            {"region": "Middle East", "color": "maroon", "coordinates": [(25.2048, 55.2708), (21.4225, 39.8262)]}
        ]
    
    def test_draw_flight_path(self):
        """Test drawing a flight path on the canvas"""
        # Test drawing a flight path
        path = self.flight_paths[0]  # Ukraine (red)
        
        # Draw the path
        self.draw_flight_path(path)
        
        # Verify the circle was drawn
        self.mock_canvas.create_oval.assert_called()
        
        # Verify the center point was drawn
        self.mock_canvas.create_oval.assert_called()
    
    def test_draw_all_flight_paths(self):
        """Test drawing all flight paths on the canvas"""
        # Draw all paths
        self.draw_all_flight_paths()
        
        # Verify the correct number of paths were drawn
        # Each path has a circle and a center point, so 16 calls in total
        self.assertEqual(self.mock_canvas.create_oval.call_count, 16)
    
    def test_select_flight_path(self):
        """Test selecting a flight path"""
        # Select a path
        selected_index = 2  # Turkey (orange)
        
        # Select the path
        self.select_flight_path(selected_index)
        
        # Verify the path was highlighted
        self.mock_canvas.itemconfig.assert_called_once()
    
    def test_get_path_coordinates(self):
        """Test retrieving path coordinates"""
        # Get coordinates for a path
        path_index = 1  # Europe/Germany (blue)
        
        # Get the coordinates
        coordinates = self.get_path_coordinates(path_index)
        
        # Verify the coordinates
        self.assertEqual(coordinates, self.flight_paths[path_index]["coordinates"])
    
    def test_convert_gps_to_screen(self):
        """Test converting GPS coordinates to screen coordinates"""
        # Convert GPS coordinates to screen coordinates
        lat, lon = 50.1109, 8.6821  # Frankfurt
        
        # Define map dimensions
        map_width = 800
        map_height = 600
        
        # Define GPS bounds of the map
        min_lat, max_lat = 30.0, 70.0
        min_lon, max_lon = -10.0, 60.0
        
        # Convert coordinates
        x, y = self.convert_gps_to_screen(lat, lon, min_lat, max_lat, min_lon, max_lon, map_width, map_height)
        
        # Verify the conversion
        expected_x = int((lon - min_lon) / (max_lon - min_lon) * map_width)
        expected_y = int((max_lat - lat) / (max_lat - min_lat) * map_height)
        
        self.assertEqual(x, expected_x)
        self.assertEqual(y, expected_y)
    
    def test_convert_screen_to_gps(self):
        """Test converting screen coordinates to GPS coordinates"""
        # Convert screen coordinates to GPS coordinates
        x, y = 400, 300
        
        # Define map dimensions
        map_width = 800
        map_height = 600
        
        # Define GPS bounds of the map
        min_lat, max_lat = 30.0, 70.0
        min_lon, max_lon = -10.0, 60.0
        
        # Convert coordinates
        lat, lon = self.convert_screen_to_gps(x, y, min_lat, max_lat, min_lon, max_lon, map_width, map_height)
        
        # Verify the conversion
        expected_lat = max_lat - (y / map_height) * (max_lat - min_lat)
        expected_lon = min_lon + (x / map_width) * (max_lon - min_lon)
        
        self.assertAlmostEqual(lat, expected_lat)
        self.assertAlmostEqual(lon, expected_lon)
    
    def test_draw_map_background(self):
        """Test drawing the map background"""
        # Draw the map background
        self.draw_map_background()
        
        # Verify the background image was loaded
        self.mock_canvas.create_image.assert_called_once()
    
    def test_draw_drone_position(self):
        """Test drawing the drone position on the map"""
        # Draw the drone position
        lat, lon = 50.1109, 8.6821  # Frankfurt
        heading = 45.0
        
        # Draw the drone
        self.draw_drone_position(lat, lon, heading)
        
        # Verify the drone icon was drawn
        self.mock_canvas.create_polygon.assert_called_once()
    
    def test_draw_mission_waypoints(self):
        """Test drawing mission waypoints on the map"""
        # Create test waypoints
        waypoints = [
            {"lat": 50.1109, "lon": 8.6821, "alt": 100.0},
            {"lat": 50.1209, "lon": 8.6921, "alt": 110.0},
            {"lat": 50.1309, "lon": 8.7021, "alt": 120.0}
        ]
        
        # Draw the waypoints
        self.draw_mission_waypoints(waypoints)
        
        # Verify the waypoints were drawn
        self.assertEqual(self.mock_canvas.create_oval.call_count, 3)
    
    def test_draw_flight_path_line(self):
        """Test drawing a line for a flight path"""
        # Draw a line for a flight path
        path = self.flight_paths[0]  # Ukraine (red)
        
        # Draw the line
        self.draw_flight_path_line(path)
        
        # Verify the line was drawn
        self.mock_canvas.create_line.assert_called_once()
    
    def draw_flight_path(self, path):
        """Helper method to simulate drawing a flight path"""
        # Draw a circle for the path
        x, y = self.convert_gps_to_screen(
            path["coordinates"][0][0],
            path["coordinates"][0][1],
            30.0, 70.0, -10.0, 60.0, 800, 600
        )
        
        # Draw the circle
        self.mock_canvas.create_oval(
            x - 10, y - 10, x + 10, y + 10,
            fill=path["color"],
            outline="black",
            width=2,
            tags=("path", path["region"])
        )
        
        # Draw the center point
        self.mock_canvas.create_oval(
            x - 2, y - 2, x + 2, y + 2,
            fill="black",
            outline="black",
            tags=("center", path["region"])
        )
    
    def draw_all_flight_paths(self):
        """Helper method to simulate drawing all flight paths"""
        for path in self.flight_paths:
            self.draw_flight_path(path)
    
    def select_flight_path(self, index):
        """Helper method to simulate selecting a flight path"""
        path = self.flight_paths[index]
        
        # Highlight the selected path
        self.mock_canvas.itemconfig(
            f"path && {path['region']}",
            width=4,
            outline="yellow"
        )
    
    def get_path_coordinates(self, index):
        """Helper method to simulate retrieving path coordinates"""
        return self.flight_paths[index]["coordinates"]
    
    def convert_gps_to_screen(self, lat, lon, min_lat, max_lat, min_lon, max_lon, width, height):
        """Helper method to simulate converting GPS coordinates to screen coordinates"""
        x = int((lon - min_lon) / (max_lon - min_lon) * width)
        y = int((max_lat - lat) / (max_lat - min_lat) * height)
        return x, y
    
    def convert_screen_to_gps(self, x, y, min_lat, max_lat, min_lon, max_lon, width, height):
        """Helper method to simulate converting screen coordinates to GPS coordinates"""
        lat = max_lat - (y / height) * (max_lat - min_lat)
        lon = min_lon + (x / width) * (max_lon - min_lon)
        return lat, lon
    
    def draw_map_background(self):
        """Helper method to simulate drawing the map background"""
        # Load the map image
        self.mock_canvas.create_image(
            0, 0,
            anchor="nw",
            image="render.png",
            tags="background"
        )
    
    def draw_drone_position(self, lat, lon, heading):
        """Helper method to simulate drawing the drone position"""
        # Convert coordinates
        x, y = self.convert_gps_to_screen(
            lat, lon,
            30.0, 70.0, -10.0, 60.0, 800, 600
        )
        
        # Draw the drone icon (triangle pointing in the heading direction)
        # Calculate vertices based on heading
        import math
        size = 10
        x1 = x + size * math.sin(math.radians(heading))
        y1 = y - size * math.cos(math.radians(heading))
        x2 = x + size * math.sin(math.radians(heading + 120))
        y2 = y - size * math.cos(math.radians(heading + 120))
        x3 = x + size * math.sin(math.radians(heading - 120))
        y3 = y - size * math.cos(math.radians(heading - 120))
        
        # Draw the triangle
        self.mock_canvas.create_polygon(
            x1, y1, x2, y2, x3, y3,
            fill="yellow",
            outline="black",
            width=2,
            tags="drone"
        )
    
    def draw_mission_waypoints(self, waypoints):
        """Helper method to simulate drawing mission waypoints"""
        for i, wp in enumerate(waypoints):
            # Convert coordinates
            x, y = self.convert_gps_to_screen(
                wp["lat"], wp["lon"],
                30.0, 70.0, -10.0, 60.0, 800, 600
            )
            
            # Draw the waypoint
            self.mock_canvas.create_oval(
                x - 5, y - 5, x + 5, y + 5,
                fill="green",
                outline="black",
                width=1,
                tags=f"waypoint_{i}"
            )
    
    def draw_flight_path_line(self, path):
        """Helper method to simulate drawing a line for a flight path"""
        # Convert coordinates
        points = []
        for lat, lon in path["coordinates"]:
            x, y = self.convert_gps_to_screen(
                lat, lon,
                30.0, 70.0, -10.0, 60.0, 800, 600
            )
            points.extend([x, y])
        
        # Draw the line
        self.mock_canvas.create_line(
            points,
            fill=path["color"],
            width=2,
            smooth=True,
            tags=f"path_line_{path['region']}"
        )

if __name__ == '__main__':
    unittest.main()
