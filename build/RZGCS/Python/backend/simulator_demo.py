"""
Demo-Programm für den kompatiblen Sensor-Simulator
"""

import os
import sys
import time
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QUrl
from PySide6.QtQml import QQmlApplicationEngine

# Importiere SensorViewModel und den kompatiblen Simulator
from backend.sensorviewmodel import SensorViewModel
from backend.compatible_simulator import CompatibleSensorSimulator

def main():
    """Hauptfunktion"""
    app = QApplication(sys.argv)
    
    # QML-Engine erstellen
    engine = QQmlApplicationEngine()
    
    # Sensor-Modell erstellen
    sensor_model = SensorViewModel()
    
    # Modell an den QML-Kontext übergeben
    engine.rootContext().setContextProperty("sensorModel", sensor_model)
    
    # Kompatiblen Simulator erstellen und initialisieren
    simulator = CompatibleSensorSimulator()
    simulator.initialize_sensors(sensor_model)
    
    # Lade die QML-Datei - korrekter Pfad zur SensorView.ui.qml
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    qml_file = os.path.join(project_root, "RZGCSContent", "SensorView.ui.qml")
    print(f"Lade QML von: {qml_file}")
    
    # Simulator starten
    simulator.start()
    
    # QML-Datei laden
    engine.load(QUrl.fromLocalFile(qml_file))
    
    # Prüfen, ob QML geladen wurde
    if not engine.rootObjects():
        print("Fehler beim Laden der QML-Datei!")
        return 1
    
    # Hauptschleife starten
    exit_code = app.exec()
    
    # Simulator stoppen
    simulator.stop()
    
    return exit_code

if __name__ == "__main__":
    sys.exit(main())
