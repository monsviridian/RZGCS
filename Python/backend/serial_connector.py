# backend/serial_connector.py

import sys
import os
from PySide6.QtCore import QObject, Signal, Slot
import serial.tools.list_ports

from backend.mavlink_connector import MAVLinkConnector
from .sensorviewmodel import SensorViewModel

os.environ["QT_QUICK_CONTROLS_STYLE"] = "Fusion"
# backend/serial_connector.py



from backend.logger import Logger  # ⬅️ Logger importieren

class SerialConnector(QObject):
    available_ports_changed = Signal(list)
    connection_successful = Signal()
    gps_msg = Signal(float, float)
    attitude_msg = Signal(float, float, float)

    def __init__(self, sensor_model: SensorViewModel, logger: Logger):
        super().__init__()
        self.sensor_model = sensor_model
        self.logger = logger  # ⬅️ Logger speichern
        self.ardupilot_reader = None

    @Slot(str)
    def add_log(self, message):
        print(f"[SerialConnector] {message}")
        self.logger.add_log(message)  # ⬅️ direkt an Logger schicken

    @Slot()
    def load_ports(self):
        try:
            ports = serial.tools.list_ports.comports()
            port_names = [port.device for port in ports]
            print("port")
            print(port_names)
            if not port_names:
                self.add_log("❌ Keine seriellen Ports gefunden")
            self.available_ports_changed.emit(port_names)
        except Exception as e:
            self.add_log(f"❌ Fehler beim Laden der Ports: {e}")

    @Slot(str, int, str)
    def connect_to_serial(self, port_name, baudrate, autopilot):
        port_name = "COM8"
        try:
            if autopilot == "ArduPilot":
                self.ardupilot_reader = MAVLinkConnector(port_name, baudrate)
                self.ardupilot_reader.log_received.connect(self.add_log)
                self.ardupilot_reader.gps_msg.connect(self.gps_msg.emit)
                self.ardupilot_reader.attitude_msg.connect(self.attitude_msg.emit)
                self.ardupilot_reader.sensor_data.connect(self.update_sensor_data)
                self.ardupilot_reader.connect_to_ardupilot()
                self.add_log(f"🔌 Verbunden mit {port_name} @ {baudrate} ({autopilot})")

            self.connection_successful.emit()
        except Exception as e:
            self.add_log(f"❌ Verbindungsfehler: {e}")

    @Slot(str, float)
    def update_sensor_data(self, name, value):
        self.sensor_model.update_sensor(name, value)
        
    @Slot()
    def disconnect(self):
        if self.ardupilot_reader:
            self.ardupilot_reader.stop()  # Verbindungsstop
            self.add_log("🛑 Verbindung getrennt.")  # Loggen, dass die Verbindung getrennt wurde
            self.ardupilot_reader = None  # Setze den Reader auf None
        else:
            self.add_log("❌ Keine aktive Verbindung zum Trennen.")  # Falls keine Verbindung besteht

    def stop(self):
        if self.ardupilot_reader:
            self.ardupilot_reader.stop()
            self.add_log("🛑 Verbindung getrennt.")
