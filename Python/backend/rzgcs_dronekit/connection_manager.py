"""
DroneKit Connection Manager - Verwaltet DroneKit-Verbindungen
"""

import time
import threading
from typing import Optional, Callable
from PySide6.QtCore import QObject, Signal
import traceback

# DroneKit-Imports
# External DroneKit import - fixed to avoid circular imports
import dronekit as dronekit_external  # Externe DroneKit-Bibliothek
connect = dronekit_external.connect  # Aus externer DroneKit-Bibliothek
VehicleMode = dronekit_external.VehicleMode  # Aus externer DroneKit-Bibliothek

# Import our custom vehicle class
from .custom_vehicle import RZGCSVehicle

from .utils import DroneKitUtils

class DroneKitConnectionManager(QObject):
    """Verwaltet DroneKit-Verbindungen mit Fehlerbehandlung und Reconnect"""
    
    # Signals
    connection_established = Signal()
    connection_lost = Signal()
    connection_failed = Signal(str)  # error message
    reconnecting = Signal(int)  # attempt number
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.connection_timeout = 30  # Sekunden
        self.heartbeat_timeout = 5    # Sekunden
        self.reconnect_attempts = 3
        self.reconnect_delay = 2      # Sekunden
        self.vehicle = None
        self.connection_string = ""
        self.is_connected = False
        self.last_heartbeat = 0
        self.reconnect_thread = None
        self.stop_event = threading.Event()
        
    def establish_connection(self, connection_string: str) -> Optional['RZGCSVehicle']:
        """Verbindung zu Fahrzeug herstellen"""
        try:
            # Verbindungsstring validieren
            validated_string = DroneKitUtils.validate_connection_string(connection_string)
            self.connection_string = validated_string

            # Windows serial port handling
            if validated_string.lower().startswith('com'):
                # Nur den Portnamen extrahieren (z.B. 'com8' aus 'com8:115200')
                port = validated_string.split(':')[0].lower()
                baud = 115200  # Make configurable if needed
                print(f"[DEBUG] Verbinde mit: {port} (baud={baud})")
                self.vehicle = connect(port, 
                                      wait_ready=True, 
                                      baud=baud,
                                      timeout=self.connection_timeout,
                                      vehicle_class=RZGCSVehicle)
            else:
                print(f"[DEBUG] Verbinde mit: {validated_string}")
                self.vehicle = connect(validated_string, 
                                      wait_ready=True, 
                                      timeout=self.connection_timeout,
                                      vehicle_class=RZGCSVehicle)

            # Verbindungsstatus prüfen (defensive programming)
            if not self.vehicle:
                raise ConnectionError("Failed to create vehicle object")
            
            # Wait for vehicle to be ready
            if not self.vehicle.is_armable:
                # Wait a bit more for vehicle to initialize
                timeout_counter = 0
                while not self.vehicle.is_armable and timeout_counter < 10:
                    time.sleep(1)
                    timeout_counter += 1
                
                if not self.vehicle.is_armable:
                    raise ConnectionError("Vehicle not armable after initialization")
            
            # Heartbeat-Monitoring starten
            self.last_heartbeat = time.time()
            self.is_connected = True
            self.connection_established.emit()
            
            return self.vehicle
            
        except Exception as e:
            error_msg = f"Connection failed: {str(e)}"
            print(error_msg)
            traceback.print_exc()
            self.connection_failed.emit(error_msg)
            self.is_connected = False
            return None
    
    def start_heartbeat_monitoring(self):
        """Startet Heartbeat-Monitoring in separatem Thread"""
        if self.reconnect_thread and self.reconnect_thread.is_alive():
            return
            
        self.stop_event.clear()
        self.reconnect_thread = threading.Thread(target=self._heartbeat_monitor_loop, daemon=True)
        self.reconnect_thread.start()
    
    def _heartbeat_monitor_loop(self):
        """Hauptschleife für Heartbeat-Monitoring"""
        while not self.stop_event.is_set():
            try:
                if self.vehicle and self.is_connected:
                    # Heartbeat prüfen
                    if not DroneKitUtils.is_connection_alive(self.last_heartbeat, self.heartbeat_timeout):
                        self.connection_lost.emit()
                        self.is_connected = False
                        
                        # Automatischer Reconnect
                        if self.reconnect_attempts > 0:
                            self._attempt_reconnect()
                        break
                
                time.sleep(1)  # 1 Hz Check-Rate
                
            except Exception as e:
                print(f"Heartbeat monitoring error: {e}")
                break
        
        self.is_connected = False
    
    def _attempt_reconnect(self):
        """Versucht automatischen Reconnect"""
        for attempt in range(self.reconnect_attempts):
            try:
                self.reconnecting.emit(attempt + 1)
                time.sleep(self.reconnect_delay)
                
                # Reconnect versuchen (synchron)
                self.vehicle = self.establish_connection(self.connection_string)
                
                if self.vehicle:
                    self.is_connected = True
                    self.connection_established.emit()
                    return
                    
            except Exception as e:
                print(f"Reconnect attempt {attempt + 1} failed: {e}")
        
        # Alle Reconnect-Versuche fehlgeschlagen
        self.connection_failed.emit("All reconnect attempts failed")
    
    def update_heartbeat(self):
        """Aktualisiert Heartbeat-Timestamp"""
        self.last_heartbeat = time.time()
    
    def close_connection(self):
        """Trennt Verbindung"""
        self.stop_event.set()
        
        if self.vehicle:
            try:
                self.vehicle.close()
            except:
                pass
            finally:
                self.vehicle = None
        
        self.is_connected = False
    
    def get_connection_status(self) -> dict:
        """Gibt aktuellen Verbindungsstatus zurück"""
        return {
            'connected': self.is_connected,
            'connection_string': self.connection_string,
            'last_heartbeat': self.last_heartbeat,
            'time_since_heartbeat': time.time() - self.last_heartbeat if self.last_heartbeat > 0 else 0,
            'vehicle_ready': self.vehicle.is_armable if self.vehicle else False
        }
    
    def set_connection_timeout(self, timeout: float):
        """Setzt Connection-Timeout"""
        self.connection_timeout = timeout
    
    def set_heartbeat_timeout(self, timeout: float):
        """Setzt Heartbeat-Timeout"""
        self.heartbeat_timeout = timeout
    
    def set_reconnect_attempts(self, attempts: int):
        """Setzt Anzahl Reconnect-Versuche"""
        self.reconnect_attempts = attempts
    
    def set_reconnect_delay(self, delay: float):
        """Setzt Reconnect-Delay"""
        self.reconnect_delay = delay 