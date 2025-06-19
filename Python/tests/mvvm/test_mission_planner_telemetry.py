#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test für die verbesserte Telemetrie-Funktionalität in MissionPlannerStyle
"""

import os
import sys
import unittest
import time
from unittest.mock import MagicMock, patch

# Pfad für die Importe hinzufügen
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from rzgcs.viewmodel.mission_planner_style import MissionPlannerStyle


class TestMissionPlannerTelemetry(unittest.TestCase):
    """Tests für die kontinuierliche Telemetrie-Übertragung im MissionPlannerStyle ViewModel"""

    def setUp(self):
        """Setup für jeden Test"""
        self.mission_planner = MissionPlannerStyle()
        # Mock das Signal, um zu überprüfen, ob es aufgerufen wurde
        self.mission_planner.telemetryUpdated = MagicMock()

    def tearDown(self):
        """Cleanup nach jedem Test"""
        # Sicherstellen, dass der Thread beendet wird (falls er läuft)
        if hasattr(self.mission_planner, "_telemetry_thread") and self.mission_planner._telemetry_thread:
            self.mission_planner._telemetry_thread = None

    def test_telemetry_updates_when_disarmed(self):
        """Testen, ob Telemetriedaten auch im disarmed-Zustand gesendet werden"""
        # Mission Planner verbinden und starten
        with patch.object(self.mission_planner, '_start_telemetry_thread') as mock_start:
            self.mission_planner.connect("udp://:14550")
            mock_start.assert_called_once()

        # Sicherstellen, dass der Zustand auf "nicht armiert" gesetzt ist
        self.mission_planner._armed = False

        # Manuell die Update-Funktion aufrufen (Simulation des Thread-Verhaltens)
        self.mission_planner._update_telemetry()
        
        # Überprüfen, ob das telemetryUpdated-Signal mindestens einmal aufgerufen wurde
        self.mission_planner.telemetryUpdated.emit.assert_called()

    def test_vehicle_state_updates_when_disarmed(self):
        """Testen, ob Fahrzeugstatusdaten auch im disarmed-Zustand aktualisiert werden"""
        # Mission Planner verbinden
        with patch.object(self.mission_planner, '_start_telemetry_thread'):
            self.mission_planner.connect("udp://:14550")

        # Sicherstellen, dass der Zustand auf "nicht armiert" gesetzt ist
        self.mission_planner._armed = False
        
        # Speichern der ursprünglichen Werte
        original_roll = self.mission_planner._roll
        original_pitch = self.mission_planner._pitch
        
        # Manuell die Fahrzeugstatus-Update-Funktion aufrufen
        self.mission_planner._update_vehicle_state()
        
        # Überprüfen, ob sich die Roll- und Pitch-Werte geändert haben
        # Dies sollte passieren, da die Methode auch im disarmed-Zustand kleine Bewegungen simuliert
        self.assertNotEqual(original_roll, self.mission_planner._roll, 
                           "Roll-Wert sollte sich auch im disarmed-Zustand ändern")
        self.assertNotEqual(original_pitch, self.mission_planner._pitch, 
                           "Pitch-Wert sollte sich auch im disarmed-Zustand ändern")

    def test_battery_updates_when_disarmed(self):
        """Testen, ob Batterieinformationen auch im disarmed-Zustand aktualisiert werden"""
        # Mission Planner verbinden
        with patch.object(self.mission_planner, '_start_telemetry_thread'):
            self.mission_planner.connect("udp://:14550")

        # Sicherstellen, dass der Zustand auf "nicht armiert" gesetzt ist
        self.mission_planner._armed = False
        
        # Speichern des ursprünglichen Werts
        original_battery = self.mission_planner._battery
        
        # Manuell die Update-Funktion aufrufen
        self.mission_planner._update_telemetry()
        
        # Sicherstellen, dass das telemetryUpdated-Signal Batterieinformationen enthält
        args, _ = self.mission_planner.telemetryUpdated.emit.call_args
        self.assertIn('battery', args[0], "Batterieinformationen fehlen in den Telemetriedaten")
        self.assertGreater(args[0]['battery'], 0, "Batteriewert sollte größer als 0 sein")


if __name__ == '__main__':
    unittest.main()
