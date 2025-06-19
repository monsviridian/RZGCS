"""
MAVLink Handler Class

Diese Klasse ist verantwortlich für:
1. Herstellung und Verwaltung von MAVLink-Verbindungen
2. Verarbeitung eingehender MAVLink-Nachrichten
3. Anfragen von Datenströmen
4. Senden von MAVLink-Befehlen

Die Klasse bietet eine saubere Schnittstelle für alle MAVLink-bezogenen Operationen.
"""

import time
import math
import threading
from typing import Dict, Any, Callable, Optional, List, Union

from PySide6.QtCore import QObject, Signal

from pymavlink import mavutil

class MAVLinkHandler(QObject):
    """
    MAVLink-Kommunikationsmanager, der eine saubere Trennung der Belange sicherstellt.
    
    Signale:
        heartbeat_received: Emittiert, wenn ein Heartbeat empfangen wird
        attitude_updated: Emittiert, wenn neue Lagedaten (roll, pitch, yaw) empfangen werden
        gps_updated: Emittiert, wenn neue GPS-Daten empfangen werden
        battery_updated: Emittiert, wenn neue Batteriestatus-Daten empfangen werden
        status_text_received: Emittiert, wenn eine Statusnachricht empfangen wird
        connection_state_changed: Emittiert, wenn sich der Verbindungsstatus ändert
    """
    
    # Signal-Definitionen
    heartbeat_received = Signal(object)  # object = msg
    attitude_updated = Signal(float, float, float)  # roll, pitch, yaw in Grad
    gps_updated = Signal(float, float, float)  # lat, lon, alt
    battery_updated = Signal(float, float, float)  # voltage, current, remaining
    status_text_received = Signal(str)  # text message
    connection_state_changed = Signal(bool)  # connected: True/False
    error_occurred = Signal(str)  # Fehlermeldung
    
    # Verbindungsstatus-Konstanten
    DISCONNECTED = 0
    CONNECTING = 1
    CONNECTED = 2
    ERROR = 3
    
    # MAVLink Stream IDs
    MAV_DATA_STREAM_RAW_SENSORS = 1
    MAV_DATA_STREAM_EXTENDED_STATUS = 2
    MAV_DATA_STREAM_RC_CHANNELS = 3
    MAV_DATA_STREAM_POSITION = 6
    MAV_DATA_STREAM_EXTRA1 = 10  # Attitude
    MAV_DATA_STREAM_EXTRA2 = 11  # VFR_HUD
    
    def __init__(self, logger=None):
        """Initialisiert den MAVLink-Handler"""
        super().__init__()
        
        # Verbindungsvariablen
        self.connection = None
        self.device = ""
        self.baudrate = 115200
        self.target_system = None
        self.target_component = None
        self.connection_status = self.DISCONNECTED
        
        # Threading
        self.message_thread = None
        self.running = False
        self.last_heartbeat_time = 0
        
        # Logger
        self.logger = logger
        
        # Timer für Verbindungsüberwachung
        # (Wird in SerialConnector durch QTimer ersetzt)
        self.last_connection_check = 0
        self.heartbeat_timeout = 5.0  # 5 Sekunden ohne Heartbeat = Verbindungsverlust
    
    def log(self, message):
        """Gibt eine Nachricht an den Logger weiter, wenn vorhanden"""
        if self.logger:
            self.logger.addLog(message)
        else:
            print(message)
    
    def connect(self, device, baud=115200, source_system=255, source_component=190):
        """
        Stellt eine MAVLink-Verbindung zum angegebenen Gerät her
        
        Args:
            device: Der Gerätepfad (z.B. "COM3" oder "udp://127.0.0.1:14550")
            baud: Baudrate für serielle Verbindungen
            source_system: System ID der Ground Control Station
            source_component: Component ID der Ground Control Station
            
        Returns:
            bool: True bei erfolgreicher Verbindung, sonst False
        """
        try:
            self.device = device
            self.baudrate = baud
            self.connection_status = self.CONNECTING
            
            self.log(f"Verbinde zu {device} mit {baud} Baud...")
            
            # Windows-spezifische COM-Port-Normalisierung
            if device.upper().startswith("COM"):
                # Verwende kleingeschriebenes Format für pymavlink
                device = device.lower()
                self.log(f"Windows COM-Port normalisiert zu '{device}'")
            
            # MAVLink-Verbindung erstellen
            self.connection = mavutil.mavlink_connection(
                device=device,
                baud=baud,
                source_system=source_system,
                source_component=source_component
            )
            
            self.log("Warte auf ersten Heartbeat...")
            msg = self.connection.wait_heartbeat(timeout=10.0)
            if not msg:
                self.log("ERROR: Kein Heartbeat empfangen!")
                self.connection_status = self.ERROR
                if self.connection:
                    self.connection.close()
                    self.connection = None
                self.connection_state_changed.emit(False)
                return False
            
            # Target System und Component aus Heartbeat speichern
            self.target_system = self.connection.target_system
            self.target_component = self.connection.target_component
            
            self.log(f"Verbunden mit System {self.target_system}, Komponente {self.target_component}")
            
            # Sichere Zugriffe auf MAVLink-Eigenschaften über die messages-Attribute
            try:
                mav_type = self.connection.target_system_type or "Unbekannt"
                self.log(f"Fahrzeugtyp: {mav_type}")
            except AttributeError:
                self.log("Fahrzeugtyp konnte nicht ermittelt werden")
            
            # Datenströme anfordern
            self.request_data_streams()
            
            # Message-Handling-Thread starten
            self.start_message_thread()
            
            # Verbindungsstatus aktualisieren
            self.connection_status = self.CONNECTED
            self.last_heartbeat_time = time.time()
            self.connection_state_changed.emit(True)
            
            return True
            
        except Exception as e:
            self.log(f"Verbindungsfehler: {str(e)}")
            self.connection_status = self.ERROR
            if self.connection:
                try:
                    self.connection.close()
                except:
                    pass
                self.connection = None
            self.connection_state_changed.emit(False)
            return False
    
    def request_data_streams(self, rate_hz=10):
        """
        Fordert alle wichtigen Datenströme vom Fahrzeug an
        
        Args:
            rate_hz: Rate der Datenströme in Hz
            
        Returns:
            bool: True bei erfolgreicher Anforderung, sonst False
        """
        if not self.connection or not self.target_system:
            return False
        
        streams = [
            self.MAV_DATA_STREAM_RAW_SENSORS,
            self.MAV_DATA_STREAM_EXTENDED_STATUS,
            self.MAV_DATA_STREAM_POSITION,
            self.MAV_DATA_STREAM_EXTRA1,  # Attitude
            self.MAV_DATA_STREAM_EXTRA2   # VFR_HUD
        ]
        
        for stream_id in streams:
            self.connection.mav.request_data_stream_send(
                self.target_system,
                self.target_component,
                stream_id,
                rate_hz,  # Hz
                1         # Start
            )
            
        self.log(f"Datenströme angefordert mit {rate_hz} Hz")
        return True
    
    def start_message_thread(self):
        """Startet den MAVLink-Nachrichten-Thread"""
        if self.message_thread and self.message_thread.is_alive():
            self.log("MAVLink-Message-Thread läuft bereits")
            return
        
        self.running = True
        self.message_thread = threading.Thread(target=self._message_loop)
        self.message_thread.daemon = True
        self.message_thread.start()
        self.log("MAVLink-Message-Thread gestartet")
    
    def stop_message_thread(self):
        """Stoppt den MAVLink-Nachrichten-Thread sicher"""
        if not self.message_thread:
            return
        
        self.running = False
        if self.message_thread.is_alive():
            self.message_thread.join(timeout=2.0)
        self.message_thread = None
        self.log("MAVLink-Message-Thread gestoppt")
    
    def _message_loop(self):
        """
        Hauptschleife für die MAVLink-Nachrichtenverarbeitung
        Läuft in einem separaten Thread
        """
        self.log("MAVLink-Nachrichten-Loop gestartet")
        
        while self.running and self.connection:
            try:
                # Nicht-blockierendes Lesen mit Timeout
                msg = self.connection.recv_match(blocking=True, timeout=0.1)
                
                if msg:
                    # Verarbeite die Nachricht nach Typ
                    msg_type = msg.get_type()
                    
                    # Debug output for message types we received
                    # self.log(f"MAVLink-Nachricht empfangen: {msg_type}")
                    
                    if msg_type == 'HEARTBEAT':
                        # Aktualisiere Zeitstempel des letzten Heartbeats
                        self.last_heartbeat_time = time.time()
                        # Emittiere Signal mit der Heartbeat-Nachricht
                        self.heartbeat_received.emit(msg)
                        
                    elif msg_type == 'ATTITUDE':
                        # Umrechnung von rad in Grad
                        roll = math.degrees(msg.roll)
                        pitch = math.degrees(msg.pitch)
                        yaw = math.degrees(msg.yaw)
                        # Signal emittieren
                        self.attitude_updated.emit(roll, pitch, yaw)
                        
                    elif msg_type == 'GPS_RAW_INT':
                        # GPS-Daten konvertieren (lat/lon von 10e7 zu Grad, alt von mm zu m)
                        lat = msg.lat / 1e7
                        lon = msg.lon / 1e7
                        alt = msg.alt / 1000.0
                        # Signal emittieren
                        self.gps_updated.emit(lat, lon, alt)
                        
                    elif msg_type == 'SYS_STATUS':
                        # Batterie-Daten konvertieren
                        voltage = msg.voltage_battery / 1000.0  # mV zu V
                        current = msg.current_battery / 100.0   # 10*mA zu A
                        remaining = msg.battery_remaining       # 0-100%
                        # Signal emittieren
                        self.battery_updated.emit(voltage, current, remaining)
                        
                    elif msg_type == 'STATUSTEXT':
                        # Statustext-Nachricht verarbeiten
                        status_text = msg.text.decode('utf-8', errors='replace') if isinstance(msg.text, bytes) else str(msg.text)
                        # Signal emittieren
                        self.status_text_received.emit(status_text)
                
            except Exception as e:
                self.log(f"Fehler in MAVLink-Message-Loop: {str(e)}")
                time.sleep(0.5)  # Kurze Pause bei Fehlern, um CPU-Last zu reduzieren
        
        self.log("MAVLink-Nachrichten-Loop beendet")
    
    def check_connection_status(self):
        """
        Überprüft den aktuellen Verbindungsstatus basierend auf Heartbeat-Zeitstempel
        
        Returns:
            bool: True wenn verbunden, False wenn getrennt
        """
        if not self.connection or self.connection_status != self.CONNECTED:
            return False
        
        current_time = time.time()
        time_since_last_heartbeat = current_time - self.last_heartbeat_time
        
        if time_since_last_heartbeat > self.heartbeat_timeout:
            # Kein Heartbeat für zu lange Zeit - verbindung vermutlich verloren
            self.log(f"Verbindung verloren: Kein Heartbeat seit {time_since_last_heartbeat:.1f} Sekunden")
            self.connection_status = self.DISCONNECTED
            self.connection_state_changed.emit(False)
            return False
        
        return True
    
    def disconnect(self):
        """
        Trennt die MAVLink-Verbindung sauber
        
        Returns:
            bool: True bei erfolgreicher Trennung, sonst False
        """
        try:
            self.log("Trenne MAVLink-Verbindung...")
            
            # Message Thread stoppen
            self.stop_message_thread()
            
            # Alle Datenströme stoppen
            if self.connection and self.target_system:
                for stream_id in range(0, 13):  # Alle möglichen Stream IDs stoppen
                    try:
                        self.connection.mav.request_data_stream_send(
                            self.target_system,
                            self.target_component,
                            stream_id,
                            0,  # 0 Hz = aus
                            0   # Stop
                        )
                    except:
                        pass  # Fehler beim Stoppen einzelner Streams ignorieren
            
            # Verbindung schließen
            if self.connection:
                self.connection.close()
                self.connection = None
            
            # Status aktualisieren
            self.connection_status = self.DISCONNECTED
            self.connection_state_changed.emit(False)
            self.log("MAVLink-Verbindung erfolgreich getrennt")
            
            return True
            
        except Exception as e:
            self.log(f"Fehler beim Trennen der MAVLink-Verbindung: {str(e)}")
            # Trotz Fehler Status auf getrennt setzen
            self.connection_status = self.DISCONNECTED
            self.connection_state_changed.emit(False)
            return False
    
    def is_connected(self):
        """
        Gibt den aktuellen Verbindungsstatus zurück
        
        Returns:
            bool: True wenn verbunden, False wenn nicht
        """
        return self.connection_status == self.CONNECTED and self.connection is not None
        
    def get_mavlink_connection(self):
        """
        Gibt das MAVLink-Verbindungsobjekt zurück
        
        Returns:
            mavutil.mavlink_connection: Das MAVLink-Verbindungsobjekt oder None
        """
        return self.connection
    
    def send_command(self, command_type, param1=0, param2=0, param3=0, param4=0, param5=0, param6=0, param7=0):
        """
        Sendet einen MAVLink-Befehl an das Fahrzeug
        
        Args:
            command_type: MAVLink-Befehlstyp
            param1-7: Befehlsparameter
            
        Returns:
            bool: True bei erfolgreichem Senden, sonst False
        """
        if not self.connection or not self.target_system:
            self.log("Kann Befehl nicht senden: Keine Verbindung")
            return False
        
        try:
            self.connection.mav.command_long_send(
                self.target_system,
                self.target_component,
                command_type,
                0,  # confirmation
                param1, param2, param3, param4, param5, param6, param7
            )
            self.log(f"Befehl {command_type} gesendet")
            return True
        except Exception as e:
            self.log(f"Fehler beim Senden des Befehls {command_type}: {str(e)}")
            return False
