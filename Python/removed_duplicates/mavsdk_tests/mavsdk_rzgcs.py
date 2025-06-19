#!/usr/bin/env python3
"""
RZGCS mit MAVSDK-Integration über serielle Verbindung

Verwendet die bestehende UI von RZGCS und integriert die MAVSDK-Verbindung
über COM-Port mit dem MAVSDK-Server im Hintergrund.
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

# Importiere die neuen MAVSDK-Komponenten
from backend.enhanced_mavsdk_connector import EnhancedMAVSDKConnector
from backend.sensor_manager import SensorManager  # Verwenden Sie die bestehende SensorManager-Klasse
from rzgcs.viewmodel.drone_view_model import DroneViewModel  # Neuer DroneViewModel


class MAVSDKConnectionManager(QObject):
    """Verwaltet die MAVSDK-Verbindung und kommuniziert mit der UI
    
    Diese Klasse dient der Kompatibilität mit bestehenden Code, der den ConnectionManager verwendet.
    Für neue Funktionen sollte der DroneViewModel verwendet werden.
    """
    
    # Signale für die UI
    connectionChanged = Signal(bool)
    armedChanged = Signal(bool)
    flightModeChanged = Signal(str)
    
    def __init__(self, logger, sensor_viewmodel):
        """Initialisiert den MAVSDK-Connection-Manager
        
        Args:
            logger: Logger-Instanz für die Protokollierung
            sensor_viewmodel: SensorViewModel-Instanz für die Anzeige von Sensordaten
        """
        super().__init__()
        self._logger = logger
        self._sensor_viewmodel = sensor_viewmodel
        self._is_connected = False
        self._is_armed = False
        self._flight_mode = "UNBEKANNT"
        
    def _update_connection_state(self, is_connected):
        """Aktualisiert den Verbindungsstatus (wird vom DroneViewModel aufgerufen)"""
        self._is_connected = is_connected
        self.connectionChanged.emit(is_connected)
        
    def _update_armed_state(self, is_armed):
        """Aktualisiert den Armed-Status (wird vom DroneViewModel aufgerufen)"""
        self._is_armed = is_armed
        self.armedChanged.emit(is_armed)
        
    def _update_flight_mode(self, flight_mode):
        """Aktualisiert den Flugmodus (wird vom DroneViewModel aufgerufen)"""
        self._flight_mode = flight_mode
        self.flightModeChanged.emit(flight_mode)
        
        # MAVSDK-Connector initialisieren
        self._connector = EnhancedMAVSDKConnector(logger)
        
        # Sensor-Manager initialisieren und mit dem Connector verbinden
        self._sensor_manager = SensorManager(self._sensor_viewmodel, logger, None)
        
        # Verbinde Signale zwischen Connector und Sensor-Manager
        # Position
        if hasattr(self._connector, 'position_received') and hasattr(self._sensor_manager, 'handle_position'):
            self._connector.position_received.connect(self._sensor_manager.handle_position)
            
        # Attitude
        if hasattr(self._connector, 'attitude_received') and hasattr(self._sensor_manager, 'handle_attitude'):
            self._connector.attitude_received.connect(self._sensor_manager.handle_attitude)
            
        # Battery
        if hasattr(self._connector, 'battery_received') and hasattr(self._sensor_manager, 'handle_battery'):
            self._connector.battery_received.connect(self._sensor_manager.handle_battery)
            
        # GPS Info
        if hasattr(self._connector, 'gps_info_received') and hasattr(self._sensor_manager, 'handle_gps_info'):
            self._connector.gps_info_received.connect(self._sensor_manager.handle_gps_info)
            
        # Status Text
        if hasattr(self._connector, 'status_text_received') and hasattr(self._sensor_manager, 'handle_status_text'):
            self._connector.status_text_received.connect(self._sensor_manager.handle_status_text)
            
        # Actuator Output Status
        if hasattr(self._connector, 'actuator_output_status_received') and hasattr(self._sensor_manager, 'handle_actuator_output'):
            self._connector.actuator_output_status_received.connect(self._sensor_manager.handle_actuator_output)
        
        # Verbinde Signale zwischen Connector und diesem Manager
        self._connector.connected.connect(self._handle_connected)
        self._connector.disconnected.connect(self._handle_disconnected)
        self._connector.armed_received.connect(self._handle_armed_changed)
        self._connector.flight_mode_received.connect(self._handle_flight_mode_changed)
        self._connector.error_occurred.connect(self._handle_error)
        
        self._logger.addLog("[INFO] MAVSDK-Connection-Manager initialisiert")
    
    @Slot(str, int)
    def connect(self, port, baudrate):
        """Verbindet mit einem Fahrzeug über seriellen Port
        
        Args:
            port: COM-Port (z.B. 'COM3')
            baudrate: Baudrate (z.B. 57600)
            
        Returns:
            bool: True, wenn die Verbindung erfolgreich initiiert wurde
        """
        self._logger.addLog(f"[INFO] Verbinde mit {port} bei {baudrate} Baud...")
        return self._connector.connect_serial(port, int(baudrate))
    
    @Slot()
    def disconnect(self):
        """Trennt die Verbindung zum Fahrzeug"""
        self._logger.addLog("[INFO] Trenne Verbindung...")
        return self._connector.disconnect()
    
    @Slot()
    def arm(self):
        """Armiert das Fahrzeug"""
        self._logger.addLog("[INFO] Armiere Fahrzeug...")
        return self._connector.arm()
    
    @Slot()
    def disarm(self):
        """Disarmiert das Fahrzeug"""
        self._logger.addLog("[INFO] Disarmiere Fahrzeug...")
        return self._connector.disarm()
    
    @Slot()
    def takeoff(self):
        """Lässt das Fahrzeug starten"""
        self._logger.addLog("[INFO] Starte Fahrzeug...")
        return self._connector.takeoff()
    
    @Slot()
    def land(self):
        """Lässt das Fahrzeug landen"""
        self._logger.addLog("[INFO] Lande Fahrzeug...")
        return self._connector.land()
    
    def _handle_connected(self):
        """Wird aufgerufen, wenn die Verbindung hergestellt wurde"""
        self._is_connected = True
        self._logger.addLog("[INFO] Verbindung hergestellt")
        self.connectionChanged.emit(True)
    
    def _handle_disconnected(self):
        """Wird aufgerufen, wenn die Verbindung getrennt wurde"""
        self._is_connected = False
        self._is_armed = False
        self._flight_mode = "UNBEKANNT"
        self._logger.addLog("[INFO] Verbindung getrennt")
        self.connectionChanged.emit(False)
        self.armedChanged.emit(False)
        self.flightModeChanged.emit(self._flight_mode)
    
    def _handle_armed_changed(self, armed):
        """Wird aufgerufen, wenn sich der Armed-Status ändert"""
        self._is_armed = armed
        self._logger.addLog(f"[INFO] Armed-Status: {'ARMED' if armed else 'DISARMED'}")
        self.armedChanged.emit(armed)
    
    def _handle_flight_mode_changed(self, flight_mode):
        """Wird aufgerufen, wenn sich der Flugmodus ändert"""
        self._flight_mode = flight_mode
        self._logger.addLog(f"[INFO] Flugmodus: {flight_mode}")
        self.flightModeChanged.emit(flight_mode)
    
    def _handle_error(self, error_message):
        """Wird aufgerufen, wenn ein Fehler auftritt"""
        self._logger.addLog(f"[FEHLER] {error_message}")
    
    @Property(bool, notify=connectionChanged)
    def is_connected(self):
        """Gibt zurück, ob eine Verbindung besteht"""
        return self._is_connected
    
    @Property(bool, notify=armedChanged)
    def is_armed(self):
        """Gibt zurück, ob das Fahrzeug armiert ist"""
        return self._is_armed
    
    @Property(str, notify=flightModeChanged)
    def flight_mode(self):
        """Gibt den aktuellen Flugmodus zurück"""
        return self._flight_mode


class MAVSDKBackend(QObject):
    """Backend für die RZGCS-Anwendung mit MAVSDK-Integration"""
    
    def __init__(self):
        """Initialisiert das Backend"""
        super().__init__()
        
        # Grundlegende Komponenten
        self.logger = Logger()
        self.sensor_model = SensorViewModel()
        self.parameter_model = ParameterTableModel()
        self.parameter_manager = ParameterManager(self.parameter_model, self.logger)
        
        # MAVSDK-DroneViewModel (MVVM-Architektur)
        self.drone_view_model = DroneViewModel(self.logger)
        
        # Verbinde DroneViewModel-Signale mit SensorViewModel
        self._connect_drone_to_sensor_model()
        
        # Legacy-Kompatibilität: Stellt connection_manager bereit für bestehenden Code
        self.connection_manager = self._create_legacy_connection_manager()
        
        # Zusätzliche Controller
        try:
            self.flight_view_controller = FlightViewController(self.logger, self.sensor_model)
            self.logger.addLog("[INFO] FlightViewController erfolgreich initialisiert")
        except Exception as e:
            self.logger.addLog(f"[WARNUNG] Konnte FlightViewController nicht initialisieren: {str(e)}")
            self.flight_view_controller = None
            
        try:
            self.calibration_view_controller = CalibrationViewController(self.sensor_model, self.logger)
            self.logger.addLog("[INFO] CalibrationViewController erfolgreich initialisiert")
        except Exception as e:
            self.logger.addLog(f"[WARNUNG] Konnte CalibrationViewController nicht initialisieren: {str(e)}")
            self.calibration_view_controller = None
            
        try:
            self.motor_test_controller = MotorTestController(self.logger)
            self.logger.addLog("[INFO] MotorTestController erfolgreich initialisiert")
        except Exception as e:
            self.logger.addLog(f"[WARNUNG] Konnte MotorTestController nicht initialisieren: {str(e)}")
            self.motor_test_controller = None
            
        # License-Controller
        self.license_controller = LicenseController()
        
        # Initialisierungsnachricht
        self.logger.addLog("[INFO] MAVSDK-Backend mit MVVM-Architektur initialisiert")
    
    def _connect_drone_to_sensor_model(self):
        """Verbindet die Signale des DroneViewModel mit dem SensorViewModel"""
        # Verbindungsstatus
        self.drone_view_model.connectionStateChanged.connect(self.sensor_model.setConnectionStatus)
        
        # Telemetrie-Daten
        self.drone_view_model.positionChanged.connect(self._update_position_data)
        self.drone_view_model.attitudeChanged.connect(self._update_attitude_data)
        self.drone_view_model.headingChanged.connect(self._update_heading_data)
        self.drone_view_model.batteryChanged.connect(self._update_battery_data)
        self.drone_view_model.gpsInfoChanged.connect(self._update_gps_data)
        
        # Nachrichten
        self.drone_view_model.messageReceived.connect(self.logger.addLog)
        self.drone_view_model.errorOccurred.connect(lambda msg: self.logger.addLog(f"[FEHLER] {msg}"))
    
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
    
    def _create_legacy_connection_manager(self):
        """Erstellt einen Adapter für den alten ConnectionManager für Legacy-Kompatibilität"""
        # Verwende den vorhandenen MAVSDKConnectionManager mit dem DroneViewModel als Datenquelle
        connection_manager = MAVSDKConnectionManager(self.logger, self.sensor_model)
        
        # Verbinde die Signale des DroneViewModel mit dem ConnectionManager
        self.drone_view_model.connectionStateChanged.connect(connection_manager._update_connection_state)
        self.drone_view_model.armedStateChanged.connect(connection_manager._update_armed_state)
        self.drone_view_model.flightModeChanged.connect(connection_manager._update_flight_mode)
        
        # Überschreibe die connect_serial-Methode, um den DroneViewModel zu verwenden
        connection_manager.connect_serial = self.drone_view_model.connect_serial
        connection_manager.disconnect = self.drone_view_model.disconnect
        
        return connection_manager


def main():
    """Hauptmethode der Anwendung"""
    # Qt-Anwendung erstellen
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    
    # Pfade ermitteln
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.abspath(os.path.join(script_dir, ".."))
    qml_content_dir = os.path.join(project_dir, "RZGCSContent")
    
    # QML-Importpfade setzen
    engine.addImportPath(project_dir)
    engine.addImportPath(qml_content_dir)
    
    # QML-Typen registrieren
    qmlRegisterType(LicenseController, "RZGCS", 1, 0, "LicenseController")
    
    # Backend erstellen
    backend = MAVSDKBackend()
    
    # QML-Kontext einrichten
    root_context = engine.rootContext()
    root_context.setContextProperty("backend", backend)
    root_context.setContextProperty("logger", backend.logger)
    root_context.setContextProperty("sensorViewModel", backend.sensor_model)
    root_context.setContextProperty("connectionManager", backend.connection_manager)
    root_context.setContextProperty("parameterModel", backend.parameter_model)
    
    # Controller für verschiedene Ansichten
    if backend.flight_view_controller:
        root_context.setContextProperty("flightViewController", backend.flight_view_controller)
    
    if backend.calibration_view_controller:
        root_context.setContextProperty("calibrationViewController", backend.calibration_view_controller)
    
    if backend.motor_test_controller:
        root_context.setContextProperty("motorTestController", backend.motor_test_controller)
    
    # License-Controller
    root_context.setContextProperty("licenseController", backend.license_controller)
    
    # QML-Datei laden
    print(f"QML-Importpfade: {engine.importPathList()}")
    qml_file = os.path.join(qml_content_dir, "App.qml")
    print(f"Lade QML-Datei: {qml_file}")
    engine.load(QUrl.fromLocalFile(os.path.abspath(qml_file)))
    
    # Prüfen, ob QML-Datei erfolgreich geladen wurde
    if not engine.rootObjects():
        print("[FEHLER] Konnte QML-Datei nicht laden")
        return -1
    
    print("[OK] RZGCS-UI erfolgreich geladen")
    return app.exec()


if __name__ == "__main__":
    # Aktuelle Python-Version ausgeben
    print(f"Python-Version: {sys.version}")
    print(f"PySide6-Version: {PySide6.__version__}")
    
    # Arbeitsverzeichnis auf Projektverzeichnis setzen für korrekte QML-Pfade
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.abspath(os.path.join(script_dir, ".."))
    os.chdir(project_dir)
    print(f"Arbeitsverzeichnis: {os.getcwd()}")
    
    # Anwendung starten
    sys.exit(main())
