#!/usr/bin/env python
"""
Test-Runner für die RZ Ground Control Station.
Führt alle Tests aus und erstellt einen Bericht.
"""
import os
import sys
import argparse
import pytest
import datetime
import webbrowser
import shutil

def ensure_report_dir():
    """Stellt sicher, dass das Reports-Verzeichnis existiert."""
    report_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_reports')
    if not os.path.exists(report_dir):
        os.makedirs(report_dir)
    return report_dir

def main():
    """Hauptfunktion zum Ausführen der Tests."""
    parser = argparse.ArgumentParser(description='RZ Ground Control Station Test Runner')
    parser.add_argument('--unit-only', action='store_true', help='Nur Unit-Tests ausführen')
    parser.add_argument('--integration-only', action='store_true', help='Nur Integrationstests ausführen')
    parser.add_argument('--ui-only', action='store_true', help='Nur UI-Tests ausführen')
    parser.add_argument('--security', action='store_true', help='Nur Sicherheitstests ausführen')
    parser.add_argument('--performance', action='store_true', help='Nur Performance-Tests ausführen')
    parser.add_argument('--no-report', action='store_true', help='Keinen Bericht erstellen')
    parser.add_argument('--verbose', '-v', action='store_true', help='Ausführliche Ausgabe')
    parser.add_argument('--open-report', action='store_true', help='Bericht nach dem Test öffnen')
    args = parser.parse_args()

    # Basisverzeichnis für Tests und Reports
    tests_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tests')
    report_dir = ensure_report_dir()
    
    # Aktuelles Datum für den Berichtsnamen
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    html_report = os.path.join(report_dir, f'test_report_{timestamp}.html')
    xml_report = os.path.join(report_dir, f'test_results_{timestamp}.xml')
    
    # Standard-Argumentliste
    pytest_args = [tests_dir]
    
    # Verbositätseinstellungen
    if args.verbose:
        pytest_args.append('-v')
    
    # Testauswahl basierend auf Argumenten
    if args.unit_only:
        pytest_args.extend(['-k', 'test_mavlink_connector or test_parameter_model or test_mavlink_simulator and not test_performance and not test_security'])
    elif args.integration_only:
        pytest_args.extend(['-k', 'test_integration'])
    elif args.ui_only:
        pytest_args.extend(['-k', 'test_ui_components'])
    elif args.security:
        pytest_args.extend(['-k', 'test_security'])
    elif args.performance:
        pytest_args.extend(['-k', 'test_performance'])
    
    # Berichtseinstellungen - immer Berichte erstellen, es sei denn, --no-report ist gesetzt
    if not args.no_report:
        # Prüfen, ob das pytest-html Plugin installiert ist
        try:
            import pytest_html
            pytest_args.extend(['--html', html_report, '--self-contained-html'])
        except ImportError:
            print("WARNUNG: pytest-html nicht installiert. HTML-Bericht wird nicht erstellt.")
            print("Installieren Sie es mit: pip install pytest-html")
        
        # JUnit XML-Bericht erstellen
        pytest_args.extend(['--junitxml', xml_report])
    
    # Tests ausführen
    print("RZ Ground Control Station Test Runner")
    print("=======================================")
    print(f"Ausführen der Tests in: {tests_dir}")
    if not args.no_report:
        print(f"HTML-Bericht wird erstellt unter: {html_report}")
        print(f"XML-Bericht wird erstellt unter: {xml_report}")
    
    # Kopiere die conftest.py in das gleiche Verzeichnis wie die Testskripte,
    # falls sie noch nicht da ist
    conftest_path = os.path.join(tests_dir, 'conftest.py')
    if not os.path.exists(conftest_path):
        shutil.copy(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tests', 'conftest.py'), conftest_path)
    
    # Tests ausführen
    exit_code = pytest.main(pytest_args)
    
    # Bericht öffnen, wenn gewünscht und er existiert
    if args.open_report and not args.no_report and os.path.exists(html_report):
        try:
            webbrowser.open(f'file://{os.path.abspath(html_report)}')
            print(f"Testbericht wurde im Browser geöffnet.")
        except Exception as e:
            print(f"Konnte den Bericht nicht im Browser öffnen: {e}")
    
    # Statuszusammenfassung
    if exit_code == 0:
        print("\n[ERFOLG] Alle Tests wurden erfolgreich ausgeführt!")
    else:
        print(f"\n[FEHLER] Tests wurden mit Exit-Code {exit_code} abgeschlossen. Sehen Sie den Bericht für Details.")
    
    return exit_code

if __name__ == "__main__":
    sys.exit(main())
