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
        
        # Initialisiere Startwerte - Ingolstadt (nahe dem BMW Testgelände)
        self._lat = 48.744101  # Ingolstadt
        self._lon = 11.446327
        self._alt = 374.0
        self._roll = 0.0
        self._pitch = 0.0
        self._yaw = 0.0
        self._voltage = 12.6
        self._current = 8.5
        self._remaining = 75.0
        self._airspeed = 5.0
        self._groundspeed = 6.0
        self._heading = 0.0
        
        # Flugmuster-Parameter
        self._flight_time = 0.0
        self._flight_radius = 0.001  # ca. 100m Radius
        self._flight_pattern = "circle"  # circle, figure8, hover
        self._center_lat = self._lat
        self._center_lon = self._lon
        
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
                # Flugzeit hochzählen
                self._flight_time += 0.1
                
                # GPS-Daten basierend auf Flugmuster aktualisieren
                if self._flight_pattern == "circle":
                    # Kreisförmige Bewegung
                    angle = self._flight_time * 0.05  # Langsamere Bewegung
                    self._lat = self._center_lat + self._flight_radius * math.sin(angle)
                    self._lon = self._center_lon + self._flight_radius * math.cos(angle) * 1.5  # Ellipse statt Kreis wegen Projektion
                    
                    # Flugausrichtung basierend auf Bewegungsrichtung
                    # In einem Kreis ändert sich der Heading kontinuierlich
                    self._heading = (angle * 180 / math.pi + 90) % 360
                    
                    # Roll anpassen (in einer Kurve leicht neigen)
                    self._roll = math.radians(10)  # 10° Neigung in der Kurve
                    
                elif self._flight_pattern == "figure8":
                    # Achterbahn-Bewegung mit Lemniskate (Achterschleife)
                    t = self._flight_time * 0.05
                    denom = 1 + math.sin(t) ** 2
                    self._lat = self._center_lat + self._flight_radius * math.cos(t) / denom
                    self._lon = self._center_lon + self._flight_radius * math.sin(t) * math.cos(t) / denom * 1.5
                    
                    # Roll und Heading basierend auf Position in der 8
                    self._heading = (t * 180 / math.pi) % 360
                    self._roll = math.radians(15 * math.sin(t))  # Neigung variiert
                    
                else:  # hover oder andere Muster
                    # Leichte Bewegung um einen Punkt (Hover-Modus)
                    self._lat = self._center_lat + random.uniform(-0.000005, 0.000005)
                    self._lon = self._center_lon + random.uniform(-0.000005, 0.000005)
                    self._heading = (self._heading + random.uniform(-1, 1)) % 360
                    self._roll = math.radians(random.uniform(-3, 3))
                
                # Höhe mit leichten Schwankungen
                self._alt += random.uniform(-0.2, 0.2)
                self._alt = max(370.0, min(380.0, self._alt))  # Höhe zwischen 370-380m halten
                
                # Pitch an Flugmuster anpassen (leichte Steig- und Sinkflüge)
                self._pitch = math.radians(2 * math.sin(self._flight_time * 0.02))
                
                # Yaw aus Heading in Radiant umrechnen
                self._yaw = math.radians(self._heading)
                
                # Geschwindigkeiten anpassen
                if self._flight_pattern == "hover":
                    self._groundspeed = random.uniform(0, 1.0)  # Langsam im Hover
                    self._airspeed = random.uniform(0, 1.5)
                else:
                    self._groundspeed = 5.0 + random.uniform(-0.5, 1.0)  # ~5 m/s
                    self._airspeed = 6.0 + random.uniform(-0.5, 1.0)    # ~6 m/s
                
                # Batterie-Daten aktualisieren
                self._voltage -= random.uniform(0, 0.001)  # Sehr langsam entladen
                self._voltage = max(10.0, self._voltage)  # Nicht unter 10V
                self._current = max(0, 8.0 + random.uniform(-0.5, 0.5))  # ~8A
                self._remaining = max(0, min(100, 75.0 - (self._flight_time * 0.01)))  # Langsam entladen
                
                # Alle 30 Sekunden Flugmuster wechseln
                if int(self._flight_time) % 30 == 0 and int(self._flight_time) > 0 and random.random() < 0.05:
                    patterns = ["circle", "figure8", "hover"]
                    old_pattern = self._flight_pattern
                    self._flight_pattern = random.choice([p for p in patterns if p != old_pattern])
                    print(f"Flugmuster geändert von {old_pattern} zu {self._flight_pattern}")
                    # Aktuelle Position als neues Zentrum
                    self._center_lat = self._lat
                    self._center_lon = self._lon
                
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
