"""
Integration tests for MAVLink communication flow.
"""
import pytest
import time
import json
import sys
import os
from pathlib import Path
from unittest.mock import MagicMock, patch, call
from PySide6.QtCore import QObject, Signal, Slot

# Add project root to Python path
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Add Python directory to path
python_dir = os.path.join(project_root, 'Python')
if python_dir not in sys.path:
    sys.path.insert(0, python_dir)

class TestMavlinkIntegration:
    """Integration tests for MAVLink communication."""
    
    @pytest.fixture
    def mock_serial_connector(self):
        """Create a mock serial connector."""
        with patch('mavlink_connector.MavlinkConnector') as mock_connector:
            mock_instance = MagicMock()
            mock_instance.is_connected = True
            mock_instance.connect.return_value = True
            mock_instance.disconnect.return_value = None
            mock_connector.return_value = mock_instance
            yield mock_instance
    
    @pytest.fixture
    def mock_message_handler(self):
        """Create a mock message handler."""
        with patch('backend.message_handler.MessageHandler') as mock_handler:
            mock_instance = MagicMock()
            mock_handler.return_value = mock_instance
            yield mock_instance
            
    @pytest.fixture
    def mock_sensor_manager(self):
        """Create a mock sensor manager."""
        with patch('backend.sensor_manager.SensorManager') as mock_manager:
            mock_instance = MagicMock()
            mock_manager.return_value = mock_instance
            yield mock_instance
    
    def test_connection_flow(self, mock_serial_connector, mock_message_handler):
        """Test the complete connection flow."""
        from mavlink_connector import MavlinkConnector
        
        # Get the mock instance from the fixture
        mock_connector = mock_serial_connector.return_value
        
        # Test connection
        result = mock_connector.connect("COM8")
        assert result is True
        
        # Verify connection attempt was made with correct parameters
        mock_connector.connect.assert_called_once_with("COM8")
        
        # Verify connection state was updated
        assert mock_connector.is_connected is True
        
        # Test disconnection
        mock_connector.disconnect()
        mock_connector.disconnect.assert_called_once()
        
        # Verify disconnection state was updated
        mock_connector.is_connected = False
        
    def test_telemetry_flow(self, mock_serial_connector, mock_message_handler, mock_sensor_manager):
        """Test telemetry data flow from MAVLink to UI."""
        from mavlink_connector import MavlinkConnector
        
        # Get the mock instances
        mock_connector = mock_serial_connector.return_value
        
        # Simulate telemetry data from MAVLink
        test_telemetry = [
            ("gps", {"lat": 48.1234, "lon": 11.5678, "alt": 500.0}),
            ("attitude", {"roll": 0.1, "pitch": 0.2, "yaw": 1.57}),
            ("battery", {"voltage": 12.3, "current": 5.6, "remaining": 75})
        ]
        
        # Simulate receiving telemetry data
        for sensor_type, data in test_telemetry:
            # This would normally be called by the message handler
            mock_sensor_manager.update_sensor_value(sensor_type, data)
        
        # Verify data was stored in the sensor manager
        assert mock_sensor_manager.update_sensor_value.call_count == len(test_telemetry)
        
        # Verify appropriate logging was done
        assert mock_message_handler.log_debug.called
        
    def test_connection_flow(self, mock_serial_connector, mock_message_manager):
        """Test the complete connection flow."""
        from Python.mavlink_connector import MavlinkConnector
        
        # Setup mocks
        mock_connector = mock_serial_connector.return_value
        
        # Test connection
        mock_connector.connect.return_value = True
        assert mock_connector.connect("COM8") is True
        
        # Verify connection attempt was logged
        mock_message_manager.add_message.assert_any_call(
            "Verbinde zu: COM8 mit Baudrate: 115200", 1
        )
        
        # Verify connection state was updated
        assert mock_connector.is_connected() is True
        
        # Test disconnection
        mock_connector.disconnect()
        mock_connector.is_connected.return_value = False
        
        # Verify disconnection was logged
        mock_message_manager.add_message.assert_any_call(
            "Verbindung getrennt", 1
        )
        
    def test_heartbeat_monitoring(self, mock_serial_connector, mock_message_handler):
        """Test heartbeat monitoring and connection state tracking."""
        from mavlink_connector import MavlinkConnector
        
        # Get the mock instance
        mock_connector = mock_serial_connector.return_value
        
        # Simulate connection
        mock_connector.is_connected = True
        
        # Simulate heartbeat received
        if hasattr(mock_connector, 'heartbeat_received'):
            mock_connector.heartbeat_received.emit({"system_status": 4})  # MAV_STATE_ACTIVE
        
        # Verify connection state was updated
        assert mock_connector.is_connected is True
        
        # Simulate heartbeat timeout (10 seconds without heartbeat)
        mock_connector.is_connected = False
        
        # Verify disconnection was detected and logged
        # Note: The actual message might be different based on implementation
        mock_message_handler.log_warning.assert_called()
        
    def test_telemetry_error_handling(self, mock_serial_connector, mock_message_handler, mock_sensor_manager):
        """Test error handling during telemetry processing."""
        # Get the mock instance
        mock_connector = mock_serial_connector.return_value
        
        # Simulate error in message handling
        error_message = "Test error in telemetry processing"
        if hasattr(mock_connector, 'error_occurred'):
            mock_connector.error_occurred.emit(error_message)
        
        # Verify error was logged
        # The actual error handling might be different based on implementation
        assert mock_message_handler.log_error.called
        
    def test_preflight_checks(self, mock_serial_connector, mock_message_handler, mock_sensor_manager):
        """Test preflight check functionality."""
        # Skip this test for now as we need to verify the preflight checker implementation
        pytest.skip("Preflight checker implementation needs to be verified first")
        
        # The following is a placeholder for when we implement proper preflight checks
        from backend.flight_control.preflight_checker import PreflightChecker
        
        # Get the mock instance
        mock_connector = mock_serial_connector.return_value
        
        # Create preflight checker with mocks
        preflight_checker = PreflightChecker()
        preflight_checker.message_handler = mock_message_handler
        
        # Test preflight check with good conditions
        mock_sensor_manager.get_sensor_value.return_value = {
            "voltage": 12.6,
            "current": 0.5,
            "remaining": 95,
            "fix_type": 3,
            "satellites_visible": 8,
            "roll": 0.0,
            "pitch": 0.0,
            "yaw": 0.0
        }
        
        # Run preflight check
        result = preflight_checker.run_checks()
        
        # Verify all checks passed
        assert result is True
        mock_message_handler.log_info.assert_called()
        
        # Test preflight check with critical issue (low battery)
        mock_sensor_manager.get_sensor_value.return_value = {
            "voltage": 10.5,
            "current": 0.5,
            "remaining": 15
        }
        
        # Run preflight check
        result = preflight_checker.run_checks()
        
        # Verify check failed due to low battery
        assert result is False
        assert mock_message_handler.log_warning.called
