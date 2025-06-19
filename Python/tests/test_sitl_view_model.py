#!/usr/bin/env python3
"""
Tests für das SITL ViewModel.
Diese Tests validieren die Funktionalität des Software-in-the-Loop Simulationsmoduls.
"""
import os
import sys
import time
import unittest
import pytest
from unittest.mock import MagicMock, patch
from PySide6.QtCore import QObject, Signal

# Pfad zum Hauptmodul hinzufügen
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# SITL ViewModel importieren
from rzgcs.viewmodel.sitl_view_model import SITLViewModel

class MockLogger:
    """Mock für den Logger."""
    def __init__(self):
        self.logs = []
    
    def addLog(self, message):
        self.logs.append(message)
        print(f"Log: {message}")  # Für bessere Testausgaben

class TestSITLViewModel(unittest.TestCase):
    """Testet das SITL ViewModel."""
    
    def setUp(self):
        """Richtet die Testumgebung ein."""
        self.logger = MockLogger()
        self.sitl_vm = SITLViewModel(self.logger)
    
    def test_init(self):
        """Testet, ob das ViewModel korrekt initialisiert wird."""
        self.assertFalse(self.sitl_vm.isSimulationRunning)
        self.assertEqual(self.sitl_vm.statusMessage, "Bereit")
        self.assertEqual(self.sitl_vm.downloadProgress, 0.0)
    
    def test_signals_existence(self):
        """Testet, ob alle erforderlichen Signale existieren."""
        expected_signals = [
            'simulationStarted',
            'simulationStopped',
            'downloadProgressChanged',
            'statusMessageChanged',
            'errorOccurred',
            'autoConnectRequested'
        ]
        for signal_name in expected_signals:
            self.assertTrue(hasattr(self.sitl_vm, signal_name), f"Signal {signal_name} fehlt")
    
    @patch('subprocess.Popen')
    def test_start_simulation(self, mock_popen):
        """Testet das Starten der Simulation."""
        # Mock für den Prozess konfigurieren
        mock_process = MagicMock()
        mock_process.poll.return_value = None  # Prozess läuft
        mock_popen.return_value = mock_process
        
        # SITL starten
        result = self.sitl_vm.startSimulation("copter", "stable")
        
        # Überprüfungen
        self.assertTrue(result)
        self.assertTrue(self.sitl_vm.isSimulationRunning)
        self.assertIn("gestartet", self.sitl_vm.statusMessage)
        mock_popen.assert_called_once()
        
        # Überprüfen, ob das Signal emittiert wurde (schwer zu testen ohne QSignalSpy)
        # In einem echten Test könnte QSignalSpy verwendet werden
        
    @patch('subprocess.Popen')
    def test_start_simulation_failure(self, mock_popen):
        """Testet den Fehlerfall beim Starten der Simulation."""
        # Mock für fehlgeschlagenen Prozessstart
        mock_popen.side_effect = Exception("Simulationsstart fehlgeschlagen")
        
        # SITL starten sollte fehlschlagen
        result = self.sitl_vm.startSimulation("copter", "stable")
        
        # Überprüfungen
        self.assertFalse(result)
        self.assertFalse(self.sitl_vm.isSimulationRunning)
        self.assertIn("Fehler", self.sitl_vm.statusMessage)
    
    @patch('subprocess.Popen')
    def test_stop_simulation(self, mock_popen):
        """Testet das Stoppen der Simulation."""
        # Mock für den Prozess konfigurieren
        mock_process = MagicMock()
        mock_process.poll.return_value = None  # Prozess läuft
        mock_popen.return_value = mock_process
        
        # SITL starten und dann stoppen
        self.sitl_vm.startSimulation("copter", "stable")
        result = self.sitl_vm.stopSimulation()
        
        # Überprüfungen
        self.assertTrue(result)
        self.assertFalse(self.sitl_vm.isSimulationRunning)
        mock_process.terminate.assert_called_once()
    
    def test_set_home_position(self):
        """Testet das Setzen der Home-Position."""
        test_lat = 49.445232
        test_lon = 7.769488
        
        self.sitl_vm.setHomePosition(test_lat, test_lon)
        
        self.assertEqual(self.sitl_vm.home_lat, test_lat)
        self.assertEqual(self.sitl_vm.home_lon, test_lon)
    
    @patch('requests.get')
    def test_download_sitl_binary(self, mock_get):
        """Testet das Herunterladen der SITL-Binärdatei."""
        # Mock für HTTP-Response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.iter_content.return_value = [b"chunk1", b"chunk2", b"chunk3"]
        mock_get.return_value = mock_response
        
        # Download-URL und Zielverzeichnis
        url = "http://example.com/ardupilot/copter.exe"
        target_dir = "./temp_test_dir"
        
        # Mock für os.path.exists und os.makedirs
        with patch('os.path.exists', return_value=False), \
             patch('os.makedirs'), \
             patch('builtins.open', unittest.mock.mock_open()):
            
            result = self.sitl_vm._download_sitl_binary(url, target_dir)
            
            # Überprüfungen
            self.assertTrue(result)
            mock_get.assert_called_once_with(url, stream=True)
    
    def test_auto_connect_to_simulation(self):
        """Testet die automatische Verbindung zur Simulation."""
        # Patchen des autoConnectRequested-Signals
        self.signal_emitted = False
        
        def on_auto_connect_requested(conn_str):
            self.signal_emitted = True
            self.connection_string = conn_str
        
        # Signal-Handler hinzufügen
        self.sitl_vm.autoConnectRequested.connect(on_auto_connect_requested)
        
        # Funktion aufrufen
        self.sitl_vm._auto_connect_to_simulation()
        
        # Überprüfungen
        self.assertTrue(self.signal_emitted)
        self.assertIn("tcp:", self.connection_string)

# Main-Funktion für direktes Ausführen der Tests
if __name__ == "__main__":
    unittest.main()
