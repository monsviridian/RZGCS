#!/usr/bin/env python3
"""
RZGCS mit MAVSDK-Integration im MVVM-Pattern

Dieses Programm startet die RZGCS-Anwendung mit der neuen MAVSDK-Integration,
die einen sauberen MVVM-Ansatz verwendet, frei von Metaklassen-Konflikten.
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
# Verwende den neuen SensorViewModel aus dem rzgcs.viewmodel-Paket
from rzgcs.viewmodel.sensor_viewmodel import SensorViewModel
from backend.parameter_model import ParameterTableModel
from backend.parameter_manager import ParameterManager
from backend.flight_view_controller import FlightViewController
from backend.calibration_view_controller import CalibrationViewController
from backend.motor_test_controller import MotorTestController
from backend.license_ui import LicenseController

# Importiere die neue MAVSDK-MVVM-Integration
from rzgcs.viewmodel.mavsdk_drone_view_model import MAVSDKDroneViewModel
from rzgcs.mvvm.qml_compatibility_adapter import QMLCompatibilityAdapter


class RZGCSBackend(QObject):
    """Backend für die RZGCS-Anwendung mit MAVSDK-Integration in MVVM-Architektur"""
    
    def __init__(self):
        """Initialisiert das Backend"""
        super().__init__()
        
        # Grundlegende Komponenten
        self.logger = Logger()
        self.logger.addLog("[INFO] Initialisiere RZGCS mit MAVSDK-MVVM-Integration")
        
        # Sensor-ViewModel
        self.sensor_model = SensorViewModel()
        
        # Parameter-Modell und Manager
        self.parameter_model = ParameterTableModel()
        self.parameter_manager = ParameterManager(self.parameter_model, self.logger)
        
        # MAVSDK-ViewModel (MVVM-Architektur)
        self.drone_view_model = MAVSDKDroneViewModel(self.logger)
        
        # QML-Kompatibilitätsadapter für das DroneViewModel
        self.qml_adapter = QMLCompatibilityAdapter(self.drone_view_model, self.logger)
        
        # Verbinde die ViewModels
        self._connect_view_models()
        
        # Erstelle die Controller
        self._initialize_controllers()
        
        # Initialisierung abgeschlossen
        self.logger.addLog("[INFO] RZGCS mit MAVSDK-MVVM-Integration initialisiert")
    
    def _connect_view_models(self):
        """Verbindet die ViewModels miteinander"""
        # Verbindungsstatus
        self.drone_view_model.connectionStateChanged.connect(self._update_connection_status)
        
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
        
        # Verbinde das allgemeine Telemetrie-Signal mit dem SensorViewModel
        # Dies ermöglicht die direkte Aktualisierung des SensorViewModel aus MAVSDK-Daten
        if hasattr(self.drone_view_model, 'signals') and hasattr(self.drone_view_model.signals, 'telemetry_updated'):
            self.logger.addLog("[INFO] Verbinde Telemetrie-Signal mit SensorViewModel")
            self.drone_view_model.signals.telemetry_updated.connect(self.sensor_model.update_from_telemetry)
    
    def _update_connection_status(self, is_connected: bool):
        """Aktualisiert den Verbindungsstatus im SensorViewModel"""
        self.logger.addLog(f"[INFO] Verbindungsstatus: {'Verbunden' if is_connected else 'Getrennt'}")
        # Verbindungsstatus als Sensor aktualisieren
        self.sensor_model.update_sensor("connection_status", 1.0 if is_connected else 0.0)
        self.sensor_model.updateQmlSensor("Verbindung", "Aktiv" if is_connected else "Inaktiv", "")
    
    def _update_position_data(self, position_data: dict):
        """Aktualisiert die Positionsdaten im SensorViewModel"""
        # Positionsdaten in einzelne Sensoren umwandeln
        self.sensor_model.update_sensor("latitude", position_data.get("latitude_deg", 0.0))
        self.sensor_model.update_sensor("longitude", position_data.get("longitude_deg", 0.0))
        self.sensor_model.update_sensor("altitude", position_data.get("relative_altitude_m", 0.0))
        
        # QML-Sensoren aktualisieren
        self.sensor_model.updateQmlSensor("Latitude", position_data.get("latitude_deg", 0.0), "°")
        self.sensor_model.updateQmlSensor("Longitude", position_data.get("longitude_deg", 0.0), "°")
        self.sensor_model.updateQmlSensor("Höhe", position_data.get("relative_altitude_m", 0.0), "m")
    
    def _update_attitude_data(self, attitude_data: dict):
        """Aktualisiert die Lagedaten im SensorViewModel"""
        # Lagedaten in einzelne Sensoren umwandeln
        self.sensor_model.update_sensor("roll", attitude_data.get("roll_deg", 0.0))
        self.sensor_model.update_sensor("pitch", attitude_data.get("pitch_deg", 0.0))
        
        # QML-Sensoren aktualisieren
        self.sensor_model.updateQmlSensor("Roll", attitude_data.get("roll_deg", 0.0), "°")
        self.sensor_model.updateQmlSensor("Pitch", attitude_data.get("pitch_deg", 0.0), "°")
    
    def _update_heading_data(self, heading: float):
        """Aktualisiert den Heading-Wert im SensorViewModel"""
        self.sensor_model.update_sensor("heading", heading)
        self.sensor_model.updateQmlSensor("Heading", heading, "°")
    
    def _update_battery_data(self, battery_data: dict):
        """Aktualisiert die Batteriedaten im SensorViewModel"""
        # Batteriedaten in einzelne Sensoren umwandeln
        battery_percent = battery_data.get("remaining_percent", 0.0)
        voltage = battery_data.get("voltage_v", 0.0)
        current = battery_data.get("current_a", 0.0)
        
        self.sensor_model.update_sensor("battery", battery_percent)
        self.sensor_model.update_sensor("voltage", voltage)
        self.sensor_model.update_sensor("current", current)
        
        # QML-Sensoren aktualisieren
        self.sensor_model.updateQmlSensor("Batterie", battery_percent, "%")
        self.sensor_model.updateQmlSensor("Spannung", voltage, "V")
        self.sensor_model.updateQmlSensor("Strom", current, "A")
    
    def _update_gps_data(self, gps_data: dict):
        """Aktualisiert die GPS-Daten im SensorViewModel"""
        # GPS-Daten in einzelne Sensoren umwandeln
        satellites = gps_data.get("num_satellites", 0)
        fix_type = gps_data.get("fix_type", 0)
        
        self.sensor_model.update_sensor("satellites", float(satellites))
        self.sensor_model.update_sensor("gps_fix", float(fix_type))
        
        # QML-Sensoren aktualisieren
        self.sensor_model.updateQmlSensor("Satelliten", satellites, "")
        
        # Fix-Typ in Text umwandeln
        fix_text = "Keine Pos."
        if fix_type == 2:
            fix_text = "2D Fix"
        elif fix_type == 3:
            fix_text = "3D Fix"
        elif fix_type > 3:
            fix_text = "RTK Fix"
            
        self.sensor_model.updateQmlSensor("GPS Fix", fix_text, "")
    
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
    backend = RZGCSBackend()
    
    # Typen für QML registrieren
    qmlRegisterType(SensorViewModel, "RZGCS", 1, 0, "SensorViewModel")
    
    # Typen für QML setzen
    engine.rootContext().setContextProperty("backend", backend)
    engine.rootContext().setContextProperty("sensorModel", backend.sensor_model)
    engine.rootContext().setContextProperty("logger", backend.logger)
    engine.rootContext().setContextProperty("parameterModel", backend.parameter_model)
    engine.rootContext().setContextProperty("parameterManager", backend.parameter_manager)
    
    # WICHTIG: Füge den QML-Kompatibilitätsadapter als serialConnector zur QML-Engine hinzu
    # Die UI erwartet ein Objekt namens 'serialConnector' für die Verbindungssteuerung
    engine.rootContext().setContextProperty("serialConnector", backend.qml_adapter)
    engine.rootContext().setContextProperty("droneViewModel", backend.drone_view_model)
    
    # Controller für QML setzen
    if backend.flight_view_controller:
        engine.rootContext().setContextProperty("flightViewController", backend.flight_view_controller)
    
    if backend.calibration_view_controller:
        engine.rootContext().setContextProperty("calibrationViewController", backend.calibration_view_controller)
    
    if backend.motor_test_controller:
        engine.rootContext().setContextProperty("motorTestController", backend.motor_test_controller)
    
    engine.rootContext().setContextProperty("licenseController", backend.license_controller)
    
    # Hauptfenster laden (App.qml in RZGCSContent)
    # Finde den korrekten Pfad zur QML-Datei
    project_dir = Path(os.path.dirname(os.path.abspath(__file__))).parent
    qml_file = project_dir / "RZGCSContent" / "App.qml"
    
    # Prüfe, ob die Datei existiert
    if not qml_file.exists():
        print(f"[FEHLER] QML-Datei nicht gefunden: {qml_file}")
        # Versuche alternative Pfade, falls der Hauptpfad nicht existiert
        alternative_paths = [
            project_dir / "RZGCS" / "RZGCSContent" / "App.qml",
            project_dir / "build" / "RZGCS" / "RZGCSContent" / "App.qml"
        ]
        
        for alt_path in alternative_paths:
            if alt_path.exists():
                qml_file = alt_path
                print(f"[INFO] Alternative QML-Datei gefunden: {qml_file}")
                break
        else:
            print("[FEHLER] Keine QML-Datei gefunden. Versuche mit UI zu starten...")
    
    # Lade die QML-Datei
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
