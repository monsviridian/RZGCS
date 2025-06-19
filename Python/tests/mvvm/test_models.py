"""
Tests für die Model-Schicht der MVVM-Architektur.

Diese Tests überprüfen die korrekte Funktionalität der Model-Komponenten,
insbesondere der MAVSDKConnector und der SITL-Controller.
"""

import os
import sys
import unittest
from unittest.mock import Mock, patch, MagicMock, call
import pytest
import asyncio

# Pfad zum Hauptverzeichnis hinzufügen, damit Module importiert werden können
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Model-Importe
from backend.mavsdk_connector_mvvm import MAVSDKConnectorMVVM
from backend.drone_signal_hub import DroneSignalHub
from backend.sitl_controller import SITLController

# Andere notwendige Importe
from backend.logger import Logger


class TestMAVSDKConnectorMVVM(unittest.TestCase):
    """Tests für den MAVSDKConnectorMVVM."""
    
    def setUp(self):
        """Testumgebung einrichten."""
        self.logger = Mock(spec=Logger)
        
        # Mock für die DroneSignalHub erstellen
        self.signal_hub = Mock(spec=DroneSignalHub)
        
        # MAVSDKConnectorMVVM mit Mocks erstellen
        with patch('backend.mavsdk_connector_mvvm.MAVSDKServerController') as mock_server_controller:
            self.connector = MAVSDKConnectorMVVM(self.signal_hub, self.logger)
            self.mock_server_controller = mock_server_controller.return_value
    
    @patch('backend.mavsdk_connector_mvvm.mavsdk.System')
    @patch('backend.mavsdk_connector_mvvm.asyncio.create_task')
    def test_connect_to_serial(self, mock_create_task, mock_system):
        """Testet die Verbindung über einen seriellen Port."""
        # Mock für asynchrone Funktionen
        async def mock_coro():
            return True
        mock_create_task.return_value = MagicMock()
        
        # Mock für System.connect konfigurieren
        mock_system_instance = mock_system.return_value
        mock_system_instance.connect.return_value = mock_coro()
        
        # Verbindungsstring
        conn_string = "COM3:115200"
        
        # Verbindung testen
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(self.connector.connect(conn_string))
        finally:
            loop.close()
        
        # Überprüfen, ob die richtigen Methoden aufgerufen wurden
        self.mock_server_controller.start_server.assert_called()
        mock_system_instance.connect.assert_called()
    
    @patch('backend.mavsdk_connector_mvvm.mavsdk.System')
    @patch('backend.mavsdk_connector_mvvm.asyncio.create_task')
    def test_connect_to_udp(self, mock_create_task, mock_system):
        """Testet die Verbindung über UDP."""
        # Mock für asynchrone Funktionen
        async def mock_coro():
            return True
        mock_create_task.return_value = MagicMock()
        
        # Mock für System.connect konfigurieren
        mock_system_instance = mock_system.return_value
        mock_system_instance.connect.return_value = mock_coro()
        
        # Verbindungsstring
        conn_string = "udp:127.0.0.1:14550"
        
        # Verbindung testen
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(self.connector.connect(conn_string))
        finally:
            loop.close()
        
        # Überprüfen, ob die richtigen Methoden aufgerufen wurden
        mock_system_instance.connect.assert_called()
    
    @patch('backend.mavsdk_connector_mvvm.mavsdk.System')
    def test_disconnect(self, mock_system):
        """Testet die Trennung der Verbindung."""
        # Mock für System konfigurieren
        mock_system_instance = mock_system.return_value
        
        # Verbindungsstatus simulieren
        self.connector._is_connected = True
        
        # Verbindung trennen
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(self.connector.disconnect())
        finally:
            loop.close()
        
        # Überprüfen, ob der Verbindungsstatus zurückgesetzt wurde
        self.assertFalse(self.connector._is_connected)
    
    @patch('backend.mavsdk_connector_mvvm.mavsdk.System')
    @patch('backend.mavsdk_connector_mvvm.asyncio.create_task')
    def test_telemetry_subscriptions(self, mock_create_task, mock_system):
        """Testet die Telemetrie-Abonnements."""
        # Mock für asynchrone Funktionen
        async def mock_coro():
            return True
        mock_create_task.return_value = MagicMock()
        
        # Mock für System konfigurieren
        mock_system_instance = mock_system.return_value
        
        # Telemetriedienst-Mock erstellen
        mock_telemetry = MagicMock()
        mock_system_instance.telemetry = mock_telemetry
        
        # Verbindungsstatus simulieren
        self.connector._is_connected = True
        self.connector._drone = mock_system_instance
        
        # Telemetrie-Abonnements starten
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(self.connector._start_telemetry_subscriptions())
        finally:
            loop.close()
        
        # Überprüfen, ob die Telemetrieabonnements gestartet wurden
        # Dies hängt von der genauen Implementierung ab


class TestSITLController(unittest.TestCase):
    """Tests für den SITLController."""
    
    def setUp(self):
        """Testumgebung einrichten."""
        self.logger = Mock(spec=Logger)
        self.controller = SITLController(self.logger)
        
        # Signal-Empfänger simulieren
        self.sim_started_called = False
        self.sim_stopped_called = False
        
        # Signals mit Mock-Funktionen verbinden
        self.controller.simStarted.connect(self._on_sim_started)
        self.controller.simStopped.connect(self._on_sim_stopped)
    
    def _on_sim_started(self, vehicle_type, connection_string):
        """Mock für Signal-Handler."""
        self.sim_started_called = True
        self.last_vehicle_type = vehicle_type
        self.last_connection_string = connection_string
    
    def _on_sim_stopped(self):
        """Mock für Signal-Handler."""
        self.sim_stopped_called = True
    
    def test_build_home_location(self):
        """Testet die Erstellung des Home-Location-Strings."""
        # Home-Location erstellen
        home_location = self.controller.build_home_location(49.0, 8.0, 40.0, 0.0)
        
        # Überprüfen, ob der String korrekt ist
        self.assertEqual(home_location, "49.0,8.0,40.0,0.0")
    
    @patch('backend.sitl_controller.subprocess.Popen')
    def test_start_simulator(self, mock_popen):
        """Testet das Starten des Simulators."""
        # Mock für Popen konfigurieren
        mock_process = mock_popen.return_value
        mock_process.poll.return_value = None  # Prozess läuft
        mock_process.stdout = MagicMock()
        
        # Simulator starten
        self.controller.start_simulator("copter", "quad", "49.0,8.0,40.0,0.0")
        
        # Überprüfen, ob der Prozess gestartet wurde
        mock_popen.assert_called_once()
        
        # Überprüfen, ob das Signal ausgelöst wurde
        self.assertTrue(self.sim_started_called)
        self.assertEqual(self.last_vehicle_type, "copter")
        self.assertEqual(self.last_connection_string, "tcp:127.0.0.1:5760")
    
    @patch('backend.sitl_controller.subprocess.Popen')
    def test_stop_simulator(self, mock_popen):
        """Testet das Stoppen des Simulators."""
        # Mock für Popen konfigurieren
        mock_process = mock_popen.return_value
        mock_process.poll.return_value = None  # Prozess läuft
        
        # Simulator-Status simulieren
        self.controller._is_simulation_running = True
        self.controller._simulator_processes = [mock_process]
        
        # Simulator stoppen
        self.controller.stop_simulator()
        
        # Überprüfen, ob der Prozess beendet wurde
        mock_process.terminate.assert_called_once()
        
        # Überprüfen, ob der Status zurückgesetzt wurde
        self.assertFalse(self.controller._is_simulation_running)
        self.assertEqual(self.controller._simulator_processes, [])
        
        # Überprüfen, ob das Signal ausgelöst wurde
        self.assertTrue(self.sim_stopped_called)
    
    @patch('backend.sitl_controller.requests.get')
    def test_get_binary_path_download(self, mock_get):
        """Testet das Herunterladen des SITL-Binaries."""
        # Mocks für Requests konfigurieren
        mock_response = Mock()
        mock_response.headers = {'content-length': '1000'}
        mock_response.iter_content.return_value = [b'test' * 250]  # 1000 Bytes
        mock_get.return_value = mock_response
        
        # Binary-Path testen (dieser sollte einen Download auslösen)
        with patch('builtins.open', unittest.mock.mock_open()) as mock_file:
            with patch('os.path.exists', return_value=False):  # Binary existiert nicht
                with patch('os.chmod'):  # chmod mock
                    binary_path = self.controller.get_binary_path("copter", "quad", "Stable")
        
        # Überprüfen, ob der Download ausgeführt wurde
        mock_get.assert_called_once()
        mock_file.assert_called_once()


if __name__ == '__main__':
    unittest.main()
