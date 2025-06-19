#!/usr/bin/env python3
"""
Testrunner für alle RZGCS-Tests
Führt alle Unit- und Integrationstests aus und gibt einen Bericht aus.
"""
import os
import sys
import unittest
import pytest
import argparse

def run_tests_with_unittest():
    """Führt alle Tests mit unittest aus."""
    print("\n=== Führe Tests mit unittest aus ===")
    # Alle Tests im aktuellen Verzeichnis finden und ausführen
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover(os.path.dirname(__file__), pattern='test_*.py')
    
    # Führe die Tests aus
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    # Gibt True zurück, wenn alle Tests erfolgreich waren
    return result.wasSuccessful()

def run_tests_with_pytest(verbose=True, coverage=False):
    """Führt alle Tests mit pytest aus."""
    print("\n=== Führe Tests mit pytest aus ===")
    args = ['-xvs'] if verbose else ['-xs']
    
    # Füge Coverage-Messung hinzu, wenn gewünscht
    if coverage:
        args.extend(['--cov=rzgcs', '--cov-report=term', '--cov-report=html'])
    
    # Führe Tests aus
    args.append(os.path.dirname(__file__))
    return pytest.main(args)

def main():
    """Hauptfunktion zum Ausführen der Tests."""
    parser = argparse.ArgumentParser(description='RZGCS Testrunner')
    parser.add_argument('--unittest', action='store_true', help='Führe Tests mit unittest aus')
    parser.add_argument('--pytest', action='store_true', help='Führe Tests mit pytest aus')
    parser.add_argument('--coverage', action='store_true', help='Erstelle Coverage-Bericht (nur mit pytest)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Ausführliche Ausgabe')
    
    args = parser.parse_args()
    
    # Standardmäßig beide Frameworks verwenden, wenn nichts angegeben wurde
    if not args.unittest and not args.pytest:
        args.unittest = True
        args.pytest = True
    
    success = True
    
    if args.unittest:
        unittest_success = run_tests_with_unittest()
        success = success and unittest_success
    
    if args.pytest:
        pytest_exit_code = run_tests_with_pytest(verbose=args.verbose, coverage=args.coverage)
        success = success and (pytest_exit_code == 0)
    
    # Ergebnisse anzeigen
    print("\n=== Testergebnisse ===")
    print(f"Status: {'ERFOLGREICH' if success else 'FEHLGESCHLAGEN'}")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
