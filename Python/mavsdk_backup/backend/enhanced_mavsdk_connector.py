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


class EnhancedMAVSDKConnector(QObject): # Nur QObject als Basisklasse verwenden, kein Interface-Mehrfachvererbung
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
        
        # Signal-Hub für die Drohnen-Kommunikation
        from rzgcs.mvvm.drone_signal_hub import DroneSignalHub
        self._signals = DroneSignalHub()
        
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
                           oder "serial:port:baudrate" oder "COM8:115200"
        
        Returns:
            bool: True, wenn die Verbindung erfolgreich gestartet wurde
        """
        if not connection_string:
            self._logger.addLog("[FEHLER] Kein Verbindungsstring angegeben")
            return False
            
        self._connection_string = connection_string
        self._logger.addLog(f"[INFO] Versuche Verbindung mit: {connection_string}")
        
        # Verbesserte Verbindungsformat-Erkennung
        # Format 1: COM8:115200 oder /dev/ttyACM0:115200 (einfacher COM-Port mit Baudrate)
        if ":" in connection_string and not any(connection_string.startswith(p) for p in ["serial:", "udp:", "tcp:"]):
            parts = connection_string.split(":")
            port = parts[0]
            baudrate = 115200  # Neue Standard-Baudrate gemäß Anforderung
            
            if len(parts) >= 2:
                try:
                    baudrate = int(parts[1])
                except ValueError:
                    self._logger.addLog(f"[WARNUNG] Ungültige Baudrate {parts[1]}, verwende 115200")
            
            self._logger.addLog(f"[INFO] Verbinde mit COM-Port {port} bei {baudrate} Baud")
            return self.connect_serial(port, baudrate)
            
        # Format 2: COM8 oder /dev/ttyACM0 (nur COM-Port, Standard-Baudrate)
        elif connection_string.startswith("COM") or "/dev" in connection_string:
            self._logger.addLog(f"[INFO] Verbinde mit COM-Port {connection_string} bei 115200 Baud (Standard)")
            return self.connect_serial(connection_string, 115200)
        
        # Format 3: serial:port:baudrate (altes Format)
        elif connection_string.startswith("serial:"):
            # Format: serial:port:baudrate
            parts = connection_string.split(":")
            if len(parts) < 2:
                self._logger.addLog("[FEHLER] Ungültiger serieller Verbindungsstring")
                return False
                
            port = parts[1]
            baudrate = 115200  # Neue Standard-Baudrate gemäß Anforderung
            
            if len(parts) >= 3:
                try:
                    baudrate = int(parts[2])
                except ValueError:
                    self._logger.addLog(f"[WARNUNG] Ungültige Baudrate {parts[2]}, verwende 115200")
            
            return self.connect_serial(port, baudrate)
        
        # Format 4: udp:/tcp: Verbindungen
        elif connection_string.startswith("udp:") or connection_string.startswith("tcp:"):
            # UDP/TCP-Verbindung
            try:
                # Thread starten
                self._stop_event.clear()
                self._thread = MAVSDKThread(self._run)
                self._thread.start()
                
                # Verbindungsstring weitergeben
                self._server_controller.start_server(connection_string)
                
                self._logger.addLog(f"[INFO] Verbindung zu {connection_string} gestartet")
                return True
            except Exception as e:
                self._logger.addLog(f"[FEHLER] Konnte keine Verbindung herstellen: {str(e)}")
                self._signals.error_occurred.emit(f"Verbindungsfehler: {str(e)}")
                return False
        else:
            # Unbekanntes Format - versuche als seriellen Port zu interpretieren
            self._logger.addLog(f"[INFO] Versuche unbekanntes Format als COM-Port: {connection_string}")
            try:
                return self.connect_serial(connection_string, 115200)
            except Exception as e:
                error_msg = f"[FEHLER] Unbekanntes Verbindungsformat: {connection_string} - {str(e)}"
                self._logger.addLog(error_msg)
                self._signals.error_occurred.emit(error_msg)
                return False
    
    def connect_serial(self, port: str, baudrate: int) -> bool:
        """
        Verbindet mit einer Drohne über einen seriellen Port
        
        Args:
            port: COM-Port oder Device (z.B. COM3, /dev/ttyACM0)
            baudrate: Baudrate (z.B. 57600, 115200)
            
        Returns:
            bool: True, wenn die Verbindung erfolgreich gestartet wurde
        """
        # Speichere den Verbindungsstring im korrekten Format
        self._connection_string = f"serial://{port}:{baudrate}"
        self._logger.addLog(f"[INFO] Starte Verbindung mit {port} bei {baudrate} Baud")
        
        # MAVSDK-Server starten
        if not self._server_controller.start_server(port, baudrate):
            error_msg = f"[FEHLER] MAVSDK-Server konnte nicht gestartet werden für {port}:{baudrate}"
            self._logger.addLog(error_msg)
            self._signals.error_occurred.emit(error_msg)
            return False
            
        # Kurz warten, bis der Server gestartet ist (erweiterte Wartezeit für mehr Stabilität)
        wait_time = 2.0
        self._logger.addLog(f"[INFO] Warte {wait_time} Sekunden, bis der MAVSDK-Server initialisiert ist")
        time.sleep(wait_time)
        
        try:
            # Thread für die Verbindung starten
            self._stop_event.clear()
            self._thread = MAVSDKThread(self._run)
            self._thread.start()
            
            self._logger.addLog(f"[INFO] MAVSDK-Thread gestartet, warte auf Verbindungsbestätigung")
            return True
        except Exception as e:
            error_msg = f"[FEHLER] Konnte MAVSDK-Thread nicht starten: {str(e)}"
            self._logger.addLog(error_msg)
            self._signals.error_occurred.emit(error_msg)
            return False
    
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
            self._logger.addLog(f"[INFO] Verbinde mit Drohne über {self._connection_string}")
            await self._drone.connect(system_address=self._connection_string)
            
            # Verbesserte Verbindungsprüfung mit Timeout
            connection_established = False
            connection_timeout = 15  # Sekunden
            start_time = time.time()
            
            self._logger.addLog("[INFO] Prüfe Verbindungsstatus mit mehreren Methoden...")
            
            # Versuche verschiedene Methoden, um die Verbindung zu prüfen
            while time.time() - start_time < connection_timeout and not connection_established:
                # Methode 1: Connection State prüfen (traditionelle Methode)
                try:
                    async for state in self._drone.core.connection_state():
                        if state.is_connected:
                            self._logger.addLog("[INFO] Verbindung hergestellt (via connection_state)")
                            connection_established = True
                            break
                        await asyncio.sleep(0.2)  # Nicht zu häufig prüfen
                        if time.time() - start_time >= connection_timeout:
                            break
                except Exception:
                    # Wenn die erste Methode fehlschlägt, versuchen wir andere
                    pass
                
                if not connection_established:
                    # Methode 2: Version abfragen
                    try:
                        self._logger.addLog("[INFO] Prüfe Verbindung durch Versionsabfrage...")
                        version = await self._drone.info.get_version()
                        self._logger.addLog(f"[INFO] Firmware Version: {version.firmware_version}")
                        connection_established = True
                    except Exception as e:
                        self._logger.addLog(f"[INFO] Versionsabfrage fehlgeschlagen: {str(e)}")
                
                if not connection_established:
                    # Methode 3: Identifikation abfragen
                    try:
                        self._logger.addLog("[INFO] Prüfe Verbindung durch Identifikationsabfrage...")
                        ident = await self._drone.info.get_identification()
                        self._logger.addLog(f"[INFO] Hardware UID: {ident.hardware_uid}")
                        connection_established = True
                    except Exception as e:
                        self._logger.addLog(f"[INFO] Identifikationsabfrage fehlgeschlagen: {str(e)}")
                
                # Kurz warten vor dem nächsten Versuch
                if not connection_established:
                    await asyncio.sleep(0.5)
            
            # Prüfen, ob die Verbindung erfolgreich war
            if connection_established:
                self._is_connected = True
                self._signals.connection_established.emit()
                self.connected.emit() # Für Abwärtskompatibilität
                self._logger.addLog("[INFO] Verbindung zur Drohne vollständig hergestellt")
                
                # Telemetrie-Subscriptions starten
                await self._start_telemetry_subscriptions()
                
                # Systeminformationen abfragen (für Preflight-View)
                await self._request_system_info()
                
                # Warte auf Stop-Event
                while not self._stop_event.is_set():
                    await asyncio.sleep(0.1)
            else:
                error_msg = "Timeout bei Verbindungsversuch"
                self._logger.addLog(f"[FEHLER] {error_msg}")
                self._signals.error_occurred.emit(error_msg)
                self.error_occurred.emit(error_msg) # Für Abwärtskompatibilität
                
        except Exception as e:
            error_msg = f"MAVSDK-Fehler: {str(e)}"
            self._logger.addLog(f"[FEHLER] {error_msg}")
            self._signals.error_occurred.emit(error_msg)
            self.error_occurred.emit(error_msg) # Für Abwärtskompatibilität
            
        finally:
            # Verbindung trennen
            if self._is_connected:
                self._is_connected = False
                self._signals.connection_lost.emit()
                self.disconnected.emit() # Für Abwärtskompatibilität
                
            # MAVSDK-Server herunterfahren
            try:
                # In neueren MAVSDK-Versionen "shutdown" verwenden
                await self._drone.core.shutdown()
            except AttributeError:
                # In älteren Versionen "dispose"
                try:
                    await self._drone.dispose()
                except Exception:
                    # Wenn nichts funktioniert, ignorieren - der MAVSDK-Server wird trotzdem beendet
                    pass
                    
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
                # Status-Änderung melden (beide Signalwege)
                self.armed_changed.emit(armed)  # Alter Signalweg für Abwärtskompatibilität
                self._signals.armed_changed.emit(armed)  # Neuer Signal-Hub
                
                # Bei Änderung loggen
                if self._should_emit_message('armed', armed):
                    self._logger.addLog(f"[INFO] Armed-Status: {'ARMED' if armed else 'DISARMED'}")
                    
        except Exception as e:
            error_msg = f"Fehler beim Überwachen des Armed-Status: {str(e)}"
            self._logger.addLog(f"[FEHLER] {error_msg}")
            self._signals.error_occurred.emit(error_msg)
    
    async def _monitor_flight_mode(self):
        """
        Überwacht den Flugmodus
        """
        try:
            async for flight_mode in self._drone.telemetry.flight_mode():
                mode_str = str(flight_mode)
                
                # Status-Änderung melden (beide Signalwege)
                self.flight_mode_changed.emit(mode_str)  # Alter Signalweg für Abwärtskompatibilität
                self._signals.flight_mode_changed.emit(mode_str)  # Neuer Signal-Hub
                
                # Bei Änderung loggen
                if self._should_emit_message('flight_mode', mode_str):
                    self._logger.addLog(f"[INFO] Flugmodus: {mode_str}")
                    
        except Exception as e:
            error_msg = f"Fehler beim Überwachen des Flugmodus: {str(e)}"
            self._logger.addLog(f"[FEHLER] {error_msg}")
            self._signals.error_occurred.emit(error_msg)
    
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
                
                # Status-Änderung melden (beide Signalwege)
                self.gps_info_changed.emit(info)  # Alter Signalweg für Abwärtskompatibilität
                self._signals.gps_info_changed.emit(info)  # Neuer Signal-Hub
                
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
                    'voltage_v': battery.voltage_v,
                    'remaining_percent': battery.remaining_percent,
                    'warning': {
                        'low_battery': False,  # Standardwert
                        'critical': False      # Standardwert
                    }
                }
                
                # Warnungen ermitteln
                if battery.remaining_percent < 20.0:
                    info['warning']['low_battery'] = True
                if battery.remaining_percent < 10.0:
                    info['warning']['critical'] = True
                
                # Status-Änderung melden (beide Signalwege)
                self.battery_changed.emit(info)  # Alter Signalweg für Abwärtskompatibilität
                self._signals.battery_changed.emit(info)  # Neuer Signal-Hub
                
                # Bei Änderung loggen
                if self._should_emit_message('battery', info['remaining_percent']):
                    self._logger.addLog(f"[INFO] Batterie: {info['remaining_percent']:.1f}%")
                    
        except Exception as e:
            error_msg = f"Fehler beim Überwachen des Batteriestatus: {str(e)}"
            self._logger.addLog(f"[FEHLER] {error_msg}")
            self._signals.error_occurred.emit(error_msg)
    
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
                
                # Status-Änderung melden (beide Signalwege)
                self.attitude_changed.emit(info)  # Alter Signalweg für Abwärtskompatibilität
                self._signals.attitude_changed.emit(info)  # Neuer Signal-Hub
                
                # Heading separat melden
                self.heading_changed.emit(attitude.yaw_deg)  # Alter Signalweg
                self._signals.heading_changed.emit(attitude.yaw_deg)  # Neuer Signal-Hub
                
                # Bei signifikanter Änderung des Headings loggen
                if self._should_emit_message('heading', attitude.yaw_deg):
                    self._logger.addLog(f"[INFO] Heading: {attitude.yaw_deg:.1f}\u00b0")
                    
        except Exception as e:
            error_msg = f"Fehler beim Überwachen der Lage: {str(e)}"
            self._logger.addLog(f"[FEHLER] {error_msg}")
            self._signals.error_occurred.emit(error_msg)
    
    async def _monitor_position(self):
        """
        Überwacht die Position der Drohne
        """
        try:
            async for position in self._drone.telemetry.position():
                # Position als Dictionary mit Fehlerbehandlung
                try:
                    info = {
                        'latitude_deg': position.latitude_deg,
                        'longitude_deg': position.longitude_deg,
                        'absolute_altitude_m': position.absolute_altitude_m,
                        'relative_altitude_m': position.relative_altitude_m
                    }
                    
                    # Status-Änderung melden (beide Signalwege)
                    self.position_changed.emit(info)  # Alter Signalweg für Abwärtskompatibilität
                    self._signals.position_changed.emit(info)  # Neuer Signal-Hub
                    
                    # Bei Änderung der Höhe loggen
                    if self._should_emit_message('altitude', info['relative_altitude_m']):
                        self._logger.addLog(f"[INFO] Höhe: {info['relative_altitude_m']:.1f}m")
                except AttributeError as e:
                    # Fehlerbehandlung für fehlende Attribute (argument out of range Fehler)
                    self._logger.addLog(f"[WARNUNG] Position-Daten unvollständig: {str(e)}")
                except Exception as e:
                    self._logger.addLog(f"[WARNUNG] Fehler bei Position-Verarbeitung: {str(e)}")
        except Exception as e:
            error_msg = f"Fehler beim Überwachen der Position: {str(e)}"
            self._logger.addLog(f"[FEHLER] {error_msg}")
            self._signals.error_occurred.emit(error_msg)
    
    async def _monitor_home_position(self):
        """
        Überwacht die Home-Position der Drohne
        """
        try:
            async for position in self._drone.telemetry.home():
                try:
                    # Home-Position als Dictionary
                    info = {
                        'latitude_deg': position.latitude_deg,
                        'longitude_deg': position.longitude_deg,
                        'absolute_altitude_m': position.absolute_altitude_m,
                        'relative_altitude_m': position.relative_altitude_m
                    }
                    
                    # Status-Änderung melden (beide Signalwege)
                    self.home_position_changed.emit(info)  # Alter Signalweg für Abwärtskompatibilität
                    self._signals.home_position_changed.emit(info)  # Neuer Signal-Hub
                    
                except AttributeError as e:
                    # Fehlerbehandlung für fehlende Attribute
                    self._logger.addLog(f"[WARNUNG] Home-Position unvollständig: {str(e)}")
                except Exception as e:
                    self._logger.addLog(f"[WARNUNG] Fehler bei Home-Position-Verarbeitung: {str(e)}")
                
        except Exception as e:
            error_msg = f"Fehler beim Überwachen der Home-Position: {str(e)}"
            self._logger.addLog(f"[FEHLER] {error_msg}")
            self._signals.error_occurred.emit(error_msg)
    
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
                    "PreArm", "RCOut", "Firmware", "Version", "APM", "Arducopter",
                    "PX4", "MAVSDK", "INS", "Motor", "Battery", "GPS", "EKF", "Compass"
                ]
                
                for pattern in system_info_patterns:
                    if pattern in text:
                        is_system_info = True
                        break
                
                # Systeminformationen markieren und formatieren
                if is_system_info and not text.startswith("[SYSTEM INFO]"):
                    text = f"[SYSTEM INFO] {text}"
                
                # Status-Änderung melden (beide Signalwege)
                self.statustext_received.emit(text)  # Alter Signalweg für Abwärtskompatibilität
                self._signals.statustext_received.emit(text)  # Neuer Signal-Hub
                
                # Immer loggen
                if self._should_emit_message('statustext', text):
                    self._logger.addLog(text)
                    
        except Exception as e:
            error_msg = f"Fehler beim Überwachen der Status-Texte: {str(e)}"
            self._logger.addLog(f"[FEHLER] {error_msg}")
            self._signals.error_occurred.emit(error_msg)
    
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
