# tests/test_license_system.py
import unittest
import sys
import os
import time
import tempfile
import json
import base64
from unittest.mock import MagicMock, patch

# Füge das Hauptverzeichnis zum Pfad hinzu, um relative Importe zu ermöglichen
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.license_manager import LicenseManager
from backend.license_ui import LicenseController
from PySide6.QtCore import QObject, Signal

class MockLogger(QObject):
    """Mock-Logger für Tests"""
    def __init__(self):
        super().__init__()
        self.logs = []
    
    def addLog(self, message):
        self.logs.append(message)
        print(f"[LOG] {message}")

class TestLicenseManager(unittest.TestCase):
    """Tests für den LicenseManager"""
    
    def setUp(self):
        # Erstelle einen temporären Pfad für Lizenzdateien
        self.temp_dir = tempfile.TemporaryDirectory()
        
        # Patche die _get_license_path-Methode, um temporäre Dateien zu verwenden
        patcher = patch('backend.license_manager.LicenseManager._get_license_path')
        self.mock_get_license_path = patcher.start()
        self.mock_get_license_path.return_value = os.path.join(self.temp_dir.name, 'license.dat')
        self.addCleanup(patcher.stop)
        
        # Mock-Logger erstellen
        self.logger = MockLogger()
        
        # LicenseManager initialisieren
        self.license_manager = LicenseManager(self.logger)
    
    def tearDown(self):
        # Temporäres Verzeichnis aufräumen
        self.temp_dir.cleanup()
    
    def test_initialization(self):
        """Test, ob der LicenseManager korrekt initialisiert wird"""
        self.assertFalse(self.license_manager.license_valid)
        self.assertEqual(self.license_manager.license_type, "basic")
        self.assertIsNone(self.license_manager._license_key)
        self.assertIsNone(self.license_manager._license_expiry)
    
    def test_validate_license_key_format(self):
        """Test zur Validierung des Lizenzschlüsselformats"""
        # Gültiges Format
        self.assertTrue(self.license_manager._validate_license_key_format("RZGCS-PRO-1234-5678-9ABC-DEF0"))
        self.assertTrue(self.license_manager._validate_license_key_format("RZGCS-ENT-ABCD-EF12-3456-789A"))
        
        # Ungültiges Format
        self.assertFalse(self.license_manager._validate_license_key_format("invalid-key"))
        self.assertFalse(self.license_manager._validate_license_key_format("RZGCS-XXX-1234-5678-9ABC-DEF0"))
        self.assertFalse(self.license_manager._validate_license_key_format("RZGCS-PRO-1234-56789-ABC-DEF0"))
    
    def test_activate_license(self):
        """Test zur Aktivierung einer Lizenz"""
        # Mock die _get_machine_id-Methode
        with patch('backend.license_manager.LicenseManager._get_machine_id') as mock_get_machine_id:
            mock_get_machine_id.return_value = "test-machine-id"
            
            # Test für Professional-Lizenz
            result = self.license_manager.activate_license("RZGCS-PRO-1234-5678-9ABC-DEF0")
            self.assertTrue(result)
            self.assertTrue(self.license_manager.license_valid)
            self.assertEqual(self.license_manager.license_type, "professional")
            
            # Überprüfe Feature-Zugriff
            self.assertTrue(self.license_manager.is_feature_enabled("parameter_adjustment"))
            self.assertTrue(self.license_manager.is_feature_enabled("flight_planning"))
            self.assertFalse(self.license_manager.is_feature_enabled("angel_mode"))
    
    def test_enterprise_license_features(self):
        """Test für Enterprise-Lizenz-Features"""
        # Mock die _get_machine_id-Methode
        with patch('backend.license_manager.LicenseManager._get_machine_id') as mock_get_machine_id:
            mock_get_machine_id.return_value = "test-machine-id"
            
            # Test für Enterprise-Lizenz
            result = self.license_manager.activate_license("RZGCS-ENT-ABCD-EF12-3456-789A")
            self.assertTrue(result)
            self.assertTrue(self.license_manager.license_valid)
            self.assertEqual(self.license_manager.license_type, "enterprise")
            
            # Überprüfe Feature-Zugriff (insbesondere Angel Mode)
            self.assertTrue(self.license_manager.is_feature_enabled("angel_mode"))
            self.assertTrue(self.license_manager.is_feature_enabled("parameter_adjustment"))
            self.assertTrue(self.license_manager.is_feature_enabled("flight_planning"))

class TestLicenseController(unittest.TestCase):
    """Tests für den LicenseController"""
    
    def setUp(self):
        # Mock-Logger erstellen
        self.logger = MockLogger()
        
        # Mock LicenseManager
        self.license_manager = MagicMock(spec=LicenseManager)
        self.license_manager.license_valid = False
        self.license_manager.license_type = "basic"
        self.license_manager.is_feature_enabled.return_value = False
        
        # LicenseController initialisieren
        self.license_controller = LicenseController(self.license_manager, self.logger)
    
    def test_initialization(self):
        """Test, ob der LicenseController korrekt initialisiert wird"""
        self.assertFalse(self.license_controller.isLicensed)
        self.assertEqual(self.license_controller.licenseType, "basic")
    
    def test_activate_license(self):
        """Test zur Aktivierung einer Lizenz über den Controller"""
        # Mock die activate_license-Methode
        self.license_manager.activate_license.return_value = True
        self.license_manager.license_valid = True
        self.license_manager.license_type = "professional"
        
        # Aktiviere Lizenz
        result = self.license_controller.activateLicense("RZGCS-PRO-1234-5678-9ABC-DEF0")
        
        # Überprüfe Ergebnisse
        self.assertTrue(result)
        self.license_manager.activate_license.assert_called_once_with("RZGCS-PRO-1234-5678-9ABC-DEF0")
    
    def test_feature_access(self):
        """Test für Feature-Zugriffskontrolle"""
        # Mock die is_feature_enabled-Methode
        self.license_manager.is_feature_enabled.side_effect = lambda feature: feature in ["parameter_adjustment", "flight_planning"]
        
        # Überprüfe Feature-Zugriff
        self.assertTrue(self.license_controller.isFeatureEnabled("parameter_adjustment"))
        self.assertTrue(self.license_controller.isFeatureEnabled("flight_planning"))
        self.assertFalse(self.license_controller.isFeatureEnabled("angel_mode"))

# Haupttest-Runner
if __name__ == '__main__':
    unittest.main()
