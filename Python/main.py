# main.py

import os
import sys
from pathlib import Path
from PySide6.QtCore import QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from autogen.settings import url, import_paths
from backend.logger import Logger
from backend.serial_connector import SerialConnector
from backend.sensorviewmodel import SensorViewModel

if __name__ == '__main__':
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()

    logger = Logger()
    sensor_model = SensorViewModel()
    serial_connector = SerialConnector(sensor_model, logger)

    engine.rootContext().setContextProperty("sensorModel", sensor_model)
    engine.rootContext().setContextProperty("serialConnector", serial_connector)
    engine.rootContext().setContextProperty("logger", logger)

    app_dir = Path(__file__).parent.parent
    engine.addImportPath(os.fspath(app_dir))
    for path in import_paths:
        engine.addImportPath(os.fspath(app_dir / path))

    engine.load(os.fspath(app_dir / url))
    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec())
