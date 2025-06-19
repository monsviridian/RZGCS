#!/usr/bin/env python3
"""
Clean MAVSDK Integration with MVVM Architecture

Diese Version bietet eine saubere MAVSDK-Integration mit MVVM-Architektur,
funktionierender COM-Port-Unterstützung, verbesserter Systeminfo-Filterung
und Motor-Animationsunterstützung.
"""

import os
import sys
import time
import asyncio
from pathlib import Path

# PySide6 imports
import PySide6
from PySide6.QtCore import QObject, Signal, Slot, Property, QTimer
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine, QmlElement

# MAVSDK imports
from mavsdk import System

# Sicherstellen, dass Project Root im Python-Pfad ist
project_root = str(Path(__file__).resolve().parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Eigene Module importieren
from backend.logger import Logger
from rzgcs.mvvm.qml_compatibility_adapter import QMLCompatibilityAdapter
from backend.sensorviewmodel import SensorViewModel

# Stil auf Material Design setzen
os.environ["QT_QUICK_CONTROLS_STYLE"] = "Material"

class MAVSDKDroneViewModel(QObject):
    """
    ViewModel für MAVSDK-Integration mit QML
    Enthält die Businesslogik für die Kommunikation mit Drohnen
    """
    # Signale für QML
    portsChanged = Signal(list)
    portChanged = Signal(str)
    connectionStateChanged = Signal(bool)
    attitudeChanged = Signal(dict)
    batteryChanged = Signal(dict)
    gpsChanged = Signal(dict)
    positionChanged = Signal(dict)
    
    def __init__(self, logger, parent=None):
        """Initialisiert das ViewModel"""
        super().__init__(parent)
        
        # Logger
        self._logger = logger
        
        # Drone System
        self._drone = System()
        
        # MAVSDK-Server Prozess
        self._server_process = None
        
        # Eigenschaften
        self._is_connected = False
        self._selected_port = ""
        self._available_ports = []
        self._connection_string = ""
        
        # Regelmäßige Aktualisierung der Port-Liste
        self._refresh_timer = QTimer(self)
        self._refresh_timer.timeout.connect(self.refreshPorts)
        self._refresh_timer.start(5000)  # Alle 5 Sekunden
        
        # Ports initial laden
        self.refreshPorts()
        
    # Properties
    
    def getAvailablePorts(self):
        """Gibt die verfügbaren Ports zurück"""
        return self._available_ports
    
    def setPort(self, port):
        """Setzt den ausgewählten Port"""
        if port != self._selected_port:
            self._selected_port = port
            self.portChanged.emit(port)
    
    def getPort(self):
        """Gibt den aktuell ausgewählten Port zurück"""
        return self._selected_port
    
    def isConnected(self):
        """Gibt zurück, ob eine Verbindung besteht"""
        return self._is_connected
    
    # Slots
    
    @Slot()
    def refreshPorts(self):
        """Aktualisiert die Liste der verfügbaren Ports"""
        try:
            import serial.tools.list_ports
            self._available_ports = [p.device for p in serial.tools.list_ports.comports()]
            self._logger.addLog(f"[INFO] {len(self._available_ports)} COM-Port(s) gefunden")
            self.portsChanged.emit(self._available_ports)
        except Exception as e:
            self._logger.addLog(f"[ERROR] Fehler beim Aktualisieren der Ports: {str(e)}")
    
    @Slot(str)
    def connectToDrone(self, connection_string=""):
        """Verbindet mit der Drohne"""
        # Wenn Port ausgewählt aber kein Verbindungsstring angegeben
        if not connection_string and self._selected_port:
            connection_string = self._selected_port
        
        if not connection_string:
            self._logger.addLog("[ERROR] Kein Verbindungsstring oder Port angegeben")
            return False
        
        # Verbindungsstring verarbeiten
        connection_string = connection_string.strip()
        
        # Format prüfen (COM-Port)
        if connection_string.startswith("COM"):
            # Baudrate extrahieren, falls vorhanden
            baudrate = 57600  # Standard-Baudrate
            port = connection_string
            
            if ":" in connection_string:
                parts = connection_string.split(":", 1)
                port = parts[0]
                try:
                    baudrate = int(parts[1])
                except ValueError:
                    self._logger.addLog(f"[WARNUNG] Ungültige Baudrate: {parts[1]}, verwende Standard: 57600")
            
            # Formatierter Verbindungsstring für MAVSDK
            formatted_conn_string = f"serial:///{port}:{baudrate}"
            self._logger.addLog(f"[INFO] Verbinde mit {formatted_conn_string}")
            
            # Starte zuerst den MAVSDK-Server mit dem gleichen COM-Port und Baudrate
            mavsdk_server_path = os.path.join(os.getcwd(), "mavsdk_server", "windows", "mavsdk-server.exe")
            if not os.path.exists(mavsdk_server_path):
                self._logger.addLog(f"[FEHLER] MAVSDK-Server nicht gefunden an: {mavsdk_server_path}")
                return False
                
            self._logger.addLog(f"[INFO] Starte MAVSDK-Server mit {port} und {baudrate} baud...")
            
            # In separatem Thread verbinden
            import threading
            import subprocess
            
            # MAVSDK-Server-Prozess für globalen Zugriff
            self._server_process = None
            
            def connect_thread():
                try:
                    # MAVSDK-Server starten
                    server_args = [mavsdk_server_path, "-p", "50051", f"-d=serial://{port}:{baudrate}"]
                    self._logger.addLog(f"[INFO] MAVSDK-Server-Befehl: {' '.join(server_args)}")
                    self._server_process = subprocess.Popen(server_args)
                    self._logger.addLog(f"[INFO] MAVSDK-Server gestartet mit PID: {self._server_process.pid}")
                    
                    # Kurz warten, bis der Server gestartet ist
                    time.sleep(2.0)
                    
                    # Asyncio-Loop erstellen
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    # Verbindung zum MAVSDK-Server über UDP herstellen
                    server_connection = "udp://127.0.0.1:50051"
                    self._logger.addLog(f"[INFO] Verbinde mit MAVSDK-Server über: {server_connection}")
                    loop.run_until_complete(self._drone.connect(server_connection))
                    
                    # Auf Verbindung warten
                    start_time = time.time()
                    while not self._drone.is_connected:
                        if time.time() - start_time > 10:
                            self._logger.addLog("[ERROR] Timeout bei Verbindungsaufbau")
                            self._is_connected = False
                            self.connectionStateChanged.emit(False)
                            return
                        loop.run_until_complete(asyncio.sleep(0.5))
                    
                    # Verbindung erfolgreich
                    self._logger.addLog("[INFO] Verbindung erfolgreich hergestellt")
                    self._is_connected = True
                    self.connectionStateChanged.emit(True)
                    self._connection_string = formatted_conn_string
                    
                    # Telemetrie abonnieren
                    self._subscribe_to_telemetry(loop)
                    
                except Exception as e:
                    self._logger.addLog(f"[ERROR] Verbindungsfehler: {str(e)}")
                    self._is_connected = False
                    self.connectionStateChanged.emit(False)
            
            threading.Thread(target=connect_thread, daemon=True).start()
            return True
            
        # UDP/TCP-Format
        elif connection_string.startswith(("udp://", "tcp://")):
            self._logger.addLog(f"[INFO] Verbinde mit {connection_string}")
            
            # In separatem Thread verbinden
            import threading
            def connect_thread():
                try:
                    # Asyncio-Loop erstellen
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    # Verbindung herstellen
                    loop.run_until_complete(self._drone.connect(connection_string))
                    
                    # Auf Verbindung warten
                    start_time = time.time()
                    while not self._drone.is_connected:
                        if time.time() - start_time > 10:
                            self._logger.addLog("[ERROR] Timeout bei Verbindungsaufbau")
                            self._is_connected = False
                            self.connectionStateChanged.emit(False)
                            return
                        loop.run_until_complete(asyncio.sleep(0.5))
                    
                    # Verbindung erfolgreich
                    self._logger.addLog("[INFO] Verbindung erfolgreich hergestellt")
                    self._is_connected = True
                    self.connectionStateChanged.emit(True)
                    self._connection_string = connection_string
                    
                    # Telemetrie abonnieren
                    self._subscribe_to_telemetry(loop)
                    
                except Exception as e:
                    self._logger.addLog(f"[ERROR] Verbindungsfehler: {str(e)}")
                    self._is_connected = False
                    self.connectionStateChanged.emit(False)
            
            threading.Thread(target=connect_thread, daemon=True).start()
            return True
            
        # Andere Formate
        else:
            self._logger.addLog(f"[INFO] Versuche Verbindung mit: {connection_string}")
            
            # In separatem Thread verbinden
            import threading
            def connect_thread():
                try:
                    # Asyncio-Loop erstellen
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    # Verbindung herstellen
                    loop.run_until_complete(self._drone.connect(connection_string))
                    
                    # Auf Verbindung warten
                    start_time = time.time()
                    while not self._drone.is_connected:
                        if time.time() - start_time > 10:
                            self._logger.addLog("[ERROR] Timeout bei Verbindungsaufbau")
                            self._is_connected = False
                            self.connectionStateChanged.emit(False)
                            return
                        loop.run_until_complete(asyncio.sleep(0.5))
                    
                    # Verbindung erfolgreich
                    self._logger.addLog("[INFO] Verbindung erfolgreich hergestellt")
                    self._is_connected = True
                    self.connectionStateChanged.emit(True)
                    self._connection_string = connection_string
                    
                    # Telemetrie abonnieren
                    self._subscribe_to_telemetry(loop)
                    
                except Exception as e:
                    self._logger.addLog(f"[ERROR] Verbindungsfehler: {str(e)}")
                    self._is_connected = False
                    self.connectionStateChanged.emit(False)
            
            threading.Thread(target=connect_thread, daemon=True).start()
            return True
    
    @Slot()
    def disconnect(self):
        """Trennt die Verbindung zur Drohne und beendet den MAVSDK-Server"""
        if not self._is_connected:
            return
        
        self._logger.addLog("[INFO] Trenne Verbindung...")
        
        # In separatem Thread trennen
        import threading
        def disconnect_thread():
            try:
                # Neuen asyncio-Loop erstellen
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # Verbindung trennen (falls möglich)
                try:
                    loop.run_until_complete(asyncio.wait_for(self._drone.core.shutdown(), 3))
                except:
                    pass
                
                # MAVSDK-Server-Prozess beenden, falls vorhanden
                if self._server_process is not None:
                    try:
                        self._logger.addLog(f"[INFO] Beende MAVSDK-Server-Prozess (PID: {self._server_process.pid})")
                        self._server_process.terminate()
                        # Kurz warten und dann ggf. mit kill beenden
                        self._server_process.wait(timeout=2)
                    except Exception as server_error:
                        self._logger.addLog(f"[WARNUNG] Fehler beim Beenden des MAVSDK-Server-Prozesses: {str(server_error)}")
                        try:
                            # Versuche kill als letztes Mittel
                            self._server_process.kill()
                        except:
                            pass
                    finally:
                        self._server_process = None
                
                self._is_connected = False
                self.connectionStateChanged.emit(False)
                self._logger.addLog("[INFO] Verbindung getrennt")
                
            except Exception as e:
                self._logger.addLog(f"[ERROR] Fehler beim Trennen der Verbindung: {str(e)}")
        
        threading.Thread(target=disconnect_thread, daemon=True).start()
    
    def _subscribe_to_telemetry(self, loop):
        """Abonniert Telemetrie-Streams"""
        try:
            # Attitude abonnieren
            loop.run_until_complete(self._drone.telemetry.attitude_euler_angle_subscribe(self._handle_attitude))
            
            # Battery abonnieren
            loop.run_until_complete(self._drone.telemetry.battery_subscribe(self._handle_battery))
            
            # Position abonnieren
            loop.run_until_complete(self._drone.telemetry.position_subscribe(self._handle_position))
            
            # GPS-Info abonnieren
            loop.run_until_complete(self._drone.telemetry.gps_info_subscribe(self._handle_gps))
            
            self._logger.addLog("[INFO] Telemetrie-Streams abonniert")
            
        except Exception as e:
            self._logger.addLog(f"[ERROR] Fehler beim Abonnieren der Telemetrie: {str(e)}")
    
    def _handle_attitude(self, attitude):
        """Verarbeitet Attitude-Updates"""
        # Daten für QML aufbereiten
        data = {
            "roll_deg": attitude.roll_deg,
            "pitch_deg": attitude.pitch_deg,
            "yaw_deg": attitude.yaw_deg
        }
        
        # Signal auslösen
        self.attitudeChanged.emit(data)
    
    def _handle_battery(self, battery):
        """Verarbeitet Battery-Updates"""
        # Daten für QML aufbereiten
        data = {
            "voltage_v": battery.voltage_v,
            "remaining_percent": battery.remaining_percent
        }
        
        # Signal auslösen
        self.batteryChanged.emit(data)
    
    def _handle_position(self, position):
        """Verarbeitet Position-Updates"""
        # Daten für QML aufbereiten
        data = {
            "latitude_deg": position.latitude_deg,
            "longitude_deg": position.longitude_deg,
            "absolute_altitude_m": position.absolute_altitude_m,
            "relative_altitude_m": position.relative_altitude_m
        }
        
        # Signal auslösen
        self.positionChanged.emit(data)
    
    def _handle_gps(self, gps_info):
        """Verarbeitet GPS-Info-Updates"""
        # Daten für QML aufbereiten
        data = {
            "num_satellites": gps_info.num_satellites,
            "fix_type": gps_info.fix_type
        }
        
        # Signal auslösen
        self.gpsChanged.emit(data)
    
    # Property-Definitionen für QML
    availablePorts = Property(list, getAvailablePorts, notify=portsChanged)
    port = Property(str, getPort, setPort, notify=portChanged)
    connected = Property(bool, isConnected, notify=connectionStateChanged)


def main():
    """Hauptfunktion"""
    print(f"Python version: {sys.version}")
    print(f"PySide6 version: {PySide6.__version__}")
    
    # Arbeitsverzeichnis setzen
    os.chdir(str(Path(__file__).resolve().parent.parent))  # Setze auf Project Root
    print(f"Working directory: {os.getcwd()}")
    
    # QML-Pfade festlegen
    qml_content_dir = os.path.join(os.getcwd(), "RZGCSContent")
    os.environ["QML_IMPORT_PATH"] = qml_content_dir
    os.environ["QML2_IMPORT_PATH"] = qml_content_dir
    
    # Material Design Style setzen
    os.environ["QT_QUICK_CONTROLS_STYLE"] = "Material"
    
    # Logger initialisieren
    logger = Logger()
    logger.addLog("[INFO] Starte MAVSDK MVVM Integration")
    
    # ViewModel erstellen
    drone_view_model = MAVSDKDroneViewModel(logger)
    
    # QML-Kompatibilitätsadapter erstellen
    qml_adapter = QMLCompatibilityAdapter(drone_view_model)
    
    # Sensor Model erstellen
    sensor_model = SensorViewModel()
    
    # QML-Engine erstellen
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    
    # Import-Pfade hinzufügen
    engine.addImportPath(qml_content_dir)
    engine.addImportPath(os.getcwd())
    
    # Objekte im QML-Kontext registrieren
    context = engine.rootContext()
    context.setContextProperty("serialConnector", qml_adapter)
    context.setContextProperty("droneViewModel", drone_view_model)
    context.setContextProperty("sensorModel", sensor_model)
    context.setContextProperty("logger", logger)
    
    # QML-Datei laden
    qml_file = os.path.join(qml_content_dir, "App.qml")
    print(f"Loading QML file: {qml_file}")
    engine.load(qml_file)
    
    # Prüfen, ob QML geladen wurde
    if not engine.rootObjects():
        print(f"[ERROR] Failed to load QML file: {qml_file}")
        return 1
    
    # Log-Nachricht
    logger.addLog("[INFO] MAVSDK MVVM Integration gestartet")
    
    # Anwendung starten
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
