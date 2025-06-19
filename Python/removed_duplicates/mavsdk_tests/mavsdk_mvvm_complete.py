#!/usr/bin/env python3
"""
MAVSDK MVVM Complete Integration
A complete implementation that integrates MAVSDK with MVVM architecture
and ensures compatibility with existing QML UI components
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

# Add project path to sys.path if needed
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import modules
from backend.logger import Logger
from backend.sensorviewmodel import SensorViewModel
from backend.parameter_model import ParameterTableModel
from backend.parameter_manager import ParameterManager
from rzgcs.mvvm.viewmodel.mavsdk_drone_viewmodel import MAVSDKDroneViewModel


class MVVMBackend(QObject):
    """Backend for RZGCS with MAVSDK MVVM integration"""
    
    def __init__(self):
        """Initialize the backend"""
        super().__init__()
        
        # Initialize logger
        self.logger = Logger()
        self.logger.addLog("[INFO] Initializing RZGCS with MAVSDK MVVM integration")
        
        # Create sensor model
        self.sensor_model = SensorViewModel()
        
        # Create parameter model and manager
        self.parameter_model = ParameterTableModel()
        self.parameter_manager = ParameterManager(self.parameter_model, self.logger)
        
        # Create drone view model
        self.drone_view_model = MAVSDKDroneViewModel(self.logger)
        
        # Add compatibility methods based on memory about UI connection improvements
        self._add_compatibility_methods()
        
        # Connect signals between models
        self._connect_signals()
        
        # Verify MAVSDK server availability
        self._check_mavsdk_server()
        
        self.logger.addLog("[INFO] RZGCS backend with MVVM architecture initialized")
    
    def _add_compatibility_methods(self):
        """Add compatibility methods required by QML UI"""
        vm = self.drone_view_model
        
        # Store selected port
        vm._selected_port = ""
        
        # Add 'connected' property as alias for connectionState if not already present
        if not hasattr(type(vm), 'connected'):
            # This creates a property named 'connected' on the class, not the instance
            setattr(type(vm), 'connected',
                    Property(bool, lambda self: getattr(self._model, 'is_connected', False),
                            notify=vm.connectionStateChanged))
        
        # Add 'load_ports' method if not already present
        if not hasattr(vm, 'load_ports'):
            @Slot()
            def load_ports():
                vm.refreshPorts()
            vm.load_ports = load_ports
        
        # Add 'setPort' method if not already present
        if not hasattr(vm, 'setPort'):
            @Slot(str)
            def setPort(port_name):
                vm._selected_port = port_name
                self.logger.addLog(f"[INFO] Port selected: {port_name}")
            vm.setPort = setPort
        
        # Add 'connect' method if not already present
        if not hasattr(vm, 'connect'):
            @Slot(str)
            def connect_drone(connection_string=""):
                # If port was selected but no connection string provided
                if vm._selected_port and not connection_string:
                    connection_string = vm._selected_port
                
                # Extract baudrate from connection string (e.g., "COM3:115200")
                if ":" in connection_string and not connection_string.startswith(("udp:", "tcp:")):
                    try:
                        port, baudrate = connection_string.split(":", 1)
                        baudrate = int(baudrate)
                    except (ValueError, TypeError):
                        baudrate = 57600
                
                self.logger.addLog(f"[INFO] Connecting to: {connection_string}")
                vm.connectDrone(connection_string)
            vm.connect = connect_drone
        
        # Add 'update_connection_status' method if not already present
        if not hasattr(vm, 'update_connection_status'):
            @Slot(bool)
            def update_connection_status(is_connected):
                vm.connectionStateChanged.emit(is_connected)
            vm.update_connection_status = update_connection_status
    
    def _connect_signals(self):
        """Connect signals between models for data updates"""
        # Connect drone view model signals to sensor model
        self.drone_view_model.batteryChanged.connect(self._update_battery)
        self.drone_view_model.gpsInfoChanged.connect(self._update_gps)
        self.drone_view_model.positionChanged.connect(self._update_position)
        self.drone_view_model.attitudeChanged.connect(self._update_attitude)
        self.drone_view_model.headingChanged.connect(self._update_heading)
    
    def _update_battery(self, battery):
        """Update battery info in sensor model"""
        self.sensor_model.setBatteryLevel(battery['remaining_percent'])
        self.sensor_model.setBatteryVoltage(battery['voltage_v'])
    
    def _update_gps(self, gps_info):
        """Update GPS info in sensor model"""
        self.sensor_model.setGpsSatelliteCount(gps_info['num_satellites'])
        self.sensor_model.setGpsFixType(gps_info['fix_type'])
    
    def _update_position(self, position):
        """Update position in sensor model"""
        if 'latitude_deg' in position and 'longitude_deg' in position:
            self.sensor_model.setLatitude(position['latitude_deg'])
            self.sensor_model.setLongitude(position['longitude_deg'])
        
        if 'absolute_altitude_m' in position:
            self.sensor_model.setAltitude(position['absolute_altitude_m'])
    
    def _update_attitude(self, attitude):
        """Update attitude in sensor model"""
        if 'roll_deg' in attitude:
            self.sensor_model.setRoll(attitude['roll_deg'])
        
        if 'pitch_deg' in attitude:
            self.sensor_model.setPitch(attitude['pitch_deg'])
        
        if 'yaw_deg' in attitude:
            self.sensor_model.setYaw(attitude['yaw_deg'])
    
    def _update_heading(self, heading):
        """Update heading in sensor model"""
        self.sensor_model.setHeading(heading)
    
    def _check_mavsdk_server(self):
        """Check if MAVSDK server is available"""
        mavsdk_server_path = os.path.join(project_root, "mavsdk_server", "windows", "mavsdk-server.exe")
        
        if os.path.exists(mavsdk_server_path):
            self.logger.addLog(f"[INFO] MAVSDK server found: {mavsdk_server_path}")
        else:
            self.logger.addLog(f"[WARNING] MAVSDK server not found at: {mavsdk_server_path}")
            self.logger.addLog("[WARNING] Connection to drone may not work without MAVSDK server")


def main():
    """Main application function"""
    # Print version information
    print(f"Python version: {sys.version}")
    print(f"PySide6 version: {PySide6.__version__}")
    
    # Set working directory
    os.chdir(project_root)
    print(f"Working directory: {os.getcwd()}")
    
    # Set Material style
    QQuickStyle.setStyle("Material")
    
    # Create QApplication
    app = QGuiApplication(sys.argv)
    
    # Create backend
    backend = MVVMBackend()
    
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
    
    # IMPORTANT: Register view model as 'serialConnector' for UI compatibility
    # This is mentioned in memory 0e34d025-aeec-4ad1-af5a-21f6eef67c2d
    context.setContextProperty("serialConnector", backend.drone_view_model)
    context.setContextProperty("droneViewModel", backend.drone_view_model)
    context.setContextProperty("sensorModel", backend.sensor_model)
    context.setContextProperty("parameterModel", backend.parameter_model)
    context.setContextProperty("parameterManager", backend.parameter_manager)
    context.setContextProperty("logger", backend.logger)
    
    # Create Material style configuration file if it doesn't exist
    config_file = os.path.join(qml_content_dir, "qtquickcontrols2.conf")
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
    
    # Find and load QML file
    qml_file = os.path.join(os.getcwd(), "RZGCSContent", "App.qml")
    print(f"Loading QML file: {qml_file}")
    
    # Ensure QML file exists
    if not os.path.exists(qml_file):
        print(f"[ERROR] QML file not found: {qml_file}")
        return 1
    
    # Update QML imports if necessary
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
    
    # Load QML file
    url = QUrl.fromLocalFile(qml_file)
    engine.load(url)
    
    # Check if application loaded successfully
    if not engine.rootObjects():
        print(f"[ERROR] Failed to load QML file: {url.toString()}")
        return 1
    
    # Start application
    backend.logger.addLog("[INFO] RZGCS with MAVSDK MVVM integration started")
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
