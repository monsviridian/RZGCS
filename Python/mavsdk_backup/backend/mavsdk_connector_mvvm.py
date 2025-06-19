#!/usr/bin/env python3
"""
MAVSDK Connector für MVVM-Architektur
Verbindet die MAVSDK mit der RZGCS-Anwendung unter Beibehaltung einer sauberen MVVM-Architektur
"""

import sys
import time
import json
import asyncio
import threading
import subprocess
import math
from typing import Dict, Any, List, Optional, Tuple, Callable, Any, Optional

from PySide6.QtCore import QObject, Signal, Slot, Property

try:
    from mavsdk import System
    from mavsdk.telemetry import FlightMode, LandedState
except ImportError:
    print("MAVSDK nicht installiert!")
    print("Installiere mit: pip install mavsdk")
    sys.exit(1)


class MAVSDKSignals(QObject):
    """Signale für die Kommunikation zwischen MAVSDK und QML-UI"""
    
    # Telemetrie-Signale (neue Namen)
    battery_updated = Signal(dict)          # Batteriestatus (remaining_percent, voltage_v, current_a)
    attitude_updated = Signal(dict)         # Lage (roll_deg, pitch_deg, yaw_deg)
    position_updated = Signal(dict)         # Position (latitude_deg, longitude_deg, absolute_altitude_m, relative_altitude_m)
    gps_info_updated = Signal(dict)         # GPS-Info (num_satellites, fix_type)
    flight_mode_changed = Signal(str)       # Flugmodus als String
    armed_state_changed = Signal(bool)      # Armed-Status (True/False)
    
    # Verbindungssignale (neue Namen)
    connection_state_changed = Signal(bool) # Verbindungsstatus (True/False)
    
    # Legacy-Signale für Kompatibilität mit bestehendem Code
    battery_changed = Signal(dict)          # Alias für battery_updated
    attitude_changed = Signal(dict)         # Alias für attitude_updated
    position_changed = Signal(dict)         # Alias für position_updated
    gps_info_changed = Signal(dict)         # Alias für gps_info_updated 
    armed_changed = Signal(bool)            # Alias für armed_state_changed
    connection_established = Signal()       # Wird emittiert, wenn connection_state_changed(True)
    connection_lost = Signal()              # Wird emittiert, wenn connection_state_changed(False)
    
    # Parameter-Signale
    parameters_updated = Signal(list)       # Parameter-Liste
    
    # Erweiterte Telemetrie-Signale
    in_air_changed = Signal(bool)           # In-Air-Status (True = in der Luft, False = am Boden)
    health_updated = Signal(dict)           # Gesundheitsstatus der Drohne (detailliert)
    health_all_ok_changed = Signal(bool)    # Gesamtgesundheitsstatus (True = alles OK, False = Probleme)
    
    # Zusätzliche Telemetrie-Signale
    angular_velocity_updated = Signal(dict)    # Winkelgeschwindigkeit (roll_rad_s, pitch_rad_s, yaw_rad_s)
    status_text_received = Signal(dict)        # Statustext (text, type)
    actuator_control_updated = Signal(dict)    # Aktuator-Kontrolle (group, controls)
    actuator_output_updated = Signal(dict)     # Aktuator-Ausgabe (active, actuator)
    odometry_updated = Signal(dict)           # Odometrie-Daten (position, velocity, etc.)
    distance_sensor_updated = Signal(dict)     # Abstandssensor-Daten (min, max, current)
    scaled_pressure_updated = Signal(dict)     # Skalierter Druck (temperature, abs_pressure, diff_pressure)
    heading_updated = Signal(float)            # Heading (Kompass) in Grad
    altitude_updated = Signal(dict)           # Höheninformationen (rel, abs, agl)
    landed_state_changed = Signal(str)        # Landezustand (ON_GROUND, IN_AIR, TAKING_OFF, LANDING)
    rc_status_updated = Signal(dict)          # RC-Status (available, signal_strength)
    unix_epoch_time_updated = Signal(int)     # Unix-Epochenzeit in µs
    raw_imu_updated = Signal(dict)            # Rohe IMU-Daten (Beschleunigung, Gyro, Temp)
    
    def __init__(self, parent=None):
        super().__init__(parent)

from backend.logger import Logger
from backend.mavsdk_server_controller import MAVSDKServerController
from backend.drone_signal_hub import DroneSignalHub
from backend.exceptions import ConnectionError, ConnectionTimeoutError


class MAVSDKConnectorMVVM(QObject):
    """
    MAVSDK-Connector für MVVM-Architektur
    
    Diese Implementierung vermeidet Metaklassen-Konflikte und bietet eine saubere
    Schnittstelle für die ViewModels.
    """
    
    def __init__(self, logger: Logger, parent=None):
        """Initialisierung des MAVSDKConnectorMVVM"""
        super().__init__(parent)
        
        # Signale für die Kommunikation mit der UI
        self.signals = MAVSDKSignals(self)
        
        # Logger
        self._logger = logger
        
        # Signal-Hub erstellen (vermeidet Metaklassen-Konflikte)
        self.signals = DroneSignalHub(self)
        
        # Callback-Speicher
        self._connection_callbacks = []
        self._disconnection_callbacks = []
        self._telemetry_callbacks = {}
        self._statustext_callbacks = []
        
        # MAVSDK-System
        self._drone = System()
        self._mission_raw = None
        
        # Status
        self._is_connected = False
        self._connection_string = ""
        
        # Server-Controller für den MAVSDK-Server
        self._server_controller = MAVSDKServerController(self._logger)
        
        # Thread und Event-Loop
        self._thread = None
        self._stop_event = threading.Event()
        self._loop = None
        
        # Konfiguration
        self._server_port = 50051
        self._server_backend = "backend-tcp"
        
        # Message-Filter-Konfiguration (speziell für die Preflight-View)
        self._last_message_values = {}
        self._last_message_times = {}
        self._message_thresholds = {
            'heading': 5.0,  # Heading-Änderung in Grad
            'altitude': 0.5,  # Höhenänderung in Metern
            'battery': 1.0,   # Batterie-Änderung in Prozent
            'armed': 1,        # Armed-Status (jede Änderung ist signifikant)
            'flight_mode': 1,  # Flugmodus (jede Änderung ist signifikant)
            'gps': 1           # GPS-Status (jede Änderung ist signifikant)
        }
        self._min_message_interval_seconds = {
            'heading': 1.0,    # Mind. 1 Sekunde zwischen Heading-Meldungen
            'altitude': 1.0,   # Mind. 1 Sekunde zwischen Höhen-Meldungen
            'battery': 5.0,    # Mind. 5 Sekunden zwischen Batterie-Meldungen
            'armed': 0.0,      # Keine Mindestzeit für Armed-Status
            'flight_mode': 0.0, # Keine Mindestzeit für Flugmodus
            'gps': 2.0         # Mind. 2 Sekunden zwischen GPS-Status-Meldungen
        }
    
    # Callback-Registrierungsmethoden
    
    def register_connection_callback(self, callback: Callable[[], None]) -> None:
        """Registriert einen Callback für Verbindungs-Status-Änderungen"""
        if callback not in self._connection_callbacks:
            self._connection_callbacks.append(callback)
    
    def register_disconnection_callback(self, callback: Callable[[], None]) -> None:
        """Registriert einen Callback für Verbindungs-Verlust"""
        if callback not in self._disconnection_callbacks:
            self._disconnection_callbacks.append(callback)
    
    def register_telemetry_callback(self, telemetry_type: str, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Registriert einen Callback für einen bestimmten Telemetrie-Typ
        
        Args:
            telemetry_type: Typ der Telemetrie (z.B. 'position', 'attitude', 'battery')
            callback: Funktion, die aufgerufen wird, wenn neue Daten verfügbar sind
        """
        if telemetry_type not in self._telemetry_callbacks:
            self._telemetry_callbacks[telemetry_type] = []
            
        if callback not in self._telemetry_callbacks[telemetry_type]:
            self._telemetry_callbacks[telemetry_type].append(callback)
    
    def register_statustext_callback(self, callback: Callable[[str], None]) -> None:
        """Registriert einen Callback für Status-Texte"""
        if callback not in self._statustext_callbacks:
            self._statustext_callbacks.append(callback)
    
    # Callback-Trigger-Methoden
    
    def _trigger_connection_callbacks(self) -> None:
        """Ruft alle registrierten Verbindungs-Callbacks auf"""
        for callback in self._connection_callbacks:
            try:
                callback()
            except Exception as e:
                self._logger.addLog(f"[FEHLER] Fehler beim Ausführen eines Connection-Callbacks: {str(e)}")
    
    def _trigger_disconnection_callbacks(self) -> None:
        """Ruft alle registrierten Disconnection-Callbacks auf"""
        for callback in self._disconnection_callbacks:
            try:
                callback()
            except Exception as e:
                self._logger.addLog(f"[FEHLER] Fehler beim Ausführen eines Disconnection-Callbacks: {str(e)}")
    
    def _trigger_telemetry_callbacks(self, telemetry_type: str, data: Dict[str, Any]) -> None:
        """Ruft alle registrierten Telemetrie-Callbacks für einen bestimmten Typ auf"""
        if telemetry_type in self._telemetry_callbacks:
            for callback in self._telemetry_callbacks[telemetry_type]:
                try:
                    # Füge den Telemetrie-Typ zum Dict hinzu, damit der Empfänger weiß, worum es geht
                    data_with_type = data.copy() if isinstance(data, dict) else {'value': data}
                    data_with_type['type'] = telemetry_type
                    callback(data_with_type)
                except Exception as e:
                    self._logger.addLog(f"[FEHLER] Fehler beim Ausführen eines Telemetrie-Callbacks ({telemetry_type}): {str(e)}")
    
    def _trigger_statustext_callbacks(self, text: str) -> None:
        """Ruft alle registrierten Statustext-Callbacks auf"""
        for callback in self._statustext_callbacks:
            try:
                callback(text)
            except Exception as e:
                self._logger.addLog(f"[FEHLER] Fehler beim Ausführen eines Statustext-Callbacks: {str(e)}")
    
    # Verbindungsmethoden
    
    def connect_to_running_server(self, server_port: int = 50051) -> bool:
        """Verbindet zu einem bereits laufenden MAVSDK-Server
        
        Args:
            server_port: Port des laufenden MAVSDK-Servers (Standard: 50051)
            
        Returns:
            bool: True, wenn die Verbindung erfolgreich hergestellt wurde
        """
        if self._is_connected:
            self._logger.addLog("[WARNUNG] Bereits verbunden, bitte zuerst trennen")
            return False
            
        self._connection_string = f"tcp://localhost:{server_port}"
        self._logger.addLog(f"[INFO] Verbinde mit {self._connection_string}...")
        
        try:
            # Event-Loop und Thread erstellen
            self._stop_event.clear()
            self._loop = asyncio.new_event_loop()
            
            # Thread mit der speziellen Funktion für externe Server starten
            self._thread = threading.Thread(
                target=self._run_external_server_connection_loop, 
                args=(server_port,)
            )
            self._thread.daemon = True
            self._thread.start()
            
            return True
        except Exception as e:
            error_msg = f"[FEHLER] Fehler beim Verbinden mit MAVSDK-Server auf Port {server_port}: {str(e)}"
            self._logger.addLog(error_msg)
            self.signals.error_occurred.emit(error_msg)
            return False
    
    def connect(self, connection_string: str) -> bool:
        """Stellt eine Verbindung zur Drohne her
        
        Args:
            connection_string: Verbindungsstring (z.B. 'udp://:14540')
        
        Returns:
            bool: True, wenn die Verbindung erfolgreich hergestellt wurde
        """
        if self._is_connected:
            self._logger.addLog("[WARNUNG] Bereits verbunden, bitte zuerst trennen")
            return False
        
        self._connection_string = connection_string
        self._logger.addLog(f"[INFO] Verbinde mit {connection_string}")
        
        try:
            # Event-Loop und Thread erstellen
            self._stop_event.clear()
            self._loop = asyncio.new_event_loop()
            self._thread = threading.Thread(target=self._run_connection_loop, args=(connection_string,))
            self._thread.daemon = True
            self._thread.start()
            
            return True
        except Exception as e:
            error_msg = f"[FEHLER] Fehler beim Verbinden mit {connection_string}: {str(e)}"
            self._logger.addLog(error_msg)
            self.signals.error_occurred.emit(error_msg)
            return False
    
    def connect_serial(self, port: str, baudrate: int) -> bool:
        """Stellt eine Verbindung zur Drohne über einen seriellen Port her
        
        Args:
            port: COM-Port oder Device (z.B. COM3, /dev/ttyACM0)
            baudrate: Baudrate (z.B. 115200)
        
        Returns:
            bool: True, wenn die Verbindung erfolgreich hergestellt wurde
        """
        if self._is_connected:
            self._logger.addLog("[WARNUNG] Bereits verbunden, bitte zuerst trennen")
            return False
        
        # MAVSDK-Server starten
        try:
            self._logger.addLog(f"[INFO] Starte MAVSDK-Server für {port} mit {baudrate} Baud")
            # Starte den MAVSDK-Server mit dynamischem Port
            success, server_port = self._server_controller.start_server(
                port=port,
                baudrate=baudrate
            )
            
            if not success or server_port is None:
                error_msg = "MAVSDK-Server konnte nicht gestartet werden"
                self._logger.addLog(f"[FEHLER] {error_msg}")
                self.signals.error_occurred.emit(error_msg)
                self._logger.addLog(f"[SYSTEM INFO] MAVSDK-Server konnte nicht gestartet werden für {port}")
                return False
            
            # Mit dem MAVSDK-Server auf dem dynamischen Port verbinden
            self._logger.addLog(f"[INFO] Verbinde mit lokalem MAVSDK-Server auf Port {server_port}")
            return self.connect_to_running_server(server_port)
            
        except Exception as e:
            error_msg = f"[FEHLER] Fehler beim Verbinden mit {port}: {str(e)}"
            self._logger.addLog(error_msg)
            self.signals.error_occurred.emit(error_msg)
            return False
    
    def disconnect(self) -> bool:
        """Trennt die Verbindung zur Drohne
        
        Returns:
            bool: True, wenn die Verbindung erfolgreich getrennt wurde
        """
        if not self._is_connected:
            self._logger.addLog("[WARNUNG] Nicht verbunden")
            return False
        
        try:
            # Event-Loop beenden
            self._stop_event.set()
            
            # Thread beenden, falls aktiv
            if self._thread and self._thread.is_alive():
                self._thread.join(timeout=3.0)
            
            # MAVSDK-Server beenden
            self._server_controller.stop_server()
            
            # Status zurücksetzen
            self._is_connected = False
            self._connection_string = ""
            
            # Signal senden
            self.signals.connection_lost.emit()
            self._trigger_disconnection_callbacks()
            
            self._logger.addLog("[INFO] Verbindung zur Drohne getrennt")
            return True
            
        except Exception as e:
            error_msg = f"[FEHLER] Fehler beim Trennen der Verbindung: {str(e)}"
            self._logger.addLog(error_msg)
            self.signals.error_occurred.emit(error_msg)
            return False
    
    def get_parameters(self):
        """Lädt alle Parameter vom Flight Controller
        
        Fügt einen Task zur bestehenden MAVSDK Event-Loop hinzu, um die Parameter abzurufen.
        
        Returns:
            bool: True, wenn der Abrufprozess gestartet wurde
        """
        if not self._is_connected or not self._drone:
            self._logger.addLog("[WARNUNG] Nicht verbunden - kann keine Parameter abrufen")
            return False
            
        self._logger.addLog("[INFO] Starte Parameter-Abruf...")
        
        # Verwende die bereits existierende MAVSDK-Loop
        if self._loop and not self._loop.is_closed():
            try:
                # Füge den Task zur bestehenden Event-Loop hinzu
                asyncio.run_coroutine_threadsafe(self._get_parameters_in_existing_loop(), self._loop)
                return True
            except Exception as e:
                self._logger.addLog(f"[FEHLER] Fehler beim Abrufen der Parameter: {str(e)}")
                return False
        else:
            self._logger.addLog("[FEHLER] Keine aktive Event-Loop für MAVSDK gefunden")
            return False
    
    async def _get_parameters_in_existing_loop(self):
        """Asynchrone Funktion zum Abrufen aller Parameter in der bestehenden Event-Loop"""
        try:
            self._logger.addLog("[INFO] Rufe Parameter in der MAVSDK-Loop ab...")
            
            # Hole alle Parameter
            params = await self._get_params_safe()
            
            # Emittiere das Signal mit den Parametern
            if params:
                self.signals.parameters_updated.emit(params)
                
            return True
        except Exception as e:
            self._logger.addLog(f"[FEHLER] Fehler beim Abrufen der Parameter in der MAVSDK-Loop: {str(e)}")
            return False
    
    async def _get_params_safe(self):
        """Sicherer Parameter-Abruf in der bestehenden Event-Loop"""
        try:
            # Prüfe, ob das Drone-Objekt bereit ist
            if not self._drone:
                self._logger.addLog("[FEHLER] Kein Drone-Objekt verfügbar")
                return None

            # Alle Parameter abrufen
            all_params = await self._drone.param.get_all_params()
            
            # Parameter in eine Liste und ein Wörterbuch umwandeln
            param_list = []
            param_dict = {}
            
            # Int-Parameter hinzufügen
            for param in all_params.int_params:
                param_info = {
                    "name": param.name,
                    "value": param.value,
                    "type": "int",
                    "description": "",  # PX4/Ardupilot Parameter haben oft Beschreibungen, aber nicht direkt in MAVSDK verfügbar
                    "min": None,        # Minimaler Wert, falls bekannt
                    "max": None,        # Maximaler Wert, falls bekannt
                    "editable": True    # Ob der Parameter über die UI bearbeitet werden kann
                }
                param_list.append(param_info)
                param_dict[param.name] = param_info
            
            # Float-Parameter hinzufügen
            for param in all_params.float_params:
                param_info = {
                    "name": param.name,
                    "value": param.value,
                    "type": "float",
                    "description": "", 
                    "min": None,        
                    "max": None,        
                    "editable": True    
                }
                param_list.append(param_info)
                param_dict[param.name] = param_info
            
            # Speichere das Parameter-Wörterbuch für schnellen Zugriff
            self._parameter_dict = param_dict
                
            # Log-Nachricht
            self._logger.addLog(f"[INFO] {len(param_list)} Parameter erfolgreich abgerufen")
            return param_list
            
        except Exception as e:
            self._logger.addLog(f"[FEHLER] Fehler beim Parameterzugriff: {str(e)}")
            return None
    
    async def _get_parameters_async(self):
        """Asynchrone Funktion zum Abrufen aller Parameter"""
        try:
            # Warten, bis das Drone-Objekt bereit ist
            if not self._drone:
                self._logger.addLog("[FEHLER] Kein Drone-Objekt verfügbar")
                return False
                
            self._logger.addLog("[INFO] Rufe Parameter vom Flight Controller ab...")
            
            # Parameter abrufen und als Signal senden
            param_list = await self._get_params_safe()
            if param_list:
                # Parameter-Signal emittieren
                self.signals.parameters_updated.emit(param_list)
                return True
            else:
                return False
                
        except Exception as e:
            error_msg = f"[FEHLER] Fehler beim asynchronen Abrufen der Parameter: {str(e)}"
            self._logger.addLog(error_msg)
            return False
            
    def set_parameter(self, name: str, value: Any, param_type: str = None) -> bool:
        """Setzt einen Parameter auf dem Flight Controller
        
        Args:
            name: Name des Parameters
            value: Neuer Parameterwert
            param_type: Typ des Parameters ('int', 'float', oder None für automatische Erkennung)
            
        Returns:
            bool: True, wenn der Parameter erfolgreich gesetzt wurde
        """
        if not self._is_connected or not self._drone:
            self._logger.addLog("[WARNUNG] Nicht verbunden - kann Parameter nicht setzen")
            return False
            
        self._logger.addLog(f"[INFO] Setze Parameter {name} auf {value}...")
        
        # Verwende die bereits existierende MAVSDK-Loop
        if self._loop and not self._loop.is_closed():
            try:
                # Füge den Task zur bestehenden Event-Loop hinzu
                future = asyncio.run_coroutine_threadsafe(
                    self._set_parameter_in_existing_loop(name, value, param_type), 
                    self._loop
                )
                # Auf das Ergebnis warten (mit Timeout)
                result = future.result(timeout=5.0)
                return result
            except Exception as e:
                self._logger.addLog(f"[FEHLER] Fehler beim Setzen des Parameters: {str(e)}")
                return False
        else:
            self._logger.addLog("[FEHLER] Keine aktive Event-Loop für MAVSDK gefunden")
            return False
            
    async def _set_parameter_in_existing_loop(self, name: str, value: Any, param_type: str = None):
        """Setzt einen Parameter in der bestehenden Event-Loop"""
        try:
            # Automatische Typerkennung, wenn kein Typ angegeben
            if param_type is None:
                # Wenn der Parameter bereits im Wörterbuch ist, verwende den bekannten Typ
                if hasattr(self, '_parameter_dict') and name in self._parameter_dict:
                    param_type = self._parameter_dict[name]["type"]
                # Sonst versuche den Parametertyp zu bestimmen
                elif isinstance(value, int) or (isinstance(value, str) and value.isdigit()):
                    param_type = "int"
                elif isinstance(value, float) or (isinstance(value, str) and '.' in value):
                    param_type = "float"
                else:
                    # Bei Unsicherheit als String behandeln
                    param_type = "custom"
                    
            # Parameter setzen basierend auf Typ
            if param_type == "int":
                # Ggf. String zu int konvertieren
                if isinstance(value, str):
                    value = int(value)
                    
                await self._drone.param.set_param_int(name, value)
                self._logger.addLog(f"[INFO] Int-Parameter {name} erfolgreich auf {value} gesetzt")
                
            elif param_type == "float":
                # Ggf. String zu float konvertieren
                if isinstance(value, str):
                    value = float(value)
                    
                await self._drone.param.set_param_float(name, value)
                self._logger.addLog(f"[INFO] Float-Parameter {name} erfolgreich auf {value} gesetzt")
                
            elif param_type == "custom":
                # Custom-Parameter als String setzen
                await self._drone.param.set_param_custom(name, str(value))
                self._logger.addLog(f"[INFO] Custom-Parameter {name} erfolgreich auf {value} gesetzt")
            
            # Nach dem Setzen die Parameter erneut abrufen, um die UI zu aktualisieren
            await self._get_parameters_in_existing_loop()
            return True
            
        except Exception as e:
            self._logger.addLog(f"[FEHLER] Fehler beim Setzen des Parameters {name}: {str(e)}")
            return False
    
    def is_connected(self) -> bool:
        """Gibt zurück, ob eine Verbindung zur Drohne besteht
        
        Returns:
            bool: True, wenn eine Verbindung besteht
        """
        return self._is_connected
    
    # Drohnensteuerungsmethoden
    
    def arm(self) -> bool:
        """Armiert die Drohne
        
        Returns:
            bool: True, wenn das Armieren erfolgreich war
        """
        if not self._is_connected:
            self._logger.addLog("[WARNUNG] Nicht verbunden")
            return False
        
        try:
            # Event-Loop erstellen
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Drohne armieren
            loop.run_until_complete(self._drone.action.arm())
            
            self._logger.addLog("[INFO] Drohne armiert")
            return True
            
        except Exception as e:
            error_msg = f"[FEHLER] Fehler beim Armieren: {str(e)}"
            self._logger.addLog(error_msg)
            self.signals.error_occurred.emit(error_msg)
            return False
    
    def disarm(self) -> bool:
        """Disarmiert die Drohne
        
        Returns:
            bool: True, wenn das Disarmieren erfolgreich war
        """
        if not self._is_connected:
            self._logger.addLog("[WARNUNG] Nicht verbunden")
            return False
        
        try:
            # Event-Loop erstellen
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Drohne disarmieren
            loop.run_until_complete(self._drone.action.disarm())
            
            self._logger.addLog("[INFO] Drohne disarmiert")
            return True
            
        except Exception as e:
            error_msg = f"[FEHLER] Fehler beim Disarmieren: {str(e)}"
            self._logger.addLog(error_msg)
            self.signals.error_occurred.emit(error_msg)
            return False
    
    def takeoff(self) -> bool:
        """Lässt die Drohne starten
        
        Returns:
            bool: True, wenn der Takeoff-Befehl erfolgreich gesendet wurde
        """
        if not self._is_connected:
            self._logger.addLog("[WARNUNG] Nicht verbunden")
            return False
        
        try:
            # Event-Loop erstellen
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Drohne starten
            loop.run_until_complete(self._drone.action.takeoff())
            
            self._logger.addLog("[INFO] Takeoff-Befehl gesendet")
            return True
            
        except Exception as e:
            error_msg = f"[FEHLER] Fehler beim Starten: {str(e)}"
            self._logger.addLog(error_msg)
            self.signals.error_occurred.emit(error_msg)
            return False
    
    def land(self) -> bool:
        """Lässt die Drohne landen
        
        Returns:
            bool: True, wenn der Land-Befehl erfolgreich gesendet wurde
        """
        if not self._is_connected:
            self._logger.addLog("[WARNUNG] Nicht verbunden")
            return False
        
        try:
            # Event-Loop erstellen
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Drohne landen
            loop.run_until_complete(self._drone.action.land())
            
            self._logger.addLog("[INFO] Land-Befehl gesendet")
            return True
            
        except Exception as e:
            error_msg = f"[FEHLER] Fehler beim Landen: {str(e)}"
            self._logger.addLog(error_msg)
            self.signals.error_occurred.emit(error_msg)
            return False
    
    # Hilfsmethoden
    
    def _run_external_server_connection_loop(self, server_port: int) -> None:
        """Führt die Verbindungsschleife für einen externen MAVSDK-Server aus
        
        Args:
            server_port: Port des laufenden MAVSDK-Servers
        """
        asyncio.set_event_loop(self._loop)
        self._loop.run_until_complete(self._run_external_server_connection(server_port))
    
    # Telemetrie-Monitor-Methoden
    
    async def _monitor_battery(self):
        """Überwacht den Batteriestatus"""
        try:
            self._logger.addLog("[INFO] Starte Batterie-Überwachung")
            prev_battery = None
            update_interval = 1.0  # Sekunden zwischen Updates
            
            async for battery in self._drone.telemetry.battery():
                # Prüfe, ob genug Zeit vergangen ist oder signifikante Änderung
                if prev_battery is None or \
                   abs(battery.remaining_percent - prev_battery.remaining_percent) > 1.0:
                    
                    battery_info = {
                        'remaining_percent': battery.remaining_percent,
                        'voltage_v': battery.voltage_v,
                        'current_a': battery.current_a
                    }
                    
                    # Status aktualisieren
                    self._logger.addLog(f"[DEBUG] Batterie: {battery.remaining_percent:.1f}% ({battery.voltage_v:.2f}V)")
                    
                    # Emittiere die verfügbaren Signale
                    try:
                        # Neues Signal (falls verfügbar)
                        if hasattr(self.signals, 'battery_updated'):
                            self.signals.battery_updated.emit(battery_info)
                        # Legacy-Signal (falls verfügbar)
                        if hasattr(self.signals, 'battery_changed'):
                            self.signals.battery_changed.emit(battery_info)
                    except Exception as e:
                        self._logger.addLog(f"[WARNUNG] Fehler beim Emittieren des Batteriestatus: {str(e)}")
                    
                    # Cache aktualisieren
                    prev_battery = battery
                
                # Prüfe, ob der Thread beendet werden soll
                if self._stop_event.is_set():
                    break
                    
                # Warte kurz, um nicht zu viel CPU zu verbrauchen
                await asyncio.sleep(update_interval)
                
        except asyncio.CancelledError:
            # Task wurde abgebrochen, normal beenden
            pass
        except Exception as e:
            self._logger.addLog(f"[FEHLER] Fehler bei Batterie-Überwachung: {str(e)}")
    
    async def _monitor_attitude(self):
        """Überwacht die Lage des Fluggeräts"""
        try:
            self._logger.addLog("[INFO] Starte Lage-Überwachung")
            prev_attitude = None
            update_interval = 0.2  # Sekunden zwischen Updates
            
            async for attitude in self._drone.telemetry.attitude_euler():
                # Signifikante Änderung prüfen (mehr als 1 Grad)
                if prev_attitude is None or \
                   abs(attitude.roll_deg - prev_attitude.roll_deg) > 1.0 or \
                   abs(attitude.pitch_deg - prev_attitude.pitch_deg) > 1.0 or \
                   abs(attitude.yaw_deg - prev_attitude.yaw_deg) > 1.0:
                    
                    attitude_info = {
                        'roll_deg': attitude.roll_deg,
                        'pitch_deg': attitude.pitch_deg,
                        'yaw_deg': attitude.yaw_deg
                    }
                    
                    # Status aktualisieren
                    self._logger.addLog(f"[DEBUG] Lage: Roll={attitude.roll_deg:.1f}°, Pitch={attitude.pitch_deg:.1f}°, Yaw={attitude.yaw_deg:.1f}°")
                    
                    # Emittiere die verfügbaren Signale
                    try:
                        # Neues Signal (falls verfügbar)
                        if hasattr(self.signals, 'attitude_updated'):
                            self.signals.attitude_updated.emit(attitude_info)
                        # Legacy-Signal (falls verfügbar)
                        if hasattr(self.signals, 'attitude_changed'):
                            self.signals.attitude_changed.emit(attitude_info)
                    except Exception as e:
                        self._logger.addLog(f"[WARNUNG] Fehler beim Emittieren der Lage-Daten: {str(e)}")
                    
                    # Cache aktualisieren
                    prev_attitude = attitude
                
                # Prüfe, ob der Thread beendet werden soll
                if self._stop_event.is_set():
                    break
                    
                # Warte kurz, um nicht zu viel CPU zu verbrauchen
                await asyncio.sleep(update_interval)
                
        except asyncio.CancelledError:
            # Task wurde abgebrochen, normal beenden
            pass
        except Exception as e:
            self._logger.addLog(f"[FEHLER] Fehler bei Lage-Überwachung: {str(e)}")
    
    async def _monitor_position(self):
        """Überwacht die Position des Fluggeräts"""
        try:
            self._logger.addLog("[INFO] Starte Positions-Überwachung")
            prev_position = None
            update_interval = 1.0  # Sekunden zwischen Updates
            
            async for position in self._drone.telemetry.position():
                # Signifikante Änderung prüfen (mehr als 0.5 Meter oder 0.5 m Höhe)
                if prev_position is None or \
                   self._calculate_distance(position, prev_position) > 0.5 or \
                   abs(position.relative_altitude_m - prev_position.relative_altitude_m) > 0.5:
                    
                    position_info = {
                        'latitude_deg': position.latitude_deg,
                        'longitude_deg': position.longitude_deg,
                        'absolute_altitude_m': position.absolute_altitude_m,
                        'relative_altitude_m': position.relative_altitude_m
                    }
                    
                    # Status aktualisieren
                    self._logger.addLog(f"[DEBUG] Position: Lat={position.latitude_deg:.6f}, Lon={position.longitude_deg:.6f}, Alt={position.relative_altitude_m:.1f}m")
                    
                    # Emittiere die verfügbaren Signale
                    try:
                        # Neues Signal (falls verfügbar)
                        if hasattr(self.signals, 'position_updated'):
                            self.signals.position_updated.emit(position_info)
                        # Legacy-Signal (falls verfügbar)
                        if hasattr(self.signals, 'position_changed'):
                            self.signals.position_changed.emit(position_info)
                    except Exception as e:
                        self._logger.addLog(f"[WARNUNG] Fehler beim Emittieren der Positionsdaten: {str(e)}")
                    
                    # Cache aktualisieren
                    prev_position = position
                
                # Prüfe, ob der Thread beendet werden soll
                if self._stop_event.is_set():
                    break
                    
                # Warte kurz, um nicht zu viel CPU zu verbrauchen
                await asyncio.sleep(update_interval)
                
        except asyncio.CancelledError:
            # Task wurde abgebrochen, normal beenden
            pass
        except Exception as e:
            self._logger.addLog(f"[FEHLER] Fehler bei Positions-Überwachung: {str(e)}")
    
    async def _monitor_gps_info(self):
        """Überwacht die GPS-Informationen"""
        try:
            self._logger.addLog("[INFO] Starte GPS-Info-Überwachung")
            prev_gps_info = None
            update_interval = 1.0  # Sekunden zwischen Updates
            
            async for gps_info in self._drone.telemetry.gps_info():
                # Änderung prüfen (Satellitenzahl oder Fix-Typ)
                if prev_gps_info is None or \
                   gps_info.num_satellites != prev_gps_info.num_satellites or \
                   gps_info.fix_type != prev_gps_info.fix_type:
                    
                    info = {
                        'num_satellites': gps_info.num_satellites,
                        'fix_type': gps_info.fix_type
                    }
                    
                    # Status aktualisieren
                    self._logger.addLog(f"[DEBUG] GPS: Sats={gps_info.num_satellites}, Fix={gps_info.fix_type}")
                    
                    # Emittiere die verfügbaren Signale
                    try:
                        # Neues Signal (falls verfügbar)
                        if hasattr(self.signals, 'gps_info_updated'):
                            self.signals.gps_info_updated.emit(info)
                        # Legacy-Signal (falls verfügbar)
                        if hasattr(self.signals, 'gps_info_changed'):
                            self.signals.gps_info_changed.emit(info)
                    except Exception as e:
                        self._logger.addLog(f"[WARNUNG] Fehler beim Emittieren der GPS-Daten: {str(e)}")
                    
                    # Cache aktualisieren
                    prev_gps_info = gps_info
                
                # Prüfe, ob der Thread beendet werden soll
                if self._stop_event.is_set():
                    break
                    
                # Warte kurz, um nicht zu viel CPU zu verbrauchen
                await asyncio.sleep(update_interval)
                
        except asyncio.CancelledError:
            # Task wurde abgebrochen, normal beenden
            pass
        except Exception as e:
            self._logger.addLog(f"[FEHLER] Fehler bei GPS-Info-Überwachung: {str(e)}")
    
    async def _monitor_flight_mode(self):
        """Überwacht den Flugmodus"""
        try:
            self._logger.addLog("[INFO] Starte Flugmodus-Überwachung")
            prev_flight_mode = None
            
            async for flight_mode in self._drone.telemetry.flight_mode():
                # Änderung prüfen
                if prev_flight_mode is None or flight_mode != prev_flight_mode:
                    mode_str = str(flight_mode)
                    
                    # Status aktualisieren
                    self._logger.addLog(f"[INFO] Flugmodus: {mode_str}")
                    
                    # Emittiere die verfügbaren Signale
                    try:
                        # Prüfe, ob das Signal verfügbar ist
                        if hasattr(self.signals, 'flight_mode_changed'):
                            self.signals.flight_mode_changed.emit(mode_str)
                    except Exception as e:
                        self._logger.addLog(f"[WARNUNG] Fehler beim Emittieren des Flugmodus: {str(e)}")
                    
                    # Cache aktualisieren
                    prev_flight_mode = flight_mode
                
                # Prüfe, ob der Thread beendet werden soll
                if self._stop_event.is_set():
                    break
                    
                # Warte kurz, um nicht zu viel CPU zu verbrauchen
                await asyncio.sleep(0.5)
                
        except asyncio.CancelledError:
            # Task wurde abgebrochen, normal beenden
            pass
        except Exception as e:
            self._logger.addLog(f"[FEHLER] Fehler bei Flugmodus-Überwachung: {str(e)}")
    
    async def _monitor_armed_state(self):
        """Überwacht den Armed-Status"""
        try:
            self._logger.addLog("[INFO] Starte Armed-Status-Überwachung")
            prev_armed = None
            
            async for armed in self._drone.telemetry.armed():
                # Änderung prüfen
                if prev_armed is None or armed != prev_armed:
                    # Status aktualisieren
                    self._logger.addLog(f"[INFO] Armed-Status: {armed}")
                    
                    # Emittiere die verfügbaren Signale
                    try:
                        # Neues Signal (falls verfügbar)
                        if hasattr(self.signals, 'armed_state_changed'):
                            self.signals.armed_state_changed.emit(armed)
                        # Legacy-Signal (falls verfügbar)
                        if hasattr(self.signals, 'armed_changed'):
                            self.signals.armed_changed.emit(armed)
                    except Exception as e:
                        self._logger.addLog(f"[WARNUNG] Fehler beim Emittieren des Armed-Status: {str(e)}")
                    
                    # Cache aktualisieren
                    prev_armed = armed
                
                # Prüfe, ob der Thread beendet werden soll
                if self._stop_event.is_set():
                    break
                    
                # Warte kurz, um nicht zu viel CPU zu verbrauchen
                await asyncio.sleep(0.5)
                
        except asyncio.CancelledError:
            # Task wurde abgebrochen, normal beenden
            pass
        except Exception as e:
            self._logger.addLog(f"[FEHLER] Fehler bei Armed-Status-Überwachung: {str(e)}")
    
    async def _monitor_in_air(self):
        """Überwacht, ob die Drohne in der Luft ist"""
        try:
            # Cache für Statusinformationen initialisieren
            prev_in_air = None
            
            # Überwachung starten
            async for in_air in self._drone.telemetry.in_air():
                # Änderungen nur senden, wenn sie sich geändert haben
                if prev_in_air is None or in_air != prev_in_air:
                    # Status aktualisieren
                    status_text = "IN DER LUFT" if in_air else "AM BODEN"
                    self._logger.addLog(f"[INFO] Flugstatus: {status_text}")
                    
                    # Emittiere die verfügbaren Signale
                    try:
                        if hasattr(self.signals, 'in_air_changed'):
                            self.signals.in_air_changed.emit(in_air)
                    except Exception as e:
                        self._logger.addLog(f"[WARNUNG] Fehler beim Emittieren des Flugstatus: {str(e)}")
                    
                    # Cache aktualisieren
                    prev_in_air = in_air
                
                # Prüfe, ob der Thread beendet werden soll
                if self._stop_event.is_set():
                    break
                    
                # Warte kurz, um nicht zu viel CPU zu verbrauchen
                await asyncio.sleep(0.5)
                    
        except asyncio.CancelledError:
            # Task wurde abgebrochen, normal beenden
            pass
        except Exception as e:
            self._logger.addLog(f"[FEHLER] Fehler bei Flugstatus-Überwachung: {str(e)}")
    
    async def _monitor_heading(self):
        """Überwacht den Heading (Kompassrichtung) der Drohne"""
        try:
            # Cache für Statusinformationen initialisieren
            prev_heading = None
            message_threshold = 5.0  # Grad-Schwelle für Nachrichten
            
            # Überwachung starten
            async for position in self._drone.telemetry.position():
                # Heading extrahieren (0-360 Grad)
                heading = position.heading_deg
                
                # Minimale Änderungsschwelle
                if prev_heading is None or abs(heading - prev_heading) > message_threshold:
                    # Emittiere die verfügbaren Signale
                    try:
                        if hasattr(self.signals, 'heading_updated'):
                            self.signals.heading_updated.emit(heading)
                    except Exception as e:
                        self._logger.addLog(f"[WARNUNG] Fehler beim Emittieren des Headings: {str(e)}")
                    
                    # Cache aktualisieren
                    prev_heading = heading
                    
                    # Debug-Nachrichten für wichtige Richtungsänderungen
                    if abs(heading - prev_heading) > 45.0:
                        self._logger.addLog(f"[DEBUG] Signifikante Richtungsänderung: {heading:.1f}°")
                
                # Prüfe, ob der Thread beendet werden soll
                if self._stop_event.is_set():
                    break
                    
                # Warte kurz, um nicht zu viel CPU zu verbrauchen
                await asyncio.sleep(0.2)
                
        except asyncio.CancelledError:
            # Task wurde abgebrochen, normal beenden
            pass
        except Exception as e:
            self._logger.addLog(f"[FEHLER] Fehler bei Heading-Überwachung: {str(e)}")
            
    async def _monitor_angular_velocity(self):
        """Überwacht die Winkelgeschwindigkeit der Drohne"""
        try:
            # Überwachung starten
            async for angular_velocity in self._drone.telemetry.angular_velocity_body():
                # Winkelgeschwindigkeit in ein Dictionary umwandeln
                velocity_info = {
                    "roll_rad_s": angular_velocity.roll_rad_s,
                    "pitch_rad_s": angular_velocity.pitch_rad_s,
                    "yaw_rad_s": angular_velocity.yaw_rad_s
                }
                
                # Emittiere die verfügbaren Signale
                try:
                    if hasattr(self.signals, 'angular_velocity_updated'):
                        self.signals.angular_velocity_updated.emit(velocity_info)
                except Exception as e:
                    self._logger.addLog(f"[WARNUNG] Fehler beim Emittieren der Winkelgeschwindigkeit: {str(e)}")
                
                # Prüfe, ob der Thread beendet werden soll
                if self._stop_event.is_set():
                    break
                    
                # Warte kurz, um nicht zu viel CPU zu verbrauchen
                await asyncio.sleep(0.1)
                
        except asyncio.CancelledError:
            # Task wurde abgebrochen, normal beenden
            pass
        except Exception as e:
            self._logger.addLog(f"[FEHLER] Fehler bei Winkelgeschwindigkeits-Überwachung: {str(e)}")
            
    async def _monitor_status_text(self):
        """Überwacht Statustexte vom Flight Controller"""
        try:
            # Überwachung starten
            async for status_text in self._drone.telemetry.status_text():
                # Statustext in ein Dictionary umwandeln
                text_info = {
                    "text": status_text.text,
                    "type": str(status_text.type)
                }
                
                # Status in Log schreiben
                severity = "INFO"
                if status_text.type.name in ["WARNING", "ERROR", "CRITICAL", "ALERT", "EMERGENCY"]:
                    severity = status_text.type.name
                self._logger.addLog(f"[FC {severity}] {status_text.text}")
                
                # Emittiere die verfügbaren Signale
                try:
                    if hasattr(self.signals, 'status_text_received'):
                        self.signals.status_text_received.emit(text_info)
                except Exception as e:
                    self._logger.addLog(f"[WARNUNG] Fehler beim Emittieren des Statustextes: {str(e)}")
                
                # Prüfe, ob der Thread beendet werden soll
                if self._stop_event.is_set():
                    break
                    
                # Bei wichtigen Nachrichten nicht warten
                if severity in ["INFO", "DEBUG", "NOTICE"]:
                    await asyncio.sleep(0.1)
                
        except asyncio.CancelledError:
            # Task wurde abgebrochen, normal beenden
            pass
        except Exception as e:
            self._logger.addLog(f"[FEHLER] Fehler bei Statustext-Überwachung: {str(e)}")
            
    async def _monitor_altitude(self):
        """Überwacht die Höheninformationen der Drohne"""
        try:
            # Cache für Höheninformationen
            prev_altitude_info = None
            message_threshold = 0.5  # Meter-Schwelle für Nachrichten
            
            # Überwachung starten
            async for position in self._drone.telemetry.position():
                # Höheninformationen extrahieren
                altitude_info = {
                    "relative": position.relative_altitude_m,  # Höhe über Startpunkt
                    "absolute": position.absolute_altitude_m,  # Höhe über Meeresspiegel
                    "agl": None                            # Höhe über Grund (falls verfügbar)
                }
                
                # Prüfe, ob sich die Höhe signifikant geändert hat
                if prev_altitude_info is None or abs(altitude_info["relative"] - prev_altitude_info["relative"]) > message_threshold:
                    # Emittiere die verfügbaren Signale
                    try:
                        if hasattr(self.signals, 'altitude_updated'):
                            self.signals.altitude_updated.emit(altitude_info)
                    except Exception as e:
                        self._logger.addLog(f"[WARNUNG] Fehler beim Emittieren der Höheninformation: {str(e)}")
                    
                    # Cache aktualisieren
                    prev_altitude_info = altitude_info.copy()
                    
                    # Wichtige Höhenänderungen loggen
                    if abs(altitude_info["relative"] - prev_altitude_info["relative"]) > 1.0:
                        self._logger.addLog(f"[DEBUG] Höhe: {altitude_info['relative']:.1f}m über Startpunkt")
                
                # Prüfe, ob der Thread beendet werden soll
                if self._stop_event.is_set():
                    break
                    
                # Warte kurz, um nicht zu viel CPU zu verbrauchen
                await asyncio.sleep(0.2)
                
        except asyncio.CancelledError:
            # Task wurde abgebrochen, normal beenden
            pass
        except Exception as e:
            self._logger.addLog(f"[FEHLER] Fehler bei Höhen-Überwachung: {str(e)}")
    
    async def _monitor_landed_state(self):
        """Überwacht den Landezustand der Drohne"""
        try:
            # Cache für Landezustand
            prev_landed_state = None
            
            # Überwachung starten
            async for landed_state in self._drone.telemetry.landed_state():
                # Landezustand als String
                state_str = str(landed_state)
                
                # Prüfe auf Änderungen
                if prev_landed_state is None or state_str != prev_landed_state:
                    # Status aktualisieren
                    self._logger.addLog(f"[INFO] Landezustand: {state_str}")
                    
                    # Emittiere die verfügbaren Signale
                    try:
                        if hasattr(self.signals, 'landed_state_changed'):
                            self.signals.landed_state_changed.emit(state_str)
                    except Exception as e:
                        self._logger.addLog(f"[WARNUNG] Fehler beim Emittieren des Landezustands: {str(e)}")
                    
                    # Cache aktualisieren
                    prev_landed_state = state_str
                
                # Prüfe, ob der Thread beendet werden soll
                if self._stop_event.is_set():
                    break
                    
                # Warte kurz, um nicht zu viel CPU zu verbrauchen
                await asyncio.sleep(0.5)
                
        except asyncio.CancelledError:
            # Task wurde abgebrochen, normal beenden
            pass
        except Exception as e:
            self._logger.addLog(f"[FEHLER] Fehler bei Landezustands-Überwachung: {str(e)}")
    
    async def _monitor_rc_status(self):
        """Überwacht den RC-Status (Fernbedienung)"""
        try:
            # Cache für RC-Status
            prev_rc_info = None
            
            # Überwachung starten
            async for rc_status in self._drone.telemetry.rc_status():
                # RC-Statusinformationen in ein Dictionary umwandeln
                rc_info = {
                    "available": rc_status.is_available,
                    "signal_strength": rc_status.signal_strength_percent
                }
                
                # RC-Info als String für Vergleiche
                rc_info_str = str(rc_info)
                
                # Prüfe auf Änderungen
                if prev_rc_info is None or rc_info_str != prev_rc_info:
                    # Status aktualisieren
                    signal_text = f"{rc_info['signal_strength']}%" if rc_info['available'] else "nicht verfügbar"
                    self._logger.addLog(f"[INFO] RC-Signal: {signal_text}")
                    
                    # Emittiere die verfügbaren Signale
                    try:
                        if hasattr(self.signals, 'rc_status_updated'):
                            self.signals.rc_status_updated.emit(rc_info)
                    except Exception as e:
                        self._logger.addLog(f"[WARNUNG] Fehler beim Emittieren des RC-Status: {str(e)}")
                    
                    # Cache aktualisieren
                    prev_rc_info = rc_info_str
                
                # Prüfe, ob der Thread beendet werden soll
                if self._stop_event.is_set():
                    break
                    
                # Warte kurz, um nicht zu viel CPU zu verbrauchen
                await asyncio.sleep(1.0)
                
        except asyncio.CancelledError:
            # Task wurde abgebrochen, normal beenden
            pass
        except Exception as e:
            self._logger.addLog(f"[FEHLER] Fehler bei RC-Status-Überwachung: {str(e)}")
    
    async def _monitor_unix_epoch_time(self):
        """Überwacht die UNIX-Epochenzeit vom Flight Controller"""
        try:
            # Überwachung starten
            async for unix_time in self._drone.telemetry.unix_epoch_time():
                # Zeit in Mikrosekunden
                time_us = unix_time.time_us
                
                # Emittiere die verfügbaren Signale (seltener aktualisieren)
                try:
                    if hasattr(self.signals, 'unix_epoch_time_updated'):
                        self.signals.unix_epoch_time_updated.emit(time_us)
                except Exception as e:
                    self._logger.addLog(f"[WARNUNG] Fehler beim Emittieren der Unix-Zeit: {str(e)}")
                
                # Prüfe, ob der Thread beendet werden soll
                if self._stop_event.is_set():
                    break
                    
                # Längere Pause, da Zeit-Updates nicht so wichtig sind
                await asyncio.sleep(5.0)
                
        except asyncio.CancelledError:
            # Task wurde abgebrochen, normal beenden
            pass
        except Exception as e:
            self._logger.addLog(f"[FEHLER] Fehler bei Unix-Zeit-Überwachung: {str(e)}")
            
    async def _monitor_actuator_control_target(self):
        """Überwacht die Aktuator-Steuerungsziele"""
        try:
            # Überwachung starten
            async for control_data in self._drone.telemetry.actuator_control_target():
                # Aktuator-Daten in ein Dictionary umwandeln
                control_info = {
                    "group": control_data.group,
                    "controls": list(control_data.controls)  # Liste der Steuerwerte
                }
                
                # Emittiere die verfügbaren Signale
                try:
                    if hasattr(self.signals, 'actuator_control_updated'):
                        self.signals.actuator_control_updated.emit(control_info)
                except Exception as e:
                    self._logger.addLog(f"[WARNUNG] Fehler beim Emittieren der Aktuator-Steuerdaten: {str(e)}")
                
                # Prüfe, ob der Thread beendet werden soll
                if self._stop_event.is_set():
                    break
                    
                # Warte kurz, Aktuator-Updates sind schnell
                await asyncio.sleep(0.05)
                
        except asyncio.CancelledError:
            # Task wurde abgebrochen, normal beenden
            pass
        except Exception as e:
            self._logger.addLog(f"[FEHLER] Fehler bei Aktuator-Steuerungs-Überwachung: {str(e)}")
    
    async def _monitor_actuator_output_status(self):
        """Überwacht den Aktuator-Ausgabestatus"""
        try:
            # Überwachung starten
            async for output_data in self._drone.telemetry.actuator_output_status():
                # Aktuator-Ausgabedaten in ein Dictionary umwandeln
                output_info = {
                    "active": output_data.active,
                    "actuator": list(output_data.actuator)  # Liste der Aktuator-Werte
                }
                
                # Emittiere die verfügbaren Signale
                try:
                    if hasattr(self.signals, 'actuator_output_updated'):
                        self.signals.actuator_output_updated.emit(output_info)
                except Exception as e:
                    self._logger.addLog(f"[WARNUNG] Fehler beim Emittieren der Aktuator-Ausgabedaten: {str(e)}")
                
                # Prüfe, ob der Thread beendet werden soll
                if self._stop_event.is_set():
                    break
                    
                # Warte kurz, Aktuator-Updates sind schnell
                await asyncio.sleep(0.05)
                
        except asyncio.CancelledError:
            # Task wurde abgebrochen, normal beenden
            pass
        except Exception as e:
            self._logger.addLog(f"[FEHLER] Fehler bei Aktuator-Ausgabe-Überwachung: {str(e)}")
    
    async def _monitor_odometry(self):
        """Überwacht die Odometrie-Daten der Drohne"""
        try:
            # Überwachung starten
            async for odometry in self._drone.telemetry.odometry():
                # Odometrie-Daten in ein Dictionary umwandeln
                odometry_info = {
                    "position": {
                        "x": odometry.position_body.x_m,
                        "y": odometry.position_body.y_m,
                        "z": odometry.position_body.z_m
                    },
                    "velocity": {
                        "x": odometry.velocity_body.x_m_s,
                        "y": odometry.velocity_body.y_m_s,
                        "z": odometry.velocity_body.z_m_s
                    },
                    "angular_velocity": {
                        "roll": odometry.angular_velocity_body.roll_rad_s,
                        "pitch": odometry.angular_velocity_body.pitch_rad_s,
                        "yaw": odometry.angular_velocity_body.yaw_rad_s
                    },
                    "frame_id": odometry.frame_id,
                    "child_frame_id": odometry.child_frame_id
                }
                
                # Emittiere die verfügbaren Signale
                try:
                    if hasattr(self.signals, 'odometry_updated'):
                        self.signals.odometry_updated.emit(odometry_info)
                except Exception as e:
                    self._logger.addLog(f"[WARNUNG] Fehler beim Emittieren der Odometrie-Daten: {str(e)}")
                
                # Prüfe, ob der Thread beendet werden soll
                if self._stop_event.is_set():
                    break
                    
                # Warte kurz, um nicht zu viel CPU zu verbrauchen
                await asyncio.sleep(0.1)
                
        except asyncio.CancelledError:
            # Task wurde abgebrochen, normal beenden
            pass
        except Exception as e:
            self._logger.addLog(f"[FEHLER] Fehler bei Odometrie-Überwachung: {str(e)}")
    
    async def _monitor_distance_sensor(self):
        """Überwacht die Abstandssensor-Daten der Drohne"""
        try:
            # Überwachung starten
            async for distance_data in self._drone.telemetry.distance_sensor():
                # Distanzsensor-Daten in ein Dictionary umwandeln
                distance_info = {
                    "minimum_distance_m": distance_data.minimum_distance_m,
                    "maximum_distance_m": distance_data.maximum_distance_m,
                    "current_distance_m": distance_data.current_distance_m
                }
                
                # Emittiere die verfügbaren Signale
                try:
                    if hasattr(self.signals, 'distance_sensor_updated'):
                        self.signals.distance_sensor_updated.emit(distance_info)
                except Exception as e:
                    self._logger.addLog(f"[WARNUNG] Fehler beim Emittieren der Abstandssensor-Daten: {str(e)}")
                
                # Prüfe, ob der Thread beendet werden soll
                if self._stop_event.is_set():
                    break
                    
                # Warte kurz, um nicht zu viel CPU zu verbrauchen
                await asyncio.sleep(0.2)
                
        except asyncio.CancelledError:
            # Task wurde abgebrochen, normal beenden
            pass
        except Exception as e:
            self._logger.addLog(f"[FEHLER] Fehler bei Abstandssensor-Überwachung: {str(e)}")
    
    async def _monitor_scaled_pressure(self):
        """Überwacht die skalierten Drucksensor-Daten der Drohne"""
        try:
            # Überwachung starten
            async for pressure in self._drone.telemetry.scaled_pressure():
                # Drucksensor-Daten in ein Dictionary umwandeln
                pressure_info = {
                    "timestamp_us": pressure.timestamp_us,
                    "absolute_pressure_hpa": pressure.absolute_pressure_hpa,
                    "differential_pressure_hpa": pressure.differential_pressure_hpa,
                    "temperature_deg": pressure.temperature_deg,
                    "differential_temperature_deg": pressure.differential_temperature_deg
                }
                
                # Emittiere die verfügbaren Signale
                try:
                    if hasattr(self.signals, 'scaled_pressure_updated'):
                        self.signals.scaled_pressure_updated.emit(pressure_info)
                except Exception as e:
                    self._logger.addLog(f"[WARNUNG] Fehler beim Emittieren der Drucksensor-Daten: {str(e)}")
                
                # Prüfe, ob der Thread beendet werden soll
                if self._stop_event.is_set():
                    break
                    
                # Warte kurz, um nicht zu viel CPU zu verbrauchen
                await asyncio.sleep(0.5)
                
        except asyncio.CancelledError:
            # Task wurde abgebrochen, normal beenden
            pass
        except Exception as e:
            self._logger.addLog(f"[FEHLER] Fehler bei Drucksensor-Überwachung: {str(e)}")
    
    async def _monitor_raw_imu(self):
        """Überwacht die rohen IMU-Daten der Drohne"""
        try:
            # Überwachung starten
            async for imu in self._drone.telemetry.raw_imu():
                # IMU-Daten in ein Dictionary umwandeln
                imu_info = {
                    "timestamp_us": imu.timestamp_us,
                    "acceleration": {
                        "x": imu.acceleration_x_ms2,
                        "y": imu.acceleration_y_ms2,
                        "z": imu.acceleration_z_ms2
                    },
                    "gyro": {
                        "x": imu.angular_velocity_x_rad_s,
                        "y": imu.angular_velocity_y_rad_s,
                        "z": imu.angular_velocity_z_rad_s
                    },
                    "magnetic_field": {
                        "x": imu.magnetic_field_x_ut,
                        "y": imu.magnetic_field_y_ut,
                        "z": imu.magnetic_field_z_ut
                    },
                    "temperature": imu.temperature_degc
                }
                
                # Emittiere die verfügbaren Signale
                try:
                    if hasattr(self.signals, 'raw_imu_updated'):
                        self.signals.raw_imu_updated.emit(imu_info)
                except Exception as e:
                    self._logger.addLog(f"[WARNUNG] Fehler beim Emittieren der IMU-Daten: {str(e)}")
                
                # Prüfe, ob der Thread beendet werden soll
                if self._stop_event.is_set():
                    break
                    
                # Warte kurz, IMU-Updates sind schnell
                await asyncio.sleep(0.05)
                
        except asyncio.CancelledError:
            # Task wurde abgebrochen, normal beenden
            pass
        except Exception as e:
            self._logger.addLog(f"[FEHLER] Fehler bei IMU-Überwachung: {str(e)}")
    
    async def _monitor_health(self):
        """Überwacht den Gesundheitsstatus der Drohne"""
        try:
            # Cache für Statusinformationen initialisieren
            prev_health = None
            
            # Überwachung starten
            async for health in self._drone.telemetry.health():
                # Gesundheitsinformationen mit sicherem Attributzugriff strukturieren
                health_info = {}
                
                # Sicherer Zugriff auf alle möglichen Attribute der Health-Struktur
                for attr in [
                    "is_gyrometer_calibration_ok",
                    "is_accelerometer_calibration_ok",
                    "is_magnetometer_calibration_ok",
                    "is_level_calibration_ok",  # Könnte in einigen Versionen fehlen
                    "is_local_position_ok",
                    "is_global_position_ok",
                    "is_home_position_ok",
                    # Ältere MAVSDK-Versionen könnten diese haben
                    "is_armable",
                    "calibration_ok"
                ]:
                    # Prüfe, ob das Attribut existiert, bevor darauf zugegriffen wird
                    if hasattr(health, attr):
                        health_info[attr] = getattr(health, attr)
                    else:
                        # Standard-Wert für fehlende Attribute
                        health_info[attr] = None
                
                # Füge einige abgeleitete Felder hinzu
                health_info["calibration_ok"] = (
                    health_info.get("is_gyrometer_calibration_ok", False) and
                    health_info.get("is_accelerometer_calibration_ok", False) and
                    health_info.get("is_magnetometer_calibration_ok", False)
                )
                
                # Änderungen erkennen (vereinfachte Prüfung durch String-Vergleich)
                health_str = str(health_info)
                if prev_health is None or health_str != prev_health:
                    # Status aktualisieren
                    self._logger.addLog("[DEBUG] Gesundheitsstatus aktualisiert")
                    
                    # Emittiere die verfügbaren Signale
                    try:
                        if hasattr(self.signals, 'health_updated'):
                            self.signals.health_updated.emit(health_info)
                    except Exception as e:
                        self._logger.addLog(f"[WARNUNG] Fehler beim Emittieren des Gesundheitsstatus: {str(e)}")
                    
                    # Cache aktualisieren
                    prev_health = health_str
                
                # Prüfe, ob der Thread beendet werden soll
                if self._stop_event.is_set():
                    break
                    
                # Warte kurz, um nicht zu viel CPU zu verbrauchen
                await asyncio.sleep(0.5)
                    
        except asyncio.CancelledError:
            # Task wurde abgebrochen, normal beenden
            pass
        except Exception as e:
            self._logger.addLog(f"[FEHLER] Fehler bei Gesundheitsstatus-Überwachung: {str(e)}")
    
    async def _monitor_health_all(self):
        """Überwacht den gesamten Gesundheitsstatus der Drohne"""
        try:
            # Cache für Statusinformationen initialisieren
            prev_health_all_ok = None
            
            # Überwachung starten
            async for health_all_ok in self._drone.telemetry.health_all_ok():
                # Änderungen nur senden, wenn sie sich geändert haben
                if prev_health_all_ok is None or health_all_ok != prev_health_all_ok:
                    # Status aktualisieren
                    status_text = "OK" if health_all_ok else "FEHLER"
                    self._logger.addLog(f"[INFO] Gesamtstatus: {status_text}")
                    
                    # Emittiere die verfügbaren Signale
                    try:
                        if hasattr(self.signals, 'health_all_ok_changed'):
                            self.signals.health_all_ok_changed.emit(health_all_ok)
                    except Exception as e:
                        self._logger.addLog(f"[WARNUNG] Fehler beim Emittieren des Gesamtstatus: {str(e)}")
                    
                    # Cache aktualisieren
                    prev_health_all_ok = health_all_ok
                
                # Prüfe, ob der Thread beendet werden soll
                if self._stop_event.is_set():
                    break
                    
                # Warte kurz, um nicht zu viel CPU zu verbrauchen
                await asyncio.sleep(0.5)
                    
        except asyncio.CancelledError:
            # Task wurde abgebrochen, normal beenden
            pass
        except Exception as e:
            self._logger.addLog(f"[FEHLER] Fehler bei Gesamtstatus-Überwachung: {str(e)}")
    
    def _update_connection_state(self, is_connected):
        """Aktualisiert den Verbindungsstatus und emittiert entsprechende Signale"""
        self._is_connected = is_connected
        
        # Log-Nachricht
        status_text = "VERBUNDEN" if is_connected else "GETRENNT"
        self._logger.addLog(f"[INFO] Verbindungsstatus: {status_text}")
        
        try:
            # Prüfe, welche Signale verfügbar sind und emittiere sie
            if hasattr(self.signals, 'connection_state_changed'):
                # Neues Verbindungssignal emittieren
                self.signals.connection_state_changed.emit(is_connected)
            
            # Legacy-Verbindungssignale emittieren (falls verfügbar)
            if is_connected:
                if hasattr(self.signals, 'connection_established'):
                    self.signals.connection_established.emit()
            else:
                if hasattr(self.signals, 'connection_lost'):
                    self.signals.connection_lost.emit()
        except Exception as e:
            self._logger.addLog(f"[WARNUNG] Fehler beim Emittieren der Verbindungssignale: {str(e)}")
    
    def _calculate_distance(self, pos1, pos2):
        """Berechnet die Entfernung zwischen zwei GPS-Positionen (grobe Annäherung)"""
        # Einfache Entfernungsberechnung (für genaue Berechnung würde man Haversine-Formel verwenden)
        lat_diff = abs(pos1.latitude_deg - pos2.latitude_deg)
        lon_diff = abs(pos1.longitude_deg - pos2.longitude_deg)
        # Grobe Annäherung: 1 Grad ≈ 111km (variiert je nach Breite)
        return ((lat_diff * 111000) ** 2 + (lon_diff * 111000 * math.cos(math.radians(pos1.latitude_deg))) ** 2) ** 0.5
        
    async def _run_external_server_connection(self, server_port: int) -> None:
        """Asynchrone Methode für die Verbindung zu einem externen MAVSDK-Server
        
        Args:
            server_port: Port des laufenden MAVSDK-Servers
        """
        try:
            # Drone-Objekt mit explizitem Verweis auf den externen Server erstellen
            from mavsdk import System
            self._logger.addLog(f"[INFO] Erstelle System-Objekt mit Server auf localhost:{server_port}")
            self._drone = System(mavsdk_server_address="localhost", port=server_port)
            
            # Verbinden ohne system_address (da wir uns mit einem laufenden Server verbinden)
            self._logger.addLog("[INFO] Verbinde mit MAVSDK-Server...")
            await self._drone.connect()
            
            self._logger.addLog("[INFO] Warte auf Heartbeat vom Flight Controller...")
            # Warte auf Verbindung (connection_state)
            async for state in self._drone.core.connection_state():
                if state.is_connected:
                    self._logger.addLog("[INFO] Verbindung zum Flight Controller hergestellt!")
                    self._is_connected = True
                    self.signals.connection_established.emit()
                    self._trigger_connection_callbacks()
                    break
                
                # Prüfe, ob der Thread beendet werden soll
                if self._stop_event.is_set():
                    self._logger.addLog("[INFO] Verbindungsversuch abgebrochen")
                    return
                    
                # Kurze Pause, um nicht zu viel CPU zu verbrauchen
                await asyncio.sleep(0.1)
            
            # Wenn verbunden, starte Telemetrie und bleibe in der Event-Loop
            if self._is_connected:
                self._logger.addLog("[INFO] Verbindung hergestellt, starte Telemetrie-Abonnements")
                
                # Signalisiere Verbindungsstatus (sowohl neues als auch Legacy-Signal)
                self._update_connection_state(True)
                
                # Telemetrie-Aufgaben starten
                await self._create_telemetry_tasks()
                
                try:
                    # In der Event-Loop bleiben, bis stop_event gesetzt wird
                    while not self._stop_event.is_set():
                        await asyncio.sleep(0.1)
                finally:
                    # Alle Telemetrie-Tasks abbrechen
                    for task in self._telemetry_tasks:
                        task.cancel()
                    
                    # Warten bis alle Tasks beendet sind
                    await asyncio.gather(*self._telemetry_tasks, return_exceptions=True)
                    
                self._logger.addLog("[INFO] Verbindungsschleife beendet")
                
                # Signalisiere Verbindungsabbruch
                self._update_connection_state(False)
                
        except Exception as e:
            error_msg = f"[FEHLER] Fehler in der Verbindungsschleife: {str(e)}"
            self._logger.addLog(error_msg)
            self.signals.error_occurred.emit(error_msg)
        finally:
            # Drohne-Objekt bereinigen
            self._is_connected = False
            self._drone = None
            
    async def _create_telemetry_tasks(self):
        """Erstellt alle asynchronen Telemetrie-Tasks"""
        try:
            self._logger.addLog("[INFO] Starte Telemetrie-Abonnements")
            
            # Erstelle eine Liste aller aktiven Tasks
            self._telemetry_tasks = [
                # Basis-Telemetrie
                asyncio.create_task(self._monitor_armed_state()),
                asyncio.create_task(self._monitor_flight_mode()),
                asyncio.create_task(self._monitor_attitude()),
                asyncio.create_task(self._monitor_position()),
                asyncio.create_task(self._monitor_home_position()),
                asyncio.create_task(self._monitor_battery()),
                asyncio.create_task(self._monitor_gps_info()),
                # Erweiterte Telemetrie
                asyncio.create_task(self._monitor_in_air()),
                asyncio.create_task(self._monitor_health()),
                asyncio.create_task(self._monitor_health_all()),
                # Zusätzliche Telemetrie
                asyncio.create_task(self._monitor_heading()),
                asyncio.create_task(self._monitor_angular_velocity()),
                asyncio.create_task(self._monitor_status_text()),
                asyncio.create_task(self._monitor_altitude()),
                asyncio.create_task(self._monitor_landed_state()),
                asyncio.create_task(self._monitor_rc_status()),
                asyncio.create_task(self._monitor_unix_epoch_time()),
                # Fortgeschrittene Telemetrie (optional, je nach Systembelastung)
                asyncio.create_task(self._monitor_actuator_control_target()),
                asyncio.create_task(self._monitor_actuator_output_status()),
                asyncio.create_task(self._monitor_odometry()),
                asyncio.create_task(self._monitor_distance_sensor()),
                asyncio.create_task(self._monitor_scaled_pressure()),
                asyncio.create_task(self._monitor_raw_imu())
            ]
            return self._telemetry_tasks
        except Exception as e:
            self._logger.addLog(f"[FEHLER] Fehler beim Erstellen der Telemetrie-Tasks: {str(e)}")
            self._logger.addLog("[INFO] Versuche mit reduziertem Telemetrie-Set")
            
            # Versuche mit minimalen Telemetrie-Tasks
            try:
                self._telemetry_tasks = [
                    # Nur die wichtigsten Telemetrie-Streams
                    asyncio.create_task(self._monitor_armed_state()),
                    asyncio.create_task(self._monitor_flight_mode()),
                    asyncio.create_task(self._monitor_attitude()),
                    asyncio.create_task(self._monitor_position()),
                    asyncio.create_task(self._monitor_battery()),
                    asyncio.create_task(self._monitor_health()),
                    asyncio.create_task(self._monitor_in_air())
                ]
                return self._telemetry_tasks
            except Exception as e2:
                self._logger.addLog(f"[FEHLER] Fehler beim Erstellen der minimalen Telemetrie-Tasks: {str(e2)}")
                return []
    
    def _run_connection_loop(self, connection_string: str) -> None:
        """Führt die Verbindungsschleife in einem separaten Thread aus
        
        Args:
            connection_string: Verbindungsstring (z.B. 'udp://:14540')
        """
        try:
            # Event-Loop setzen
            asyncio.set_event_loop(self._loop)
            
            # Verbindung herstellen und Telemetrie überwachen
            self._loop.run_until_complete(self._connect_and_monitor(connection_string))
            
        except Exception as e:
            error_msg = f"[FEHLER] Fehler in der Event-Loop: {str(e)}"
            self._logger.addLog(error_msg)
            self.signals.error_occurred.emit(error_msg)
            
        finally:
            # Event-Loop schließen
            self._loop.close()
    
    async def _connect_and_monitor(self, connection_string: str) -> None:
        """Verbindet mit der Drohne und überwacht die Telemetrie
        
        Args:
            connection_string: Verbindungsstring (z.B. 'udp://:14540')
        """
        try:
            self._logger.addLog(f"[INFO] Verbinde zu {connection_string}...")
            
            # Zum System verbinden
            await self._drone.connect(system_address=connection_string)

            # Auf Connection-Callbacks warten
            self._logger.addLog("[INFO] Warte auf Verbindung...")
            async for state in self._drone.core.connection_state():
                if state.is_connected:
                    self._logger.addLog("[INFO] Verbindung hergestellt")
                    break
                
            # Verbindungsstatus aktualisieren
            self._update_connection_state(True)
            
            # Parameter abrufen
            self._logger.addLog("[INFO] Lade Parameter...")
            await self._get_parameters_in_existing_loop()

            # Telemetrie-Subscriptions starten
            self._logger.addLog("[INFO] Starte Telemetrie-Überwachung...")
            await self._start_telemetry_subscriptions()

            # Nicht blockierend fortfahren und Telemetrie überwachen
            self._logger.addLog("[INFO] Verbindungsstatus: Verbunden")
            
        except Exception as e:
            error_msg = f"[FEHLER] Verbindungsfehler: {str(e)}"
            self._logger.addLog(error_msg)
            self._update_connection_state(False)
            self.signals.error_occurred.emit(error_msg)
    
    async def _start_telemetry_subscriptions(self) -> None:
        """Startet alle Telemetrie-Subscriptions, die MAVSDK bereitstellt
        
        Diese Methode abonniert die wichtigsten Telemetriedaten der Drohne und
        sendet sie über Signale an die UI-Komponenten.
        """
        self._logger.addLog("[INFO] Initialisiere Telemetrie-Subscriptions...")
        
        # Tasks für asynchrone Subscriptions erstellen
        tasks = [
            self._monitor_attitude(),
            self._monitor_position(),
            self._monitor_battery(),
            self._monitor_gps_info(),
            self._monitor_flight_mode(),
            self._monitor_armed(),
            self._monitor_heading(),
            self._monitor_status_text()
        ]
        
        # Alle Tasks parallel starten
        for task in tasks:
            asyncio.create_task(task)
            
        self._logger.addLog("[INFO] Telemetrie-Subscriptions gestartet")
        
    # Die Monitor-Methoden wurden vereinheitlicht und sind jetzt in den unten definierten
    # Methoden implementiert. Diese werden von _start_telemetry_subscriptions aufgerufen.

    async def _start_telemetry_subscriptions(self) -> None:
        """Startet alle Telemetrie-Subscriptions, die MAVSDK bereitstellt
        
        Diese Methode abonniert die wichtigsten Telemetriedaten der Drohne und
        sendet sie über Signale an die UI-Komponenten.
        """
        self._logger.addLog("[INFO] Initialisiere Telemetrie-Subscriptions...")
        
        try:
            # Tasks erstellen
            tasks = [
                # Basis-Telemetrie-Aufgaben
                asyncio.create_task(self._monitor_armed()),
                asyncio.create_task(self._monitor_flight_mode()),
                asyncio.create_task(self._monitor_gps_info()),
                asyncio.create_task(self._monitor_battery()),
                asyncio.create_task(self._monitor_attitude()),
                asyncio.create_task(self._monitor_position()),
                asyncio.create_task(self._monitor_home_position()),
                
                # Erweiterte Gesundheits- und Status-Überwachung
                asyncio.create_task(self._monitor_health()),
                asyncio.create_task(self._monitor_health_all()),
                asyncio.create_task(self._monitor_in_air()),
                asyncio.create_task(self._monitor_status_text()),
                
                # Navigation und Heading
                asyncio.create_task(self._monitor_heading()),
                asyncio.create_task(self._monitor_altitude()),
                asyncio.create_task(self._monitor_landed_state()),
                
                # Sensor- und System-Telemetrie
                asyncio.create_task(self._monitor_rc_status()),
                asyncio.create_task(self._monitor_angular_velocity()),
                asyncio.create_task(self._monitor_unix_epoch_time()),
                
                # Erweiterte und detaillierte Telemetrie (optional, können bei Bedarf deaktiviert werden)
                asyncio.create_task(self._monitor_actuator_control_target()),
                asyncio.create_task(self._monitor_actuator_output_status()),
                asyncio.create_task(self._monitor_odometry()),
                asyncio.create_task(self._monitor_distance_sensor()),
                asyncio.create_task(self._monitor_scaled_pressure()),
                asyncio.create_task(self._monitor_raw_imu())
            ]
            
            self._logger.addLog(f"[INFO] {len(tasks)} Telemetrie-Überwachungsaufgaben gestartet")
            
            # Auf Abbruch warten
            while not self._stop_event.is_set():
                await asyncio.sleep(0.1)
                
            # Tasks abbrechen
            for task in tasks:
                task.cancel()
            
            self._logger.addLog(f"[INFO] Telemetrie-Überwachung beendet")
                
        except Exception as e:
            error_msg = f"[FEHLER] Fehler beim Starten der Telemetrie-Subscriptions: {str(e)}"
            self._logger.addLog(error_msg)
            self.signals.error_occurred.emit(error_msg)
    
    # Telemetrie-Monitoring-Methoden
    
    async def _monitor_armed(self) -> None:
        """Überwacht den Armed-Status"""
        try:
            async for armed in self._drone.telemetry.armed():
                if self._stop_event.is_set():
                    break
                    
                # Status-Änderung melden
                self.signals.armed_changed.emit(armed)
                self._trigger_telemetry_callbacks('armed', {'armed': armed})
                
                # Bei Änderung loggen
                if self._should_emit_message('armed', armed):
                    self._logger.addLog(f"[INFO] Armed-Status: {'ARMED' if armed else 'DISARMED'}")
                    
        except Exception as e:
            self._logger.addLog(f"[FEHLER] Fehler beim Überwachen des Armed-Status: {str(e)}")
    
    async def _monitor_flight_mode(self) -> None:
        """Überwacht den Flugmodus"""
        try:
            async for flight_mode in self._drone.telemetry.flight_mode():
                if self._stop_event.is_set():
                    break
                    
                mode_str = str(flight_mode)
                
                # Status-Änderung melden
                self.signals.flight_mode_changed.emit(mode_str)
                self._trigger_telemetry_callbacks('flight_mode', {'mode': mode_str})
                
                # Bei Änderung loggen
                if self._should_emit_message('flight_mode', mode_str):
                    self._logger.addLog(f"[INFO] Flugmodus: {mode_str}")
                    
        except Exception as e:
            self._logger.addLog(f"[FEHLER] Fehler beim Überwachen des Flugmodus: {str(e)}")
    
    async def _monitor_gps_info(self) -> None:
        """Überwacht die GPS-Informationen"""
        try:
            async for gps_info in self._drone.telemetry.gps_info():
                if self._stop_event.is_set():
                    break
                    
                # GPS-Info als Dictionary
                info = {
                    'num_satellites': gps_info.num_satellites,
                    'fix_type': gps_info.fix_type
                }
                
                # Status-Änderung melden
                self.signals.gps_info_changed.emit(info)
                self._trigger_telemetry_callbacks('gps_info', info)
                
                # Bei Änderung loggen
                if self._should_emit_message('gps', info):
                    self._logger.addLog(f"[INFO] GPS: {gps_info.num_satellites} Satelliten, Fix: {gps_info.fix_type}")
                    
        except Exception as e:
            self._logger.addLog(f"[FEHLER] Fehler beim Überwachen der GPS-Informationen: {str(e)}")
    
    async def _monitor_battery(self) -> None:
        """Überwacht den Batteriestatus"""
        try:
            async for battery in self._drone.telemetry.battery():
                if self._stop_event.is_set():
                    break
                    
                # Batterie-Info als Dictionary
                info = {
                    'remaining_percent': battery.remaining_percent,
                    'voltage_v': battery.voltage_v,
                    'current_a': battery.current_a
                }
                
                # Status-Änderung melden
                self.signals.battery_changed.emit(info)
                self._trigger_telemetry_callbacks('battery', info)
                
                # Bei signifikanter Änderung loggen
                if self._should_emit_message('battery', info['remaining_percent']):
                    self._logger.addLog(f"[INFO] Batterie: {info['remaining_percent']:.1f}%, {info['voltage_v']:.2f}V")
                    
        except Exception as e:
            self._logger.addLog(f"[FEHLER] Fehler beim Überwachen des Batteriestatus: {str(e)}")
    
    async def _monitor_attitude(self) -> None:
        """Überwacht die Lage der Drohne"""
        try:
            async for attitude in self._drone.telemetry.attitude_euler():
                if self._stop_event.is_set():
                    break
                    
                # Lage als Dictionary
                info = {
                    'roll_deg': attitude.roll_deg,
                    'pitch_deg': attitude.pitch_deg,
                    'yaw_deg': attitude.yaw_deg
                }
                
                # Status-Änderung melden
                self.signals.attitude_changed.emit(info)
                self.signals.heading_changed.emit(attitude.yaw_deg)
                self._trigger_telemetry_callbacks('attitude', info)
                self._trigger_telemetry_callbacks('heading', {'heading': attitude.yaw_deg})
                
                # Bei signifikanter Änderung des Headings loggen
                if self._should_emit_message('heading', attitude.yaw_deg):
                    self._logger.addLog(f"[INFO] Heading: {attitude.yaw_deg:.1f}\u00b0")
                    
        except Exception as e:
            self._logger.addLog(f"[FEHLER] Fehler beim Überwachen der Lage: {str(e)}")
    
    async def _monitor_position(self) -> None:
        """Überwacht die Position der Drohne"""
        try:
            async for position in self._drone.telemetry.position():
                if self._stop_event.is_set():
                    break
                    
                # Position als Dictionary
                info = {
                    'latitude_deg': position.latitude_deg,
                    'longitude_deg': position.longitude_deg,
                    'absolute_altitude_m': position.absolute_altitude_m,
                    'relative_altitude_m': position.relative_altitude_m
                }
                
                # Status-Änderung melden
                self.signals.position_changed.emit(info)
                self._trigger_telemetry_callbacks('position', info)
                
                # Bei signifikanter Änderung der Höhe loggen
                if self._should_emit_message('altitude', info['relative_altitude_m']):
                    self._logger.addLog(f"[INFO] Höhe: {info['relative_altitude_m']:.1f}m AGL")
                    
        except Exception as e:
            self._logger.addLog(f"[FEHLER] Fehler beim Überwachen der Position: {str(e)}")
    
    async def _monitor_home_position(self) -> None:
        """Überwacht die Home-Position der Drohne"""
        try:
            async for position in self._drone.telemetry.home():
                if self._stop_event.is_set():
                    break
                    
                # Home-Position als Dictionary
                info = {
                    'latitude_deg': position.latitude_deg,
                    'longitude_deg': position.longitude_deg,
                    'absolute_altitude_m': position.absolute_altitude_m,
                    'relative_altitude_m': position.relative_altitude_m
                }
                
                # Status-Änderung melden
                self.signals.home_position_changed.emit(info)
                self._trigger_telemetry_callbacks('home_position', info)
                
        except Exception as e:
            self._logger.addLog(f"[FEHLER] Fehler beim Überwachen der Home-Position: {str(e)}")
    
    async def _monitor_status_text(self) -> None:
        """Überwacht Status-Texte"""
        try:
            async for status_text in self._drone.telemetry.status_text():
                if self._stop_event.is_set():
                    break
                    
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
                self.signals.statustext_received.emit(text)
                self._trigger_statustext_callbacks(text)
                
                # Status-Texte immer loggen (keine Filterung)
                # Wichtig für die spezielle Preflight-View mit hervorgehobenen Systeminformationen
                self._logger.addLog(text)
                
        except Exception as e:
            self._logger.addLog(f"[FEHLER] Fehler beim Überwachen der Status-Texte: {str(e)}")
    
    def _should_emit_message(self, message_type: str, value: Any) -> bool:
        """Prüft, ob eine Änderungsmeldung ausgelöst werden soll
        
        Implementiert eine intelligente Nachrichtenfilterung, die Nachrichten nur dann
        ausgibt, wenn sich der Wert signifikant geändert hat oder eine Mindestzeit
        vergangen ist.
        
        Args:
            message_type: Typ der Nachricht (z.B. 'heading', 'battery')
            value: Aktueller Wert
            
        Returns:
            bool: True, wenn die Nachricht ausgegeben werden soll
        """
        # Standard-Werte für nicht konfigurierte Nachrichtentypen
        threshold = self._message_thresholds.get(message_type, 0.0)
        min_interval = self._min_message_interval_seconds.get(message_type, 0.0)
        
        current_time = time.time()
        last_time = self._last_message_times.get(message_type, 0)
        last_value = self._last_message_values.get(message_type, None)
        
        # Prüfen, ob die Mindestzeit vergangen ist
        time_condition = (current_time - last_time) >= min_interval
        
        # Prüfen, ob sich der Wert signifikant geändert hat
        if last_value is None:
            # Erster Wert wird immer ausgegeben
            value_condition = True
        else:
            # Prüfen, ob die Änderung signifikant ist
            if isinstance(value, (int, float)) and isinstance(last_value, (int, float)):
                value_condition = abs(value - last_value) >= threshold
            else:
                # Bei nicht-numerischen Werten jede Änderung melden
                value_condition = value != last_value
        
        # Nachricht ausgeben, wenn beide Bedingungen erfüllt sind
        should_emit = time_condition and value_condition
        
        if should_emit:
            # Werte aktualisieren
            self._last_message_times[message_type] = current_time
            self._last_message_values[message_type] = value
        
        return should_emit
