#!/usr/bin/env python3
"""
Fixed MAVSDK MVVM Implementation
Clean integration focusing on COM port connections with proper signal handling
"""

import os
import sys
import asyncio
import threading
from pathlib import Path

# Set QML style BEFORE importing PySide6
os.environ["QT_QUICK_CONTROLS_STYLE"] = "Material"

# Import PySide6 components
import PySide6
from PySide6.QtCore import QObject, QUrl, Property, Signal, Slot
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine, qmlRegisterType
from PySide6.QtQuickControls2 import QQuickStyle

# Import MVVM components
from backend.logger import Logger
from backend.sensorviewmodel import SensorViewModel
from backend.parameter_model import ParameterTableModel
from backend.parameter_manager import ParameterManager
from rzgcs.mvvm.viewmodel.mavsdk_drone_viewmodel import MAVSDKDroneViewModel


class SerialConnectionAdapter(QObject):
    """
    Adapter class that handles the connection between QML UI and MAVSDK
    This prevents naming conflicts between signal.connect() and our connect() method
    """
    # Define signals
    connectionRequested = Signal(str)
    connectionStateChanged = Signal(bool)
    
    def __init__(self, drone_view_model, logger):
        super().__init__()
        self._drone_view_model = drone_view_model
        self._logger = logger
        self._selected_port = ""
        
        # Connect to drone_view_model signals
        self._drone_view_model.connectionStateChanged.connect(self._onConnectionStateChanged)
        
        # Connect our signal to the drone view model
        self.connectionRequested.connect(self._handleConnectionRequest)
    
    def _onConnectionStateChanged(self, state):
        """Forward connection state changes"""
        self.connectionStateChanged.emit(state)
    
    @Slot(str)
    def _handleConnectionRequest(self, connection_string):
        """Handle connection requests from QML"""
        self._logger.addLog(f"[INFO] Verbindungsanfrage für: {connection_string}")
        self._drone_view_model.connectDrone(connection_string)
    
    @Property(bool, notify=connectionStateChanged)
    def connected(self):
        """Get connection state for QML"""
        return getattr(self._drone_view_model._model, 'is_connected', False)
    
    @Slot()
    def load_ports(self):
        """Load available ports for QML"""
        self._logger.addLog("[INFO] Lade verfügbare Ports")
        self._drone_view_model.refreshPorts()
    
    @Slot(str)
    def setPort(self, port_name):
        """Set selected port for QML"""
        self._selected_port = port_name
        self._logger.addLog(f"[INFO] Port ausgewählt: {port_name}")
    
    @Slot(str)
    def connect(self, connection_string=""):
        """QML-compatible connect method that routes to our signal"""
        # If port was selected but no connection string provided
        if self._selected_port and not connection_string:
            connection_string = self._selected_port
        
        self._logger.addLog(f"[INFO] Verbinde mit: {connection_string}")
        self.connectionRequested.emit(connection_string)
    
    @Slot(bool)
    def update_connection_status(self, is_connected):
        """Update connection status from QML"""
        self._drone_view_model.connectionStateChanged.emit(is_connected)


class SensorModelUpdater(QObject):
    """
    Class that handles updating the sensor model from drone telemetry
    without causing signal connection conflicts
    """
    def __init__(self, drone_view_model, sensor_model, logger):
        super().__init__()
        self._drone_view_model = drone_view_model
        self._sensor_model = sensor_model
        self._logger = logger
        
        # Connect all signals using lambdas to avoid naming conflicts
        self._connect_signals()
    
    def _connect_signals(self):
        """Connect drone view model signals to sensor model update methods"""
        # Battery updates
        self._drone_view_model.batteryChanged.connect(
            lambda battery: self._update_battery(battery)
        )
        
        # GPS updates
        self._drone_view_model.gpsInfoChanged.connect(
            lambda gps: self._update_gps(gps)
        )
        
        # Position updates
        self._drone_view_model.positionChanged.connect(
            lambda pos: self._update_position(pos)
        )
        
        # Attitude updates
        self._drone_view_model.attitudeChanged.connect(
            lambda att: self._update_attitude(att)
        )
        
        # Heading updates
        self._drone_view_model.headingChanged.connect(
            lambda heading: self._update_heading(heading)
        )
    
    def _update_battery(self, battery):
        """Update battery info in sensor model"""
        self._sensor_model.setBatteryLevel(battery['remaining_percent'])
        self._sensor_model.setBatteryVoltage(battery['voltage_v'])
    
    def _update_gps(self, gps_info):
        """Update GPS info in sensor model"""
        self._sensor_model.setGpsSatelliteCount(gps_info['num_satellites'])
        self._sensor_model.setGpsFixType(gps_info['fix_type'])
    
    def _update_position(self, position):
        """Update position info in sensor model"""
        if 'latitude_deg' in position and 'longitude_deg' in position:
            self._sensor_model.setLatitude(position['latitude_deg'])
            self._sensor_model.setLongitude(position['longitude_deg'])
        
        if 'absolute_altitude_m' in position:
            self._sensor_model.setAltitude(position['absolute_altitude_m'])
    
    def _update_attitude(self, attitude):
        """Update attitude info in sensor model"""
        if 'roll_deg' in attitude:
            self._sensor_model.setRoll(attitude['roll_deg'])
        
        if 'pitch_deg' in attitude:
            self._sensor_model.setPitch(attitude['pitch_deg'])
        
        if 'yaw_deg' in attitude:
            self._sensor_model.setYaw(attitude['yaw_deg'])
    
    def _update_heading(self, heading):
        """Update heading in sensor model"""
        self._sensor_model.setHeading(heading)


def configure_material_style():
    """Set up Material style for QML"""
    # Use environment variable
    os.environ["QT_QUICK_CONTROLS_STYLE"] = "Material"
    
    # Use QQuickStyle API
    QQuickStyle.setStyle("Material")
    
    # Create Material style configuration file if it doesn't exist
    config_file = os.path.join(os.getcwd(), "RZGCSContent", "qtquickcontrols2.conf")
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


def check_mavsdk_server():
    """Check if MAVSDK server is available and log result"""
    mavsdk_server_path = os.path.join(os.getcwd(), "mavsdk_server", "windows", "mavsdk-server.exe")
    
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
    
    # Set working directory to project root (essential for finding QML files)
    project_root = Path(__file__).resolve().parent.parent
    os.chdir(str(project_root))
    print(f"Working directory: {os.getcwd()}")
    
    # Set Material style for QML
    configure_material_style()
    
    # Check MAVSDK server
    check_mavsdk_server()
    
    # Create QApplication
    app = QGuiApplication(sys.argv)
    
    # Create logger
    logger = Logger()
    logger.addLog("[INFO] Starting fixed MAVSDK MVVM integration")
    
    # Create drone view model
    drone_view_model = MAVSDKDroneViewModel(logger)
    
    # Create adapter for QML (this is the key to avoiding method name conflicts)
    serial_adapter = SerialConnectionAdapter(drone_view_model, logger)
    
    # Create additional models required by the QML UI
    sensor_model = SensorViewModel()
    parameter_model = ParameterTableModel()
    parameter_manager = ParameterManager(parameter_model, logger)
    
    # Register sensor model type for QML
    qmlRegisterType(SensorViewModel, "RZGCS", 1, 0, "SensorViewModel")
    
    # Create sensor model updater to handle telemetry updates
    sensor_updater = SensorModelUpdater(drone_view_model, sensor_model, logger)
    
    # Create QML engine
    engine = QQmlApplicationEngine()
    
    # Set import paths
    qml_content_dir = os.path.join(os.getcwd(), "RZGCSContent")
    engine.addImportPath(qml_content_dir)
    engine.addImportPath(os.getcwd())
    
    # Set environment variables for QML import paths
    os.environ["QML_IMPORT_PATH"] = qml_content_dir
    os.environ["QML2_IMPORT_PATH"] = qml_content_dir
    
    # Register objects in QML context
    context = engine.rootContext()
    
    # IMPORTANT: Register the adapter as 'serialConnector' for QML compatibility
    context.setContextProperty("serialConnector", serial_adapter)  # This is what QML expects
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
    logger.addLog("[INFO] RZGCS with fixed MAVSDK MVVM integration started")
    logger.addLog("[INFO] COM port connection handling is enabled")
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
