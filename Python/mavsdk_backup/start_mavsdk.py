#!/usr/bin/env python3
"""
Direkte Startdatei für RZGCS mit MAVSDK-Integration
Vereinfachte Version ohne Paketimports
"""

import os
import sys
import time
import asyncio
from pathlib import Path
from PySide6.QtCore import QUrl, QObject, Signal, Slot, Property, QTimer
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

# Versuche MAVSDK zu importieren
try:
    import mavsdk
    from mavsdk import System
    from mavsdk.telemetry import Position, Quaternion, AngularVelocityBody
    from mavsdk.param import Parameter
    MAVSDK_AVAILABLE = True
except ImportError:
    print("WARNUNG: MAVSDK ist nicht installiert. Verwende simulierte Daten.")
    MAVSDK_AVAILABLE = False


# Einfacher Logger
class Logger(QObject):
    logAdded = Signal(str)
    
    def __init__(self):
        super().__init__()
        self._logs = []
    
    def addLog(self, message):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        self._logs.append(formatted_message)
        self.logAdded.emit(formatted_message)
        print(formatted_message)
    
    def getLogs(self, count=None):
        if count is None:
            return self._logs
        return self._logs[-count:]


# Einfaches SensorViewModel
class SensorViewModel(QObject):
    sensorUpdated = Signal(str, object, str)
    
    def __init__(self):
        super().__init__()
        self._sensors = {}
    
    @Slot(str, object, str)
    def updateSensor(self, name, value, unit):
        self._sensors[name] = {"value": value, "unit": unit}
        self.sensorUpdated.emit(name, value, unit)
    
    @Slot(str, result="QVariant")
    def getSensor(self, name):
        return self._sensors.get(name, {"value": "N/A", "unit": ""})


# MAVSDK-Controller
class DroneController(QObject):
    connectionChanged = Signal(bool)
    armingChanged = Signal(bool)
    flightModeChanged = Signal(str)
    
    def __init__(self, logger, sensor_viewmodel):
        super().__init__()
        self._logger = logger
        self._sensor_viewmodel = sensor_viewmodel
        self._is_connected = False
        self._is_armed = False
        self._flight_mode = "UNKNOWN"
        self._drone = None
        self._update_timer = QTimer()
        self._update_timer.timeout.connect(self._update_sensor_data)
        
        # Asynchrones Event-Loop für MAVSDK
        self._loop = asyncio.new_event_loop()
        
    def _create_drone(self):
        if MAVSDK_AVAILABLE:
            return System()
        else:
            # Dummy-Objekt, wenn MAVSDK nicht verfügbar ist
            self._logger.addLog("⚠️ MAVSDK nicht verfügbar, verwende Simulation")
            return None
    
    @Slot(str)
    def connect(self, connection_string):
        self._logger.addLog(f"Verbindung zu {connection_string} wird hergestellt...")
        
        if MAVSDK_AVAILABLE:
            # Echte MAVSDK-Verbindung
            self._drone = self._create_drone()
            
            # Verbindungsstring analysieren
            if connection_string.startswith("udp://"):
                # UDP-Verbindung (z.B. SITL-Simulator)
                connection_string = connection_string.replace("udp://", "")
                if ":" in connection_string:
                    host, port = connection_string.split(":")
                    if not host:
                        host = "localhost"
                    port = int(port)
                else:
                    host = "localhost"
                    port = 14550
                    
                # Verbindung asynchron starten
                asyncio.run_coroutine_threadsafe(self._connect_udp(host, port), self._loop)
            else:
                # Serielle Verbindung oder andere
                self._logger.addLog(f"Verbindungstyp nicht unterstützt: {connection_string}")
                self._is_connected = False
                self.connectionChanged.emit(False)
                return False
                
            # Timer für Sensorupdates starten
            self._update_timer.start(200)  # 5 Hz Update-Rate
        else:
            # Simulierte Verbindung
            self._is_connected = True
            self.connectionChanged.emit(True)
            self._logger.addLog("Verbindung hergestellt (Simulation)")
            
            # Simulierte Sensordaten
            self._update_timer.start(1000)  # 1 Hz Update-Rate für Simulation
            
        return True
    
    async def _connect_udp(self, host, port):
        # Verbindung zum Drone herstellen
        connection_str = f"udp://{host}:{port}"
        self._logger.addLog(f"Verbinde mit MAVSDK Server: {connection_str}")
        
        try:
            await self._drone.connect(system_address=connection_str)
            self._logger.addLog("Verbindung zu MAVSDK Server hergestellt")
            
            # Telemetrie-Callbacks einrichten
            self._drone.telemetry.armed.subscribe(self._on_armed_status_update)
            self._drone.telemetry.flight_mode.subscribe(self._on_flight_mode_update)
            
            self._is_connected = True
            self.connectionChanged.emit(True)
            
        except Exception as e:
            self._logger.addLog(f"❌ Fehler bei der Verbindung: {str(e)}")
            self._is_connected = False
            self.connectionChanged.emit(False)
    
    def _on_armed_status_update(self, armed_status):
        self._is_armed = armed_status
        self.armingChanged.emit(armed_status)
        self._logger.addLog(f"Arming Status: {'ARMED' if armed_status else 'DISARMED'}")
    
    def _on_flight_mode_update(self, flight_mode):
        mode_str = str(flight_mode)
        self._flight_mode = mode_str
        self.flightModeChanged.emit(mode_str)
        self._logger.addLog(f"Flugmodus: {mode_str}")
    
    def _update_sensor_data(self):
        """Update Sensordaten regelmäßig"""
        if not self._is_connected:
            return
            
        if MAVSDK_AVAILABLE and self._drone:
            # Echte Daten via MAVSDK asynchron holen
            asyncio.run_coroutine_threadsafe(self._fetch_telemetry_data(), self._loop)
        else:
            # Simulierte Daten erzeugen
            import random
            roll = random.uniform(-10, 10)
            pitch = random.uniform(-10, 10)
            yaw = random.uniform(0, 359)
            altitude = random.uniform(50, 150)
            battery = random.uniform(70, 95)
            gps_fix = random.choice(["2D", "3D", "RTK"])
            satellites = random.randint(8, 15)
            
            # Sensordaten aktualisieren
            self._sensor_viewmodel.updateSensor("Roll", f"{roll:.1f}", "°")
            self._sensor_viewmodel.updateSensor("Pitch", f"{pitch:.1f}", "°")
            self._sensor_viewmodel.updateSensor("Yaw", f"{yaw:.1f}", "°")
            self._sensor_viewmodel.updateSensor("Altitude", f"{altitude:.1f}", "m")
            self._sensor_viewmodel.updateSensor("Battery %", f"{battery:.0f}%", "")
            self._sensor_viewmodel.updateSensor("GPS Fix", gps_fix, "")
            self._sensor_viewmodel.updateSensor("GPS Satellites", str(satellites), "")
            self._sensor_viewmodel.updateSensor("System CPU", f"{random.uniform(10, 40):.1f}%", "")
    
    async def _fetch_telemetry_data(self):
        """Holt Telemetriedaten von MAVSDK"""
        try:
            # Position
            position = await self._drone.telemetry.position().__anext__()
            self._sensor_viewmodel.updateSensor("Altitude", f"{position.relative_altitude_m:.1f}", "m")
            self._sensor_viewmodel.updateSensor("GPS Pos", f"{position.latitude_deg:.6f}, {position.longitude_deg:.6f}", "°")
            
            # Ausrichtung
            attitude_euler = await self._drone.telemetry.attitude_euler().__anext__()
            self._sensor_viewmodel.updateSensor("Roll", f"{attitude_euler.roll_deg:.1f}", "°")
            self._sensor_viewmodel.updateSensor("Pitch", f"{attitude_euler.pitch_deg:.1f}", "°")
            self._sensor_viewmodel.updateSensor("Yaw", f"{attitude_euler.yaw_deg:.1f}", "°")
            
            # Batterie
            battery = await self._drone.telemetry.battery().__anext__()
            self._sensor_viewmodel.updateSensor("Battery", f"{battery.voltage_v:.1f}", "V")
            self._sensor_viewmodel.updateSensor("Battery %", f"{battery.remaining_percent:.0f}%", "")
            
            # GPS
            gps_info = await self._drone.telemetry.gps_info().__anext__()
            self._sensor_viewmodel.updateSensor("GPS Fix", str(gps_info.fix_type), "")
            self._sensor_viewmodel.updateSensor("GPS Satellites", str(gps_info.num_satellites), "")
            
            # System Status
            # Vereinfachte CPU-Last-Simulation, da MAVSDK diese Info nicht direkt liefert
            self._sensor_viewmodel.updateSensor("System CPU", "25.0%", "")
            
        except Exception as e:
            self._logger.addLog(f"Fehler beim Abrufen von Telemetriedaten: {str(e)}")
    
    @Slot()
    def disconnect(self):
        self._logger.addLog("Verbindung wird getrennt...")
        
        # Timer anhalten
        self._update_timer.stop()
        
        if MAVSDK_AVAILABLE and self._drone:
            # Asynchron trennen
            asyncio.run_coroutine_threadsafe(self._disconnect_drone(), self._loop)
        else:
            # Simuliertes Trennen
            self._is_connected = False
            self.connectionChanged.emit(False)
            self._logger.addLog("Verbindung getrennt")
        
        return True
    
    async def _disconnect_drone(self):
        try:
            # Keine direkte disconnect-Methode in MAVSDK, aber wir können aufräumen
            self._drone = None
            self._is_connected = False
            self.connectionChanged.emit(False)
            self._logger.addLog("MAVSDK-Verbindung getrennt")
        except Exception as e:
            self._logger.addLog(f"Fehler beim Trennen der Verbindung: {str(e)}")
    
    @Slot()
    def arm(self):
        if self._is_connected and MAVSDK_AVAILABLE and self._drone:
            self._logger.addLog("Arming...")
            asyncio.run_coroutine_threadsafe(self._arm_drone(), self._loop)
        return True
    
    async def _arm_drone(self):
        try:
            await self._drone.action.arm()
            self._logger.addLog("Drone erfolgreich gearmt")
        except Exception as e:
            self._logger.addLog(f"Fehler beim Arming: {str(e)}")
    
    @Slot()
    def disarm(self):
        if self._is_connected and MAVSDK_AVAILABLE and self._drone:
            self._logger.addLog("Disarming...")
            asyncio.run_coroutine_threadsafe(self._disarm_drone(), self._loop)
        return True
    
    async def _disarm_drone(self):
        try:
            await self._drone.action.disarm()
            self._logger.addLog("Drone erfolgreich disarmt")
        except Exception as e:
            self._logger.addLog(f"Fehler beim Disarming: {str(e)}")
    
    @Slot()
    def takeoff(self):
        if self._is_connected and MAVSDK_AVAILABLE and self._drone:
            self._logger.addLog("Starte Takeoff...")
            asyncio.run_coroutine_threadsafe(self._takeoff_drone(), self._loop)
        return True
    
    async def _takeoff_drone(self):
        try:
            await self._drone.action.takeoff()
            self._logger.addLog("Takeoff gestartet")
        except Exception as e:
            self._logger.addLog(f"Fehler beim Takeoff: {str(e)}")
    
    @Slot()
    def land(self):
        if self._is_connected and MAVSDK_AVAILABLE and self._drone:
            self._logger.addLog("Starte Landung...")
            asyncio.run_coroutine_threadsafe(self._land_drone(), self._loop)
        return True
    
    async def _land_drone(self):
        try:
            await self._drone.action.land()
            self._logger.addLog("Landung eingeleitet")
        except Exception as e:
            self._logger.addLog(f"Fehler bei der Landung: {str(e)}")
    
    @Property(bool, notify=connectionChanged)
    def is_connected(self):
        return self._is_connected
        
    @Property(bool, notify=armingChanged)
    def is_armed(self):
        return self._is_armed
        
    @Property(str, notify=flightModeChanged)
    def flight_mode(self):
        return self._flight_mode


def main():
    # Pfad anpassen, damit QML-Dateien gefunden werden
    app_path = os.path.dirname(os.path.abspath(__file__))
    os.chdir(os.path.join(app_path, ".."))
    
    # QT-Anwendung erstellen
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    
    # Komponenten erstellen
    logger = Logger()
    sensor_viewmodel = SensorViewModel()
    
    # MAVSDK-Event-Loop in separatem Thread starten, wenn MAVSDK verfügbar ist
    if MAVSDK_AVAILABLE:
        # Starte den asyncio Event-Loop in einem separaten Thread
        def run_event_loop(loop):
            asyncio.set_event_loop(loop)
            loop.run_forever()
        
        event_loop = asyncio.new_event_loop()
        import threading
        event_loop_thread = threading.Thread(target=run_event_loop, args=(event_loop,), daemon=True)
        event_loop_thread.start()
        logger.addLog("MAVSDK Event-Loop gestartet")
    
    # Drone-Controller mit korrekten Parametern erstellen
    drone_controller = DroneController(logger, sensor_viewmodel)
    
    # QML-Kontext einrichten
    root_context = engine.rootContext()
    root_context.setContextProperty("droneController", drone_controller)
    root_context.setContextProperty("sensorViewModel", sensor_viewmodel)
    root_context.setContextProperty("logger", logger)
    
    # QML-Importpfade einrichten
    project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    rzgcs_dir = os.path.join(project_dir, "RZGCSContent")
    
    # Wichtig: Alle möglichen Importpfade hinzufügen
    engine.addImportPath(project_dir)  # Projektwurzel
    engine.addImportPath(rzgcs_dir)    # RZGCSContent Verzeichnis
    
    # QML-Module-Umgebungsvariable setzen (wichtig für Qt)
    os.environ["QML2_IMPORT_PATH"] = f"{project_dir}{os.pathsep}{rzgcs_dir}"
    
    # Debug-Log für QML-Importpfade
    logger.addLog(f"QML-Importpfade: {engine.importPathList()}")
    
    # QML-Hauptdatei laden
    qml_file = os.path.join(os.path.dirname(__file__), "..", "RZGCSContent", "App.qml")
    qml_url = QUrl.fromLocalFile(os.path.abspath(qml_file))
    
    logger.addLog(f"Lade QML-Datei: {qml_file}")
    engine.load(qml_url)
    
    # Prüfen, ob QML-Datei erfolgreich geladen wurde
    if not engine.rootObjects():
        logger.addLog("❌ Fehler beim Laden der QML-Datei")
        return -1
    
    logger.addLog("RZGCS mit MAVSDK gestartet")
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
