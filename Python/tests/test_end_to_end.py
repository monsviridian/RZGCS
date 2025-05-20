"""
End-to-End-Tests für die RZ Ground Control Station.
Diese Tests simulieren reale Benutzerszenarien und testen den gesamten Workflow.
"""
import pytest
import sys
import os
import time
from unittest.mock import MagicMock, patch
from PySide6.QtCore import QObject, Signal, Slot, QTimer, Qt, QPoint
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

# Korrekte Pfadangaben für Import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestEndToEnd:
    """End-to-End-Tests für die RZ Ground Control Station."""
    
    @pytest.fixture
    def main_app(self, app):
        """Fixture zum Starten der Hauptanwendung für Tests."""
        # Die Hauptanwendung importieren
        from main import MainApplication
        
        # Mock für Kommandozeilenargumente
        with patch('sys.argv', ['main.py', '--test-mode']):
            # Anwendung instanziieren
            main_app = MainApplication()
            
            # Warten, bis die Anwendung geladen ist
            def wait_for_app_load():
                QTimer.singleShot(1000, lambda: None)
            
            wait_for_app_load()
            
            yield main_app
            
            # Aufräumen nach dem Test
            main_app.cleanup()
    
    @pytest.mark.skipif(os.environ.get('CI') == 'true', 
                      reason="End-to-End-Tests werden in CI-Umgebungen übersprungen")
    def test_full_application_startup(self, main_app):
        """Testet den vollständigen Startvorgang der Anwendung."""
        # Assert - Überprüfen, ob die Hauptkomponenten initialisiert wurden
        assert main_app is not None
        assert main_app.engine is not None
        assert main_app.root_object is not None
    
    @pytest.mark.skipif(os.environ.get('CI') == 'true',
                      reason="End-to-End-Tests werden in CI-Umgebungen übersprungen")
    def test_tab_navigation(self, main_app):
        """Testet die Navigation zwischen den Tabs."""
        # Den Tab-Container finden
        tab_bar = None
        for child in main_app.root_object.children():
            if hasattr(child, 'currentIndex') and hasattr(child, 'count'):
                tab_bar = child
                break
        
        assert tab_bar is not None
        
        # Ausgangstab speichern
        initial_tab = tab_bar.currentIndex
        
        # Zwischen Tabs wechseln
        for i in range(tab_bar.count):
            tab_bar.currentIndex = i
            # Warten, um den Tab-Wechsel zu ermöglichen
            QTest.qWait(300)
            assert tab_bar.currentIndex == i
        
        # Zurück zum Ausgangstab
        tab_bar.currentIndex = initial_tab
    
    @pytest.mark.skipif(os.environ.get('CI') == 'true',
                      reason="End-to-End-Tests werden in CI-Umgebungen übersprungen")
    def test_store_view_interaction(self, main_app):
        """Testet Interaktionen mit der Store-Ansicht."""
        # Den Store-Tab auswählen
        tab_bar = None
        for child in main_app.root_object.children():
            if hasattr(child, 'currentIndex') and hasattr(child, 'count'):
                tab_bar = child
                break
        
        assert tab_bar is not None
        
        # Store-Tab-Index finden und auswählen
        store_tab_index = -1
        for i in range(tab_bar.count):
            tab_bar.currentIndex = i
            QTest.qWait(300)
            
            # Prüfen, ob dieser Tab die Store-Ansicht enthält
            if main_app.root_object.findChild(QObject, "storeView") is not None:
                store_tab_index = i
                break
        
        assert store_tab_index != -1, "Store-Tab nicht gefunden"
        
        # ComboBox für Modellauswahl finden
        model_selector = main_app.root_object.findChild(QObject, "modelSelector")
        assert model_selector is not None
        
        # Modell wechseln
        initial_index = model_selector.currentIndex
        new_index = (initial_index + 1) % model_selector.count
        model_selector.currentIndex = new_index
        
        # Prüfen, ob sich der Index geändert hat
        assert model_selector.currentIndex == new_index
    
    @pytest.mark.skipif(os.environ.get('CI') == 'true',
                      reason="End-to-End-Tests werden in CI-Umgebungen übersprungen")
    def test_connection_workflow(self, main_app):
        """Testet den Verbindungsworkflow mit einer simulierten Drohne."""
        # 1. Zur Preflight-Ansicht wechseln
        tab_bar = None
        for child in main_app.root_object.children():
            if hasattr(child, 'currentIndex') and hasattr(child, 'count'):
                tab_bar = child
                break
        
        assert tab_bar is not None
        
        # Preflight-Tab-Index finden und auswählen
        preflight_tab_index = -1
        for i in range(tab_bar.count):
            tab_bar.currentIndex = i
            QTest.qWait(300)
            
            # Prüfen, ob dieser Tab die Preflight-Ansicht enthält
            if main_app.root_object.findChild(QObject, "preflightView") is not None:
                preflight_tab_index = i
                break
        
        assert preflight_tab_index != -1, "Preflight-Tab nicht gefunden"
        
        # 2. Verbindungseinstellungen konfigurieren
        with patch('backend.mavlink_connector.MAVLinkConnector.connect', return_value=True):
            with patch('backend.mavlink_connector.MAVLinkConnector.is_connected', return_value=True):
                # Connect-Button finden
                connect_button = main_app.root_object.findChild(QObject, "connectButton")
                assert connect_button is not None
                
                # Verbindungsherstellung simulieren
                QTest.mouseClick(connect_button, Qt.LeftButton)
                QTest.qWait(500)
                
                # Prüfen, ob die Verbindung hergestellt wurde
                # (in der Regel durch Änderung des Verbindungsstatus in der UI erkennbar)
                status_text = main_app.root_object.findChild(QObject, "connectionStatus")
                assert status_text is not None
                assert "Connected" in status_text.text or "Verbunden" in status_text.text
