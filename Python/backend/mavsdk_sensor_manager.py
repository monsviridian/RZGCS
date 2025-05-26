"""
MAVSDK-basierter SensorManager für RZGCS
Bietet eine moderne Alternative zum pymavlink-basierten SensorManager
"""

import re
import time
from typing import Optional, Dict, Any

from PySide6.QtCore import QObject, Signal, Slot

from mavsdk.telemetry import (
    Position, 
    Attitude, 
    Battery,
    GpsInfo,
    ActuatorOutputStatus
)

from .logger import Logger


class MAVSDKSensorManager(QObject):
    """Manager für Sensordaten über MAVSDK"""
    
    # Signale
    sensorUpdated = Signal(str, object)
    errorOccurred = Signal(str)
    
    def __init__(self, logger: Logger):
        """Initialisiert den MAVSDK SensorManager
        
        Args:
            logger: Logger-Instanz für die Protokollierung
        """
        super().__init__()
        self._logger = logger
        self._sensor_model = None
        self._is_connected = False
        
        # Sensordaten-Zwischenspeicher
        self._servo_output_data = None
        self._rc_channels_data = None
        self._battery_data = None
        self._position_data = None
        self._attitude_data = None
        
        self._logger.addLog("MAVSDK SensorManager initialisiert")
    
    def initialize_model(self, model):
        """Initialisiert das Sensormodell mit diesem Manager
        
        Args:
            model: Das zu initialisierende SensorViewModel
        """
        self._sensor_model = model
        self._logger.addLog("SensorModel an MAVSDK SensorManager angebunden")
    
    def set_connected(self):
        """Setze den Verbindungsstatus auf verbunden"""
        self._is_connected = True
        self._logger.addLog("MAVSDKSensorManager: Verbindung hergestellt")
        
    def set_disconnected(self):
        """Setze den Verbindungsstatus auf getrennt"""
        self._is_connected = False
        self._logger.addLog("MAVSDKSensorManager: Verbindung getrennt")
        
        # Alle Sensoren auf Standardwerte zurücksetzen
        self._reset_sensor_values()
    
    def _reset_sensor_values(self):
        """Setze alle Sensorwerte auf Standardwerte zurück und lösche gecachte Daten"""
        if hasattr(self._sensor_model, 'updateQmlSensor'):
            # UI auf "Nicht verbunden" setzen
            self._sensor_model.updateQmlSensor("System Servos", "Nicht verbunden", "")
            self._sensor_model.updateQmlSensor("System RC", "Nicht verbunden", "")
            self._sensor_model.updateQmlSensor("System Mission", "Nicht verbunden", "")
            self._sensor_model.updateQmlSensor("System CPU", "Nicht verbunden", "")
            self._sensor_model.updateQmlSensor("Battery %", "Nicht verbunden", "")
            
            # Wichtig: Alle gecachten Werte löschen
            self._servo_output_data = None
            self._rc_channels_data = None
            self._battery_data = None
            self._position_data = None
            self._attitude_data = None
            
            # Debug-Nachricht zur Verfolgung
            self._logger.addLog("Alle Sensor-Caches zurückgesetzt nach Verbindungstrennung")
        
        # Sicherstellen, dass keine weiteren Updates mehr erfolgen
        self._is_connected = False
    
    def handle_system_info(self, info_text):
        """Handle system information status text from the flight controller"""
        try:
            # Prüfen, ob verbunden
            if not self._is_connected:
                return
                
            # Parse firmware info
            if "ArduCopter" in info_text or "ArduPlane" in info_text or "ArduRover" in info_text:
                self._firmware_info = info_text.split(" ")[0]  # Extract ArduCopter/ArduPlane/etc
                self._update_qml_sensor("Firmware", self._firmware_info, "")
                
            # Parse frame type
            frame_match = re.search(r"Frame: (\w+)", info_text)
            if frame_match:
                self._frame_type = frame_match.group(1)
                self._update_qml_sensor("Frame", self._frame_type, "")
                
            # Parse firmware version
            version_match = re.search(r"(\d+\.\d+\.\d+|\d+\.\d+)\b", info_text)
            if version_match:
                self._firmware_version = version_match.group(0)
                self._update_qml_sensor("Version", self._firmware_version, "")
                
        except Exception as e:
            error_msg = f"❌ Error parsing system info: {str(e)}"
            self._logger.addLog(error_msg)
            self.errorOccurred.emit(error_msg)
    
    @Slot(object)
    def handle_position(self, position: Position):
        """Handle position updates from MAVSDK
        
        Args:
            position: Position-Objekt von MAVSDK
        """
        try:
            # Prüfen, ob verbunden
            if not self._is_connected:
                return
                
            # Position-Daten extrahieren
            latitude = position.latitude_deg
            longitude = position.longitude_deg
            absolute_altitude = position.absolute_altitude_m
            relative_altitude = position.relative_altitude_m
            
            # Speichere Position-Daten für spätere Verwendung
            self._position_data = {
                'lat': latitude,
                'lon': longitude,
                'alt_abs': absolute_altitude,
                'alt_rel': relative_altitude
            }
            
            # Aktualisiere Python-Modell
            self._sensor_model.update_sensor("gps_lat", latitude)
            self._sensor_model.update_sensor("gps_lon", longitude)
            self._sensor_model.update_sensor("altitude", relative_altitude)
            
            # Aktualisiere QML-Modell
            self._update_qml_sensor("GPS Pos", f"{latitude:.6f}, {longitude:.6f}", "°")
            self._update_qml_sensor("Altitude", round(relative_altitude, 1), "m")
            
            # Signale emittieren
            self.sensorUpdated.emit("position", position)
            
        except Exception as e:
            error_msg = f"Error handling position: {str(e)}"
            self._logger.addLog(error_msg)
            self.errorOccurred.emit(error_msg)
    
    @Slot(object)
    def handle_attitude(self, attitude: Attitude):
        """Handle attitude updates from MAVSDK
        
        Args:
            attitude: Attitude-Objekt von MAVSDK
        """
        try:
            # Prüfen, ob verbunden
            if not self._is_connected:
                return
                
            # Attitude-Daten extrahieren (bereits in Grad)
            roll = attitude.roll_deg
            pitch = attitude.pitch_deg
            yaw = attitude.yaw_deg
            
            # Speichere Attitude-Daten für spätere Verwendung
            self._attitude_data = {
                'roll': roll,
                'pitch': pitch,
                'yaw': yaw
            }
            
            # Aktualisiere Python-Modell
            self._sensor_model.update_sensor("roll", roll)
            self._sensor_model.update_sensor("pitch", pitch)
            self._sensor_model.update_sensor("yaw", yaw)
            
            # Aktualisiere QML-Modell
            self._update_qml_sensor("Roll", round(roll, 1), "°")
            self._update_qml_sensor("Pitch", round(pitch, 1), "°")
            self._update_qml_sensor("Yaw", round(yaw, 1), "°")
            
            # Signale emittieren
            self.sensorUpdated.emit("attitude", attitude)
            
        except Exception as e:
            error_msg = f"Error handling attitude: {str(e)}"
            self._logger.addLog(error_msg)
            self.errorOccurred.emit(error_msg)
    
    @Slot(object)
    def handle_battery(self, battery: Battery):
        """Handle battery updates from MAVSDK
        
        Args:
            battery: Battery-Objekt von MAVSDK
        """
        try:
            # Prüfen, ob verbunden
            if not self._is_connected:
                return
                
            # Battery-Daten extrahieren
            voltage = battery.voltage_v
            remaining = battery.remaining_percent
            
            # Batterieprozentsatz validieren und korrigieren
            if remaining < 0 or remaining > 100:
                # Wenn der Wert außerhalb des gültigen Bereichs liegt, verwenden wir einen Standardwert
                self._logger.addLog(f"[WARN] Ungültiger Batteriewert empfangen: {remaining}%")
                remaining = 0  # Standardwert, wenn keine gültige Prozentangabe empfangen wurde
            
            # Speichere in Python-Modell
            self._sensor_model.update_sensor("battery_voltage", round(voltage, 1))
            self._sensor_model.update_sensor("battery_remaining", round(remaining, 0))
            
            # Forciere einen gültigen Batterieprozentsatz für die Anzeige
            # Bei negativen oder zu großen Werten verwenden wir 0%
            display_remaining = max(0, min(100, round(remaining, 0)))
            
            # Aktualisiere QML-Modell mit korrigierten Werten
            battery_data = {"voltage": round(voltage, 1), "remaining": display_remaining}
            
            # Debug-Nachricht zur Verfolgung
            self._logger.addLog(f"[DEBUG] Battery % Update: Original={remaining}, Display={display_remaining}%")
            
            # Zum QML-Modell senden
            if hasattr(self._sensor_model, 'updateQmlSensor'):
                self._sensor_model.updateQmlSensor("Battery", battery_data, "V")
                # Zeige den Batterieprozentsatz auch als eigenen Sensor an
                self._sensor_model.updateQmlSensor("Battery %", f"{display_remaining}%", "")
            
            self.sensorUpdated.emit("battery", voltage)
            
        except Exception as e:
            error_msg = f"Error handling battery: {str(e)}"
            self._logger.addLog(error_msg)
            self.errorOccurred.emit(error_msg)
    
    @Slot(object)
    def handle_gps_info(self, gps_info: GpsInfo):
        """Handle GPS info updates from MAVSDK
        
        Args:
            gps_info: GpsInfo-Objekt von MAVSDK
        """
        try:
            # Prüfen, ob verbunden
            if not self._is_connected:
                return
                
            # GPS-Daten extrahieren
            num_satellites = gps_info.num_satellites
            fix_type = gps_info.fix_type
            
            # Fix-Typ in Text umwandeln
            fix_text = "No Fix"
            if fix_type == GpsInfo.FixType.FIX_2D:
                fix_text = "2D Fix"
            elif fix_type == GpsInfo.FixType.FIX_3D:
                fix_text = "3D Fix"
            elif fix_type == GpsInfo.FixType.FIX_DGPS:
                fix_text = "DGPS Fix"
            elif fix_type == GpsInfo.FixType.RTK_FLOAT:
                fix_text = "RTK Float"
            elif fix_type == GpsInfo.FixType.RTK_FIXED:
                fix_text = "RTK Fixed"
            
            # Aktualisiere QML-Modell
            self._update_qml_sensor("GPS Fix", fix_text, "")
            self._update_qml_sensor("GPS Satellites", num_satellites, "")
            
            # Signale emittieren
            self.sensorUpdated.emit("gps_info", gps_info)
            
        except Exception as e:
            error_msg = f"Error handling GPS info: {str(e)}"
            self._logger.addLog(error_msg)
            self.errorOccurred.emit(error_msg)
    
    @Slot(object)
    def handle_actuator_output(self, actuator_output: ActuatorOutputStatus):
        """Handle actuator output updates from MAVSDK
        
        Args:
            actuator_output: ActuatorOutputStatus-Objekt von MAVSDK
        """
        try:
            # Prüfen, ob verbunden
            if not self._is_connected:
                return
                
            # Servo-Werte extrahieren (maximal 8)
            servo_data = {}
            servo_values = []
            
            # Maximal 8 Servos
            for i in range(min(8, len(actuator_output.actuator))):
                value = int(actuator_output.actuator[i])
                servo_data[f'S{i+1}'] = value
                servo_values.append(f"S{i+1}={value}")
            
            # Speichere Servo-Daten für spätere Verwendung
            self._servo_output_data = servo_data
            
            # Aktualisiere QML-Modell mit Servo-Daten
            self._update_qml_sensor("Servos", servo_data, "")
            
            # Formatierte Servo-Werte für SensorView
            if servo_values:
                servo_info = ", ".join(servo_values)
                # Debug-Nachricht zur Verfolgung
                self._logger.addLog(f"[DEBUG] System Servos Update: {servo_info}")
                # Aktualisiere direkt im QML-Modell
                if hasattr(self._sensor_model, 'updateQmlSensor'):
                    self._sensor_model.updateQmlSensor("System Servos", servo_info, "")
            
        except Exception as e:
            error_msg = f"Error handling actuator output: {str(e)}"
            self._logger.addLog(error_msg)
            self.errorOccurred.emit(error_msg)
    
    def _update_qml_sensor(self, name, value, unit):
        """Update a sensor in the QML model using the QML update_sensor function"""
        if hasattr(self._sensor_model, 'updateQmlSensor'):
            self._sensor_model.updateQmlSensor(name, value, unit)
