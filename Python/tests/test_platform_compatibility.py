# tests/test_platform_compatibility.py
import unittest
import sys
import os
import platform
from unittest.mock import MagicMock, patch

# Fu00fcge das Hauptverzeichnis zum Pfad hinzu, um relative Importe zu ermu00f6glichen
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.connection_manager import ConnectionManager

class TestConnectionManager(unittest.TestCase):
    """Tests fu00fcr die plattformu00fcbergreifende Funktionalitu00e4t des ConnectionManagers"""
    
    def setUp(self):
        # Aktuelle Plattform sichern, um sie spu00e4ter wiederherzustellen
        self.original_platform = platform.system()
    
    def test_get_available_ports_windows(self):
        """Test der Port-Erkennung unter Windows"""
        with patch('platform.system', return_value='Windows'):
            with patch('serial.tools.list_ports.comports') as mock_comports:
                # Simuliere Windows-COM-Ports
                mock_port1 = MagicMock()
                mock_port1.device = 'COM1'
                mock_port1.description = 'USB Serial Device'
                mock_port1.hwid = 'USB VID:PID=1A86:7523'
                
                mock_port2 = MagicMock()
                mock_port2.device = 'COM8'
                mock_port2.description = 'ArduPilot'
                mock_port2.hwid = 'USB VID:PID=2341:0043'
                
                mock_comports.return_value = [mock_port1, mock_port2]
                
                # ConnectionManager mit simulierter Windows-Plattform initialisieren
                cm = ConnectionManager()
                ports = cm.get_available_ports()
                
                # u00dcberpru00fcfe, ob Windows-Ports korrekt erkannt werden
                self.assertEqual(len(ports), 2)
                self.assertEqual(ports[0]['port'], 'COM1')
                self.assertEqual(ports[1]['port'], 'COM8')
    
    def test_get_available_ports_macos(self):
        """Test der Port-Erkennung unter macOS"""
        with patch('platform.system', return_value='Darwin'):
            with patch('serial.tools.list_ports.comports') as mock_comports:
                # Simuliere macOS-Ports
                mock_port1 = MagicMock()
                mock_port1.device = '/dev/cu.usbmodem1421'
                mock_port1.description = 'USB Serial Device'
                mock_port1.hwid = 'USB VID:PID=1A86:7523'
                
                mock_port2 = MagicMock()
                mock_port2.device = '/dev/cu.SLAB_USBtoUART'
                mock_port2.description = 'CP210x USB to UART Bridge'
                mock_port2.hwid = 'USB VID:PID=10C4:EA60'
                
                mock_comports.return_value = [mock_port1, mock_port2]
                
                # ConnectionManager mit simulierter macOS-Plattform initialisieren
                cm = ConnectionManager()
                ports = cm.get_available_ports()
                
                # u00dcberpru00fcfe, ob macOS-Ports korrekt erkannt werden
                self.assertEqual(len(ports), 2)
                self.assertEqual(ports[0]['port'], '/dev/cu.usbmodem1421')
                self.assertEqual(ports[1]['port'], '/dev/cu.SLAB_USBtoUART')
                self.assertTrue(ports[0].get('probable_fc', False))
                self.assertTrue(ports[1].get('probable_fc', False))
    
    def test_get_default_connection_params(self):
        """Test der plattformspezifischen Standardverbindungsparameter"""
        # Test fu00fcr Windows
        with patch('platform.system', return_value='Windows'):
            cm = ConnectionManager()
            params = cm.get_default_connection_params()
            self.assertEqual(params['port'], 'COM8')
            self.assertEqual(params['baudrate'], 57600)
        
        # Test fu00fcr macOS
        with patch('platform.system', return_value='Darwin'):
            with patch.object(ConnectionManager, 'get_available_ports') as mock_get_ports:
                # Simuliere verfu00fcgbare Ports
                mock_get_ports.return_value = [
                    {'port': '/dev/cu.usbmodem1421', 'probable_fc': True},
                    {'port': '/dev/cu.SLAB_USBtoUART', 'probable_fc': True}
                ]
                
                cm = ConnectionManager()
                params = cm.get_default_connection_params()
                self.assertEqual(params['port'], '/dev/cu.usbmodem1421')  # Erster FC-Port
                self.assertEqual(params['baudrate'], 57600)
    
    def test_create_connection_string(self):
        """Test der Erstellung des Verbindungsstrings fu00fcr verschiedene Plattformen"""
        # Test fu00fcr Windows
        with patch('platform.system', return_value='Windows'):
            cm = ConnectionManager()
            conn_str = cm.create_connection_string('serial', port='COM8', baudrate=57600)
            self.assertEqual(conn_str, 'COM8')  # Windows gibt nur den Portnamen zuru00fcck
        
        # Test fu00fcr macOS
        with patch('platform.system', return_value='Darwin'):
            cm = ConnectionManager()
            conn_str = cm.create_connection_string('serial', port='/dev/cu.usbmodem1421', baudrate=57600)
            self.assertEqual(conn_str, '/dev/cu.usbmodem1421')  # macOS verwendet den vollstu00e4ndigen Pfad

class TestMAVLinkConnector(unittest.TestCase):
    """Tests fu00fcr die plattformu00fcbergreifende Funktionalitu00e4t des MAVLinkConnectors"""
    
    def test_mavsdk_server_path_windows(self):
        """Test des MAVSDK-Server-Pfads unter Windows"""
        with patch('sys.platform', 'win32'):
            with patch('pathlib.Path.exists', return_value=True):
                from backend.mavlink_connector import get_mavsdk_server_path
                server_path = get_mavsdk_server_path()
                self.assertTrue('windows' in server_path)
                self.assertTrue(server_path.endswith('mavsdk-server.exe'))
    
    def test_mavsdk_server_path_macos(self):
        """Test des MAVSDK-Server-Pfads unter macOS"""
        with patch('sys.platform', 'darwin'):
            with patch('pathlib.Path.exists', side_effect=lambda p: 'mac' in str(p)):
                from backend.mavlink_connector import get_mavsdk_server_path
                server_path = get_mavsdk_server_path()
                self.assertTrue('mac' in server_path)
                self.assertTrue(server_path.endswith('mavsdk-server'))

# Haupttest-Runner
if __name__ == '__main__':
    unittest.main()
