"""
Unit-Tests für den MAVLink-Simulator.
"""
import pytest
import sys
import os
import time
from unittest.mock import MagicMock, patch

# Korrekte Pfadangaben für Import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Module importieren
from backend.mavlink_simulator import MAVLinkSimulator
from backend.message_handler import MessageHandler

class TestMAVLinkSimulator:
    """Test-Suite für die MAVLinkSimulator-Klasse."""
    
    @pytest.fixture
    def mock_message_handler(self):
        """Fixture für einen Mock MessageHandler."""
        handler = MagicMock(spec=MessageHandler)
        return handler
    
    @pytest.fixture
    def simulator(self, mock_message_handler):
        """Fixture für einen MAVLinkSimulator mit Mock-Handler."""
        return MAVLinkSimulator(mock_message_handler)
    
    def test_initialization(self, simulator, mock_message_handler):
        """Testet die korrekte Initialisierung des Simulators."""
        assert simulator._message_handler == mock_message_handler
        assert simulator._is_running is False
        assert simulator._thread is None
    
    def test_start_simulator(self, simulator):
        """Testet den Start des Simulators."""
        # Mock den Thread und die run-Methode
        with patch('backend.mavlink_simulator.Thread') as mock_thread:
            mock_thread_instance = MagicMock()
            mock_thread.return_value = mock_thread_instance
            
            # Act
            simulator.start()
            
            # Assert
            assert simulator._is_running is True
            assert simulator._thread is mock_thread_instance
            mock_thread.assert_called_once()
            mock_thread_instance.start.assert_called_once()
    
    def test_stop_simulator(self, simulator):
        """Testet das Stoppen des Simulators."""
        # Arrange
        simulator._is_running = True
        simulator._thread = MagicMock()
        
        # Act
        simulator.stop()
        
        # Assert
        assert simulator._is_running is False
    
    def test_is_running(self, simulator):
        """Testet die is_running-Methode."""
        # Arrange
        simulator._is_running = True
        
        # Act & Assert
        assert simulator.is_running() is True
        
        # Arrange
        simulator._is_running = False
        
        # Act & Assert
        assert simulator.is_running() is False
    
    @patch('time.sleep')
    def test_run_loop(self, mock_sleep, simulator, mock_message_handler):
        """Testet die run-Schleife des Simulators."""
        # Arrange - Setup für einen kurzen Lauf des Simulators
        simulator._is_running = True
        
        def stop_after_calls(*args, **kwargs):
            simulator._is_running = False
            return MagicMock()
        
        # Mock das Verhalten der simulate_*-Methoden
        with patch.object(simulator, 'simulate_heartbeat', side_effect=stop_after_calls) as mock_heartbeat:
            with patch.object(simulator, 'simulate_attitude') as mock_attitude:
                with patch.object(simulator, 'simulate_gps_status') as mock_gps:
                    with patch.object(simulator, 'simulate_battery_status') as mock_battery:
                        # Act
                        simulator.run()
                        
                        # Assert
                        mock_heartbeat.assert_called_once()
                        # Andere Methoden werden nicht aufgerufen, da wir nach heartbeat stoppen
                        mock_attitude.assert_not_called()
                        mock_gps.assert_not_called()
                        mock_battery.assert_not_called()
    
    def test_simulate_heartbeat(self, simulator, mock_message_handler):
        """Testet die Heartbeat-Simulation."""
        # Act
        simulator.simulate_heartbeat()
        
        # Assert
        mock_message_handler.process_heartbeat.assert_called_once()
        args, kwargs = mock_message_handler.process_heartbeat.call_args
        assert len(args) == 1  # Ein Argument (status)
        assert isinstance(args[0], int)  # Status sollte ein Integer sein
    
    def test_simulate_attitude(self, simulator, mock_message_handler):
        """Testet die Attitude-Simulation."""
        # Act
        simulator.simulate_attitude()
        
        # Assert
        mock_message_handler.process_attitude.assert_called_once()
        args, kwargs = mock_message_handler.process_attitude.call_args
        assert len(args) == 3  # Drei Argumente (roll, pitch, yaw)
        for value in args:
            assert isinstance(value, float)  # Werte sollten Floats sein
    
    def test_simulate_gps_status(self, simulator, mock_message_handler):
        """Testet die GPS-Status-Simulation."""
        # Act
        simulator.simulate_gps_status()
        
        # Assert
        mock_message_handler.process_gps.assert_called_once()
        # Überprüfen der GPS-Parameter
        args, kwargs = mock_message_handler.process_gps.call_args
        assert len(args) >= 3  # Mindestens lat, lon, alt
        # Der erste Parameter sollte der GPS-Fix-Typ sein
        assert isinstance(args[0], int)
    
    def test_simulate_battery_status(self, simulator, mock_message_handler):
        """Testet die Batteriestatus-Simulation."""
        # Act
        simulator.simulate_battery_status()
        
        # Assert
        mock_message_handler.process_battery.assert_called_once()
        args, kwargs = mock_message_handler.process_battery.call_args
        assert len(args) >= 1  # Mindestens ein Argument (Ladezustand)
        assert 0 <= args[0] <= 100  # Ladezustand sollte zwischen 0 und 100% liegen
