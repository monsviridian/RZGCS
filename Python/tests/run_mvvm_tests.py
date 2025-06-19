"""
Test-Runner für die MVVM-Architektur-Tests.

Führt alle Tests für die MVVM-Architektur aus und gibt eine Zusammenfassung aus.
"""

import unittest
import sys
import os

# Pfad zum Hauptverzeichnis hinzufügen, damit Module importiert werden können
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)  # Python-Verzeichnis
sys.path.insert(0, parent_dir)

# Import der Testmodule
from mvvm.test_view_models import TestMAVSDKDroneViewModel, TestSensorViewModel, TestSITLViewModel
from mvvm.test_models import TestMAVSDKConnectorMVVM, TestSITLController
from mvvm.test_integration import TestViewModelToModelIntegration, TestQMLIntegration, TestMVVMEndToEnd


def run_tests():
    """Führt alle Tests aus und gibt eine Zusammenfassung aus."""
    # Test-Suite erstellen
    test_suite = unittest.TestSuite()
    
    # ViewModels-Tests hinzufügen
    test_suite.addTest(unittest.makeSuite(TestMAVSDKDroneViewModel))
    test_suite.addTest(unittest.makeSuite(TestSensorViewModel))
    test_suite.addTest(unittest.makeSuite(TestSITLViewModel))
    
    # Models-Tests hinzufügen
    test_suite.addTest(unittest.makeSuite(TestMAVSDKConnectorMVVM))
    test_suite.addTest(unittest.makeSuite(TestSITLController))
    
    # Integrationstests hinzufügen
    test_suite.addTest(unittest.makeSuite(TestViewModelToModelIntegration))
    test_suite.addTest(unittest.makeSuite(TestQMLIntegration))
    test_suite.addTest(unittest.makeSuite(TestMVVMEndToEnd))
    
    # Tests ausführen
    test_runner = unittest.TextTestRunner(verbosity=2)
    test_result = test_runner.run(test_suite)
    
    # Zusammenfassung ausgeben
    print("\n=== MVVM-Architektur-Tests Zusammenfassung ===")
    print(f"Ausgeführte Tests: {test_result.testsRun}")
    print(f"Fehler: {len(test_result.errors)}")
    print(f"Fehlgeschlagen: {len(test_result.failures)}")
    
    # Rückgabewert für CI/CD-Pipelines
    return len(test_result.errors) + len(test_result.failures)


if __name__ == "__main__":
    # Befehlszeilenargumente verarbeiten
    verbose = "-v" in sys.argv or "--verbose" in sys.argv
    
    if verbose:
        print("=== MVVM-Architektur-Tests werden ausgeführt (verbose) ===")
        unittest.main(verbosity=2)
    else:
        print("=== MVVM-Architektur-Tests werden ausgeführt ===")
        sys.exit(run_tests())
