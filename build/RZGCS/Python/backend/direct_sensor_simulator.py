"""
Ein direkter Sensor-Simulator, der Sensordaten generiert, ohne MAVLink zu verwenden
"""

import math
import time
import random
import threading
from typing import Optional, Dict, List, Any
from PySide6.QtCore import QObject, Signal, Slot, QTimer

class DirectSensorSimulator(QObject):
    """Einfacher Sensor-Simulator, der direkt Sensorwerte generiert ohne MAVLink-Abhängigkeit"""
    
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
        """Startet den Sensor-Simulator"""
        if self._running:
            return True
            
        self._running = True
        self._thread = threading.Thread(target=self._generation_loop)
        self._thread.daemon = True
        self._thread.start()
        return True
        
    def stop(self):
        """Stoppt den Sensor-Simulator"""
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
                print(f"Fehler bei Sensor-Simulation: {str(e)}")
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
