# backend/serial_connector.py

import sys
import os
from PySide6.QtCore import QObject, Signal, Slot
import serial.tools.list_ports
import math

from backend.mavlink_connector import MAVLinkConnector
from .sensorviewmodel import SensorViewModel
from backend.logger import Logger

os.environ["QT_QUICK_CONTROLS_STYLE"] = "Fusion"

class SerialConnector(QObject):
    """
    Manages the serial connection to the drone and coordinates sensor data transmission.
    
    Signals:
        available_ports_changed: Emitted when available ports change
        connection_successful: Emitted on successful connection
        gps_msg: Emits GPS data
        attitude_msg: Emits attitude data
    """
    
    available_ports_changed = Signal(list)
    connection_successful = Signal()
    gps_msg = Signal(float, float)
    attitude_msg = Signal(float, float, float)

    def __init__(self, sensor_model: SensorViewModel, logger: Logger):
        """
        Initialize the SerialConnector.
        
        Args:
            sensor_model: Model for sensor data
            logger: Logger for status messages
        """
        super().__init__()
        self.sensor_model = sensor_model
        self.logger = logger
        self.ardupilot_reader = None
        
        # Initialize all required sensors
        self._initialize_sensors()
        
    def _initialize_sensors(self):
        """Initialize all required sensors in the model."""
        sensors = [
            ("gps", "GPS", ""),  # Add GPS sensor first
            ("altitude", "Altitude", "m"),
            ("climb", "Climb Rate", "m/s"),
            ("battery_voltage", "Battery Voltage", "V"),
            ("battery_current", "Battery Current", "A"),
            ("battery_remaining", "Battery", "%"),
            ("airspeed", "Airspeed", "m/s"),
            ("groundspeed", "Ground Speed", "m/s"),
            ("heading", "Heading", "°"),
            ("throttle", "Throttle", "%")
        ]
        
        for sensor_id, name, unit in sensors:
            try:
                self.sensor_model.add_sensor(sensor_id, name, unit)
            except Exception as e:
                self.add_log(f"⚠️ Error initializing sensor {name}: {str(e)}")

    @Slot(str)
    def add_log(self, message):
        print(f"[SerialConnector] {message}")
        self.logger.info(message)

    @Slot()
    def load_ports(self):
        try:
            ports = serial.tools.list_ports.comports()
            port_names = [port.device for port in ports]
            print("port")
            print(port_names)
            if not port_names:
                self.add_log("❌ No serial ports found")
            self.available_ports_changed.emit(port_names)
        except Exception as e:
            self.add_log(f"❌ Error loading ports: {e}")

    @Slot(str, int, str)
    def connect_to_serial(self, port_name, baudrate, autopilot):
        try:
            if autopilot == "ArduPilot":
                self.ardupilot_reader = MAVLinkConnector(port_name, baudrate)
                self.ardupilot_reader.log_received.connect(self.add_log)
                self.ardupilot_reader.gps_msg.connect(self.gps_msg.emit)
                self.ardupilot_reader.gps_msg.connect(self.update_gps)  # Connect GPS updates
                self.ardupilot_reader.attitude_msg.connect(self.attitude_msg.emit)
                self.ardupilot_reader.sensor_data.connect(self.update_sensor_data)
                
                # Establish connection
                if self.ardupilot_reader.connect_to_drone():
                    self.add_log(f"🔌 Connected to {port_name} @ {baudrate} ({autopilot})")
                    self.connection_successful.emit()
                else:
                    self.add_log("❌ Connection failed")
                    if self.ardupilot_reader:
                        self.ardupilot_reader.stop()
                        self.ardupilot_reader = None
        except Exception as e:
            self.add_log(f"❌ Connection error: {e}")
            if self.ardupilot_reader:
                self.ardupilot_reader.stop()
                self.ardupilot_reader = None

    @Slot(str, float)
    def update_sensor_data(self, name, value):
        try:
            self.sensor_model.update_sensor(name, value)
            
            # Add detailed logging for important sensor updates
            if name == "altitude":
                self.add_log(f"📊 Altitude: {value:.2f}m")
            elif name == "battery_remaining":
                if value < 20:
                    self.add_log(f"⚠️ Low battery: {value:.1f}%")
                else:
                    self.add_log(f"🔋 Battery: {value:.1f}%")
            elif name == "heading":
                self.add_log(f"🧭 Heading: {value:.1f}°")
            elif name == "groundspeed":
                self.add_log(f"🚀 Ground speed: {value:.1f}m/s")
            elif name == "climb":
                if abs(value) > 0.5:  # Only log significant climb/descent
                    self.add_log(f"📈 Climb rate: {value:.1f}m/s")
        except Exception as e:
            self.add_log(f"⚠️ Error updating sensor {name}: {str(e)}")
        
    @Slot()
    def disconnect(self):
        if self.ardupilot_reader:
            self.ardupilot_reader.stop()
            self.add_log("🛑 Connection terminated.")
            self.ardupilot_reader = None
        else:
            self.add_log("❌ No active connection to terminate.")

    def stop(self):
        if self.ardupilot_reader:
            self.ardupilot_reader.stop()
            self.add_log("🛑 Connection terminated.")

    @Slot(float, float)
    def update_gps(self, lat: float, lon: float):
        """Update GPS coordinates in the sensor model."""
        try:
            self.sensor_model.update_gps(lat, lon)
        except Exception as e:
            self.add_log(f"⚠️ Error updating GPS coordinates: {str(e)}")

    def _log_info(self, message: str) -> None:
        """Loggt eine Informationsnachricht."""
        print(f"[MAVLinkConnector] {message}")
        self.log_received.emit(message)
        
    def _log_error(self, message: str) -> None:
        """Loggt eine Fehlernachricht."""
        print(f"[MAVLinkConnector] ❌ {message}")
        self.log_received.emit(f"❌ {message}")

    def _handle_global_position_int(self, msg):
        """Handle GLOBAL_POSITION_INT message."""
        try:
            lat = msg.lat / 1e7
            lon = msg.lon / 1e7
            alt = msg.alt / 1000.0  # Convert to meters
            relative_alt = msg.relative_alt / 1000.0  # Convert to meters
            vx = msg.vx / 100.0  # Convert to m/s
            vy = msg.vy / 100.0  # Convert to m/s
            vz = msg.vz / 100.0  # Convert to m/s
            
            # Calculate ground speed
            ground_speed = math.sqrt(vx*vx + vy*vy)
            
            # Update sensor data
            self.sensor_data.emit("altitude", relative_alt)
            self.sensor_data.emit("groundspeed", ground_speed)
            
            # Log GPS status based on altitude and speed
            if alt == 0 and relative_alt == 0:
                self._log_error("No GPS fix")
            elif ground_speed < 0.1:
                self._log_info("GPS fix (stationary)")
            else:
                self._log_info(f"GPS fix (moving: {ground_speed:.1f}m/s)")
            
            # Always emit GPS data for updates
            self.gps_msg.emit(lat, lon)
            
            # Log position changes with more detail
            if hasattr(self, '_last_lat') and hasattr(self, '_last_lon'):
                lat_change = abs(lat - self._last_lat)
                lon_change = abs(lon - self._last_lon)
                if lat_change > 0.00001 or lon_change > 0.00001:  # More sensitive to changes
                    self._log_info(
                        f"GPS: {lat:.6f}, {lon:.6f}\n"
                        f"   Alt: {relative_alt:.1f}m\n"
                        f"   Speed: {ground_speed:.1f}m/s"
                    )
            
            # Store last position
            self._last_lat = lat
            self._last_lon = lon
            
        except Exception as e:
            self._log_error(f"Error processing GPS data: {str(e)}")
