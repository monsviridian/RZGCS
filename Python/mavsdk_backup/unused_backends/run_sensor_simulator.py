"""
Direkter Sensor-Simulator ohne MAVLink-Abhängigkeit
Dieses Modul startet eine vereinfachte Version des GCS mit direkter Sensor-Simulation
ohne die problematischen MAVLink-Abhängigkeiten.
"""

import os
import sys
import time
import math
import random
import threading
from typing import Optional, Dict, List, Any

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QObject, Signal, Slot, QTimer, QUrl
from PySide6.QtQml import QQmlApplicationEngine, QQmlComponent

# Import Sensor-Modell
from backend.sensorviewmodel import SensorViewModel

class DirectSensorSimulator(QObject):
    """Einfacher Sensor-Simulator, der direkt Sensordaten generiert"""
    
    batteryUpdated = Signal(float, float, float)  # voltage, current, remaining
    attitudeUpdated = Signal(float, float, float)  # roll, pitch, yaw (in Radians)
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
        
        print("Sensor-Simulator initialisiert")
    
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
                
                # Sende Daten über Signale
                self.batteryUpdated.emit(self._voltage, self._current, self._remaining)
                self.attitudeUpdated.emit(self._roll, self._pitch, self._yaw)
                self.gpsUpdated.emit(self._lat, self._lon, self._alt)
                
                # Kurze Pause
                time.sleep(0.1)
                
            except Exception as e:
                print(f"Fehler bei Daten-Generierung: {str(e)}")
                time.sleep(1.0)  # Bei Fehler etwas länger warten


class SensorHandler(QObject):
    """Verarbeitet Sensordaten und aktualisiert das UI"""
    
    def __init__(self, sensor_model: SensorViewModel):
        super().__init__()
        self._sensor_model = sensor_model
        print("Sensor-Handler initialisiert")
    
    @Slot(float, float, float)
    def handle_battery(self, voltage, current, remaining):
        """Verarbeitet Batterie-Daten"""
        try:
            # Log-Meldung
            print(f"Batterie: {voltage:.1f}V {current:.1f}A {remaining:.0f}%")
            
            # Sensordaten aktualisieren
            self._sensor_model.update_battery(voltage, current, remaining)
                
        except Exception as e:
            print(f"Fehler bei der Verarbeitung von Batterie-Daten: {str(e)}")

    @Slot(float, float, float)
    def handle_attitude(self, roll, pitch, yaw):
        """Verarbeitet Attitude-Daten"""
        try:
            # Konvertiere in Grad für bessere Lesbarkeit
            roll_deg = math.degrees(roll)
            pitch_deg = math.degrees(pitch)
            yaw_deg = math.degrees(yaw)
            
            # Log-Meldung
            print(f"Attitude: Roll={roll_deg:.1f}° Pitch={pitch_deg:.1f}° Yaw={yaw_deg:.1f}°")
            
            # Sensordaten aktualisieren
            self._sensor_model.update_attitude(roll_deg, pitch_deg, yaw_deg)
                
        except Exception as e:
            print(f"Fehler bei der Verarbeitung von Attitude-Daten: {str(e)}")

    @Slot(float, float, float)
    def handle_gps(self, lat, lon, alt):
        """Verarbeitet GPS-Daten"""
        try:
            # Log-Meldung
            print(f"GPS: Lat={lat:.6f} Lon={lon:.6f} Alt={alt:.1f}m")
            
            # Sensordaten aktualisieren
            # Berechne Geschwindigkeit basierend auf letzten Koordinaten (simuliert)
            ground_speed = 5.0  # Default-Wert
            
            self._sensor_model.update_gps(lat, lon, alt, ground_speed)
                
        except Exception as e:
            print(f"Fehler bei der Verarbeitung von GPS-Daten: {str(e)}")


def main():
    """Hauptprogramm"""
    app = QApplication(sys.argv)
    
    # Engine für QML erstellen
    engine = QQmlApplicationEngine()
    
    # Sensor-Modell und Simulator erstellen
    sensor_model = SensorViewModel()
    simulator = DirectSensorSimulator()
    sensor_handler = SensorHandler(sensor_model)
    
    # Verbinde Simulator-Signale mit Handler-Slots
    simulator.batteryUpdated.connect(sensor_handler.handle_battery)
    simulator.attitudeUpdated.connect(sensor_handler.handle_attitude)
    simulator.gpsUpdated.connect(sensor_handler.handle_gps)
    
    # Setze das Sensor-Modell als Kontext-Property
    engine.rootContext().setContextProperty("sensorModel", sensor_model)
    
    # Lade das QML-Hauptfenster
    qml_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                            "RZGCSContent", "SensorView.ui.qml")
    print(f"Loading QML from: {qml_path}")
    
    # Startet den Simulator
    simulator.start()
    
    # Lade und zeige das UI
    engine.load(QUrl.fromLocalFile(qml_path))
    
    if not engine.rootObjects():
        print("Fehler beim Laden des QML-Hauptfensters")
        return 1
    
    # Starte die Hauptschleife
    exit_code = app.exec()
    
    # Cleanup
    simulator.stop()
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
