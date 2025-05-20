"""
Kompatibler Sensor-Simulator für das bestehende SensorViewModel
"""

import math
import time
import random
import threading
from typing import Optional
from PySide6.QtCore import QObject, Signal, Slot, QTimer

class CompatibleSensorSimulator(QObject):
    """Sensor-Simulator, der kompatibel mit dem bestehenden SensorViewModel ist"""
    
    # Standard-Signal für Sensor-Updates
    sensorUpdated = Signal(str, float)  # sensor_id, value
    
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
        
        print("Kompatibler Sensor-Simulator initialisiert")
    
    def initialize_sensors(self, model):
        """Initialisiere Sensoren im SensorViewModel"""
        # Liste aller Sensoren mit ID, Name und Einheit
        sensors = [
            ("roll", "Roll", "°"),
            ("pitch", "Pitch", "°"),
            ("yaw", "Heading", "°"),
            ("altitude", "Altitude", "m"),
            ("groundspeed", "Ground Speed", "m/s"),
            ("airspeed", "Air Speed", "m/s"),
            ("heading", "Heading", "°"),
            ("battery_remaining", "Battery", "%"),
            ("battery_voltage", "Voltage", "V"),
            ("battery_current", "Current", "A"),
            ("gps_lat", "GPS Latitude", "°"),
            ("gps_lon", "GPS Longitude", "°"),
        ]
        
        # Füge alle Sensoren hinzu
        for sensor_id, name, unit in sensors:
            model.add_sensor(sensor_id, name, unit)
            
        # Verbinde Signal für Updates
        self.sensorUpdated.connect(model.update_sensor)
        
        print(f"{len(sensors)} Sensoren im Modell initialisiert")
    
    def start(self):
        """Startet den Simulator"""
        if self._running:
            return True
            
        print("Simulator wird gestartet...")
        self._running = True
        self._thread = threading.Thread(target=self._generation_loop)
        self._thread.daemon = True
        self._thread.start()
        print("Simulator-Thread gestartet")
        return True
        
    def stop(self):
        """Stoppt den Simulator"""
        if not self._running:
            return
            
        print("Simulator wird gestoppt...")
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)
            self._thread = None
        print("Simulator gestoppt")
    
    def _generation_loop(self):
        """Hauptschleife für die Datengenerierung"""
        print("Daten-Generierung startet...")
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
                self._voltage = max(10.0, self._voltage)  # Nicht unter 10V
                self._current = max(0, 8.0 + random.uniform(-0.5, 0.5))  # ~8A
                self._remaining = max(0, min(100, 75.0 - random.uniform(0, 0.01)))  # ~75%
                
                # Sende alle Daten
                self._send_all_updates()
                
                # Kurze Pause
                time.sleep(0.1)
                
            except Exception as e:
                print(f"Fehler bei Daten-Generierung: {str(e)}")
                time.sleep(1.0)  # Bei Fehler etwas länger warten
    
    def _send_all_updates(self):
        """Sendet alle aktualisierten Daten über das kompatible Signal"""
        try:
            # Zufallswerte für realistische Simulationen
            # Etwas mehr Varianz bei den Werten einbringen
            self._groundspeed = 5.0 + random.uniform(-2.0, 3.0)
            self._airspeed = 6.0 + random.uniform(-1.0, 2.0)
            self._heading = (self._heading + random.uniform(0, 5.0)) % 360.0
            throttle_val = 20.0 + random.uniform(-5.0, 10.0)
            
            # Konvertiere Rad in Grad für bessere Lesbarkeit
            roll_deg = math.degrees(self._roll)
            pitch_deg = math.degrees(self._pitch)
            yaw_deg = math.degrees(self._yaw)
            heading = (yaw_deg % 360)
            
            # Debug-Ausgabe hinzufügen (nur jedes 10. Mal drucken, um Konsole zu schonen)
            if random.random() < 0.1:  
                print("\n" + "="*50)
                print(f"[Simulator] Sende Sensor-Updates:")
                print(f"  Roll: {roll_deg:.1f}°, Pitch: {pitch_deg:.1f}°, Yaw: {yaw_deg:.1f}°")
                print(f"  Altitude: {self._alt:.1f}m, Groundspeed: {self._groundspeed:.1f}m/s")
                print(f"  Battery: {self._voltage:.1f}V, {self._current:.1f}A, {self._remaining:.0f}%")
                print(f"  GPS: Lat={self._lat:.6f}, Lon={self._lon:.6f}")
                print("="*50)
            
            # Aktualisiere jeden Sensor einzeln - das ist kompatibel mit dem SensorViewModel
            # Attitude-Daten
            self.sensorUpdated.emit("roll", float(roll_deg))
            self.sensorUpdated.emit("pitch", float(pitch_deg))
            self.sensorUpdated.emit("yaw", float(yaw_deg))
            self.sensorUpdated.emit("heading", float(heading))
            
            # Höhen- und Geschwindigkeitsdaten 
            self.sensorUpdated.emit("altitude", float(self._alt))
            self.sensorUpdated.emit("groundspeed", float(self._groundspeed))
            self.sensorUpdated.emit("airspeed", float(self._airspeed))
            
            # Batterie-Daten - wichtig: Richtige ID verwenden
            self.sensorUpdated.emit("battery_voltage", float(self._voltage))
            self.sensorUpdated.emit("battery_current", float(self._current))
            self.sensorUpdated.emit("battery_remaining", float(self._remaining))
            
            # GPS-Daten
            self.sensorUpdated.emit("gps_lat", float(self._lat))
            self.sensorUpdated.emit("gps_lon", float(self._lon))
            
            # Weitere wichtige Sensoren
            self.sensorUpdated.emit("gps_hdop", float(1.2 + random.uniform(-0.2, 0.5)))  # Variabler HDOP-Wert
            self.sensorUpdated.emit("gps_satellites", float(int(12 + random.uniform(-2, 4))))  # Variable Anzahl an Satelliten
            self.sensorUpdated.emit("throttle", float(throttle_val))  # Variabler Throttle-Wert
            
        except Exception as e:
            import traceback
            print(f"Fehler beim Senden der Updates: {str(e)}")
            print(traceback.format_exc())


def run_simulator(sensor_model):
    """Hilfsfunktion zum Ausführen des Simulators mit einem vorhandenen SensorViewModel"""
    simulator = CompatibleSensorSimulator()
    simulator.initialize_sensors(sensor_model)
    simulator.start()
    return simulator
