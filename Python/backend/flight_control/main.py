"""Flugsteuerungs-Main.

Dieses Modul enthält die Main-Klasse für die Flugsteuerung.
"""

import sys
from pathlib import Path
from PySide6.QtCore import QObject, QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine, qmlRegisterType

from .controllers.flight_control_controller import FlightControlController

class FlightControlMain(QObject):
    """Flugsteuerungs-Main.
    
    Diese Klasse initialisiert die Flugsteuerungs-Anwendung.
    
    Attributes:
        _app: QGuiApplication
        _engine: QQmlApplicationEngine
        _controller: FlightControlController
    """
    
    def __init__(self):
        """Initialisierung."""
        super().__init__()
        
        # QML-Typen registrieren
        qmlRegisterType(FlightControlController, "FlightControl", 1, 0, "FlightControlController")
        
        # Anwendung erstellen
        self._app = QGuiApplication(sys.argv)
        
        # QML-Engine erstellen
        self._engine = QQmlApplicationEngine()
        
        # Controller erstellen
        self._controller = FlightControlController()
        
        # QML-Kontext-Eigenschaft setzen
        self._engine.rootContext().setContextProperty("flightControlController", self._controller)
        
        # QML-Datei laden
        qml_file = Path(__file__).parent.parent.parent / "RZGCSContent" / "RZGCS" / "FlightControlView.qml"
        self._engine.load(QUrl.fromLocalFile(str(qml_file)))
        
        # Anwendung ausführen
        sys.exit(self._app.exec()) 