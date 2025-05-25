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
from backend.parameter_manager import ParameterManager
from backend.flight_view_controller import FlightViewController
from backend.calibration_view_controller import CalibrationViewController
from backend.motor_test_controller import MotorTestController
from backend.license_ui import LicenseController

class Backend(QObject):
    def __init__(self):
        super().__init__()
        self.logger = Logger()
        self.sensor_model = SensorViewModel()
        self.parameter_model = ParameterTableModel()
        self.parameter_manager = ParameterManager(self.parameter_model, self.logger)
        self.serial_connector = SerialConnector(self.sensor_model, self.logger, self.parameter_model)
        
        # Lizenzcontroller initialisieren
        self.license_controller = LicenseController()
        
        # Verbinde den ParameterManager mit dem SerialConnector
        self.parameter_manager.set_connection(self.serial_connector.get_mavlink_connection())
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
    
    # Add QML import paths for modules
    qml_dir = Path(__file__).parent.parent
    rzgcs_import_path = str(qml_dir / "RZGCSContent")
    print(f"Adding QML import path: {rzgcs_import_path}")
    engine.addImportPath(rzgcs_import_path)

    # Expose Python objects to QML
    engine.rootContext().setContextProperty("logger", backend.logger)
    engine.rootContext().setContextProperty("serialConnector", backend.serial_connector)
    engine.rootContext().setContextProperty("sensorModel", backend.sensor_model)
    engine.rootContext().setContextProperty("parameterModel", backend.parameter_model)
    engine.rootContext().setContextProperty("parameterController", backend.parameter_manager)
    engine.rootContext().setContextProperty("licenseController", backend.license_controller)
    
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
        
        # Registriere den FlightViewController im QML-Kontext
        engine.rootContext().setContextProperty("flightViewController", flight_controller)
        
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
        
    # Initialisiere den Kalibrierungs-Controller
    try:
        print("Initialisiere Kalibrierungsansicht...")
        calibration_controller = CalibrationViewController()
        
        # Registriere den Controller im QML-Kontext
        engine.rootContext().setContextProperty("calibrationViewController", calibration_controller)
        
        # Initialisiere mit dem message_handler vom SerialConnector und dem SensorViewModel
        if calibration_controller.initialize(backend.serial_connector.get_message_handler(), backend.sensor_model):
            print("Kalibrierungsansicht erfolgreich initialisiert")
        else:
            print("Warnung: Kalibrierungsansicht konnte nicht initialisiert werden")
    except Exception as e:
        print(f"Fehler bei der Initialisierung der Kalibrierungsansicht: {str(e)}")
        print("Die Anwendung wird ohne Kalibrierungsfunktion fortgesetzt.")
        
    # Initialisiere den Motor-Test-Controller
    try:
        print("Initialisiere Motor-Test-Ansicht...")
        motor_test_controller = MotorTestController(engine)
        
        # Registriere den Controller im QML-Kontext
        engine.rootContext().setContextProperty("motorTestController", motor_test_controller)
        
        # Initialisiere mit Root-Objekt
        root_object = engine.rootObjects()[0]
        if motor_test_controller.initialize(root_object):
            print("Motor-Test-Ansicht erfolgreich initialisiert")
        else:
            print("Warnung: Motor-Test-Ansicht konnte nicht initialisiert werden")
    except Exception as e:
        print(f"Fehler bei der Initialisierung der Motor-Test-Ansicht: {str(e)}")
        print("Die Anwendung wird ohne Motor-Test-Funktion fortgesetzt.")
        
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
