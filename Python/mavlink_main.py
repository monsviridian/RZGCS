"""
mavlink_main.py - RZGCS mit PyMAVLink-Integration

Diese Version der RZGCS verwendet PyMAVLink direkt anstelle von DroneKit
für eine robustere und einfachere Kommunikation mit dem Flugcontroller.
"""

import sys
import os
import enum
from pathlib import Path
from PySide6.QtCore import QCoreApplication, QDir, QObject, QUrl, Signal, QTimer, Property, Slot
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine, qmlRegisterType, QQmlComponent

# Import für die Dummy-Komponenten
from dummy_qml_components import DummyQmlComponents
from dummy_license_controller import DummyLicenseController

# Import der PyMAVLink-Komponenten
from mavlink_connector import MavlinkConnector
from dronekit_sensor_viewmodel import DroneKitSensorViewModel
from viewmodel.mission_planner_viewmodel import MissionPlannerViewModel

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
        self._firmware_version = "PyMAVLink Firmware v1.0"
        print("FirmwareViewModel initialisiert")
    
    @Property(str, notify=firmwareVersionChanged)
    def firmwareVersion(self):
        return self._firmware_version
    
    def setFirmwareVersion(self, value):
        if self._firmware_version != value:
            self._firmware_version = value
            self.firmwareVersionChanged.emit(value)

# PyMAVLink Serial Connector (Ersatz für DroneKitSerialConnector)
class MavlinkSerialConnector(QObject):
    """PyMAVLink-basierter Serial Connector"""
    
    # Signals (kompatibel mit DroneKitSerialConnector)
    connectedChanged = Signal(bool)
    connectionStatusChanged = Signal(int)
    gpsChanged = Signal(float, float, float)  # lat, lon, alt
    attitudeChanged = Signal(float, float, float)  # roll, pitch, yaw
    batteryChanged = Signal(float)  # voltage
    statusMessageChanged = Signal(str)
    
    # Connection status constants
    CONNECTION_STATUS_DISCONNECTED = 0
    CONNECTION_STATUS_CONNECTING = 1
    CONNECTION_STATUS_CONNECTED = 2
    CONNECTION_STATUS_FAILED = 3
    
    def __init__(self):
        super().__init__()
        self.mavlink_connector = MavlinkConnector()
        self.available_ports = []
        self.selected_port = ""
        self.selected_baudrate = 115200
        self.connected = False
        
        # Verbinde PyMAVLink-Signals
        self.mavlink_connector.connected.connect(self._on_connected)
        self.mavlink_connector.disconnected.connect(self._on_disconnected)
        self.mavlink_connector.connection_failed.connect(self._on_connection_failed)
        self.mavlink_connector.gps_updated.connect(self.gpsChanged)
        self.mavlink_connector.attitude_updated.connect(self.attitudeChanged)
        self.mavlink_connector.battery_updated.connect(self.batteryChanged)
        self.mavlink_connector.status_updated.connect(self.statusMessageChanged)
        
        print("MavlinkSerialConnector initialisiert")
    
    def _on_connected(self):
        """PyMAVLink verbunden"""
        self.connected = True
        self.connectedChanged.emit(True)
        self.connectionStatusChanged.emit(self.CONNECTION_STATUS_CONNECTED)
        print("[MAVLINK] Verbindung erfolgreich")
    
    def _on_disconnected(self):
        """PyMAVLink getrennt"""
        self.connected = False
        self.connectedChanged.emit(False)
        self.connectionStatusChanged.emit(self.CONNECTION_STATUS_DISCONNECTED)
        print("[MAVLINK] Verbindung getrennt")
    
    def _on_connection_failed(self, error):
        """PyMAVLink Verbindung fehlgeschlagen"""
        self.connected = False
        self.connectedChanged.emit(False)
        self.connectionStatusChanged.emit(self.CONNECTION_STATUS_FAILED)
        print(f"[MAVLINK] Verbindung fehlgeschlagen: {error}")
    
    def load_ports(self):
        """Verfügbare Ports laden"""
        import serial.tools.list_ports
        
        print("[DEBUG] Starte Port-Erkennung...")
        ports = []
        
        # Serielle Ports
        try:
            serial_ports = serial.tools.list_ports.comports()
            print(f"[DEBUG] PySerial hat {len(serial_ports)} Ports gefunden.")
            
            for port in serial_ports:
                port_name = port.device
                port_desc = port.description
                print(f"[DEBUG] Port gefunden: {port_name} - {port_desc}")
                ports.append(port_name)
        except Exception as e:
            print(f"[DEBUG] Fehler beim Laden der seriellen Ports: {e}")
        
        # Netzwerk-Ports hinzufügen
        network_ports = [
            'tcp:127.0.0.1:5760',  # SITL
            'udp:127.0.0.1:14550',  # UDP
            'udp:192.168.4.1:14550'  # WiFi
        ]
        ports.extend(network_ports)
        
        self.available_ports = ports
        print(f"[DEBUG] Verfügbare Ports aktualisiert: {ports}")
        print("[DEBUG] Port-Liste hat sich geändert, emittiere Signal")
    
    def connect_to_drone(self, port=None, baudrate=None):
        """Verbindung zum Drohne herstellen"""
        if port:
            self.selected_port = port
        if baudrate:
            self.selected_baudrate = baudrate
        
        print(f"Verbinde zu: {self.selected_port} mit Baudrate: {self.selected_baudrate}")
        
        # Verbindungsstring erstellen
        if self.selected_port.startswith('COM'):
            # Serieller Port
            connection_string = self.selected_port
        else:
            # Netzwerk-Port (TCP/UDP)
            connection_string = self.selected_port
        
        print(f"Verbindungsstring erstellt: {connection_string}")
        
        # PyMAVLink-Verbindung herstellen
        success = self.mavlink_connector.connect_to_vehicle(connection_string)
        
        if success:
            print("Verbindung erfolgreich hergestellt")
        else:
            print("Verbindung fehlgeschlagen")
        
        return success
    
    def disconnect_from_drone(self):
        """Verbindung trennen"""
        self.mavlink_connector.disconnect()
    
    @Property(list, notify=connectedChanged)
    def ports(self):
        return self.available_ports
    
    @Property(str, notify=connectedChanged)
    def selectedPort(self):
        return self.selected_port
    
    @Property(int, notify=connectedChanged)
    def selectedBaudrate(self):
        return self.selected_baudrate
    
    @Property(bool, notify=connectedChanged)
    def isConnected(self):
        return self.connected

def main():
    # Qt-Anwendung initialisieren
    QCoreApplication.setApplicationName("RZGCS")
    QCoreApplication.setOrganizationName("RZ Solutions")
    QCoreApplication.setOrganizationDomain("rz-solutions.de")
    
    app = QGuiApplication(sys.argv)
    
    # QML-Engine erstellen
    engine = QQmlApplicationEngine()
    
    # Instanzen der Komponenten erstellen
    logger = SimpleLogger()
    message_manager = MessageManager()
    firmware_vm = FirmwareViewModel()
    
    # PyMAVLink-Komponenten erstellen
    serial_connector = MavlinkSerialConnector()
    sensor_viewmodel = DroneKitSensorViewModel()
    mission_planner_viewmodel = MissionPlannerViewModel(serial_connector)
    
    # Verbindung zwischen Serial Connector und Sensor ViewModel herstellen
    serial_connector.attitudeChanged.connect(sensor_viewmodel.set_attitude)
    serial_connector.gpsChanged.connect(sensor_viewmodel.set_gps_position)
    serial_connector.batteryChanged.connect(sensor_viewmodel.set_battery_status)
    
    # Status- und Log-Verbindungen für die UI
    serial_connector.connectionStatusChanged.connect(lambda status: message_manager.updateConnectionStatus(
        status == serial_connector.CONNECTION_STATUS_CONNECTED,
        "Verbunden" if status == serial_connector.CONNECTION_STATUS_CONNECTED else "Getrennt"
    ))
    
    # Alle Komponenten als Context Properties für QML verfügbar machen
    engine.rootContext().setContextProperty("serialConnector", serial_connector)
    engine.rootContext().setContextProperty("sensorViewModel", sensor_viewmodel)
    engine.rootContext().setContextProperty("missionPlannerViewModel", mission_planner_viewmodel)
    engine.rootContext().setContextProperty("messageManager", message_manager)
    engine.rootContext().setContextProperty("logger", logger)
    engine.rootContext().setContextProperty("firmwareVm", firmware_vm)
    
    # Zusätzliche Context Properties für QML-Kompatibilität
    engine.rootContext().setContextProperty("connectionViewModel", serial_connector)  # Alias für serialConnector
    engine.rootContext().setContextProperty("parameterModel", None)  # Wird später implementiert
    
    # Pfad für QML-Dateien konfigurieren
    qml_path = Path(__file__).parent.parent
    engine.addImportPath(str(qml_path))
    
    # QML-Import-Pfade konfigurieren
    QDir.addSearchPath("icon", str(qml_path / "icon"))
    QDir.addSearchPath("qmlimport", str(qml_path / "qmlimport"))
    QDir.addSearchPath("assets", str(qml_path / "assets"))
    QDir.addSearchPath("components", str(qml_path / "RZGCSContent" / "Components"))
    QDir.addSearchPath("images", str(qml_path / "RZGCSContent" / "images"))
    QDir.addSearchPath("Connection", str(qml_path / "RZGCSContent" / "Connection"))
    
    # Dummy-Module-Pfad hinzufügen
    dummy_qml_path = qml_path / "RZGCSContent" / "Dummy"
    os.makedirs(str(dummy_qml_path), exist_ok=True)
    engine.addImportPath(str(qml_path / "RZGCSContent"))
    
    # Dummy QML Komponenten registrieren
    DummyQmlComponents.register_dummy_types(engine)
    
    # MessageManager als QML-Typ registrieren
    qmlRegisterType(MessageManager, "RZGCS", 1, 0, "MessageManager")
    
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
    
    # Zuerst testen wir, ob App.qml als Komponente geladen werden kann
    print("\nAnalysiere App.qml...")
    app_component = QQmlComponent(engine)
    app_component.loadUrl(QUrl.fromLocalFile(qml_file_path))
    
    if app_component.isError():
        print("\nFEHLER BEIM LADEN VON APP.QML:")
        for error in app_component.errors():
            print(f"  - {error.toString()}")
    else:
        print("App.qml konnte als Komponente geladen werden!")
    
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
    
    # Erfolgsmeldung
    logger.addLog("RZGCS mit PyMAVLink-Integration gestartet")
    
    # Automatisch die Ports laden
    serial_connector.load_ports()
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main()) 