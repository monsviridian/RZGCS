#!/usr/bin/env python3
"""
RZGCS MAVSDK MVVM Startskript mit Material Style
Integriert die MVVM-Architektur mit korrekter Material-Style-Konfiguration
"""

import os
import sys
from pathlib import Path

# PySide6 importieren
import PySide6
from PySide6.QtCore import QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine, qmlRegisterType
from PySide6.QtQuickControls2 import QQuickStyle

# Importiere benötigte Module
from backend.logger import Logger
from backend.sensorviewmodel import SensorViewModel
from rzgcs.mvvm.viewmodel.mavsdk_drone_viewmodel import MAVSDKDroneViewModel

def main():
    """Hauptfunktion der Anwendung"""
    # Aktuelle Python-Version ausgeben
    print(f"Python-Version: {sys.version}")
    print(f"PySide6-Version: {PySide6.__version__}")
    
    # WICHTIG: Arbeitsverzeichnis korrekt setzen (muss vor allem anderen passieren)
    project_root = Path(__file__).resolve().parent.parent  # Gehe eine Ebene höher zum Hauptverzeichnis
    os.chdir(str(project_root))
    print(f"Arbeitsverzeichnis: {os.getcwd()}")
    
    # WICHTIG: Material Style für QML MUSS VOR der App-Erstellung gesetzt werden
    os.environ["QT_QUICK_CONTROLS_STYLE"] = "Material"
    QQuickStyle.setStyle("Material")
    
    # Anwendung erstellen
    app = QGuiApplication(sys.argv)
    
    # Logger initialisieren
    logger = Logger()
    logger.addLog("[INFO] Initialisiere RZGCS mit MAVSDK-MVVM-Integration (Material Style)")
    
    # Sensor-ViewModel erstellen
    sensor_model = SensorViewModel()
    
    # Drohnen-ViewModel erstellen (MVVM-Architektur)
    drone_view_model = MAVSDKDroneViewModel(logger)
    
    # Füge die von der QML-UI erwarteten Methoden hinzu, falls sie nicht vorhanden sind
    if not hasattr(drone_view_model, 'load_ports'):
        def load_ports():
            drone_view_model.refreshPorts()
        drone_view_model.load_ports = load_ports
    
    if not hasattr(drone_view_model, 'setPort'):
        def setPort(port_name):
            drone_view_model._selected_port = port_name
            logger.addLog(f"[INFO] Port ausgewählt: {port_name}")
        drone_view_model.setPort = setPort
    
    if not hasattr(drone_view_model, 'connect'):
        def connect(connection_string):
            # Falls ein Port ausgewählt wurde und kein expliziter connection_string angegeben wurde
            if hasattr(drone_view_model, '_selected_port') and drone_view_model._selected_port and not connection_string:
                connection_string = drone_view_model._selected_port
            drone_view_model.connectDrone(connection_string)
        drone_view_model.connect = connect
    
    if not hasattr(drone_view_model, 'update_connection_status'):
        def update_connection_status(is_connected):
            # Dieser Slot wird vom QML aufgerufen, kann aber ignoriert werden
            pass
        drone_view_model.update_connection_status = update_connection_status
    
    # QML Engine initialisieren
    engine = QQmlApplicationEngine()
    
    # QML-Importpfade setzen
    qml_content_dir = os.path.join(os.getcwd(), "RZGCSContent")
    engine.addImportPath(qml_content_dir)
    engine.addImportPath(os.getcwd())
    
    # QML-Umgebungsvariablen setzen
    os.environ["QML_IMPORT_PATH"] = qml_content_dir
    os.environ["QML2_IMPORT_PATH"] = qml_content_dir
    
    # QML-Typen registrieren
    qmlRegisterType(SensorViewModel, "RZGCS", 1, 0, "SensorViewModel")
    
    # WICHTIG: Root-Context für QML korrekt setzen
    root_context = engine.rootContext()
    
    # ViewModels für QML verfügbar machen
    root_context.setContextProperty("droneViewModel", drone_view_model)
    root_context.setContextProperty("serialConnector", drone_view_model)  # SEHR WICHTIG: UI verwendet serialConnector!
    root_context.setContextProperty("sensorModel", sensor_model)
    root_context.setContextProperty("logger", logger)
    
    # QML-Datei finden und laden
    qml_file = os.path.join(os.getcwd(), "RZGCSContent", "App.qml")
    print(f"Lade QML-Datei: {qml_file}")
    
    if not os.path.exists(qml_file):
        logger.addLog(f"[ERROR] QML-Datei nicht gefunden: {qml_file}")
        print(f"[FEHLER] QML-Datei nicht gefunden: {qml_file}")
        return 1
    
    # QML-Datei laden
    url = QUrl.fromLocalFile(qml_file)
    engine.load(url)
    
    # Prüfen, ob die Anwendung erfolgreich geladen wurde
    if not engine.rootObjects():
        logger.addLog("[ERROR] Konnte QML-Datei nicht laden!")
        print(f"[FEHLER] Konnte QML-Datei nicht laden: {url.toString()}")
        return 1
    
    # Anwendung starten
    logger.addLog("[INFO] RZGCS mit MAVSDK-MVVM-Integration und Material Style gestartet")
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
