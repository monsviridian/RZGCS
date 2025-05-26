from PySide6.QtCore import QObject, Signal, Slot
import time
import re
from backend.sensorviewmodel import SensorViewModel
from .logger import Logger

class SensorManager(QObject):
    """Manages sensor data and updates"""
    
    # Signals
    sensorUpdated = Signal(str, object)  # Emits sensor name and value
    errorOccurred = Signal(str)  # Emits error message
    systemInfoRequested = Signal()  # Signal when system info is requested
    
    def __init__(self, sensor_model: SensorViewModel, logger: Logger):
        super().__init__()
        self._sensor_model = sensor_model
        self._logger = logger
        self._is_connected = False  # Verbindungsstatus hinzufügen
        
        # Speicher für Sensordaten
        self._attitude_data = {}
        self._gps_data = {}
        self._hud_data = {}
        self._rc_channels_data = {}
        self._servo_output_data = {}
        
        # Zeitstempel für die letzte Aktualisierung jedes Sensors
        self._last_update_time = {}
        
        # Minimale Zeit zwischen Aktualisierungen in Millisekunden
        self._min_update_interval = {
            # Grundsensoren mit schnellerer Aktualisierung
            "Roll": 500,          # 0.5 Sekunden
            "Pitch": 500,         # 0.5 Sekunden
            "Yaw": 500,           # 0.5 Sekunden
            "Groundspeed": 1000,  # 1 Sekunde
            "Airspeed": 1000,     # 1 Sekunde
            "Altitude": 1000,     # 1 Sekunde
            "GPS": 2000,          # 2 Sekunden
            "Battery": 3000,      # 3 Sekunden
            
            # Systeminfos mit langsamerer Aktualisierung
            "System Servos": 5000,   # 5 Sekunden
            "System RC": 5000,       # 5 Sekunden
            "System Mission": 5000,  # 5 Sekunden
            "System CPU": 5000,      # 5 Sekunden
            "Battery %": 5000,       # 5 Sekunden
            "CPU Last": 5000         # 5 Sekunden
        }
        
        # Letzte Werte für jeden Sensor speichern
        self._last_values = {}
        self._firmware_info = "Unbekannt"
        self._frame_type = "Unbekannt"
        self._firmware_version = "Unbekannt"
        self._system_info_requested = False
        self._last_request_time = 0
        
    def request_system_info(self):
        """Request system information from the flight controller"""
        self._system_info_requested = True
        self._last_request_time = time.time()
        self.systemInfoRequested.emit()
        self._logger.addLog("✅ FC-Daten für SensorView angefordert")
        
    @Slot(str)
    def handle_system_info(self, info_text):
        """Handle system information status text from the flight controller"""
        try:
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
    def handle_attitude(self, msg):
        """Handle attitude message"""
        try:
            roll = round(msg.roll * 57.3, 2)  # Umrechnung von Radiant in Grad
            pitch = round(msg.pitch * 57.3, 2)  # Umrechnung von Radiant in Grad
            yaw = round(msg.yaw * 57.3, 2)  # Umrechnung von Radiant in Grad
            
            # Speichere in Python-Modell
            self._sensor_model.update_sensor("roll", roll)
            self._sensor_model.update_sensor("pitch", pitch)
            self._sensor_model.update_sensor("yaw", yaw)
            
            # Aktualisiere QML-Modell
            imu_data = {"roll": roll, "pitch": pitch}
            self._update_qml_sensor("IMU", imu_data, "")
            self.sensorUpdated.emit("attitude", roll)
        except Exception as e:
            error_msg = f"❌ Error handling attitude: {str(e)}"
            self._logger.addLog(error_msg)
            self.errorOccurred.emit(error_msg)
            
    @Slot(object)
    def handle_gps(self, msg):
        """Handle GPS message"""
        try:
            lat = msg.lat / 1e7
            lon = msg.lon / 1e7
            alt = msg.relative_alt / 1000.0
            
            # Speichere in Python-Modell
            self._sensor_model.update_sensor("gps_lat", round(lat, 6))
            self._sensor_model.update_sensor("gps_lon", round(lon, 6))
            self._sensor_model.update_sensor("altitude", round(alt, 1))
            
            # Calculate ground speed
            vx = msg.vx / 100.0
            vy = msg.vy / 100.0
            ground_speed = (vx*vx + vy*vy)**0.5
            self._sensor_model.update_sensor("groundspeed", round(ground_speed, 1))
            
            # Aktualisiere QML-Modell
            gps_data = {"latitude": lat, "longitude": lon}
            self._update_qml_sensor("GPS", gps_data, "")
            self._update_qml_sensor("Altitude", round(alt, 1), "m")
            
            self.sensorUpdated.emit("gps", lat)
        except Exception as e:
            error_msg = f"❌ Error handling GPS: {str(e)}"
            self._logger.addLog(error_msg)
            self.errorOccurred.emit(error_msg)
            
    # Methoden zum Setzen und Zurücksetzen des Verbindungsstatus
    def set_connected(self):
        """Setze den Verbindungsstatus auf verbunden"""
        self._is_connected = True
        self._logger.addLog("SensorManager: Verbindung hergestellt")
        
    def set_disconnected(self):
        """Setze den Verbindungsstatus auf getrennt"""
        self._is_connected = False
        self._logger.addLog("SensorManager: Verbindung getrennt")
        
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
            
            # Debug-Nachricht zur Verfolgung
            self._logger.addLog("Alle Sensor-Caches zurückgesetzt nach Verbindungstrennung")
        
        # Sicherstellen, dass keine weiteren Updates mehr erfolgen
        self._is_connected = False
    
    @Slot(object)
    def handle_battery(self, msg):
        """Handle battery message"""
        try:
            # Prüfen, ob verbunden
            if not self._is_connected:
                return
                
            voltage = msg.voltage_battery / 1000.0
            current = msg.current_battery / 100.0
            remaining = msg.battery_remaining
            
            # Batterieprozentsatz validieren und korrigieren
            if remaining < 0 or remaining > 100 or remaining > 1000000:
                # Wenn der Wert außerhalb des gültigen Bereichs liegt, verwenden wir einen Standardwert
                self._logger.addLog(f"[WARN] Ungültiger Batteriewert empfangen: {remaining}%")
                remaining = 0  # Standardwert, wenn keine gültige Prozentangabe empfangen wurde
            
            # CPU Last auslesen
            if hasattr(msg, 'load'):
                cpu_load = msg.load / 10.0  # In Prozent
                
                # Debug-Nachricht zur Verfolgung
                self._logger.addLog(f"[DEBUG] System CPU Update: {round(cpu_load, 1)}%")
                
                # Direkt zum QML-Modell senden ohne Ratenbegrenzung zum Testen
                if hasattr(self._sensor_model, 'updateQmlSensor'):
                    self._sensor_model.updateQmlSensor("CPU Last", round(cpu_load, 1), "%")
                    # Formatiere CPU-Last für SensorView 
                    formatted_cpu = f"{round(cpu_load, 1)}%"
                    self._sensor_model.updateQmlSensor("System CPU", formatted_cpu, "")
            
            # Speichere in Python-Modell
            self._sensor_model.update_sensor("battery_voltage", round(voltage, 1))
            self._sensor_model.update_sensor("battery_current", round(current, 1))
            self._sensor_model.update_sensor("battery_remaining", round(remaining, 0))
            
            # Forciere einen gültigen Batterieprozentsatz für die Anzeige
            # Bei negativen oder zu großen Werten verwenden wir 0%
            display_remaining = max(0, min(100, round(remaining, 0)))
            
            # Aktualisiere QML-Modell mit korrigierten Werten
            battery_data = {"voltage": round(voltage, 1), "remaining": display_remaining}
            
            # Debug-Nachricht zur Verfolgung
            self._logger.addLog(f"[DEBUG] Battery % Update: Original={remaining}, Display={display_remaining}%")
            
            # Direkt zum QML-Modell senden ohne Ratenbegrenzung zum Testen
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
    def handle_vfr_hud(self, msg):
        """Handle VFR_HUD message - enthält wichtige Geschwindigkeitsdaten"""
        try:
            # Wichtige Sensorwerte aus VFR_HUD extrahieren
            airspeed = float(getattr(msg, 'airspeed', 0.0))
            groundspeed = float(getattr(msg, 'groundspeed', 0.0))
            heading = float(getattr(msg, 'heading', 0.0))
            throttle = float(getattr(msg, 'throttle', 0.0))
            alt = float(getattr(msg, 'alt', 0.0))
            climb = float(getattr(msg, 'climb', 0.0))
            
            # Speichere in Python-Modell
            self._sensor_model.update_sensor("airspeed", round(airspeed, 1))
            self._sensor_model.update_sensor("groundspeed", round(groundspeed, 1))
            self._sensor_model.update_sensor("heading", round(heading, 1))
            self._sensor_model.update_sensor("throttle", round(throttle, 0))
            if alt > 0:
                self._sensor_model.update_sensor("altitude", round(alt, 1))
            self._sensor_model.update_sensor("climb", round(climb, 1))
            
            # Aktualisiere QML-Modell
            self._update_qml_sensor("Airspeed", round(airspeed, 1), "m/s")
            self._update_qml_sensor("Groundspeed", round(groundspeed, 1), "m/s")
            self._update_qml_sensor("Altitude", round(alt, 1), "m")
            
            self.sensorUpdated.emit("vfr_hud", airspeed)
        except Exception as e:
            error_msg = f"Error bei VFR_HUD: {str(e)}"
            self._logger.addLog(error_msg)
            self.errorOccurred.emit(error_msg)
            
    @Slot(object)
    def handle_servo_output(self, msg):
        """Handle SERVO_OUTPUT_RAW message"""
        try:
            servo_data = {}
            servo_values = []
            # Servo-Werte 1-8 auslesen
            for i in range(1, 9):
                attr_name = f'servo{i}_raw'
                if hasattr(msg, attr_name):
                    value = getattr(msg, attr_name)
                    servo_data[f'S{i}'] = value
                    servo_values.append(f"S{i}={value}")
            
            # Speichere Servo-Daten für spätere Verwendung
            self._servo_output_data = servo_data
            
            # Aktualisiere QML-Modell mit Servo-Daten
            self._update_qml_sensor("Servos", servo_data, "")
            
            # Formatierte Servo-Werte für SensorView - direkt mit dem SensorViewModel kommunizieren
            if servo_values:
                servo_info = ", ".join(servo_values)
                # Debug-Nachricht zur Verfolgung
                self._logger.addLog(f"[DEBUG] System Servos Update: {servo_info}")
                # Aktualisiere direkt im QML-Modell ohne Ratenbegrenzung zum Testen
                if hasattr(self._sensor_model, 'updateQmlSensor'):
                    self._sensor_model.updateQmlSensor("System Servos", servo_info, "")
        except Exception as e:
            error_msg = f"Error handling servo output: {str(e)}"
            self._logger.addLog(error_msg)
            self.errorOccurred.emit(error_msg)
    
    @Slot(object)
    def handle_rc_channels(self, msg):
        """Handle RC_CHANNELS message"""
        try:
            rc_data = {}
            rc_values = []
            # RC-Kanäle 1-8 auslesen
            for i in range(1, 9):
                attr_name = f'chan{i}_raw'
                if hasattr(msg, attr_name):
                    value = getattr(msg, attr_name)
                    rc_data[f'RC{i}'] = value
                    rc_values.append(f"RC{i}={value}")
            
            # Speichere RC-Daten für spätere Verwendung
            self._rc_channels_data = rc_data
            
            # Aktualisiere QML-Modell mit RC-Daten
            self._update_qml_sensor("RC Inputs", rc_data, "")
            
            # Formatierte RC-Werte für SensorView - direkt mit dem SensorViewModel kommunizieren
            if rc_values:
                rc_info = ", ".join(rc_values)
                # Debug-Nachricht zur Verfolgung
                self._logger.addLog(f"[DEBUG] System RC Update: {rc_info}")
                # Aktualisiere direkt im QML-Modell ohne Ratenbegrenzung zum Testen
                if hasattr(self._sensor_model, 'updateQmlSensor'):
                    self._sensor_model.updateQmlSensor("System RC", rc_info, "")
        except Exception as e:
            error_msg = f"Error handling RC channels: {str(e)}"
            self._logger.addLog(error_msg)
            self.errorOccurred.emit(error_msg)
    
    @Slot(object)
    def handle_mission(self, msg):
        """Handle MISSION_CURRENT message"""
        try:
            # Wegpunkt-Nummer aus der Nachricht extrahieren
            if hasattr(msg, 'seq'):
                waypoint = msg.seq
                
                # Formatiere Wegpunkt-Information für SensorView
                mission_info = f"WP#{waypoint}"
                # Debug-Nachricht zur Verfolgung
                self._logger.addLog(f"[DEBUG] System Mission Update: {mission_info}")
                
                # Direkt zum QML-Modell senden ohne Ratenbegrenzung zum Testen
                if hasattr(self._sensor_model, 'updateQmlSensor'):
                    self._sensor_model.updateQmlSensor("System Mission", mission_info, "")
                
                # Speichere auch die Wegpunkt-Nummer als Sensor
                self._sensor_model.update_sensor("mission_waypoint", waypoint)
                
        except Exception as e:
            error_msg = f"Error handling mission: {str(e)}"
            self._logger.addLog(error_msg)
            self.errorOccurred.emit(error_msg)
            
    def _update_qml_sensor(self, name, value, unit):
        """Update a sensor in the QML model using the QML update_sensor function"""
        try:
            # Aktuelle Zeit in Millisekunden
            current_time = int(time.time() * 1000)
            
            # Prüfen, ob es einen Mindestintervall für diesen Sensor gibt
            if name in self._min_update_interval:
                # Prüfen, ob die letzte Aktualisierung weniger als Mindestintervall zurückliegt
                if name in self._last_update_time:
                    time_since_last_update = current_time - self._last_update_time[name]
                    if time_since_last_update < self._min_update_interval[name]:
                        # Nicht aktualisieren, wenn Intervall zu kurz ist
                        return
                
                # Prüfen, ob sich der Wert signifikant geändert hat
                if name in self._last_values:
                    # Bei Textfeldern ist jede Änderung signifikant
                    if isinstance(value, (str, dict)):
                        if self._last_values[name] == value:
                            # Keine Aktualisierung bei gleichem Wert
                            return
                    elif isinstance(value, (int, float)):
                        # Bei numerischen Werten ist nur eine Änderung > 5% signifikant
                        if isinstance(self._last_values[name], (int, float)):
                            if abs(self._last_values[name] - value) / max(1, abs(self._last_values[name])) < 0.05:
                                # Keine Aktualisierung bei kleinen Änderungen
                                return
                
                # Zeit und Wert aktualisieren
                self._last_update_time[name] = current_time
                self._last_values[name] = value
            
            # Sensor im QML-Modell aktualisieren
            if hasattr(self._sensor_model, 'updateQmlSensor'):
                self._sensor_model.updateQmlSensor(name, value, unit)
        except Exception as e:
            self._logger.addLog(f"Error updating QML sensor: {str(e)}")
            
    def initialize_sensors(self):
        """Initialize all required sensors in the model"""
        sensors = [
            ("gps_lat", "GPS Latitude", "°"),
            ("gps_lon", "GPS Longitude", "°"),
            ("altitude", "Altitude", "m"),
            ("roll", "Roll", "°"),
            ("pitch", "Pitch", "°"),
            ("yaw", "Yaw", "°"),
            ("airspeed", "Airspeed", "m/s"),
            ("groundspeed", "Ground Speed", "m/s"),
            ("heading", "Heading", "°"),
            ("climb", "Climb Rate", "m/s"),
            ("throttle", "Throttle", "%"),
            ("battery_voltage", "Battery Voltage", "V"),
            ("battery_current", "Battery Current", "A"),
            ("battery_remaining", "Battery", "%")
        ]
        
        for sensor_id, name, unit in sensors:
            try:
                self._sensor_model.add_sensor(sensor_id, name, unit)
                self._sensor_model.update_sensor(sensor_id, 0.0)
            except Exception as e:
                error_msg = f"❌ Error initializing sensor {name}: {str(e)}"
                self._logger.addLog(error_msg)
                self.errorOccurred.emit(error_msg)