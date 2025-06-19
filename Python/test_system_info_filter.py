#!/usr/bin/env python3
"""
Test-Script für den System-Informationsfilter in der Preflight-View
Dieses Script testet, ob die speziellen Systeminformationen korrekt
gefiltert und in der vergrößerten Log-Ansicht angezeigt werden.
"""

import os
import sys
import time
from pathlib import Path

# Set style before importing PySide6
os.environ["QT_QUICK_CONTROLS_STYLE"] = "Material"

# Import PySide6
import PySide6
from PySide6.QtCore import QObject, QTimer, Signal, Slot, Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle

# Project paths setup
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import modules
from backend.logger import Logger
from rzgcs.mvvm.qml_compatibility_adapter import QMLCompatibilityAdapter
from backend.sensorviewmodel import SensorViewModel


class SystemInfoTestGenerator(QObject):
    """
    Generator für Test-Systeminformationen
    Erzeugt synthetische Systeminformationen, die vom Filter erkannt werden sollten
    """
    
    def __init__(self, logger, parent=None):
        super().__init__(parent)
        self.logger = logger
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.generate_system_info)
        self.test_index = 0
        self.test_messages = [
            # Frame-Typ Informationen
            "[INFO] Frame Type: Quad X",
            "[SYS] ArduCopter Frame: QUADX",
            "[STATUS] Detected frame configuration: X4",
            
            # RCOut Informationen
            "[DEBUG] RCOut[0]: 1500, RCOut[1]: 1500, RCOut[2]: 1100, RCOut[3]: 1100",
            "[SYSTEM] RC Outputs: CH1=1500 CH2=1500 CH3=1100 CH4=1100",
            
            # Hardware Informationen
            "[INFO] Hardware: MicoAir743 detected",
            "[SYS] Running on MicoAir743 hardware",
            "[INFO] ChibiOS version: 21.11.3",
            
            # ArduCopter Version
            "[STATUS] ArduCopter V4.3.1 (ea5af3a0)",
            "[SYS] Firmware version: ArduCopter V4.3.1",
            
            # PreArm Warnungen
            "[WARN] PreArm: RC not calibrated",
            "[WARNING] PreArm check failed: Compass needs calibration",
            "[CRITICAL] PreArm: Battery below minimum voltage",
            
            # Normale Logs, die nicht hervorgehoben werden sollten
            "[INFO] Normal log message that should not be highlighted",
            "[DEBUG] This is a debug message that should be filtered out",
            "[STATUS] Regular status update"
        ]
    
    def start(self, interval_ms=1000):
        """Startet die Generierung von Test-Systeminformationen"""
        self.timer.start(interval_ms)
    
    def stop(self):
        """Stoppt die Generierung von Test-Systeminformationen"""
        self.timer.stop()
    
    def generate_system_info(self):
        """Generiert eine Test-Systeminformation"""
        if self.test_index < len(self.test_messages):
            message = self.test_messages[self.test_index]
            self.logger.addLog(message)
            self.test_index += 1
        else:
            # Alle Nachrichten wurden gesendet, Timer stoppen
            self.timer.stop()
            self.logger.addLog("[INFO] System information test complete")


class SimpleDroneViewModel(QObject):
    """
    Einfaches DroneViewModel für den Test
    Simuliert minimale Funktionalität des MAVSDKDroneViewModel
    """
    connectionStateChanged = Signal(bool)
    
    def __init__(self, logger, parent=None):
        super().__init__(parent)
        self._logger = logger
        self._is_connected = False
        self._model = self  # Für Kompatibilität mit dem Adapter
        self.ports = ["COM1", "COM2", "COM3", "COM4", "COM5"]
    
    @property
    def is_connected(self):
        return self._is_connected
    
    @Slot()
    def refreshPorts(self):
        """Aktualisiert die Liste der Ports (Mock)"""
        self._logger.addLog("[INFO] Refreshing ports (mock)")
    
    @Slot(str)
    def connectToDrone(self, connection_string=""):
        """Simuliert eine Verbindung zur Drohne"""
        self._logger.addLog(f"[INFO] Connecting to drone: {connection_string}")
        self._is_connected = True
        self.connectionStateChanged.emit(True)
        
        # Systeminfos nach Verbindung senden
        QTimer.singleShot(500, lambda: self._logger.addLog("[SYS] ArduCopter V4.3.1 (ea5af3a0)"))
        QTimer.singleShot(800, lambda: self._logger.addLog("[SYS] Frame Type: Quad X"))
        QTimer.singleShot(1100, lambda: self._logger.addLog("[SYS] Hardware: MicoAir743"))
        QTimer.singleShot(1400, lambda: self._logger.addLog("[SYS] ChibiOS: 21.11.3"))
        QTimer.singleShot(1700, lambda: self._logger.addLog("[WARN] PreArm: RC not calibrated"))
    
    @Slot()
    def disconnectDrone(self):
        """Trennt die Verbindung zur Drohne"""
        self._logger.addLog("[INFO] Disconnecting from drone")
        self._is_connected = False
        self.connectionStateChanged.emit(False)


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


def main():
    """Main function to test system information filtering"""
    print(f"Python version: {sys.version}")
    print(f"PySide6 version: {PySide6.__version__}")
    
    # Set working directory to project root
    os.chdir(project_root)
    print(f"Working directory: {os.getcwd()}")
    
    # Set up Material style
    setup_qml_material_style()
    
    # Create application
    app = QGuiApplication(sys.argv)
    
    # Create logger with system info filter
    logger = Logger()
    logger.addLog("[INFO] Testing system information filtering in Preflight-View")
    
    # Create simple ViewModel for testing
    drone_view_model = SimpleDroneViewModel(logger)
    
    # Create QML compatibility adapter
    qml_adapter = QMLCompatibilityAdapter(drone_view_model)
    
    # Create sensor model for testing
    sensor_model = SensorViewModel()
    
    # Create system info test generator
    system_info_generator = SystemInfoTestGenerator(logger)
    
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
    context.setContextProperty("serialConnector", qml_adapter)
    context.setContextProperty("droneViewModel", drone_view_model)
    context.setContextProperty("sensorModel", sensor_model)
    context.setContextProperty("logger", logger)
    
    # Reduced QML that focuses on PreflightView
    qml_file = os.path.join(os.getcwd(), "RZGCSContent", "App.qml")
    print(f"Loading QML file: {qml_file}")
    
    # Load QML file
    engine.load(qml_file)
    
    # Check if engine loaded correctly
    if not engine.rootObjects():
        print(f"[ERROR] Failed to load QML file: {qml_file}")
        return 1
    
    # Start generating test system information after a short delay
    QTimer.singleShot(2000, lambda: system_info_generator.start(1500))
    
    # Run application
    logger.addLog("[INFO] Test application started. Please check if system information is filtered correctly.")
    logger.addLog("[INFO] The log area should be enlarged to 30% of the height with 16px font size.")
    logger.addLog("[INFO] System information should be highlighted in bold.")
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
