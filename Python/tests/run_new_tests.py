#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script zum Ausführen aller neuen Tests für die aktuellen Änderungen
"""

import os
import sys
import unittest

# Pfad für die Importe hinzufügen
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))


if __name__ == '__main__':
    # Testpfad für das Auffinden der Tests
    test_path = os.path.abspath(os.path.dirname(__file__))
    
    # Erstelle Test-Suite für alle neuen Tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # MVVM Tests für die Telemetrie-Verbesserung
    try:
        mvvm_tests = loader.discover(os.path.join(test_path, "mvvm"), pattern="test_mission_planner_telemetry.py")
        suite.addTest(mvvm_tests)
        print("MVVM Telemetrie-Tests hinzugefügt")
    except Exception as e:
        print(f"Fehler beim Hinzufügen der MVVM Telemetrie-Tests: {e}")
    
    # QML Tests für den überarbeiteten ArtificialHorizon
    try:
        horizon_test = loader.discover(test_path, pattern="test_artificial_horizon.py")
        suite.addTest(horizon_test)
        print("Artificial Horizon Tests hinzugefügt")
    except Exception as e:
        print(f"Fehler beim Hinzufügen der Artificial Horizon Tests: {e}")
    
    # Runner für die Ausführung der Tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Ausgabe der Ergebnisse
    print("\n============ Testergebnisse ============")
    print(f"Ausgeführte Tests: {result.testsRun}")
    print(f"Erfolgreiche Tests: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Fehlgeschlagene Tests: {len(result.failures)}")
    print(f"Fehlerhafte Tests: {len(result.errors)}")
    
    # Exitcode basierend auf den Testergebnissen setzen
    sys.exit(len(result.failures) + len(result.errors))
