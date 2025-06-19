#!/usr/bin/env python3
"""
Einfaches Skript, um die originale RZGCS-UI anzuzeigen
"""

import os
import sys
from pathlib import Path

# Projektpfade einrichten
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.abspath(os.path.join(script_dir, ".."))
os.chdir(project_dir)  # Wichtig für relative Pfade in QML

# QML-Importpfade vorbereiten
qml_content_dir = os.path.join(project_dir, "RZGCSContent")

# Stellen Sie sicher, dass Python-Modulpfade korrekt sind
sys.path.insert(0, script_dir)
sys.path.insert(0, project_dir)

# Import der PySide6-Komponenten
from PySide6.QtCore import QObject, Signal, Slot, Property, QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine, qmlRegisterType

# Eine einfache Logger-Klasse
class Logger(QObject):
    logAdded = Signal(str)
    systemInfoAdded = Signal(str)
    
    def __init__(self):
        super().__init__()
        self._logs = []
    
    @Slot(str)
    def addLog(self, message):
        """Fügt einen Log-Eintrag hinzu"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        self._logs.append(formatted_message)
        self.logAdded.emit(formatted_message)
        
        # Prüfen, ob es sich um eine Systeminformation handelt
        if "[SYSTEM INFO]" in message:
            self.systemInfoAdded.emit(formatted_message)
        
        # Auch auf die Konsole ausgeben für Debugging
        try:
            print(formatted_message)
        except UnicodeEncodeError:
            # Fallback für Konsolen mit Unicode-Problemen
            safe_message = formatted_message.encode('ascii', 'replace').decode('ascii')
            print(safe_message)
    
    @Slot(int, result="QVariantList")
    def getLogs(self, count=100):
        """Gibt die letzten n Logs zurück"""
        return self._logs[-count:] if self._logs else []

# SensorViewModel-Dummy
class SensorViewModel(QObject):
    sensorUpdated = Signal(str, object, str)  # name, value, unit
    
    def __init__(self):
        super().__init__()
        self._sensors = {}
    
    @Slot(str, str, str)
    def updateSensor(self, name, value, unit):
        """Aktualisiert einen Sensor"""
        self._sensors[name] = {"value": value, "unit": unit}
        self.sensorUpdated.emit(name, value, unit)
    
    @Slot(str, result="QVariant")
    def getSensor(self, name):
        """Gibt Sensordaten zurück"""
        return self._sensors.get(name, {"value": "N/A", "unit": ""})

# License-Controller für QML
class LicenseController(QObject):
    def __init__(self):
        super().__init__()
    
    @Slot(result=bool)
    def checkLicense(self):
        """Dummy-Methode für Lizenzprüfung"""
        return True
    
    @Slot(result=str)
    def getLicenseInfo(self):
        """Gibt Lizenzinfos zurück"""
        return "Development License"

# Main-Controller für die UI-Steuerung
class MainController(QObject):
    connectionChanged = Signal(bool)
    armedChanged = Signal(bool)
    flightModeChanged = Signal(str)
    logAdded = Signal(str)
    systemInfoLogAdded = Signal(str)
    
    def __init__(self, logger, sensor_viewmodel):
        super().__init__()
        self._logger = logger
        self._sensor_viewmodel = sensor_viewmodel
        self._is_connected = False
        self._is_armed = False
        self._flight_mode = "UNKNOWN"
        
        # Logger-Signale verbinden
        if hasattr(self._logger, 'logAdded') and isinstance(getattr(self._logger, 'logAdded'), Signal):
            self._logger.logAdded.connect(self.logAdded)
        
        if hasattr(self._logger, 'systemInfoAdded') and isinstance(getattr(self._logger, 'systemInfoAdded'), Signal):
            self._logger.systemInfoAdded.connect(self.systemInfoLogAdded)
    
    @Slot(str)
    def connect_to_drone(self, connection_string):
        """Dummy-Methode für Verbindung"""
        self._logger.addLog(f"Verbindung zu {connection_string} wird simuliert...")
        self._is_connected = True
        self.connectionChanged.emit(True)
        self._logger.addLog("Verbindung hergestellt (Simulation)")
        
        # Simulierte System-Infos senden (wie in der MAVLink-Version)
        self._logger.addLog("[SYSTEM INFO] Frame: Quadcopter X")
        self._logger.addLog("[SYSTEM INFO] Firmware: ArduCopter 4.2.3")
        self._logger.addLog("[SYSTEM INFO] MicroAir743 [ChibiOS]")
        self._logger.addLog("[SYSTEM INFO] PreArm: All checks passed")
        return True
    
    @Slot()
    def disconnect_from_drone(self):
        """Dummy-Methode für Verbindungstrennung"""
        self._logger.addLog("Verbindung wird getrennt...")
        self._is_connected = False
        self.connectionChanged.emit(False)
        self._logger.addLog("Verbindung getrennt")
        return True
    
    @Slot()
    def arm_drone(self):
        """Dummy-Methode für Armieren"""
        self._logger.addLog("Armiere Drohne...")
        self._is_armed = True
        self.armedChanged.emit(True)
        return True
    
    @Slot()
    def disarm_drone(self):
        """Dummy-Methode für Disarmieren"""
        self._logger.addLog("Disarmiere Drohne...")
        self._is_armed = False
        self.armedChanged.emit(False)
        return True
    
    @Property(bool, notify=connectionChanged)
    def is_connected(self):
        return self._is_connected
    
    @Property(bool, notify=armedChanged)
    def is_armed(self):
        return self._is_armed
    
    @Property(str, notify=flightModeChanged)
    def flight_mode(self):
        return self._flight_mode
    
    @Slot(int, result="QVariantList")
    def get_logs(self, count=100):
        """Gibt die letzten n Logs zurück"""
        return self._logger.getLogs(count)

def main():
    # Qt-Anwendung erstellen
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    
    # QML-Typen registrieren
    qmlRegisterType(LicenseController, "RZGCS", 1, 0, "LicenseController")
    # Weitere Typen registrieren
    from PySide6.QtQml import QQmlComponent
    qml_components = {}
    
    # Anzeigen, welche QML-Module geladen werden
    print("[INFO] Registriere QML-Module:")
    try:
        import importlib
        import glob
        
        # Suche nach allen QML-Dateien im RZGCSContent-Ordner
        qml_files = glob.glob(os.path.join(qml_content_dir, "*.qml"))
        qml_ui_files = glob.glob(os.path.join(qml_content_dir, "*.ui.qml"))
        all_qml_files = qml_files + qml_ui_files
        
        for qml_file in all_qml_files:
            filename = os.path.basename(qml_file)
            component_name = os.path.splitext(filename)[0]
            if component_name.endswith(".ui"):
                component_name = component_name[:-3]  # Entferne ".ui" am Ende
            print(f"[INFO] - Gefunden: {component_name} ({qml_file})")
    except Exception as e:
        print(f"[WARNUNG] Fehler beim Scannen von QML-Dateien: {str(e)}")
    
    # QML-Modul-Namespace festlegen
    os.environ["QML_IMPORT_TRACE"] = "1"
    os.environ["QT_DEBUG_PLUGINS"] = "1"
    
    # Komponenten erstellen
    logger = Logger()
    sensor_viewmodel = SensorViewModel()
    main_controller = MainController(logger, sensor_viewmodel)
    
    # Importpfade für QML setzen
    engine.addImportPath(project_dir)
    engine.addImportPath(qml_content_dir)
    
    # QML-Umgebungsvariable für Imports setzen
    os.environ["QML2_IMPORT_PATH"] = f"{project_dir}{os.pathsep}{qml_content_dir}"
    
    # Debug-Log für QML-Importpfade
    print(f"QML-Importpfade: {engine.importPathList()}")
    
    # QML-Kontext einrichten
    root_context = engine.rootContext()
    root_context.setContextProperty("mainController", main_controller)
    root_context.setContextProperty("sensorViewModel", sensor_viewmodel)
    root_context.setContextProperty("logger", logger)
    
    # QML-Datei laden
    qml_file = os.path.join(qml_content_dir, "App.qml")
    print(f"Lade QML-Datei: {qml_file}")
    engine.load(QUrl.fromLocalFile(os.path.abspath(qml_file)))
    
    # Prüfen, ob QML-Datei erfolgreich geladen wurde
    if not engine.rootObjects():
        print("[FEHLER] Konnte QML-Datei nicht laden")
        return -1
    
    print("[OK] RZGCS-UI erfolgreich geladen")
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
