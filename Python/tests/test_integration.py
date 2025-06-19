"""
Integrationstests für die RZ Ground Control Station.
Diese Tests überprüfen das Zusammenspiel mehrerer Komponenten.
"""
import pytest
import sys
import os
import time
from unittest.mock import MagicMock, patch

# Korrekte Pfadangaben für Import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Module importieren
from backend.mavlink_connector import MAVLinkConnector
from backend.message_handler import MessageHandler
from backend.mavlink_simulator import MAVLinkSimulator

class TestIntegration:
    """Integrationstests für die RZ Ground Control Station."""
    
    @pytest.fixture
    def message_handler(self):
        """Fixture für einen echten MessageHandler."""
        return MessageHandler()
    
    @pytest.fixture
    def mock_connector(self):
        """Fixture für einen Mock-Connector."""
        connector = MagicMock(spec=MAVLinkConnector)
        connector.is_connected.return_value = True
        return connector
    
    def test_message_handler_with_simulator(self, message_handler):
        """Testet die Integration von MessageHandler und Simulator."""
        # Arrange
        simulator = MAVLinkSimulator(message_handler)
        
        # Spione auf die Signale des MessageHandlers
        with patch.object(message_handler, 'heartbeat_received') as mock_heartbeat:
            with patch.object(message_handler, 'attitude_updated') as mock_attitude:
                with patch.object(message_handler, 'gps_updated') as mock_gps:
                    with patch.object(message_handler, 'battery_updated') as mock_battery:
                        # Act - Simuliere verschiedene Nachrichten
                        simulator.simulate_heartbeat()
                        simulator.simulate_attitude()
                        simulator.simulate_gps_status()
                        simulator.simulate_battery_status()
                        
                        # Assert - Überprüfe, ob die entsprechenden Signale emittiert wurden
                        mock_heartbeat.emit.assert_called_once()
                        mock_attitude.emit.assert_called_once()
                        mock_gps.emit.assert_called_once()
                        mock_battery.emit.assert_called_once()
    
    def test_simulator_thread_operation(self, message_handler):
        """Testet die Thread-Operation des Simulators."""
        # Arrange
        simulator = MAVLinkSimulator(message_handler)
        
        # Act
        simulator.start()
        assert simulator.is_running()
        
        # Warte kurz, damit der Thread Zeit hat, zu starten und zu laufen
        time.sleep(0.5)
        
        # Stoppe den Simulator
        simulator.stop()
        
        # Assert
        assert not simulator.is_running()
    
    def test_connector_with_message_handler(self, mock_connector, message_handler):
        """Testet die Integration von Connector und MessageHandler."""
        # Arrange
        message_handler.set_connector(mock_connector)
        
        # Act - Eine Nachricht vom Connector empfangen simulieren
        # Erstellen einer simulierten MAVLink-Nachricht
        mock_message = MagicMock()
        mock_message.get_type.return_value = "HEARTBEAT"
        mock_message.custom_mode = 0
        mock_message.system_status = 3  # MAV_STATE_STANDBY
        
        # Simulieren des Empfangs
        message_handler.process_mavlink_message(mock_message)
        
        # Assert - Überprüfen, ob der MessageHandler die Nachricht korrekt verarbeitet hat
        assert message_handler._system_status == 3
    
    def test_sensor_data_flow(self, message_handler):
        """Testet den Fluss von Sensordaten durch das System."""
        # Arrange
        # Wir registrieren eine Mock-Callback-Funktion für ein Signal
        attitude_callback = MagicMock()
        message_handler.attitude_updated.connect(attitude_callback)
        
        # Act
        # Simulieren der Verarbeitung von Attitude-Daten
        message_handler.process_attitude(0.5, -0.3, 0.1)
        
        # Assert
        # Überprüfen, ob die Callback-Funktion mit den richtigen Parametern aufgerufen wurde
        attitude_callback.assert_called_once_with(0.5, -0.3, 0.1)
        
        # Überprüfen, ob die internen Zustandsdaten aktualisiert wurden
        assert message_handler._roll == 0.5
        assert message_handler._pitch == -0.3
        assert message_handler._yaw == 0.1
    
    def test_end_to_end_command_flow(self, mock_connector, message_handler):
        """Testet den End-to-End-Fluss von Befehlen durch das System."""
        # Arrange
        message_handler.set_connector(mock_connector)
        
        # Act - Einen Befehl senden
        message_handler.send_arm_command(True)  # Arm-Befehl senden
        
        # Assert - Überprüfen, ob der Connector verwendet wurde, um den Befehl zu senden
        mock_connector.send_mavlink_message.assert_called_once()
        
        # Überprüfen, ob der richtige Befehlstyp gesendet wurde
        args, kwargs = mock_connector.send_mavlink_message.call_args
        message = args[0]
        assert "COMMAND_LONG" in str(message) or "command_long" in str(message).lower()
