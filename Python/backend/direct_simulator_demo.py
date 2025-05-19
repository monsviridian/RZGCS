"""
Eine direkte Demonstrationsanwendung, die Sensordaten simuliert und im UI anzeigt, ohne MAVLink-Abhängigkeit
"""

import os
import sys
import math
import time
import random
import threading
from typing import Optional, List, Dict
from PySide6.QtCore import QObject, Signal, Slot, QAbstractListModel, Qt, QModelIndex, QTimer
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlComponent, QQmlEngine

class SensorModel(QAbstractListModel):
    """Modell für die Anzeige der Sensordaten im UI"""
    NameRole = Qt.UserRole + 1
    ValueRole = Qt.UserRole + 2
    UnitRole = Qt.UserRole + 3
    IdRole = Qt.UserRole + 4
    
    dataChanged = Signal(QModelIndex, QModelIndex, list)

    def __init__(self):
        super().__init__()
        self._sensors = []

    def roleNames(self):
        return {
            self.NameRole: b"name",
            self.ValueRole: b"value",
            self.UnitRole: b"unit",
            self.IdRole: b"id"
        }

    def rowCount(self, parent=QModelIndex()):
        return len(self._sensors)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or index.row() >= len(self._sensors):
            return None
        sensor = self._sensors[index.row()]
        if role == self.NameRole:
            return sensor["name"]
        elif role == self.ValueRole:
            return sensor["value"]
        elif role == self.UnitRole:
            return sensor["unit"]
        elif role == self.IdRole:
            return sensor["id"]
        return None

    @Slot(str, str, str)
    def add_sensor(self, sensor_id, name, unit):
        """Fügt einen neuen Sensor hinzu"""
        for i, sensor in enumerate(self._sensors):
            if sensor["id"] == sensor_id:
                return  # Sensor existiert bereits
                
        self.beginInsertRows(QModelIndex(), len(self._sensors), len(self._sensors))
        self._sensors.append({
            "id": sensor_id,
            "name": name,
            "value": 0.0,
            "unit": unit
        })
        self.endInsertRows()
        print(f"Sensor hinzugefügt: {name} ({unit})")

    @Slot(str, float)
    def update_sensor(self, sensor_id, value):
        """Aktualisiert den Wert eines Sensors"""
        for i, sensor in enumerate(self._sensors):
            if sensor["id"] == sensor_id:
                self._sensors[i]["value"] = value
                index = self.index(i, 0)
                self.dataChanged.emit(index, index, [self.ValueRole])
                print(f"Sensor aktualisiert: {sensor_id} = {value}")
                break

    @Slot(result='QVariantList')
    def get_all_sensors(self):
        """Gibt alle Sensoren zurück"""
        return self._sensors


class DirectSensorSimulator(QObject):
    """Einfacher Sensor-Simulator, der direkt Sensordaten generiert"""
    
    # Signale für Sensor-Updates
    dataUpdated = Signal(str, float)  # sensor_id, value
    
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
        
        # For testing
        print("DirectSensorSimulator initialized")
    
    def initialize_sensors(self, model: SensorModel):
        """Initialisiert die Sensoren im Modell"""
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
            ("gps_hdop", "GPS HDOP", ""),
            ("gps_satellites", "GPS Satellites", "")
        ]
        
        for sensor_id, name, unit in sensors:
            model.add_sensor(sensor_id, name, unit)
            
        # Connect signal
        self.dataUpdated.connect(model.update_sensor)
        print(f"Initialized {len(sensors)} sensors")
    
    def start(self):
        """Startet den Simulator"""
        if self._running:
            return
            
        print("Starting simulator...")
        self._running = True
        self._thread = threading.Thread(target=self._generation_loop)
        self._thread.daemon = True
        self._thread.start()
        print("Simulator thread started")
        
    def stop(self):
        """Stoppt den Simulator"""
        if not self._running:
            return
            
        print("Stopping simulator...")
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)
            self._thread = None
        print("Simulator stopped")
    
    def _generation_loop(self):
        """Hauptschleife für die Datengenerierung"""
        print("Generation loop starting...")
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
                
                # Sende Daten
                self._send_all_updates()
                
                # Kurze Pause
                time.sleep(0.1)
                
            except Exception as e:
                print(f"Error in simulation loop: {str(e)}")
                time.sleep(1.0)
    
    def _send_all_updates(self):
        """Sendet alle aktualisierten Daten"""
        try:
            # Konvertiere Rad in Grad für bessere Lesbarkeit
            roll_deg = self._roll * 180 / math.pi
            pitch_deg = self._pitch * 180 / math.pi
            yaw_deg = self._yaw * 180 / math.pi
            
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
            self.dataUpdated.emit("gps_hdop", 1.2)
            self.dataUpdated.emit("gps_satellites", 14)
        except Exception as e:
            print(f"Error sending updates: {str(e)}")


def main():
    """Hauptprogramm"""
    app = QGuiApplication(sys.argv)
    
    # Erstelle die Modelle
    sensor_model = SensorModel()
    simulator = DirectSensorSimulator()
    
    # Initialisiere die Sensoren
    simulator.initialize_sensors(sensor_model)
    
    # Engine und Kontext erstellen
    engine = QQmlEngine()
    context = engine.rootContext()
    
    # Modelle im Kontext verfügbar machen
    context.setContextProperty("sensorModel", sensor_model)
    
    # Hauptfenster laden - Pfad zum QML-Hauptfenster muss angepasst werden
    qml_file = os.path.join(os.path.dirname(__file__), "../../RZGCSContent/SensorView.ui.qml")
    component = QQmlComponent(engine, qml_file)
    
    if component.isError():
        for error in component.errors():
            print(f"Error loading QML: {error.toString()}")
        return
    
    # Hauptfenster erstellen
    window = component.create()
    if window:
        # Simulator starten
        simulator.start()
        
        # Fenster anzeigen
        window.show()
        
        # Hauptschleife starten
        status = app.exec()
        
        # Simulator stoppen
        simulator.stop()
        
        return status
    else:
        print("Failed to create window")
        return 1


if __name__ == "__main__":
    sys.exit(main())
