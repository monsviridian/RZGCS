#!/usr/bin/env python3
"""
MAVSDK Connector für RZGCS
Verbindet die MAVSDK mit der RZGCS-Anwendung unter Beibehaltung einer sauberen MVVM-Architektur
"""

import sys
import time
import asyncio
import threading
from typing import Dict, List, Callable, Any, Optional

try:
    from mavsdk import System
    from mavsdk.telemetry import FlightMode, LandedState
except ImportError:
    print("MAVSDK nicht installiert!")
    print("Installiere mit: pip install mavsdk")
    sys.exit(1)

from PySide6.QtCore import QObject

from backend.logger import Logger
from backend.mavsdk_server_controller import MAVSDKServerController
from rzgcs.utils.drone_signal_hub import DroneSignalHub
from backend.exceptions import ConnectionError, ConnectionTimeoutError


class MAVSDKConnector(QObject):
    """
    MAVSDK-Connector für MVVM-Architektur
    
    Diese Implementierung vermeidet Metaklassen-Konflikte und bietet eine saubere
    Schnittstelle für die ViewModels mit besonderer Unterstützung für:
    - Nachrichtenfilterung nach Schwellenwerten und Zeitintervallen
    - Preflight-View mit Hervorhebung von Systeminformationen
    """
    
    def __init__(self, logger: Logger, parent=None):
        """Initialisierung des MAVSDKConnector"""
        super().__init__(parent)
        
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
            baudrate: Baudrate (z.B. 57600, 115200)
        
        Returns:
            bool: True, wenn die Verbindung erfolgreich hergestellt wurde
        """
        try:
            # Bereits verbunden?
            if self._is_connected:
                self._logger.addLog("[WARNUNG] Bereits verbunden. Trenne Verbindung zuerst.")
                self.disconnect()
                
            # Connection-String formatieren
            self._connection_string = f"serial://{port}:{baudrate}"
            self._logger.addLog(f"[SYSTEM INFO] Verbindungsversuch zu {self._connection_string}")
            
            # MAVSDK-Server direkt in einem Thread starten
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._connect_thread_func)
            self._thread.daemon = True
            self._thread.start()
            
            # Erfolg - der tatsächliche Verbindungsstatus wird im Thread überwacht
            self._logger.addLog(f"[SYSTEM INFO] Verbindungs-Thread gestartet für {self._connection_string}")
            return True
            
        except Exception as e:
            error_msg = f"[FEHLER] Fehler beim Verbinden mit seriellem Port {port}: {str(e)}"
            self._logger.addLog(error_msg)
            self.signals.error_occurred.emit(error_msg)
            return False
            
    def _connect_thread_func(self):
        """Thread-Funktion für asynchrone Verbindungsherstellung basierend auf dem offiziellen MAVSDK-Python-Stil"""
        import asyncio
        import time
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self._loop = loop
        
        async def run_connection():
            # MAVSDK-Python verwendet einen eleganteren Ansatz als in unserer bisherigen Implementierung
            # connect() startet automatisch den eingebetteten MAVSDK-Server
            try:
                self._logger.addLog(f"[SYSTEM INFO] Starte MAVSDK-Verbindung zu {self._connection_string}")
                
                # Wir versuchen zuerst, den MAVSDK-Server manuell zu starten und dann zu verbinden
                try:
                    # Finde den Pfad zum MAVSDK-Server
                    import os
                    import mavsdk
                    import subprocess
                    import sys
                    
                    # Verwende den MAVSDK-Server aus dem Projektordner
                    import os
                    import sys
                    
                    # Projektpfad ermitteln (2 Ordner nach oben von dieser Datei)
                    current_file_path = os.path.abspath(__file__)
                    project_dir = os.path.abspath(os.path.join(os.path.dirname(current_file_path), '..', '..', '..'))
                    
                    # MAVSDK-Server-Pfad basierend auf Betriebssystem
                    if sys.platform == 'win32':
                        server_bin = os.path.join(project_dir, 'mavsdkserver', 'windows', 'mavsdk_server_bin.exe')
                    elif sys.platform == 'darwin':  # macOS
                        server_bin = os.path.join(project_dir, 'mavsdkserver', 'mac', 'mavsdk_server')
                    else:  # Linux oder andere
                        server_bin = os.path.join(project_dir, 'mavsdkserver', 'linux', 'mavsdk_server')
                    
                    # Debug-Ausgabe für alle potenziellen Pfade
                    self._logger.addLog(f"[DEBUG] Projekt-Verzeichnis: {project_dir}")
                    self._logger.addLog(f"[DEBUG] Erwarteter MAVSDK-Server-Pfad: {server_bin}")
                    
                    # Prüfe, ob der Server existiert
                    if not os.path.isfile(server_bin):
                        self._logger.addLog(f"[FEHLER] MAVSDK-Server nicht gefunden unter: {server_bin}")
                        
                        # Versuch, den Server an anderen Orten zu finden
                        alternate_locations = [
                            os.path.join(project_dir, 'mavsdkserver', 'windows', 'mavsdk_server.exe'),
                            os.path.join(project_dir, 'mavsdk_server', 'windows', 'mavsdk_server.exe'),
                            os.path.join(project_dir, 'mavsdk_server', 'windows', 'mavsdk_server_bin.exe')
                        ]
                        
                        for alt_path in alternate_locations:
                            self._logger.addLog(f"[DEBUG] Prüfe alternativen Pfad: {alt_path}")
                            if os.path.isfile(alt_path):
                                server_bin = alt_path
                                self._logger.addLog(f"[INFO] MAVSDK-Server gefunden unter: {server_bin}")
                                break
                        else:
                            # Falls kein Server gefunden wurde
                            self._logger.addLog("[KRITISCH] Konnte keinen MAVSDK-Server im Projektordner finden!")
                            raise FileNotFoundError("MAVSDK-Server nicht gefunden im Projektordner")
                    
                    # Starte den MAVSDK-Server manuell mit dem Connection-String
                    self._logger.addLog(f"[INFO] Starte MAVSDK-Server mit: {server_bin} {self._connection_string}")
                    self._server_process = subprocess.Popen(
                        [server_bin, self._connection_string],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                    
                    # Warte kurz, um zu sehen, ob der Prozess sofort fehlschlägt
                    import time
                    time.sleep(1.0)
                    
                    # Prüfe, ob der Prozess noch läuft
                    if self._server_process.poll() is not None:
                        # Prozess ist bereits beendet - das ist nicht gut
                        stdout, stderr = self._server_process.communicate()
                        self._logger.addLog(f"[FEHLER] MAVSDK-Server beendet mit Code {self._server_process.returncode}")
                        self._logger.addLog(f"[FEHLER] STDOUT: {stdout}")
                        self._logger.addLog(f"[FEHLER] STDERR: {stderr}")
                        raise RuntimeError(f"MAVSDK-Server konnte nicht gestartet werden: {stderr}")
                    
                    self._logger.addLog(f"[INFO] MAVSDK-Server erfolgreich gestartet (PID: {self._server_process.pid})")
                    
                    # Mit dem gestarteten Server verbinden (ohne system_address, da wir lokal verbinden)
                    self._drone = System()
                    self._logger.addLog("[INFO] Verbinde mit lokalem MAVSDK-Server...")
                    await self._drone.connect()
                    
                except Exception as e:
                    self._logger.addLog(f"[FEHLER] Fehler beim manuellen Starten des MAVSDK-Servers: {str(e)}")
                    self._logger.addLog("[INFO] Versuche Verbindung über eingebetteten MAVSDK-Server...")
                    
                    # Fallback: Nutze die eingebaute Verbindungsmethode
                    self._drone = System()
                    await self._drone.connect(system_address=self._connection_string)
                
                self._logger.addLog("[SYSTEM INFO] Warte auf Verbindung zum Flight Controller...")
                # Warte auf Verbindung (connection_state)
                connection_coroutine = self._drone.core.connection_state()
                # Warte maximal 15 Sekunden auf Verbindung
                start_time = time.time()
                connected = False
                
                while time.time() - start_time < 15 and not self._stop_event.is_set():
                    try:
                        async for state in connection_coroutine:
                            if state.is_connected:
                                self._logger.addLog("[SYSTEM INFO] Verbindung zum Flight Controller hergestellt!")
                                connected = True
                                break
                            await asyncio.sleep(0.1)
                        if connected:
                            break
                    except Exception as e:
                        self._logger.addLog(f"[SYSTEM INFO] Verbindungsprüfung: {str(e)}")
                        await asyncio.sleep(1)
                
                if connected:
                    self._is_connected = True
                    self.signals.connection_established.emit()
                    self._trigger_connection_callbacks()
                    
                    # Status-Text-Monitoring starten
                    asyncio.ensure_future(self._monitor_status_text())
                    
                    # Telemetrie-Tasks starten
                    await self._start_telemetry_subscriptions()
                    
                    # Bleibe in der Event-Loop, bis stop_event gesetzt wird
                    while not self._stop_event.is_set():
                        await asyncio.sleep(0.1)
                else:
                    if not self._stop_event.is_set():
                        self._logger.addLog("[FEHLER] Timeout bei Verbindungsherstellung")
                    self._is_connected = False
            except Exception as e:
                self._logger.addLog(f"[FEHLER] Verbindungsfehler: {str(e)}")
                self._is_connected = False
            finally:
                # Aufräumen, wenn wir hier ankommen
                if hasattr(self, '_server_process') and self._server_process:
                    try:
                        self._server_process.terminate()
                        self._server_process = None
                    except:
                        pass
        
        try:
            # Führe die asyncio-Funktion im neuen Event-Loop aus
            loop.run_until_complete(run_connection())
        except Exception as e:
            self._logger.addLog(f"[FEHLER] Thread-Fehler: {str(e)}")
            self._is_connected = False
        finally:
            # Event-Loop schließen
            loop.close()
            
    async def _check_connection_async(self):
        """Prüft asynchron, ob eine Verbindung besteht"""
        try:
            # Versuche zuerst get_identification
            try:
                await self._drone.core.get_identification()
                return True
            except Exception:
                pass
                
            # Falls das fehlschlägt, versuche get_version
            try:
                await self._drone.info.get_version()
                return True
            except Exception:
                pass
                
            # Wenn alles fehlschlägt, ist keine Verbindung vorhanden
            return False
        except Exception:
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
    
    def _run_connection_loop(self, connection_string: str) -> None:
        """Führt die asynchrone Event-Loop aus
        
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
            # Mit der Drohne verbinden
            self._logger.addLog(f"[INFO] Verbinde mit {connection_string}...")
            await self._drone.connect(connection_string)
            
            # Verbindungsstatus überwachen
            async for state in self._drone.core.connection_state():
                if self._stop_event.is_set():
                    break
                    
                if state.is_connected:
                    self._logger.addLog("[INFO] Verbindung hergestellt")
                    self._is_connected = True
                    self.signals.connection_established.emit()
                    self._trigger_connection_callbacks()
                    
                    # Telemetrie-Subscriptions starten
                    await self._start_telemetry_subscriptions()
                    break
                    
        except Exception as e:
            error_msg = f"[FEHLER] Verbindungsfehler: {str(e)}"
            self._logger.addLog(error_msg)
            self.signals.error_occurred.emit(error_msg)
    
    async def _start_telemetry_subscriptions(self) -> None:
        """Startet alle Telemetrie-Subscriptions"""
        try:
            # Tasks erstellen
            tasks = [
                asyncio.create_task(self._monitor_armed()),
                asyncio.create_task(self._monitor_flight_mode()),
                asyncio.create_task(self._monitor_gps_info()),
                asyncio.create_task(self._monitor_battery()),
                asyncio.create_task(self._monitor_attitude()),
                asyncio.create_task(self._monitor_position()),
                asyncio.create_task(self._monitor_home_position()),
                asyncio.create_task(self._monitor_status_text())
            ]
            
            # Auf Abbruch warten
            while not self._stop_event.is_set():
                await asyncio.sleep(0.1)
                
            # Tasks abbrechen
            for task in tasks:
                task.cancel()
                
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
        """Überwacht Status-Texte mit spezieller Unterstützung für die Preflight-View"""
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
                
                # Systeminformationen markieren für vergrößerte Darstellung (30% statt 10% Höhe)
                # und größere Schrift (16px) mit Hervorhebung (fett)
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
        vergangen ist. Dies reduziert Log-Spam bei realen Flugcontrollern.
        
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
    
