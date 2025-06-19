#!/usr/bin/env python3
"""
Minimal MAVSDK MVVM Implementation
Fokus auf wesentliche Komponenten mit vereinfachter UI-Integration
"""

import asyncio
import sys
import os
import subprocess
import time
import re
import types
import threading
from pathlib import Path

# Set QML style BEFORE importing PySide6
os.environ["QT_QUICK_CONTROLS_STYLE"] = "Material"
os.environ["QT_QUICK_CONTROLS_MATERIAL_THEME"] = "Dark"

from mavsdk import System
from PySide6.QtCore import QObject, Signal, Slot, Property, QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine, qmlRegisterType

# Standardkonfiguration
DEFAULT_COM_PORT = "COM8"
DEFAULT_BAUDRATE = 115200
MAVSDK_SERVER_PATH = os.path.join(os.path.dirname(os.getcwd()), "mavsdk_server", "windows", "mavsdk-server.exe")
SERVER_PORT = 50051

# Logger-Klasse für Protokollierung
class Logger(QObject):
    logUpdated = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.filter_system_info = True
        print(f"Logger initialized with system info filter")
        
    def addLog(self, message):
        # Zeitstempel hinzufügen
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        
        # Log ausgeben und Signal emittieren
        print(log_entry)
        self.logUpdated.emit(log_entry)

# MVVM ViewModel für die MAVSDK-Integration
class MAVSDKDroneViewModel(QObject):
    # QML-kompatible Signale für Aktualisierungen
    connectionStateChanged = Signal(bool)
    positionChanged = Signal(object)
    batteryChanged = Signal(object)
    gpsInfoChanged = Signal(object)
    healthChanged = Signal(object)
    fcImportantMessageReceived = Signal(str)  # Signal für FC wichtige Meldungen
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._logger = Logger()
        self._drone = None
        self._is_connected = False
        self._server_process = None
        self._position = {}
        self._battery = {}
        self._gps_info = {}
        self._health = {}
        
        self._logger.addLog("[INFO] MAVSDK-ViewModel initialisiert")
        
    def _check_connection(self, loop=None):
        """Prüft, ob eine Verbindung zur Drohne besteht"""
        try:
            if not loop:
                loop = asyncio.get_event_loop()
                
            async def check_connection_async():
                # Einfacherer Ansatz: Version oder Identification abfragen
                try:
                    await self._drone.core.get_identification()
                    return True
                except:
                    try:
                        await self._drone.info.get_version()
                        return True
                    except:
                        return False
            
            connection_task = asyncio.ensure_future(check_connection_async())
            try:
                state = asyncio.wait_for(connection_task, timeout=1.0)
                return state.is_connected
            except Exception:
                pass
                
            return False
        except Exception:
            return False
        
    def _clean_up_server(self):
        """Beendet den MAVSDK-Server-Prozess"""
        if hasattr(self, '_server_process') and self._server_process:
            try:
                self._logger.addLog("[INFO] Beende MAVSDK-Server-Prozess...")
                self._server_process.terminate()
                try:
                    self._server_process.wait(timeout=3)
                    self._logger.addLog("[INFO] MAVSDK-Server erfolgreich beendet")
                except:
                    pass
            except Exception as e:
                self._logger.addLog(f"[WARNUNG] Fehler beim Beenden des MAVSDK-Servers: {str(e)}")
                try:
                    self._logger.addLog("[INFO] Erzwinge Beendigung des MAVSDK-Servers")
                    self._server_process.kill()
                except:
                    pass
            finally:
                self._server_process = None

    def connect(self, connection_string=""):
        """Verbindet mit der Drohne - universelle Methode für verschiedene Verbindungsformate"""
        # Prüfung auf leere Verbindungszeichenfolge
        if not connection_string:
            self._logger.addLog("[WARNUNG] Keine Verbindungszeichenfolge angegeben")
            return False
            
        # Prüfen, ob bereits verbunden
        if self._is_connected:
            self._logger.addLog("[INFO] Bereits verbunden. Trenne Verbindung zuerst...")
            self.disconnectDrone()
        
        # Intelligente Analyse des Verbindungs-Strings
        # Fall 1: COM-Port ohne Baudrate (z.B. "COM8")
        if re.match(r"^COM[0-9]+$", connection_string, re.IGNORECASE):
            port = connection_string
            baud = DEFAULT_BAUDRATE
            self._logger.addLog(f"[INFO] Verbinde seriell mit {port} bei Standard-Baudrate {baud}")
        
        # Fall 2: COM-Port mit Baudrate (z.B. "COM8:115200")
        elif re.match(r"^COM[0-9]+:[0-9]+$", connection_string, re.IGNORECASE):
            parts = connection_string.split(":")
            port = parts[0]
            baud = int(parts[1])
            self._logger.addLog(f"[INFO] Verbinde seriell mit {port} bei {baud} Baud")
        
        # Fall 3: Vollständige URL (z.B. "serial://COM8:115200")
        else:
            self._logger.addLog(f"[INFO] Verwende direkte Verbindungs-URL: {connection_string}")
            return self._connect_custom_url(connection_string)
        
        # Standard-Verbindung mit COM-Port und Baudrate
        return self._connect_serial(port, baud)
    
    def _connect_serial(self, port, baud=DEFAULT_BAUDRATE):
        """Verbindet mit einem seriellen Port"""
        self._logger.addLog(f"[INFO] Verbinde seriell mit {port} bei {baud} Baud")
        
        # Formatiere die URL korrekt für den MAVSDK-Server
        # WICHTIG: Das korrekte Format ist serial://COM8:115200 (ohne dritten Slash)
        mavsdk_url = f"serial://{port}:{baud}"
        
        self._logger.addLog(f"[DEBUG] Starte MAVSDK-Server mit URL: {mavsdk_url}")
        
        # MAVSDK-Server starten
        server_args = [
            MAVSDK_SERVER_PATH,
            "-p", str(SERVER_PORT),
            mavsdk_url
        ]
        
        try:
            # Server im Hintergrund starten
            self._server_process = subprocess.Popen(server_args)
            self._logger.addLog(f"[INFO] MAVSDK-Server gestartet (PID: {self._server_process.pid})")
            
            # Kurz warten, bis der Server initiiert ist
            import time
            time.sleep(2)
            
            # Thread starten
            import threading
            self._connect_thread = threading.Thread(target=self._connect_thread_func, args=(SERVER_PORT,), daemon=True)
            self._connect_thread.start()
            
            return True
            
        except Exception as e:
            self._logger.addLog(f"[FEHLER] Fehler beim Starten des MAVSDK-Servers: {str(e)}")
            return False
    
    def _connect_custom_url(self, url):
        """Verbindet mit einer benutzerdefinierten URL"""
        self._logger.addLog(f"[INFO] Verbinde mit benutzerdefinierter URL: {url}")
        # Implementation für benutzerdefinierte URLs hier...
        return False  # Noch nicht implementiert
    
    def _connect_thread_func(self, server_port):
        """Thread-Funktion für asynchrone Verbindungsherstellung"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Verbindung zum MAVSDK-Server herstellen
            self._drone = System(mavsdk_server_address="localhost", port=server_port)
            loop.run_until_complete(self._drone.connect())
            
            # Auf Verbindung warten
            connected = False
            try:
                timeout_sec = 15
                start_time = time.time()
                
                while time.time() - start_time < timeout_sec:
                    # Prüfen, ob Verbindung besteht
                    try:
                        connection_task = asyncio.ensure_future(self._check_connection_async())
                        if loop.run_until_complete(asyncio.wait_for(connection_task, timeout=1.0)):
                            connected = True
                            break
                    except:
                        pass
                    time.sleep(1)
                
                if connected:
                    self._logger.addLog("[INFO] Verbindung zur Drohne hergestellt")
                    self._is_connected = True
                    self.connectionStateChanged.emit(True)
                    
                    # Telemetrie-Tasks starten
                    try:
                        loop.run_until_complete(self._start_telemetry(loop))
                    except Exception as e:
                        self._logger.addLog(f"[WARNUNG] Telemetrie-Start fehlgeschlagen: {str(e)}")
                else:
                    self._logger.addLog("[FEHLER] Timeout bei Verbindungsherstellung")
                    self._clean_up_server()
            except Exception as e:
                self._logger.addLog(f"[FEHLER] Fehler bei Verbindungsherstellung: {str(e)}")
                self._clean_up_server()
        except Exception as e:
            self._logger.addLog(f"[FEHLER] Thread-Fehler: {str(e)}")
            self._clean_up_server()
    
    async def _check_connection_async(self):
        """Prüft asynchron, ob eine Verbindung besteht"""
        try:
            # Versuche zuerst get_identification
            try:
                await self._drone.core.get_identification()
                return True
            except:
                pass
                
            # Falls das fehlschlägt, versuche get_version
            try:
                await self._drone.info.get_version()
                return True
            except:
                pass
                
            return False
        except:
            return False
    
    async def _start_telemetry(self, loop):
        """Startet alle Telemetrie-Streams"""
        # Position
        pos_task = asyncio.ensure_future(self._monitor_position())
        # Battery
        bat_task = asyncio.ensure_future(self._monitor_battery())
        # GPS Info
        gps_task = asyncio.ensure_future(self._monitor_gps_info())
        # Health
        health_task = asyncio.ensure_future(self._monitor_health())
        # Status-Text-Überwachung
        status_task = asyncio.ensure_future(self._monitor_status_text())
        
        # Alle Tasks zusammenfassen
        await asyncio.gather(pos_task, bat_task, gps_task, health_task, status_task)
    
    async def _monitor_position(self):
        """Monitor für Positionsdaten"""
        try:
            async for position in self._drone.telemetry.position():
                self._position = {
                    'latitude_deg': position.latitude_deg,
                    'longitude_deg': position.longitude_deg,
                    'absolute_altitude_m': position.absolute_altitude_m,
                    'relative_altitude_m': position.relative_altitude_m
                }
                self.positionChanged.emit(self._position)
        except Exception as e:
            self._logger.addLog(f"[FEHLER] Position-Monitor: {str(e)}")
    
    async def _monitor_battery(self):
        """Monitor für Batteriedaten"""
        try:
            async for battery in self._drone.telemetry.battery():
                self._battery = {
                    'voltage_v': battery.voltage_v,
                    'remaining_percent': battery.remaining_percent
                }
                self.batteryChanged.emit(self._battery)
        except Exception as e:
            self._logger.addLog(f"[FEHLER] Battery-Monitor: {str(e)}")
    
    async def _monitor_gps_info(self):
        """Monitor für GPS-Informationen"""
        try:
            async for gps_info in self._drone.telemetry.gps_info():
                self._gps_info = {
                    'num_satellites': gps_info.num_satellites,
                    'fix_type': gps_info.fix_type
                }
                self.gpsInfoChanged.emit(self._gps_info)
        except Exception as e:
            self._logger.addLog(f"[FEHLER] GPS-Monitor: {str(e)}")
    
    async def _monitor_health(self):
        """Monitor für Gesundheitsinformationen"""
        try:
            async for health in self._drone.telemetry.health():
                self._health = {
                    'is_gyrometer_calibration_ok': health.is_gyrometer_calibration_ok,
                    'is_accelerometer_calibration_ok': health.is_accelerometer_calibration_ok,
                    'is_magnetometer_calibration_ok': health.is_magnetometer_calibration_ok,
                    'is_local_position_ok': health.is_local_position_ok,
                    'is_global_position_ok': health.is_global_position_ok,
                    'is_home_position_ok': health.is_home_position_ok
                }
                self.healthChanged.emit(self._health)
        except Exception as e:
            self._logger.addLog(f"[FEHLER] Health-Monitor: {str(e)}")
    
    async def _monitor_status_text(self):
        """Monitor für Status-Text-Nachrichten"""
        try:
            async for status_text in self._drone.telemetry.status_text():
                # Prefix je nach Meldungstyp
                prefix = "[INFO]"
                if status_text.type.name == "WARNING":
                    prefix = "[WARNUNG]"
                elif status_text.type.name == "CRITICAL":
                    prefix = "[KRITISCH]"
                elif status_text.type.name == "ERROR":
                    prefix = "[FEHLER]"
                
                # Meldung protokollieren
                message = f"[FC] {prefix} {status_text.text}"
                self._logger.addLog(message)
                
                # Wichtige FC-Nachrichten an UI weiterleiten
                self.fcImportantMessageReceived.emit(status_text.text)
        except Exception as e:
            self._logger.addLog(f"[FEHLER] Status-Text-Monitor: {str(e)}")
    
    @Slot()
    def disconnectDrone(self):
        """Trennt die Verbindung zur Drohne und beendet den MAVSDK-Server"""
        if not self._is_connected:
            return True
            
        self._logger.addLog("[INFO] Trenne Verbindung zur Drohne")
        
        # MAVSDK-Server beenden
        self._clean_up_server()
        
        # Verbindungsstatus aktualisieren
        self._is_connected = False
        self.connectionStateChanged.emit(False)
        
        return True
    
    @Slot(result=bool)
    def isConnected(self):
        """Gibt zurück, ob eine Verbindung besteht"""
        return self._is_connected
    
    # Eigenschaften für QML
    @Property(bool, notify=connectionStateChanged)
    def connected(self):
        """Alias-Property für QML"""
        return self._is_connected

# Funktion für die QML-Integration    
def setup_qml_integration(drone_view_model):
    """Richtet die QML-Integration ein"""
    engine = QQmlApplicationEngine()
    
    # QML-Engine konfigurieren
    # MVVM-Model als Context-Property registrieren
    engine.rootContext().setContextProperty("serialConnector", drone_view_model)
    engine.rootContext().setContextProperty("droneModel", drone_view_model)
    
    # Logger als Context-Property registrieren
    engine.rootContext().setContextProperty("logger", drone_view_model._logger)
    
    return engine

# Minimal-Beispiel, wie die MVVM-Integration verwendet wird
def main():
    app = QGuiApplication(sys.argv)
    
    # MVVM-ViewModel erstellen
    drone_view_model = MAVSDKDroneViewModel()
    
    # Anstatt die connect-Methode umzubenennen, stellen wir sicher, dass beide Namen verfügbar sind
    if hasattr(drone_view_model, 'connect') and not hasattr(drone_view_model, 'connectToDrone'):
        # Beide Methoden verfügbar machen
        setattr(drone_view_model.__class__, 'connectToDrone', drone_view_model.connect)
        print("[INFO] Added connectToDrone method as alias for connect to support both naming conventions")
        
    # QML-Integration einrichten
    engine = setup_qml_integration(drone_view_model)
    
    # Zuerst versuchen, die Haupt-QML-Datei zu laden
    qml_file = os.path.join(os.path.dirname(os.getcwd()), "RZGCSContent", "App.qml")
    minimal_qml = os.path.join(os.getcwd(), "minimal_test.qml")
    
    if os.path.exists(qml_file) and False:  # Deaktiviert, um immer die minimale UI zu verwenden
        print(f"Loading QML file: {qml_file}")
        engine.load(QUrl.fromLocalFile(qml_file))
    elif os.path.exists(minimal_qml):
        # Minimale Test-UI laden
        print(f"Loading minimal test UI: {minimal_qml}")
        drone_view_model._logger.addLog("[INFO] Starte minimale MAVSDK-Testumgebung")
        engine.load(QUrl.fromLocalFile(minimal_qml))
    else:
        # Falls keine QML-Datei gefunden wurde
        drone_view_model._logger.addLog("[WARNUNG] Keine QML-Datei gefunden!")
        print("[ERROR] Keine QML-Datei gefunden. Erstelle minimal_test.qml im aktuellen Verzeichnis.")
    
    return app.exec()

# Wenn direkt ausgeführt, starten
if __name__ == "__main__":
    # Python-Version ausgeben
    print(f"Python version: {sys.version}")
    
    # PySide6-Version ausgeben
    from PySide6 import __version__ as PySide6_VERSION
    print(f"PySide6 version: {PySide6_VERSION}")
    
    # Arbeitsverzeichnis ausgeben
    print(f"Working directory: {os.getcwd()}")
    
    # MVVM-Integration starten
    sys.exit(main())
