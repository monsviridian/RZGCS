# main.py

import sys
import os
import PySide6
from pathlib import Path
from PySide6.QtCore import QCoreApplication, QDir, QObject, QUrl, QTimer
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine, qmlRegisterType
from PySide6.QtWidgets import QApplication
import traceback  # Debug-Ausgaben für Fehler bei der Initialisierung

from backend.logger import Logger
from backend.serial_connector import SerialConnector
from backend.flight_control.viewmodels.sensor_viewmodel import SensorViewModel  # Lokaler Import aus dem backend-Modul
from backend.sensor_manager import SensorManager
from backend.parameter_model import ParameterTableModel
from backend.parameter_manager import ParameterManager
from backend.flight_view_controller import FlightViewController
from backend.calibration_view_controller import CalibrationViewController
# from backend.motor_test_controller import MotorTestController
from backend.license_ui import LicenseController

# MAVLink-Implementierung wird ausschließlich verwendet
from backend.mavlink_connector import MAVLinkConnector, ConnectorType

# Neue Module aus der Connection-Integration
from backend.connection.viewmodels.connection_adapter import ConnectionAdapter, ConnectionStatus

# Telemetrie-ViewModel
from backend.flight_control.viewmodels.telemetry_viewmodel import TelemetryViewModel
from backend.flight_planning.viewmodels.flight_planning_viewmodel import FlightPlanningViewModel
from backend.flight_planning.services.flight_planning_service import FlightPlanningService

# Firmware-ViewModel
from backend.firmware.firmware_viewmodel import FirmwareViewModel

class Backend(QObject):
    def __init__(self):
        try:
            super().__init__()
            print("Backend: Initialisiere Logger...")
            self.logger = Logger()
            print("Backend: Initialisiere SensorViewModel...")
            self.sensor_model = SensorViewModel()
            print("Backend: Initialisiere ParameterTableModel...")
            self.parameter_model = ParameterTableModel()
            print("Backend: Initialisiere ParameterManager...")
            self.parameter_manager = ParameterManager(self.parameter_model, self.logger)
            
            # Ausschließlich MAVLink-basierte Implementation verwenden
            print("Backend: Initialisiere SerialConnector...")
            self.logger.addLog("Verwende MAVLink-Connector für die Kommunikation")
            try:
                self.serial_connector = SerialConnector(self.sensor_model, self.logger, self.parameter_model)
                self.connector = self.serial_connector  # Alias für einheitlichen Zugriff
                
                # Verbinde SerialConnector-Signale mit SensorViewModel
                print("Backend: Verbinde SerialConnector-Signale mit SensorViewModel...")
                self._connect_serial_signals_to_sensor_model()
                
            except Exception as e:
                print(f"FEHLER bei der SerialConnector-Initialisierung: {str(e)}")
                print("Stack-Trace:")
                traceback.print_exc()
                self.serial_connector = None
                self.connector = None
                
            # Wir verwenden den SensorManager aus dem SerialConnector
            # Das ist wichtig, um doppelte Instanzen zu vermeiden
            if self.serial_connector:
                print("Backend: Hole message_handler vom SerialConnector...")
                message_handler = self.serial_connector.get_message_handler()
            
            # Lizenzcontroller initialisieren
            print("Backend: Initialisiere LicenseController...")
            self.license_controller = LicenseController()
            
            # ConnectionAdapter initialisieren und mit SerialConnector verbinden
            print("Backend: Initialisiere ConnectionAdapter...")
            try:
                # Unabhängig vom SerialConnector-Status immer einen ConnectionAdapter erstellen
                if self.serial_connector:
                    # Debug-Info zum SerialConnector
                    print(f"SerialConnector Port: {self.serial_connector.port}")
                    print(f"SerialConnector BaudRate: {self.serial_connector.baud_rate}")
                    print(f"SerialConnector Connected: {self.serial_connector.connected}")
                    self.connection_viewmodel = ConnectionAdapter(self.serial_connector)
                    print("Backend: ConnectionAdapter mit SerialConnector erfolgreich initialisiert.")
                else:
                    print("WARNUNG: SerialConnector ist nicht initialisiert, erstelle einen Dummy ConnectionAdapter")
                    # Erstelle einen Dummy ConnectionAdapter um AttributeError zu vermeiden
                    from PySide6.QtCore import QObject
                    class DummySerialConnector(QObject):
                        def __init__(self):
                            super().__init__()
                            self.port = "NICHT VERFÜGBAR"
                            self.baud_rate = 0
                            self.connected = False
                        
                        def connect(self):
                            return False
                            
                        def disconnect(self):
                            pass
                            
                        def setPort(self, port):
                            self.port = port
                            
                        def setBaudRate(self, rate):
                            self.baud_rate = rate
                    
                    # Erstelle einen Dummy ConnectionAdapter
                    self.connection_viewmodel = ConnectionAdapter(DummySerialConnector())
                    print("Backend: Dummy ConnectionAdapter erfolgreich initialisiert.")
            except Exception as e:
                print(f"FEHLER bei der ConnectionAdapter-Initialisierung: {str(e)}")
                # Stattdessen Dummy-Adapter erstellen
                from PySide6.QtCore import QObject
                class DummySerialConnector(QObject):
                    def __init__(self):
                        super().__init__()
                        self.port = "FEHLER"
                        self.baud_rate = 0
                        self.connected = False
                        
                    def connect(self):
                        return False
                        
                    def disconnect(self):
                        pass
                        
                    def setPort(self, port):
                        self.port = port
                        
                    def setBaudRate(self, rate):
                        self.baud_rate = rate
                
                # Erstelle einen Dummy ConnectionAdapter
                self.connection_viewmodel = ConnectionAdapter(DummySerialConnector())
                print("Backend: Fallback Dummy ConnectionAdapter nach Fehler initialisiert.")
            
            # TelemetryViewModel initialisieren und mit SerialConnector verbinden
            print("Backend: Initialisiere TelemetryViewModel...")
            try:
                self.telemetry_viewmodel = TelemetryViewModel()
                if self.serial_connector:
                    # Verwende die neue Hilfsfunktion zum Registrieren des TelemetryViewModel
                    success = self.serial_connector.register_telemetry_viewmodel(self.telemetry_viewmodel)
                    if success:
                        print("Backend: TelemetryViewModel erfolgreich registriert")
                    else:
                        print("Backend: Fehler beim Registrieren des TelemetryViewModel")
                print("Backend: TelemetryViewModel erfolgreich initialisiert")
            except Exception as e:
                print(f"FEHLER bei der TelemetryViewModel-Initialisierung: {str(e)}")
                print("Stack-Trace:")
                traceback.print_exc()
                # Erstelle ein Dummy-TelemetryViewModel als Fallback
                self.telemetry_viewmodel = None
            
            # Verbinde den ParameterManager mit dem SerialConnector
            if self.serial_connector:
                print("Backend: Verbinde ParameterManager mit SerialConnector...")
                self.parameter_manager.set_connection(self.serial_connector.get_mavlink_connection())
                # Set simulator as port
                print("Backend: Setze Port und Baudrate...")
                self.serial_connector.setPort("Simulator")
                # Set baudrate (not used for simulator, but required)
                self.serial_connector.setBaudRate(115200)
            else:
                print("Backend: Kein SerialConnector verfügbar, überspringe ParameterManager-Verbindung")
            
            # FirmwareManager initialisieren
            print("Backend: Initialisiere FirmwareManager...")
            self.firmware_manager = FirmwareViewModel()
            print("Backend: FirmwareManager erfolgreich initialisiert")
                
            print("Backend: Initialisierung abgeschlossen.")
        except Exception as e:
            print(f"FEHLER bei der Backend-Initialisierung: {str(e)}")
            print("Stack-Trace:")
            traceback.print_exc()

    def _connect_serial_signals_to_sensor_model(self):
        """Verbinde SerialConnector-Signale mit SensorViewModel-Methoden"""
        try:
            if not self.serial_connector or not self.sensor_model:
                print("WARNUNG: SerialConnector oder SensorViewModel nicht verfügbar")
                return
                
            print("Verbinde SerialConnector-Signale mit SensorViewModel...")
            
            # Verbinde Attitude-Signal
            self.serial_connector.attitudeUpdated.connect(self._on_attitude_updated)
            print("✓ Attitude-Signal verbunden")
            
            # Verbinde GPS-Signal
            self.serial_connector.gpsUpdated.connect(self._on_gps_updated)
            print("✓ GPS-Signal verbunden")
            
            # Verbinde Battery-Signal
            self.serial_connector.batteryUpdated.connect(self._on_battery_updated)
            print("✓ Battery-Signal verbunden")
            
            # Verbinde Velocity-Signal
            self.serial_connector.velocityUpdated.connect(self._on_velocity_updated)
            print("✓ Velocity-Signal verbunden")
            
            # Verbinde VFR_HUD-Signal
            self.serial_connector.vfrHudUpdated.connect(self._on_vfr_hud_updated)
            print("✓ VFR_HUD-Signal verbunden")
            
            print("SerialConnector-Signale erfolgreich mit SensorViewModel verbunden")
            
        except Exception as e:
            print(f"FEHLER beim Verbinden der SerialConnector-Signale: {str(e)}")
            traceback.print_exc()
    
    def _on_attitude_updated(self, roll, pitch, yaw):
        """Handler für Attitude-Updates"""
        try:
            print(f"Backend: Received attitude update - roll={roll}, pitch={pitch}, yaw={yaw}")
            self.sensor_model.update_sensor_value("roll", roll)
            self.sensor_model.update_sensor_value("pitch", pitch)
            self.sensor_model.update_sensor_value("yaw", yaw)
            # Heading ist normalerweise gleich Yaw für die meisten UAVs
            self.sensor_model.update_sensor_value("heading", yaw)
        except Exception as e:
            print(f"FEHLER beim Verarbeiten von Attitude-Update: {str(e)}")
    
    def _on_gps_updated(self, lat, lon, alt):
        """Handler für GPS-Updates"""
        try:
            print(f"Backend: Received GPS update - lat={lat}, lon={lon}, alt={alt}")
            self.sensor_model.update_sensor_value("gps_latitude", lat)
            self.sensor_model.update_sensor_value("gps_longitude", lon)
            self.sensor_model.update_sensor_value("gps_altitude", alt)
        except Exception as e:
            print(f"FEHLER beim Verarbeiten von GPS-Update: {str(e)}")
    
    def _on_battery_updated(self, voltage, current, remaining):
        """Handler für Battery-Updates"""
        try:
            print(f"Backend: Received battery update - voltage={voltage}, current={current}, remaining={remaining}")
            self.sensor_model.update_sensor_value("battery_voltage", voltage)
            self.sensor_model.update_sensor_value("battery_current", current)
            self.sensor_model.update_sensor_value("battery_percentage", remaining)
        except Exception as e:
            print(f"FEHLER beim Verarbeiten von Battery-Update: {str(e)}")
    
    def _on_velocity_updated(self, groundspeed, airspeed, vertical_speed):
        """Handler für Velocity-Updates"""
        try:
            print(f"Backend: Received velocity update - groundspeed={groundspeed}, airspeed={airspeed}, vertical_speed={vertical_speed}")
            self.sensor_model.update_sensor_value("groundspeed", groundspeed)
            self.sensor_model.update_sensor_value("airspeed", airspeed)
            self.sensor_model.update_sensor_value("vertical_speed", vertical_speed)
        except Exception as e:
            print(f"FEHLER beim Verarbeiten von Velocity-Update: {str(e)}")
    
    def _on_vfr_hud_updated(self, groundspeed, airspeed, heading, throttle):
        """Handler für VFR_HUD-Updates"""
        try:
            print(f"Backend: Received VFR_HUD update - groundspeed={groundspeed}, airspeed={airspeed}, heading={heading}, throttle={throttle}")
            self.sensor_model.update_sensor_value("groundspeed", groundspeed)
            self.sensor_model.update_sensor_value("airspeed", airspeed)
            self.sensor_model.update_sensor_value("heading", heading)
            self.sensor_model.update_sensor_value("throttle", throttle)
        except Exception as e:
            print(f"FEHLER beim Verarbeiten von VFR_HUD-Update: {str(e)}")

def cleanup_resources(backend, engine):
    """
    Saubere Bereinigung aller Ressourcen beim Beenden der Anwendung
    
    Args:
        backend: Backend-Instanz
        engine: QML-Engine
    """
    try:
        print("Starte Cleanup-Prozess...")
        
        # SerialConnector sauber beenden
        if hasattr(backend, 'serial_connector') and backend.serial_connector:
            print("Beende SerialConnector...")
            backend.serial_connector.cleanup()
            
        # QML-Engine sauber beenden
        if engine:
            print("Beende QML-Engine...")
            engine.deleteLater()
            
        # Logger-Nachricht
        if hasattr(backend, 'logger') and backend.logger:
            backend.logger.addLog("[INFO] Application cleanup completed")
            
        print("Cleanup-Prozess abgeschlossen")
        
    except Exception as e:
        print(f"WARNING: Error during cleanup: {e}")
        import traceback
        traceback.print_exc()

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
    
    # Register QML types from modules
    try:
        print("Registriere QML-Typen...")
        qmlRegisterType(FirmwareViewModel, "RZGCS.Backend", 1, 0, "FirmwareViewModel")
        print("QML-Typen erfolgreich registriert")
    except Exception as e:
        print(f"Fehler bei der QML-Typ-Registrierung: {str(e)}")
        print("Stack-Trace:")
        traceback.print_exc()
    
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
    engine.rootContext().setContextProperty("connection_adapter", backend.connection_viewmodel)
    engine.rootContext().setContextProperty("parameterController", backend.parameter_manager)
    engine.rootContext().setContextProperty("licenseController", backend.license_controller)
    
    # Registriere TelemetryViewModel nur wenn es existiert
    if hasattr(backend, 'telemetry_viewmodel') and backend.telemetry_viewmodel is not None:
        engine.rootContext().setContextProperty("telemetryViewModel", backend.telemetry_viewmodel)
        print("TelemetryViewModel erfolgreich im QML-Kontext registriert")
    else:
        print("Warnung: TelemetryViewModel nicht verfügbar, wird nicht im QML-Kontext registriert")
    
    # Registriere FirmwareViewModel für QML
    try:
        print("Initialisiere FirmwareViewModel...")
        firmware_viewmodel = FirmwareViewModel()
        engine.rootContext().setContextProperty("firmwareViewModel", firmware_viewmodel)
        print("FirmwareViewModel erfolgreich registriert")
    except Exception as e:
        print(f"Fehler bei der Initialisierung des FirmwareViewModel: {str(e)}")
        print("Die Anwendung wird ohne Firmware-Funktionen fortgesetzt.")
    
    # FlightPlanningViewModel initialisieren und registrieren
    try:
        print("Initialisiere FlightPlanningViewModel...")
        flight_planning_service = FlightPlanningService()
        flight_planning_viewmodel = FlightPlanningViewModel()
        flight_planning_viewmodel.set_service(flight_planning_service)
        engine.rootContext().setContextProperty("flightPlanningViewModel", flight_planning_viewmodel)
        print("FlightPlanningViewModel erfolgreich registriert")
    except Exception as e:
        print(f"Fehler bei der Initialisierung des FlightPlanningViewModels: {str(e)}")
        print("Die Anwendung wird ohne Flugplanung fortgesetzt.")

    
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
        
        # Initialize flight controller with root object, nur wenn root_objects vorhanden
        if engine.rootObjects():
            root_object = engine.rootObjects()[0]
            flight_map_view = flight_controller.initialize(root_object)
            
            if flight_map_view:
                print("3D-Kartenansicht erfolgreich initialisiert")
            else:
                print("Warnung: 3D-Kartenansicht konnte nicht initialisiert werden")
        else:
            print("Warnung: Keine Root-Objekte vorhanden, 3D-Kartenansicht wird nicht initialisiert")
            flight_map_view = None
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
        
        # Überprüfe zuerst, ob serial_connector existiert
        if backend.serial_connector:
            if calibration_controller.initialize(backend.serial_connector.get_message_handler(), backend.sensor_model):
                print("Kalibrierungsansicht erfolgreich initialisiert")
            else:
                print("Warnung: Kalibrierungsansicht konnte nicht initialisiert werden")
        else:
            print("Warnung: Kein SerialConnector verfügbar, Kalibrierungsansicht wird deaktiviert")
    except Exception as e:
        print(f"Fehler bei der Initialisierung der Kalibrierungsansicht: {str(e)}")
        print("Die Anwendung wird ohne Kalibrierungsfunktion fortgesetzt.")
        
    # Motor-Test-Controller ist vollständig deaktiviert
    print("Motor-Test-Controller ist vollständig deaktiviert.")
    
    # Registriere das Parameter-Model im QML-Kontext
    try:
        engine.rootContext().setContextProperty("parameterModel", backend.parameter_model)
    except Exception as e:
        print(f"Fehler beim Registrieren des ParameterModels: {str(e)}")
        
    # Registriere den Logger im QML-Kontext für Log-Anzeige in der UI
    try:
        print("Registriere Logger im QML-Kontext...")
        engine.rootContext().setContextProperty("logger", backend.logger)
        print("Logger erfolgreich im QML-Kontext registriert")
    except Exception as e:
        print(f"Fehler beim Registrieren des Loggers: {str(e)}")
        
    # Cleanup-Handler für Anwendungsbeendigung
    def on_about_to_quit():
        print("Anwendung wird beendet, starte Cleanup...")
        cleanup_resources(backend, engine)
    
    # Verbinde Cleanup-Handler mit QApplication
    app.aboutToQuit.connect(on_about_to_quit)
        
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
