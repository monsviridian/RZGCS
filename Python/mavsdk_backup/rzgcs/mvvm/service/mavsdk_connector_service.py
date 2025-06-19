#!/usr/bin/env python3
"""
MAVSDK Connector Service - Service Layer für MAVSDK-Integration
Verantwortlich für die Kommunikation mit der Drohne und Signalverarbeitung
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

from rzgcs.utils.drone_signal_hub import DroneSignalHub
from backend.logger import Logger
from backend.exceptions import ConnectionError, ConnectionTimeoutError
from backend.mavsdk_server_controller import MAVSDKServerController


class MAVSDKConnectorService(QObject):
    """
    MAVSDK-Connector Service für MVVM-Architektur
    
    Diese Implementierung vermeidet Metaklassen-Konflikte und bietet eine saubere
    Schnittstelle für die ViewModels mit besonderer Unterstützung für:
    - Nachrichtenfilterung nach Schwellenwerten und Zeitintervallen
    - Preflight-View mit Hervorhebung von Systeminformationen
    """
    
    def __init__(self, logger: Logger, parent=None):
        """Initialisierung des MAVSDKConnectorService"""
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
        
        # Verfügbare Ports
        self._available_ports = []
    
    # Callback-Registrierungsmethoden
    
    def register_connection_callback(self, callback: Callable[[], None]) -> None:
        """Registriert einen Callback für Verbindungs-Status-Änderungen"""
        if callback not in self._connection_callbacks:
            self._connection_callbacks.append(callback)
    
    def register_disconnection_callback(self, callback: Callable[[], None]) -> None:
        """Registriert einen Callback für Verbindungs-Status-Änderungen"""
        if callback not in self._disconnection_callbacks:
            self._disconnection_callbacks.append(callback)
    
    def register_telemetry_callback(self, telemetry_type: str, callback: Callable[[Any], None]) -> None:
        """Registriert einen Callback für Telemetrie-Updates"""
        if telemetry_type not in self._telemetry_callbacks:
            self._telemetry_callbacks[telemetry_type] = []
        
        if callback not in self._telemetry_callbacks[telemetry_type]:
            self._telemetry_callbacks[telemetry_type].append(callback)
    
    def register_statustext_callback(self, callback: Callable[[str], None]) -> None:
        """Registriert einen Callback für Status-Text-Meldungen"""
        if callback not in self._statustext_callbacks:
            self._statustext_callbacks.append(callback)
    
    # Verbindungsmethoden
    
    def connect_serial(self, port: str, baudrate: int = 57600) -> bool:
        """Stellt eine Verbindung zur Drohne über einen seriellen Port her"""
        try:
            # Sicherstellen, dass keine aktive Verbindung besteht
            if self._is_connected:
                self._logger.addLog(f"[INFO] Trenne bestehende Verbindung")
                self.disconnect()
            
            # Verbindungsstring erstellen
            self._connection_string = f"serial://{port}:{baudrate}"
            self._logger.addLog(f"[INFO] Verbinde mit {self._connection_string}")
            
            # MAVSDK-Server starten
            if not self._server_controller.start_server(port, baudrate):
                self._logger.addLog(f"[ERROR] Konnte MAVSDK-Server nicht starten")
                return False
            
            # Verbindungsthread starten
            self._start_connection_thread(f"udp://127.0.0.1:{self._server_port}")
            return True
        
        except Exception as e:
            self._logger.addLog(f"[ERROR] Verbindungsfehler: {str(e)}")
            return False
    
    def connect_udp(self, connection_string: str) -> bool:
        """Stellt eine Verbindung zur Drohne über UDP her"""
        try:
            # Sicherstellen, dass keine aktive Verbindung besteht
            if self._is_connected:
                self._logger.addLog(f"[INFO] Trenne bestehende Verbindung")
                self.disconnect()
            
            # Verbindungsstring verarbeiten
            if connection_string.startswith("udp:"):
                connection_string = connection_string[4:]
            
            self._connection_string = f"udp://{connection_string}"
            self._logger.addLog(f"[INFO] Verbinde mit {self._connection_string}")
            
            # Verbindungsthread starten
            self._start_connection_thread(self._connection_string)
            return True
        
        except Exception as e:
            self._logger.addLog(f"[ERROR] Verbindungsfehler: {str(e)}")
            return False
    
    def connect_tcp(self, connection_string: str) -> bool:
        """Stellt eine Verbindung zur Drohne über TCP her"""
        try:
            # Sicherstellen, dass keine aktive Verbindung besteht
            if self._is_connected:
                self._logger.addLog(f"[INFO] Trenne bestehende Verbindung")
                self.disconnect()
            
            # Verbindungsstring verarbeiten
            if connection_string.startswith("tcp:"):
                connection_string = connection_string[4:]
            
            self._connection_string = f"tcp://{connection_string}"
            self._logger.addLog(f"[INFO] Verbinde mit {self._connection_string}")
            
            # Verbindungsthread starten
            self._start_connection_thread(self._connection_string)
            return True
        
        except Exception as e:
            self._logger.addLog(f"[ERROR] Verbindungsfehler: {str(e)}")
            return False
    
    def connect_simulator(self) -> bool:
        """Stellt eine Verbindung zum Simulator her"""
        try:
            # Sicherstellen, dass keine aktive Verbindung besteht
            if self._is_connected:
                self._logger.addLog(f"[INFO] Trenne bestehende Verbindung")
                self.disconnect()
            
            self._connection_string = "udp://:14550"
            self._logger.addLog(f"[INFO] Verbinde mit Simulator über {self._connection_string}")
            
            # Verbindungsthread starten
            self._start_connection_thread(self._connection_string)
            return True
        
        except Exception as e:
            self._logger.addLog(f"[ERROR] Verbindungsfehler: {str(e)}")
            return False
    
    def disconnect(self) -> None:
        """Trennt die Verbindung zur Drohne"""
        if not self._is_connected:
            return
        
        self._logger.addLog("[INFO] Trenne Verbindung...")
        
        # Stop event setzen, um den Thread zu beenden
        self._stop_event.set()
        
        # Auf Thread-Ende warten
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        
        # MAVSDK-Server stoppen
        self._server_controller.stop_server()
        
        # Status zurücksetzen
        self._is_connected = False
        self._connection_string = ""
        
        # Signal emittieren und Callbacks aufrufen
        self.signals.connection_lost.emit()
        for callback in self._disconnection_callbacks:
            try:
                callback()
            except Exception as e:
                self._logger.addLog(f"[ERROR] Fehler im Disconnect-Callback: {str(e)}")
    
    def get_available_ports(self) -> List[str]:
        """Gibt die Liste der verfügbaren seriellen Ports zurück"""
        try:
            import serial.tools.list_ports
            self._available_ports = [port.device for port in serial.tools.list_ports.comports()]
            return self._available_ports
        except Exception as e:
            self._logger.addLog(f"[ERROR] Fehler beim Abrufen der verfügbaren Ports: {str(e)}")
            return []
