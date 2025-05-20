"""
Unit-Tests für den MAVLink-Connector.
"""
import pytest
import time
import sys
import os
from unittest.mock import MagicMock, patch

# Korrekte Pfadangaben für Import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Module importieren
from backend.mavlink_connector import MAVLinkConnector, ConnectorType, create_connector
from backend.logger import Logger
from backend.exceptions import ConnectionError

class TestMAVLinkConnector:
    """Test-Suite für die MAVLinkConnector-Klasse."""
    
    @pytest.fixture
    def mock_logger(self):
        """Mockt den Logger für Tests."""
        logger = MagicMock(spec=Logger)
        return logger
        
    @pytest.fixture
    def mock_serial(self):
        """Mockt das Serial-Modul für Tests."""
        with patch('backend.mavlink_connector.serial.Serial') as mock_serial:
            instance = mock_serial.return_value
            instance.is_open = True
            instance.read.return_value = b''
            instance.inWaiting.return_value = 0
            yield instance
    
    def test_connector_initialization(self, mock_serial, mock_logger):
        """Testet die korrekte Initialisierung des MAVLink-Connectors."""
        # Arranges
        port = 'COM1'
        baudrate = 57600
        
        # Act
        connector = MAVLinkConnector(mock_logger)
        connector.set_connection_params(port, baudrate)
        
        # Assert
        assert connector is not None
        assert connector._port == port
        assert connector._baudrate == baudrate
        assert connector._connection is None
    
    def test_connect_success(self, mock_serial, mock_logger):
        """Testet die erfolgreiche Verbindungsherstellung."""
        # Arrange
        connector = MAVLinkConnector(mock_logger)
        connector.set_connection_params('COM1', 57600)
        
        # Act
        result = connector.connect()
        
        # Assert
        assert result is True
        assert connector.is_connected() is True
    
    @patch('backend.mavlink_connector.serial.Serial', side_effect=Exception('Connection failed'))
    def test_connect_failure(self, mock_serial_error, mock_logger):
        """Testet den Fehlerfall bei der Verbindungsherstellung."""
        # Arrange
        connector = MAVLinkConnector(mock_logger)
        connector.set_connection_params('COM1', 57600)
        
        # Act & Assert
        with pytest.raises(ConnectionError):
            connector.connect()
        
        assert connector.is_connected() is False
    
    def test_disconnect(self, mock_serial, mock_logger):
        """Testet das korrekte Trennen der Verbindung."""
        # Arrange
        connector = MAVLinkConnector(mock_logger)
        connector.set_connection_params('COM1', 57600)
        connector.connect()
        
        # Act
        connector.disconnect()
        
        # Assert
        assert connector.is_connected() is False
        assert connector._connection is None
    
    def test_factory_method_mavlink(self):
        """Testet die Factory-Methode für die Erstellung eines MAVLink-Connectors."""
        # Arrange & Act
        with patch('backend.mavlink_connector.MAVLinkConnector') as mock_connector:
            with patch('backend.mavlink_connector.Logger') as mock_logger_class:
                mock_logger_instance = MagicMock()
                mock_logger_class.return_value = mock_logger_instance
            
                mock_instance = MagicMock()
                mock_connector.return_value = mock_instance
                
                # Act
                connector = create_connector(ConnectorType.PYMAVLINK, port='COM1', baudrate=57600)
                
                # Assert
                assert connector is mock_instance
                mock_connector.assert_called_once()
                # Überprüfen, ob set_connection_params korrekt aufgerufen wurde
                mock_instance.set_connection_params.assert_called_once_with('COM1', 57600)
    
    def test_factory_method_missing_params(self):
        """Testet die Factory-Methode mit fehlenden Parametern."""
        # Arrange & Act & Assert
        with pytest.raises(ValueError):
            create_connector(ConnectorType.PYMAVLINK)
    
    def test_send_message(self, mock_serial, mock_logger):
        """Testet das Senden einer Nachricht."""
        # Arrange
        connector = MAVLinkConnector(mock_logger)
        connector.set_connection_params('COM1', 57600)
        connector.connect()
        
        mock_mavlink = MagicMock()
        connector._mavlink = mock_mavlink
        
        # Act
        test_message = "TEST_MESSAGE"
        connector.send_message(test_message)
        
        # Assert
        mock_mavlink.mav.send.assert_called_once_with(test_message)
    
    def test_send_message_not_connected(self, mock_logger):
        """Testet das Senden einer Nachricht ohne Verbindung."""
        # Arrange
        connector = MAVLinkConnector(mock_logger)
        connector.set_connection_params('COM1', 57600)
        
        # Act & Assert
        with pytest.raises(ConnectionError):
            connector.send_message("TEST_MESSAGE")
            
    @patch('backend.mavlink_connector.MAVLinkConnector.process_messages')
    def test_receive_messages(self, mock_process, mock_serial, mock_logger):
        """Testet den Empfang von Nachrichten."""
        # Arrange
        connector = MAVLinkConnector(mock_logger)
        connector.set_connection_params('COM1', 57600)
        connector.connect()
        
        # Simuliere eingehende Daten
        mock_serial.inWaiting.return_value = 10
        mock_serial.read.return_value = b'TestData'
        
        # Act
        connector.receive_messages()
        
        # Assert
        mock_process.assert_called_once_with(b'TestData')
