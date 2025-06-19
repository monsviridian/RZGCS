"""
Implementierung der verschiedenen Verbindungstypen
"""

import serial
import socket
import sys
import logging
import threading
from typing import Optional, Union, List, Dict
from .enums import ConnectionType, ConnectionStatus
import serial.tools.list_ports
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class ConnectionType(Enum):
    """Verfügbare Verbindungstypen"""
    SERIAL = "Serial"
    UDP = "UDP"
    TCP = "TCP"
    SIMULATOR = "Simulator"

class ConnectionStatus(Enum):
    """Mögliche Verbindungsstatus"""
    DISCONNECTED = "DISCONNECTED"
    CONNECTING = "CONNECTING"
    CONNECTED = "CONNECTED"
    ERROR = "ERROR"

@dataclass
class SerialPortInfo:
    """Informationen über einen seriellen Port"""
    device: str
    description: str
    hwid: str
    vid: int
    pid: int
    serial_number: str
    manufacturer: str
    interface: str

class BaseConnection(ABC):
    """Basisklasse für alle Verbindungstypen"""
    
    def __init__(self):
        self._connected = False
        self._last_heartbeat = 0
        self._connection_timeout = 5.0  # 5 Sekunden Timeout
        # Callback für eingehende Daten (z.B. ConnectionManager._handle_message)
        self._data_callback = None
    
    def register_callback(self, callback):
        """Registriert einen Callback, der bei eingehenden Daten aufgerufen wird"""
        self._data_callback = callback
        
    @abstractmethod
    def establish_connection(self) -> None:
        """Verbindung herstellen (muss von Unterklassen implementiert werden)"""
        pass
        
    # Alias für Abwärtskompatibilität    
    def connect(self) -> None:
        """Legacy-Alias für establish_connection"""
        return self.establish_connection()
        
    @abstractmethod
    def disconnect(self) -> None:
        """Verbindung trennen (muss von Unterklassen implementiert werden)"""
        pass
        
    def is_alive(self) -> bool:
        """Prüft ob die Verbindung aktiv ist"""
        if not self._connected:
            return False
        return (time.time() - self._last_heartbeat) < self._connection_timeout
        
    @abstractmethod
    def send_message(self, message: bytes) -> None:
        """Nachricht senden (muss von Unterklassen implementiert werden)"""
        pass
        
    @abstractmethod
    def receive_message(self) -> bytes:
        """Nachricht empfangen (muss von Unterklassen implementiert werden)"""
        pass

class SerialConnection(BaseConnection):
    """Implementiert serielle Verbindungen"""
    
    # Unterstützte Baudraten
    supported_baudrates = [
        9600, 14400, 19200, 38400, 57600, 115200, 230400, 460800, 921600
    ]
    
    def __init__(self):
        super().__init__()
        self._serial = None
        self._port = None
        self._baudrate = None
        self._available_ports: List[SerialPortInfo] = []
        self._last_port_scan = 0
        self._port_scan_interval = 1.0  # Ports alle 1 Sekunde aktualisieren
        self._configuration = {}
        self._connected = False
        self._logger = logging.getLogger(__name__)  # Initialize logger
        
    @property
    def port(self) -> str:
        """Gibt den aktuell konfigurierten Port zurück"""
        return self._port if self._port else "unknown"
        
    @property
    def baudrate(self) -> int:
        """Gibt die aktuell konfigurierte Baudrate zurück"""
        return self._baudrate if self._baudrate else 115200
        
    def get_available_ports(self, force_refresh: bool = False) -> List[SerialPortInfo]:
        """
        Gibt eine Liste aller verfügbaren seriellen Ports zurück.
        
        Args:
            force_refresh: Wenn True, wird die Liste auch aktualisiert wenn das Scan-Intervall
                         noch nicht abgelaufen ist
                         
        Returns:
            Liste von SerialPortInfo-Objekten mit Informationen zu jedem Port
        """
        current_time = time.time()
        
        # Nur aktualisieren wenn nötig
        if not force_refresh and (current_time - self._last_port_scan) < self._port_scan_interval:
            return self._available_ports
            
        self._available_ports = []
        ports = serial.tools.list_ports.comports()
        
        for port in ports:
            port_info = SerialPortInfo(
                device=port.device,
                description=port.description,
                hwid=port.hwid,
                vid=port.vid,
                pid=port.pid,
                serial_number=port.serial_number,
                manufacturer=port.manufacturer,
                interface=port.interface
            )
            self._available_ports.append(port_info)
            
        self._last_port_scan = current_time
        return self._available_ports
        
    def get_port_by_description(self, description: str) -> Optional[SerialPortInfo]:
        """
        Findet einen Port anhand seiner Beschreibung.
        
        Args:
            description: Beschreibung des Ports
            
        Returns:
            SerialPortInfo des gefundenen Ports oder None
        """
        ports = self.get_available_ports()
        for port in ports:
            if description.lower() in port.description.lower():
                return port
        return None
        
    def get_port_by_serial(self, serial_number: str) -> Optional[SerialPortInfo]:
        """
        Findet einen Port anhand seiner Seriennummer.
        
        Args:
            serial_number: Seriennummer des Ports
            
        Returns:
            SerialPortInfo des gefundenen Ports oder None
        """
        ports = self.get_available_ports()
        for port in ports:
            if serial_number == port.serial_number:
                return port
        return None
        
    def get_port_by_vid_pid(self, vid: int, pid: int) -> Optional[SerialPortInfo]:
        """
        Findet einen Port anhand seiner VID/PID.
        
        Args:
            vid: Vendor ID
            pid: Product ID
            
        Returns:
            SerialPortInfo des gefundenen Ports oder None
        """
        ports = self.get_available_ports()
        for port in ports:
            if port.vid == vid and port.pid == pid:
                return port
        return None
        
    def _validate_port_exists(self, port):
        """Überprüft, ob der angegebene serielle Port existiert
        
        Args:
            port: Der zu überprüfende Port-Name (z.B. 'COM3' oder 'com3')
            
        Returns:
            bool: True wenn der Port existiert, False sonst
        """
        try:
            import serial.tools.list_ports
            
            # Port-Name bereinigen (z.B. 'COM3:115200' -> 'COM3')
            if ":" in port:
                port = port.split(":")[0]
            
            # Alle verfügbaren Ports abrufen
            available_ports = [p.device for p in serial.tools.list_ports.comports()]
            print(f"[DEBUG] Verfügbare serielle Ports: {available_ports}")
            
            # Case-insensitive Überprüfung
            port_exists = any(p.lower() == port.lower() for p in available_ports)
            
            if not port_exists:
                print(f"[ERROR] Der Port '{port}' existiert nicht auf diesem System")
                print(f"[INFO] Verfügbare Ports: {', '.join(available_ports)}")
            
            return port_exists
            
        except ImportError:
            print("[WARNING] serial.tools.list_ports nicht verfügbar, überspringe Port-Validierung")
            return True  # Überspringe die Validierung, wenn das Modul nicht verfügbar ist
        except Exception as e:
            print(f"[WARNING] Fehler bei der Port-Validierung: {e}")
            return True  # Fehler bei der Validierung, wir lassen es trotzdem zu
            
    def establish_connection(self, port: str = None, baudrate: int = None):
        """
        Stellt eine serielle Verbindung her mit robusteren Parametern im Mission Planner-Stil.
        
        Args:
            port: Der COM-Port für die Verbindung (optional, verwendet intern gespeicherten Port wenn None)
            baudrate: Die Baudrate (optional, verwendet intern gespeicherte Baudrate wenn None)
            
        Returns:
            True wenn die Verbindung erfolgreich hergestellt wurde, sonst False
        """
        import sys
        import os
        import platform
        try:
            from pymavlink import mavutil
        except ImportError:
            print("[ERROR] pymavlink nicht installiert!")
            return False
        
        # Vorhandene Verbindung trennen
        self.disconnect()
        
        # Port und Baudrate übernehmen oder verwenden
        if port is not None:
            # Prüfe, ob der übergebene Port ein Callback anstatt eines Strings ist (häufiger Fehler)
            if callable(port):
                print(f"[ERROR] Port ist ein Callback/Funktion ({port.__name__ if hasattr(port, '__name__') else type(port).__name__}), kein String!")
                return False
            self._port = port
        if baudrate is not None:
            self._baudrate = baudrate
        
        # Prüfen ob Port und Baudrate gesetzt sind
        if not self._port:
            print("[ERROR] Kein Port angegeben!")
            return False
        if not self._baudrate:
            self._baudrate = 115200  # Default
            
        print(f"[INFO] Versuche Verbindung zu Port {self._port} mit Baudrate {self._baudrate}")
        
        try:
            # Standard-Port-Formatierung für Windows
            plat = platform.system().lower()
            mavlink_port = self._port
            
            # Prüfe auf Simulator
            if mavlink_port.lower() == "simulator":
                mavlink_port = "tcp:127.0.0.1:5760"  # Standard SITL Adresse
                print(f"[INFO] Simulator erkannt, verwende {mavlink_port}")
            
            # Windows-spezifische Konvertierung für MAVLink
            elif plat.startswith('win'):
                if mavlink_port.upper().startswith("COM"):
                    # pymavlink für Windows erwartet kleinbuchstaben (comX anstatt COMX)
                    com_port_normalized = mavlink_port.lower()
                    # Wenn eine Baudrate im Port-String angegeben ist (z.B. "COM3:115200")
                    if ":" in com_port_normalized:
                        parts = com_port_normalized.split(":")
                        if len(parts) > 1 and parts[1].isdigit():
                            self._baudrate = int(parts[1])
                            print(f"[INFO] Baudrate aus Port-String übernommen: {self._baudrate}")
                        com_port_normalized = parts[0]  # Nur der Port-Name
                    mavlink_port = com_port_normalized
                    print(f"[INFO] Windows COM-Port normalisiert zu '{mavlink_port}'")
            
            # Überprüfen, ob der Port existiert
            if not self._validate_port_exists(mavlink_port):
                self._logger.error(f"Verbindungsaufbau abgebrochen: Port {mavlink_port} existiert nicht")
                return False
            
            # System und Component IDs für die GCS
            source_system_id = 1      # Standard System ID für Ground Control Stations
            source_component_id = 190  # MAV_COMP_ID_MISSIONPLANNER (190) für GCS
            
            # MAVLink Verbindung herstellen
            print(f"[DEBUG] Öffne MAVLink-Verbindung zu {mavlink_port} mit Baudrate {self._baudrate}")
            print(f"[DEBUG] Verwende System-ID: {source_system_id}, Component-ID: {source_component_id}")
            
            self._serial = mavutil.mavlink_connection(
                mavlink_port,
                baud=self._baudrate,
                source_system=source_system_id,
                source_component=source_component_id
            )
            
            if not self._serial:
                print(f"[ERROR] Konnte keine Verbindung zu {mavlink_port} herstellen!")
                return False
                
            # Warte auf Heartbeat, um sicherzustellen, dass die Verbindung funktioniert
            print("[INFO] Warte auf ersten Heartbeat...")
            try:
                self._logger.debug(f"Warte auf Heartbeat von {mavlink_port} (Timeout: 5s)...")
                heartbeat_start = time.time()
                self._serial.wait_heartbeat(timeout=5)
                heartbeat_time = time.time() - heartbeat_start
                
                # Details zum Heartbeat protokollieren
                self._logger.info(f"✅ Verbunden mit {mavlink_port}, Heartbeat empfangen nach {heartbeat_time:.2f}s")
                try:
                    # Systeminformationen extrahieren, wenn vorhanden
                    last_msg = self._serial.messages.get('HEARTBEAT')
                    if last_msg:
                        autopilot = mavutil.mavlink.enums['MAV_AUTOPILOT'][last_msg.autopilot].description
                        vehicle = mavutil.mavlink.enums['MAV_TYPE'][last_msg.type].description
                        system_id = last_msg.get_srcSystem()
                        component_id = last_msg.get_srcComponent()
                        self._logger.info(f"Verbunden mit: {autopilot} ({vehicle}), System-ID: {system_id}, Komponenten-ID: {component_id}")
                except Exception as detail_error:
                    self._logger.debug(f"Konnte keine detaillierten Heartbeat-Informationen extrahieren: {detail_error}")
                
                # Verbindung erfolgreich
                self._connected = True
                self._last_heartbeat = time.time()
                
                return True
                
            except Exception as e:
                self._logger.error(f"❌ Konnte keinen Heartbeat empfangen: {e}")
                self._stop_read_thread()
                return False
                
            # Threading für kontinuierliches Lesen starten
            self._connected = True
            self._read_thread = threading.Thread(target=self._read_loop, daemon=True)
            self._read_thread.start()
            
            print(f"[INFO] MAVLink-Verbindung erfolgreich auf {mavlink_port}:{self._baudrate}")
            return True
            
        except Exception as e:
            import traceback
            print(f"[ERROR] Fehler beim Verbindungsaufbau: {str(e)}")
            traceback.print_exc()
            self._connected = False
            return False
        
    # Alias für Abwärtskompatibilität    
    def connect(self, port: str = None, baudrate: int = None) -> bool:
        """Legacy-Alias für establish_connection"""
        return self.establish_connection(port=port, baudrate=baudrate)
    
    def _read_loop(self):
        """Kontinuierliches Lesen im Hintergrund"""
        consecutive_errors = 0
        max_consecutive_errors = 10
        
        print("[INFO] MAVLink-Lesethread gestartet")
        
        while self._connected and self._serial:
            try:
                # Nachricht lesen
                msg = self._serial.recv_msg()
                if msg:
                    # Heartbeat-Zeitstempel aktualisieren
                    msg_type = msg.get_type()
                    if msg_type == "HEARTBEAT":
                        self._last_heartbeat = time.time()
                        # Verbose Debug alle 10 Sekunden
                        if int(self._last_heartbeat) % 10 == 0:
                            print(f"[DEBUG] Heartbeat empfangen: SYS={msg.get_srcSystem()} COMP={msg.get_srcComponent()}")
                    
                    # Callback aufrufen, wenn einer registriert ist
                    if self._data_callback and msg.get_msgbuf():
                        self._data_callback(msg.get_msgbuf())
                        
                        # Debug-Ausgabe für spezifische Nachrichtentypen
                        if msg_type in ["STATUSTEXT", "SYS_STATUS", "PARAM_VALUE"]:
                            print(f"[DEBUG] MAVLink {msg_type} empfangen")
                        
                else:
                    # Kurze Pause, wenn keine Nachricht empfangen wurde
                    time.sleep(0.001)
                    
                # Fehler zurücksetzen, wenn erfolgreich gelesen wurde
                consecutive_errors = 0
                
            except Exception as e:
                consecutive_errors += 1
                print(f"[ERROR] Fehler beim Lesen ({consecutive_errors}/{max_consecutive_errors}): {str(e)}")
                
                # Bei zu vielen Fehlern hintereinander abbrechen
                if consecutive_errors >= max_consecutive_errors:
                    print("[ERROR] Zu viele Lesefehler hintereinander, Verbindung wird getrennt")
                    self._connected = False
                    break
                    
                # Kurze Pause nach Fehler
                time.sleep(0.1)
        
        print("[INFO] MAVLink-Lesethread beendet")
    
    def disconnect(self) -> None:
        """Serielle Verbindung trennen"""
        print("[INFO] Trenne serielle Verbindung...")
        self._connected = False
        
        # Thread beenden
        if hasattr(self, '_read_thread') and self._read_thread:
            if self._read_thread.is_alive():
                print("[DEBUG] Warte auf Beendigung des Lesethreads...")
                # Warten bis der Thread beendet ist (max 1s)
                self._read_thread.join(1.0)
                if self._read_thread.is_alive():
                    print("[WARNING] Lesethread konnte nicht sauber beendet werden")
        
        # Serielle Verbindung schließen
        if self._serial:
            try:
                self._serial.close()
                print("[INFO] MAVLink-Verbindung geschlossen")
            except Exception as e:
                print(f"[WARNING] Fehler beim Schließen der Verbindung: {str(e)}")
            self._serial = None
        
    def send_message(self, message: bytes) -> None:
        """
        Nachricht über die serielle Verbindung senden
        
        Args:
            message: Zu sendende Nachricht als Bytes
        """
        if not self._connected or not self._serial:
            raise ConnectionError("Keine aktive Verbindung")
            
        try:
            self._serial.write(message)
            self._last_heartbeat = time.time()
        except serial.SerialException as e:
            self._connected = False
            raise ConnectionError(f"Fehler beim Senden: {str(e)}")
            
    def receive_message(self) -> bytes:
        """
        Empfängt eine Nachricht von der seriellen Verbindung.
        
        Returns:
            Empfangene Nachricht als Bytes
        """
        if not self._connected or not self._serial:
            raise ConnectionError("Keine aktive Verbindung")
            
        try:
            if self._serial.in_waiting:
                message = self._serial.read(self._serial.in_waiting)
                self._last_heartbeat = time.time()
                return message
            return b''
        except serial.SerialException as e:
            self._connected = False
            raise ConnectionError(f"Fehler beim Empfangen: {str(e)}")
            
    def configure(self, config_dict: Dict) -> None:
        """
        Konfiguriert die serielle Verbindung mit den angegebenen Parametern.
        
        Args:
            config_dict: Dictionary mit Konfigurationsparametern
        """
        self._configuration.update(config_dict)
        
        # Wenn port und baudrate in der Konfiguration sind, direkt verwenden
        if 'port' in config_dict:
            self._port = config_dict['port']
        
        if 'baudrate' in config_dict:
            self._baudrate = config_dict['baudrate']
            
        return True
        
    def is_connected(self) -> bool:
        """Prüft ob die Verbindung aktiv ist"""
        if not self._connected or not self._serial:
            return False
        try:
            # For MAVLink connections, check if we can still receive messages
            return self._connected and self._serial and self._serial.mavlink10()
        except Exception:
            return False

class UDPConnection(BaseConnection):
    """UDP Verbindung"""
    
    def __init__(self):
        super().__init__()
        self.default_ports = {
            'local': 14550,  # Standard MAVLink UDP Port
            'remote': 14540  # Standard GCS UDP Port
        }
    
    def connect(self, host: str, port: Optional[int] = None) -> None:
        """
        UDP Verbindung herstellen
        
        Args:
            host: Host-IP oder Hostname
            port: Port für die Verbindung (optional)
            
        Raises:
            ConnectionError: Wenn die Verbindung fehlschlägt
        """
        if port is None:
            port = self.default_ports['remote']
        
        try:
            self._connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self._connection.connect((host, port))
            self._connected = True
        except socket.error as e:
            raise ConnectionError(f"Failed to connect to {host}:{port}: {str(e)}")
    
    def disconnect(self) -> None:
        """UDP Verbindung trennen"""
        if self._connection:
            self._connection.close()
            self._connected = False
    
    def send_message(self, message: bytes) -> None:
        """
        Nachricht über UDP Verbindung senden
        
        Args:
            message: Zu sendende Nachricht als Bytes
        """
        if not self._connected or not self._connection:
            raise ConnectionError("Keine aktive Verbindung")
            
        try:
            self._connection.send(message)
            self._last_heartbeat = time.time()
        except socket.error as e:
            self._connected = False
            raise ConnectionError(f"Fehler beim Senden: {str(e)}")
    
    def receive_message(self) -> bytes:
        """
        Nachricht von UDP Verbindung empfangen
        
        Returns:
            Empfangene Nachricht als Bytes
        """
        if not self._connected or not self._connection:
            raise ConnectionError("Keine aktive Verbindung")
            
        try:
            return self._connection.recv(1024)
        except socket.error as e:
            self._connected = False
            raise ConnectionError(f"Fehler beim Empfangen: {str(e)}")

class TCPConnection(BaseConnection):
    """TCP Verbindung"""
    
    def __init__(self):
        super().__init__()
        self.default_port = 5760  # Standard MAVLink TCP Port
        self._connection = None
    
    def establish_connection(self, host: str, port: Optional[int] = None) -> bool:
        """
        TCP Verbindung herstellen
        
        Args:
            host: Host-IP oder Hostname
            port: Port für die Verbindung (optional)
            
        Returns:
            True wenn Verbindung erfolgreich, sonst False
            
        Raises:
            ConnectionError: Wenn die Verbindung fehlschlägt
        """
        if port is None:
            port = self.default_port
        
        try:
            self._connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._connection.connect((host, port))
            self._connected = True
            return True
        except socket.error as e:
            self._connected = False
            error_msg = f"Failed to connect to {host}:{port}: {str(e)}"
            logging.error(error_msg)
            raise ConnectionError(error_msg)
            
    # Alias für Abwärtskompatibilität    
    def connect(self, host: str, port: Optional[int] = None) -> bool:
        """Legacy-Alias für establish_connection"""
        return self.establish_connection(host=host, port=port)
    
    def disconnect(self) -> None:
        """TCP Verbindung trennen"""
        if self._connection:
            self._connection.close()
            self._connected = False
    
    def send_message(self, message: bytes) -> None:
        """
        Nachricht über TCP Verbindung senden
        
        Args:
            message: Zu sendende Nachricht als Bytes
        """
        if not self._connected or not self._connection:
            raise ConnectionError("Keine aktive Verbindung")
            
        try:
            self._connection.send(message)
            self._last_heartbeat = time.time()
        except socket.error as e:
            self._connected = False
            raise ConnectionError(f"Fehler beim Senden: {str(e)}")
    
    def receive_message(self) -> bytes:
        """
        Nachricht von TCP Verbindung empfangen
        
        Returns:
            Empfangene Nachricht als Bytes
        """
        if not self._connected or not self._connection:
            raise ConnectionError("Keine aktive Verbindung")
            
        try:
            return self._connection.recv(1024)
        except socket.error as e:
            self._connected = False
            raise ConnectionError(f"Fehler beim Empfangen: {str(e)}")

class SimulatorConnection(BaseConnection):
    """Simulator Verbindung"""
    
    def establish_connection(self) -> bool:
        """Simulator Verbindung herstellen"""
        self._connected = True
        return True
        
    # Alias für Abwärtskompatibilität
    def connect(self) -> bool:
        """Legacy-Alias für establish_connection"""
        return self.establish_connection()
    
    def disconnect(self) -> None:
        """Simulator Verbindung trennen"""
        self._connected = False
    
    def send_message(self, message: bytes) -> None:
        """
        Nachricht an Simulator senden
        
        Args:
            message: Zu sendende Nachricht als Bytes
        """
        pass
    
    def receive_message(self) -> bytes:
        """
        Nachricht vom Simulator empfangen
        
        Returns:
            Leere Bytes (Simulator implementierung)
        """
        return b'' 