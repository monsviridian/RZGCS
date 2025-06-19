#!/usr/bin/env python3
"""
Optimierter Starter für RZGCS mit MAVSDK-Integration
Diese Version verwendet den originalen QML-Code und passt die Importpfade an
"""

import os
import sys
import time
from pathlib import Path
from PySide6.QtCore import QUrl, QObject, Signal, Slot, Property, QDir
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

# Stellen Sie sicher, dass wir vom Projektverzeichnis aus starten
os.chdir(os.path.dirname(os.path.abspath(__file__)))
print(f"Arbeitsverzeichnis: {os.getcwd()}")

# Einfacher Logger
class Logger(QObject):
    logAdded = Signal(str)
    
    def __init__(self):
        super().__init__()
        self._logs = []
    
    def addLog(self, message):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        self._logs.append(formatted_message)
        self.logAdded.emit(formatted_message)
        print(formatted_message)
    
    def getLogs(self, count=None):
        if count is None:
            return self._logs
        return self._logs[-count:]


# Einfaches SensorViewModel
class SensorViewModel(QObject):
    sensorUpdated = Signal(str, object, str)
    sensorListChanged = Signal()
    
    def __init__(self):
        super().__init__()
        self._sensors = {}
        self._list_elements = {}
    
    def initialize_default_sensors(self):
        """Initialisiert die Standard-Sensoren"""
        list_elements = [
            {"name": "System Servos", "unit": ""},
            {"name": "System RC", "unit": ""},
            {"name": "System Mission", "unit": ""},
            {"name": "System CPU", "unit": ""},
            {"name": "Battery %", "unit": ""},
            {"name": "Roll", "unit": "°"},
            {"name": "Pitch", "unit": "°"},
            {"name": "Yaw", "unit": "°"},
            {"name": "Altitude", "unit": "m"},
            {"name": "Groundspeed", "unit": "m/s"},
            {"name": "Airspeed", "unit": "m/s"},
            {"name": "GPS Pos", "unit": "°"},
            {"name": "GPS Fix", "unit": ""},
            {"name": "GPS Satellites", "unit": ""},
            {"name": "Battery", "unit": "V"},
            {"name": "Firmware", "unit": ""},
            {"name": "Frame", "unit": ""},
            {"name": "Version", "unit": ""}
        ]
        
        for element in list_elements:
            self._list_elements[element["name"]] = {
                "name": element["name"],
                "value": "Nicht verbunden",
                "unit": element["unit"]
            }
        
        self.sensorListChanged.emit()
    
    @Slot(str, object)
    def update_sensor(self, sensor_id, value):
        """Aktualisiert einen Sensor im Datenmodell"""
        self._sensors[sensor_id] = value
        return True
    
    @Slot(str, object, str)
    def updateQmlSensor(self, name, value, unit):
        """Aktualisiert einen Sensor in der QML-Ansicht"""
        # ListElement-Update für die SensorView
        if name in self._list_elements:
            self._list_elements[name]["value"] = value
            self._list_elements[name]["unit"] = unit
        
        # Signal für QML emittieren
        self.sensorUpdated.emit(name, value, unit)
    
    @Slot(result="QVariantList")
    def get_sensor_list(self):
        """Gibt eine Liste aller Sensoren für QML zurück"""
        result = []
        for name, data in self._list_elements.items():
            result.append({
                "name": name,
                "value": data["value"],
                "unit": data["unit"]
            })
        return result


# Einfacher Controller
class DroneController(QObject):
    connectionChanged = Signal(bool)
    
    def __init__(self, logger, sensor_viewmodel):
        super().__init__()
        self._logger = logger
        self._sensor_viewmodel = sensor_viewmodel
        self._is_connected = False
    
    @Slot(str)
    def connect(self, connection_string):
        self._logger.addLog(f"Verbindung zu {connection_string} wird hergestellt...")
        # Hier würde die echte MAVSDK-Verbindung stattfinden
        self._is_connected = True
        self.connectionChanged.emit(True)
        self._logger.addLog("Verbindung hergestellt (Simulation)")
        
        # Simulierte Sensordaten
        self._sensor_viewmodel.updateQmlSensor("Roll", "5.2", "°")
        self._sensor_viewmodel.updateQmlSensor("Pitch", "2.1", "°")
        self._sensor_viewmodel.updateQmlSensor("Yaw", "358.7", "°")
        self._sensor_viewmodel.updateQmlSensor("Altitude", "120.5", "m")
        self._sensor_viewmodel.updateQmlSensor("Groundspeed", "12.3", "m/s")
        self._sensor_viewmodel.updateQmlSensor("Battery %", "78%", "")
        self._sensor_viewmodel.updateQmlSensor("GPS Pos", "48.744101, 11.446327", "°")
        self._sensor_viewmodel.updateQmlSensor("System CPU", "23.5%", "")
        
        return True
    
    @Slot()
    def disconnect(self):
        self._logger.addLog("Verbindung wird getrennt...")
        # Hier würde die echte MAVSDK-Verbindung getrennt werden
        self._is_connected = False
        self.connectionChanged.emit(False)
        self._logger.addLog("Verbindung getrennt")
        return True
    
    @Property(bool, notify=connectionChanged)
    def is_connected(self):
        return self._is_connected


def main():
    # QT-Anwendung erstellen
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    
    # Komponenten erstellen
    logger = Logger()
    sensor_viewmodel = SensorViewModel()
    drone_controller = DroneController(logger, sensor_viewmodel)
    
    # QML-Kontext einrichten
    root_context = engine.rootContext()
    root_context.setContextProperty("droneController", drone_controller)
    root_context.setContextProperty("sensorViewModel", sensor_viewmodel)
    root_context.setContextProperty("loggerModel", logger)
    
    # Initialisierung
    sensor_viewmodel.initialize_default_sensors()
    
    # Debug-Ausgabe für den aktuellen Arbeitsverzeichnis und QML-Importpfade
    logger.addLog(f"Arbeitsverzeichnis: {os.getcwd()}")
    
    # QML-Importpfade einrichten
    project_dir = os.path.abspath(os.getcwd())
    content_dir = os.path.join(project_dir, "RZGCSContent")
    
    # Alle wichtigen Pfade hinzufügen
    engine.addImportPath(project_dir)
    engine.addImportPath(content_dir)
    
    # Zusätzlich den Pfad zur Umgebungsvariable hinzufügen
    os.environ["QML2_IMPORT_PATH"] = f"{project_dir}{os.pathsep}{content_dir}"
    
    # Debug-Ausgabe für alle QML-Importpfade
    logger.addLog(f"QML-Importpfade: {engine.importPathList()}")
    logger.addLog(f"QML2_IMPORT_PATH: {os.environ.get('QML2_IMPORT_PATH', 'nicht gesetzt')}")
    
    # QML-Dateien suchen und ausgeben
    qml_dir = QDir(content_dir)
    qml_files = qml_dir.entryList(["*.qml", "*.ui.qml"], QDir.Files)
    logger.addLog(f"Gefundene QML-Dateien: {qml_files}")
    
    # qmldir-Dateien suchen und ausgeben
    qmldir_files = []
    for root, dirs, files in os.walk(content_dir):
        for file in files:
            if file == "qmldir":
                rel_path = os.path.relpath(os.path.join(root, file), project_dir)
                qmldir_files.append(rel_path)
    logger.addLog(f"Gefundene qmldir-Dateien: {qmldir_files}")
    
    # QML-Hauptdatei laden
    qml_file = os.path.join(content_dir, "App.qml")
    qml_url = QUrl.fromLocalFile(qml_file)
    
    logger.addLog(f"Lade QML-Datei: {qml_file}")
    engine.load(qml_url)
    
    # Prüfen, ob QML-Datei erfolgreich geladen wurde
    if not engine.rootObjects():
        logger.addLog("❌ Fehler beim Laden der QML-Datei")
        return -1
    
    logger.addLog("RZGCS mit MAVSDK gestartet")
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
