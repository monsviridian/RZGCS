#!/usr/bin/env python3
"""
MAVSDK QML Adapter
This script provides a clean adapter that connects MAVSDK with the QML UI
without modifying the original classes or creating method name conflicts
"""

import os
import sys
from pathlib import Path

# Set style before importing PySide6
os.environ["QT_QUICK_CONTROLS_STYLE"] = "Material"

# Import PySide6
import PySide6
from PySide6.QtCore import QObject, QUrl, Signal, Slot, Property
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine, qmlRegisterType
from PySide6.QtQuickControls2 import QQuickStyle

# Get project root
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import modules
from backend.logger import Logger
from backend.sensorviewmodel import SensorViewModel
from backend.parameter_model import ParameterTableModel
from backend.parameter_manager import ParameterManager
from rzgcs.mvvm.viewmodel.mavsdk_drone_viewmodel import MAVSDKDroneViewModel


class SerialConnectorAdapter(QObject):
    """
    Adapter class that wraps MAVSDKDroneViewModel to provide
    a QML-compatible interface without method name conflicts
    """
    # Define signals for compatibility with QML
    connectedChanged = Signal(bool)
    
    def __init__(self, drone_view_model, logger):
        """Initialize with reference to the actual drone view model"""
        super().__init__()
        self._drone_view_model = drone_view_model
        self._logger = logger
        self._selected_port = ""
        
        # Connect to the original signals
        self._drone_view_model.connectionStateChanged.connect(self._onConnectionStateChanged)
    
    def _onConnectionStateChanged(self, is_connected):
        """Handle connection state changes"""
        self.connectedChanged.emit(is_connected)
    
    @Property(bool, notify=connectedChanged)
    def connected(self):
        """Property for QML: whether the drone is connected"""
        return getattr(self._drone_view_model._model, 'is_connected', False)
    
    @Slot()
    def load_ports(self):
        """Load available ports for QML"""
        self._logger.addLog("[INFO] Loading available ports")
        self._drone_view_model.refreshPorts()
    
    @Slot(str)
    def setPort(self, port_name):
        """Set selected port for QML"""
        self._selected_port = port_name
        self._logger.addLog(f"[INFO] Port selected: {port_name}")
    
    @Slot(str)
    def connect(self, connection_string=""):
        """Connect to drone for QML - handles different connection formats"""
        # If port was selected but no connection string provided
        if self._selected_port and not connection_string:
            connection_string = self._selected_port
        
        self._logger.addLog(f"[INFO] Connecting to: {connection_string}")
        
        # Extract baudrate from connection string (e.g., "COM3:115200")
        if ":" in connection_string and not connection_string.startswith(("udp:", "tcp:")):
            try:
                port, baudrate = connection_string.split(":", 1)
                baudrate = int(baudrate)
            except (ValueError, TypeError):
                baudrate = 57600
        
        # Call the actual connect method on the drone view model
        self._drone_view_model.connectDrone(connection_string)
    
    @Slot(bool)
    def update_connection_status(self, is_connected):
        """Update connection status for QML"""
        self._drone_view_model.connectionStateChanged.emit(is_connected)


class DataRelayService(QObject):
    """
    Service that relays data between models
    Keeps model connections clean and separate
    """
    def __init__(self, drone_view_model, sensor_model, logger):
        super().__init__()
        self._drone_view_model = drone_view_model
        self._sensor_model = sensor_model
        self._logger = logger
        
        # Connect signals for data relay
        self._connect_signals()
    
    def _connect_signals(self):
        """Connect signals for data relay"""
        # Battery updates
        self._drone_view_model.batteryChanged.connect(self._update_battery)
        
        # GPS updates
        self._drone_view_model.gpsInfoChanged.connect(self._update_gps)
        
        # Position updates
        self._drone_view_model.positionChanged.connect(self._update_position)
        
        # Attitude updates
        self._drone_view_model.attitudeChanged.connect(self._update_attitude)
        
        # Heading updates
        self._drone_view_model.headingChanged.connect(self._update_heading)
    
    def _update_battery(self, battery):
        """Update battery info in sensor model"""
        self._sensor_model.setBatteryLevel(battery['remaining_percent'])
        self._sensor_model.setBatteryVoltage(battery['voltage_v'])
    
    def _update_gps(self, gps_info):
        """Update GPS info in sensor model"""
        self._sensor_model.setGpsSatelliteCount(gps_info['num_satellites'])
        self._sensor_model.setGpsFixType(gps_info['fix_type'])
    
    def _update_position(self, position):
        """Update position in sensor model"""
        if 'latitude_deg' in position and 'longitude_deg' in position:
            self._sensor_model.setLatitude(position['latitude_deg'])
            self._sensor_model.setLongitude(position['longitude_deg'])
        
        if 'absolute_altitude_m' in position:
            self._sensor_model.setAltitude(position['absolute_altitude_m'])
    
    def _update_attitude(self, attitude):
        """Update attitude in sensor model"""
        if 'roll_deg' in attitude:
            self._sensor_model.setRoll(attitude['roll_deg'])
        
        if 'pitch_deg' in attitude:
            self._sensor_model.setPitch(attitude['pitch_deg'])
        
        if 'yaw_deg' in attitude:
            self._sensor_model.setYaw(attitude['yaw_deg'])
    
    def _update_heading(self, heading):
        """Update heading in sensor model"""
        self._sensor_model.setHeading(heading)


def setup_qml_material_style():
    """Set up Material style for QML"""
    # Use environment variable
    os.environ["QT_QUICK_CONTROLS_STYLE"] = "Material"
    
    # Use QQuickStyle API
    QQuickStyle.setStyle("Material")
    
    # Create Material style configuration file if it doesn't exist
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
    
    # Update App.qml imports if necessary
    qml_file = os.path.join(project_root, "RZGCSContent", "App.qml")
    if os.path.exists(qml_file):
        with open(qml_file, "r") as f:
            content = f.read()
        
        # Add Material style imports if not present
        if "QtQuick.Controls.Material" not in content:
            content = content.replace(
                "import QtQuick.Controls",
                "import QtQuick.Controls.Material 2.15\nimport QtQuick.Controls 2.15"
            )
            with open(qml_file, "w") as f:
                f.write(content)


def check_mavsdk_server():
    """Check if MAVSDK server is available and log result"""
    mavsdk_server_path = os.path.join(project_root, "mavsdk_server", "windows", "mavsdk-server.exe")
    
    if os.path.exists(mavsdk_server_path):
        print(f"[INFO] MAVSDK server found: {mavsdk_server_path}")
        return True
    else:
        print(f"[WARNING] MAVSDK server not found at: {mavsdk_server_path}")
        return False


def main():
    """Main application function"""
    # Print version information
    print(f"Python version: {sys.version}")
    print(f"PySide6 version: {PySide6.__version__}")
    
    # Set working directory
    os.chdir(project_root)
    print(f"Working directory: {os.getcwd()}")
    
    # Set up Material style for QML
    setup_qml_material_style()
    
    # Check MAVSDK server
    check_mavsdk_server()
    
    # Create QApplication
    app = QGuiApplication(sys.argv)
    
    # Create models and services
    logger = Logger()
    logger.addLog("[INFO] Starting MAVSDK QML adapter")
    
    drone_view_model = MAVSDKDroneViewModel(logger)
    sensor_model = SensorViewModel()
    parameter_model = ParameterTableModel()
    parameter_manager = ParameterManager(parameter_model, logger)
    
    # Create adapter for QML
    serial_connector = SerialConnectorAdapter(drone_view_model, logger)
    
    # Create data relay service
    data_relay = DataRelayService(drone_view_model, sensor_model, logger)
    
    # Create QML engine
    engine = QQmlApplicationEngine()
    
    # Set import paths
    qml_content_dir = os.path.join(os.getcwd(), "RZGCSContent")
    engine.addImportPath(qml_content_dir)
    engine.addImportPath(os.getcwd())
    
    # Set environment variables for QML import paths
    os.environ["QML_IMPORT_PATH"] = qml_content_dir
    os.environ["QML2_IMPORT_PATH"] = qml_content_dir
    
    # Register QML types
    qmlRegisterType(SensorViewModel, "RZGCS", 1, 0, "SensorViewModel")
    
    # Register objects in QML context
    context = engine.rootContext()
    
    # Register the adapter as 'serialConnector' for QML compatibility
    context.setContextProperty("serialConnector", serial_connector)
    context.setContextProperty("droneViewModel", drone_view_model)
    context.setContextProperty("sensorModel", sensor_model)
    context.setContextProperty("parameterModel", parameter_model)
    context.setContextProperty("parameterManager", parameter_manager)
    context.setContextProperty("logger", logger)
    
    # Find and load QML file
    qml_file = os.path.join(os.getcwd(), "RZGCSContent", "App.qml")
    print(f"Loading QML file: {qml_file}")
    
    # Load QML file
    url = QUrl.fromLocalFile(qml_file)
    engine.load(url)
    
    # Check if application loaded successfully
    if not engine.rootObjects():
        print(f"[ERROR] Failed to load QML file: {url.toString()}")
        return 1
    
    # Start application
    logger.addLog("[INFO] RZGCS with MAVSDK QML adapter started")
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
