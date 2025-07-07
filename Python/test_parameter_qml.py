#!/usr/bin/env python3
"""
Test-Skript für Parameter-QML-Anzeige
"""

import sys
import os
from pathlib import Path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dronekit_parameter_viewmodel import DroneKitParameterViewModel
from PySide6.QtCore import QCoreApplication, QTimer, QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

def test_parameter_qml():
    """Testet die Parameter-QML-Anzeige"""
    app = QGuiApplication(sys.argv)
    
    # QML-Engine erstellen
    engine = QQmlApplicationEngine()
    
    # ParameterViewModel erstellen
    viewmodel = DroneKitParameterViewModel()
    
    # Test-Parameter hinzufügen
    test_parameters = {
        "TEST_PARAM1": {
            "value": 1.5,
            "type": "float",
            "description": "Test Parameter 1",
            "index": 0,
            "count": 3
        },
        "TEST_PARAM2": {
            "value": 2.0,
            "type": "float", 
            "description": "Test Parameter 2",
            "index": 1,
            "count": 3
        },
        "TEST_PARAM3": {
            "value": 3.0,
            "type": "float",
            "description": "Test Parameter 3", 
            "index": 2,
            "count": 3
        }
    }
    
    print(f"Test-Parameter erstellt: {len(test_parameters)}")
    
    # Parameter zum Modell hinzufügen
    viewmodel._on_parameters_received(test_parameters)
    
    # Context Property setzen
    engine.rootContext().setContextProperty("parameterViewModel", viewmodel)
    
    # QML-Datei laden
    qml_file = Path(__file__).parent.parent / "RZGCSContent" / "SimpleParameterTest.qml"
    print(f"Lade QML-Datei: {qml_file}")
    
    if not qml_file.exists():
        print(f"FEHLER: QML-Datei nicht gefunden: {qml_file}")
        return -1
    
    engine.load(QUrl.fromLocalFile(str(qml_file)))
    
    if not engine.rootObjects():
        print("FEHLER: Keine Root-Objekte nach dem Laden der QML-Datei")
        return -1
    
    print("QML-Datei erfolgreich geladen")
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(test_parameter_qml()) 