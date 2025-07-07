"""
Unit tests for the MavlinkSerialConnector class.
"""
import pytest
from unittest.mock import MagicMock, patch

class TestMavlinkSerialConnector:
    """Test cases for MavlinkSerialConnector."""
    
    @pytest.fixture
    def mock_serial(self):
        """Mock the serial port."""
        with patch('serial.Serial') as mock_serial:
            yield mock_serial
    
    @pytest.fixture
    def mock_mavutil(self):
        """Mock the pymavlink mavutil."""
        with patch('pymavlink.mavutil') as mock_mavutil:
            yield mock_mavutil
    
    def test_initialization(self, mock_serial, mock_mavutil):
        """Test that the connector initializes correctly."""
        from Python.mavlink_connector import MavlinkSerialConnector
        
        # Create a test instance
        connector = MavlinkSerialConnector()
        
        # Verify initialization
        assert connector.is_connected() is False
        assert connector.port is None
        assert connector.baudrate == 115200
        
    def test_connect_success(self, mock_serial, mock_mavutil):
        """Test successful connection to a serial port."""
        from Python.mavlink_connector import MavlinkSerialConnector
        
        # Setup mocks
        mock_connection = MagicMock()
        mock_mavutil.mavlink_connection.return_value = mock_connection
        
        # Create and test connection
        connector = MavlinkSerialConnector()
        result = connector.connect("COM8")
        
        # Verify connection
        assert result is True
        assert connector.is_connected() is True
        mock_mavutil.mavlink_connection.assert_called_once_with(
            'COM8', baud=115200, source_system=255, source_component=0, 
            autoreconnect=True, retries=3, use_native=True
        )
        
    def test_disconnect(self, mock_serial, mock_mavutil):
        """Test disconnecting from the serial port."""
        from Python.mavlink_connector import MavlinkSerialConnector
        
        # Setup mocks and connect first
        mock_connection = MagicMock()
        mock_mavutil.mavlink_connection.return_value = mock_connection
        
        connector = MavlinkSerialConnector()
        connector.connect("COM8")
        
        # Test disconnect
        connector.disconnect()
        
        # Verify disconnection
        assert connector.is_connected() is False
        mock_connection.close.assert_called_once()
