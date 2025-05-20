import math
import time
import random
import threading
from typing import Optional
from PySide6.QtCore import QObject, Signal, Slot

class TestDataGenerator(QObject):
    """Einfacher Test-Daten-Generator für Sensorwerte ohne MAVLink-Abhängigkeit"""
    
    # Signale
    dataUpdated = Signal(str, float)  # sensor_id, value
    batteryUpdated = Signal(float, float, float)  # voltage, current, remaining
    attitudeUpdated = Signal(float, float, float)  # roll, pitch, yaw
    gpsUpdated = Signal(float, float, float)  # lat, lon, alt
    
    def __init__(self):
        super().__init__()
        self._running = False
        self._thread: Optional[threading.Thread] = None
        
        # Initialisiere Startwerte
        self._lat = 52.520008  # Berlin
        self._lon = 13.404954
        self._alt = 100.0
        self._roll = 0.0
        self._pitch = 0.0
        self._yaw = 0.0
        self._voltage = 12.6
        self._current = 8.5
        self._remaining = 75.0
        self._airspeed = 5.0
        self._groundspeed = 6.0
        self._heading = 0.0
    
    def start(self):
        """Startet den Test-Daten-Generator"""
        if self._running:
            return True
            
        self._running = True
        self._thread = threading.Thread(target=self._generation_loop)
        self._thread.daemon = True
        self._thread.start()
        return True
        
    def stop(self):
        """Stoppt den Test-Daten-Generator"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)
            self._thread = None
    
    def _generation_loop(self):
        """Hauptschleife für die Datengenerierung"""
        while self._running:
            try:
                # GPS-Daten aktualisieren
                self._lat += random.uniform(-0.00001, 0.00001)
                self._lon += random.uniform(-0.00001, 0.00001)
                self._alt += random.uniform(-0.5, 0.5)
                self._alt = max(0.0, min(1000.0, self._alt))
                
                # Attitude-Daten aktualisieren
                self._roll = 0.1 * math.sin(time.time())
                self._pitch = 0.1 * math.cos(time.time()) 
                self._yaw = (self._yaw + 0.01) % (2 * math.pi)
                
                # Batterie-Daten aktualisieren
                self._voltage -= random.uniform(0, 0.001)  # Sehr langsam entladen
                self._current = max(0, self._current + random.uniform(-0.1, 0.1))
                self._remaining = max(0, min(100, self._remaining - random.uniform(0, 0.01)))
                
                # Sende Daten über Signale
                self._send_all_updates()
                
                # Kurze Pause
                time.sleep(0.1)
                
            except Exception as e:
                print(f"Fehler bei Testdaten-Generierung: {str(e)}")
                time.sleep(1.0)  # Bei Fehler etwas länger warten
    
    def _send_all_updates(self):
        """Sendet alle aktualisierten Daten"""
        # Signale für die zusammengefassten Daten
        self.batteryUpdated.emit(self._voltage, self._current, self._remaining)
        
        # Konvertiere Rad in Grad für bessere Lesbarkeit
        roll_deg = self._roll * 180 / math.pi
        pitch_deg = self._pitch * 180 / math.pi
        yaw_deg = self._yaw * 180 / math.pi
        self.attitudeUpdated.emit(self._roll, self._pitch, self._yaw)
        
        self.gpsUpdated.emit(self._lat, self._lon, self._alt)
        
        # Einzelsensoren aktualisieren
        self.dataUpdated.emit("roll", roll_deg)
        self.dataUpdated.emit("pitch", pitch_deg)
        self.dataUpdated.emit("yaw", yaw_deg)
        self.dataUpdated.emit("gps_lat", self._lat)
        self.dataUpdated.emit("gps_lon", self._lon)
        self.dataUpdated.emit("altitude", self._alt)
        self.dataUpdated.emit("battery_voltage", self._voltage)
        self.dataUpdated.emit("battery_current", self._current)
        self.dataUpdated.emit("battery_remaining", self._remaining)
        self.dataUpdated.emit("groundspeed", self._groundspeed)
        self.dataUpdated.emit("airspeed", self._airspeed)
        self.dataUpdated.emit("heading", (yaw_deg % 360))

class TestDataGenerator:
    """Generates realistic test data for drone simulation"""
    
    def __init__(self):
        self._start_time = time.time()
        self._last_update = time.time()
        self._data = TestData()
        self._mode = "STABILIZE"  # Default flight mode
        self._armed = False
        self._home_lat = 48.137154
        self._home_lon = 11.576124
        self._radius = 0.0001  # ~10m radius
        self._altitude = 10.0  # 10m altitude
        self._speed = 0.0
        self._heading = 0.0
        
    def update(self) -> TestData:
        """Update test data based on time and current state"""
        current_time = time.time()
        dt = current_time - self._last_update
        self._last_update = current_time
        
        # Update position based on speed and heading
        if self._armed:
            # Calculate new position
            dx = self._speed * math.cos(math.radians(self._heading)) * dt
            dy = self._speed * math.sin(math.radians(self._heading)) * dt
            
            # Convert to lat/lon (approximate)
            self._data.lat = self._home_lat + (dy / 111111.0)
            self._data.lon = self._home_lon + (dx / (111111.0 * math.cos(math.radians(self._home_lat))))
            
            # Update altitude
            self._data.alt = self._altitude + random.uniform(-0.1, 0.1)
            
            # Update attitude
            self._data.roll = math.sin(current_time) * 5.0  # ±5 degrees
            self._data.pitch = math.cos(current_time) * 5.0  # ±5 degrees
            self._data.yaw = (self._heading + random.uniform(-1, 1)) % 360
            
            # Update speeds
            self._data.airspeed = self._speed + random.uniform(-0.1, 0.1)
            self._data.groundspeed = self._speed + random.uniform(-0.2, 0.2)
            self._data.climb = random.uniform(-0.1, 0.1)
            
            # Update battery
            self._data.voltage = max(10.0, self._data.voltage - random.uniform(0, 0.01))
            self._data.current = 2.0 + random.uniform(-0.1, 0.1)
            self._data.remaining = max(0, self._data.remaining - random.uniform(0, 0.01))
        else:
            # Reset to home position when disarmed
            self._data.lat = self._home_lat
            self._data.lon = self._home_lon
            self._data.alt = 0.0
            self._data.roll = 0.0
            self._data.pitch = 0.0
            self._data.yaw = 0.0
            self._data.airspeed = 0.0
            self._data.groundspeed = 0.0
            self._data.climb = 0.0
            
        return self._data
        
    def set_mode(self, mode: str):
        """Set flight mode"""
        self._mode = mode
        if mode == "RTL":
            self._speed = 2.0  # Return to home at 2 m/s
            self._heading = self._calculate_heading_to_home()
        elif mode == "LOITER":
            self._speed = 1.0  # Loiter at 1 m/s
        elif mode == "STABILIZE":
            self._speed = 0.0  # Hover in place
            
    def set_armed(self, armed: bool):
        """Set armed state"""
        self._armed = armed
        
    def _calculate_heading_to_home(self) -> float:
        """Calculate heading to home position"""
        dx = self._home_lon - self._data.lon
        dy = self._home_lat - self._data.lat
        heading = math.degrees(math.atan2(dy, dx))
        return (heading + 360) % 360 