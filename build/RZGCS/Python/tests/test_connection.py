import pytest
from backend.mavlink_connector import MavlinkConnector
from backend.exceptions import ConnectionTimeoutError, ConnectionError

class TestMavlinkConnector:
    @pytest.fixture
    def connector(self):
        return MavlinkConnector()

    def test_connection_timeout(self, connector):
        """Test that connection times out when port is invalid"""
        with pytest.raises(ConnectionTimeoutError):
            connector.connect("COM99", timeout=1)

    def test_connection_invalid_port(self, connector):
        """Test that connection fails with invalid port"""
        with pytest.raises(ConnectionError):
            connector.connect("INVALID_PORT")

    def test_reconnection(self, connector):
        """Test reconnection logic"""
        # First connection
        connector.connect("COM1", timeout=1)
        assert connector.is_connected() == True
        
        # Disconnect
        connector.disconnect()
        assert connector.is_connected() == False
        
        # Reconnect
        connector.connect("COM1", timeout=1)
        assert connector.is_connected() == True

    def test_connection_parameters(self, connector):
        """Test connection with different parameters"""
        # Test with default baudrate
        connector.connect("COM1", timeout=1)
        assert connector.baudrate == 57600
        
        # Test with custom baudrate
        connector.disconnect()
        connector.connect("COM1", baudrate=115200, timeout=1)
        assert connector.baudrate == 115200

    def test_connection_state(self, connector):
        """Test connection state management"""
        assert connector.is_connected() == False
        
        connector.connect("COM1", timeout=1)
        assert connector.is_connected() == True
        
        connector.disconnect()
        assert connector.is_connected() == False

    def test_connection_events(self, connector):
        """Test connection event handling"""
        connected_events = []
        disconnected_events = []
        
        def on_connected():
            connected_events.append(True)
            
        def on_disconnected():
            disconnected_events.append(True)
        
        connector.connected.connect(on_connected)
        connector.disconnected.connect(on_disconnected)
        
        # Connect and check events
        connector.connect("COM1", timeout=1)
        assert len(connected_events) == 1
        
        # Disconnect and check events
        connector.disconnect()
        assert len(disconnected_events) == 1 