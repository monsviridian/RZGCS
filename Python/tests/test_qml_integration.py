#!/usr/bin/env python3
"""
Integration-Tests für die QML-Komponenten.
Diese Tests validieren die Integration zwischen Python-Backend und QML-Frontend.
"""
import os
import sys
import unittest
import pytest
from unittest.mock import MagicMock, patch
from PySide6.QtCore import QObject, Signal, QUrl
from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine, qmlRegisterType

# Pfad zum Hauptmodul hinzufügen
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Benötigte Module importieren
from rzgcs.viewmodel.sitl_view_model import SITLViewModel
from rzgcs.viewmodel.sensor_viewmodel import SensorViewModel
from rzgcs.viewmodel.mission_view_model import MissionViewModel
from rzgcs.viewmodel.mavsdk_drone_view_model import MAVSDKDroneViewModel
from rzgcs.mvvm.qml_compatibility_adapter import QMLCompatibilityAdapter

class MockLogger:
    """Mock für den Logger."""
    def __init__(self):
        self.logs = []
    
    def addLog(self, message):
        self.logs.append(message)
        print(f"Log: {message}")  # Für bessere Testausgaben

# Pytest-Fixture für QApplication
@pytest.fixture
def app():
    """Stellt eine QApplication-Instanz bereit."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app

# Pytest-Fixture für QmlEngine
@pytest.fixture
def qml_engine(app):
    """Stellt eine QQmlApplicationEngine-Instanz bereit."""
    engine = QQmlApplicationEngine()
    return engine

@pytest.mark.usefixtures("app", "qml_engine")
class TestQMLIntegration:
    """Testet die Integration zwischen Python-Backend und QML-Frontend."""
    
    def setup_method(self):
        """Richtet die Testumgebung ein."""
        self.logger = MockLogger()
        self.sitl_vm = SITLViewModel(self.logger)
        self.sensor_vm = SensorViewModel()
        self.mission_vm = MissionViewModel(self.logger)
        self.drone_vm = MAVSDKDroneViewModel(self.logger)
        self.qml_adapter = QMLCompatibilityAdapter(self.drone_vm, self.logger)
    
    def test_qml_type_registration(self, qml_engine):
        """Testet die Registrierung von Typen für QML."""
        # SensorViewModel als QML-Typ registrieren
        qmlRegisterType(SensorViewModel, "RZGCS", 1, 0, "SensorViewModel")
        
        # Überprüfen, ob die Registrierung erfolgreich war (indirekt durch Instanziierung)
        try:
            # Wenn die Registrierung fehlschlägt, würde ein Fehler auftreten
            # Da wir keinen direkten Weg haben, zu überprüfen, ob die Registrierung erfolgreich war,
            # nehmen wir an, dass sie erfolgreich war, wenn keine Exception auftritt
            pass
        except Exception as e:
            pytest.fail(f"QML-Typ-Registrierung fehlgeschlagen: {str(e)}")
    
    def test_context_property_setting(self, qml_engine):
        """Testet das Setzen von Kontexteigenschaften in der QML-Engine."""
        # Setze die Context-Properties
        qml_engine.rootContext().setContextProperty("sitlViewModel", self.sitl_vm)
        qml_engine.rootContext().setContextProperty("sensorModel", self.sensor_vm)
        qml_engine.rootContext().setContextProperty("missionViewModel", self.mission_vm)
        qml_engine.rootContext().setContextProperty("droneViewModel", self.drone_vm)
        qml_engine.rootContext().setContextProperty("serialConnector", self.qml_adapter)
        qml_engine.rootContext().setContextProperty("logger", self.logger)
        
        # Überprüfen ist schwierig, da wir keinen direkten Zugriff auf die Context-Properties haben
        # Wir nehmen an, dass es funktioniert hat, wenn keine Exception auftritt
    
    @pytest.mark.skipif(not os.path.exists(os.path.join(os.path.dirname(__file__), '..', '..', 'RZGCSContent', 'SITLView.ui.qml')),
                       reason="SITLView.ui.qml nicht gefunden")
    def test_sitl_view_loading(self, qml_engine):
        """Testet das Laden der SITL-View."""
        # Setze die Context-Properties
        qml_engine.rootContext().setContextProperty("sitlViewModel", self.sitl_vm)
        
        # Pfad zur QML-Datei
        qml_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 
                                                    '..', '..', 'RZGCSContent', 'SITLView.ui.qml'))
        
        # Lade die QML-Datei
        qml_engine.load(QUrl.fromLocalFile(qml_file_path))
        
        # Überprüfe, ob das Laden erfolgreich war
        assert len(qml_engine.rootObjects()) > 0, "QML-Datei konnte nicht geladen werden"
    
    def test_signal_connections(self):
        """Testet die Signalverbindungen zwischen den ViewModels."""
        # Erstelle Signal-Handler
        self.sitl_signal_received = False
        self.drone_signal_received = False
        self.mission_signal_received = False
        
        # Handler für Signale
        def sitl_handler():
            self.sitl_signal_received = True
        
        def drone_handler(connected):
            self.drone_signal_received = True
        
        def mission_handler():
            self.mission_signal_received = True
        
        # Verbinde Signale
        self.sitl_vm.simulationStarted.connect(sitl_handler)
        self.drone_vm.connectionStateChanged.connect(drone_handler)
        self.mission_vm.missionUpdatedSignal.connect(mission_handler)
        
        # Löse Signale aus
        self.sitl_vm.simulationStarted()
        self.drone_vm.connectionStateChanged.emit(True)
        self.mission_vm.missionUpdatedSignal.emit()
        
        # Überprüfungen
        assert self.sitl_signal_received, "SITL-Signal wurde nicht empfangen"
        assert self.drone_signal_received, "Drone-Signal wurde nicht empfangen"
        assert self.mission_signal_received, "Mission-Signal wurde nicht empfangen"
    
    def test_data_flow_from_sitl_to_sensor(self):
        """Testet den Datenfluss von SITL über das DroneViewModel zum SensorViewModel."""
        # Simuliere, dass SITL eine Verbindung hergestellt hat
        self.sitl_vm._auto_connect_to_simulation()
        
        # Überprüfe, ob das autoConnectRequested-Signal emittiert wurde
        # (indirekt durch Verbindung mit einer Testfunktion)
        self.auto_connect_signal_received = False
        self.connection_string = None
        
        def on_auto_connect_requested(conn_str):
            self.auto_connect_signal_received = True
            self.connection_string = conn_str
        
        self.sitl_vm.autoConnectRequested.connect(on_auto_connect_requested)
        self.sitl_vm._auto_connect_to_simulation()
        
        assert self.auto_connect_signal_received, "autoConnectRequested-Signal wurde nicht emittiert"
        assert "tcp:" in self.connection_string, "Verbindungsstring enthält nicht das erwartete Format"
        
        # In einer vollständigen Integration würde dieses Signal den serialConnector (QMLCompatibilityAdapter)
        # dazu veranlassen, eine Verbindung herzustellen, was dann zu Telemetriedaten führen würde,
        # die an das SensorViewModel weitergeleitet werden
        
        # Da wir keinen echten MAVSDK-Server starten können, simulieren wir stattdessen die Telemetriedaten
        telemetry_data = {
            "position": {
                "latitude_deg": 49.445232,
                "longitude_deg": 7.769488,
                "relative_altitude_m": 100.0
            },
            "attitude": {
                "roll_deg": 5.0,
                "pitch_deg": 10.0,
                "yaw_deg": 45.0
            },
            "battery": {
                "remaining_percent": 75.0,
                "voltage_v": 12.5,
                "current_a": 2.1
            },
            "gps_info": {
                "num_satellites": 8,
                "fix_type": 3
            }
        }
        
        # Aktualisiere das SensorViewModel direkt mit den Telemetriedaten
        self.sensor_vm.update_from_telemetry(telemetry_data)
        
        # Überprüfe, ob die Daten korrekt aktualisiert wurden
        assert self.sensor_vm.getSensorValue("latitude") == 49.445232
        assert self.sensor_vm.getSensorValue("longitude") == 7.769488
        assert self.sensor_vm.getSensorValue("altitude") == 100.0
        assert self.sensor_vm.getSensorValue("roll") == 5.0
        assert self.sensor_vm.getSensorValue("pitch") == 10.0
        assert self.sensor_vm.getSensorValue("battery") == 75.0

# Main-Funktion für direktes Ausführen der Tests
if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
