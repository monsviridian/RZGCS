# tests/test_3d_map_standalone.py
import unittest
import os
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QTest
import pytest

class TestStandaloneMap(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Initialize test environment"""
        cls.app = QApplication.instance() or QApplication(sys.argv)
        
    def test_map_initialization(self):
        """Test map window initialization"""
        # Import here to avoid Qt initialization issues
        from standalone_map import MapWindow
        
        try:
            window = MapWindow()
            window.show()
            QTest.qWait(1000)  # Wait for window to initialize
            self.assertTrue(window.isVisible())
            window.close()
            return True
        except Exception as e:
            self.fail(f"Map window initialization failed: {str(e)}")
            return False

# This allows running with pytest and getting coverage reports
if __name__ == '__main__':
    unittest.main()