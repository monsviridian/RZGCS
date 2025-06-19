#!/usr/bin/env python3
"""
EnhancedMAVSDKConnector - Verbesserte Integration von MAVSDK mit Fehlerbehandlung

Diese Klasse implementiert das DroneConnectionInterface und nutzt MAVSDK
für die Kommunikation mit Drohnen über serielle Verbindungen oder UDP.
"""

import os
import sys
import time
import asyncio
import threading
from typing import List, Dict, Optional, Tuple, Callable, Any

try:
    import mavsdk
    from mavsdk import System
    from mavsdk.mission import (MissionItem, MissionPlan)
    from mavsdk.telemetry import (LandedState, FlightMode)
except ImportError:
    print("FEHLER: MAVSDK nicht installiert")
    print("Installiere mit: pip install mavsdk")
    sys.exit(1)

from PySide6.QtCore import QObject, Signal, QThread, QEventLoop, QTimer

# Eigene Module
from backend.drone_connection_interface import DroneConnectionInterface
from backend.logger import Logger
from backend.mavsdk_server_controller import MAVSDKServerController
from backend.exceptions import ConnectionError, ConnectionTimeoutError


class MAVSDKThread(QThread):
    """Thread für die MAVSDK-Kommunikation"""
    
    def __init__(self, run_method, parent=None):
        """Initialisierung des MAVSDK-Threads"""
        super().__init__(parent)
        self._run_method = run_method
        self._loop = None
        
    def run(self):
        """Hauptmethode des Threads"""
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        
        # Koroutine starten
        self._loop.run_until_complete(self._run_method())
        
        # Event-Loop beenden
        self._loop.close()


class EnhancedMAVSDKConnector(QObject, DroneConnectionInterface):
    """
    Erweiterte MAVSDK-Connector-Klasse, die das DroneConnectionInterface implementiert
    """
    
    # Signale aus dem Interface
    connected = Signal()
    disconnected = Signal()
    error_occurred = Signal(str)
    telemetry_updated = Signal(dict)
    armed_changed = Signal(bool)
    flight_mode_changed = Signal(str)
    gps_info_changed = Signal(dict)
    battery_changed = Signal(dict)
    attitude_changed = Signal(dict)
    heading_changed = Signal(float)
    position_changed = Signal(dict)
    home_position_changed = Signal(dict)
    statustext_received = Signal(str)
    
    def __init__(self, logger: Logger, parent=None):
        """Initialisierung des EnhancedMAVSDKConnector"""
        QObject.__init__(self, parent)
        
        # Logger
        self._logger = logger
        
        # MAVSDK-System
        self._drone = System()
        
        # MAVSDK-Server-Controller
        self._server_controller = MAVSDKServerController(logger)
        
        # Thread und Event-Loop
        self._thread = None
        self._stop_event = threading.Event()
        
        # Verbindungsstatus
        self._is_connected = False
        self._connection_string = ""
        
        # Telemetrie-Caching
        self._telemetry_cache = {}
        
        # Konfiguration
        self._message_filter_enabled = True
        self._message_filter_threshold = {
            'battery': 1.0,  # 1% Änderung
            'heading': 5.0,  # 5 Grad Änderung
            'altitude': 0.5,  # 0.5m Änderung
            'speed': 0.5,    # 0.5 m/s Änderung
        }
        self._message_filter_interval = {
            'battery': 5.0,    # 5 Sekunden
            'heading': 1.0,    # 1 Sekunde
            'position': 1.0,   # 1 Sekunde
            'attitude': 1.0,   # 1 Sekunde
            'gps': 5.0,        # 5 Sekunden
            'statustext': 0.0, # Immer anzeigen
        }
        self._last_message_time = {}
    
    def connect(self, connection_string: str) -> bool:
        """
        Verbindet mit einer Drohne über den angegebenen Verbindungsstring
        
        Args:
            connection_string: Verbindungsstring im Format "protocol:host:port"
                               oder "serial:port:baudrate"
        
        Returns:
            bool: True, wenn die Verbindung erfolgreich gestartet wurde
        """
        if self._is_connected:
            self._logger.addLog("[INFO] Bereits verbunden, trenne zuerst")
            self.disconnect()
        
        # Verbindungsstring speichern
        self._connection_string = connection_string
        
        # Thread für die Verbindung starten
        self._stop_event.clear()
        self._thread = MAVSDKThread(self._run)
        self._thread.start()
        
        # Der tatsächliche Verbindungsstatus wird im Thread gesetzt
        return True
        
    def connect_serial(self, port: str, baudrate: int) -> bool:
        """
        Verbindet mit einer Drohne über einen seriellen Port
        
        Args:
            port: COM-Port oder Device (z.B. COM3, /dev/ttyACM0)
            baudrate: Baudrate (z.B. 57600, 115200)
            
        Returns:
            bool: True, wenn die Verbindung erfolgreich gestartet wurde
        """
        # MAVSDK-Server starten
        if not self._server_controller.start_server(port, baudrate):
            error_msg = f"[FEHLER] MAVSDK-Server konnte nicht gestartet werden für {port}:{baudrate}"
            self._logger.addLog(error_msg)
            self.error_occurred.emit(error_msg)
            return False
            
        # Kurz warten, bis der Server gestartet ist
        time.sleep(1.5)
        
        # Mit MAVSDK-Server verbinden
        connection_string = "tcp://localhost:50051"
        self._logger.addLog(f"[INFO] Verbinde mit MAVSDK-Server über {connection_string}")
        
        return self.connect(connection_string)
    
    def disconnect(self) -> bool:
        """
        Trennt die Verbindung zur Drohne
        
        Returns:
            bool: True, wenn die Verbindung erfolgreich getrennt wurde
        """
        try:
            # Stoppe MAVSDK-Thread
            self._stop_event.set()
            
            if self._thread:
                self._thread.wait(5000)  # Warte max. 5 Sekunden
                self._thread = None
            
            # Stoppe MAVSDK-Server
            self._server_controller.stop_server()
            
            # Status zurücksetzen
            self._is_connected = False
            self._connection_string = ""
            
            # Signal senden
            self.disconnected.emit()
            
            self._logger.addLog("[INFO] Verbindung zur Drohne getrennt")
            return True
            
        except Exception as e:
            error_msg = f"[FEHLER] Fehler beim Trennen der Verbindung: {str(e)}"
            self._logger.addLog(error_msg)
            self.error_occurred.emit(error_msg)
            return False
    
    def is_connected(self) -> bool:
        """
        Gibt zurück, ob eine Verbindung zur Drohne besteht
        
        Returns:
            bool: True, wenn eine Verbindung besteht
        """
        return self._is_connected
    
    def arm(self) -> bool:
        """
        Armiert die Drohne
        
        Returns:
            bool: True, wenn der Armierungs-Befehl erfolgreich gesendet wurde
        """
        if not self._is_connected:
            self._logger.addLog("[FEHLER] Nicht verbunden")
            return False
            
        # Armierungs-Befehl senden
        self._logger.addLog("[INFO] Sende Armierungs-Befehl")
        
        # Koroutine im Thread ausführen
        self._execute_in_thread(self._drone.action.arm)
        return True
    
    def disarm(self) -> bool:
        """
        Disarmiert die Drohne
        
        Returns:
            bool: True, wenn der Disarmierungs-Befehl erfolgreich gesendet wurde
        """
        if not self._is_connected:
            self._logger.addLog("[FEHLER] Nicht verbunden")
            return False
            
        # Disarmierungs-Befehl senden
        self._logger.addLog("[INFO] Sende Disarmierungs-Befehl")
        
        # Koroutine im Thread ausführen
        self._execute_in_thread(self._drone.action.disarm)
        return True
    
    def takeoff(self) -> bool:
        """
        Lässt die Drohne starten
        
        Returns:
            bool: True, wenn der Takeoff-Befehl erfolgreich gesendet wurde
        """
        if not self._is_connected:
            self._logger.addLog("[FEHLER] Nicht verbunden")
            return False
            
        # Takeoff-Befehl senden
        self._logger.addLog("[INFO] Sende Takeoff-Befehl")
        
        # Koroutine im Thread ausführen
        self._execute_in_thread(self._drone.action.takeoff)
        return True
    
    def land(self) -> bool:
        """
        Lässt die Drohne landen
        
        Returns:
            bool: True, wenn der Land-Befehl erfolgreich gesendet wurde
        """
        if not self._is_connected:
            self._logger.addLog("[FEHLER] Nicht verbunden")
            return False
            
        # Land-Befehl senden
        self._logger.addLog("[INFO] Sende Land-Befehl")
        
        # Koroutine im Thread ausführen
        self._execute_in_thread(self._drone.action.land)
        return True
    
    def _execute_in_thread(self, coroutine_func, *args, **kwargs):
        """
        Führt eine Koroutine im MAVSDK-Thread aus
        
        Args:
            coroutine_func: Die auszuführende Koroutine
            *args, **kwargs: Parameter für die Koroutine
        """
        if self._thread and hasattr(self._thread, '_loop') and self._thread._loop:
            asyncio.run_coroutine_threadsafe(coroutine_func(*args, **kwargs), self._thread._loop)
        else:
            self._logger.addLog("[FEHLER] MAVSDK-Thread nicht verfügbar")
    
    async def _run(self):
        """
        Hauptschleife für den MAVSDK-Thread
        """
        try:
            # Verbindung herstellen
            self._logger.addLog(f"[INFO] Verbinde mit Drone über {self._connection_string}")
            await self._drone.connect(system_address=self._connection_string)
            
            # Warte auf Verbindung
            self._logger.addLog("[INFO] Warte auf Heartbeat...")
            async for state in self._drone.core.connection_state():
                if state.is_connected:
                    self._logger.addLog("[INFO] Verbindung hergestellt")
                    self._is_connected = True
                    self.connected.emit()
                    
                    # Telemetrie-Subscriptions starten
                    await self._start_telemetry_subscriptions()
                    break
            
            # Systeminformationen abfragen (für Preflight-View)
            await self._request_system_info()
            
            # Warte auf Stop-Event
            while not self._stop_event.is_set():
                await asyncio.sleep(0.1)
                
        except Exception as e:
            self._logger.addLog(f"[FEHLER] MAVSDK-Fehler: {str(e)}")
            self.error_occurred.emit(str(e))
            
        finally:
            # Verbindung trennen
            self._is_connected = False
            self._logger.addLog("[INFO] MAVSDK-Thread beendet")
            
    async def _start_telemetry_subscriptions(self):
        """
        Startet alle Telemetrie-Subscriptions
        """
        # Armed-Status
        self._execute_in_thread(self._monitor_armed_status)
        
        # Flugmodus
        self._execute_in_thread(self._monitor_flight_mode)
        
        # GPS-Info
        self._execute_in_thread(self._monitor_gps_info)
        
        # Batterie
        self._execute_in_thread(self._monitor_battery)
        
        # Attitude
        self._execute_in_thread(self._monitor_attitude)
        
        # Position
        self._execute_in_thread(self._monitor_position)
        
        # Home-Position
        self._execute_in_thread(self._monitor_home_position)
        
        # Status-Texte
        self._execute_in_thread(self._monitor_status_text)
    
    async def _request_system_info(self):
        """
        Fragt Systeminformationen ab und zeigt sie in der Preflight-View an
        """
        try:
            # Automatisch nach Systeminformationen fragen
            self._logger.addLog("[INFO] Frage Systeminformationen ab...")
            
            # Version abfragen
            version = await self._drone.info.get_version()
            self._logger.addLog(f"[SYSTEM INFO] Version: {version.flight_sw_major}.{version.flight_sw_minor}.{version.flight_sw_patch}")
            self._logger.addLog(f"[SYSTEM INFO] Hardware: {version.hardware}")
            
            # Produkt abfragen
            product = await self._drone.info.get_product()
            self._logger.addLog(f"[SYSTEM INFO] Produkt: {product.name}")
            
        except Exception as e:
            self._logger.addLog(f"[FEHLER] Fehler beim Abfragen der Systeminformationen: {str(e)}")
    
    async def _monitor_armed_status(self):
        """
        Überwacht den Armed-Status
        """
        try:
            async for armed in self._drone.telemetry.armed():
                # Status-Änderung melden
                self.armed_changed.emit(armed)
                
                # Bei Änderung loggen
                if self._should_emit_message('armed', armed):
                    self._logger.addLog(f"[INFO] Armed-Status: {'ARMED' if armed else 'DISARMED'}")
                    
        except Exception as e:
            self._logger.addLog(f"[FEHLER] Fehler beim Überwachen des Armed-Status: {str(e)}")
    
    async def _monitor_flight_mode(self):
        """
        Überwacht den Flugmodus
        """
        try:
            async for flight_mode in self._drone.telemetry.flight_mode():
                mode_str = str(flight_mode)
                
                # Status-Änderung melden
                self.flight_mode_changed.emit(mode_str)
                
                # Bei Änderung loggen
                if self._should_emit_message('flight_mode', mode_str):
                    self._logger.addLog(f"[INFO] Flugmodus: {mode_str}")
                    
        except Exception as e:
            self._logger.addLog(f"[FEHLER] Fehler beim Überwachen des Flugmodus: {str(e)}")
    
    async def _monitor_gps_info(self):
        """
        Überwacht die GPS-Informationen
        """
        try:
            async for gps_info in self._drone.telemetry.gps_info():
                # GPS-Info als Dictionary
                info = {
                    'num_satellites': gps_info.num_satellites,
                    'fix_type': gps_info.fix_type
                }
                
                # Status-Änderung melden
                self.gps_info_changed.emit(info)
                
                # Bei Änderung loggen
                if self._should_emit_message('gps', info):
                    self._logger.addLog(f"[INFO] GPS: {gps_info.num_satellites} Satelliten, Fix: {gps_info.fix_type}")
                    
        except Exception as e:
            self._logger.addLog(f"[FEHLER] Fehler beim Überwachen der GPS-Informationen: {str(e)}")
    
    async def _monitor_battery(self):
        """
        Überwacht den Batteriestatus
        """
        try:
            async for battery in self._drone.telemetry.battery():
                # Batterie-Info als Dictionary
                info = {
                    'remaining_percent': battery.remaining_percent,
                    'voltage_v': battery.voltage_v,
                    'current_a': battery.current_a
                }
                
                # Status-Änderung melden
                self.battery_changed.emit(info)
                
                # Bei signifikanter Änderung loggen
                if self._should_emit_message('battery', info['remaining_percent']):
                    self._logger.addLog(f"[INFO] Batterie: {info['remaining_percent']:.1f}%, {info['voltage_v']:.2f}V")
                    
        except Exception as e:
            self._logger.addLog(f"[FEHLER] Fehler beim Überwachen des Batteriestatus: {str(e)}")
    
    async def _monitor_attitude(self):
        """
        Überwacht die Lage der Drohne
        """
        try:
            async for attitude in self._drone.telemetry.attitude_euler():
                # Lage als Dictionary
                info = {
                    'roll_deg': attitude.roll_deg,
                    'pitch_deg': attitude.pitch_deg,
                    'yaw_deg': attitude.yaw_deg
                }
                
                # Status-Änderung melden
                self.attitude_changed.emit(info)
                self.heading_changed.emit(attitude.yaw_deg)
                
                # Bei signifikanter Änderung des Headings loggen
                if self._should_emit_message('heading', attitude.yaw_deg):
                    self._logger.addLog(f"[INFO] Heading: {attitude.yaw_deg:.1f}\u00b0")
                    
        except Exception as e:
            self._logger.addLog(f"[FEHLER] Fehler beim Überwachen der Lage: {str(e)}")
    
    async def _monitor_position(self):
        """
        Überwacht die Position der Drohne
        """
        try:
            async for position in self._drone.telemetry.position():
                # Position als Dictionary
                info = {
                    'latitude_deg': position.latitude_deg,
                    'longitude_deg': position.longitude_deg,
                    'absolute_altitude_m': position.absolute_altitude_m,
                    'relative_altitude_m': position.relative_altitude_m
                }
                
                # Status-Änderung melden
                self.position_changed.emit(info)
                
                # Bei signifikanter Änderung der Höhe loggen
                if self._should_emit_message('altitude', info['relative_altitude_m']):
                    self._logger.addLog(f"[INFO] Höhe: {info['relative_altitude_m']:.1f}m AGL")
                    
        except Exception as e:
            self._logger.addLog(f"[FEHLER] Fehler beim Überwachen der Position: {str(e)}")
    
    async def _monitor_home_position(self):
        """
        Überwacht die Home-Position der Drohne
        """
        try:
            async for position in self._drone.telemetry.home():
                # Home-Position als Dictionary
                info = {
                    'latitude_deg': position.latitude_deg,
                    'longitude_deg': position.longitude_deg,
                    'absolute_altitude_m': position.absolute_altitude_m,
                    'relative_altitude_m': position.relative_altitude_m
                }
                
                # Status-Änderung melden
                self.home_position_changed.emit(info)
                
        except Exception as e:
            self._logger.addLog(f"[FEHLER] Fehler beim Überwachen der Home-Position: {str(e)}")
    
    async def _monitor_status_text(self):
        """
        Überwacht Status-Texte
        """
        try:
            async for status_text in self._drone.telemetry.status_text():
                text = status_text.text
                
                # Auf Systeminformationen prüfen (für Preflight-View)
                is_system_info = False
                system_info_patterns = [
                    "Frame", "ArduCopter", "MicoAir743", "ChibiOS", 
                    "PreArm", "RCOut", "Firmware", "Version"
                ]
                
                for pattern in system_info_patterns:
                    if pattern in text:
                        is_system_info = True
                        break
                
                # Systeminformationen markieren
                if is_system_info and not text.startswith("[SYSTEM INFO]"):
                    text = f"[SYSTEM INFO] {text}"
                
                # Status-Text melden
                self.statustext_received.emit(text)
                
                # Status-Texte immer loggen (keine Filterung)
                self._logger.addLog(text)
                
        except Exception as e:
            self._logger.addLog(f"[FEHLER] Fehler beim Überwachen der Status-Texte: {str(e)}")
    
    def _should_emit_message(self, message_type: str, value: Any) -> bool:
        """
        Prüft, ob eine Nachricht ausgegeben werden soll, basierend auf Schwellenwerten und Zeitintervallen
        
        Args:
            message_type: Typ der Nachricht (z.B. 'battery', 'heading')
            value: Aktueller Wert
            
        Returns:
            bool: True, wenn die Nachricht ausgegeben werden soll
        """
        # Nachrichtenfilterung deaktiviert
        if not self._message_filter_enabled:
            return True
            
        # Status-Texte immer ausgeben
        if message_type == 'statustext':
            return True
            
        # Aktuelle Zeit
        current_time = time.time()
        
        # Prüfen, ob genügend Zeit vergangen ist
        if message_type in self._last_message_time:
            interval = self._message_filter_interval.get(message_type, 1.0)
            if current_time - self._last_message_time[message_type] < interval:
                return False
        
        # Prüfen, ob sich der Wert signifikant geändert hat
        if message_type in self._telemetry_cache:
            threshold = self._message_filter_threshold.get(message_type, 0.0)
            
            if isinstance(value, (int, float)):
                old_value = self._telemetry_cache[message_type]
                if isinstance(old_value, (int, float)) and abs(value - old_value) < threshold:
                    return False
            elif value == self._telemetry_cache[message_type]:
                return False
        
        # Wert und Zeit speichern
        self._telemetry_cache[message_type] = value
        self._last_message_time[message_type] = current_time
        
        return True
