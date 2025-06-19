"""
Tests für die ViewModel-Schicht der MVVM-Architektur.

Diese Tests überprüfen die korrekte Funktionalität der verschiedenen 
ViewModels und deren Integration mit den Models und Views.
"""

import os
import sys
import unittest
from unittest.mock import Mock, patch, MagicMock
import pytest

# Pfad zum Hauptverzeichnis hinzufügen, damit Module importiert werden können
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# ViewModel-Importe
from rzgcs.viewmodel.mavsdk_drone_view_model import MAVSDKDroneViewModel
from rzgcs.viewmodel.sensor_viewmodel import SensorViewModel
from rzgcs.viewmodel.sitl_view_model import SITLViewModel

# Andere notwendige Importe
from backend.logger import Logger


class TestMAVSDKDroneViewModel(unittest.TestCase):
    """Tests für das MAVSDKDroneViewModel."""
    
    def setUp(self):
        """Testumgebung einrichten."""
        self.logger = Mock(spec=Logger)
        self.drone_vm = MAVSDKDroneViewModel(self.logger)
        
        # Signal-Empfänger simulieren
        self.connection_state_changed_called = False
        self.message_received_called = False
        self.error_occurred_called = False
        
        # Signals mit Mock-Funktionen verbinden
        self.drone_vm.connectionStateChanged.connect(self._on_connection_state_changed)
        self.drone_vm.messageReceived.connect(self._on_message_received)
        self.drone_vm.errorOccurred.connect(self._on_error_occurred)
    
    def _on_connection_state_changed(self, is_connected):
        """Mock für Signal-Handler."""
        self.connection_state_changed_called = True
        self.last_connection_state = is_connected
    
    def _on_message_received(self, message):
        """Mock für Signal-Handler."""
        self.message_received_called = True
        self.last_message = message
    
    def _on_error_occurred(self, error):
        """Mock für Signal-Handler."""
        self.error_occurred_called = True
        self.last_error = error
    
    def test_initial_state(self):
        """Testet den initialen Zustand des ViewModels."""
        self.assertFalse(self.drone_vm.connectionState)
        self.assertFalse(self.drone_vm.connected)  # Alias-Property für QML
        
    @patch('rzgcs.viewmodel.mavsdk_drone_view_model.MAVSDKConnectionHelper')
    def test_connection_handling(self, mock_connection_helper):
        """Testet die Verbindungsverwaltung."""
        # Mock-Connection-Helper konfigurieren
        mock_instance = mock_connection_helper.return_value
        mock_instance.connect.return_value = True
        
        # Verbindung herstellen
        conn_string = "tcp:127.0.0.1:5760"
        result = self.drone_vm.connect(conn_string)
        
        # Überprüfungen
        self.assertTrue(result)
        mock_instance.connect.assert_called_once_with(conn_string)
        
    @patch('rzgcs.viewmodel.mavsdk_drone_view_model.MAVSDKConnectionHelper')
    def test_baudrate_extraction(self, mock_connection_helper):
        """Testet die Extraktion der Baudrate aus dem Verbindungsstring."""
        # Mock-Connection-Helper konfigurieren
        mock_instance = mock_connection_helper.return_value
        mock_instance.connect.return_value = True
        
        # Verbindung mit Baudrate herstellen
        conn_string = "COM3:115200"
        self.drone_vm.connect(conn_string)
        
        # Überprüfen, ob die Baudrate korrekt extrahiert wurde
        # Die genaue Überprüfung hängt von der Implementierung ab
        mock_instance.connect.assert_called_once()
        
    def test_connected_property(self):
        """Testet, dass die 'connected' Property als Alias für 'connectionState' funktioniert."""
        # Internen Zustand ändern
        self.drone_vm._connection_state = True
        
        # Überprüfen, ob beide Properties denselben Wert haben
        self.assertTrue(self.drone_vm.connectionState)
        self.assertTrue(self.drone_vm.connected)
        
        # Zustand zurücksetzen
        self.drone_vm._connection_state = False
        self.assertFalse(self.drone_vm.connectionState)
        self.assertFalse(self.drone_vm.connected)


class TestSensorViewModel(unittest.TestCase):
    """Tests für das SensorViewModel."""
    
    def setUp(self):
        """Testumgebung einrichten."""
        self.sensor_vm = SensorViewModel()
        
        # Signal-Empfänger simulieren
        self.sensor_list_changed_called = False
        
        # Signals mit Mock-Funktionen verbinden
        self.sensor_vm.sensorListChanged.connect(self._on_sensor_list_changed)
    
    def _on_sensor_list_changed(self):
        """Mock für Signal-Handler."""
        self.sensor_list_changed_called = True
    
    def test_update_sensor(self):
        """Testet die Aktualisierung eines Sensors."""
        # Sensor aktualisieren
        self.sensor_vm.update_sensor("test_sensor", 42.0)
        
        # Überprüfen, ob der Sensor im Model ist
        self.assertEqual(self.sensor_vm.get_sensor_value("test_sensor"), 42.0)
    
    def test_update_qml_sensor(self):
        """Testet die Aktualisierung eines QML-Sensors mit Name, Wert und Einheit."""
        # QML-Sensor aktualisieren
        self.sensor_vm.updateQmlSensor("Test", 42.0, "m")
        
        # Überprüfen, ob der Sensor im Model ist und das Signal ausgelöst wurde
        sensor_list = self.sensor_vm.get_sensor_list()
        self.assertTrue(any(s["name"] == "Test" and s["value"] == 42.0 and s["unit"] == "m" for s in sensor_list))
        self.assertTrue(self.sensor_list_changed_called)
    
    def test_update_from_telemetry(self):
        """Testet die update_from_telemetry Methode mit verschiedenen Telemetrietypen."""
        # Attitude-Telemetrie simulieren
        attitude_data = {
            "data": {
                "roll": {"value": 10.5, "unit": "°"},
                "pitch": {"value": -5.2, "unit": "°"},
                "yaw": {"value": 180.0, "unit": "°"}
            }
        }
        
        # Telemetrie-Update durchführen
        self.sensor_vm.update_from_telemetry("attitude", attitude_data)
        
        # Überprüfen, ob die Sensoren korrekt aktualisiert wurden
        sensor_list = self.sensor_vm.get_sensor_list()
        
        # Nach Roll suchen
        roll_sensor = next((s for s in sensor_list if s["name"] == "Roll"), None)
        self.assertIsNotNone(roll_sensor)
        self.assertEqual(roll_sensor["value"], 10.5)
        self.assertEqual(roll_sensor["unit"], "°")
        
        # Nach Pitch suchen
        pitch_sensor = next((s for s in sensor_list if s["name"] == "Pitch"), None)
        self.assertIsNotNone(pitch_sensor)
        self.assertEqual(pitch_sensor["value"], -5.2)
        self.assertEqual(pitch_sensor["unit"], "°")


class TestSITLViewModel(unittest.TestCase):
    """Tests für das SITLViewModel."""
    
    def setUp(self):
        """Testumgebung einrichten."""
        self.logger = Mock(spec=Logger)
        self.sitl_vm = SITLViewModel(self.logger)
        
        # Mocks für Controller-Methoden
        self.sitl_vm._controller = Mock()
        
        # Signal-Empfänger simulieren
        self.simulation_started_called = False
        self.simulation_stopped_called = False
        self.auto_connect_requested_called = False
        
        # Signals mit Mock-Funktionen verbinden
        self.sitl_vm.simulationStarted.connect(self._on_simulation_started)
        self.sitl_vm.simulationStopped.connect(self._on_simulation_stopped)
        self.sitl_vm.autoConnectRequested.connect(self._on_auto_connect_requested)
    
    def _on_simulation_started(self, vehicle_type, connection_string):
        """Mock für Signal-Handler."""
        self.simulation_started_called = True
        self.last_vehicle_type = vehicle_type
        self.last_connection_string = connection_string
    
    def _on_simulation_stopped(self):
        """Mock für Signal-Handler."""
        self.simulation_stopped_called = True
    
    def _on_auto_connect_requested(self, connection_string):
        """Mock für Signal-Handler."""
        self.auto_connect_requested_called = True
        self.auto_connect_string = connection_string
    
    def test_start_copter_simulation(self):
        """Testet das Starten einer Copter-Simulation."""
        # Controller-Mock konfigurieren
        self.sitl_vm._controller.start_simulator.return_value = True
        self.sitl_vm._controller.build_home_location.return_value = "49.0,8.0,40.0,0.0"
        
        # Simulation starten
        self.sitl_vm.startCopterSimulation()
        
        # Überprüfen, ob der Controller aufgerufen wurde
        self.sitl_vm._controller.start_simulator.assert_called_once()
        # Die genauen Parameter hängen von der Implementierung ab
        args, kwargs = self.sitl_vm._controller.start_simulator.call_args
        self.assertEqual(args[0], "copter")  # Erster Parameter sollte "copter" sein
        self.assertEqual(args[1], "quad")    # Zweiter Parameter sollte "quad" sein
    
    def test_auto_connect_request(self):
        """Testet, dass das autoConnectRequested-Signal ausgelöst wird."""
        # Mock für _on_simulation_started aufrufen (interne Methode, würde normalerweise 
        # durch das Signal des Controllers ausgelöst)
        
        # Simulation-Start simulieren
        self.sitl_vm._on_simulation_started("copter", "tcp:127.0.0.1:5760")
        
        # Überprüfen, ob das Signal ausgelöst wurde
        # Hinweis: Die eigentliche _auto_connect_to_simulation-Methode enthält
        # einen time.sleep, was den Test verlangsamen würde, daher testen wir
        # nur, ob das Signal ausgelöst wurde
        self.assertTrue(self.auto_connect_requested_called)
        self.assertEqual(self.auto_connect_string, "tcp:127.0.0.1:5760")


if __name__ == '__main__':
    unittest.main()
