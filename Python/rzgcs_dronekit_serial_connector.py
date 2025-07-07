"""
DroneKit Serial Connector für RZGCS
Verbindet die DroneKit-Funktionalität mit der QML-UI
"""

from PySide6.QtCore import QObject, Signal, Slot, Property, QTimer
import sys
import os
import time
import threading
import serial
import glob
from typing import Optional, List
from PySide6.QtQml import qmlRegisterType

# Pfad zum backend-Modul hinzufügen
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

# DroneKit-Connector importieren
try:
    from backend.rzgcs_dronekit.connector import DroneKitConnector
except ImportError:
    print("WARNUNG: DroneKit-Connector nicht gefunden")
    DroneKitConnector = None


class DroneKitSerialConnector(QObject):
    """
    Wrapper-Klasse für DroneKitConnector, die kompatible Signale und Slots
    für die QML-UI bereitstellt.
    """

    # Verbindungs-Signale
    connectionChanged = Signal(bool)           # Für QML Property-Binding (früher 'connected')
    connectedChanged = Signal()                # Für QML Property-Binding
    connectionStatusChanged = Signal(int)      # Status-Code für UI
    availablePortsChanged = Signal()           # Signal für die Aktualisierung der Port-Liste
    
    # Telemetrie-Signale
    attitudeChanged = Signal(float, float, float)  # roll, pitch, yaw
    gpsChanged = Signal(float, float, float)       # lat, lon, alt
    batteryChanged = Signal(float, float, float)   # voltage, current, percent
    
    # Log und Nachrichten-Signale
    messageReceived = Signal(str)
    statusTextReceived = Signal(str)
    errorOccurred = Signal(str)
    
    # Mission und Parameter-Signale
    mission_received = Signal(object)  # mission dict
    waypoint_reached = Signal(int)  # waypoint index
    mission_completed = Signal()  # mission completed
    mission_upload_complete = Signal(bool, str)  # success, message
    mission_download_complete = Signal(bool, str)  # success, message
    parameters_received = Signal(list)
    parameter_updated = Signal(str, float)
    parameter_write_complete = Signal(str, bool)

    # Enums für Connection-Status
    CONNECTION_STATUS_DISCONNECTED = 0
    CONNECTION_STATUS_CONNECTING = 1
    CONNECTION_STATUS_CONNECTED = 2
    CONNECTION_STATUS_ERROR = 3
    CONNECTION_STATUS_FAILED = 4

    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Verbindungseigenschaften
        self._port = "COM1"
        self._baud_rate = 115200
        self._is_connected = False
        # Standardmäßige Port-Liste (wird durch load_ports überschrieben)
        self._available_ports = [
            "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8",
            "/dev/ttyACM0", "/dev/ttyUSB0", "tcp:127.0.0.1:5760", "udp:127.0.0.1:14550", "udp:192.168.4.1:14550"
        ]
        self._connection_status = self.CONNECTION_STATUS_DISCONNECTED
        
        # DroneKit-Connector
        self._drone_connector = None
        self._connection_string = ""
        
        # Threading
        self._thread = None
        self._stop_event = threading.Event()
        
        # Automatisch nach verfügbaren Ports suchen beim Start
        # Verwende QTimer.singleShot nur im Hauptthread
        if parent:
        QTimer.singleShot(500, self.load_ports)  # Nach 500ms, um UI nicht zu blockieren
        
        print("DroneKitSerialConnector initialisiert")

    @Slot()
    def connect(self):
        """Verbindet zum Flugcontroller über DroneKit"""
        if self._is_connected:
            print("Bereits verbunden")
            return True
            
        print(f"Verbinde zu: {self._port} mit Baudrate: {self._baud_rate}")
        
        # Verbindungsstatus aktualisieren
        self._set_connection_status(self.CONNECTION_STATUS_CONNECTING)
        
        # Verbindungsstring erstellen
        if "://" in self._port:  # URL-Format
            self._connection_string = self._port
        elif ":" in self._port and ("tcp" in self._port or "udp" in self._port):  # TCP/UDP mit Doppelpunkt
            self._connection_string = self._port
        elif "tcp" in self._port or "udp" in self._port:  # TCP/UDP ohne Doppelpunkt
            self._connection_string = self._port
        else:  # Serielle Verbindung
            # Prüfen, ob der Port bereits eine Baudrate enthält
            if ":" in self._port:
                parts = self._port.split(":")
                self._port = parts[0]
                try:
                    self._baud_rate = int(parts[1])
                    print(f"Baudrate aus Verbindungsstring extrahiert: {self._baud_rate}")
                except (ValueError, IndexError):
                    pass
            
            self._connection_string = f"{self._port}:{self._baud_rate}"
            
        print(f"Verbindungsstring erstellt: {self._connection_string}")
        
        # Synchrone Verbindung starten
        self._start_connection_thread()
        
        return True
        
    def _start_connection_thread(self):
        """Startet einen Thread für die synchrone Verbindung"""
        self._thread = threading.Thread(target=self._connection_thread)
        self._thread.daemon = True
        self._thread.start()
        
    def _connection_thread(self):
        """Thread-Funktion für die synchrone Verbindung"""
        try:
            # DroneKit-Connector erstellen
            self._drone_connector = DroneKitConnector(self._connection_string)
            
            # Verbindung herstellen (synchron)
            success = self._drone_connector.establish_connection()
            
            if success:
                # Verbindungserfolg
                self._is_connected = True
                
                # Signale verbinden
                self._connect_signals()
                
                # UI aktualisieren
                self._set_connection_status(self.CONNECTION_STATUS_CONNECTED)
                
                # Thread laufen lassen bis Stopp-Event
                while not self._stop_event.is_set():
                    time.sleep(0.1)  # 100ms Pause
            else:
                # Verbindungsfehler
                self._set_connection_status(self.CONNECTION_STATUS_FAILED)
                self.errorOccurred.emit("Verbindung fehlgeschlagen")
        
        except Exception as e:
            # Fehlerbehandlung
            print(f"Fehler beim Verbinden: {e}")
            self._set_connection_status(self.CONNECTION_STATUS_ERROR)
            self.errorOccurred.emit(f"Verbindungsfehler: {str(e)}")
        
        finally:
            # Aufräumen, wenn der Thread beendet wird
            pass

    def _connect_signals(self):
        """Verbindet Signale vom DroneKit-Connector mit lokalen Slots"""
        if not self._drone_connector:
            return
            
        # Verbindungs-Signale
        self._drone_connector.connection_status_changed.connect(self._on_connection_status_changed)
        
        # Telemetrie-Signale
        self._drone_connector.attitude_updated.connect(self._on_attitude_updated)
        self._drone_connector.gps_position_updated.connect(self._on_gps_updated)
        self._drone_connector.battery_updated.connect(self._on_battery_updated)
        
        # Log-Signale
        self._drone_connector.log_message.connect(self._on_log_message)
        self._drone_connector.error_occurred.connect(self._on_error_occurred)
        
    def _on_connection_status_changed(self, is_connected):
        """Callback für Verbindungsstatus-Änderungen"""
        self._is_connected = is_connected
        self._set_connection_status(self.CONNECTION_STATUS_CONNECTED if is_connected else self.CONNECTION_STATUS_DISCONNECTED)
        
    def _on_attitude_updated(self, roll, pitch, yaw):
        """Callback für Attitude-Updates"""
        self.attitudeChanged.emit(roll, pitch, yaw)
        
    def _on_gps_updated(self, lat, lon, alt):
        """Callback für GPS-Updates"""
        self.gpsChanged.emit(lat, lon, alt)
        
    def _on_battery_updated(self, percent):
        """Callback für Battery-Updates"""
        # Da DroneKit nur Prozent liefert, setzen wir fiktive Werte für Volt/Ampere
        voltage = 12.0 if percent > 20 else 11.0
        current = 5.0  # A
        self.batteryChanged.emit(voltage, current, percent)
        
    def _on_log_message(self, message):
        """Callback für Log-Nachrichten"""
        self.messageReceived.emit(message)
        
    def _on_error_occurred(self, error):
        """Callback für Fehler"""
        self.errorOccurred.emit(error)
        
    @Slot()
    def disconnect(self):
        """Trennt die Verbindung"""
        if not self._is_connected:
            return True
            
        print("Trenne Verbindung...")
        
        # Stopp-Event setzen, um den Thread zu beenden
        self._stop_event.set()
        
        # DroneKit-Verbindung trennen
        if self._drone_connector:
            try:
                self._drone_connector.close_connection()
            except Exception as e:
                print(f"Fehler beim Trennen der Verbindung: {e}")
        
        # Status zurücksetzen
        self._is_connected = False
        self._set_connection_status(self.CONNECTION_STATUS_DISCONNECTED)
        
        # Thread beenden und warten
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2)
            
        # Reset
        self._drone_connector = None
        self._thread = None
        self._stop_event.clear()
        
        return True
                
    def _set_connection_status(self, status):
        """Setzt den Verbindungsstatus und emittiert Signale"""
        if self._connection_status != status:
            self._connection_status = status
            self._is_connected = (status == self.CONNECTION_STATUS_CONNECTED)
            self.connectionStatusChanged.emit(status)
            self.connectedChanged.emit()
            self.connectionChanged.emit(self._is_connected)

    @Slot()
    def load_ports(self) -> List[str]:
        """Lädt verfügbare Ports"""
        try:
            # Debug-Ausgabe vor der Port-Erkennung
            print("[DEBUG] Starte Port-Erkennung...")
            
            # Reale Port-Erkennung implementieren
            import serial.tools.list_ports
            ports = list(serial.tools.list_ports.comports())
            print(f"[DEBUG] PySerial hat {len(ports)} Ports gefunden.")
            
            # Liste der verfügbaren Ports erstellen
            available_ports = []
            
            # COM-Ports hinzufügen
            for port in ports:
                available_ports.append(port.device)
                print(f"[DEBUG] Port gefunden: {port.device} - {port.description}")
            
            # Spezielle Verbindungen hinzufügen
            available_ports.append("tcp:127.0.0.1:5760")
            available_ports.append("udp:127.0.0.1:14550")
            available_ports.append("udp:192.168.4.1:14550")
            
            # Ergebnis speichern und zurückgeben
            if available_ports:
                # Alte Liste sichern zum Vergleich
                old_ports = self._available_ports.copy()
                
                # Neue Liste setzen
                self._available_ports = available_ports
                print(f"[DEBUG] Verfügbare Ports aktualisiert: {self._available_ports}")
                
                # Signal emittieren, aber nur wenn sich die Liste geändert hat
                if old_ports != self._available_ports:
                    print("[DEBUG] Port-Liste hat sich geändert, emittiere Signal")
                    self.availablePortsChanged.emit()
                else:
                    print("[DEBUG] Port-Liste unverändert, kein Signal nötig")
            else:
                print("[WARNUNG] Keine Ports gefunden, verwende Standard-Ports")
                
            return self._available_ports
            
        except Exception as e:
            print(f"[FEHLER] Problem bei der Port-Erkennung: {str(e)}")
            # Im Fehlerfall die Standard-Ports zurückgeben
            return self._available_ports
            
    @Slot()
    def refreshPorts(self):
        """Alias für load_ports() für die QML-UI"""
        print("refreshPorts() aufgerufen - Lade verfügbare Ports")
        ports = self.load_ports()
        # Hier müssen wir ein Signal emittieren, damit die QML-UI aktualisiert wird
        # Da availablePorts eine Property ist, müssen wir ein NOTIFY Signal definieren
        # und hier emittieren
        self.availablePortsChanged.emit()
        return ports

    @Property(bool, notify=connectedChanged)
    def isConnected(self):
        """Gibt zurück, ob eine Verbindung besteht"""
        return self._is_connected
        
    @Property(bool, notify=connectedChanged)
    def connected(self):
        """Alias für isConnected (Kompatibilität mit QML)"""
        return self._is_connected
        
    @Property(list, notify=availablePortsChanged)
    def availablePorts(self):
        """Gibt verfügbare Ports zurück"""
        return self._available_ports
        
    @Slot(str)
    def setPort(self, port):
        """Setzt den zu verwendenden Port"""
        if self._is_connected:
            print("Kann Port nicht ändern während Verbindung aktiv ist")
            return
            
        self._port = port
        print(f"Port gesetzt: {port}")
        
    @Slot(int)
    def setBaudRate(self, rate):
        """Setzt die zu verwendende Baudrate"""
        if self._is_connected:
            print("Kann Baudrate nicht ändern während Verbindung aktiv ist")
            return
            
        self._baud_rate = rate
        print(f"Baudrate gesetzt: {rate}")
        
    @Property(str)
    def port(self):
        """Gibt den aktuellen Port zurück"""
        return self._port

    def fetch_parameters(self):
        """Lädt alle Parameter vom FC und emittiert parameters_received"""
        if not self._drone_connector or not self._is_connected:
            print("[MAVLINK] Nicht verbunden, kann keine Parameter laden.")
            self.parameters_received.emit([])
            return
        params = []
        try:
            self._drone_connector.connection.param_list_send()
            start_time = time.time()
            timeout = 30
            while time.time() - start_time < timeout:
                msg = self._drone_connector.connection.recv_match(type='PARAM_VALUE', blocking=False)
                if msg is None:
                    time.sleep(0.1)
                    continue
                param_id = msg.param_id.decode('utf-8').rstrip('\x00')
                param_value = msg.param_value
                param_type = msg.param_type
                params.append({
                    'name': param_id,
                    'value': param_value,
                    'type': param_type,
                    'index': msg.param_index,
                    'count': msg.param_count
                })
                if msg.param_index + 1 >= msg.param_count:
                    break
            print(f"[MAVLINK] {len(params)} Parameter geladen.")
            self.parameters_received.emit(params)
        except Exception as e:
            print(f"[MAVLINK] Fehler beim Laden der Parameter: {e}")
            self.parameters_received.emit([])

    def write_parameter(self, name, value):
        """Setzt einen Parameter am FC und emittiert parameter_write_complete"""
        if not self._drone_connector or not self._is_connected:
            print("[MAVLINK] Nicht verbunden, kann Parameter nicht setzen.")
            self.parameter_write_complete.emit(name, False)
            return
        try:
            self._drone_connector.connection.param_set_send(name, float(value))
            # Warte auf Bestätigung
            tstart = time.time()
            acked = False
            while time.time() - tstart < 2:
                ack = self._drone_connector.connection.recv_match(type='PARAM_VALUE', blocking=False)
                if ack and ack.param_id.decode('utf-8').rstrip('\x00') == name:
                    acked = True
                    break
                time.sleep(0.1)
            self.parameter_write_complete.emit(name, acked)
        except Exception as e:
            print(f"[MAVLINK] Fehler beim Setzen von {name}: {e}")
            self.parameter_write_complete.emit(name, False)

    def is_connected(self):
        return self._is_connected
