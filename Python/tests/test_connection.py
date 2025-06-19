import pytest
from unittest.mock import MagicMock, patch
from backend.mavlink_connector import MAVLinkConnector
from backend.exceptions import ConnectionTimeoutError, ConnectionError
from backend.logger import Logger

class TestMAVLinkConnector:
    @pytest.fixture
    def mock_logger(self):
        return MagicMock(spec=Logger)
        
    @pytest.fixture
    def connector(self, mock_logger):
        connector = MAVLinkConnector(mock_logger)
        return connector

    def test_connection_timeout(self, connector):
        """Test that connection times out when port is invalid"""
        connector.set_connection_params("COM99", 57600)
        with patch('serial.Serial', side_effect=ConnectionTimeoutError("Connection timeout")):
            with pytest.raises(ConnectionTimeoutError):
                connector.connect()

    def test_connection_invalid_port(self, connector):
        """Test that connection fails with invalid port"""
        connector.set_connection_params("INVALID_PORT", 57600)
        with patch('serial.Serial', side_effect=ConnectionError("Invalid port")):
            with pytest.raises(ConnectionError):
                connector.connect()

    def test_reconnection(self, connector):
        """Test reconnection logic"""
        # Mock Serial
        with patch('serial.Serial') as mock_serial:
            mock_instance = mock_serial.return_value
            mock_instance.is_open = True
            mock_instance.read.return_value = b''
            mock_instance.inWaiting.return_value = 0

            # First connection
            connector.set_connection_params("COM1", 57600)
            connector.connect()
            assert connector.is_connected() == True
            
            # Disconnect
            connector.disconnect()
            assert connector.is_connected() == False
            
            # Reconnect
            connector.connect()
            assert connector.is_connected() == True

    def test_connection_parameters(self, connector):
        """Test connection with different parameters"""
        with patch('serial.Serial') as mock_serial:
            mock_instance = mock_serial.return_value
            mock_instance.is_open = True
            
            # Test with default baudrate
            connector.set_connection_params("COM1", 57600)
            connector.connect()
            assert connector._baudrate == 57600
            
            # Test with custom baudrate
            connector.disconnect()
            connector.set_connection_params("COM1", 115200)
            connector.connect()
            assert connector._baudrate == 115200

    def test_connection_state(self, connector):
        """Test connection state management"""
        with patch('serial.Serial') as mock_serial:
            mock_instance = mock_serial.return_value
            mock_instance.is_open = True
            mock_instance.read.return_value = b''
            mock_instance.inWaiting.return_value = 0
            
            assert connector.is_connected() == False
            
            connector.set_connection_params("COM1", 57600)
            connector.connect()
            assert connector.is_connected() == True
            
            connector.disconnect()
            assert connector.is_connected() == False

    def test_connection_events(self, connector):
        """Test connection event handling"""
        with patch('serial.Serial') as mock_serial:
            mock_instance = mock_serial.return_value
            mock_instance.is_open = True
            mock_instance.read.return_value = b''
            mock_instance.inWaiting.return_value = 0

            connected_events = []
            disconnected_events = []
            
            def on_connected():
                connected_events.append(True)
                
            def on_disconnected():
                disconnected_events.append(True)
            
            # Verbindung mit Signal-Slots aufsetzen
            connector.connected.connect(on_connected)
            connector.disconnected.connect(on_disconnected)
            
            # Connect and check events
            connector.set_connection_params("COM1", 57600)
            connector.connect()
            assert len(connected_events) >= 1
            
            # Disconnect and check events
            connector.disconnect()
            assert len(disconnected_events) >= 1