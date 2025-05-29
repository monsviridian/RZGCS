"""
SensorViewModel für die Verbindung zwischen Sensordaten und UI
"""

from typing import Dict, Any, Optional, List
from PySide6.QtCore import QObject, Signal, Slot, Property, QTimer

from ..model.sensor_model import SensorData, DroneState


class SensorViewModel(QObject):
    """ViewModel für Sensordaten in MVVM-Architektur"""
    
    # Signale für UI-Updates
    sensorUpdated = Signal(str, object, str)  # name, value, unit
    sensorListChanged = Signal()
    connectionStatusChanged = Signal(bool)
    parametersUpdated = Signal()  # Neues Signal für Parameter-Updates
    
    def __init__(self):
        """Initialisiert das SensorViewModel"""
        super().__init__()
        
        # Interne Datenmodelle
        self._sensor_data = SensorData()
        self._drone_state = DroneState()
        
        # Liste von QML-Sensordaten für die Anzeige
        self._qml_sensors = []
        
        # Liste der ListElements für die SensorView
        self._list_elements = {}
        
        # Parametersammlung
        self._parameter_list = []
        self._parameter_dict = {}
        self._model = None  # MAVSDK-Connector als Modell
        
        # Timer für regelmäßige UI-Updates
        self._update_timer = QTimer()
        self._update_timer.timeout.connect(self._update_ui)
        self._update_timer.start(200)  # Alle 200ms aktualisieren
    
    def initialize_default_sensors(self):
        """Initialisiert die Standard-Sensoren"""
        default_sensors = [
            ("roll", "Roll", "°"),
            ("pitch", "Pitch", "°"),
            ("yaw", "Yaw", "°"),
            ("altitude", "Altitude", "m"),
            ("groundspeed", "Groundspeed", "m/s"),
            ("airspeed", "Airspeed", "m/s"),
            ("gps_lat", "GPS Latitude", "°"),
            ("gps_lon", "GPS Longitude", "°"),
            ("battery_voltage", "Voltage", "V"),
            ("battery_current", "Current", "A"),
            ("battery_remaining", "Battery", "%"),
        ]
        
        for sensor_id, name, unit in default_sensors:
            self._sensor_data.add_sensor(sensor_id, name, unit)
        
        # Systemsensoren für die SensorView hinzufügen
        list_elements = [
            {"name": "System Servos", "unit": ""},
            {"name": "System RC", "unit": ""},
            {"name": "System Mission", "unit": ""},
            {"name": "System CPU", "unit": ""},
            {"name": "Battery %", "unit": ""},
            {"name": "Roll", "unit": "°"},
            {"name": "Pitch", "unit": "°"},
            {"name": "Yaw", "unit": "°"},
            {"name": "Altitude", "unit": "m"},
            {"name": "Groundspeed", "unit": "m/s"},
            {"name": "Airspeed", "unit": "m/s"},
            {"name": "GPS Pos", "unit": "°"},
            {"name": "GPS Fix", "unit": ""},
            {"name": "GPS Satellites", "unit": ""},
            {"name": "Battery", "unit": "V"},
            {"name": "Firmware", "unit": ""},
            {"name": "Frame", "unit": ""},
            {"name": "Version", "unit": ""}
        ]
        
        for element in list_elements:
            self._list_elements[element["name"]] = {
                "name": element["name"],
                "value": "Nicht verbunden",
                "unit": element["unit"]
            }
        
        self.sensorListChanged.emit()
    
    @Slot(str, object)
    def update_sensor(self, sensor_id: str, value: Any) -> bool:
        """Aktualisiert einen Sensor im Datenmodell
        
        Args:
            sensor_id: ID des zu aktualisierenden Sensors
            value: Neuer Sensorwert
            
        Returns:
            bool: True, wenn der Sensor erfolgreich aktualisiert wurde
        """
        return self._sensor_data.update_sensor(sensor_id, value)
    
    @Slot(str, object, str)
    def updateQmlSensor(self, name: str, value: Any, unit: str):
        """Aktualisiert einen Sensor in der QML-Ansicht
        
        Args:
            name: Name des Sensors
            value: Sensorwert
            unit: Einheit des Sensors
        """
        # ListElement-Update für die SensorView
        if name in self._list_elements:
            self._list_elements[name]["value"] = value
            self._list_elements[name]["unit"] = unit
        
        # Signal für QML emittieren
        self.sensorUpdated.emit(name, value, unit)
    
    @Slot()
    def reset_values(self):
        """Setzt alle Sensorwerte auf Standardwerte zurück"""
        # Drohnenstatus zurücksetzen
        self._drone_state.reset()
        
        # ListElements zurücksetzen
        for name in self._list_elements:
            self._list_elements[name]["value"] = "Nicht verbunden"
        
        # UI-Update signalisieren
        self.sensorListChanged.emit()
        self.connectionStatusChanged.emit(False)
    
    @Slot(bool)
    def set_connection_status(self, is_connected: bool):
        """Setzt den Verbindungsstatus
        
        Args:
            is_connected: Neuer Verbindungsstatus
        """
        if self._drone_state.is_connected != is_connected:
            self._drone_state.is_connected = is_connected
            self.connectionStatusChanged.emit(is_connected)
            
            # Bei Verbindungsverlust alle Werte zurücksetzen
            if not is_connected:
                self.reset_values()
    
    @Property(bool)
    def is_connected(self) -> bool:
        """Gibt an, ob eine Verbindung besteht
        
        Returns:
            bool: True, wenn verbunden
        """
        return self._drone_state.is_connected
    
    @Slot(str)
    def get_sensor_value(self, sensor_id: str) -> Any:
        """Gibt den aktuellen Wert eines Sensors zurück
        
        Args:
            sensor_id: ID des gesuchten Sensors
            
        Returns:
            Sensorwert oder None, wenn nicht gefunden
        """
        sensor = self._sensor_data.get_sensor(sensor_id)
        if sensor:
            return sensor.value
        return None
    
    @Slot(result="QVariantList")
    def get_sensor_list(self) -> List[Dict[str, Any]]:
        """Gibt eine Liste aller Sensoren für QML zurück
        
        Returns:
            Liste von Sensor-Dictionaries mit Name, Wert und Einheit
        """
        result = []
        for name, data in self._list_elements.items():
            result.append({
                "name": name,
                "value": data["value"],
                "unit": data["unit"]
            })
        return result
    
    def _update_ui(self):
        """Aktualisiert die UI mit den neuesten Daten"""
        if not self._drone_state.is_connected:
            return
            
        # Hier könnten wir weitere UI-Updates durchführen, 
        # falls regelmäßige Updates benötigt werden
    
    # Methoden für Telemetriedaten aus dem MAVSDKConnector
    
    @Slot(str, dict)
    def update_from_telemetry(self, telemetry_type: str, telemetry_data: dict):
        """Aktualisiert Sensoren basierend auf Telemetriedaten
        
        Args:
            telemetry_type: Typ der Telemetrie (z.B. 'attitude', 'battery')
            telemetry_data: Telemetriedaten als Dictionary
        """
        # Wenn es Daten im richtigen Format gibt, verwende sie
        if "data" in telemetry_data:
            data_dict = telemetry_data["data"]
            
            # Verarbeite die Sensordaten je nach Telemetrie-Typ
            if telemetry_type == "attitude":
                if "roll" in data_dict:
                    self._list_elements["Roll"] = {
                        "name": "Roll", 
                        "value": data_dict["roll"]["value"],
                        "unit": data_dict["roll"]["unit"]
                    }
                if "pitch" in data_dict:
                    self._list_elements["Pitch"] = {
                        "name": "Pitch", 
                        "value": data_dict["pitch"]["value"],
                        "unit": data_dict["pitch"]["unit"]
                    }
                if "yaw" in data_dict:
                    self._list_elements["Yaw"] = {
                        "name": "Yaw", 
                        "value": data_dict["yaw"]["value"],
                        "unit": data_dict["yaw"]["unit"]
                    }
                    
            elif telemetry_type == "battery":
                if "remaining" in data_dict:
                    self._list_elements["Battery"] = {
                        "name": "Battery", 
                        "value": data_dict["remaining"]["value"],
                        "unit": data_dict["remaining"]["unit"]
                    }
                if "voltage" in data_dict:
                    self._list_elements["Voltage"] = {
                        "name": "Voltage", 
                        "value": data_dict["voltage"]["value"],
                        "unit": data_dict["voltage"]["unit"]
                    }
                    
            elif telemetry_type == "position":
                if "abs_altitude" in data_dict:
                    self._list_elements["Altitude"] = {
                        "name": "Altitude", 
                        "value": data_dict["abs_altitude"]["value"],
                        "unit": data_dict["abs_altitude"]["unit"]
                    }
                    
            elif telemetry_type == "gps_info":
                if "fix_type" in data_dict:
                    self._list_elements["GPS Fix"] = {
                        "name": "GPS Fix", 
                        "value": data_dict["fix_type"]["value"],
                        "unit": data_dict["fix_type"]["unit"]
                    }
                if "num_satellites" in data_dict:
                    self._list_elements["Satellites"] = {
                        "name": "Satellites", 
                        "value": data_dict["num_satellites"]["value"],
                        "unit": data_dict["num_satellites"]["unit"]
                    }
                    
        # UI benachrichtigen
        self.sensorListChanged.emit()
        
    # MAVSDK Telemetrie-Setter-Methoden
    @Slot(float)
    def setRoll(self, value):
        """Setzt den Roll-Wert"""
        self.update_sensor("roll", value)
        if "Roll" in self._list_elements:
            self._list_elements["Roll"]["value"] = f"{value:.1f}"
            self.sensorListChanged.emit()
    
    @Slot(float)
    def setPitch(self, value):
        """Setzt den Pitch-Wert"""
        self.update_sensor("pitch", value)
        if "Pitch" in self._list_elements:
            self._list_elements["Pitch"]["value"] = f"{value:.1f}"
            self.sensorListChanged.emit()
    
    @Slot(float)
    def setYaw(self, value):
        """Setzt den Yaw-Wert"""
        self.update_sensor("yaw", value)
        if "Yaw" in self._list_elements:
            self._list_elements["Yaw"]["value"] = f"{value:.1f}"
            self.sensorListChanged.emit()
    
    @Slot(float)
    def setAltitude(self, value):
        """Setzt den Altitude-Wert"""
        self.update_sensor("altitude", value)
        if "Altitude" in self._list_elements:
            self._list_elements["Altitude"]["value"] = f"{value:.1f}"
            self.sensorListChanged.emit()
    
    @Slot(float)
    def setGroundspeed(self, value):
        """Setzt den Groundspeed-Wert"""
        self.update_sensor("groundspeed", value)
        if "Groundspeed" in self._list_elements:
            self._list_elements["Groundspeed"]["value"] = f"{value:.1f}"
            self.sensorListChanged.emit()
    
    @Slot(float)
    def setAirspeed(self, value):
        """Setzt den Airspeed-Wert"""
        self.update_sensor("airspeed", value)
        if "Airspeed" in self._list_elements:
            self._list_elements["Airspeed"]["value"] = f"{value:.1f}"
            self.sensorListChanged.emit()
    
    @Slot(float, float)
    def setGpsPosition(self, lat, lon):
        """Setzt die GPS-Position"""
        self.update_sensor("gps_lat", lat)
        self.update_sensor("gps_lon", lon)
        if "GPS Pos" in self._list_elements:
            self._list_elements["GPS Pos"]["value"] = f"{lat:.6f}, {lon:.6f}"
            self.sensorListChanged.emit()
    
    @Slot(int)
    def setGpsSatelliteCount(self, count):
        """Setzt die Anzahl der GPS-Satelliten"""
        self.update_sensor("gps_satellites", count)
        if "GPS Satellites" in self._list_elements:
            self._list_elements["GPS Satellites"]["value"] = str(count)
            self.sensorListChanged.emit()
    
    @Slot(int)
    def setGpsFix(self, fix_type):
        """Setzt den GPS-Fix-Typ"""
        self.update_sensor("gps_fix", fix_type)
        if "GPS Fix" in self._list_elements:
            fix_text = "No Fix"
            if fix_type == 2:
                fix_text = "2D Fix"
            elif fix_type >= 3:
                fix_text = "3D Fix"
            self._list_elements["GPS Fix"]["value"] = fix_text
            self.sensorListChanged.emit()
    
    @Slot(float)
    def setBatteryVoltage(self, voltage):
        """Setzt die Batteriespannung"""
        self.update_sensor("battery_voltage", voltage)
        if "Battery" in self._list_elements:
            self._list_elements["Battery"]["value"] = f"{voltage:.2f}"
            self.sensorListChanged.emit()
            
    @Slot(float)
    def setCurrent(self, current):
        """Setzt den Batteriestrom"""
        self.update_sensor("battery_current", current)
        if "Current" in self._list_elements:
            self._list_elements["Current"]["value"] = f"{current:.2f}"
            self.sensorListChanged.emit()
    
    @Slot(float)
    def setBatteryRemaining(self, remaining):
        """Setzt die verbleibende Batteriekapazität in Prozent"""
        self.update_sensor("battery_remaining", remaining)
        if "Battery %" in self._list_elements:
            self._list_elements["Battery %"]["value"] = f"{remaining:.1f}"
            self.sensorListChanged.emit()
            
    @Slot(dict)
    def setHealthStatus(self, health_info):
        """Setzt den Gesundheitsstatus der Drohne"""
        # System-Sensoren aktualisieren
        if "Firmware" in self._list_elements:
            # Allgemeiner Systemzustand
            overall_status = "OK"
            if not health_info.get("is_global_position_ok", False) or not health_info.get("is_home_position_ok", False):
                overall_status = "GPS/Home FEHLT"
            elif not health_info.get("is_gyrometer_calibration_ok", False):
                overall_status = "GYRO KALIBRIEREN"
            elif not health_info.get("is_accelerometer_calibration_ok", False):
                overall_status = "ACCEL KALIBRIEREN"
            elif not health_info.get("is_magnetometer_calibration_ok", False):
                overall_status = "MAG KALIBRIEREN"
            elif not health_info.get("is_local_position_ok", False):
                overall_status = "POS UNGENAU"
                
            self._list_elements["Firmware"]["value"] = overall_status
            self.sensorListChanged.emit()

    @Slot(bool)
    def setHealthAllOk(self, all_ok):
        """Setzt den Gesamtstatus der Drohne (alle Gesundheitsprüfungen OK)"""
        if "System Servos" in self._list_elements:
            self._list_elements["System Servos"]["value"] = "READY" if all_ok else "CHECK"
            self.sensorListChanged.emit()
            
    @Slot(bool)
    def setInAir(self, in_air):
        """Setzt den In-Air-Status der Drohne"""
        self.update_sensor("in_air", in_air)
        if "System Mission" in self._list_elements:
            self._list_elements["System Mission"]["value"] = "FLYING" if in_air else "LANDED"
            self.sensorListChanged.emit()
            
    @Slot(float)
    def setHeading(self, heading):
        """Setzt die Kompassrichtung (Heading) in Grad"""
        # Heading ist ähnlich wie Yaw, aber bezogen auf magnetischen Norden
        self.update_sensor("heading", heading)
        # Keine direkte UI-Aktualisierung, da dies oft im Yaw-Wert abgedeckt wird
        
    @Slot(dict)
    def setAngularVelocity(self, velocity_info):
        """Setzt die Winkelgeschwindigkeit der Drohne"""
        # Sensoren für Rotationsgeschwindigkeit aktualisieren
        self.update_sensor("angular_velocity_roll", velocity_info.get("roll_rad_s", 0.0))
        self.update_sensor("angular_velocity_pitch", velocity_info.get("pitch_rad_s", 0.0))
        self.update_sensor("angular_velocity_yaw", velocity_info.get("yaw_rad_s", 0.0))
        
    @Slot(dict)
    def setStatusText(self, text_info):
        """Verarbeitet Status-Texte vom Flight Controller"""
        text = text_info.get("text", "")
        msg_type = text_info.get("type", "INFO")
        
        # Status-Texte könnten für spezielle UI-Updates verwendet werden
        # Zum Beispiel für wichtige Warnungen
        if "WARNING" in msg_type or "ERROR" in msg_type:
            if "System CPU" in self._list_elements:
                self._list_elements["System CPU"]["value"] = text[:15] + "..." if len(text) > 15 else text
                self.sensorListChanged.emit()
                
    @Slot(dict)
    def setAltitudeInfo(self, altitude_info):
        """Setzt die Höheninformationen der Drohne"""
        # Relative Höhe für die Anzeige verwenden (Höhe über Startpunkt)
        rel_altitude = altitude_info.get("relative", 0.0)
        self.setAltitude(rel_altitude)  # Verwende bestehende Methode
        
        # Zusätzliche Höheninformationen speichern
        self.update_sensor("altitude_absolute", altitude_info.get("absolute", 0.0))
        if altitude_info.get("agl") is not None:
            self.update_sensor("altitude_agl", altitude_info.get("agl", 0.0))
            
    @Slot(str)
    def setLandedState(self, state_str):
        """Setzt den Landezustand der Drohne"""
        self.update_sensor("landed_state", state_str)
        # Könnte in der UI verwendet werden, um den Landezustand anzuzeigen
        
    @Slot(dict)
    def setRcStatus(self, rc_info):
        """Setzt den RC-Status (Fernbedienung)"""
        is_available = rc_info.get("available", False)
        signal_strength = rc_info.get("signal_strength", 0)
        
        self.update_sensor("rc_available", is_available)
        self.update_sensor("rc_signal_strength", signal_strength)
        
        if "System RC" in self._list_elements:
            if is_available:
                self._list_elements["System RC"]["value"] = f"{signal_strength}%"
            else:
                self._list_elements["System RC"]["value"] = "KEINE RC"
            self.sensorListChanged.emit()
            
    @Slot(int)
    def setUnixEpochTime(self, time_us):
        """Setzt die Unix-Epochenzeit vom Flight Controller"""
        # Umrechnung in Sekunden
        time_s = time_us / 1000000.0
        self.update_sensor("fc_time", time_s)
        
    @Slot(dict)
    def setActuatorControl(self, control_info):
        """Setzt die Aktuator-Steuerungsdaten"""
        group = control_info.get("group", 0)
        controls = control_info.get("controls", [])
        
        # Speichere die Steuerwerte nach Gruppe
        self.update_sensor(f"actuator_control_group_{group}", controls)
        
    @Slot(dict)
    def setActuatorOutput(self, output_info):
        """Setzt die Aktuator-Ausgabedaten"""
        active = output_info.get("active", 0)
        actuators = output_info.get("actuator", [])
        
        # Speichere die Aktuator-Werte
        self.update_sensor("actuator_output_active", active)
        self.update_sensor("actuator_output_values", actuators)
        
        # System-Servos-Status aktualisieren
        if "System Servos" in self._list_elements and actuators:
            # Zeige die Anzahl aktiver Aktuatoren an
            self._list_elements["System Servos"]["value"] = f"AKTIV: {active}"
            self.sensorListChanged.emit()
    
    @Slot(dict)
    def setOdometry(self, odometry_info):
        """Setzt die Odometrie-Daten"""
        # Positionsdaten
        position = odometry_info.get("position", {})
        self.update_sensor("odom_pos_x", position.get("x", 0.0))
        self.update_sensor("odom_pos_y", position.get("y", 0.0))
        self.update_sensor("odom_pos_z", position.get("z", 0.0))
        
        # Geschwindigkeitsdaten
        velocity = odometry_info.get("velocity", {})
        self.update_sensor("odom_vel_x", velocity.get("x", 0.0))
        self.update_sensor("odom_vel_y", velocity.get("y", 0.0))
        self.update_sensor("odom_vel_z", velocity.get("z", 0.0))
        
        # Berechnung der Gesamtgeschwindigkeit (für Groundspeed)
        vel_x = velocity.get("x", 0.0)
        vel_y = velocity.get("y", 0.0)
        import math
        ground_speed = math.sqrt(vel_x * vel_x + vel_y * vel_y)
        self.setGroundspeed(ground_speed)
    
    @Slot(dict)
    def setDistanceSensor(self, distance_info):
        """Setzt die Distanzsensor-Daten"""
        min_dist = distance_info.get("minimum_distance_m", 0.0)
        max_dist = distance_info.get("maximum_distance_m", 0.0)
        current_dist = distance_info.get("current_distance_m", 0.0)
        
        self.update_sensor("distance_min", min_dist)
        self.update_sensor("distance_max", max_dist)
        self.update_sensor("distance_current", current_dist)
    
    @Slot(dict)
    def setScaledPressure(self, pressure_info):
        """Setzt die Drucksensor-Daten"""
        abs_pressure = pressure_info.get("absolute_pressure_hpa", 0.0)
        diff_pressure = pressure_info.get("differential_pressure_hpa", 0.0)
        temperature = pressure_info.get("temperature_deg", 0.0)
        
        self.update_sensor("pressure_absolute", abs_pressure)
        self.update_sensor("pressure_differential", diff_pressure)
        self.update_sensor("pressure_temp", temperature)
        
        # Aktualisiere den CPU-Status in der UI, um Temperatur anzuzeigen
        if "System CPU" in self._list_elements:
            self._list_elements["System CPU"]["value"] = f"{temperature:.1f}°C"
            self.sensorListChanged.emit()
    
    @Slot(dict)
    def setRawImu(self, imu_info):
        """Setzt die rohen IMU-Daten"""
        # Beschleunigungsdaten
        accel = imu_info.get("acceleration", {})
        self.update_sensor("accel_x", accel.get("x", 0.0))
        self.update_sensor("accel_y", accel.get("y", 0.0))
        self.update_sensor("accel_z", accel.get("z", 0.0))
        
        # Gyro-Daten (Winkelgeschwindigkeit)
        gyro = imu_info.get("gyro", {})
        self.update_sensor("gyro_x", gyro.get("x", 0.0))
        self.update_sensor("gyro_y", gyro.get("y", 0.0))
        self.update_sensor("gyro_z", gyro.get("z", 0.0))
        
        # Magnetometer-Daten
        mag = imu_info.get("magnetic_field", {})
        self.update_sensor("mag_x", mag.get("x", 0.0))
        self.update_sensor("mag_y", mag.get("y", 0.0))
        self.update_sensor("mag_z", mag.get("z", 0.0))
        
        # Temperatur
        temp = imu_info.get("temperature", 0.0)
        self.update_sensor("imu_temp", temp)
    
    @Slot(float)
    def setBatteryCurrent(self, current):
        """Setzt den Batteriestrom"""
        self.update_sensor("battery_current", current)
        
    # Parameter-Verwaltung
    @Slot(list)
    def setParameters(self, parameter_list):
        """Verarbeitet die Liste der Parameter vom Flight Controller
        
        Args:
            parameter_list: Liste der Parameter vom Flight Controller
        """
        # Parameter-Listen-Signal emittieren
        self._parameter_list = parameter_list
        
        # Parameter-Dictionary erstellen
        self._parameter_dict = {param["name"]: param for param in parameter_list}
        
        # Signalisieren, dass die Parameter-Liste aktualisiert wurde
        self.parametersUpdated.emit()
        
        # Wichtige Parameter im UI anzeigen
        self._update_key_parameters_in_ui()
        
        # Log-Parameter für Debug-Zwecke
        print(f"[INFO] {len(parameter_list)} Parameter geladen")
        
    def _update_key_parameters_in_ui(self):
        """Aktualisiert wichtige Parameter in der UI"""
        # Firmware-Version anzeigen
        if "FIRMWARE_VERSION" in self._parameter_dict:
            if "Firmware" in self._list_elements:
                self._list_elements["Firmware"]["value"] = str(self._parameter_dict["FIRMWARE_VERSION"]["value"])
                self.sensorListChanged.emit()
                
        # Vehicle Type anzeigen
        if "VEHICLE_TYPE" in self._parameter_dict:
            if "Frame" in self._list_elements:
                vehicle_type = str(int(self._parameter_dict["VEHICLE_TYPE"]["value"]))
                vehicle_names = {
                    "1": "Fixed Wing",
                    "2": "Quadrotor",
                    "3": "Hexarotor",
                    "4": "Octorotor",
                    "5": "Tricopter",
                    "10": "Rover",
                    "11": "Boat"
                }
                self._list_elements["Frame"]["value"] = vehicle_names.get(vehicle_type, f"Type {vehicle_type}")
                self.sensorListChanged.emit()
                
        # Version anzeigen
        if "SYS_AUTOSTART" in self._parameter_dict:
            if "Version" in self._list_elements:
                self._list_elements["Version"]["value"] = str(self._parameter_dict["SYS_AUTOSTART"]["value"])
                self.sensorListChanged.emit()
    
    @Slot(str, result="QVariant")
    def getParameterValue(self, name):
        """Gibt den Wert eines Parameters zurück
        
        Args:
            name: Name des Parameters
            
        Returns:
            Der Wert des Parameters oder None, wenn der Parameter nicht existiert
        """
        if name in self._parameter_dict:
            return self._parameter_dict[name]["value"]
        return None
        
    @Slot(str, str, str, result=bool)
    def setParameterValue(self, name, value, param_type=None):
        """Setzt den Wert eines Parameters
        
        Args:
            name: Name des Parameters
            value: Neuer Parameterwert
            param_type: Typ des Parameters ('int', 'float', oder None für automatische Erkennung)
            
        Returns:
            bool: True, wenn der Parameter erfolgreich gesetzt wurde
        """
        # MAVSDK-Connector aufrufen
        if self._model and hasattr(self._model, 'set_parameter'):
            return self._model.set_parameter(name, value, param_type)
        return False
    
    @Slot(result=list)
    def getParameterList(self):
        """Gibt die Liste aller Parameter zurück
        
        Returns:
            Die Liste aller Parameter
        """
        return self._parameter_list
    
    @Slot(str, result="QVariant")
    def getParameterInfo(self, name):
        """Gibt die vollständigen Informationen zu einem Parameter zurück
        
        Args:
            name: Name des Parameters
            
        Returns:
            Ein Dictionary mit allen Informationen zum Parameter oder None, wenn nicht gefunden
        """
        if name in self._parameter_dict:
            return self._parameter_dict[name]
        return None
    
    @Slot(float)
    def setBatteryRemaining(self, remaining):
        """Setzt die verbleibende Batteriekapazität in Prozent"""
        self.update_sensor("battery_remaining", remaining)
        if "Battery %" in self._list_elements:
            self._list_elements["Battery %"]["value"] = f"{remaining:.0f}"
            self.sensorListChanged.emit()
