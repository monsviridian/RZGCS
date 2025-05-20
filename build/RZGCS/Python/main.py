# main.py

import sys
from pathlib import Path
from PySide6.QtCore import QObject, Slot, QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from backend.logger import Logger
from backend.serial_connector import SerialConnector
from backend.sensorviewmodel import SensorViewModel
from backend.parameter_model import ParameterTableModel

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
    app = QGuiApplication(sys.argv)
    
    # Create backend
    backend = Backend()
    
    # Create QML engine
    engine = QQmlApplicationEngine()

    # Expose Python objects to QML
    engine.rootContext().setContextProperty("logger", backend.logger)
    engine.rootContext().setContextProperty("serialConnector", backend.serial_connector)
    engine.rootContext().setContextProperty("sensorModel", backend.sensor_model)
    engine.rootContext().setContextProperty("parameterModel", backend.parameter_model)

    # Load main QML file
    qml_file = Path(__file__).parent.parent / "RZGCSContent" / "App.qml"
    engine.load(QUrl.fromLocalFile(str(qml_file)))
    
    if not engine.rootObjects():
        sys.exit(-1)
        
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
