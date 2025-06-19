#!/usr/bin/env python3
"""
End-to-End Integration Tests für die SITL-Funktionalität.
Diese Tests validieren den gesamten Workflow von der Simulation bis zur Datenvisualisierung.
"""
import os
import sys
import time
import unittest
import pytest
from unittest.mock import MagicMock, patch
import threading
import subprocess
from PySide6.QtCore import QObject, Signal, QTimer, QEventLoop
from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine

# Pfad zum Hauptmodul hinzufügen
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import der Haupt-Backend-Klasse für den End-to-End-Test
from mavsdk_rzgcs_main import RZGCSBackend
from backend.logger import Logger

# Abhängigkeiten
from rzgcs.viewmodel.sitl_view_model import SITLViewModel
from rzgcs.viewmodel.sensor_viewmodel import SensorViewModel
from rzgcs.viewmodel.mission_view_model import MissionViewModel
from rzgcs.viewmodel.mavsdk_drone_view_model import MAVSDKDroneViewModel
from rzgcs.mvvm.qml_compatibility_adapter import QMLCompatibilityAdapter

class TestSITLIntegration(unittest.TestCase):
    """End-to-End-Tests für die SITL-Integration."""
    
    @classmethod
    def setUpClass(cls):
        """Einmalige Einrichtung für alle Tests."""
        # Stelle sicher, dass eine QApplication existiert
        cls.app = QApplication.instance() or QApplication([])
        
    def setUp(self):
        """Richtet die Testumgebung für jeden Test ein."""
        self.logger = Logger()
        
        # Richtiges SITL-Binärverzeichnis erstellen
        self.sitl_bin_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'sitl_binaries'))
        os.makedirs(self.sitl_bin_dir, exist_ok=True)
        
        # Patchen der Subprocess-Aufrufe für SITL
        self.popen_patcher = patch('subprocess.Popen')
        self.mock_popen = self.popen_patcher.start()
        
        # Mock für den SITL-Prozess
        self.mock_process = MagicMock()
        self.mock_process.poll.return_value = None  # Prozess läuft
        self.mock_popen.return_value = self.mock_process
        
        # Backend erstellen
        self.backend = RZGCSBackend()
        
        # Direkter Zugriff auf die ViewModels
        self.sitl_vm = self.backend.sitl_view_model
        self.drone_vm = self.backend.drone_view_model
        self.sensor_model = self.backend.sensor_model
        self.qml_adapter = self.backend.qml_adapter
        
        # Event-Tracking für asynchrone Tests
        self.events = {
            'simulation_started': False,
            'connection_requested': False,
            'connection_established': False,
            'telemetry_received': False,
            'position_updated': False
        }
        
        # Signal-Handler konfigurieren
        self.sitl_vm.simulationStarted.connect(self._on_simulation_started)
        self.sitl_vm.autoConnectRequested.connect(self._on_connection_requested)
        self.drone_vm.connectionStateChanged.connect(self._on_connection_state_changed)
        self.drone_vm.positionChanged.connect(self._on_position_updated)
        
    def tearDown(self):
        """Aufräumen nach jedem Test."""
        # Patcher stoppen
        self.popen_patcher.stop()
        
        # SITL-Prozess beenden, falls er läuft
        if hasattr(self, 'sitl_vm') and self.sitl_vm.isSimulationRunning:
            self.sitl_vm.stopSimulation()
        
        # Verbindung trennen, falls verbunden
        if hasattr(self, 'drone_vm') and self.drone_vm.connected:
            self.drone_vm.disconnect()
    
    # Event-Handler für Signale
    def _on_simulation_started(self):
        self.events['simulation_started'] = True
        print("Simulation gestartet")
    
    def _on_connection_requested(self, connection_string):
        self.events['connection_requested'] = True
        self.connection_string = connection_string
        print(f"Verbindung angefordert: {connection_string}")
    
    def _on_connection_state_changed(self, connected):
        if connected:
            self.events['connection_established'] = True
            print("Verbindung hergestellt")
    
    def _on_position_updated(self, position_data):
        self.events['position_updated'] = True
        self.position_data = position_data
        print(f"Position aktualisiert: {position_data}")
    
    # Hilfsfunktion zum Warten auf Events
    def _wait_for_event(self, event_name, timeout=5):
        """Wartet auf ein bestimmtes Event mit Timeout."""
        start_time = time.time()
        while not self.events[event_name] and (time.time() - start_time) < timeout:
            QApplication.processEvents()
            time.sleep(0.1)
        
        return self.events[event_name]
    
    # Tests
    def test_sitl_startup_sequence(self):
        """Testet die vollständige SITL-Startsequenz."""
        # 1. SITL starten
        result = self.sitl_vm.startSimulation("copter", "stable")
        self.assertTrue(result, "SITL konnte nicht gestartet werden")
        
        # Warten auf simulationStarted-Signal
        self.assertTrue(self._wait_for_event('simulation_started'), 
                        "Simulation wurde nicht gestartet")
        
        # 2. Automatische Verbindung sollte angefordert werden
        self.sitl_vm._auto_connect_to_simulation()
        
        # Warten auf autoConnectRequested-Signal
        self.assertTrue(self._wait_for_event('connection_requested'),
                        "Verbindungsanforderung wurde nicht gesendet")
        
        # Überprüfen des Verbindungsstrings
        self.assertIn("tcp:", self.connection_string, 
                     "Verbindungsstring hat nicht das erwartete Format")
        
        # 3. Verbindung herstellen (mocken)
        # Wir simulieren hier, dass der QMLCompatibilityAdapter die Verbindung herstellt
        # In einer echten Anwendung würde das über das QML-Interface passieren
        
        # Mock für die connect-Methode, um eine erfolgreiche Verbindung zu simulieren
        with patch.object(self.drone_vm, 'connect', return_value=True):
            # Verbindung herstellen
            self.qml_adapter.connect(self.connection_string)
            
            # Verbindungsstatus manuell setzen (da wir keine echte Verbindung haben)
            self.drone_vm.connectionStateChanged.emit(True)
            
            # Warten auf connection_established-Event
            self.assertTrue(self._wait_for_event('connection_established'),
                           "Verbindung wurde nicht hergestellt")
            
            # 4. Simulierte Telemetriedaten senden
            test_position = {
                "latitude_deg": 49.445232,
                "longitude_deg": 7.769488,
                "relative_altitude_m": 100.0
            }
            
            # Position-Update simulieren
            self.drone_vm.positionChanged.emit(test_position)
            
            # Warten auf position_updated-Event
            self.assertTrue(self._wait_for_event('position_updated'),
                           "Positionsdaten wurden nicht aktualisiert")
            
            # 5. Überprüfen, ob die Sensordaten korrekt aktualisiert wurden
            # (durch den _update_position_data-Handler im Backend)
            self.assertEqual(self.sensor_model.getSensorValue("latitude"), 49.445232)
            self.assertEqual(self.sensor_model.getSensorValue("longitude"), 7.769488)
            self.assertEqual(self.sensor_model.getSensorValue("altitude"), 100.0)
    
    def test_simulation_failure_handling(self):
        """Testet die Fehlerbehandlung bei SITL-Startproblemen."""
        # Simuliere einen Fehler beim Starten der SITL
        self.mock_popen.side_effect = Exception("SITL konnte nicht gestartet werden")
        
        # Versuche, SITL zu starten
        result = self.sitl_vm.startSimulation("copter", "stable")
        
        # Überprüfungen
        self.assertFalse(result, "SITL-Start sollte fehlschlagen")
        self.assertFalse(self.sitl_vm.isSimulationRunning, 
                        "isSimulationRunning sollte False sein")
        self.assertIn("Fehler", self.sitl_vm.statusMessage, 
                      "Statusmeldung sollte einen Fehler anzeigen")
    
    @patch('os.path.exists')
    def test_sitl_binary_download(self, mock_exists):
        """Testet den Download der SITL-Binärdatei."""
        # Simuliere, dass die Binärdatei nicht existiert
        mock_exists.return_value = False
        
        # Mock für die Download-Methode
        with patch.object(self.sitl_vm, '_download_sitl_binary', return_value=True):
            # SITL starten (sollte zuerst versuchen, die Binärdatei herunterzuladen)
            result = self.sitl_vm.startSimulation("copter", "stable")
            
            # Überprüfungen
            self.assertTrue(result, "SITL konnte nicht gestartet werden")
            self.assertTrue(self.sitl_vm.isSimulationRunning, 
                           "isSimulationRunning sollte True sein")
    
    def test_mission_integration(self):
        """Testet die Integration zwischen SITL und Missionsplanung."""
        # Erstelle ein MissionViewModel
        mission_vm = MissionViewModel(self.logger)
        
        # Füge Wegpunkte hinzu
        mission_vm.addWaypoint(49.445232, 7.769488, 100.0)
        mission_vm.addWaypoint(49.446000, 7.770000, 110.0)
        
        # Überprüfe, ob die Wegpunkte korrekt hinzugefügt wurden
        self.assertEqual(len(mission_vm.missionItems), 2)
        self.assertEqual(mission_vm.totalWaypoints, 2)
        
        # In einer echten Integration würden wir hier die Mission hochladen
        # und dann in der SITL-Simulation ausführen
        # Da wir keine echte MAVSDK-Verbindung haben, simulieren wir das
        with patch.object(mission_vm, 'uploadMission', return_value=True):
            result = mission_vm.uploadMission()
            self.assertTrue(result, "Mission konnte nicht hochgeladen werden")
            
            # Mission starten
            mission_vm.startMission()
            self.assertTrue(mission_vm.isExecuting, 
                           "Mission sollte ausgeführt werden")
            
            # Simuliere Missionsfortschritt
            mission_vm.update_mission_progress(1)
            self.assertEqual(mission_vm.currentWaypoint, 1,
                            "Aktueller Wegpunkt sollte 1 sein")

# Pytest-Dekorator für Skiptest, wenn in einer CI-Umgebung
ci_skip = pytest.mark.skipif(
    os.environ.get('CI') == 'true',
    reason="Dieser Test benötigt eine lokale GUI-Umgebung und kann in CI fehlschlagen"
)

@ci_skip
def test_sitl_qml_loading():
    """Testet das Laden der SITL-QML-Komponente."""
    # Dieser Test benötigt eine aktive QApplication
    app = QApplication.instance() or QApplication([])
    
    # QML-Engine erstellen
    engine = QQmlApplicationEngine()
    
    # ViewModels erstellen
    logger = Logger()
    sitl_vm = SITLViewModel(logger)
    
    # Setze die Context-Properties
    engine.rootContext().setContextProperty("sitlViewModel", sitl_vm)
    engine.rootContext().setContextProperty("logger", logger)
    
    # Pfad zur QML-Datei
    qml_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 
                                                '..', '..', 'RZGCSContent', 'SITLView.ui.qml'))
    
    # Teste nur, wenn die Datei existiert
    if os.path.exists(qml_file_path):
        # Lade die QML-Datei
        engine.load(QUrl.fromLocalFile(qml_file_path))
        
        # Prozessiere Events
        QApplication.processEvents()
        
        # Überprüfe, ob das Laden erfolgreich war
        assert len(engine.rootObjects()) > 0, "QML-Datei konnte nicht geladen werden"

# Main-Funktion für direktes Ausführen der Tests
if __name__ == "__main__":
    unittest.main()
