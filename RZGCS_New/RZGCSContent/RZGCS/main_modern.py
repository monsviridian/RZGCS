import sys
import os
from pathlib import Path
from PySide6.QtCore import QObject, Slot, QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication
import traceback

# Python-Backend-Pfad hinzufügen, falls nötig
python_path = Path(__file__).parent.parent.parent / "Python"
if str(python_path) not in sys.path:
    print(f"Füge Python-Backend-Pfad hinzu: {python_path}")
    sys.path.append(str(python_path))

# Import von BackendBridge aus dem lokalen Modul
from backend_bridge import BackendBridge

# Zusätzliche Imports für die erweiterte Integration
try:
    # Probiere die Backend-Komponenten zu importieren
    from backend.logger import Logger
    from backend.serial_connector import SerialConnector
    from backend.motor_test_controller import MotorTestController
    from backend.mavlink_connector import MAVLinkConnector
    from backend.connection.viewmodels.connection_adapter import ConnectionAdapter, ConnectionStatus
    from backend.flight_view_controller import FlightViewController
    
    FULL_BACKEND_AVAILABLE = True
    print("Backend-Komponenten erfolgreich importiert.")
except ImportError as e:
    print(f"Warnung: Backend-Komponenten konnten nicht importiert werden. {str(e)}")
    print("Die Anwendung wird im eingeschränkten Modus gestartet.")
    FULL_BACKEND_AVAILABLE = False

# Moderne, vereinfachte Version des Backends für die moderne UI
class ModernBackend(QObject):
    def __init__(self):
        super().__init__()
        try:
            # Logger initialisieren
            self.logger = Logger() if FULL_BACKEND_AVAILABLE else None
            print("Logger initialisiert.")
            
            # BackendBridge initialisieren, die eine Vereinfachung des vollen Backends darstellt
            self.bridge = BackendBridge()
            print("BackendBridge initialisiert.")
            
            # Wenn das volle Backend verfügbar ist, initialisieren wir auch den ConnectionAdapter
            if FULL_BACKEND_AVAILABLE:
                print("Initialisiere erweiterte Backend-Komponenten...")
                
                # Initialisiere SerialConnector für Verbindungsmanagement
                if hasattr(self.bridge, 'mavlink_controller') and self.bridge.mavlink_controller:
                    # Verwende den bestehenden MAVLink-Controller aus der Bridge
                    self.serial_connector = self.bridge.mavlink_controller
                    print("Verwende MAVLink-Controller aus BackendBridge")
                else:
                    # Erstelle einen neuen SerialConnector, falls nicht vorhanden
                    self.serial_connector = SerialConnector(None, self.logger, None)
                    print("Neuer SerialConnector erstellt")
                
                # Initialisiere ConnectionAdapter mit dem SerialConnector
                self.connection_adapter = ConnectionAdapter(self.serial_connector)
                print("ConnectionAdapter initialisiert.")
                
                # Stelle sicher, dass die Baudrate auf 115200 gesetzt ist (gemäß Memory)
                if hasattr(self.serial_connector, 'setBaudRate'):
                    self.serial_connector.setBaudRate(115200)
                    print("Baudrate auf 115200 gesetzt.")
                
                # Initialisiere Motor-Test-Controller für Motorsteuerung (optional)
                try:
                    self.motor_test_controller = MotorTestController(self.logger)
                    
                    # Verbinde mit dem MessageHandler vom SerialConnector
                    if self.serial_connector and hasattr(self.serial_connector, 'get_message_handler'):
                        message_handler = self.serial_connector.get_message_handler()
                        if message_handler:
                            self.motor_test_controller.set_message_handler(message_handler)
                            print("MotorTestController mit MessageHandler verbunden.")
                    
                    # Verbinde das Status-Signal mit dem MotorTestController
                    try:
                        # Versuch 1: Direct Connection mit QtCore SIGNAL/SLOT
                        from PySide6.QtCore import QObject, SIGNAL, SLOT
                        QObject.connect(
                            self.connection_adapter,
                            SIGNAL("connected_changed(bool)"),
                            self.motor_test_controller,
                            SLOT("set_connected(bool)")
                        )
                        print("Signal per DirectConnection verbunden.")
                    except Exception as e1:
                        print(f"DirectConnection fehlgeschlagen: {str(e1)}")
                        
                        # Versuch 2: Direkte Verbindung über connected_changed-Signal
                        try:
                            if hasattr(self.connection_adapter, 'connected_changed'):
                                self.connection_adapter.connected_changed.connect(
                                    self.motor_test_controller.set_connected
                                )
                                print("connected_changed-Signal mit MotorTestController verbunden.")
                            # Versuch 3: status_changed mit Lambda-Konverter
                            elif hasattr(self.connection_adapter, 'status_changed'):
                                self.connection_adapter.status_changed.connect(
                                    lambda status: self.motor_test_controller.set_connected(status == 1)
                                )
                                print("status_changed-Signal mit Lambda-Konverter verbunden.")
                            else:
                                print("Warnung: Keines der benötigten Signale gefunden.")
                        except Exception as e2:
                            print(f"Fehler beim Verbinden des Signals: {str(e2)}")
                    
                    print("MotorTestController initialisiert.")
                except Exception as e:
                    print(f"MotorTestController konnte nicht initialisiert werden: {str(e)}")
                    self.motor_test_controller = None
            else:
                # Wenn kein volles Backend verfügbar ist, verwenden wir nur die BackendBridge
                self.serial_connector = None
                self.connection_adapter = None
                self.motor_test_controller = None
                
            print("ModernBackend erfolgreich initialisiert.")
        except Exception as e:
            print(f"FEHLER bei der Backend-Initialisierung: {str(e)}")
            traceback.print_exc()

    def _setup_bridge_signals(self):
        """Stellt sicher, dass die BackendBridge die erwarteten Signale hat"""
        # Diese Methode stellt sicher, dass die BackendBridge die von der App.qml
        # erwarteten Signale implementiert, auch wenn sie nicht verwendet werden
        from PySide6.QtCore import Signal, Slot
        
        # Stelle sicher, dass die Bridge die Basisklasse QObject hat
        if not hasattr(self.bridge, 'stateChanged'):
            setattr(self.bridge.__class__, 'stateChanged', Signal(object))
            
        if not hasattr(self.bridge, 'modeChanged'):
            setattr(self.bridge.__class__, 'modeChanged', Signal(str))
            
        if not hasattr(self.bridge, 'errorOccurred'):
            setattr(self.bridge.__class__, 'errorOccurred', Signal(str))
            
        if not hasattr(self.bridge, 'missionStarted'):
            setattr(self.bridge.__class__, 'missionStarted', Signal(object))
            
        if not hasattr(self.bridge, 'missionCompleted'):
            setattr(self.bridge.__class__, 'missionCompleted', Signal(object))

def main():
    # QApplication für Widget-Support
    app = QApplication(sys.argv)
    
    # Debug-Informationen zur Python-Version
    print(f"Python-Version: {sys.version}")
    
    # Create modern backend
    backend = ModernBackend()
    
    # Create QML engine
    engine = QQmlApplicationEngine()
    
    # QML-Importpfade EXAKT wie in der original main.py setzen 
    qml_dir = Path(__file__).parent.parent.parent  # Zu Root-Verzeichnis navigieren
    rzgcs_import_path = str(qml_dir / "RZGCSContent")
    print(f"QML-Import-Pfad: {rzgcs_import_path}")
    engine.addImportPath(rzgcs_import_path)
    
    # Zusätzliche Import-Pfade für Components und Connection Module
    components_path = str(qml_dir / "RZGCSContent" / "Components")
    connection_path = str(qml_dir / "RZGCSContent" / "Connection")
    print(f"Components-Import-Pfad: {components_path}")
    print(f"Connection-Import-Pfad: {connection_path}")
    engine.addImportPath(components_path)
    engine.addImportPath(connection_path)
    
    # Die wichtigste QML-Kontexteigenschaft: 'backend'
    # Merke: Die App.qml erwartet eine Kontextproperty 'backend'
    engine.rootContext().setContextProperty("backend", backend.bridge)
    
    # Logger bereitstellen
    if hasattr(backend, 'logger') and backend.logger is not None:
        engine.rootContext().setContextProperty("logger", backend.logger)
    
    # Registriere erweiterte Backend-Komponenten im QML-Kontext, wenn vorhanden
    if hasattr(backend, 'has_full_backend') and backend.has_full_backend:
        # SerialConnector als serialConnector bereitstellen
        if hasattr(backend, 'serial_connector') and backend.serial_connector is not None:
            engine.rootContext().setContextProperty("serialConnector", backend.serial_connector)

        # ConnectionAdapter als connectionViewModel bereitstellen
        if hasattr(backend, 'connection_adapter') and backend.connection_adapter is not None:
            engine.rootContext().setContextProperty("connectionViewModel", backend.connection_adapter)
            
        # SensorViewModel als sensorModel bereitstellen, wenn vorhanden
        if hasattr(backend, 'sensor_model') and backend.sensor_model is not None:
            engine.rootContext().setContextProperty("sensorModel", backend.sensor_model)

        # MotorTestController als motorTestController bereitstellen
        if hasattr(backend, 'motor_test_controller') and backend.motor_test_controller is not None:
            engine.rootContext().setContextProperty("motorTestController", backend.motor_test_controller)
            print("MotorTestController im QML-Kontext registriert")
    
    # Lade die vollständige App.qml aus dem RZGCSContent-Verzeichnis
    qml_file = Path(__file__).parent.parent.parent / "RZGCSContent" / "App.qml"
    qml_file_path = str(qml_file)
    print(f"Lade QML-Datei: {qml_file_path}")
    if not qml_file.exists():
        print(f"FEHLER: QML-Datei nicht gefunden: {qml_file_path}")
        sys.exit(-1)
    
    # QML-Datei laden
    engine.load(QUrl.fromLocalFile(qml_file_path))
    
    # Überprüfe, ob die Datei erfolgreich geladen wurde
    if not engine.rootObjects():
        print(f"FEHLER: Keine Root-Objekte nach dem Laden von {qml_file_path}")
        sys.exit(-1)
    else:
        print("QML-Datei erfolgreich geladen.")
    
    # Wenn das vollständige Backend verfügbar ist, initialisiere zusätzliche Controller
    if FULL_BACKEND_AVAILABLE:
        # Versuche, den FlightViewController zu initialisieren
        try:
            print("Initialisiere FlightViewController...")
            flight_view_controller = FlightViewController(parent=None, logger=backend.logger)
            
            # Registriere den FlightViewController im QML-Kontext
            engine.rootContext().setContextProperty("flightViewController", flight_view_controller)
            
            # Verbinde MessageHandler, falls vorhanden
            if backend.serial_connector and hasattr(backend.serial_connector, 'get_message_handler'):
                message_handler = backend.serial_connector.get_message_handler()
                if message_handler:
                    flight_view_controller.set_message_handler(message_handler)
            
            # Initialisiere mit Root-Objekt
            if engine.rootObjects():
                root_object = engine.rootObjects()[0]
                if flight_view_controller.initialize(root_object):
                    print("FlightViewController erfolgreich initialisiert.")
                else:
                    print("Warnung: FlightViewController konnte nicht initialisiert werden.")
        except Exception as e:
            print(f"Fehler bei der Initialisierung des FlightViewController: {str(e)}")
            print("Die Anwendung wird ohne 3D-Karte fortgesetzt.")
    
    print("Anwendung gestartet. Starte Event-Loop...")
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 