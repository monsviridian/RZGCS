#!/usr/bin/env python3
"""
Tests für das MAVSDK Drone ViewModel.
Diese Tests validieren die Funktionalität des MAVSDK-Drone ViewModels und die Integration mit SITL.
"""
import os
import sys
import unittest
import pytest
from unittest.mock import MagicMock, patch
from PySide6.QtCore import QObject, Signal

# Pfad zum Hauptmodul hinzufügen
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# MAVSDKDroneViewModel importieren
from rzgcs.viewmodel.mavsdk_drone_view_model import MAVSDKDroneViewModel

class MockLogger:
    """Mock für den Logger."""
    def __init__(self):
        self.logs = []
    
    def addLog(self, message):
        self.logs.append(message)
        print(f"Log: {message}")  # Für bessere Testausgaben

class TestMAVSDKDroneViewModel(unittest.TestCase):
    """Testet das MAVSDK Drone ViewModel."""
    
    def setUp(self):
        """Richtet die Testumgebung ein."""
        self.logger = MockLogger()
        # Mock der MAVSDK-System-Klasse
        self.mock_system_patcher = patch('rzgcs.viewmodel.mavsdk_drone_view_model.System')
        self.mock_system = self.mock_system_patcher.start()
        
        # Mock des Drone-System-Objekts
        self.mock_drone = MagicMock()
        self.mock_system.return_value = self.mock_drone
        
        # Verschiedene MAVSDK-Komponenten mocken
        self.mock_telemetry = MagicMock()
        self.mock_action = MagicMock()
        self.mock_info = MagicMock()
        self.mock_param = MagicMock()
        
        self.mock_drone.telemetry = self.mock_telemetry
        self.mock_drone.action = self.mock_action
        self.mock_drone.info = self.mock_info
        self.mock_drone.param = self.mock_param
        
        # ViewModel erstellen
        self.drone_vm = MAVSDKDroneViewModel(self.logger)
    
    def tearDown(self):
        """Räumt die Testumgebung auf."""
        self.mock_system_patcher.stop()
    
    def test_init(self):
        """Testet, ob das ViewModel korrekt initialisiert wird."""
        self.assertFalse(self.drone_vm.connected)
        self.assertEqual(self.drone_vm.selectedPort, "")
        self.assertEqual(self.drone_vm.selectedBaudRate, 0)
    
    def test_signals_existence(self):
        """Testet, ob alle erforderlichen Signale existieren."""
        expected_signals = [
            'connectionStateChanged',
            'positionChanged',
            'attitudeChanged',
            'headingChanged',
            'batteryChanged',
            'gpsInfoChanged',
            'messageReceived',
            'errorOccurred',
            'systemInfoReceived'
        ]
        for signal_name in expected_signals:
            self.assertTrue(hasattr(self.drone_vm, signal_name), f"Signal {signal_name} fehlt")
    
    @patch('mavsdk.System')
    @patch('asyncio.run')
    def test_connect_tcp(self, mock_asyncio_run, mock_system):
        """Testet die Verbindung über TCP (für SITL)."""
        # Erfolgreich verbinden
        self.mock_drone.connect.return_value = None
        self.mock_telemetry.armed.return_value = True
        
        # Mock für asyncio.run
        mock_asyncio_run.side_effect = lambda coro: None  # Einfach erfolgreich zurückkehren
        
        # Verbindung herstellen
        connection_string = "tcp://localhost:5760"
        result = self.drone_vm.connect(connection_string)
        
        # Überprüfungen
        self.assertTrue(result)
        self.assertTrue(self.drone_vm.connected)
        mock_asyncio_run.assert_called_once()
    
    @patch('serial.tools.list_ports.comports')
    def test_load_ports(self, mock_comports):
        """Testet das Laden der verfügbaren COM-Ports."""
        # Mock-Ports erstellen
        mock_port1 = MagicMock()
        mock_port1.device = "COM1"
        mock_port2 = MagicMock()
        mock_port2.device = "COM2"
        mock_comports.return_value = [mock_port1, mock_port2]
        
        # Ports laden
        self.drone_vm.load_ports()
        
        # Überprüfungen
        self.assertEqual(len(self.drone_vm.availablePorts), 2)
        self.assertIn("COM1", self.drone_vm.availablePorts)
        self.assertIn("COM2", self.drone_vm.availablePorts)
    
    def test_available_baud_rates(self):
        """Testet die verfügbaren Baudraten."""
        self.assertIn(115200, self.drone_vm.availableBaudRates)
        self.assertIn(57600, self.drone_vm.availableBaudRates)
        self.assertIn(9600, self.drone_vm.availableBaudRates)
    
    def test_set_port_and_baud_rate(self):
        """Testet das Setzen von Port und Baudrate."""
        # Port setzen
        self.drone_vm.setPort("COM1")
        self.assertEqual(self.drone_vm.selectedPort, "COM1")
        
        # Baudrate setzen
        self.drone_vm.setBaudRate(115200)
        self.assertEqual(self.drone_vm.selectedBaudRate, 115200)
    
    @patch('asyncio.run')
    def test_arm_disarm(self, mock_asyncio_run):
        """Testet die Arm- und Disarm-Funktionen."""
        # Mock für asyncio.run
        mock_asyncio_run.side_effect = lambda coro: None
        
        # Simuliere, dass das Drone-Objekt verbunden ist
        self.drone_vm._connected = True
        
        # Arm
        self.drone_vm.arm()
        self.mock_action.arm.assert_called_once()
        
        # Reset Mocks
        self.mock_action.reset_mock()
        
        # Disarm
        self.drone_vm.disarm()
        self.mock_action.disarm.assert_called_once()
    
    @patch('asyncio.run')
    def test_takeoff_land(self, mock_asyncio_run):
        """Testet die Takeoff- und Land-Funktionen."""
        # Mock für asyncio.run
        mock_asyncio_run.side_effect = lambda coro: None
        
        # Simuliere, dass das Drone-Objekt verbunden ist
        self.drone_vm._connected = True
        
        # Takeoff
        self.drone_vm.takeoff()
        self.mock_action.takeoff.assert_called_once()
        
        # Reset Mocks
        self.mock_action.reset_mock()
        
        # Land
        self.drone_vm.land()
        self.mock_action.land.assert_called_once()
    
    @patch('asyncio.run')
    def test_set_flight_mode(self, mock_asyncio_run):
        """Testet das Setzen des Flugmodus."""
        # Mock für asyncio.run
        mock_asyncio_run.side_effect = lambda coro: None
        
        # Simuliere, dass das Drone-Objekt verbunden ist
        self.drone_vm._connected = True
        
        # Flugmodus setzen
        self.drone_vm.setFlightMode("GUIDED")
        # In einer vollständigen Implementierung würden wir hier die Argumente überprüfen
        self.mock_action.set_flight_mode.assert_called_once()
    
    @patch('asyncio.run')
    def test_disconnect(self, mock_asyncio_run):
        """Testet die Disconnect-Funktion."""
        # Mock für asyncio.run
        mock_asyncio_run.side_effect = lambda coro: None
        
        # Simuliere, dass das Drone-Objekt verbunden ist
        self.drone_vm._connected = True
        
        # Verbindung trennen
        self.drone_vm.disconnect()
        
        # Überprüfungen
        self.assertFalse(self.drone_vm.connected)

# Main-Funktion für direktes Ausführen der Tests
if __name__ == "__main__":
    unittest.main()
