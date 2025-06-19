#!/usr/bin/env python3
"""
Tests für das Mission ViewModel.
Diese Tests validieren die Funktionalität des Missionsplanungsmoduls.
"""
import os
import sys
import unittest
import pytest
from unittest.mock import MagicMock, patch
from PySide6.QtCore import QObject, Signal

# Pfad zum Hauptmodul hinzufügen
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# MissionViewModel importieren
from rzgcs.viewmodel.mission_view_model import MissionViewModel

class MockLogger:
    """Mock für den Logger."""
    def __init__(self):
        self.logs = []
    
    def addLog(self, message):
        self.logs.append(message)
        print(f"Log: {message}")  # Für bessere Testausgaben

class TestMissionViewModel(unittest.TestCase):
    """Testet das Mission ViewModel."""
    
    def setUp(self):
        """Richtet die Testumgebung ein."""
        self.logger = MockLogger()
        self.mission_vm = MissionViewModel(self.logger)
    
    def test_init(self):
        """Testet, ob das ViewModel korrekt initialisiert wird."""
        self.assertFalse(self.mission_vm.isExecuting)
        self.assertEqual(self.mission_vm.missionName, "Neue Mission")
        self.assertEqual(self.mission_vm.currentWaypoint, 0)
        self.assertEqual(self.mission_vm.totalWaypoints, 0)
        self.assertEqual(len(self.mission_vm.missionItems), 0)
    
    def test_signals_existence(self):
        """Testet, ob alle erforderlichen Signale existieren."""
        expected_signals = [
            'missionLoadedSignal',
            'missionUpdatedSignal',
            'missionItemAddedSignal',
            'missionItemRemovedSignal',
            'missionUploadedSignal',
            'missionDownloadedSignal',
            'missionExecutionStatusSignal'
        ]
        for signal_name in expected_signals:
            self.assertTrue(hasattr(self.mission_vm, signal_name), f"Signal {signal_name} fehlt")
    
    def test_add_waypoint(self):
        """Testet das Hinzufügen eines Wegpunkts."""
        # Wegpunkt hinzufügen
        result = self.mission_vm.addWaypoint(49.445232, 7.769488, 100.0)
        
        # Überprüfungen
        self.assertTrue(result)
        self.assertEqual(len(self.mission_vm.missionItems), 1)
        self.assertEqual(self.mission_vm.totalWaypoints, 1)
        
        # Inhalt des Wegpunkts überprüfen
        waypoint = self.mission_vm.missionItems[0]
        self.assertEqual(waypoint["type"], "waypoint")
        self.assertEqual(waypoint["latitude"], 49.445232)
        self.assertEqual(waypoint["longitude"], 7.769488)
        self.assertEqual(waypoint["altitude"], 100.0)
    
    def test_remove_waypoint(self):
        """Testet das Entfernen eines Wegpunkts."""
        # Wegpunkt hinzufügen und dann entfernen
        self.mission_vm.addWaypoint(49.445232, 7.769488, 100.0)
        result = self.mission_vm.removeWaypoint(0)
        
        # Überprüfungen
        self.assertTrue(result)
        self.assertEqual(len(self.mission_vm.missionItems), 0)
        self.assertEqual(self.mission_vm.totalWaypoints, 0)
    
    def test_remove_waypoint_invalid_index(self):
        """Testet das Entfernen eines nicht existierenden Wegpunkts."""
        result = self.mission_vm.removeWaypoint(0)  # Keine Wegpunkte vorhanden
        self.assertFalse(result)
        
        # Wegpunkt hinzufügen
        self.mission_vm.addWaypoint(49.445232, 7.769488, 100.0)
        
        # Versuchen, einen nicht existierenden Index zu entfernen
        result = self.mission_vm.removeWaypoint(1)  # Index außerhalb des Bereichs
        self.assertFalse(result)
    
    def test_save_mission(self):
        """Testet das Speichern einer Mission."""
        filename = "test_mission.json"
        result = self.mission_vm.saveMission(filename)
        
        self.assertTrue(result)
        # In einer vollständigen Implementierung würden wir auch prüfen, ob die Datei existiert
    
    def test_load_mission(self):
        """Testet das Laden einer Mission."""
        filename = "test_mission.json"
        result = self.mission_vm.loadMission(filename)
        
        self.assertTrue(result)
        # In einer vollständigen Implementierung würden wir überprüfen, ob die Missionsdaten korrekt geladen wurden
    
    def test_upload_mission(self):
        """Testet das Hochladen einer Mission."""
        result = self.mission_vm.uploadMission()
        
        self.assertTrue(result)
        # In einer vollständigen Implementierung würden wir überprüfen, ob das Signal korrekt emittiert wurde
    
    def test_download_mission(self):
        """Testet das Herunterladen einer Mission."""
        result = self.mission_vm.downloadMission()
        
        self.assertTrue(result)
        # In einer vollständigen Implementierung würden wir überprüfen, ob das Signal korrekt emittiert wurde
    
    def test_mission_execution_control(self):
        """Testet die Steuerung der Missionsausführung (Start, Pause, Fortsetzen, Stopp)."""
        # Start
        start_result = self.mission_vm.startMission()
        self.assertTrue(start_result)
        self.assertTrue(self.mission_vm.isExecuting)
        
        # Pause
        pause_result = self.mission_vm.pauseMission()
        self.assertTrue(pause_result)
        self.assertFalse(self.mission_vm.isExecuting)
        
        # Fortsetzen
        resume_result = self.mission_vm.resumeMission()
        self.assertTrue(resume_result)
        self.assertTrue(self.mission_vm.isExecuting)
        
        # Stopp
        stop_result = self.mission_vm.stopMission()
        self.assertTrue(stop_result)
        self.assertFalse(self.mission_vm.isExecuting)
        self.assertEqual(self.mission_vm.currentWaypoint, 0)
    
    def test_goto_waypoint(self):
        """Testet den Wechsel zu einem bestimmten Wegpunkt."""
        # Mehrere Wegpunkte hinzufügen
        self.mission_vm.addWaypoint(49.445232, 7.769488, 100.0)
        self.mission_vm.addWaypoint(49.446000, 7.770000, 110.0)
        self.mission_vm.addWaypoint(49.447000, 7.771000, 120.0)
        
        # Zu einem bestimmten Wegpunkt wechseln
        result = self.mission_vm.gotoWaypoint(1)
        
        self.assertTrue(result)
        self.assertEqual(self.mission_vm.currentWaypoint, 1)
        
        # Zu einem nicht existierenden Wegpunkt wechseln
        result = self.mission_vm.gotoWaypoint(10)
        self.assertFalse(result)
    
    def test_update_mission_progress(self):
        """Testet die Aktualisierung des Missionsfortschritts."""
        # Mehrere Wegpunkte hinzufügen
        self.mission_vm.addWaypoint(49.445232, 7.769488, 100.0)
        self.mission_vm.addWaypoint(49.446000, 7.770000, 110.0)
        
        # Mission starten
        self.mission_vm.startMission()
        
        # Fortschritt aktualisieren
        self.mission_vm.update_mission_progress(1)
        
        self.assertEqual(self.mission_vm.currentWaypoint, 1)

# Main-Funktion für direktes Ausführen der Tests
if __name__ == "__main__":
    unittest.main()
