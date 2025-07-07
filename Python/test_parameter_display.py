#!/usr/bin/env python3
"""
Test-Skript für Parameter-Anzeige
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dronekit_parameter_viewmodel import DroneKitParameterViewModel
from PySide6.QtCore import QCoreApplication, QTimer
from PySide6.QtGui import QGuiApplication

def test_parameter_model():
    """Testet das Parameter-Modell"""
    app = QGuiApplication(sys.argv)
    
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
    
    # Modell-Status überprüfen
    model = viewmodel.parameterModel
    print(f"ParameterModel count: {model.count}")
    print(f"ParameterModel rowCount: {model.rowCount()}")
    
    # Erste Zeile testen
    if model.rowCount() > 0:
        index = model.index(0, 0)
        name = model.data(index, model.NameRole)
        value = model.data(index, model.ValueRole)
        type_val = model.data(index, model.TypeRole)
        desc = model.data(index, model.DescriptionRole)
        
        print(f"Erste Zeile: Name={name}, Value={value}, Type={type_val}, Desc={desc}")
    
    # Alle Parameter auflisten
    print("\nAlle Parameter:")
    for i in range(model.rowCount()):
        index = model.index(i, 0)
        name = model.data(index, model.NameRole)
        value = model.data(index, model.ValueRole)
        print(f"  {i}: {name} = {value}")
    
    print("Test abgeschlossen")
    return app.exec()

if __name__ == "__main__":
    sys.exit(test_parameter_model()) 