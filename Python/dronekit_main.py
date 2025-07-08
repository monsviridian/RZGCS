"""
dronekit_main.py - RZGCS mit PyMAVLink-Integration (statt DroneKit)

Diese Version verbindet die bestehende UI mit dem PyMAVLink-Backend
für die direkte Kommunikation mit dem Flugcontroller über COM-Port oder Netzwerk.
"""

# Python 3.13 Kompatibilitätsfix für DroneKit
import collections.abc
import collections
if not hasattr(collections, 'MutableMapping'):
    collections.MutableMapping = collections.abc.MutableMapping

import sys
import os
import enum
from pathlib import Path
from PySide6.QtCore import QCoreApplication, QDir, QObject, QUrl, Signal, QTimer, Property, Slot
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine, qmlRegisterType, QQmlComponent
import datetime
import serial.tools.list_ports
from pymavlink import mavutil
import threading
import time

# Import für die Dummy-Komponenten (für UI-Komponenten, die noch nicht mit DroneKit integriert sind)
from dummy_qml_components import DummyQmlComponents
from dummy_license_controller import DummyLicenseController

# Importiere den PyMAVLink-Connector
from mavlink_connector import MavlinkConnector
from dronekit_sensor_viewmodel import DroneKitSensorViewModel
from viewmodel.mission_planner_viewmodel import MissionPlannerViewModel

# Importiere den ParameterManager
from backend.parameter_manager import ParameterManager
from dronekit_parameter_viewmodel import DroneKitParameterViewModel as ParameterViewModel

# Importiere die FlightNavigationViewModel
from backend.flight_control.viewmodels.flight_navigation_viewmodel import FlightNavigationViewModel
from backend.firmware.firmware_viewmodel import FirmwareViewModel

# Importiere MAVLinkV2Integration
from backend.mavlink_v2_integration import MAVLinkV2Integration
# Importiere ProtocolConnectionManager
from backend.protocol_connection_manager import ProtocolConnectionManager
# Importiere CalibrationController
from backend.calibration_controller import CalibrationController

# Einfacher Logger für die UI (unverändert von main_ui_only.py)
class SimpleLogger(QObject):
    logAdded = Signal(str, str)  # type, message
    
    def __init__(self):
        super().__init__()
        self._logs = []
        self._message_callback = None  # Callback für MessageManager
        print("[OK]SimpleLogger initialisiert")
    
    def set_message_callback(self, callback):
        """Setzt eine Callback-Funktion für die Weiterleitung an MessageManager"""
        self._message_callback = callback
        print("[DEBUG] SimpleLogger: Message callback gesetzt")
    
    def addLog(self, message, log_type="INFO"):
        print(f"[{log_type}] {message}")
        self._logs.append({"type": log_type, "message": message})
        self.logAdded.emit(log_type, message)
        
        # Forward to MessageManager if callback is set
        if self._message_callback:
            try:
                # Determine message type based on content
                message_type = self._determine_message_type(message)
                self._message_callback(message, message_type)
            except Exception as e:
                print(f"[ERROR] SimpleLogger: Fehler beim Weiterleiten an MessageManager: {e}")
    
    def _determine_message_type(self, message):
        """Bestimmt den Message-Typ basierend auf dem Inhalt"""
        message_lower = message.lower()
        
        # Error messages
        if any(keyword in message_lower for keyword in ['error', 'failed', 'fehlgeschlagen', 'ungültig']):
            return 3  # Error
        
        # Warning messages
        if any(keyword in message_lower for keyword in ['warn', 'warning', 'warnung']):
            return 2  # Warning
        
        # Success messages
        if any(keyword in message_lower for keyword in ['ok', 'success', 'erfolgreich', 'connected', 'verbunden']):
            return 4  # Success
        
        # Debug messages
        if message.startswith('[DEBUG]') or message.startswith('[FIRMWARE]'):
            return 1  # Info
        
        # Default to info
        return 1  # Info
    
    def getLogs(self):
        return self._logs

# MessageManager-Klasse für Benachrichtigungen (unverändert von main_ui_only.py)
class MessageManager(QObject):
    # Signal-Definitionen
    messageAdded = Signal(str, int)  # message, type
    connectionStatusChanged = Signal(bool, str)  # isConnected, statusText
    messagesChanged = Signal()  # <-- Neu für QML-Update
    
    # Enum für Nachrichtentypen
    class MessageType(enum.IntEnum):
        Info = 1
        Warning = 2
        Error = 3
        Success = 4
    
    def __init__(self):
        super().__init__()
        self._messages = []
        print("[OK]MessageManager initialisiert")
        # Test-Message beim Start hinzufügen
        self.addMessage("System initialized - MessageManager ready", 1)
    
    @Slot(str, int)
    def addMessage(self, message, message_type=1):  # Default: Info
        self._messages.append({"message": message, "type": message_type})
        self.messageAdded.emit(message, message_type)
        self.messagesChanged.emit()  # <-- Wichtig für QML
        print(f"MessageManager: addMessage [{{'message': '{message}', 'type': {message_type}}}]")
    
    @Slot(bool, str)
    def updateConnectionStatus(self, isConnected, statusText):
        self.connectionStatusChanged.emit(isConnected, statusText)
        print(f"Connection status: {isConnected}, {statusText}")
    
    @Property(list, notify=messagesChanged)
    def messages(self):
        """Property für QML-Zugriff auf die Nachrichten"""
        return self._messages
    
    @Slot()
    def clearMessages(self):
        """Alle Nachrichten löschen"""
        self._messages.clear()
        self.messagesChanged.emit()
        print("[OK]MessageManager: Alle Nachrichten gelöscht")

# PyMAVLink Serial Connector (Ersatz für DroneKitSerialConnector)
class MavlinkSerialConnector(QObject):
    connectedChanged = Signal(bool)
    connectionStatusChanged = Signal(int)
    gpsChanged = Signal(float, float, float)
    attitudeChanged = Signal(float, float, float)
    batteryChanged = Signal(float, float, float)  # voltage, current, remaining
    statusMessageChanged = Signal(str)
    portsChanged = Signal()  # Neues Signal für Port-Änderungen
    # --- WICHTIG: Parameter-Signale für ViewModel ---
    parameters_received = Signal(object)
    parameter_updated = Signal(str, float)
    parameter_write_complete = Signal(str, bool)
    # --- ENDE: Parameter-Signale ---
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
        self.mavlink_connector.connected.connect(self._on_connected)
        self.mavlink_connector.disconnected.connect(self._on_disconnected)
        self.mavlink_connector.connection_failed.connect(self._on_connection_failed)
        self.mavlink_connector.gps_updated.connect(self.gpsChanged)
        self.mavlink_connector.attitude_updated.connect(self.attitudeChanged)
        self.mavlink_connector.battery_updated.connect(self._on_battery_updated)
        self.mavlink_connector.status_updated.connect(self.statusMessageChanged)
        print("[OK]MavlinkSerialConnector initialisiert")
    def _on_connected(self):
        self.connected = True
        self.connectedChanged.emit(True)
        self.connectionStatusChanged.emit(self.CONNECTION_STATUS_CONNECTED)
        print("[OK][MAVLINK] Verbindung erfolgreich")
        
        # Message senden, wenn message_manager verfügbar ist
        if hasattr(self, 'message_manager') and self.message_manager:
            self.message_manager.addMessage("MAVLink-Verbindung erfolgreich hergestellt", 4)
        
        # Systeminfos ins Message Panel loggen
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        msg = f"Verbunden mit Port: {self.selected_port}, Baudrate: {self.selected_baudrate} ({timestamp})"
        fc_type = getattr(self.mavlink_connector.connection, 'autopilot', None)
        if fc_type:
            msg += f"\nFC-Typ: {fc_type}"
        firmware = getattr(self.mavlink_connector.connection, 'version', None)
        if firmware:
            msg += f"\nFirmware: {firmware}"
        if hasattr(self, 'message_manager') and self.message_manager:
            self.message_manager.addMessage(msg, 4)
        else:
            print(f"[INFO] {msg}")
    def _on_disconnected(self):
        self.connected = False
        self.connectedChanged.emit(False)
        self.connectionStatusChanged.emit(self.CONNECTION_STATUS_DISCONNECTED)
        print("[OK][MAVLINK] Verbindung getrennt")
        
        # Message senden, wenn message_manager verfügbar ist
        if hasattr(self, 'message_manager') and self.message_manager:
            self.message_manager.addMessage("MAVLink-Verbindung getrennt", 2)
    def _on_connection_failed(self, error):
        self.connected = False
        self.connectedChanged.emit(False)
        self.connectionStatusChanged.emit(self.CONNECTION_STATUS_FAILED)
        print(f"[OK][MAVLINK] Verbindung fehlgeschlagen: {error}")
        
        # Message senden, wenn message_manager verfügbar ist
        if hasattr(self, 'message_manager') and self.message_manager:
            self.message_manager.addMessage(f"MAVLink-Verbindung fehlgeschlagen: {error}", 3)
        
        # Fehler ins Message Panel loggen
        if hasattr(self, 'message_manager') and self.message_manager:
            self.message_manager.addMessage(f"Verbindung fehlgeschlagen: {error}", 3)
        else:
            print(f"[ERROR] Verbindung fehlgeschlagen: {error}")
    def _on_battery_updated(self, voltage):
        """Adapter für Battery-Signal: Konvertiert single voltage zu drei Parametern"""
        # Dummy-Werte für current und remaining
        current = 0.0
        remaining = 100
        self.batteryChanged.emit(voltage, current, remaining)
    @Slot()
    def load_ports(self):
        # Message senden, wenn message_manager verfügbar ist
        if hasattr(self, 'message_manager') and self.message_manager:
            self.message_manager.addMessage("Starte Port-Erkennung...", 1)
        
        import serial.tools.list_ports
        print("[OK][DEBUG] Starte Port-Erkennung...")
        ports = []
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
        network_ports = [
            'tcp:127.0.0.1:5760',
            'udp:127.0.0.1:14550',
            'udp:192.168.4.1:14550'
        ]
        ports.extend(network_ports)
        self.available_ports = ports
        print(f"[DEBUG] Verfügbare Ports aktualisiert: {ports}")
        print("[OK][DEBUG] Port-Liste hat sich geändert, emittiere Signal")
        self.portsChanged.emit()
        
        # Message senden, wenn message_manager verfügbar ist
        if hasattr(self, 'message_manager') and self.message_manager:
            self.message_manager.addMessage(f"Port-Erkennung abgeschlossen: {len(ports)} Ports gefunden", 1)
    @Slot(str, int)
    def connect_to_drone(self, port, baudrate=115200):
        self.selected_port = port
        self.selected_baudrate = baudrate
        print(f"Verbinde zu: {self.selected_port} mit Baudrate: {self.selected_baudrate}")
        
        # Message senden, wenn message_manager verfügbar ist
        if hasattr(self, 'message_manager') and self.message_manager:
            self.message_manager.addMessage(f"Verbinde zu: {self.selected_port} mit Baudrate: {self.selected_baudrate}", 1)
        
        connection_string = self.selected_port
        print(f"Verbindungsstring erstellt: {connection_string}")
        success = self.mavlink_connector.connect_to_vehicle(connection_string)
        if success:
            print("[OK]Verbindung erfolgreich hergestellt")
            # Message senden, wenn message_manager verfügbar ist
            if hasattr(self, 'message_manager') and self.message_manager:
                self.message_manager.addMessage("Verbindung erfolgreich hergestellt", 4)
        else:
            print("[OK]Verbindung fehlgeschlagen")
            # Message senden, wenn message_manager verfügbar ist
            if hasattr(self, 'message_manager') and self.message_manager:
                self.message_manager.addMessage("Verbindung fehlgeschlagen", 3)
        return success
    @Slot(str)
    def setPort(self, port):
        """Port setzen (für QML-Kompatibilität)"""
        self.selected_port = port
        print(f"Port gesetzt: {port}")
        
        # Message senden, wenn message_manager verfügbar ist
        if hasattr(self, 'message_manager') and self.message_manager:
            self.message_manager.addMessage(f"Port gesetzt: {port}", 1)
    @Slot(int)
    def setBaudRate(self, baudrate):
        """Baudrate setzen (für QML-Kompatibilität)"""
        self.selected_baudrate = baudrate
        print(f"Baudrate gesetzt: {baudrate}")
        
        # Message senden, wenn message_manager verfügbar ist
        if hasattr(self, 'message_manager') and self.message_manager:
            self.message_manager.addMessage(f"Baudrate gesetzt: {baudrate}", 1)
    @Slot()
    def disconnect_from_drone(self):
        # Message senden, wenn message_manager verfügbar ist
        if hasattr(self, 'message_manager') and self.message_manager:
            self.message_manager.addMessage("Trenne Verbindung...", 2)
        
        self.mavlink_connector.disconnect()
    @Slot()
    def disconnect(self):
        """Disconnect-Methode für QML-Kompatibilität"""
        # Message senden, wenn message_manager verfügbar ist
        if hasattr(self, 'message_manager') and self.message_manager:
            self.message_manager.addMessage("Trenne Verbindung...", 2)
        
        self.disconnect_from_drone()
    @Slot()
    def connect(self):
        """Connect-Methode für QML-Kompatibilität (ohne Parameter)"""
        # Message senden, wenn message_manager verfügbar ist
        if hasattr(self, 'message_manager') and self.message_manager:
            self.message_manager.addMessage(f"Verbinde zu: {self.selected_port} mit Baudrate: {self.selected_baudrate}", 1)
        
        return self.connect_to_drone(self.selected_port, self.selected_baudrate)
    @Slot(str)
    def connectWithPort(self, port):
        """Connect-Methode mit Port-Parameter für QML-Kompatibilität"""
        # Message senden, wenn message_manager verfügbar ist
        if hasattr(self, 'message_manager') and self.message_manager:
            self.message_manager.addMessage(f"Verbinde zu: {port} mit Baudrate: {self.selected_baudrate}", 1)
        
        return self.connect_to_drone(port, self.selected_baudrate)
    @Property(list, notify=portsChanged)
    def ports(self):
        return self.available_ports
    @Property(list, notify=portsChanged)
    def availablePorts(self):
        """Alias für ports (QML-Kompatibilität)"""
        return self.available_ports
    @Property(list, notify=portsChanged)
    def availableBaudRates(self):
        """Verfügbare Baudraten für QML"""
        return [9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600]
    @Property(str, notify=connectedChanged)
    def selectedPort(self):
        return self.selected_port
    @Property(int, notify=connectedChanged)
    def selectedBaudrate(self):
        return self.selected_baudrate
    @Property(bool, notify=connectedChanged)
    def isConnected(self):
        return self.connected
    def get_vehicle(self):
        """Dummy für Mission Planner Kompatibilität"""
        return None
    def set_message_manager(self, mm):
        self.message_manager = mm

    def _mavset(self, name, value, parm_type=None, retries=3):
        '''Set a parameter on a mavlink connection with type safety and retries.'''
        mav = self.mavlink_connector.connection
        got_ack = False
        import struct
        from pymavlink import mavutil

        if parm_type is not None and parm_type != mavutil.mavlink.MAV_PARAM_TYPE_REAL32:
            # need to encode as a float for sending
            if parm_type == mavutil.mavlink.MAV_PARAM_TYPE_UINT8:
                vstr = struct.pack(">xxxB", int(value))
            elif parm_type == mavutil.mavlink.MAV_PARAM_TYPE_INT8:
                vstr = struct.pack(">xxxb", int(value))
            elif parm_type == mavutil.mavlink.MAV_PARAM_TYPE_UINT16:
                vstr = struct.pack(">xxH", int(value))
            elif parm_type == mavutil.mavlink.MAV_PARAM_TYPE_INT16:
                vstr = struct.pack(">xxh", int(value))
            elif parm_type == mavutil.mavlink.MAV_PARAM_TYPE_UINT32:
                vstr = struct.pack(">I", int(value))
            elif parm_type == mavutil.mavlink.MAV_PARAM_TYPE_INT32:
                vstr = struct.pack(">i", int(value))
            else:
                print(f"[ERROR] Can't send {name} of type {parm_type}")
                return False
            numeric_value, = struct.unpack(">f", vstr)
        else:
            if isinstance(value, str) and value.lower().startswith('0x'):
                numeric_value = int(value[2:], 16)
            else:
                numeric_value = float(value)

        while retries > 0 and not got_ack:
            retries -= 1
            mav.mav.param_set_send(
                mav.target_system,
                mav.target_component,
                name.encode('utf-8'),
                numeric_value,
                parm_type if parm_type is not None else mavutil.mavlink.MAV_PARAM_TYPE_REAL32
            )
            tstart = time.time()
            while time.time() - tstart < 1:
                ack = mav.recv_match(type='PARAM_VALUE', blocking=False)
                if ack is None:
                    time.sleep(0.1)
                    continue
                param_id = ack.param_id.rstrip('\x00')
                if str(name).upper() == str(param_id).upper():
                    got_ack = True
                    break
        if not got_ack:
            print(f"[ERROR] Timeout setting {name} to {numeric_value}")
            return False
        return True

    def write_parameter(self, name, value, parm_type=None):
        """Set a parameter on the FC and emit parameter_write_complete when done, with type safety."""
        if not self.mavlink_connector.connection:
            print("[ERROR] No MAVLink connection for parameter write")
            self.parameter_write_complete.emit(name, False)
            return
        try:
            print(f"[MAVLINK] Setting parameter {name} = {value}")
            success = self._mavset(name, value, parm_type)
            if success:
                self.parameter_updated.emit(name, float(value))
            self.parameter_write_complete.emit(name, success)
        except Exception as e:
            print(f"[ERROR] Parameter write failed: {e}")
            self.parameter_write_complete.emit(name, False)

    @Slot(str)
    def save_parameters_to_file(self, filename):
        '''Save all parameters to a file.'''
        if not hasattr(self, 'last_parameters') or not self.last_parameters:
            print("[ERROR] No parameters to save.")
            return False
        try:
            with open(filename, 'w') as f:
                keys = sorted(self.last_parameters.keys())
                count = 0
                for param_name in keys:
                    value = self.last_parameters[param_name]['value']
                    if isinstance(value, float):
                        f.write(f"{param_name:<16} {value}\n")
                    else:
                        f.write(f"{param_name:<16} {str(value)}\n")
                    count += 1
            print(f"[OK] Saved {count} parameters to {filename}")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to save parameters: {e}")
            return False

    @Slot(str)
    def load_parameters_from_file(self, filename):
        '''Load parameters from a file and write them to the FC.'''
        try:
            with open(filename, 'r') as f:
                count = 0
                for line in f:
                    line = line.strip()
                    if not line or line[0] == "#":
                        continue
                    line = line.replace(',', ' ')
                    parts = line.split()
                    if len(parts) != 2:
                        print(f"[ERROR] Invalid line: {line}")
                        continue
                    param_name = parts[0]
                    value_str = parts[1].strip()
                    if value_str.lower().startswith('0x'):
                        value = int(value_str[2:], 16)
                    else:
                        value = float(value_str)
                    self.write_parameter(param_name, value)
                    count += 1
            print(f"[OK] Loaded and wrote {count} parameters from {filename}")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to load parameters: {e}")
            return False

    def fetch_parameters(self):
        """Fetch all parameters from the FC and emit parameters_received when done."""
        if not self.mavlink_connector.connection:
            print("[ERROR] No MAVLink connection for parameter fetch")
            return
        try:
            print("[MAVLINK] Requesting all parameters...")
            self.mavlink_connector.connection.mav.param_request_list_send(
                self.mavlink_connector.connection.target_system,
                self.mavlink_connector.connection.target_component
            )
            params = {}
            start_time = time.time()
            timeout = 30
            while time.time() - start_time < timeout:
                msg = self.mavlink_connector.connection.recv_match(type='PARAM_VALUE', blocking=False)
                if msg is None:
                    time.sleep(0.05)
                    continue
                param_id = msg.param_id.rstrip('\x00')
                param_value = msg.param_value
                param_type = msg.param_type
                params[param_id] = {
                    "value": param_value,
                    "type": param_type,
                    "index": msg.param_index,
                    "count": msg.param_count
                }
                if len(params) >= msg.param_count:
                    break
            print(f"[MAVLINK] Received {len(params)} parameters")
            self.last_parameters = params  # For save/restore
            self.parameters_received.emit(params)
        except Exception as e:
            print(f"[ERROR] Parameter fetch failed: {e}")

    def is_connected(self):
        return self.connected

def get_qml_base_path():
    """Ermittelt den Basis-Pfad für QML-Dateien, kompatibel mit PyInstaller und Entwicklung"""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller: _MEIPASS ist das temp-Verzeichnis mit allen Ressourcen
        return Path(sys._MEIPASS) / "RZGCSContent"
    else:
        # Entwicklung: Relativ zum Projektverzeichnis
        return Path(__file__).parent.parent / "RZGCSContent"

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
    firmware_viewmodel = FirmwareViewModel()
    
    # Verbinde Logger mit MessageManager
    logger.set_message_callback(message_manager.addMessage)
    
    # Test-Message beim Start der Anwendung
    message_manager.addMessage("RZGCS mit PyMAVLink-Integration gestartet", 4)
    message_manager.addMessage("Qt-Anwendung initialisiert", 1)
    message_manager.addMessage("QML-Engine erstellt", 1)
    
    # DroneKit-Komponenten erstellen
    serial_connector = MavlinkSerialConnector()
    serial_connector.set_message_manager(message_manager)
    sensor_viewmodel = DroneKitSensorViewModel()
    mission_planner_viewmodel = MissionPlannerViewModel(serial_connector)
    
    # Parameter-Manager erstellen
    parameter_manager = ParameterManager()
    parameter_viewmodel = ParameterViewModel(serial_connector)  # DroneKit-Connector übergeben
    
    # FlightNavigationViewModel für das Flight-Tab
    flight_navigation_viewmodel = FlightNavigationViewModel()
    # FirmwareViewModel für das Firmware-Tab
    firmware_viewmodel = FirmwareViewModel()
    
    # Verbinde SerialConnector mit MessageManager für Logger-Integration
    if hasattr(serial_connector, 'set_message_manager'):
        serial_connector.set_message_manager(message_manager)
    
    # Test-Messages für Komponenten-Erstellung
    message_manager.addMessage("MavlinkSerialConnector erstellt", 1)
    message_manager.addMessage("DroneKitSensorViewModel erstellt", 1)
    message_manager.addMessage("MissionPlannerViewModel erstellt", 1)
    message_manager.addMessage("ParameterManager erstellt", 1)
    message_manager.addMessage("ParameterViewModel erstellt", 1)
    message_manager.addMessage("FlightNavigationViewModel erstellt", 1)
    message_manager.addMessage("MessageManager an SerialConnector übergeben", 1)
    
    # Verbindung zwischen Serial Connector und Sensor ViewModel herstellen
    serial_connector.attitudeChanged.connect(sensor_viewmodel.set_attitude)
    serial_connector.gpsChanged.connect(sensor_viewmodel.set_gps_position)
    
    # Parameter-Manager mit MAVLink-Verbindung verbinden
    serial_connector.connectedChanged.connect(lambda connected: 
        parameter_manager.set_mavlink_connection(
            serial_connector.mavlink_connector.connection if connected else None
        )
    )
    
    # ParameterViewModel mit SerialConnector verbinden
    serial_connector.connectedChanged.connect(lambda connected:
        parameter_viewmodel.set_drone_connector(serial_connector if connected else None)
    )
    
    # Direkte Verbindung der Parameter-Signale
    serial_connector.parameters_received.connect(parameter_viewmodel._on_parameters_received)
    serial_connector.parameter_updated.connect(parameter_viewmodel._on_parameter_updated)
    serial_connector.parameter_write_complete.connect(parameter_viewmodel._on_parameter_write_complete)
    
    # Automatisches Parameter-Laden nach Verbindung
    serial_connector.connectedChanged.connect(lambda connected:
        parameter_viewmodel.refreshParameters() if connected else None
    )
    
    # Test-Messages für Signal-Verbindungen
    message_manager.addMessage("Signal-Verbindungen hergestellt", 1)
    
    # Status- und Log-Verbindungen für die UI
    serial_connector.connectionStatusChanged.connect(lambda status: message_manager.updateConnectionStatus(
        status == serial_connector.CONNECTION_STATUS_CONNECTED,
        "Verbunden" if status == serial_connector.CONNECTION_STATUS_CONNECTED else "Getrennt"
    ))
    
    # Zusätzliche Verbindungen für MessageManager
    serial_connector.connectedChanged.connect(lambda connected: 
        message_manager.addMessage(
            f"Verbindungsstatus geändert: {'Verbunden' if connected else 'Getrennt'}", 
            4 if connected else 2
        )
    )
    
    serial_connector.statusMessageChanged.connect(lambda status: 
        message_manager.addMessage(f"Status: {status}", 1)
    )
    
    # Test-Messages für MessageManager-Verbindungen
    message_manager.addMessage("MessageManager-Signal-Verbindungen hergestellt", 1)
    
    # Erstelle ein Dictionary mit allen Komponenten für die QML-Engine
    components = {
        'serial_connector': serial_connector,
        'sensor_viewmodel': sensor_viewmodel,
        'mission_planner_viewmodel': mission_planner_viewmodel,
        'parameter_viewmodel': parameter_viewmodel,
        'message_manager': message_manager,
        'logger': logger,
        'firmware_vm': firmware_viewmodel,
        'flight_navigation_viewmodel': flight_navigation_viewmodel
    }
    
    # Test-Messages für Dictionary-Erstellung
    message_manager.addMessage("Komponenten-Dictionary erstellt", 1)
    
    # Alle Komponenten als Context Properties für QML verfügbar machen
    engine.rootContext().setContextProperty("serialConnector", serial_connector)
    engine.rootContext().setContextProperty("sensorViewModel", sensor_viewmodel)
    engine.rootContext().setContextProperty("missionPlannerViewModel", mission_planner_viewmodel)
    engine.rootContext().setContextProperty("parameterViewModel", parameter_viewmodel)
    engine.rootContext().setContextProperty("messageManager", message_manager)
    engine.rootContext().setContextProperty("logger", logger)
    engine.rootContext().setContextProperty("firmwareViewModel", firmware_viewmodel)
    engine.rootContext().setContextProperty("firmware_vm", firmware_viewmodel)  # Alternative name for compatibility
    engine.rootContext().setContextProperty("flightNavigationViewModel", flight_navigation_viewmodel)
    engine.rootContext().setContextProperty("missionViewModel", mission_planner_viewmodel)  # Add missing missionViewModel
    engine.rootContext().setContextProperty("flightViewModel", flight_navigation_viewmodel)  # Alias for compatibility
    
    # Debug: Test missionViewModel
    test_mission = engine.rootContext().contextProperty("missionViewModel")
    if test_mission:
        print(f"[OK] missionViewModel erfolgreich gesetzt: {test_mission}")
        message_manager.addMessage("missionViewModel Context Property erfolgreich", 4)
    else:
        print("[ERROR] missionViewModel konnte nicht gesetzt werden")
        message_manager.addMessage("missionViewModel Context Property fehlgeschlagen", 3)
    
    # Test-Messages für Context Properties
    message_manager.addMessage("Context Properties für QML gesetzt", 1)
    message_manager.addMessage("messageManager als Context Property verfügbar", 1)
    
    # Zusätzliche Context Properties für QML-Kompatibilität
    engine.rootContext().setContextProperty("connectionViewModel", serial_connector)  # Alias für serialConnector
    engine.rootContext().setContextProperty("parameterModel", parameter_viewmodel.parameterModel)  # Parameter-Model für QML
    
    # Stelle sicher, dass der logger auch direkt verfügbar ist
    engine.rootContext().setContextProperty("logger", logger)
    
    # Instantiate and expose MAVLinkV2Integration for the new MAVLink 2 tab
    mavlink_v2_backend = MAVLinkV2Integration()
    mavlink_v2_backend.set_message_manager(message_manager)  # Connect message manager
    engine.rootContext().setContextProperty("mavlinkV2Backend", mavlink_v2_backend)
    
    # Create and expose ProtocolConnectionManager for protocol switching
    protocol_connection_manager = ProtocolConnectionManager(mavlink_v2_backend)
    protocol_connection_manager.setMavlinkV1Connector(serial_connector)
    protocol_connection_manager.setMessageManager(message_manager)  # Connect message manager
    engine.rootContext().setContextProperty("protocolConnectionManager", protocol_connection_manager)
    
    # Debug: Test Context Properties
    test_mavlink = engine.rootContext().contextProperty("mavlinkV2Backend")
    test_protocol = engine.rootContext().contextProperty("protocolConnectionManager")
    if test_mavlink:
        print(f"[OK] mavlinkV2Backend erfolgreich gesetzt: {test_mavlink}")
        message_manager.addMessage("mavlinkV2Backend Context Property erfolgreich", 4)
    else:
        print("[ERROR] mavlinkV2Backend konnte nicht gesetzt werden")
        message_manager.addMessage("mavlinkV2Backend Context Property fehlgeschlagen", 3)
        
    if test_protocol:
        print(f"[OK] protocolConnectionManager erfolgreich gesetzt: {test_protocol}")
        message_manager.addMessage("protocolConnectionManager Context Property erfolgreich", 4)
    else:
        print("[ERROR] protocolConnectionManager konnte nicht gesetzt werden")
        message_manager.addMessage("protocolConnectionManager Context Property fehlgeschlagen", 3)
    
    # CalibrationController erstellen und für QML verfügbar machen
    calibration_controller = CalibrationController()
    calibration_controller.set_mavlink_connection(serial_connector.mavlink_connector.connection)
    
    # Connect calibration controller logs to message manager
    calibration_controller.logMessageReceived.connect(
        lambda log_type, message: message_manager.addMessage(
            f"[CALIBRATION] {message}", 
            4 if log_type == "success" else (3 if log_type == "error" else (2 if log_type == "warning" else 1))
        )
    )
    
    # Connect calibration progress to message manager
    calibration_controller.calibrationProgressChanged.connect(
        lambda progress, message: message_manager.addMessage(
            f"[CALIBRATION] {message} ({int(progress*100)}%)", 1
        )
    )
    
    # Connect calibration finished to message manager
    calibration_controller.calibrationFinished.connect(
        lambda success, message: message_manager.addMessage(
            f"[CALIBRATION] {message}", 4 if success else 3
        )
    )
    
    engine.rootContext().setContextProperty("calibrationController", calibration_controller)
    
    # FirmwareViewModel initialisieren
    firmware_viewmodel.initialize()
    
    # MessageManager-Verbindung für FirmwareViewModel
    firmware_viewmodel.set_message_manager(message_manager)
    
    # Debug: Test FirmwareViewModel
    test_firmware = engine.rootContext().contextProperty("firmwareViewModel")
    if test_firmware:
        print(f"[OK] firmwareViewModel erfolgreich gesetzt: {test_firmware}")
        message_manager.addMessage("firmwareViewModel Context Property erfolgreich", 4)
    else:
        print("[ERROR] firmwareViewModel konnte nicht gesetzt werden")
        message_manager.addMessage("firmwareViewModel Context Property fehlgeschlagen", 3)
    
    # Test-Message für Protocol Connection Manager
    message_manager.addMessage("ProtocolConnectionManager erstellt und für QML verfügbar gemacht", 1)
    message_manager.addMessage("MAVLink v1/v2 Protokoll-Umschaltung implementiert", 4)
    message_manager.addMessage("CalibrationController erstellt und für QML verfügbar gemacht", 1)
    
    # Test-Message für FirmwareViewModel
    message_manager.addMessage("FirmwareViewModel initialisiert und für QML verfügbar", 1)
    
    # Test-Message für zusätzliche Context Properties
    message_manager.addMessage("Zusätzliche Context Properties gesetzt", 1)
    
    # Stelle sicher, dass der context messageManager auch für Screen01.ui.qml verfügbar ist
    print("[OK]messageManager wird für StatusBar bereitgestellt")
    
    # Debug: Teste ob messageManager korrekt gesetzt wurde
    test_message_manager = engine.rootContext().contextProperty("messageManager")
    if test_message_manager:
        print(f"[OK] messageManager erfolgreich als Context Property gesetzt: {test_message_manager}")
        # Test-Message senden
        test_message_manager.addMessage("Test-Message: Context Property erfolgreich gesetzt", 1)
        message_manager.addMessage("Context Property Test erfolgreich", 4)
    else:
        print("[OK] messageManager konnte nicht als Context Property gesetzt werden")
        message_manager.addMessage("Context Property Test fehlgeschlagen", 3)
    
    # QML-Dateipfad korrekt bestimmen
    qml_base_path = get_qml_base_path()
    qml_file = qml_base_path / "App.qml"
    qml_file_path = str(qml_file)
    print(f"Lade Hauptanwendungs-QML-Datei: {qml_file_path}")
    message_manager.addMessage(f"Lade Hauptanwendungs-QML-Datei: {qml_file_path}", 1)
    
    # QML-Import-Pfade konfigurieren
    engine.addImportPath(str(qml_base_path))
    engine.addImportPath(str(qml_base_path / "Utils"))
    engine.addImportPath(str(qml_base_path / "Components"))
    QDir.addSearchPath("icon", str(qml_base_path / "icon"))
    QDir.addSearchPath("qmlimport", str(qml_base_path / "qmlimport"))
    QDir.addSearchPath("assets", str(qml_base_path / "assets"))
    QDir.addSearchPath("components", str(qml_base_path / "Components"))
    QDir.addSearchPath("images", str(qml_base_path / "images"))
    QDir.addSearchPath("Connection", str(qml_base_path / "Connection"))
    
    # Test-Messages für QML-Pfad-Konfiguration
    message_manager.addMessage("QML-Pfade konfiguriert", 1)
    
    # Dummy-Module-Pfad hinzufügen
    dummy_qml_path = qml_base_path / "Dummy"
    os.makedirs(str(dummy_qml_path), exist_ok=True)
    engine.addImportPath(str(qml_base_path))
    
    # Test-Messages für Dummy-Module-Pfad
    message_manager.addMessage("Dummy-Module-Pfad hinzugefügt", 1)
    
    # Dummy QML Komponenten registrieren
    DummyQmlComponents.register_dummy_types(engine)
    
    # Test-Messages für Dummy-QML-Komponenten
    message_manager.addMessage("Dummy-QML-Komponenten registriert", 1)
    
    # MessageManager als QML-Typ registrieren
    # qmlRegisterType(MessageManager, "RZGCS", 1, 0, "MessageManager")
    
    # Test-Messages für QML-Typ-Registrierung
    message_manager.addMessage("QML-Typen registriert", 1)
    message_manager.addMessage("MessageManager als QML-Typ registriert", 1)
    
    # Debug-Ausgabe für QML-Pfad
    print(f"QML-Pfad: {qml_base_path}")
    message_manager.addMessage(f"QML-Pfad: {qml_base_path}", 1)
    
    # Prüfen, ob die Datei existiert
    if not qml_file.exists():
        print(f"FEHLER: QML-Datei nicht gefunden: {qml_file_path}")
        message_manager.addMessage(f"FEHLER: QML-Datei nicht gefunden: {qml_file_path}", 3)
        return -1
        
    # Test-Message für QML-Datei gefunden
    message_manager.addMessage(f"QML-Datei gefunden: {qml_file_path}", 1)
        
    # QML-Debug und Fehlerberichterstattung aktivieren
    os.environ["QT_VERBOSE_ERRORS"] = "1"
    os.environ["QT_MESSAGE_PATTERN"] = "%{if-debug}D%{endif}%{if-warning}W%{endif}%{if-critical}C%{endif}%{if-fatal}F%{endif}: %{message}"
    os.environ["QML_IMPORT_TRACE"] = "1"
    os.environ["QT_LOGGING_RULES"] = "qt.qml.connections=true;qt.quick.import=true;qt.scenegraph.general=true"
    
    # Test-Messages für QML-Debug-Aktivierung
    message_manager.addMessage("QML-Debug aktiviert", 1)
    
    # Zuerst testen wir, ob App.qml als Komponente geladen werden kann, um Fehler zu sehen
    print("[OK]\nAnalysiere App.qml...")
    message_manager.addMessage("Analysiere App.qml...", 1)
    app_component = QQmlComponent(engine)
    app_component.loadUrl(QUrl.fromLocalFile(qml_file_path))
    
    if app_component.isError():
        print("[OK]\nFEHLER BEIM LADEN VON APP.QML:")
        message_manager.addMessage("FEHLER BEIM LADEN VON APP.QML:", 3)
        for error in app_component.errors():
            print(f"  - {error.toString()}")
            message_manager.addMessage(f"QML-Fehler: {error.toString()}", 3)
    else:
        print("[OK]App.qml konnte als Komponente geladen werden!")
        message_manager.addMessage("App.qml konnte als Komponente geladen werden!", 4)
    
    # Funktion zum Abfangen von Status-Änderungen
    def on_status_changed(obj, url):
        if obj is None:
            print(f"Engine konnte kein Root-Objekt für URL erstellen: {url}")
        else:
            print(f"Engine hat Root-Objekt erfolgreich erstellt: {obj}")
            # Test-Message senden, wenn QML erfolgreich geladen wurde
            message_manager.addMessage("QML-UI erfolgreich initialisiert", 4)
            # Zusätzliche Test-Message nach QML-Load
            message_manager.addMessage("Test: MessageManager-Verbindung nach QML-Load", 1)
            
    engine.objectCreated.connect(on_status_changed)
        
    # QML-Datei laden
    message_manager.addMessage("Lade QML-Datei...", 1)
    engine.load(QUrl.fromLocalFile(qml_file_path))
    
    # Prüfen, ob QML-Datei geladen wurde
    if not engine.rootObjects():
        print(f"FEHLER: Keine Root-Objekte nach dem Laden von {qml_file_path}")
        message_manager.addMessage(f"FEHLER: Keine Root-Objekte nach dem Laden von {qml_file_path}", 3)
        return -1
    
    # Erfolgsmeldung
    logger.addLog("RZGCS mit PyMAVLink-Integration gestartet")
    message_manager.addMessage("QML-Datei erfolgreich geladen", 4)
    message_manager.addMessage("RZGCS bereit für Verbindungen", 4)
    message_manager.addMessage("=== Initialisierung abgeschlossen ===", 4)
    
    # Timer für Test-Message nach QML-Load
    test_timer = QTimer()
    test_timer.setSingleShot(True)
    test_timer.timeout.connect(lambda: message_manager.addMessage("Timer-Test: MessageManager nach QML-Load funktioniert", 4))
    test_timer.start(1000)  # 1 Sekunde nach QML-Load
    
    # Automatisch die Ports laden
    message_manager.addMessage("Starte automatische Port-Erkennung...", 1)
    serial_connector.load_ports()
    message_manager.addMessage("Port-Erkennung abgeschlossen", 1)
    message_manager.addMessage("RZGCS vollständig initialisiert und bereit", 4)
    
    # Telemetrie-Signale an das FlightNavigationViewModel weiterleiten
    serial_connector.gpsChanged.connect(
        lambda lat, lon, alt: flight_navigation_viewmodel.set_current_position(lat, lon, alt)
    )
    serial_connector.attitudeChanged.connect(
        lambda roll, pitch, yaw: flight_navigation_viewmodel.set_current_attitude(roll, pitch, yaw)
    )
    serial_connector.batteryChanged.connect(
        lambda voltage, current, remaining: flight_navigation_viewmodel.set_current_battery(voltage)
    )
    
    # Telemetrie-Signale auch an den MAVLinkV2Integration weiterleiten für den MAVLink 2 Tab
    serial_connector.gpsChanged.connect(
        lambda lat, lon, alt: mavlink_v2_backend.update_gps_position(lat, lon, alt)
    )
    serial_connector.attitudeChanged.connect(
        lambda roll, pitch, yaw: mavlink_v2_backend.update_attitude(roll, pitch, yaw)
    )
    serial_connector.batteryChanged.connect(
        lambda voltage, current, remaining: mavlink_v2_backend.update_battery(voltage, current, remaining)
    )
    
    # Verbindungsstatus vom SerialConnector an den MAVLinkV2Integration weiterleiten
    serial_connector.connectedChanged.connect(
        lambda connected: mavlink_v2_backend.connectedChanged.emit(connected)
    )
    
    # Status-Nachrichten vom SerialConnector an den MAVLinkV2Integration weiterleiten
    serial_connector.statusMessageChanged.connect(
        lambda message: mavlink_v2_backend._send_status_message(message, 1)
    )
    
    # Sensor-Kalibrierungsstatus ins Message Panel schreiben
    def on_sensors_to_calibrate_changed(sensor_list):
        if sensor_list:
            message_manager.addMessage(f"Sensoren benötigen Kalibrierung: {', '.join(sensor_list)}", 2)
        # Keine Nachricht mehr, wenn alle Sensoren gesund sind!
    mavlink_v2_backend.sensorsToCalibrateChanged.connect(on_sensors_to_calibrate_changed)
    
    # Nach der Initialisierung von mavlink_v2_integration und parameter_viewmodel:
    if hasattr(mavlink_v2_backend, 'parameterListReceived'):
        mavlink_v2_backend.parameterListReceived.connect(parameter_viewmodel._on_parameters_received)
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
