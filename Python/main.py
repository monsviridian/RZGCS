# main.py

import sys
import PySide6
from pathlib import Path
from PySide6.QtCore import QObject, Slot, QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication

from backend.logger import Logger
from backend.serial_connector import SerialConnector
from backend.sensorviewmodel import SensorViewModel
from backend.parameter_model import ParameterTableModel
from backend.flight_view_controller import FlightViewController

class Backend(QObject):
    def __init__(self):
        super().__init__()
        self.logger = Logger()
        self.sensor_model = SensorViewModel()
        self.parameter_model = ParameterTableModel()
        self.serial_connector = SerialConnector(self.sensor_model, self.logger, self.parameter_model)
        # Set simulator as port
        self.serial_connector.setPort("Simulator")
        # Set baudrate (not used for simulator, but required)
        self.serial_connector.setBaudRate(57600)

def main():
    # QApplication statt QGuiApplication für Widget-Support
    app = QApplication(sys.argv)
    
    # Debug-Informationen zur Python-Version und PySide6-Version
    print(f"Python-Version: {sys.version}")
    print(f"PySide6-Version: {PySide6.__version__}")
    
    # Create backend
    backend = Backend()
    
    # Create QML engine
    engine = QQmlApplicationEngine()

    # Expose Python objects to QML
    engine.rootContext().setContextProperty("logger", backend.logger)
    engine.rootContext().setContextProperty("serialConnector", backend.serial_connector)
    engine.rootContext().setContextProperty("sensorModel", backend.sensor_model)
    engine.rootContext().setContextProperty("parameterModel", backend.parameter_model)
    
    # Load main QML file first
    qml_file = Path(__file__).parent.parent / "RZGCSContent" / "App.qml"
    qml_file_path = str(qml_file)
    print(f"Lade QML-Datei: {qml_file_path}")
    
    # Prüfe, ob die Datei existiert
    if not qml_file.exists():
        print(f"FEHLER: QML-Datei nicht gefunden: {qml_file_path}")
        sys.exit(-1)
        
    # QML-Datei laden
    engine.load(QUrl.fromLocalFile(qml_file_path))
    
    # Warten auf das Laden der QML-Datei
    # Status-Prüfung nach dem Laden
    if not engine.rootObjects():
        print(f"FEHLER: Keine Root-Objekte nach dem Laden von {qml_file_path}")
        # Fehler ausgeben, aber nicht beenden, um Anwendung ohne 3D-Karte zu starten
        # sys.exit(-1)
    
    # Create and initialize flight view controller nach dem QML-Laden
    try:
        print("Initialisiere 3D-Kartenansicht...")
        flight_controller = FlightViewController(engine)
        
        # Initialize flight controller with root object
        root_object = engine.rootObjects()[0]
        flight_map_view = flight_controller.initialize(root_object)
        
        if flight_map_view:
            print("3D-Kartenansicht erfolgreich initialisiert")
        else:
            print("Warnung: 3D-Kartenansicht konnte nicht initialisiert werden")
    except Exception as e:
        print(f"Fehler bei der Initialisierung der 3D-Kartenansicht: {str(e)}")
        print("Die Anwendung wird ohne 3D-Karte fortgesetzt.")
        flight_map_view = None
        
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
