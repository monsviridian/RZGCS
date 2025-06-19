#!/usr/bin/env python3
"""
MAVSDK COM Port Runner
Spezialisierter Runner für MAVSDK mit optimierter COM-Port-Verbindung
"""

import os
import sys
import types
from pathlib import Path

# Stil MUSS vor dem Import von PySide6 konfiguriert werden
os.environ["QT_QUICK_CONTROLS_STYLE"] = "Material"

# PySide6 importieren
import PySide6
from PySide6.QtCore import QObject, QUrl, Signal, Slot, Property
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine, qmlRegisterType
from PySide6.QtQuickControls2 import QQuickStyle

# Pfad zum Projektverzeichnis
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import von Modulen
from backend.logger import Logger
from backend.sensorviewmodel import SensorViewModel
from backend.parameter_model import ParameterTableModel
from backend.parameter_manager import ParameterManager


def fix_signal_connect_conflict():
    """
    Löst den Konflikt zwischen Signal.connect und der Methode connect()
    im MAVSDKDroneViewModel durch Monkey-Patching
    """
    from rzgcs.mvvm.viewmodel.mavsdk_drone_viewmodel import MAVSDKDroneViewModel
    
    # Speichere die ursprüngliche connect-Methode unter einem anderen Namen
    if hasattr(MAVSDKDroneViewModel, 'connect') and not hasattr(MAVSDKDroneViewModel, '_original_connect'):
        MAVSDKDroneViewModel._original_connect = MAVSDKDroneViewModel.connect
        
        # Lösche die Methode 'connect' aus der Klasse, um die Signal.connect-Methode freizugeben
        delattr(MAVSDKDroneViewModel, 'connect')
        
        # Füge eine neue Methode connectToDrone hinzu, die die original-Funktionalität bietet
        @Slot(str)
        def connectToDrone(self, connection_string=""):
            return self._original_connect(connection_string)
        
        MAVSDKDroneViewModel.connectToDrone = connectToDrone
        
        print("[INFO] MAVSDKDroneViewModel.connect wurde erfolgreich umbenannt in connectToDrone")
    
    return MAVSDKDroneViewModel


class SensorModelUpdater(QObject):
    """Aktualisiert das SensorModel mit Daten vom DroneViewModel"""
    
    def __init__(self, drone_view_model, sensor_model, logger):
        super().__init__()
        self._drone_view_model = drone_view_model
        self._sensor_model = sensor_model
        self._logger = logger
        
        # Verbinde Signale
        self._connect_signals()
    
    def _connect_signals(self):
        """Verbinde alle Signale mit dem SensorModel"""
        # Batterie-Updates
        self._drone_view_model.batteryChanged.connect(self._update_battery)
        
        # GPS-Updates
        self._drone_view_model.gpsInfoChanged.connect(self._update_gps)
        
        # Position-Updates
        self._drone_view_model.positionChanged.connect(self._update_position)
        
        # Attitude-Updates
        self._drone_view_model.attitudeChanged.connect(self._update_attitude)
        
        # Heading-Updates
        self._drone_view_model.headingChanged.connect(self._update_heading)
    
    def _update_battery(self, battery):
        """Aktualisiere Batterie-Informationen im SensorModel"""
        self._sensor_model.setBatteryLevel(battery['remaining_percent'])
        self._sensor_model.setBatteryVoltage(battery['voltage_v'])
    
    def _update_gps(self, gps_info):
        """Aktualisiere GPS-Informationen im SensorModel"""
        self._sensor_model.setGpsSatelliteCount(gps_info['num_satellites'])
        self._sensor_model.setGpsFixType(gps_info['fix_type'])
    
    def _update_position(self, position):
        """Aktualisiere Positions-Informationen im SensorModel"""
        if 'latitude_deg' in position and 'longitude_deg' in position:
            self._sensor_model.setLatitude(position['latitude_deg'])
            self._sensor_model.setLongitude(position['longitude_deg'])
        
        if 'absolute_altitude_m' in position:
            self._sensor_model.setAltitude(position['absolute_altitude_m'])
    
    def _update_attitude(self, attitude):
        """Aktualisiere Attitude-Informationen im SensorModel"""
        if 'roll_deg' in attitude:
            self._sensor_model.setRoll(attitude['roll_deg'])
        
        if 'pitch_deg' in attitude:
            self._sensor_model.setPitch(attitude['pitch_deg'])
        
        if 'yaw_deg' in attitude:
            self._sensor_model.setYaw(attitude['yaw_deg'])
    
    def _update_heading(self, heading):
        """Aktualisiere Heading im SensorModel"""
        self._sensor_model.setHeading(heading)


def setup_material_style():
    """Konfiguriert den Material-Stil für QML"""
    # Umgebungsvariable setzen
    os.environ["QT_QUICK_CONTROLS_STYLE"] = "Material"
    
    # QQuickStyle API verwenden
    QQuickStyle.setStyle("Material")
    
    # Material-Stil-Konfigurationsdatei erstellen, falls sie nicht existiert
    config_file = os.path.join(project_root, "RZGCSContent", "qtquickcontrols2.conf")
    if not os.path.exists(config_file):
        config_content = """[Controls]
Style=Material

[Material]
Theme=Dark
Accent=Teal
Primary=BlueGrey
Variant=Dense
"""
        with open(config_file, "w") as f:
            f.write(config_content)
        print(f"[INFO] Material-Stil-Konfigurationsdatei erstellt: {config_file}")
    
    # QML-Importpfade setzen
    qml_content_dir = os.path.join(project_root, "RZGCSContent")
    os.environ["QML_IMPORT_PATH"] = qml_content_dir
    os.environ["QML2_IMPORT_PATH"] = qml_content_dir


def main():
    """Hauptfunktion der Anwendung"""
    # Versionsinfo ausgeben
    print(f"Python-Version: {sys.version}")
    print(f"PySide6-Version: {PySide6.__version__}")
    
    # Arbeitsverzeichnis setzen
    os.chdir(project_root)
    print(f"Arbeitsverzeichnis: {os.getcwd()}")
    
    # Material-Stil konfigurieren
    setup_material_style()
    
    # Signal-Connect-Konflikt lösen (WICHTIG: vor der Erstellung des ViewModels)
    MAVSDKDroneViewModel = fix_signal_connect_conflict()
    
    # Anwendung erstellen
    app = QGuiApplication(sys.argv)
    
    # Logger erstellen
    logger = Logger()
    logger.addLog("[INFO] Starte MAVSDK COM Port Runner")
    
    # MAVSDK-Server prüfen
    mavsdk_server_path = os.path.join(os.getcwd(), "mavsdk_server", "windows", "mavsdk-server.exe")
    if os.path.exists(mavsdk_server_path):
        logger.addLog(f"[INFO] MAVSDK-Server gefunden: {mavsdk_server_path}")
    else:
        logger.addLog(f"[WARNUNG] MAVSDK-Server nicht gefunden: {mavsdk_server_path}")
    
    # DroneViewModel erstellen
    drone_view_model = MAVSDKDroneViewModel(logger)
    
    # Weitere Modelle erstellen
    sensor_model = SensorViewModel()
    parameter_model = ParameterTableModel()
    parameter_manager = ParameterManager(parameter_model, logger)
    
    # SensorModelUpdater erstellen
    sensor_updater = SensorModelUpdater(drone_view_model, sensor_model, logger)
    
    # QML-Engine erstellen
    engine = QQmlApplicationEngine()
    
    # QML-Importpfade setzen
    qml_content_dir = os.path.join(os.getcwd(), "RZGCSContent")
    engine.addImportPath(qml_content_dir)
    engine.addImportPath(os.getcwd())
    
    # QML-Typen registrieren
    qmlRegisterType(SensorViewModel, "RZGCS", 1, 0, "SensorViewModel")
    
    # Modelle im QML-Kontext registrieren
    context = engine.rootContext()
    
    # WICHTIG: Das DroneViewModel als 'serialConnector' für QML-Kompatibilität registrieren
    context.setContextProperty("serialConnector", drone_view_model)
    context.setContextProperty("droneViewModel", drone_view_model)
    context.setContextProperty("sensorModel", sensor_model)
    context.setContextProperty("parameterModel", parameter_model)
    context.setContextProperty("parameterManager", parameter_manager)
    context.setContextProperty("logger", logger)
    
    # QML-Datei laden
    qml_file = os.path.join(os.getcwd(), "RZGCSContent", "App.qml")
    print(f"Lade QML-Datei: {qml_file}")
    
    # Prüfe, ob die QML-Datei existiert
    if not os.path.exists(qml_file):
        print(f"[FEHLER] QML-Datei nicht gefunden: {qml_file}")
        available_files = os.listdir(os.path.join(os.getcwd(), "RZGCSContent"))
        print(f"Verfügbare Dateien in RZGCSContent: {available_files}")
        return 1
    
    # Debug-Ausgabe: Existierende Environment-Variablen
    print(f"QML_IMPORT_PATH: {os.environ.get('QML_IMPORT_PATH', 'nicht gesetzt')}")
    print(f"QML2_IMPORT_PATH: {os.environ.get('QML2_IMPORT_PATH', 'nicht gesetzt')}")
    print(f"QT_QUICK_CONTROLS_STYLE: {os.environ.get('QT_QUICK_CONTROLS_STYLE', 'nicht gesetzt')}")
    
    # Stelle sicher, dass die QML-Datei lesbar ist
    try:
        with open(qml_file, 'r') as f:
            qml_content_preview = f.read(100)
            print(f"QML-Datei-Vorschau: {qml_content_preview}...")
    except Exception as e:
        print(f"[FEHLER] Konnte QML-Datei nicht lesen: {e}")
        return 1
    
    # QML-Datei laden
    url = QUrl.fromLocalFile(qml_file)
    engine.load(url)
    
    # Fehlerbehandlung
    def handle_qml_warnings(msg):
        print(f"[QML WARNUNG] {msg}")
    
    # QML-Fehler abfangen
    engine.warnings.connect(handle_qml_warnings)
    
    # Prüfen, ob die Anwendung erfolgreich geladen wurde
    if not engine.rootObjects():
        print(f"[FEHLER] Konnte QML-Datei nicht laden: {url.toString()}")
        return 1
    
    # Anwendung starten
    logger.addLog("[INFO] MAVSDK COM Port Runner gestartet")
    logger.addLog("[INFO] Verbindung über COM-Port ist optimiert")
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
