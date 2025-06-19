"""
Zentraler MAVLink-Manager für die Koordination aller MAVLink-Operationen.
"""

import logging
import threading
import time
import math
from queue import Queue
from typing import Optional, Dict, Any
from PySide6.QtCore import QObject, Signal, QTimer

from pymavlink import mavutil
from pymavlink.dialects.v20 import ardupilotmega as mavlink

class MAVLinkError(Exception):
    """Basisklasse für MAVLink-Fehler"""
    pass

class MAVLinkConnectionError(MAVLinkError):
    """Fehler bei der MAVLink-Verbindung"""
    pass

class MAVLinkTimeoutError(MAVLinkError):
    """Timeout bei MAVLink-Operationen"""
    pass

class MAVLinkManager(QObject):
    """
    Zentraler Manager für alle MAVLink-Operationen.
    Koordiniert Verbindung, Nachrichtenverarbeitung und Fehlerbehandlung.
    """
    
    # Signale
    connection_status_changed = Signal(bool)  # True = verbunden
    message_received = Signal(object)  # MAVLink-Nachricht
    error_occurred = Signal(str)  # Fehlermeldung
    heartbeat_received = Signal()  # Heartbeat empfangen
    attitude_updated = Signal(float, float, float)  # roll, pitch, yaw
    gps_updated = Signal(float, float, float)  # lat, lon, alt
    battery_updated = Signal(float, float, float)  # voltage, current, remaining
    
    def __init__(self):
        super().__init__()
        
        # Logger einrichten
        self.logger = logging.getLogger('mavlink')
        self.logger.setLevel(logging.DEBUG)
        
        # Thread-Synchronisation
        self._lock = threading.Lock()
        self._message_queue = Queue()
        self._running = False
        self._connection = None
        self._message_thread = None
        
        # Verbindungsstatus
        self._connected = False
        self._system_id = None
        self._component_id = None
        self._last_heartbeat = 0
        
        # Timer für Heartbeat-Überwachung
        self._heartbeat_timer = QTimer()
        self._heartbeat_timer.timeout.connect(self._check_heartbeat)
        self._heartbeat_timer.start(1000)  # Prüfe jede Sekunde
        
        # Konstanten
        self.HEARTBEAT_TIMEOUT = 5.0  # Sekunden
        self.MAX_RECONNECT_ATTEMPTS = 3
        self.RECONNECT_DELAY = 1.0
        
    def connect(self, port: str, baudrate: int = 115200) -> bool:
        """
        Stellt eine MAVLink-Verbindung her.
        
        Args:
            port: Serieller Port oder UDP-Adresse
            baudrate: Baudrate für serielle Verbindungen
            
        Returns:
            bool: True bei erfolgreicher Verbindung
        """
        try:
            with self._lock:
                if self._connected:
                    self.logger.warning("Bereits verbunden")
                    return True
                
                self.logger.info(f"Verbinde mit {port} bei {baudrate} baud...")
                
                # Verbindung erstellen
                self._connection = mavutil.mavlink_connection(
                    port,
                    baud=baudrate,
                    source_system=255,  # GCS System ID
                    source_component=1,  # GCS Component ID
                    dialect='ardupilotmega'
                )
                
                # Warte auf Heartbeat
                self.logger.info("Warte auf Heartbeat...")
                msg = self._connection.wait_heartbeat(timeout=self.HEARTBEAT_TIMEOUT)
                
                if not msg:
                    raise MAVLinkTimeoutError("Kein Heartbeat empfangen")
                
                # System und Component ID speichern
                self._system_id = msg.get_srcSystem()
                self._component_id = msg.get_srcComponent()
                self._last_heartbeat = time.time()
                
                # Verbindung erfolgreich
                self._connected = True
                self.connection_status_changed.emit(True)
                self.logger.info(f"Verbunden mit System {self._system_id}, Component {self._component_id}")
                
                # Message Thread starten
                self._start_message_thread()
                
                # Datenströme anfordern
                self._request_data_streams()
                
                return True
                
        except Exception as e:
            self.logger.error(f"Verbindungsfehler: {str(e)}")
            self._cleanup_connection()
            self.error_occurred.emit(str(e))
            return False
            
    def disconnect(self) -> None:
        """Trennt die MAVLink-Verbindung"""
        with self._lock:
            if not self._connected:
                return
                
            self.logger.info("Trenne Verbindung...")
            self._running = False
            
            if self._message_thread:
                self._message_thread.join(timeout=2.0)
                self._message_thread = None
            
            if self._connection:
                try:
                    self._connection.close()
                except:
                    pass
                self._connection = None
            
            self._cleanup_connection()
            
    def _cleanup_connection(self) -> None:
        """Räumt Verbindungsressourcen auf"""
        self._connected = False
        self._system_id = None
        self._component_id = None
        self._last_heartbeat = 0
        self.connection_status_changed.emit(False)
        
    def _start_message_thread(self) -> None:
        """Startet den Message-Thread"""
        self._running = True
        self._message_thread = threading.Thread(target=self._message_loop)
        self._message_thread.daemon = True
        self._message_thread.start()
        
    def _message_loop(self) -> None:
        """Hauptschleife für MAVLink-Nachrichten"""
        while self._running:
            try:
                msg = self._connection.recv_match(blocking=True, timeout=1.0)
                if msg:
                    self._handle_message(msg)
            except Exception as e:
                self.logger.error(f"Fehler im Message-Loop: {str(e)}")
                if not self._running:
                    break
                    
    def _handle_message(self, msg: mavlink.MAVLink_message) -> None:
        """Verarbeitet eine MAVLink-Nachricht"""
        try:
            msg_type = msg.get_type()
            
            # Heartbeat aktualisieren
            if msg_type == "HEARTBEAT":
                self._last_heartbeat = time.time()
                self.heartbeat_received.emit()
                
            # Nachricht an Handler weiterleiten
            self.message_received.emit(msg)
            
            # Spezifische Nachrichtentypen verarbeiten
            if msg_type == "ATTITUDE":
                self.attitude_updated.emit(
                    math.degrees(msg.roll),
                    math.degrees(msg.pitch),
                    math.degrees(msg.yaw)
                )
            elif msg_type == "GLOBAL_POSITION_INT":
                self.gps_updated.emit(
                    msg.lat / 1e7,
                    msg.lon / 1e7,
                    msg.alt / 1e3
                )
            elif msg_type == "SYS_STATUS":
                self.battery_updated.emit(
                    msg.voltage_battery / 1000.0,
                    msg.current_battery / 100.0,
                    msg.battery_remaining
                )
                
        except Exception as e:
            self.logger.error(f"Fehler bei der Nachrichtenverarbeitung: {str(e)}")
            
    def _check_heartbeat(self) -> None:
        """Überprüft den Heartbeat-Status"""
        if not self._connected:
            return
            
        if time.time() - self._last_heartbeat > self.HEARTBEAT_TIMEOUT:
            self.logger.warning("Kein Heartbeat empfangen")
            self._cleanup_connection()
            self.error_occurred.emit("Verbindung verloren: Kein Heartbeat")
            
    def _request_data_streams(self) -> None:
        """Fordert Datenströme vom Fahrzeug an"""
        if not self._connected or not self._system_id:
            return
            
        try:
            # Standard-Datenströme anfordern
            streams = [
                mavutil.mavlink.MAV_DATA_STREAM_RAW_SENSORS,
                mavutil.mavlink.MAV_DATA_STREAM_EXTENDED_STATUS,
                mavutil.mavlink.MAV_DATA_STREAM_RC_CHANNELS,
                mavutil.mavlink.MAV_DATA_STREAM_POSITION,
                mavutil.mavlink.MAV_DATA_STREAM_EXTRA1,  # Attitude
                mavutil.mavlink.MAV_DATA_STREAM_EXTRA2   # VFR_HUD
            ]
            
            for stream_id in streams:
                self._connection.mav.request_data_stream_send(
                    self._system_id,
                    self._component_id,
                    stream_id,
                    10,  # 10 Hz
                    1    # Start
                )
                
            self.logger.info("Datenströme angefordert")
            
        except Exception as e:
            self.logger.error(f"Fehler beim Anfordern der Datenströme: {str(e)}")
            
    def send_message(self, message: mavlink.MAVLink_message) -> bool:
        """
        Sendet eine MAVLink-Nachricht.
        
        Args:
            message: Zu sendende MAVLink-Nachricht
            
        Returns:
            bool: True bei erfolgreicher Übertragung
        """
        if not self._connected or not self._connection:
            self.logger.error("Keine aktive Verbindung")
            return False
            
        try:
            with self._lock:
                self._connection.mav.send(message)
            return True
        except Exception as e:
            self.logger.error(f"Fehler beim Senden der Nachricht: {str(e)}")
            return False
