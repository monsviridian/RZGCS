#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for configuration and data persistence in the RZGCS application
"""

import unittest
import sys
import os
import json
from unittest.mock import MagicMock, patch, mock_open

# Add parent directory to path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

class TestConfiguration(unittest.TestCase):
    """Test cases for configuration and data persistence"""
    
    def setUp(self):
        """Set up test environment"""
        self.config_manager = MagicMock()
        self.logger = MagicMock()
    
    def test_load_default_config(self):
        """Test loading default configuration"""
        # Define default config
        default_config = {
            "connection": {
                "port": "COM8",
                "baud_rate": 115200,
                "auto_connect": False
            },
            "ui": {
                "theme": "dark",
                "language": "en",
                "map_type": 1
            },
            "logs": {
                "log_level": "INFO",
                "log_to_file": True,
                "log_file": "rzgcs.log"
            },
            "angel_mode": {
                "default_path": "Europe/Germany",
                "auto_activate": False
            }
        }
        
        # Mock the config manager
        self.config_manager.get_default_config.return_value = default_config
        
        # Load default config
        config = self.load_default_config()
        
        # Verify the config
        self.assertEqual(config["connection"]["port"], "COM8")
        self.assertEqual(config["connection"]["baud_rate"], 115200)
        self.assertEqual(config["ui"]["theme"], "dark")
        self.assertEqual(config["angel_mode"]["default_path"], "Europe/Germany")
    
    def test_save_config(self):
        """Test saving configuration to a file"""
        # Define config
        config = {
            "connection": {
                "port": "COM8",
                "baud_rate": 115200,
                "auto_connect": False
            },
            "ui": {
                "theme": "dark",
                "language": "en",
                "map_type": 1
            }
        }
        
        # Set up mock file
        m = mock_open()
        
        # Save config
        with patch('builtins.open', m):
            self.save_config(config, "config.json")
        
        # Verify the file was written
        m.assert_called_once_with("config.json", 'w')
        handle = m()
        
        # Verify the config was written as JSON
        handle.write.assert_called_once()
        write_args = handle.write.call_args[0]
        saved_config = json.loads(write_args[0])
        
        # Verify the saved config
        self.assertEqual(saved_config["connection"]["port"], "COM8")
        self.assertEqual(saved_config["ui"]["theme"], "dark")
    
    def test_load_config(self):
        """Test loading configuration from a file"""
        # Define config
        config_str = """
        {
            "connection": {
                "port": "COM8",
                "baud_rate": 115200,
                "auto_connect": false
            },
            "ui": {
                "theme": "dark",
                "language": "en",
                "map_type": 1
            }
        }
        """
        
        # Set up mock file
        m = mock_open(read_data=config_str)
        
        # Load config
        with patch('builtins.open', m):
            config = self.load_config("config.json")
        
        # Verify the file was read
        m.assert_called_once_with("config.json", 'r')
        
        # Verify the config
        self.assertEqual(config["connection"]["port"], "COM8")
        self.assertEqual(config["connection"]["baud_rate"], 115200)
        self.assertEqual(config["ui"]["theme"], "dark")
        self.assertEqual(config["ui"]["language"], "en")
    
    def test_update_config(self):
        """Test updating configuration"""
        # Define initial config
        config = {
            "connection": {
                "port": "COM1",
                "baud_rate": 9600,
                "auto_connect": False
            },
            "ui": {
                "theme": "light",
                "language": "de",
                "map_type": 0
            }
        }
        
        # Define updates
        updates = {
            "connection": {
                "port": "COM8",
                "baud_rate": 115200
            },
            "ui": {
                "theme": "dark"
            }
        }
        
        # Update config
        updated_config = self.update_config(config, updates)
        
        # Verify the updated config
        self.assertEqual(updated_config["connection"]["port"], "COM8")
        self.assertEqual(updated_config["connection"]["baud_rate"], 115200)
        self.assertEqual(updated_config["connection"]["auto_connect"], False)
        self.assertEqual(updated_config["ui"]["theme"], "dark")
        self.assertEqual(updated_config["ui"]["language"], "de")
        self.assertEqual(updated_config["ui"]["map_type"], 0)
    
    def test_get_config_value(self):
        """Test getting a specific config value"""
        # Define config
        config = {
            "connection": {
                "port": "COM8",
                "baud_rate": 115200,
                "auto_connect": False
            },
            "ui": {
                "theme": "dark",
                "language": "en",
                "map_type": 1
            }
        }
        
        # Test getting different values
        port = self.get_config_value(config, "connection.port")
        theme = self.get_config_value(config, "ui.theme")
        non_existent = self.get_config_value(config, "non.existent.key", "default")
        
        # Verify the values
        self.assertEqual(port, "COM8")
        self.assertEqual(theme, "dark")
        self.assertEqual(non_existent, "default")
    
    def test_set_config_value(self):
        """Test setting a specific config value"""
        # Define config
        config = {
            "connection": {
                "port": "COM1",
                "baud_rate": 9600,
                "auto_connect": False
            },
            "ui": {
                "theme": "light",
                "language": "de",
                "map_type": 0
            }
        }
        
        # Set config values
        updated_config = self.set_config_value(config, "connection.port", "COM8")
        updated_config = self.set_config_value(updated_config, "ui.theme", "dark")
        updated_config = self.set_config_value(updated_config, "ui.new_setting", "value")
        
        # Verify the updated config
        self.assertEqual(updated_config["connection"]["port"], "COM8")
        self.assertEqual(updated_config["ui"]["theme"], "dark")
        self.assertEqual(updated_config["ui"]["new_setting"], "value")
    
    def test_apply_config(self):
        """Test applying configuration to components"""
        # Define config
        config = {
            "connection": {
                "port": "COM8",
                "baud_rate": 115200,
                "auto_connect": False
            },
            "ui": {
                "theme": "dark",
                "language": "en",
                "map_type": 1
            }
        }
        
        # Create mock components
        serial_connector = MagicMock()
        flight_controller = MagicMock()
        
        # Apply config
        self.apply_config(config, serial_connector, flight_controller)
        
        # Verify the components were configured
        serial_connector.setPort.assert_called_once_with("COM8")
        serial_connector.setBaudRate.assert_called_once_with(115200)
        flight_controller.set_map_type.assert_called_once_with(1)
    
    def test_validate_config(self):
        """Test validating configuration"""
        # Define valid config
        valid_config = {
            "connection": {
                "port": "COM8",
                "baud_rate": 115200,
                "auto_connect": False
            },
            "ui": {
                "theme": "dark",
                "language": "en",
                "map_type": 1
            }
        }
        
        # Define invalid config (missing required fields)
        invalid_config = {
            "connection": {
                "port": "COM8"
            },
            "ui": {
                "theme": "dark"
            }
        }
        
        # Validate configs
        valid_result = self.validate_config(valid_config)
        invalid_result = self.validate_config(invalid_config)
        
        # Verify the results
        self.assertTrue(valid_result)
        self.assertFalse(invalid_result)
    
    def load_default_config(self):
        """Helper method to simulate loading default configuration"""
        return self.config_manager.get_default_config()
    
    def save_config(self, config, filename):
        """Helper method to simulate saving configuration to a file"""
        with open(filename, 'w') as f:
            json.dump(config, f, indent=4)
    
    def load_config(self, filename):
        """Helper method to simulate loading configuration from a file"""
        with open(filename, 'r') as f:
            return json.load(f)
    
    def update_config(self, config, updates):
        """Helper method to simulate updating configuration"""
        result = config.copy()
        
        # Update recursively
        for key, value in updates.items():
            if key in result and isinstance(value, dict) and isinstance(result[key], dict):
                # Recursive update for nested dictionaries
                result[key] = self.update_config(result[key], value)
            else:
                # Direct update for other values
                result[key] = value
        
        return result
    
    def get_config_value(self, config, key_path, default=None):
        """Helper method to simulate getting a specific config value"""
        keys = key_path.split('.')
        value = config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set_config_value(self, config, key_path, value):
        """Helper method to simulate setting a specific config value"""
        keys = key_path.split('.')
        result = config.copy()
        
        # Navigate to the nested dictionary
        current = result
        for i, key in enumerate(keys[:-1]):
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # Set the value
        current[keys[-1]] = value
        
        return result
    
    def apply_config(self, config, serial_connector, flight_controller):
        """Helper method to simulate applying configuration to components"""
        # Configure serial connector
        serial_connector.setPort(config["connection"]["port"])
        serial_connector.setBaudRate(config["connection"]["baud_rate"])
        
        # Configure flight controller
        flight_controller.set_map_type(config["ui"]["map_type"])
        
        # Auto-connect if enabled
        if config["connection"]["auto_connect"]:
            serial_connector.connect()
    
    def validate_config(self, config):
        """Helper method to simulate validating configuration"""
        # Check required fields
        required_fields = [
            "connection.port",
            "connection.baud_rate",
            "connection.auto_connect",
            "ui.theme",
            "ui.language",
            "ui.map_type"
        ]
        
        for field in required_fields:
            if self.get_config_value(config, field) is None:
                return False
        
        return True

if __name__ == '__main__':
    unittest.main()
