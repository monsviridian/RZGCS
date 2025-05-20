"""
UI-Komponententests für die RZ Ground Control Station.
"""
import pytest
import sys
import os
from unittest.mock import MagicMock, patch
from PySide6.QtCore import QUrl, QObject, Signal, Slot, Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QWidget
from PySide6.QtQml import QQmlApplicationEngine, QQmlComponent

# Korrekte Pfadangaben für Import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestUIComponents:
    """Test-Suite für die UI-Komponenten der RZ Ground Control Station."""
    
    @pytest.fixture
    def qml_component_loader(self, app, qml_engine):
        """Fixture zum Laden von QML-Komponenten für Tests."""
        def _load_component(file_path):
            # Absoluter Pfad zur QML-Datei
            abs_path = os.path.abspath(os.path.join(
                os.path.dirname(__file__), '..', '..', 'RZGCSContent', file_path
            ))
            url = QUrl.fromLocalFile(abs_path)
            
            # Komponentenerstellung
            component = QQmlComponent(qml_engine, url)
            if component.status() != QQmlComponent.Status.Ready:
                print(f"Fehler beim Laden der Komponente: {component.errorString()}")
                return None
            
            # Objekterstellung
            obj = component.create()
            if obj is None:
                print(f"Fehler beim Erstellen des Objekts: {component.errorString()}")
                return None
                
            return obj
        
        return _load_component
    
    def test_preflight_view_loads(self, qml_component_loader):
        """Testet, ob die PreflightView korrekt geladen wird."""
        # Act
        preflight_view = qml_component_loader("PreflightView.ui.qml")
        
        # Assert
        assert preflight_view is not None
        
    def test_store_view_loads(self, qml_component_loader):
        """Testet, ob die StoreView korrekt geladen wird."""
        # Act
        store_view = qml_component_loader("StoreView.ui.qml")
        
        # Assert
        assert store_view is not None
        
    def test_flight_view_loads(self, qml_component_loader):
        """Testet, ob die FlightView korrekt geladen wird."""
        # Act
        flight_view = qml_component_loader("FlightView.ui.qml")
        
        # Assert
        assert flight_view is not None
        
    def test_sensor_view_loads(self, qml_component_loader):
        """Testet, ob die SensorView korrekt geladen wird."""
        # Act
        sensor_view = qml_component_loader("SensorView.ui.qml")
        
        # Assert
        assert sensor_view is not None

    @pytest.mark.skipif(os.environ.get('CI') == 'true', 
                       reason="Interaktive Tests werden in CI-Umgebungen übersprungen")
    def test_menu_tab_interaction(self, qml_component_loader):
        """Testet die Interaktion mit den Menü-Tabs."""
        # Arrange
        menu_tab = qml_component_loader("MenuTab.ui.qml")
        assert menu_tab is not None
        
        # Act - Simulieren eines Klicks
        with patch.object(menu_tab, 'clicked') as mock_clicked:
            # Führe den Klick durch
            QTest.mouseClick(menu_tab, Qt.LeftButton, Qt.NoModifier, QPoint(10, 10))
            
            # Assert
            mock_clicked.emit.assert_called_once()

    def test_parameter_view_model(self, app):
        """Testet das ParameterViewModel."""
        # Import hier, damit QApplication bereits existiert
        from RZGCSContent.ParameterViewModel import ParameterViewModel
        
        # Arrange & Act
        model = ParameterViewModel()
        
        # Assert
        assert model is not None
        
        # Überprüfen der Signale und Slots
        assert hasattr(model, 'parametersLoaded')
        assert hasattr(model, 'loadParameters')
        assert hasattr(model, 'setParameterValue')

    def test_sensor_view_model(self, app):
        """Testet das SensorViewModel."""
        # Import hier, damit QApplication bereits existiert
        from RZGCSContent.SensorViewModel import SensorViewModel
        
        # Arrange & Act
        model = SensorViewModel()
        
        # Assert
        assert model is not None
        
        # Test der Eigenschaften und Methoden
        assert hasattr(model, 'roll')
        assert hasattr(model, 'pitch')
        assert hasattr(model, 'yaw')
        assert hasattr(model, 'updateAttitude')
