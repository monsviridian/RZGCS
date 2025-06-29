"""
Test-Datei für DroneKit-Integration
"""

import asyncio
import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Pfad zum backend-Modul hinzufügen
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from backend.rzgcs_dronekit.connector import DroneKitConnector
from backend.rzgcs_dronekit.utils import DroneKitUtils
from backend.rzgcs_dronekit.connection_manager import DroneKitConnectionManager
from backend.rzgcs_dronekit.telemetry_handler import DroneKitTelemetryHandler
from backend.rzgcs_dronekit.control_handler import DroneKitControlHandler
from backend.rzgcs_dronekit.mission_handler import DroneKitMissionHandler
from backend.rzgcs_dronekit.parameter_manager import DroneKitParameterManager
from backend.rzgcs_dronekit.vehicle_manager import DroneKitVehicleManager

class TestDroneKitUtils(unittest.TestCase):
    """Tests für DroneKitUtils"""
    
    def test_validate_connection_string(self):
        """Test für Verbindungsstring-Validierung"""
        # Gültige Strings
        self.assertEqual(DroneKitUtils.validate_connection_string("udp://127.0.0.1:14550"), 
                        "udp://127.0.0.1:14550")
        self.assertEqual(DroneKitUtils.validate_connection_string("tcp://192.168.1.100:5760"), 
                        "tcp://192.168.1.100:5760")
        self.assertEqual(DroneKitUtils.validate_connection_string("COM3"), 
                        "COM3:115200")
        self.assertEqual(DroneKitUtils.validate_connection_string("/dev/ttyACM0"), 
                        "/dev/ttyACM0")
        
        # Ungültige Strings
        with self.assertRaises(ValueError):
            DroneKitUtils.validate_connection_string("")
        
        with self.assertRaises(ValueError):
            DroneKitUtils.validate_connection_string("invalid://string")
    
    def test_calculate_distance(self):
        """Test für Distanz-Berechnung"""
        # Berlin nach München (ungefähre Koordinaten)
        berlin_lat, berlin_lon = 52.5200, 13.4050
        munich_lat, munich_lon = 48.1351, 11.5820
        
        distance = DroneKitUtils.calculate_distance(berlin_lat, berlin_lon, munich_lat, munich_lon)
        
        # Distanz sollte etwa 500-600 km sein
        self.assertGreater(distance, 500000)  # 500 km
        self.assertLess(distance, 600000)     # 600 km
    
    def test_calculate_bearing(self):
        """Test für Bearing-Berechnung"""
        # Norden
        bearing = DroneKitUtils.calculate_bearing(0, 0, 1, 0)
        self.assertAlmostEqual(bearing, 0, delta=1)
        
        # Osten
        bearing = DroneKitUtils.calculate_bearing(0, 0, 0, 1)
        self.assertAlmostEqual(bearing, 90, delta=1)
        
        # Süden
        bearing = DroneKitUtils.calculate_bearing(0, 0, -1, 0)
        self.assertAlmostEqual(bearing, 180, delta=1)
        
        # Westen
        bearing = DroneKitUtils.calculate_bearing(0, 0, 0, -1)
        self.assertAlmostEqual(bearing, 270, delta=1)
    
    def test_format_functions(self):
        """Test für Format-Funktionen"""
        # Koordinaten
        self.assertEqual(DroneKitUtils.format_coordinate(52.5200, 13.4050), 
                        "52.520000, 13.405000")
        
        # Höhe
        self.assertEqual(DroneKitUtils.format_altitude(1500), "1.5 km")
        self.assertEqual(DroneKitUtils.format_altitude(500), "500.0 m")
        
        # Geschwindigkeit
        self.assertEqual(DroneKitUtils.format_speed(15.5), "15.5 m/s")
        self.assertEqual(DroneKitUtils.format_speed(0.5), "50 cm/s")
        
        # Batterie
        self.assertEqual(DroneKitUtils.format_battery(85.7), "86%")
    
    def test_flight_mode_encoding(self):
        """Test für Flight-Mode-Encoding"""
        # Decodierung
        self.assertEqual(DroneKitUtils.decode_flight_mode(4), "GUIDED")
        self.assertEqual(DroneKitUtils.decode_flight_mode(3), "AUTO")
        self.assertEqual(DroneKitUtils.decode_flight_mode(999), "UNKNOWN")
        
        # Encodierung
        self.assertEqual(DroneKitUtils.encode_flight_mode("GUIDED"), 4)
        self.assertEqual(DroneKitUtils.encode_flight_mode("AUTO"), 3)
        self.assertEqual(DroneKitUtils.encode_flight_mode("INVALID"), 0)
    
    def test_waypoint_creation(self):
        """Test für Waypoint-Erstellung"""
        waypoint = DroneKitUtils.create_waypoint(52.5200, 13.4050, 100.0)
        
        self.assertEqual(waypoint['lat'], 52.5200)
        self.assertEqual(waypoint['lon'], 13.4050)
        self.assertEqual(waypoint['alt'], 100.0)
        self.assertEqual(waypoint['command'], 16)  # MAV_CMD_NAV_WAYPOINT
        self.assertEqual(waypoint['frame'], 0)     # MAV_FRAME_GLOBAL

class TestDroneKitConnectionManager(unittest.TestCase):
    """Tests für DroneKitConnectionManager"""
    
    def setUp(self):
        """Setup für Tests"""
        self.manager = DroneKitConnectionManager()
    
    def test_initialization(self):
        """Test für Initialisierung"""
        self.assertFalse(self.manager.is_connected)
        self.assertEqual(self.manager.connection_string, "")
        self.assertIsNone(self.manager.vehicle)
    
    def test_connection_timeout_settings(self):
        """Test für Connection-Timeout-Einstellungen"""
        self.manager.set_connection_timeout(60)
        self.assertEqual(self.manager.connection_timeout, 60)
        
        self.manager.set_heartbeat_timeout(10)
        self.assertEqual(self.manager.heartbeat_timeout, 10)
        
        self.manager.set_reconnect_attempts(5)
        self.assertEqual(self.manager.reconnect_attempts, 5)
        
        self.manager.set_reconnect_delay(5)
        self.assertEqual(self.manager.reconnect_delay, 5)
    
    def test_connection_status(self):
        """Test für Verbindungsstatus"""
        status = self.manager.get_connection_status()
        
        self.assertIn('connected', status)
        self.assertIn('connection_string', status)
        self.assertIn('last_heartbeat', status)
        self.assertIn('time_since_heartbeat', status)
        self.assertIn('vehicle_ready', status)
        
        self.assertFalse(status['connected'])
        self.assertEqual(status['connection_string'], "")

class TestDroneKitTelemetryHandler(unittest.TestCase):
    """Tests für DroneKitTelemetryHandler"""
    
    def setUp(self):
        """Setup für Tests"""
        self.mock_vehicle = Mock()
        self.mock_connector = Mock()
        self.handler = DroneKitTelemetryHandler(self.mock_vehicle, self.mock_connector)
    
    def test_initialization(self):
        """Test für Initialisierung"""
        self.assertEqual(self.handler.vehicle, self.mock_vehicle)
        self.assertEqual(self.handler.connector, self.mock_connector)
        self.assertFalse(self.handler.callbacks_registered)
        self.assertIsInstance(self.handler.update_rates, dict)
        self.assertIsInstance(self.handler.telemetry_cache, dict)
    
    def test_update_rates(self):
        """Test für Update-Rates"""
        rates = self.handler.get_update_rates()
        
        self.assertIn('gps', rates)
        self.assertIn('attitude', rates)
        self.assertIn('battery', rates)
        self.assertIn('vfr_hud', rates)
        
        # Rate ändern
        self.handler.set_update_rate('gps', 2.0)
        self.assertEqual(self.handler.update_rates['gps'], 2.0)
    
    def test_telemetry_cache(self):
        """Test für Telemetrie-Cache"""
        # Cache leeren
        self.handler.clear_telemetry_cache()
        self.assertEqual(len(self.handler.telemetry_cache), 0)
        
        # Daten hinzufügen
        self.handler.telemetry_cache['test'] = 123
        self.assertEqual(self.handler.get_specific_telemetry('test'), 123)
        self.assertIsNone(self.handler.get_specific_telemetry('nonexistent'))

class TestDroneKitControlHandler(unittest.TestCase):
    """Tests für DroneKitControlHandler"""
    
    def setUp(self):
        """Setup für Tests"""
        self.mock_vehicle = Mock()
        self.mock_connector = Mock()
        self.handler = DroneKitControlHandler(self.mock_vehicle, self.mock_connector)
    
    def test_initialization(self):
        """Test für Initialisierung"""
        self.assertEqual(self.handler.vehicle, self.mock_vehicle)
        self.assertEqual(self.handler.connector, self.mock_connector)
        self.assertFalse(self.handler.is_armed)
        self.assertFalse(self.handler.is_flying)
        self.assertEqual(self.handler.current_altitude, 0.0)
    
    def test_control_status(self):
        """Test für Control-Status"""
        status = self.handler.get_control_status()
        
        self.assertIn('armed', status)
        self.assertIn('flying', status)
        self.assertIn('current_altitude', status)
        self.assertIn('mode', status)
        self.assertIn('location', status)
        
        self.assertFalse(status['armed'])
        self.assertFalse(status['flying'])
        self.assertEqual(status['current_altitude'], 0.0)

class TestDroneKitMissionHandler(unittest.TestCase):
    """Tests für DroneKitMissionHandler"""
    
    def setUp(self):
        """Setup für Tests"""
        self.mock_vehicle = Mock()
        self.mock_connector = Mock()
        self.handler = DroneKitMissionHandler(self.mock_vehicle, self.mock_connector)
    
    def test_initialization(self):
        """Test für Initialisierung"""
        self.assertEqual(self.handler.vehicle, self.mock_vehicle)
        self.assertEqual(self.handler.connector, self.mock_connector)
        self.assertEqual(self.handler.current_mission, [])
        self.assertFalse(self.handler.mission_uploaded)
        self.assertFalse(self.handler.mission_running)
        self.assertEqual(self.handler.current_waypoint, 0)
        self.assertEqual(self.handler.total_waypoints, 0)
    
    def test_mission_status(self):
        """Test für Mission-Status"""
        status = self.handler.get_mission_status()
        
        self.assertIn('total_waypoints', status)
        self.assertIn('current_waypoint', status)
        self.assertIn('mission_uploaded', status)
        self.assertIn('mission_running', status)
        self.assertIn('in_mission', status)
        self.assertIn('progress', status)
        
        self.assertEqual(status['total_waypoints'], 0)
        self.assertEqual(status['current_waypoint'], 0)
        self.assertFalse(status['mission_uploaded'])
        self.assertFalse(status['mission_running'])
        self.assertFalse(status['in_mission'])
        self.assertEqual(status['progress'], 0)

class TestDroneKitParameterManager(unittest.TestCase):
    """Tests für DroneKitParameterManager"""
    
    def setUp(self):
        """Setup für Tests"""
        self.mock_vehicle = Mock()
        self.mock_connector = Mock()
        self.manager = DroneKitParameterManager(self.mock_vehicle, self.mock_connector)
    
    def test_initialization(self):
        """Test für Initialisierung"""
        self.assertEqual(self.manager.vehicle, self.mock_vehicle)
        self.assertEqual(self.manager.connector, self.mock_connector)
        self.assertEqual(self.manager.parameters_cache, {})
        self.assertFalse(self.manager.parameters_loaded_flag)
    
    def test_parameter_search(self):
        """Test für Parameter-Suche"""
        # Test-Daten hinzufügen
        self.manager.parameters_cache = {
            'SYSID_MYGCS': 255,
            'ARMING_CHECK': 1,
            'RTL_ALT': 100,
            'WPNAV_SPEED': 5.0
        }
        
        # Suche nach "SYS"
        results = self.manager.search_parameters("SYS")
        self.assertIn('SYSID_MYGCS', results)
        self.assertEqual(results['SYSID_MYGCS'], 255)
        
        # Suche nach "ARM"
        results = self.manager.search_parameters("ARM")
        self.assertIn('ARMING_CHECK', results)
        self.assertEqual(results['ARMING_CHECK'], 1)
    
    def test_parameter_categories(self):
        """Test für Parameter-Kategorien"""
        # Test-Daten hinzufügen
        self.manager.parameters_cache = {
            'SYSID_MYGCS': 255,
            'ARMING_CHECK': 1,
            'RTL_ALT': 100,
            'WPNAV_SPEED': 5.0,
            'BATT_CAPACITY': 5200
        }
        
        categories = self.manager.get_parameter_categories()
        
        self.assertIn('System', categories)
        self.assertIn('Arming', categories)
        self.assertIn('Navigation', categories)
        self.assertIn('Battery', categories)
        
        self.assertIn('SYSID_MYGCS', categories['System'])
        self.assertIn('ARMING_CHECK', categories['Arming'])
        self.assertIn('RTL_ALT', categories['Navigation'])
        self.assertIn('BATT_CAPACITY', categories['Battery'])

class TestDroneKitVehicleManager(unittest.TestCase):
    """Tests für DroneKitVehicleManager"""
    
    def setUp(self):
        """Setup für Tests"""
        self.mock_vehicle = Mock()
        self.mock_connector = Mock()
        self.manager = DroneKitVehicleManager(self.mock_vehicle, self.mock_connector)
    
    def test_initialization(self):
        """Test für Initialisierung"""
        self.assertEqual(self.manager.vehicle, self.mock_vehicle)
        self.assertEqual(self.manager.connector, self.mock_connector)
        self.assertEqual(self.manager.vehicle_info, {})
        self.assertEqual(self.manager.system_status, "UNKNOWN")
        self.assertFalse(self.manager.is_ready)
    
    def test_vehicle_summary(self):
        """Test für Vehicle-Zusammenfassung"""
        # Test-Daten setzen
        self.manager.vehicle_info = {
            'system_id': 1,
            'autopilot_type': 'ArduPilot',
            'vehicle_type': 'Quadcopter',
            'firmware_version': {'major': 4, 'minor': 2, 'patch': 0},
            'is_armable': True
        }
        self.manager.system_status = "ACTIVE"
        self.manager.is_ready = True
        
        summary = self.manager.get_vehicle_summary()
        
        self.assertEqual(summary['system_id'], 1)
        self.assertEqual(summary['autopilot_type'], 'ArduPilot')
        self.assertEqual(summary['vehicle_type'], 'Quadcopter')
        self.assertEqual(summary['system_status'], 'ACTIVE')
        self.assertTrue(summary['is_ready'])
    
    def test_vehicle_health(self):
        """Test für Vehicle-Gesundheit"""
        health = self.manager.get_vehicle_health()
        
        self.assertIn('gps_health', health)
        self.assertIn('battery_health', health)
        self.assertIn('system_health', health)
        self.assertIn('overall_health', health)
        
        # Alle sollten "UNKNOWN" sein, da keine echten Daten vorhanden
        self.assertEqual(health['gps_health'], 'UNKNOWN')
        self.assertEqual(health['battery_health'], 'UNKNOWN')
        self.assertEqual(health['system_health'], 'UNKNOWN')
        self.assertEqual(health['overall_health'], 'UNKNOWN')

class TestDroneKitConnector(unittest.TestCase):
    """Tests für DroneKitConnector"""
    
    def setUp(self):
        """Setup für Tests"""
        self.connector = DroneKitConnector("udp://127.0.0.1:14550")
    
    def test_initialization(self):
        """Test für Initialisierung"""
        self.assertEqual(self.connector.connection_string, "udp://127.0.0.1:14550")
        self.assertIsNone(self.connector.vehicle)
        self.assertFalse(self.connector.is_connected)
        self.assertIsInstance(self.connector.telemetry_cache, dict)
    
    def test_properties(self):
        """Test für Properties"""
        self.assertFalse(self.connector.connected)
        self.assertFalse(self.connector.vehicle_ready)
        self.assertEqual(self.connector.flight_mode, "UNKNOWN")
        self.assertFalse(self.connector.armed)
    
    def test_getter_methods(self):
        """Test für Getter-Methoden"""
        # Alle sollten leere Dictionaries zurückgeben, da keine Verbindung besteht
        self.assertEqual(self.connector.get_telemetry_data(), {})
        self.assertEqual(self.connector.get_mission_status(), {})
        self.assertEqual(self.connector.get_control_status(), {})
        self.assertEqual(self.connector.get_parameter_summary(), {})
        self.assertEqual(self.connector.get_vehicle_summary(), {})
        self.assertEqual(self.connector.get_vehicle_health(), {})
        self.assertEqual(self.connector.get_connection_status(), {})

if __name__ == '__main__':
    # Test-Suite ausführen
    unittest.main(verbosity=2) 