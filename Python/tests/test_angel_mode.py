# tests/test_angel_mode.py
import unittest
import sys
import os
from unittest.mock import MagicMock, patch
from PySide6.QtCore import QObject, Signal, Property

# Fu00fcge das Hauptverzeichnis zum Pfad hinzu, um relative Importe zu ermu00f6glichen
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.license_manager import LicenseManager
from backend.license_ui import LicenseController

class MockQMLItem(QObject):
    """Simuliert ein QML-Item fu00fcr Tests"""
    def __init__(self):
        super().__init__()
        self._is_feature_enabled = False
        self._visibility_changed = False
    
    def setProperty(self, name, value):
        if name == "isFeatureEnabled":
            self._is_feature_enabled = value
            return True
        return False
    
    def property(self, name):
        if name == "isFeatureEnabled":
            return self._is_feature_enabled
        return None

class MockLogger(QObject):
    """Mock-Logger fu00fcr Tests"""
    def __init__(self):
        super().__init__()
        self.logs = []
    
    def addLog(self, message):
        self.logs.append(message)
        print(f"[LOG] {message}")

class TestAngelMode(unittest.TestCase):
    """Tests fu00fcr den Angel Mode mit Lizenzbeschru00e4nkung"""
    
    def setUp(self):
        # Mock-Logger erstellen
        self.logger = MockLogger()
        
        # LicenseManager initialisieren
        self.license_manager = LicenseManager(self.logger)
        
        # LicenseController initialisieren
        self.license_controller = LicenseController(self.license_manager, self.logger)
        
        # Mock AngelView QML-Element
        self.angel_view = MockQMLItem()
    
    def test_angel_mode_basic_license(self):
        """Test, ob Angel Mode mit Basic-Lizenz deaktiviert ist"""
        # Setze Basic-Lizenz (Standard)
        self.assertEqual(self.license_manager.license_type, "basic")
        
        # u00dcberpru00fcfe, ob Angel Mode deaktiviert ist
        self.assertFalse(self.license_controller.isFeatureEnabled("angel_mode"))
        
        # Simuliere QML-Binding
        self.angel_view.setProperty("isFeatureEnabled", 
                                    self.license_controller.isFeatureEnabled("angel_mode"))
        
        # u00dcberpru00fcfe, ob die Eigenschaft korrekt gesetzt wurde
        self.assertFalse(self.angel_view.property("isFeatureEnabled"))
    
    def test_angel_mode_professional_license(self):
        """Test, ob Angel Mode mit Professional-Lizenz deaktiviert ist"""
        # Mock die _get_machine_id-Methode
        with patch('backend.license_manager.LicenseManager._get_machine_id') as mock_get_machine_id:
            mock_get_machine_id.return_value = "test-machine-id"
            
            # Aktiviere Professional-Lizenz
            result = self.license_manager.activate_license("RZGCS-PRO-1234-5678-9ABC-DEF0")
            self.assertTrue(result)
            self.assertEqual(self.license_manager.license_type, "professional")
            
            # u00dcberpru00fcfe, ob Angel Mode deaktiviert ist
            self.assertFalse(self.license_controller.isFeatureEnabled("angel_mode"))
            
            # Simuliere QML-Binding
            self.angel_view.setProperty("isFeatureEnabled", 
                                        self.license_controller.isFeatureEnabled("angel_mode"))
            
            # u00dcberpru00fcfe, ob die Eigenschaft korrekt gesetzt wurde
            self.assertFalse(self.angel_view.property("isFeatureEnabled"))
    
    def test_angel_mode_enterprise_license(self):
        """Test, ob Angel Mode mit Enterprise-Lizenz aktiviert ist"""
        # Mock die _get_machine_id-Methode
        with patch('backend.license_manager.LicenseManager._get_machine_id') as mock_get_machine_id:
            mock_get_machine_id.return_value = "test-machine-id"
            
            # Aktiviere Enterprise-Lizenz
            result = self.license_manager.activate_license("RZGCS-ENT-ABCD-EF12-3456-789A")
            self.assertTrue(result)
            self.assertEqual(self.license_manager.license_type, "enterprise")
            
            # u00dcberpru00fcfe, ob Angel Mode aktiviert ist
            self.assertTrue(self.license_controller.isFeatureEnabled("angel_mode"))
            
            # Simuliere QML-Binding
            self.angel_view.setProperty("isFeatureEnabled", 
                                        self.license_controller.isFeatureEnabled("angel_mode"))
            
            # u00dcberpru00fcfe, ob die Eigenschaft korrekt gesetzt wurde
            self.assertTrue(self.angel_view.property("isFeatureEnabled"))

# Haupttest-Runner
if __name__ == '__main__':
    unittest.main()
