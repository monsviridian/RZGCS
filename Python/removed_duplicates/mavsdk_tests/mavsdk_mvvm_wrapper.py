#!/usr/bin/env python3
"""
MAVSDK MVVM Wrapper
Integrates the MVVM architecture with existing RZGCS infrastructure
"""

import os
import sys
from pathlib import Path

# Set Material style environment variable
os.environ["QT_QUICK_CONTROLS_STYLE"] = "Material"

# PySide6 imports
import PySide6
from PySide6.QtCore import QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle

# Import existing MAVSDK implementation
from backend.logger import Logger
from rzgcs.mvvm.viewmodel.mavsdk_drone_viewmodel import MAVSDKDroneViewModel


def main():
    """Main application function"""
    # Print version information
    print(f"Python version: {sys.version}")
    print(f"PySide6 version: {PySide6.__version__}")
    
    # Set working directory to project root
    os.chdir(str(Path(__file__).resolve().parent.parent))
    print(f"Working directory: {os.getcwd()}")
    
    # Set Material style for QML
    QQuickStyle.setStyle("Material")
    
    # Create application
    app = QGuiApplication(sys.argv)
    
    # Create logger
    logger = Logger()
    logger.addLog("[INFO] Starting RZGCS with MAVSDK MVVM integration")
    
    # Create ViewModel with all necessary compatibility methods
    drone_view_model = MAVSDKDroneViewModel(logger)
    
    # Add UI compatibility methods from memory
    drone_view_model._selected_port = ""
    
    # load_ports method
    if not hasattr(drone_view_model, 'load_ports'):
        def load_ports():
            drone_view_model.refreshPorts()
        drone_view_model.load_ports = load_ports
    
    # setPort method
    if not hasattr(drone_view_model, 'setPort'):
        def setPort(port_name):
            drone_view_model._selected_port = port_name
            logger.addLog(f"[INFO] Port selected: {port_name}")
        drone_view_model.setPort = setPort
    
    # connect method for different formats
    if not hasattr(drone_view_model, 'connect'):
        def connect(connection_string):
            if drone_view_model._selected_port and not connection_string:
                connection_string = drone_view_model._selected_port
            
            # Extract baudrate if present
            if ":" in connection_string and not connection_string.startswith(("udp:", "tcp:")):
                try:
                    port, baudrate = connection_string.split(":", 1)
                    baudrate = int(baudrate)
                except (ValueError, TypeError):
                    baudrate = 57600
            
            drone_view_model.connectDrone(connection_string)
        drone_view_model.connect = connect
    
    # update_connection_status method
    if not hasattr(drone_view_model, 'update_connection_status'):
        def update_connection_status(is_connected):
            drone_view_model.connectionStateChanged.emit(is_connected)
        drone_view_model.update_connection_status = update_connection_status
    
    # Import existing main module
    # This is what makes this approach different - we're importing the existing code
    # that we know works, rather than trying to recreate it
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import mavsdk_rzgcs_main
    
    # Override the QML engine setup in the existing code
    original_main = mavsdk_rzgcs_main.main
    
    def patched_main():
        # Set Material style again just to be sure
        QQuickStyle.setStyle("Material")
        
        # Run the original main function
        # The existing code already handles loading QML files properly
        return original_main()
    
    # Replace the main function with our patched version
    mavsdk_rzgcs_main.main = patched_main
    
    # Run the patched main function
    return mavsdk_rzgcs_main.main()


if __name__ == "__main__":
    sys.exit(main())
