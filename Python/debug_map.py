#!/usr/bin/env python
"""
Debugging-Skript für die RZGCS-Kartenansicht
Dieses Skript testet die Komponenten einzeln, um präzise Fehlermeldungen zu erhalten
"""

import sys
import os
import traceback
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel
from PySide6.QtCore import Qt

# Spezieller Debug-Logger
class DebugLogger:
    def __init__(self, log_file="map_debug.log"):
        self.log_file = log_file
        # Logdatei leeren/erstellen
        with open(self.log_file, "w") as f:
            f.write(f"=== RZGCS Map Debug Log ===\n\n")
    
    def log(self, message):
        print(f"DEBUG: {message}")
        try:
            with open(self.log_file, "a") as f:
                f.write(f"{message}\n")
        except Exception as e:
            print(f"Fehler beim Schreiben ins Log: {str(e)}")

# Logger initialisieren
logger = DebugLogger()

def check_environment():
    """Prüft die Umgebungsvariablen und Python-Version"""
    logger.log(f"Python Version: {sys.version}")
    logger.log(f"Executable: {sys.executable}")
    logger.log(f"Pfad: {os.getcwd()}")
    
    # Prüfe Qt-Module
    try:
        from PySide6 import __version__ as pyside_version
        logger.log(f"PySide6 Version: {pyside_version}")
    except ImportError:
        logger.log("PySide6 ist nicht installiert!")
        return False
    
    # Prüfe PySide6.QtWebEngine
    try:
        from PySide6 import QtWebEngineWidgets
        logger.log("QtWebEngineWidgets ist verfügbar")
    except ImportError as e:
        logger.log(f"QtWebEngineWidgets ist NICHT verfügbar: {str(e)}")
    
    # Prüfe auf erforderliche Dateien
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    map_html_path = os.path.join(base_dir, 'RZGCSContent', 'cesium', 'simple_3d_map.html')
    logger.log(f"Suche nach Karten-HTML-Datei: {map_html_path}")
    if os.path.exists(map_html_path):
        logger.log("Karten-HTML-Datei gefunden")
    else:
        logger.log("Karten-HTML-Datei NICHT gefunden!")
    
    return True

def test_simple_map_view():
    """Testet unsere vereinfachte Kartenansicht"""
    logger.log("Teste SimpleMapView...")
    try:
        from backend.simple_map_view import SimpleMapView
        logger.log("SimpleMapView-Modul erfolgreich importiert")
        
        # Versuch, die Klasse zu instanziieren
        app = QApplication.instance() or QApplication(sys.argv)
        test_widget = SimpleMapView()
        logger.log("SimpleMapView erfolgreich erstellt")
        
        # Test der API
        test_widget.update_drone_position(51.505600, 7.452400, 100.0)
        logger.log("Drohnenposition erfolgreich aktualisiert")
        
        return True
    except Exception as e:
        logger.log(f"Fehler beim Testen von SimpleMapView: {str(e)}")
        logger.log(traceback.format_exc())
        return False

def test_webengine():
    """Testet die WebEngine-Komponente separat"""
    logger.log("Teste WebEngine-Komponente...")
    try:
        from PySide6.QtWebEngineWidgets import QWebEngineView
        from PySide6.QtCore import QUrl
        
        # Versuche, die WebEngine zu initialisieren
        app = QApplication.instance() or QApplication(sys.argv)
        web_view = QWebEngineView()
        logger.log("QWebEngineView erfolgreich erstellt")
        
        # Lade eine einfache HTML-Seite
        html = "<html><body><h1>WebEngine Test</h1><p>Wenn dieser Text angezeigt wird, funktioniert WebEngine.</p></body></html>"
        web_view.setHtml(html)
        logger.log("HTML erfolgreich in WebEngine geladen")
        
        # Zeige das Fenster kurz an
        main_window = QMainWindow()
        main_window.setCentralWidget(web_view)
        main_window.setWindowTitle("WebEngine Test")
        main_window.resize(800, 600)
        main_window.show()
        
        logger.log("WebEngine-Fenster angezeigt")
        return True
    except Exception as e:
        logger.log(f"Fehler beim Testen von WebEngine: {str(e)}")
        logger.log(traceback.format_exc())
        return False

def test_flight_map_view():
    """Testet die FlightMapView-Komponente"""
    logger.log("Teste FlightMapView...")
    try:
        from backend.flight_map_bridge import FlightMapView
        
        # Versuch, die Klasse zu instanziieren
        app = QApplication.instance() or QApplication(sys.argv)
        test_widget = FlightMapView()
        logger.log("FlightMapView erfolgreich erstellt")
        
        # Test der API
        test_widget.update_drone_position(51.505600, 7.452400, 100.0)
        logger.log("Drohnenposition erfolgreich aktualisiert")
        
        return True
    except Exception as e:
        logger.log(f"Fehler beim Testen von FlightMapView: {str(e)}")
        logger.log(traceback.format_exc())
        return False

def main():
    """Hauptfunktion für den Debug-Prozess"""
    logger.log("=== Starte RZGCS Map Debugging ===\n")
    
    # Prüfe Umgebung
    if not check_environment():
        logger.log("Umgebungsprüfung fehlgeschlagen!")
        return
    
    # Teste SimpleMapView
    simple_map_result = test_simple_map_view()
    logger.log(f"SimpleMapView Test: {'ERFOLGREICH' if simple_map_result else 'FEHLGESCHLAGEN'}\n")
    
    # Teste WebEngine
    webengine_result = test_webengine()
    logger.log(f"WebEngine Test: {'ERFOLGREICH' if webengine_result else 'FEHLGESCHLAGEN'}\n")
    
    # Teste FlightMapView
    flight_map_result = test_flight_map_view()
    logger.log(f"FlightMapView Test: {'ERFOLGREICH' if flight_map_result else 'FEHLGESCHLAGEN'}\n")
    
    logger.log("=== Ende des Debugging-Prozesses ===\n")
    logger.log(f"Gesamtergebnis: {' '.join(['SimpleMapView: ' + ('\u2713' if simple_map_result else '\u2717'), 'WebEngine: ' + ('\u2713' if webengine_result else '\u2717'), 'FlightMapView: ' + ('\u2713' if flight_map_result else '\u2717')])}")

if __name__ == "__main__":
    # Erstelle eine QApplication zuerst, falls nicht vorhanden
    app = QApplication.instance() or QApplication(sys.argv)
    
    try:
        main()
        
        # Warte kurz, damit die Fenster angezeigt werden können
        import time
        time.sleep(3)
    except Exception as e:
        logger.log(f"Kritischer Fehler: {str(e)}")
        logger.log(traceback.format_exc())
    
    sys.exit(0)
