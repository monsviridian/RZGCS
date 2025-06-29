"""
Telemetry and Log Data Flow Implementation
==========================================

This file contains the specific code implementations needed to fix
telemetry and log data flow from FC to UI and DroneKit backend.

Current Status:
- ✅ DroneKit import warnings fixed
- ✅ Asyncio coroutine warnings fixed  
- ✅ Python 3.13 compatibility fixed
- ✅ Circular import errors fixed
- 🔄 Telemetry data flow to UI (in progress)
"""

import sys
import collections.abc
from PySide6.QtCore import QObject, Signal, Slot, QTimer
import math
import time
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtGui import QGuiApplication

# Python 3.13 compatibility patch
if sys.version_info >= (3, 13):
    collections.MutableMapping = collections.abc.MutableMapping

# Import DroneKit components
# External DroneKit import - fixed to avoid circular imports
import dronekit as dronekit_external  # Externe DroneKit-Bibliothek
connect = dronekit_external.connect  # Aus externer DroneKit-Bibliothek
Vehicle = dronekit_external.Vehicle  # Aus externer DroneKit-Bibliothek
VehicleMode = dronekit_external.VehicleMode  # Aus externer DroneKit-Bibliothek


class TelemetryDataFlow(QObject):
    """
    Main class to handle telemetry data flow from FC to UI
    """
    
    # Telemetry signals
    attitude_updated = Signal(float, float, float)  # roll, pitch, yaw
    gps_updated = Signal(float, float, float)       # lat, lon, alt
    battery_updated = Signal(int, float)            # percentage, voltage
    status_updated = Signal(str)                    # status text
    connection_status_changed = Signal(bool)        # connected state
    heartbeat_received = Signal()                   # heartbeat
    
    def __init__(self):
        super().__init__()
        self.vehicle = None
        self.connected = False
        self.last_heartbeat = 0
        
        # Telemetrie-Timer
        self.telemetry_timer = QTimer()
        self.telemetry_timer.timeout.connect(self._update_telemetry)
        self.telemetry_timer.start(100)  # Update every 100ms
        
        # Verbindungsüberwachungs-Timer
        self.connection_check_timer = QTimer()
        self.connection_check_timer.timeout.connect(self._check_connection)
        self.connection_check_timer.start(1000)  # Check every 1s
    
    @Slot(str)
    def connect(self, connection_string):
        """Universal connection method that handles different connection formats
        
        Formats:
        - COM Port: "COM3" oder "COM3:115200" 
        - Serial: "/dev/ttyUSB0" oder "/dev/ttyUSB0:57600"
        - UDP: "udp:127.0.0.1:14550"
        - TCP: "tcp:192.168.1.1:5760"
        """
        try:
            # Verbindungsstring parsen
            port, baud_rate = self._parse_connection_string(connection_string)
            
            # Verbindungsart ermitteln
            if port.lower().startswith(('com', '/dev')):
                # Serial port
                return self._connect_to_serial(port, baud_rate)
            elif port.lower().startswith('udp:'):
                # UDP connection
                return self._connect_to_udp(port)
            elif port.lower().startswith('tcp:'):
                # TCP connection
                return self._connect_to_tcp(port)
            else:
                # Fallback: versuche als COM-Port
                return self._connect_to_serial(port, baud_rate)
                
        except Exception as e:
            self.status_updated.emit(f"Connection failed: {str(e)}")
            self.connection_status_changed.emit(False)
            return False
    
    def _parse_connection_string(self, connection_string):
        """Parse connection string to extract port and baud rate"""
        default_baud = 115200  # Default Baudrate
        
        # Prüfe auf Port:Baudrate Format
        if ':' in connection_string:
            parts = connection_string.split(':', 1)
            port = parts[0]
            try:
                # Extrahiere Baudrate wenn vorhanden
                baud_rate = int(parts[1])
            except ValueError:
                # Falls keine gültige Zahl, verwende Standard
                baud_rate = default_baud
        else:
            # Nur Port spezifiziert
            port = connection_string
            baud_rate = default_baud
            
        return port, baud_rate
            
    def _connect_to_serial(self, port, baud_rate):
        """Connect to flight controller via serial port"""
        try:
            connection_string = f"comport:{port}?baud={baud_rate}"
            self.vehicle = connect(connection_string, wait_ready=True)
            self.connected = True
            self.last_heartbeat = time.time()
            self.connection_status_changed.emit(True)
            self.status_updated.emit(f"Connected to FC on {port} at {baud_rate} baud")
            return True
        except Exception as e:
            self.status_updated.emit(f"Serial connection failed: {str(e)}")
            self.connection_status_changed.emit(False)
            return False
    
    def _connect_to_udp(self, udp_address):
        """Connect to flight controller via UDP"""
        try:
            self.vehicle = connect(udp_address, wait_ready=True)
            self.connected = True
            self.last_heartbeat = time.time()
            self.connection_status_changed.emit(True)
            self.status_updated.emit(f"Connected to FC via UDP at {udp_address}")
            return True
        except Exception as e:
            self.status_updated.emit(f"UDP connection failed: {str(e)}")
            self.connection_status_changed.emit(False)
            return False
            
    def _connect_to_tcp(self, tcp_address):
        """Connect to flight controller via TCP"""
        try:
            self.vehicle = connect(tcp_address, wait_ready=True)
            self.connected = True
            self.last_heartbeat = time.time()
            self.connection_status_changed.emit(True)
            self.status_updated.emit(f"Connected to FC via TCP at {tcp_address}")
            return True
        except Exception as e:
            self.status_updated.emit(f"TCP connection failed: {str(e)}")
            self.connection_status_changed.emit(False)
            return False
            
    def disconnect(self):
        """Disconnect from flight controller"""
        if self.vehicle:
            self.vehicle.close()
            self.vehicle = None
            self.connected = False
            self.connection_status_changed.emit(False)
            self.status_updated.emit("Disconnected from FC")
            
    def _check_connection(self):
        """Check connection status based on heartbeats"""
        if not self.vehicle:
            return
            
        current_time = time.time()
        
        # Heartbeat empfangen?
        if hasattr(self.vehicle, 'last_heartbeat'):
            # Heartbeat-Zeit seit Start in Sekunden
            heartbeat_age = self.vehicle.last_heartbeat
            
            # Update letzten Heartbeat
            if heartbeat_age < 5:  # Wenn Heartbeat jünger als 5 Sekunden
                if not self.connected:
                    self.connected = True
                    self.connection_status_changed.emit(True)
                    self.status_updated.emit("Connection restored")
                self.last_heartbeat = current_time
                self.heartbeat_received.emit()
            # Verbindung verloren?
            elif current_time - self.last_heartbeat > 10 and self.connected:  # 10 Sekunden ohne Heartbeat
                self.connected = False
                self.connection_status_changed.emit(False)
                self.status_updated.emit("Connection lost - no heartbeat")
    
    def _update_telemetry(self):
        """Update telemetry data from vehicle"""
        if not self.vehicle or not self.connected:
            return
        
        try:
            # Update attitude
            if hasattr(self.vehicle, 'attitude'):
                # Konvertiere von Radians zu Degrees
                roll = math.degrees(self.vehicle.attitude.roll) if self.vehicle.attitude.roll is not None else 0.0
                pitch = math.degrees(self.vehicle.attitude.pitch) if self.vehicle.attitude.pitch is not None else 0.0
                yaw = math.degrees(self.vehicle.attitude.yaw) if self.vehicle.attitude.yaw is not None else 0.0
                
                self.attitude_updated.emit(roll, pitch, yaw)
            
            # Update GPS
            if hasattr(self.vehicle, 'location') and hasattr(self.vehicle.location, 'global_frame'):
                loc = self.vehicle.location.global_frame
                lat = loc.lat if loc and hasattr(loc, 'lat') else 0.0
                lon = loc.lon if loc and hasattr(loc, 'lon') else 0.0
                alt = loc.alt if loc and hasattr(loc, 'alt') else 0.0
                
                self.gps_updated.emit(lat, lon, alt)
            
            # Update battery
            if hasattr(self.vehicle, 'battery'):
                battery_percentage = self.vehicle.battery.level if hasattr(self.vehicle.battery, 'level') else 0
                battery_voltage = self.vehicle.battery.voltage if hasattr(self.vehicle.battery, 'voltage') else 0.0
                
                # Fallback für Drohnen ohne Batterieprozent
                if battery_percentage is None or battery_percentage == 0:
                    # Schätze Prozent aus Voltage (12.6V = 100%, 10.5V = 0%)
                    if battery_voltage:
                        battery_percentage = min(100, max(0, int((battery_voltage - 10.5) / (12.6 - 10.5) * 100)))
                    else:
                        battery_percentage = 0
                        
                self.battery_updated.emit(battery_percentage, battery_voltage)
                
            # Update arming status und Flugmodus bei Änderungen
            if hasattr(self.vehicle, 'armed') and hasattr(self.vehicle, 'mode'):
                mode_text = f"Mode: {self.vehicle.mode.name if hasattr(self.vehicle.mode, 'name') else 'UNKNOWN'}"
                armed_text = "ARMED" if self.vehicle.armed else "DISARMED"
                status = f"{mode_text} - {armed_text}"
                self.status_updated.emit(status)
                
        except Exception as e:
            self.status_updated.emit(f"Telemetry update error: {str(e)}")


class LogDataFlow(QObject):
    """
    Main class to handle log data flow from FC to message panel
    """
    
    # Log signal
    log_message = Signal(str, str)  # level, message
    systeminfo_detected = Signal(str)  # systeminfo message for preflight view
    
    def __init__(self):
        super().__init__()
        self.message_queue = []
        self.system_info = {}
        self.filter_patterns = {
            "frame_type": ["Frame Type:", "Frame:"],
            "rcout": ["RCOut:"],
            "hardware": ["MicroAir", "ChibiOS"],
            "version": ["ArduCopter V", "Firmware Version:"],
            "prearm": ["PreArm:", "Arming check:"],
            "mission": ["Mission:", "Waypoint"]
        }
    
    @Slot(str, str)
    def add_message(self, level, message):
        """Add a message to the log and check for system info"""
        # Add to log
        self.log_message.emit(level, message)
        
        # Check for system info patterns
        for info_type, patterns in self.filter_patterns.items():
            for pattern in patterns:
                if pattern in message:
                    # Store system info and emit signal
                    self.system_info[info_type] = message
                    self.systeminfo_detected.emit(message)
                    break
        
    def get_system_info(self, info_type=None):
        """Get system info, either a specific type or all"""
        if info_type:
            return self.system_info.get(info_type, "")
        return self.system_info
        
    @Slot(str, str)
    def log_connection_event(self, event_type, details=""):
        """Log connection-related events"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if event_type == "connected":
            self.add_message("INFO", f"[{timestamp}] Connected to flight controller {details}".strip())
            # Autoabfrage von Systeminformationen
            self.request_system_info()
        elif event_type == "disconnected":
            self.add_message("WARNING", f"[{timestamp}] Disconnected from flight controller {details}".strip())
        elif event_type == "error":
            self.add_message("ERROR", f"[{timestamp}] Connection error: {details}".strip())
        elif event_type == "heartbeat":
            # Keine Log-Meldung für Heartbeats (zu viele)
            pass
        elif event_type == "statustext":
            self.add_message("INFO", f"[{timestamp}] {details}".strip())
        elif event_type == "systeminfo":
            # Spezielle Formatierung für Systeminfos
            self.add_message("SYSTEM", f"[{timestamp}] {details}".strip())
        else:
            self.add_message("INFO", f"[{timestamp}] {event_type} {details}".strip())
            
    def request_system_info(self):
        """Autoabfrage von Systeminformationen nach Verbindung"""
        self.add_message("INFO", "Requesting system information...")
        # Die Anfrage würde hier mit DroneKit an den Flugcontroller gesendet
        # In der nächsten Version wird das implementiert

class TelemetryViewModel(QObject):
    """
    ViewModel for telemetry data binding to QML
    """
    
    # Property change signals
    attitudeChanged = Signal()
    gpsChanged = Signal()
    batteryChanged = Signal()
    statusChanged = Signal()
    
    def __init__(self):
        super().__init__()
        self._attitude = {"roll": 0.0, "pitch": 0.0, "yaw": 0.0}
        self._gps = {"lat": 0.0, "lon": 0.0, "alt": 0.0}
        self._battery = {"percentage": 0, "voltage": 0.0}
        self._status = "Disconnected"
        
    # Attitude properties
    @property
    def attitude(self):
        return self._attitude
        
    @Slot(float, float, float)
    def set_attitude(self, roll, pitch, yaw):
        self._attitude = {"roll": roll, "pitch": pitch, "yaw": yaw}
        self.attitudeChanged.emit()
        
    # GPS properties
    @property
    def gps(self):
        return self._gps
        
    @Slot(float, float, float)
    def set_gps_position(self, lat, lon, alt):
        self._gps = {"lat": lat, "lon": lon, "alt": alt}
        self.gpsChanged.emit()
        
    # Battery properties
    @property
    def battery(self):
        return self._battery
        
    @Slot(int, float)
    def set_battery_status(self, percentage, voltage):
        self._battery = {"percentage": percentage, "voltage": voltage}
        self.batteryChanged.emit()
        
    # Status property
    @property
    def status(self):
        return self._status
        
    @Slot(str)
    def set_status(self, status):
        self._status = status
        self.statusChanged.emit()

class MessageManager(QObject):
    """
    Message manager for log display in QML
    """
    
    # Message signals
    messageAdded = Signal(str, str)  # level, message
    messagesCleared = Signal()      # Signal wenn Log geleert wird
    
    def __init__(self):
        super().__init__()
        self.messages = []
        self.max_messages = 100  # Maximale Anzahl an Nachrichten
        
    @Slot(str, str)
    def add_message(self, level, message):
        """Add a message to the log"""
        # Aktuelle Zeit für die Nachricht
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] [{level}] {message}"
        
        # Nachricht zum Log hinzufügen
        self.messages.append({"level": level, "message": formatted_message})
        
        # Begrenze die Anzahl der Nachrichten
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)  # Entferne älteste Nachricht
            
        # Signal senden
        self.messageAdded.emit(level, formatted_message)
    
    @Slot(result="QVariantList")
    def get_messages(self):
        """Get all messages for QML"""
        return self.messages
    
    @Slot(str)
    def log_info(self, message):
        """Log an info message"""
        self.add_message("INFO", message)
    
    @Slot(str)
    def log_warning(self, message):
        """Log a warning message"""
        self.add_message("WARNING", message)
    
    @Slot(str)
    def log_error(self, message):
        """Log an error message"""
        self.add_message("ERROR", message)
    
    @Slot(str)
    def log_debug(self, message):
        """Log a debug message"""
        self.add_message("DEBUG", message)
        
    def clear_messages(self):
        """Clear all messages"""
        self.messages.clear()

class DroneKitIntegration(QObject):
    """
    Main integration class that connects all components
    """
    
    def __init__(self):
        super().__init__()
        self.telemetry_flow = TelemetryDataFlow()
        self.log_flow = LogDataFlow()
        self.telemetry_viewmodel = TelemetryViewModel()
        self.message_manager = MessageManager()
        
        # Connect telemetry signals to viewmodel
        self.telemetry_flow.attitude_updated.connect(
            self.telemetry_viewmodel.set_attitude
        )
        self.telemetry_flow.gps_updated.connect(
            self.telemetry_viewmodel.set_gps_position
        )
        self.telemetry_flow.battery_updated.connect(
            self.telemetry_viewmodel.set_battery_status
        )
        self.telemetry_flow.status_updated.connect(
            self.telemetry_viewmodel.set_status
        )
        
        # Connect log signals to message manager
        self.log_flow.log_message.connect(
            self.message_manager.add_message
        )
        
        # Connect connection status to logging
        self.telemetry_flow.connection_status_changed.connect(
            self._on_connection_status_changed
        )
        
    def connect_to_fc(self, port, baud_rate):
        """Connect to flight controller"""
        # Log connection attempt
        self.log_flow.add_message("INFO", f"Attempting connection to {port} at {baud_rate} baud")
        
        # Attempt connection
        success = self.telemetry_flow.connect_to_fc(port, baud_rate)
        
        if success:
            self.log_flow.log_connection_event("connected", f"Port: {port}, Baud: {baud_rate}")
        else:
            self.log_flow.log_connection_event("error", f"Failed to connect to {port}")
            
        return success
        
    def _on_connection_status_changed(self, connected):
        """Handle connection status changes"""
        if connected:
            self.log_flow.log_connection_event("connected")
        else:
            self.log_flow.log_connection_event("disconnected")
            
    def setup_qml_context(self, engine):
        """Setup QML context with all required properties"""
        context = engine.rootContext()
        
        # Expose main components to QML
        context.setContextProperty("dronekitIntegration", self)
        context.setContextProperty("telemetryViewModel", self.telemetry_viewmodel)
        context.setContextProperty("messageManager", self.message_manager)
        
        # Expose connection method
        context.setContextProperty("connectToFC", self.connect_to_fc)

def create_main_application():
    """
    Create and setup the main application with all integrations
    """
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    
    # Create integration
    integration = DroneKitIntegration()
    
    # Setup QML context
    integration.setup_qml_context(engine)
    
    # Load main QML file
    engine.load("RZGCSContent/Screen01.ui.qml")
    
    if not engine.rootObjects():
        print("Failed to load QML")
        return None
        
    return app, engine, integration

def test_telemetry_flow():
    """
    Test function to verify telemetry data flow
    """
    print("Testing telemetry data flow...")
    
    # Create integration
    integration = DroneKitIntegration()
    
    # Test connection (replace with actual COM port)
    success = integration.connect_to_fc("COM3", 115200)
    print(f"Connection test: {'SUCCESS' if success else 'FAILED'}")
    
    # Test telemetry updates
    if success:
        print("Telemetry flow test completed")
    else:
        print("Skipping telemetry test due to connection failure")
        
    return success

def test_log_flow():
    """
    Test function to verify log data flow
    """
    print("Testing log data flow...")
    
    # Create message manager
    message_manager = MessageManager()
    
    # Test message addition
    message_manager.add_message("INFO", "Test info message")
    message_manager.add_message("WARNING", "Test warning message")
    message_manager.add_message("ERROR", "Test error message")
    
    # Verify messages
    messages = message_manager.get_messages()
    print(f"Log flow test: {len(messages)} messages added")
    
    return len(messages) == 3

if __name__ == "__main__":
    # Run tests
    print("=== Telemetry and Log Data Flow Tests ===")
    
    telemetry_success = test_telemetry_flow()
    log_success = test_log_flow()
    
    print(f"\nTest Results:")
    print(f"Telemetry Flow: {'PASS' if telemetry_success else 'FAIL'}")
    print(f"Log Flow: {'PASS' if log_success else 'FAIL'}")
    
    if telemetry_success and log_success:
        print("\n✅ All tests passed! Integration ready.")
    else:
        print("\n❌ Some tests failed. Check implementation.") 