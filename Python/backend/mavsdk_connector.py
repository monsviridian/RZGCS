"""
MAVSDK-Connector für RZGCS
Bietet eine moderne Alternative zum pymavlink-basierten Connector
"""

import asyncio
import time
from typing import Optional, Dict, Any, List, Callable
from PySide6.QtCore import QObject, Signal, Slot, QThread, QTimer

import mavsdk
from mavsdk.telemetry import (
    Position, 
    Quaternion, 
    Attitude, 
    AngularVelocityBody, 
    GroundTruth,
    GpsInfo,
    Battery,
    RcStatus,
    StatusText,
    ActuatorControlTarget,
    ActuatorOutputStatus,
    VelocityNed,
    PositionVelocityNed
)
from mavsdk.system import System
from mavsdk.action import ActionError
from .logger import Logger


class MAVSDKThread(QThread):
    """Thread für die asynchrone MAVSDK Event-Loop"""
    
    def __init__(self, connector):
        """Initialisiert den MAVSDK-Thread
        
        Args:
            connector: Die MAVSDKConnector-Instanz
        """
        super().__init__()
        self.connector = connector
        self._running = False
        
    def run(self):
        """Führt die asyncio Event-Loop aus"""
        self._running = True
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(self.connector.run())
        except Exception as e:
            self.connector._logger.addLog(f"❌ Fehler im MAVSDK-Thread: {str(e)}")
        finally:
            loop.close()
            self._running = False
            
    def stop(self):
        """Stoppt den Thread"""
        self._running = False
        self.connector._stop_event.set()
        self.wait()


class MAVSDKConnector(QObject):
    """MAVSDK-basierter Connector für die Kommunikation mit Drohnen"""
    
    # Signale für verschiedene Telemetrie-Daten
    position_received = Signal(object)
    attitude_received = Signal(object)
    battery_received = Signal(object)
    gps_info_received = Signal(object)
    status_text_received = Signal(object)
    health_received = Signal(object)
    armed_received = Signal(bool)
    flight_mode_received = Signal(str)
    actuator_control_target_received = Signal(object)
    actuator_output_status_received = Signal(object)
    connected = Signal()
    disconnected = Signal()
    error_occurred = Signal(str)
    
    def __init__(self, logger: Logger):
        """Initialisiert den MAVSDK-Connector
        
        Args:
            logger: Logger-Instanz für die Protokollierung
        """
        super().__init__()
        self._logger = logger
        self._drone = System()
        self._thread = None
        self._stop_event = asyncio.Event()
        self._connection_string = ""
        self._is_connected = False
        self._is_simulator = False
        self._last_telemetry_time = {}
        
        # Timer für Telemetrie-Ratensteuerung
        self._telemetry_timers = {}
        
    @Slot(str)
    def connect(self, connection_string: str) -> bool:
        """Verbindet mit einem Fahrzeug über die angegebene Verbindung
        
        Args:
            connection_string: Der Verbindungsstring (z.B. udp://:14550 oder serial:///dev/ttyACM0:57600)
            
        Returns:
            bool: True, wenn die Verbindung erfolgreich initiiert wurde
        """
        if self._is_connected:
            self._logger.addLog("🔄 Bereits verbunden, zuerst trennen")
            return False
            
        self._connection_string = connection_string
        self._is_simulator = "udp" in connection_string.lower()
        
        # Protokolliere Verbindungsversuch
        if self._is_simulator:
            self._logger.addLog(f"🚁 Verbinde mit SITL-Simulator über {connection_string}")
        else:
            self._logger.addLog(f"🚁 Verbinde mit Fluggerät über {connection_string}")
        
        # Starte MAVSDK-Thread
        self._thread = MAVSDKThread(self)
        self._thread.start()
        
        return True
        
    def disconnect(self) -> bool:
        """Trennt die Verbindung zum Fahrzeug
        
        Returns:
            bool: True, wenn die Trennung erfolgreich war
        """
        if not self._is_connected:
            return True
            
        try:
            # Event setzen, um die asyncio-Loops zu beenden
            self._stop_event.set()
            
            # Thread stoppen, falls er läuft
            if self._thread and self._thread.isRunning():
                self._thread.stop()
                self._thread = None
                
            self._is_connected = False
            self._logger.addLog("🔌 Verbindung getrennt")
            
            # Signal senden
            self.disconnected.emit()
            
            return True
            
        except Exception as e:
            error_msg = f"❌ Fehler beim Trennen: {str(e)}"
            self._logger.addLog(error_msg)
            self.error_occurred.emit(error_msg)
            return False
    
    async def run(self):
        """Hauptschleife für den MAVSDK-Thread"""
        try:
            # Verbindung zum Drohne-System herstellen
            self._logger.addLog(f"🔄 Initialisiere MAVSDK-Verbindung zu {self._connection_string}")
            
            # Verbindungsstring für MAVSDK formatieren
            # Konvertiere zwischen pymavlink- und MAVSDK-Formaten
            mavsdk_url = self._connection_string
            
            # Für serielle Verbindungen
            if "serial://" in self._connection_string:
                # Extrahiere Port und Baudrate
                parts = self._connection_string.replace("serial://", "").split(":")
                if len(parts) == 2:
                    port, baudrate = parts
                    mavsdk_url = f"serial://{port}:{baudrate}"
            
            # Verbinde zum Drohnen-System
            await self._drone.connect(system_address=mavsdk_url)
            
            # Warte auf die Drohne
            self._logger.addLog("⏳ Warte auf Fahrzeugverbindung...")
            async for state in self._drone.core.connection_state():
                if state.is_connected:
                    self._logger.addLog("✅ Fahrzeug verbunden!")
                    self._is_connected = True
                    self.connected.emit()
                    break
            
            # Abbrechen, wenn Stop-Event gesetzt ist
            if self._stop_event.is_set():
                return
                
            # Telemetrie-Streams starten
            await self._start_telemetry_subscriptions()
            
            # Event-Loop am Leben halten, bis Stopp angefordert wird
            while not self._stop_event.is_set():
                await asyncio.sleep(0.1)
                
        except Exception as e:
            error_msg = f"❌ Fehler in MAVSDK-Verbindung: {str(e)}"
            self._logger.addLog(error_msg)
            self.error_occurred.emit(error_msg)
        finally:
            self._is_connected = False
            self._logger.addLog("🔌 MAVSDK-Verbindung beendet")
            self.disconnected.emit()
    
    async def _start_telemetry_subscriptions(self):
        """Startet alle Telemetrie-Subscriptions"""
        try:
            # Position
            self._drone.telemetry.position.subscribe(self._handle_position)
            
            # Attitude
            self._drone.telemetry.attitude_euler.subscribe(self._handle_attitude)
            
            # Battery
            self._drone.telemetry.battery.subscribe(self._handle_battery)
            
            # GPS Info
            self._drone.telemetry.gps_info.subscribe(self._handle_gps_info)
            
            # Status Text
            self._drone.telemetry.status_text.subscribe(self._handle_status_text)
            
            # Armed Status
            self._drone.telemetry.armed.subscribe(self._handle_armed)
            
            # Flight Mode
            self._drone.telemetry.flight_mode.subscribe(self._handle_flight_mode)
            
            # Actuator Control Target
            self._drone.telemetry.actuator_control_target.subscribe(self._handle_actuator_control_target)
            
            # Actuator Output Status
            self._drone.telemetry.actuator_output_status.subscribe(self._handle_actuator_output_status)
            
            self._logger.addLog("✅ Telemetrie-Subscriptions gestartet")
            
        except Exception as e:
            error_msg = f"❌ Fehler beim Start der Telemetrie: {str(e)}"
            self._logger.addLog(error_msg)
            self.error_occurred.emit(error_msg)
    
    def _should_emit_telemetry(self, message_type: str, min_interval: float = 0.1) -> bool:
        """Prüft, ob eine Telemetrie-Nachricht gesendet werden sollte basierend auf Rate-Limiting
        
        Args:
            message_type: Typ der Telemetrie-Nachricht
            min_interval: Minimales Intervall zwischen Nachrichten in Sekunden
            
        Returns:
            bool: True, wenn die Nachricht gesendet werden sollte
        """
        current_time = time.time()
        
        # Überprüfe, ob wir diesen Nachrichtentyp schon einmal gesehen haben
        if message_type not in self._last_telemetry_time:
            self._last_telemetry_time[message_type] = current_time
            return True
            
        # Überprüfe, ob genug Zeit vergangen ist
        elapsed = current_time - self._last_telemetry_time[message_type]
        if elapsed >= min_interval:
            self._last_telemetry_time[message_type] = current_time
            return True
            
        return False
    
    def _handle_position(self, position):
        """Verarbeitet Position-Updates"""
        if self._should_emit_telemetry("position", 0.2):
            self.position_received.emit(position)
    
    def _handle_attitude(self, attitude):
        """Verarbeitet Attitude-Updates"""
        if self._should_emit_telemetry("attitude", 0.1):
            self.attitude_received.emit(attitude)
    
    def _handle_battery(self, battery):
        """Verarbeitet Battery-Updates"""
        if self._should_emit_telemetry("battery", 1.0):
            self.battery_received.emit(battery)
    
    def _handle_gps_info(self, gps_info):
        """Verarbeitet GPS-Info-Updates"""
        if self._should_emit_telemetry("gps_info", 0.5):
            self.gps_info_received.emit(gps_info)
    
    def _handle_status_text(self, status_text):
        """Verarbeitet Status-Text-Updates"""
        # Status-Texte immer sofort emittieren
        self.status_text_received.emit(status_text)
        
        # Status-Text in Log schreiben
        severity_name = "INFO"
        if status_text.type == StatusText.StatusType.CRITICAL:
            severity_name = "CRITICAL"
        elif status_text.type == StatusText.StatusType.ERROR:
            severity_name = "ERROR"
        elif status_text.type == StatusText.StatusType.WARNING:
            severity_name = "WARNING"
        elif status_text.type == StatusText.StatusType.NOTICE:
            severity_name = "NOTICE"
        
        # Prüfen, ob es sich um eine Systeminformation handelt
        if ("ArduCopter" in status_text.text or 
            "ArduPlane" in status_text.text or 
            "Frame:" in status_text.text or
            "Frame Type:" in status_text.text or 
            "MicroAir" in status_text.text or 
            "ChibiOS" in status_text.text or
            "NuttX" in status_text.text or 
            "VERSION" in status_text.text):
            # Als Systeminformation markieren
            self._logger.addLog(f"[SYSTEM INFO] {status_text.text}")
        else:
            # Normale Nachricht
            self._logger.addLog(f"[{severity_name}] {status_text.text}")
    
    def _handle_armed(self, armed):
        """Verarbeitet Armed-Status-Updates"""
        if self._should_emit_telemetry("armed", 1.0):
            self.armed_received.emit(armed)
            
            # Normale Log-Meldung (nicht als SYSTEM INFO, wie gewünscht)
            status = "ARMED" if armed else "DISARMED"
            self._logger.addLog(f"System ist jetzt {status}")
    
    def _handle_flight_mode(self, flight_mode):
        """Verarbeitet Flight-Mode-Updates"""
        if self._should_emit_telemetry("flight_mode", 1.0):
            mode_str = str(flight_mode)
            self.flight_mode_received.emit(mode_str)
    
    def _handle_actuator_control_target(self, actuator_control):
        """Verarbeitet Actuator-Control-Target-Updates"""
        if self._should_emit_telemetry("actuator_control", 0.5):
            self.actuator_control_target_received.emit(actuator_control)
    
    def _handle_actuator_output_status(self, actuator_output):
        """Verarbeitet Actuator-Output-Status-Updates"""
        if self._should_emit_telemetry("actuator_output", 0.5):
            self.actuator_output_status_received.emit(actuator_output)
            
    async def arm(self) -> bool:
        """Armiert das Fahrzeug
        
        Returns:
            bool: True, wenn das Armieren erfolgreich war
        """
        if not self._is_connected:
            self._logger.addLog("❌ Nicht verbunden")
            return False
            
        try:
            await self._drone.action.arm()
            self._logger.addLog("✅ Fahrzeug armiert")
            return True
        except ActionError as e:
            error_msg = f"❌ Arming fehlgeschlagen: {str(e)}"
            self._logger.addLog(error_msg)
            self.error_occurred.emit(error_msg)
            return False
            
    async def disarm(self) -> bool:
        """Disarmiert das Fahrzeug
        
        Returns:
            bool: True, wenn das Disarmieren erfolgreich war
        """
        if not self._is_connected:
            self._logger.addLog("❌ Nicht verbunden")
            return False
            
        try:
            await self._drone.action.disarm()
            self._logger.addLog("✅ Fahrzeug disarmiert")
            return True
        except ActionError as e:
            error_msg = f"❌ Disarming fehlgeschlagen: {str(e)}"
            self._logger.addLog(error_msg)
            self.error_occurred.emit(error_msg)
            return False
            
    async def takeoff(self) -> bool:
        """Lässt das Fahrzeug starten
        
        Returns:
            bool: True, wenn der Start erfolgreich initiiert wurde
        """
        if not self._is_connected:
            self._logger.addLog("❌ Nicht verbunden")
            return False
            
        try:
            await self._drone.action.takeoff()
            self._logger.addLog("🚁 Takeoff initiiert")
            return True
        except ActionError as e:
            error_msg = f"❌ Takeoff fehlgeschlagen: {str(e)}"
            self._logger.addLog(error_msg)
            self.error_occurred.emit(error_msg)
            return False
            
    async def land(self) -> bool:
        """Lässt das Fahrzeug landen
        
        Returns:
            bool: True, wenn die Landung erfolgreich initiiert wurde
        """
        if not self._is_connected:
            self._logger.addLog("❌ Nicht verbunden")
            return False
            
        try:
            await self._drone.action.land()
            self._logger.addLog("🛬 Landung initiiert")
            return True
        except ActionError as e:
            error_msg = f"❌ Landung fehlgeschlagen: {str(e)}"
            self._logger.addLog(error_msg)
            self.error_occurred.emit(error_msg)
            return False
            
    async def reboot(self) -> bool:
        """Führt einen Neustart des Flugcomputers durch
        
        Returns:
            bool: True, wenn der Neustart erfolgreich initiiert wurde
        """
        if not self._is_connected:
            self._logger.addLog("❌ Nicht verbunden")
            return False
            
        try:
            await self._drone.action.reboot()
            self._logger.addLog("🔄 Neustart des Flugcomputers initiiert")
            return True
        except ActionError as e:
            error_msg = f"❌ Neustart fehlgeschlagen: {str(e)}"
            self._logger.addLog(error_msg)
            self.error_occurred.emit(error_msg)
            return False
