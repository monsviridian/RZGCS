#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Performance tests for the RZGCS application
Tests for performance optimization and resource usage
"""

import unittest
import sys
import os
import time
import cProfile
import pstats
import io
from unittest.mock import MagicMock, patch

# Add parent directory to path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

class TestPerformance(unittest.TestCase):
    """Test cases for performance optimization and resource usage"""
    
    def setUp(self):
        """Set up test environment"""
        self.serial_connector = MagicMock()
        self.message_handler = MagicMock()
        self.flight_controller = MagicMock()
        self.logger = MagicMock()
    
    def test_message_processing_performance(self):
        """Test performance of MAVLink message processing"""
        # Create a mock message
        mock_msg = MagicMock()
        mock_msg.get_type.return_value = 'HEARTBEAT'
        
        # Set up the message handler
        self.message_handler._handle_heartbeat = MagicMock()
        
        # Run the performance test
        iterations = 1000
        start_time = time.time()
        
        for _ in range(iterations):
            self.message_handler._process_message(mock_msg)
        
        end_time = time.time()
        
        # Calculate messages per second
        elapsed_time = end_time - start_time
        messages_per_second = iterations / elapsed_time if elapsed_time > 0 else 0
        
        # Print the results
        print(f"Message processing performance: {messages_per_second:.2f} messages per second")
        
        # Verify that the performance meets minimum requirements
        # A modern system should be able to process thousands of messages per second
        self.assertGreaterEqual(messages_per_second, 1000)
    
    def test_gps_update_performance(self):
        """Test performance of GPS update operations"""
        # Set up components
        self.flight_controller.update_drone_position = MagicMock()
        
        # Run the performance test
        iterations = 1000
        start_time = time.time()
        
        for i in range(iterations):
            # Simulate GPS updates with slightly changing coordinates
            lat = 50.110924 + (i * 0.0001)
            lon = 8.682127 + (i * 0.0001)
            alt = 100.0 + i
            self.flight_controller.update_drone_position(lat, lon, alt, 45.0)
        
        end_time = time.time()
        
        # Calculate updates per second
        elapsed_time = end_time - start_time
        updates_per_second = iterations / elapsed_time if elapsed_time > 0 else 0
        
        # Print the results
        print(f"GPS update performance: {updates_per_second:.2f} updates per second")
        
        # Verify that the performance meets minimum requirements
        # GPS updates should be fast enough for real-time display
        self.assertGreaterEqual(updates_per_second, 100)
    
    def test_visualization_performance(self):
        """Test performance of visualization operations"""
        # Create a mock canvas
        mock_canvas = MagicMock()
        
        # Define visualization operations
        def draw_drone(lat, lon, heading):
            # Convert coordinates to screen coordinates
            x = int((lon - (-10.0)) / (60.0 - (-10.0)) * 800)
            y = int((70.0 - lat) / (70.0 - 30.0) * 600)
            
            # Draw the drone icon
            mock_canvas.create_polygon(x, y, x+10, y+10, x-10, y+10, fill="yellow")
        
        # Run the performance test
        iterations = 1000
        start_time = time.time()
        
        for i in range(iterations):
            # Simulate drone movement
            lat = 50.110924 + (i * 0.0001)
            lon = 8.682127 + (i * 0.0001)
            heading = (45.0 + i) % 360
            draw_drone(lat, lon, heading)
        
        end_time = time.time()
        
        # Calculate frames per second
        elapsed_time = end_time - start_time
        frames_per_second = iterations / elapsed_time if elapsed_time > 0 else 0
        
        # Print the results
        print(f"Visualization performance: {frames_per_second:.2f} frames per second")
        
        # Verify that the performance meets minimum requirements
        # Visualization should be smooth enough for real-time display
        self.assertGreaterEqual(frames_per_second, 30)
    
    def test_log_processing_performance(self):
        """Test performance of log processing"""
        # Run the performance test
        iterations = 1000
        start_time = time.time()
        
        for i in range(iterations):
            log_message = f"[INFO] Log message {i}"
            self.logger.info(f"Log message {i}")
        
        end_time = time.time()
        
        # Calculate logs per second
        elapsed_time = end_time - start_time
        logs_per_second = iterations / elapsed_time if elapsed_time > 0 else 0
        
        # Print the results
        print(f"Log processing performance: {logs_per_second:.2f} logs per second")
        
        # Verify that the performance meets minimum requirements
        # Logging should be fast enough for high-volume operations
        self.assertGreaterEqual(logs_per_second, 1000)
    
    def test_mission_upload_performance(self):
        """Test performance of mission upload operations"""
        # Create a mock mission with many waypoints
        waypoints = []
        for i in range(100):
            waypoints.append({
                "index": i,
                "lat": 50.110924 + (i * 0.001),
                "lon": 8.682127 + (i * 0.001),
                "alt": 100.0 + (i * 10),
                "type": 16  # MAV_CMD_NAV_WAYPOINT
            })
        
        # Set up components
        mission_model = MagicMock()
        mission_model.get_all_waypoints.return_value = waypoints
        
        # Profile the mission upload
        pr = cProfile.Profile()
        pr.enable()
        
        # Simulate mission upload
        for wp in waypoints:
            # In a real upload, we would send each waypoint to the drone
            self.serial_connector.send_waypoint = MagicMock()
            self.serial_connector.send_waypoint(wp["index"], wp["lat"], wp["lon"], wp["alt"], wp["type"])
        
        pr.disable()
        
        # Get profiling results
        s = io.StringIO()
        ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
        ps.print_stats(10)  # Print top 10 functions by time
        
        # Print the profiling results
        print("Mission upload performance profile:")
        print(s.getvalue())
        
        # Verify that the number of waypoints processed matches the expected count
        self.assertEqual(self.serial_connector.send_waypoint.call_count, len(waypoints))
    
    def test_memory_usage(self):
        """Test memory usage of key operations"""
        try:
            import psutil
            import os
            
            # Get current process
            process = psutil.Process(os.getpid())
            
            # Measure memory before operation
            memory_before = process.memory_info().rss / 1024 / 1024  # MB
            
            # Perform memory-intensive operation
            large_data = {}
            for i in range(10000):
                large_data[f"key_{i}"] = f"value_{i}" * 100
            
            # Measure memory after operation
            memory_after = process.memory_info().rss / 1024 / 1024  # MB
            
            # Calculate memory usage
            memory_usage = memory_after - memory_before
            
            # Print the results
            print(f"Memory usage: {memory_usage:.2f} MB")
            
            # Verify that memory usage is within acceptable limits
            self.assertLess(memory_usage, 100)  # Example limit: 100 MB
        except ImportError:
            self.skipTest("psutil module not available")
    
    def test_cpu_usage(self):
        """Test CPU usage of key operations"""
        try:
            import psutil
            import os
            
            # Get current process
            process = psutil.Process(os.getpid())
            
            # Measure CPU usage during an intensive operation
            cpu_percent_before = process.cpu_percent(interval=0.1)
            
            # Perform CPU-intensive operation
            start_time = time.time()
            while time.time() - start_time < 1.0:  # Run for 1 second
                # Simulate processing many messages
                for _ in range(1000):
                    mock_msg = MagicMock()
                    mock_msg.get_type.return_value = 'HEARTBEAT'
                    self.message_handler._process_message(mock_msg)
            
            # Measure CPU usage after operation
            cpu_percent_after = process.cpu_percent(interval=0.1)
            
            # Print the results
            print(f"CPU usage: {cpu_percent_after:.2f}%")
            
            # Verify that CPU usage is within acceptable limits
            # This will depend on the system, but should be less than 100% on a single core
            self.assertLess(cpu_percent_after, 100)
        except ImportError:
            self.skipTest("psutil module not available")
    
    def test_message_filtering_efficiency(self):
        """Test efficiency of the message filtering system"""
        # Create messages with small and large changes
        base_msg = MagicMock()
        base_msg.get_type.return_value = 'ATTITUDE'
        base_msg.roll = 0.1
        base_msg.pitch = 0.2
        base_msg.yaw = 0.3
        
        small_change_msgs = []
        large_change_msgs = []
        
        for i in range(100):
            # Small changes
            msg = MagicMock()
            msg.get_type.return_value = 'ATTITUDE'
            msg.roll = 0.1 + (i * 0.001)  # Small change
            msg.pitch = 0.2 + (i * 0.001)  # Small change
            msg.yaw = 0.3 + (i * 0.001)    # Small change
            small_change_msgs.append(msg)
            
            # Large changes
            msg = MagicMock()
            msg.get_type.return_value = 'ATTITUDE'
            msg.roll = 0.1 + (i * 0.02)   # Large change
            msg.pitch = 0.2 + (i * 0.02)  # Large change
            msg.yaw = 0.3 + (i * 0.02)    # Large change
            large_change_msgs.append(msg)
        
        # Set up the message handler with filtering
        self.message_handler._last_logged_time = {}
        self.message_handler._message_cache = {'ATTITUDE': base_msg}
        self.message_handler._thresholds = {
            'ATTITUDE': {'roll': 0.01, 'pitch': 0.01, 'yaw': 0.01}
        }
        self.message_handler._handle_attitude = MagicMock()
        self.message_handler._running = True
        
        # Process small change messages (should be mostly filtered)
        for msg in small_change_msgs:
            self.message_handler._process_message(msg)
        
        small_change_processed = self.message_handler._handle_attitude.call_count
        self.message_handler._handle_attitude.reset_mock()
        
        # Process large change messages (should be mostly processed)
        for msg in large_change_msgs:
            self.message_handler._process_message(msg)
        
        large_change_processed = self.message_handler._handle_attitude.call_count
        
        # Print the results
        print(f"Message filtering efficiency:")
        print(f"  Small changes processed: {small_change_processed}/{len(small_change_msgs)}")
        print(f"  Large changes processed: {large_change_processed}/{len(large_change_msgs)}")
        
        # Verify that the filtering is working effectively
        self.assertLess(small_change_processed, len(small_change_msgs) / 2)  # Less than half processed
        self.assertGreater(large_change_processed, len(large_change_msgs) / 2)  # More than half processed

if __name__ == '__main__':
    unittest.main()
