from PySide6.QtCore import QObject, Signal, Slot
from .sensorviewmodel import SensorViewModel
from .logger import Logger

class SensorManager(QObject):
    """Manages sensor data and updates"""
    
    # Signals
    sensorUpdated = Signal(str, float)  # Emits sensor name and value
    errorOccurred = Signal(str)  # Emits error message
    
    def __init__(self, sensor_model: SensorViewModel, logger: Logger):
        super().__init__()
        self._sensor_model = sensor_model
        self._logger = logger
        
    @Slot(object)
    def handle_attitude(self, msg):
        """Handle attitude message"""
        try:
            self._sensor_model.update_sensor("roll", round(msg.roll, 2))
            self._sensor_model.update_sensor("pitch", round(msg.pitch, 2))
            self._sensor_model.update_sensor("yaw", round(msg.yaw, 2))
            self.sensorUpdated.emit("attitude", msg.roll)
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
            
            self._sensor_model.update_sensor("gps_lat", round(lat, 6))
            self._sensor_model.update_sensor("gps_lon", round(lon, 6))
            self._sensor_model.update_sensor("altitude", round(alt, 1))
            
            # Calculate ground speed
            vx = msg.vx / 100.0
            vy = msg.vy / 100.0
            ground_speed = (vx*vx + vy*vy)**0.5
            self._sensor_model.update_sensor("groundspeed", round(ground_speed, 1))
            
            self.sensorUpdated.emit("gps", lat)
        except Exception as e:
            error_msg = f"❌ Error handling GPS: {str(e)}"
            self._logger.addLog(error_msg)
            self.errorOccurred.emit(error_msg)
            
    @Slot(object)
    def handle_battery(self, msg):
        """Handle battery message"""
        try:
            voltage = msg.voltage_battery / 1000.0
            current = msg.current_battery / 100.0
            remaining = msg.battery_remaining
            
            self._sensor_model.update_sensor("battery_voltage", round(voltage, 1))
            self._sensor_model.update_sensor("battery_current", round(current, 1))
            self._sensor_model.update_sensor("battery_remaining", round(remaining, 1))
            
            self._logger.addLog(f"📊 Batterie: {voltage:.1f}V, {current:.1f}A, {remaining}%")
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
            
            # Sensorwerte aktualisieren
            self._sensor_model.update_sensor("airspeed", round(airspeed, 1))
            self._sensor_model.update_sensor("groundspeed", round(groundspeed, 1))
            self._sensor_model.update_sensor("heading", round(heading, 1))
            # Throttle als Prozent
            self._sensor_model.update_sensor("throttle", round(throttle, 0))
            # Alternativ Höhe, falls GPS nicht verfügbar
            if alt > 0:
                self._sensor_model.update_sensor("altitude", round(alt, 1))
            # Steigrate hinzufügen
            self._sensor_model.update_sensor("climb", round(climb, 1))
            
            self._logger.addLog(f"📊 VFR_HUD: Air={airspeed:.1f}m/s, Ground={groundspeed:.1f}m/s, Alt={alt:.1f}m")
            self.sensorUpdated.emit("vfr_hud", airspeed)
        except Exception as e:
            error_msg = f"Error bei VFR_HUD: {str(e)}"
            self._logger.addLog(error_msg)
            self.errorOccurred.emit(error_msg)
            
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
            ("climb", "Climb Rate", "m/s"),
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