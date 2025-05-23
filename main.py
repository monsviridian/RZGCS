import sys
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

# Backend-Importe
from backend.sensorviewmodel import SensorViewModel
from backend.logger import Logger
from backend.parameter_model import ParameterTableModel
from backend.serial_connector import SerialConnector

if __name__ == "__main__":
    app = QGuiApplication(sys.argv)
    sensor_model = SensorViewModel()
    logger = Logger()
    parameter_model = ParameterTableModel()
    serial_connector = SerialConnector(sensor_model, logger, parameter_model)
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("sensorModel", sensor_model)
    engine.rootContext().setContextProperty("serialConnector", serial_connector)
    engine.rootContext().setContextProperty("parameterModel", parameter_model)
    engine.rootContext().setContextProperty("logger", logger)  # Logger als Kontext-Property hinzufügen
    
    # Füge für Tests ein paar System-Info-Logs hinzu
    logger.addSystemInfoLog("Frame: QUAD/X")
    logger.addSystemInfoLog("RCOut: PWM:1-10")
    logger.addSystemInfoLog("MicoAir743 001F0041 3133510F 35313933")
    logger.addSystemInfoLog("ChibiOS: c6d0293e")
    logger.addSystemInfoLog("ArduCopter V4.7.0-dev (abd8c902)")
    logger.addSystemInfoLog("PreArm: Compass not calibrated")
    
    # Lade die Test-Anwendung für Logs
    import os
    qml_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "RZGCSContent", "TestLogs.qml")
    engine.load(qml_file)
    print(f"Loading Test QML file: {qml_file}")
    
    # Starte die Anwendung
    if not engine.rootObjects():
        sys.exit(-1)
        
    sys.exit(app.exec())