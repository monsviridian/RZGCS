#!/usr/bin/env python3
"""
RZGCS MAVSDK MVVM COM Port-optimierte Startskript
Verwendet den MAVSDKQMLAdapter zur Vermeidung von Signalkonflikten und
optimiert die COM-Port-Verbindung für die Ardupilot-Kommunikation.
"""

import os
import sys
from pathlib import Path

# Stil MUSS vor dem Import von PySide6 konfiguriert werden
os.environ["QT_QUICK_CONTROLS_STYLE"] = "Material"

# PySide6 importieren
import PySide6
from PySide6.QtCore import QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine, qmlRegisterType
from PySide6.QtQuickControls2 import QQuickStyle

# Projekt-Root zum Python-Pfad hinzufügen
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Importiere benötigte Module
from backend.logger import Logger
from backend.sensorviewmodel import SensorViewModel
from backend.parameter_model import ParameterTableModel
from backend.parameter_manager import ParameterManager
from rzgcs.mvvm.viewmodel.mavsdk_drone_viewmodel import MAVSDKDroneViewModel
from rzgcs.mvvm.mavsdk_qml_adapter import MAVSDKQMLAdapter
from rzgcs.ui.qml_style_helper import configure_material_style, add_qml_paths_to_engine, set_material_config_file


class SensorDataRelay:
    """
    Klasse zur Weiterleitung von Drohnendaten an das SensorModel
    ohne Signalname-Konflikte
    """
    def __init__(self, drone_view_model, sensor_model, logger):
        """Initialisiert den Sensor-Daten-Relay"""
        self.drone_view_model = drone_view_model
        self.sensor_model = sensor_model
        self.logger = logger
        
        # Verbinde alle Signale mit Lambda-Funktionen, um Namenskonflikte zu vermeiden
        self._connect_signals()
    
    def _connect_signals(self):
        """Verbindet alle Signale für die Datenweiterleitung"""
        # Battery-Updates
        self.drone_view_model.batteryChanged.connect(
            lambda battery: self._update_battery(battery)
        )
        
        # GPS-Updates
        self.drone_view_model.gpsInfoChanged.connect(
            lambda gps: self._update_gps(gps)
        )
        
        # Position-Updates
        self.drone_view_model.positionChanged.connect(
            lambda pos: self._update_position(pos)
        )
        
        # Attitude-Updates
        self.drone_view_model.attitudeChanged.connect(
            lambda att: self._update_attitude(att)
        )
        
        # Heading-Updates
        self.drone_view_model.headingChanged.connect(
            lambda heading: self._update_heading(heading)
        )
    
    def _update_battery(self, battery):
        """Aktualisiert Batterie-Infos im Sensor-Model"""
        self.sensor_model.setBatteryLevel(battery['remaining_percent'])
        self.sensor_model.setBatteryVoltage(battery['voltage_v'])
    
    def _update_gps(self, gps_info):
        """Aktualisiert GPS-Infos im Sensor-Model"""
        self.sensor_model.setGpsSatelliteCount(gps_info['num_satellites'])
        self.sensor_model.setGpsFixType(gps_info['fix_type'])
    
    def _update_position(self, position):
        """Aktualisiert Positions-Infos im Sensor-Model"""
        if 'latitude_deg' in position and 'longitude_deg' in position:
            self.sensor_model.setLatitude(position['latitude_deg'])
            self.sensor_model.setLongitude(position['longitude_deg'])
        
        if 'absolute_altitude_m' in position:
            self.sensor_model.setAltitude(position['absolute_altitude_m'])
    
    def _update_attitude(self, attitude):
        """Aktualisiert Attitude-Infos im Sensor-Model"""
        if 'roll_deg' in attitude:
            self.sensor_model.setRoll(attitude['roll_deg'])
        
        if 'pitch_deg' in attitude:
            self.sensor_model.setPitch(attitude['pitch_deg'])
        
        if 'yaw_deg' in attitude:
            self.sensor_model.setYaw(attitude['yaw_deg'])
    
    def _update_heading(self, heading):
        """Aktualisiert Heading im Sensor-Model"""
        self.sensor_model.setHeading(heading)


def check_mavsdk_server():
    """Prüft, ob der MAVSDK-Server verfügbar ist"""
    mavsdk_server_path = os.path.join(project_root, "mavsdk_server", "windows", "mavsdk-server.exe")
    
    if os.path.exists(mavsdk_server_path):
        print(f"[INFO] MAVSDK-Server gefunden: {mavsdk_server_path}")
        return True
    else:
        print(f"[WARNUNG] MAVSDK-Server nicht gefunden: {mavsdk_server_path}")
        return False


def main():
    """Hauptfunktion der Anwendung"""
    # Version ausgeben
    print(f"Python-Version: {sys.version}")
    print(f"PySide6-Version: {PySide6.__version__}")
    
    # Arbeitsverzeichnis setzen
    os.chdir(project_root)
    print(f"Arbeitsverzeichnis: {os.getcwd()}")
    
    # Material-Stil konfigurieren
    configure_material_style()
    set_material_config_file()
    
    # MAVSDK-Server prüfen
    check_mavsdk_server()
    
    # QApplication erstellen
    app = QGuiApplication(sys.argv)
    
    # Logger erstellen
    logger = Logger()
    logger.addLog("[INFO] Starte RZGCS mit MAVSDK MVVM COM-Port-Integration")
    
    # Modelle erstellen
    drone_view_model = MAVSDKDroneViewModel(logger)
    sensor_model = SensorViewModel()
    parameter_model = ParameterTableModel()
    parameter_manager = ParameterManager(parameter_model, logger)
    
    # QML-Adapter für die Verbindung erstellen (wichtig für Signal-Namenskonflikt-Vermeidung)
    qml_adapter = MAVSDKQMLAdapter(drone_view_model, logger)
    
    # Sensor-Daten-Relay erstellen
    sensor_relay = SensorDataRelay(drone_view_model, sensor_model, logger)
    
    # QML-Engine erstellen
    engine = QQmlApplicationEngine()
    
    # Importpfade hinzufügen
    add_qml_paths_to_engine(engine)
    
    # QML-Typen registrieren
    qmlRegisterType(SensorViewModel, "RZGCS", 1, 0, "SensorViewModel")
    
    # Objekte im QML-Kontext registrieren
    context = engine.rootContext()
    
    # WICHTIG: Den Adapter als 'serialConnector' für QML-Kompatibilität registrieren
    context.setContextProperty("serialConnector", qml_adapter)
    context.setContextProperty("droneViewModel", drone_view_model)
    context.setContextProperty("sensorModel", sensor_model)
    context.setContextProperty("parameterModel", parameter_model)
    context.setContextProperty("parameterManager", parameter_manager)
    context.setContextProperty("logger", logger)
    
    # QML-Datei laden
    qml_file = os.path.join(os.getcwd(), "RZGCSContent", "App.qml")
    print(f"Lade QML-Datei: {qml_file}")
    
    # QML-Datei laden
    url = QUrl.fromLocalFile(qml_file)
    engine.load(url)
    
    # Prüfen, ob die Anwendung erfolgreich geladen wurde
    if not engine.rootObjects():
        print(f"[FEHLER] Konnte QML-Datei nicht laden: {url.toString()}")
        return 1
    
    # Anwendung starten
    logger.addLog("[INFO] RZGCS mit MAVSDK MVVM COM-Port-Integration gestartet")
    logger.addLog("[INFO] Verwende QML-Adapter zur Vermeidung von Signal-Namenskonflikten")
    logger.addLog("[INFO] COM-Port-Verbindung ist optimiert für Ardupilot")
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
