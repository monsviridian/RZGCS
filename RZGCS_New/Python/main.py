"""
RZGCS - Main Application Entry Point
"""

import sys
import os
from pathlib import Path
from PySide6.QtCore import QObject, QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine, qmlRegisterType
from backend.backend import Backend

def main():
    # Create the application
    app = QGuiApplication(sys.argv)
    
    # Create the QML engine
    engine = QQmlApplicationEngine()
    
    # Get the base path (parent directory of this script)
    base_path = Path(__file__).parent.parent
    
    # Set up QML paths
    qml_path = base_path / "RZGCSContent"
    rzgcs_path = base_path / "RZGCS"
    
    # Add import paths
    engine.addImportPath(str(qml_path))
    engine.addImportPath(str(rzgcs_path))
    
    # Register the Backend type
    qmlRegisterType(Backend, "RZGCS", 1, 0, "Backend")
    
    # Create and expose the backend instance
    backend = Backend()
    engine.rootContext().setContextProperty("backend", backend)
    
    # Load the main QML file
    main_qml = qml_path / "RZGCS" / "App.qml"
    if not main_qml.exists():
        print(f"Error: Could not find {main_qml}")
        sys.exit(1)
        
    engine.load(QUrl.fromLocalFile(str(main_qml)))
    
    if not engine.rootObjects():
        print("Error: Failed to load QML")
        sys.exit(1)
    
    # Run the application
    sys.exit(app.exec())

if __name__ == "__main__":
    sys.exit(main()) 