# main_ui_only.py - Vereinfachte Version ohne Backend-Komponenten

import sys
import os
import enum
from pathlib import Path
from PySide6.QtCore import QCoreApplication, QDir, QObject, QUrl, Signal, QTimer, Property, Slot, Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine, qmlRegisterType, QQmlComponent

# Import für die Dummy-Komponenten
from dummy_qml_components import DummyQmlComponents
from dummy_license_controller import DummyLicenseController

# Import für DroneKit-ViewModels
from rzgcs_dronekit_serial_connector import DroneKitSerialConnector
from dronekit_sensor_viewmodel import DroneKitSensorViewModel
from dronekit_mission_viewmodel import DroneKitMissionViewModel
from dronekit_parameter_viewmodel import DroneKitParameterViewModel

# Einfacher Logger für die UI
class SimpleLogger(QObject):
    logAdded = Signal(str, str)  # type, message
    
    def __init__(self):
        super().__init__()
        self._logs = []
        print("SimpleLogger initialisiert")
    
    def addLog(self, message, log_type="INFO"):
        print(f"[{log_type}] {message}")
        self._logs.append({"type": log_type, "message": message})
        self.logAdded.emit(log_type, message)
    
    def getLogs(self):
        return self._logs

# MessageManager-Klasse für Benachrichtigungen
class MessageManager(QObject):
    # Signal-Definitionen
    messageAdded = Signal(str, int)  # message, type
    connectionStatusChanged = Signal(bool, str)  # isConnected, statusText
    
    # Enum für Nachrichtentypen
    class MessageType(enum.IntEnum):
        Info = 1
        Warning = 2
        Error = 3
        Success = 4
    
    def __init__(self):
        super().__init__()
        self._messages = []
        print("MessageManager initialisiert")
    
    @Slot(str, int)
    def addMessage(self, message, message_type=1):  # Default: Info
        self._messages.append({"message": message, "type": message_type})
        self.messageAdded.emit(message, message_type)
        print(f"Message: [{message_type}] {message}")
    
    @Slot(bool, str)
    def updateConnectionStatus(self, isConnected, statusText):
        self.connectionStatusChanged.emit(isConnected, statusText)
        print(f"Connection status: {isConnected}, {statusText}")

# Dummy FirmwareViewModel
class FirmwareViewModel(QObject):
    firmwareVersionChanged = Signal()
    
    def __init__(self):
        super().__init__()
        self._firmware_version = "Dummy Firmware v1.0"
        print("FirmwareViewModel initialisiert")
    
    @Property(str, notify=firmwareVersionChanged)
    def firmwareVersion(self):
        return self._firmware_version
    
    def setFirmwareVersion(self, value):
        if self._firmware_version != value:
            self._firmware_version = value
            self.firmwareVersionChanged.emit(value)

# Dummy-Klasse für SerialConnector (nur UI-Unterstützung)
class DummySerialConnector(QObject):
    connected = Signal(bool)
    connectedChanged = Signal()  # Für QML Property-Binding
    connectionStatusChanged = Signal(int)
    
    def __init__(self):
        super().__init__()
        self._port = "DUMMY"
        self._baud_rate = 115200
        self._is_connected = False
        self._available_ports = ["COM1", "COM3", "COM6", "DUMMY"]
        print("DummySerialConnector initialisiert")
    
    @Slot()
    def connect(self):
        print("Dummy: Verbindung simulieren")
        self._is_connected = True
        self.connected.emit(True)
        self.connectedChanged.emit()
        self.connectionStatusChanged.emit(2)  # CONNECTED status
        return True
    
    @Slot()
    def disconnect(self):
        print("Dummy: Verbindung trennen")
        self._is_connected = False
        self.connected.emit(False)
        self.connectedChanged.emit()
        self.connectionStatusChanged.emit(0)  # DISCONNECTED status
        return True
    
    @Slot()
    def load_ports(self):
        print("Dummy: Lade verfügbare Ports")
        # Hier würde die echte Implementierung die Ports laden
        return self._available_ports
        
    @Property(bool, notify=connectedChanged)
    def isConnected(self):
        return self._is_connected
        
    # QML-Eigenschaft für die Verbindung (Kompatibilität mit der UI)
    @Property(bool, notify=connectedChanged)
    def connected(self):
        return self._is_connected
        
    @Property(list)
    def availablePorts(self):
        return self._available_ports
    
    @Slot(str)
    def setPort(self, port):
        print(f"Port gesetzt auf: {port}")
        self._port = port
    
    @Slot(int)
    def setBaudRate(self, rate):
        print(f"Baudrate gesetzt auf: {rate}")
        self._baud_rate = rate
    
    @Property(str)
    def port(self):
        return self._port

# Dummy-ViewModel für Sensordaten
class DummySensorViewModel(QObject):
    sensorUpdated = Signal(str, float)
    attitudeChanged = Signal(float, float, float)
    gpsChanged = Signal(float, float, float)
    batteryChanged = Signal(float, float, float)
    velocityChanged = Signal(float, float, float)
    
    def __init__(self):
        super().__init__()
        self._roll = 0.0
        self._pitch = 0.0
        self._yaw = 0.0
        self._lat = 0.0
        self._lon = 0.0
        self._alt = 0.0
        self._voltage = 12.6
        self._current = 0.0
        self._battery_percent = 75.0
        print("DummySensorViewModel initialisiert")
    
    def update_sensor_value(self, sensor_id, value):
        print(f"Sensor-Update: {sensor_id} = {value}")
        self.sensorUpdated.emit(sensor_id, value)
        
    # Eigenschaften für Attitude
    @Property(float, notify=attitudeChanged)
    def roll(self):
        return self._roll
        
    @Property(float, notify=attitudeChanged)
    def pitch(self):
        return self._pitch
        
    @Property(float, notify=attitudeChanged)
    def yaw(self):
        return self._yaw
    
    # GPS-Werte
    @Property(float, notify=gpsChanged)
    def lat(self):
        return self._lat
        
    @Property(float, notify=gpsChanged)
    def lon(self):
        return self._lon
        
    @Property(float, notify=gpsChanged)
    def alt(self):
        return self._alt
    
    # Batterie-Werte
    @Property(float, notify=batteryChanged)
    def voltage(self):
        return self._voltage
        
    @Property(float, notify=batteryChanged)
    def current(self):
        return self._current
        
    @Property(float, notify=batteryChanged)
    def battery_percent(self):
        return self._battery_percent
        
    # Methoden zum Aktualisieren der Werte
    def set_attitude(self, roll, pitch, yaw):
        self._roll = roll
        self._pitch = pitch
        self._yaw = yaw
        self.attitudeChanged.emit(roll, pitch, yaw)
        
    def set_gps_position(self, lat, lon, alt):
        self._lat = lat
        self._lon = lon
        self._alt = alt
        self.gpsChanged.emit(lat, lon, alt)
        
    def set_battery_status(self, voltage, current, remaining):
        self._voltage = voltage
        self._current = current
        self._battery_percent = remaining
        self.batteryChanged.emit(voltage, current, remaining)

def main():
    # Qt-Anwendung initialisieren
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QGuiApplication([])  # Leere Liste als Argument übergeben
    app.setOrganizationName("RZGS")
    app.setOrganizationDomain("rzgcs.de")
    app.setApplicationName("RZGS Ground Control Station")
    
    # Logger für die Anwendung erstellen
    logger = SimpleLogger()
    
    # Standard-Umgebungsvariablen für Qt setzen
    os.environ["QT_QUICK_CONTROLS_STYLE"] = "Material"
    os.environ["QT_QUICK_CONTROLS_MATERIAL_VARIANT"] = "Dense"
    os.environ["QT_QUICK_CONTROLS_MATERIAL_ACCENT"] = "#41cd52"
    os.environ["QML_IMPORT_TRACE"] = "1"  # QML Import-Debugging aktivieren
    
    # QML-Engine erstellen und initialisieren
    engine = QQmlApplicationEngine()
    
    # QML Debug-Ausgabe aktivieren
    def handle_qml_object_created(obj, url):
        print(f"QML Objekt erstellt: {obj} für URL: {url}")
        
    engine.objectCreated.connect(handle_qml_object_created)
    
    # MessageManager für QML registrieren
    qmlRegisterType(MessageManager, "RZGCS", 1, 0, "MessageManager")
    message_manager = MessageManager()
    firmware_viewmodel = FirmwareViewModel()
    
    # DroneKit-basierte Komponenten erstellen
    # DroneKit Serial Connector - verbindet zur Drone
    serial_connector = DroneKitSerialConnector()
    # Ersetzen durch echten Connector statt Dummy
    # serial_connector = DummySerialConnector()  
    
    # Sensor-ViewModel für Telemetrie
    sensor_viewmodel = DroneKitSensorViewModel(serial_connector)
    # Mission-ViewModel für Mission Planning
    mission_viewmodel = DroneKitMissionViewModel(serial_connector)
    # Parameter-ViewModel für Parameter Management
    parameter_viewmodel = DroneKitParameterViewModel(serial_connector)
    
    license_controller = DummyLicenseController()
    
    # Objekte im QML-Kontext verfügbar machen
    context = engine.rootContext()
    context.setContextProperty("logger", logger)
    context.setContextProperty("messageManager", message_manager)
    context.setContextProperty("firmwareViewModel", firmware_viewmodel)
    context.setContextProperty("serialConnector", serial_connector)
    context.setContextProperty("sensorViewModel", sensor_viewmodel)
    context.setContextProperty("licenseController", license_controller)
    
    # Neue DroneKit-ViewModels im QML-Kontext verfügbar machen
    context.setContextProperty("missionViewModel", mission_viewmodel)
    context.setContextProperty("parameterViewModel", parameter_viewmodel)
    
    # QML-Import-Pfade setzen
    qml_path = Path(__file__).parent.parent
    QDir.addSearchPath("content", str(qml_path / "RZGCSContent"))
    
    # Verbesserte Import-Pfadeinstellung
    engine.addImportPath(str(qml_path))
    engine.addImportPath(str(qml_path / "RZGCSContent"))
    engine.addImportPath(".")  # Aktuelles Verzeichnis
    
    # Weitere wichtige Pfade hinzufügen
    QDir.addSearchPath("RZGCS", str(qml_path / "RZGCSContent"))
    QDir.addSearchPath("assets", str(qml_path / "RZGCSContent" / "Assets"))
    QDir.addSearchPath("components", str(qml_path / "RZGCSContent" / "Components"))
    QDir.addSearchPath("images", str(qml_path / "RZGCSContent" / "images"))
    QDir.addSearchPath("Connection", str(qml_path / "RZGCSContent" / "Connection"))
    
    # Dummy QML Komponenten registrieren
    DummyQmlComponents.register_dummy_types(engine)
    
    # Debug-Ausgabe für QML-Pfad
    print(f"QML-Pfad: {qml_path}")
    
    # Hauptanwendungs-QML laden
    qml_file = Path(__file__).parent.parent / "RZGCSContent" / "App.qml"
    qml_file_path = str(qml_file)
    print(f"Lade Hauptanwendungs-QML-Datei: {qml_file_path}")
    
    # Prüfe, ob die Datei existiert
    if not qml_file.exists():
        print(f"FEHLER: QML-Datei nicht gefunden: {qml_file_path}")
        return -1
        
    # QML-Debug und Fehlerberichterstattung aktivieren
    os.environ["QT_VERBOSE_ERRORS"] = "1"
    os.environ["QT_MESSAGE_PATTERN"] = "%{if-debug}D%{endif}%{if-warning}W%{endif}%{if-critical}C%{endif}%{if-fatal}F%{endif}: %{message}"
    os.environ["QML_IMPORT_TRACE"] = "1"
    os.environ["QT_LOGGING_RULES"] = "qt.qml.connections=true;qt.quick.import=true;qt.scenegraph.general=true"
    
    # Zuerst testen wir, ob App.qml als Komponente geladen werden kann, um Fehler zu sehen
    print("\nAnalysiere App.qml...")
    app_component = QQmlComponent(engine)
    app_component.loadUrl(QUrl.fromLocalFile(qml_file_path))
    
    if app_component.isError():
        print("\nFEHLER BEIM LADEN VON APP.QML:")
        for error in app_component.errors():
            print(f"  - {error.toString()}")
    else:
        print("App.qml konnte als Komponente geladen werden!")
        
    # Testen, ob wir die lokale Screen01.ui.qml laden können
    print("\nAnalysiere Screen01.ui.qml...")
    screen_qml = Path(__file__).parent.parent / "RZGCSContent" / "Screen01.ui.qml"
    screen_component = QQmlComponent(engine)
    screen_component.loadUrl(QUrl.fromLocalFile(str(screen_qml)))
    
    if screen_component.isError():
        print("\nFEHLER BEIM LADEN VON SCREEN01.UI.QML:")
        for error in screen_component.errors():
            print(f"  - {error.toString()}")
    else:
        print("Screen01.ui.qml konnte als Komponente geladen werden!")
    
    # Einfachere .ui.qml Datei testen
    print("\nVersuche mit einfacherer .ui.qml Datei...")
    simple_qml = Path(__file__).parent.parent / "RZGCSContent" / "LogsList.ui.qml"
    if simple_qml.exists():
        simple_component = QQmlComponent(engine)
        simple_component.loadUrl(QUrl.fromLocalFile(str(simple_qml)))
        
        if simple_component.isError():
            print("\nFEHLER BEIM LADEN VON LOGLIST.UI.QML:")
            for error in simple_component.errors():
                print(f"  - {error.toString()}")
        else:
            print("LogsList.ui.qml konnte geladen werden!")
    else:
        print(f"LogsList.ui.qml nicht gefunden unter {simple_qml}")
        
    print("\nVersuche nun App.qml über engine.load zu laden...")
    
    # Funktion zum Abfangen von Status-Änderungen
    def on_status_changed(obj, url):
        if obj is None:
            print(f"Engine konnte kein Root-Objekt für URL erstellen: {url}")
        else:
            print(f"Engine hat Root-Objekt erfolgreich erstellt: {obj}")
            
    engine.objectCreated.connect(on_status_changed)
        
    # QML-Datei laden
    engine.load(QUrl.fromLocalFile(qml_file_path))
    
    # Prüfen, ob QML-Datei geladen wurde
    if not engine.rootObjects():
        print(f"FEHLER: Keine Root-Objekte nach dem Laden von {qml_file_path}")
        return -1
    
    # Erfolgsmeldung senden
    logger.addLog("RZGCS UI-Only Mode gestartet. Nur UI wird angezeigt, keine Backend-Funktionalität.")
    
    # Log alle 3 Sekunden hinzufügen, um zu zeigen, dass die UI funktioniert
    timer = QTimer()
    timer.timeout.connect(lambda: logger.addLog("UI ist aktiv", "DEBUG"))
    timer.start(3000)
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
