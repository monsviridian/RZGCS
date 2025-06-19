#!/usr/bin/env python3
"""
RZGCS mit MAVSDK-Integration über serielle Verbindung in MVVM-Architektur

Verwendet die bestehende UI von RZGCS und integriert die MAVSDK-Verbindung
über COM-Port mit dem MAVSDK-Server im Hintergrund. Nutzt eine saubere
MVVM-Architektur mit dem EnhancedDroneViewModel.
"""

import sys
import os
import PySide6
from pathlib import Path
from PySide6.QtCore import QObject, Slot, QUrl, Signal, Property
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine, qmlRegisterType

# Importiere bestehende Komponenten
from backend.logger import Logger
from backend.sensorviewmodel import SensorViewModel
from backend.parameter_model import ParameterTableModel
from backend.parameter_manager import ParameterManager
from backend.flight_view_controller import FlightViewController
from backend.calibration_view_controller import CalibrationViewController
from backend.motor_test_controller import MotorTestController
from backend.license_ui import LicenseController

# Importiere die MAVSDK-Komponenten mit MVVM-Architektur
from rzgcs.mvvm.enhanced_drone_view_model import EnhancedDroneViewModel
from rzgcs.mvvm.qml_compatibility_adapter import QMLCompatibilityAdapter
from rzgcs.mvvm.drone_signal_hub import DroneSignalHub


class MAVSDKBackendMVVM(QObject):
    """Backend für die RZGCS-Anwendung mit MAVSDK-Integration in MVVM-Architektur"""
    
    def __init__(self):
        """Initialisiert das Backend"""
        super().__init__()
        
        # Grundlegende Komponenten
        self.logger = Logger()
        self.logger.addLog("[INFO] Initialisiere MAVSDK-Backend mit MVVM-Architektur")
        
        # Sensor-ViewModel
        self.sensor_model = SensorViewModel()
        
        # Parameter-Modell und Manager
        self.parameter_model = ParameterTableModel()
        self.parameter_manager = ParameterManager(self.parameter_model, self.logger)
        
        # MAVSDK-ViewModel (MVVM-Architektur)
        self.drone_view_model = EnhancedDroneViewModel(self.logger)
        
        # QML-Kompatibilitätsadapter für die bestehende RZGCS-UI
        self.serial_connector = QMLCompatibilityAdapter(self.drone_view_model)
        
        # Verbinde die ViewModels
        self._connect_view_models()
        
        # Erstelle die Controller
        self._initialize_controllers()
        
        # Initialisierung abgeschlossen
        self.logger.addLog("[INFO] MAVSDK-Backend mit MVVM-Architektur initialisiert")
    
    def _connect_view_models(self):
        """Verbindet die ViewModels miteinander"""
        # Verbindungsstatus
        self.drone_view_model.connectionStateChanged.connect(self.sensor_model.setConnectionStatus)
        
        # Positions- und Lageparameter
        self.drone_view_model.positionChanged.connect(self._update_position_data)
        self.drone_view_model.attitudeChanged.connect(self._update_attitude_data)
        self.drone_view_model.headingChanged.connect(self._update_heading_data)
        
        # Batterie und GPS
        self.drone_view_model.batteryChanged.connect(self._update_battery_data)
        self.drone_view_model.gpsInfoChanged.connect(self._update_gps_data)
        
        # Nachrichten
        self.drone_view_model.messageReceived.connect(self.logger.addLog)
        self.drone_view_model.errorOccurred.connect(lambda msg: self.logger.addLog(f"[FEHLER] {msg}"))
        
        # Spezielle Systeminformationen für die Preflight-View
        self.drone_view_model.systemInfoReceived.connect(lambda msg: self.logger.addLog(msg))
    
    def _initialize_controllers(self):
        """Initialisiert die Controller"""
        # Flug-View-Controller
        try:
            self.flight_view_controller = FlightViewController(self.logger, self.sensor_model)
            self.logger.addLog("[INFO] FlightViewController erfolgreich initialisiert")
        except Exception as e:
            self.logger.addLog(f"[WARNUNG] Konnte FlightViewController nicht initialisieren: {str(e)}")
            self.flight_view_controller = None
        
        # Kalibrierungs-View-Controller
        try:
            self.calibration_view_controller = CalibrationViewController(self.sensor_model, self.logger)
            self.logger.addLog("[INFO] CalibrationViewController erfolgreich initialisiert")
        except Exception as e:
            self.logger.addLog(f"[WARNUNG] Konnte CalibrationViewController nicht initialisieren: {str(e)}")
            self.calibration_view_controller = None
        
        # Motor-Test-Controller
        try:
            self.motor_test_controller = MotorTestController(self.logger)
            self.logger.addLog("[INFO] MotorTestController erfolgreich initialisiert")
        except Exception as e:
            self.logger.addLog(f"[WARNUNG] Konnte MotorTestController nicht initialisieren: {str(e)}")
            self.motor_test_controller = None
        
        # Lizenz-Controller
        self.license_controller = LicenseController()
    
    def _update_position_data(self, position):
        """Aktualisiert die Positionsdaten im SensorViewModel"""
        self.sensor_model.setLatitude(position['latitude_deg'])
        self.sensor_model.setLongitude(position['longitude_deg'])
        self.sensor_model.setAltitude(position['relative_altitude_m'])
    
    def _update_attitude_data(self, attitude):
        """Aktualisiert die Lagedaten im SensorViewModel"""
        self.sensor_model.setRoll(attitude['roll_deg'])
        self.sensor_model.setPitch(attitude['pitch_deg'])
    
    def _update_heading_data(self, heading):
        """Aktualisiert das Heading im SensorViewModel"""
        self.sensor_model.setYaw(heading)
    
    def _update_battery_data(self, battery):
        """Aktualisiert die Batteriedaten im SensorViewModel"""
        self.sensor_model.setBatteryLevel(battery['remaining_percent'])
        self.sensor_model.setBatteryVoltage(battery['voltage_v'])
    
    def _update_gps_data(self, gps_info):
        """Aktualisiert die GPS-Daten im SensorViewModel"""
        self.sensor_model.setGpsSatelliteCount(gps_info['num_satellites'])
        self.sensor_model.setGpsFixType(gps_info['fix_type'])


def main():
    """Hauptfunktion der Anwendung"""
    # Aktuelle Python-Version ausgeben
    print(f"Python-Version: {sys.version}")
    
    # Aktuelle PySide6-Version ausgeben
    print(f"PySide6-Version: {PySide6.__version__}")
    
    # Arbeitsverzeichnis setzen und anzeigen
    os.chdir(str(Path(__file__).resolve().parent.parent))
    print(f"Arbeitsverzeichnis: {os.getcwd()}")
    
    # QML-Ressourcenpfad hinzufügen
    qml_dir = Path(__file__).resolve().parent / "qml"
    
    # Anwendung erstellen
    app = QGuiApplication(sys.argv)
    
    # QML-Engine erstellen
    engine = QQmlApplicationEngine()
    
    # Backend erstellen
    backend = MAVSDKBackendMVVM()
    
    # Typen für QML registrieren
    qmlRegisterType(SensorViewModel, "RZGCS", 1, 0, "SensorViewModel")
    
    # Typen für QML setzen
    engine.rootContext().setContextProperty("backend", backend)
    engine.rootContext().setContextProperty("sensorViewModel", backend.sensor_model)
    engine.rootContext().setContextProperty("logger", backend.logger)
    engine.rootContext().setContextProperty("parameterModel", backend.parameter_model)
    engine.rootContext().setContextProperty("parameterManager", backend.parameter_manager)
    engine.rootContext().setContextProperty("droneViewModel", backend.drone_view_model)
    
    # QML-Kompatibilitätsadapter für die bestehende RZGCS-UI als serialConnector registrieren
    # WICHTIG: Die UI erwartet einen serialConnector für viele Funktionen
    engine.rootContext().setContextProperty("serialConnector", backend.serial_connector)
    
    # Controller für QML setzen
    if backend.flight_view_controller:
        engine.rootContext().setContextProperty("flightViewController", backend.flight_view_controller)
    
    if backend.calibration_view_controller:
        engine.rootContext().setContextProperty("calibrationViewController", backend.calibration_view_controller)
    
    if backend.motor_test_controller:
        engine.rootContext().setContextProperty("motorTestController", backend.motor_test_controller)
    
    engine.rootContext().setContextProperty("licenseController", backend.license_controller)
    
    # Hauptfenster laden
    qml_file = qml_dir / "MainWindow.qml"
    url = QUrl.fromLocalFile(str(qml_file))
    engine.load(url)
    
    # Prüfen, ob QML-Datei geladen wurde
    if not engine.rootObjects():
        print(f"[FEHLER] Konnte QML-Datei nicht laden: {url.toString()}")
        return 1
    
    # Eventschleife starten
    return app.exec()


if __name__ == "__main__":
    # Anwendung starten
    sys.exit(main())
