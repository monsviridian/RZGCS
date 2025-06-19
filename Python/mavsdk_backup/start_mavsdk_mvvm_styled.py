#!/usr/bin/env python3
"""
RZGCS MAVSDK MVVM Startskript mit optimierter Material-Style-Integration
Verwendet den QML Style Helper zur konsistenten Styling-Konfiguration
"""

import os
import sys
from pathlib import Path

# QML Style Helper vor allen anderen QT-Importen importieren!
sys.path.insert(0, str(Path(__file__).resolve().parent))
from rzgcs.ui.qml_style_helper import configure_material_style, add_qml_paths_to_engine, set_material_config_file

# Stil MUSS vor dem Import von PySide6 konfiguriert werden
configure_material_style()

# PySide6 importieren
import PySide6
from PySide6.QtCore import QUrl, Property
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine, qmlRegisterType

# Importiere benötigte Module
from backend.logger import Logger
from backend.sensorviewmodel import SensorViewModel
from rzgcs.mvvm.viewmodel.mavsdk_drone_viewmodel import MAVSDKDroneViewModel


def main():
    """Hauptfunktion der Anwendung"""
    # Aktuelle Python-Version ausgeben
    print(f"Python-Version: {sys.version}")
    print(f"PySide6-Version: {PySide6.__version__}")
    
    # WICHTIG: Arbeitsverzeichnis korrekt setzen
    project_root = Path(__file__).resolve().parent.parent
    os.chdir(str(project_root))
    print(f"Arbeitsverzeichnis: {os.getcwd()}")
    
    # Stelle sicher, dass die Material-Style-Config-Datei existiert
    set_material_config_file()
    
    # Anwendung erstellen
    app = QGuiApplication(sys.argv)
    
    # Logger initialisieren
    logger = Logger()
    logger.addLog("[INFO] Initialisiere RZGCS mit MAVSDK-MVVM-Integration (Material Style)")
    
    # Sensor-ViewModel erstellen
    sensor_model = SensorViewModel()
    
    # Drohnen-ViewModel erstellen (MVVM-Architektur)
    drone_view_model = MAVSDKDroneViewModel(logger)
    
    # Stelle sicher, dass alle von der QML-UI erwarteten Eigenschaften und Methoden vorhanden sind
    # Besonders wichtig basierend auf der Erinnerung "Die Verbindungssteuerung in der RZGCS-UI wurde verbessert"
    
    # Füge 'connected' Property als Alias für 'connectionState' hinzu, falls sie nicht existiert
    if not hasattr(drone_view_model, 'connected'):
        # Property-Getter für 'connected'
        def get_connected():
            return getattr(drone_view_model._model, 'is_connected', False)
        
        # Property für QML registrieren
        connected_property = Property(bool, get_connected, notify=drone_view_model.connectionStateChanged)
        setattr(drone_view_model.__class__, 'connected', connected_property)
    
    # load_ports Methode für Kompatibilität mit QML
    if not hasattr(drone_view_model, 'load_ports'):
        def load_ports():
            drone_view_model.refreshPorts()
        drone_view_model.load_ports = load_ports
    
    # setPort Methode für Kompatibilität mit QML
    if not hasattr(drone_view_model, 'setPort'):
        def setPort(port_name):
            drone_view_model._selected_port = port_name
            logger.addLog(f"[INFO] Port ausgewählt: {port_name}")
        drone_view_model.setPort = setPort
    
    # connect Methode für universelle Verbindung (COM-Ports, UDP, TCP)
    if not hasattr(drone_view_model, 'connect'):
        def connect(connection_string):
            # Falls ein Port ausgewählt wurde und kein expliziter connection_string angegeben wurde
            if hasattr(drone_view_model, '_selected_port') and drone_view_model._selected_port and not connection_string:
                connection_string = drone_view_model._selected_port
            
            # Baudrate aus Verbindungsstring extrahieren (z.B. "COM3:115200")
            if ":" in connection_string and not connection_string.startswith(("udp:", "tcp:")):
                port, baudrate = connection_string.split(":", 1)
                try:
                    baudrate = int(baudrate)
                    drone_view_model.connectDrone(f"{port}:{baudrate}")
                except ValueError:
                    drone_view_model.connectDrone(connection_string)
            else:
                drone_view_model.connectDrone(connection_string)
        drone_view_model.connect = connect
    
    # update_connection_status für Kompatibilität mit QML
    if not hasattr(drone_view_model, 'update_connection_status'):
        def update_connection_status(is_connected):
            # Dieser Slot wird vom QML aufgerufen und leitet den Status weiter
            drone_view_model.connectionStateChanged.emit(is_connected)
        drone_view_model.update_connection_status = update_connection_status
    
    # QML Engine initialisieren
    engine = QQmlApplicationEngine()
    
    # QML-Importpfade setzen mit Hilfe des Helpers
    add_qml_paths_to_engine(engine)
    
    # QML-Typen registrieren
    qmlRegisterType(SensorViewModel, "RZGCS", 1, 0, "SensorViewModel")
    
    # WICHTIG: Root-Context für QML korrekt setzen
    root_context = engine.rootContext()
    
    # ViewModels für QML verfügbar machen - WICHTIG: serialConnector wird von der UI erwartet
    root_context.setContextProperty("droneViewModel", drone_view_model)
    root_context.setContextProperty("serialConnector", drone_view_model)
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
