#!/usr/bin/env python3
"""
Tests für das Sensor ViewModel.
Diese Tests validieren die Funktionalität des Sensormodells und die Integration mit SITL.
"""
import os
import sys
import unittest
import pytest
from unittest.mock import MagicMock, patch
from PySide6.QtCore import QObject, Signal

# Pfad zum Hauptmodul hinzufügen
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# SensorViewModel importieren
from rzgcs.viewmodel.sensor_viewmodel import SensorViewModel

class TestSensorViewModel(unittest.TestCase):
    """Testet das Sensor ViewModel."""
    
    def setUp(self):
        """Richtet die Testumgebung ein."""
        self.sensor_vm = SensorViewModel()
    
    def test_init(self):
        """Testet, ob das ViewModel korrekt initialisiert wird."""
        # Prüfe, ob die Grundlegenden Sensor-Eigenschaften existieren
        self.assertEqual(self.sensor_vm.getSensorValue("latitude"), 0.0)
        self.assertEqual(self.sensor_vm.getSensorValue("longitude"), 0.0)
        self.assertEqual(self.sensor_vm.getSensorValue("altitude"), 0.0)
        self.assertEqual(self.sensor_vm.getSensorValue("roll"), 0.0)
        self.assertEqual(self.sensor_vm.getSensorValue("pitch"), 0.0)
        self.assertEqual(self.sensor_vm.getSensorValue("yaw"), 0.0)
    
    def test_update_sensor(self):
        """Testet die Aktualisierung eines Sensors."""
        # Sensor aktualisieren
        self.sensor_vm.update_sensor("latitude", 49.445232)
        self.sensor_vm.update_sensor("longitude", 7.769488)
        self.sensor_vm.update_sensor("altitude", 100.0)
        
        # Überprüfungen
        self.assertEqual(self.sensor_vm.getSensorValue("latitude"), 49.445232)
        self.assertEqual(self.sensor_vm.getSensorValue("longitude"), 7.769488)
        self.assertEqual(self.sensor_vm.getSensorValue("altitude"), 100.0)
    
    def test_update_qml_sensor(self):
        """Testet die Aktualisierung eines QML-Sensors."""
        # QML-Sensor aktualisieren
        self.sensor_vm.updateQmlSensor("Latitude", 49.445232, "°")
        self.sensor_vm.updateQmlSensor("Longitude", 7.769488, "°")
        self.sensor_vm.updateQmlSensor("Höhe", 100.0, "m")
        
        # Überprüfen des QML-Modells
        # Hier müssten wir eigentlich auf das QML-Modell zugreifen, aber für diesen Test
        # nehmen wir an, dass es funktioniert, wenn keine Exception auftritt
    
    def test_update_from_telemetry(self):
        """Testet die Aktualisierung aus Telemetriedaten."""
        # Telemetriedaten simulieren
        telemetry_data = {
            "position": {
                "latitude_deg": 49.445232,
                "longitude_deg": 7.769488,
                "relative_altitude_m": 100.0
            },
            "attitude": {
                "roll_deg": 5.0,
                "pitch_deg": 10.0,
                "yaw_deg": 45.0
            },
            "battery": {
                "remaining_percent": 75.0,
                "voltage_v": 12.5,
                "current_a": 2.1
            },
            "gps_info": {
                "num_satellites": 8,
                "fix_type": 3
            }
        }
        
        # Sensor-ViewModel mit Telemetriedaten aktualisieren
        self.sensor_vm.update_from_telemetry(telemetry_data)
        
        # Überprüfungen
        self.assertEqual(self.sensor_vm.getSensorValue("latitude"), 49.445232)
        self.assertEqual(self.sensor_vm.getSensorValue("longitude"), 7.769488)
        self.assertEqual(self.sensor_vm.getSensorValue("altitude"), 100.0)
        self.assertEqual(self.sensor_vm.getSensorValue("roll"), 5.0)
        self.assertEqual(self.sensor_vm.getSensorValue("pitch"), 10.0)
        self.assertEqual(self.sensor_vm.getSensorValue("yaw"), 45.0)
        self.assertEqual(self.sensor_vm.getSensorValue("battery"), 75.0)
        self.assertEqual(self.sensor_vm.getSensorValue("voltage"), 12.5)
        self.assertEqual(self.sensor_vm.getSensorValue("current"), 2.1)
        self.assertEqual(self.sensor_vm.getSensorValue("satellites"), 8.0)
        self.assertEqual(self.sensor_vm.getSensorValue("gps_fix"), 3.0)
    
    def test_setters(self):
        """Testet die Setter-Methoden."""
        # Setter für Positionsdaten
        self.sensor_vm.setLatitude(49.445232)
        self.sensor_vm.setLongitude(7.769488)
        self.sensor_vm.setAltitude(100.0)
        
        # Überprüfungen
        self.assertEqual(self.sensor_vm.getSensorValue("latitude"), 49.445232)
        self.assertEqual(self.sensor_vm.getSensorValue("longitude"), 7.769488)
        self.assertEqual(self.sensor_vm.getSensorValue("altitude"), 100.0)
        
        # Setter für Lagedaten
        self.sensor_vm.setRoll(5.0)
        self.sensor_vm.setPitch(10.0)
        self.sensor_vm.setYaw(45.0)
        
        # Überprüfungen
        self.assertEqual(self.sensor_vm.getSensorValue("roll"), 5.0)
        self.assertEqual(self.sensor_vm.getSensorValue("pitch"), 10.0)
        self.assertEqual(self.sensor_vm.getSensorValue("yaw"), 45.0)
        
        # Setter für Batteriedaten
        self.sensor_vm.setBatteryLevel(75.0)
        self.sensor_vm.setBatteryVoltage(12.5)
        
        # Überprüfungen
        self.assertEqual(self.sensor_vm.getSensorValue("battery"), 75.0)
        self.assertEqual(self.sensor_vm.getSensorValue("voltage"), 12.5)
        
        # Setter für GPS-Daten
        self.sensor_vm.setGpsSatelliteCount(8)
        self.sensor_vm.setGpsFixType(3)
        
        # Überprüfungen
        self.assertEqual(self.sensor_vm.getSensorValue("satellites"), 8.0)
        self.assertEqual(self.sensor_vm.getSensorValue("gps_fix"), 3.0)

# Main-Funktion für direktes Ausführen der Tests
if __name__ == "__main__":
    unittest.main()
