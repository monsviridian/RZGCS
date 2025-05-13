# backend/mavlink_connector.py

import threading
from PySide6.QtCore import QObject, Signal
from pymavlink import mavutil

class MAVLinkConnector(QObject):
    log_received = Signal(str)
    gps_msg = Signal(float, float)
    attitude_msg = Signal(float, float, float)
    sensor_data = Signal(str, float)  # NEU

    def __init__(self, port, baudrate):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.master = None
        self.running = False
        self.thread = None

    def connect_to_ardupilot(self):
        try:
            self.master = mavutil.mavlink_connection(self.port, baud=self.baudrate)
            self.log_received.emit(f"✅ Verbunden mit {self.port} @ {self.baudrate}")
            self.running = True
            self.thread = threading.Thread(target=self.read_loop, daemon=True)
            self.thread.start()
        except Exception as e:
            self.log_received.emit(f"❌ Fehler beim Verbinden: {str(e)}")

    def read_loop(self):
        while self.running:
            try:
                msg = self.master.recv_match(blocking=True, timeout=1)
                if msg:
                    self.process_message(msg)
            except Exception as e:
                self.log_received.emit(f"⚠️ MAVLink Fehler: {str(e)}")

    def process_message(self, msg):
        msg_type = msg.get_type()
        if msg_type == "GLOBAL_POSITION_INT":
            lat = msg.lat / 1e7
            lon = msg.lon / 1e7
            self.gps_msg.emit(lat, lon)
            self.sensor_data.emit("GPS", lat)  # Beispiel: lat als Sensorwert
            self.log_received.emit(f"📡 GPS: {lat:.5f}, {lon:.5f}")
        elif msg_type == "ATTITUDE":
            roll = msg.roll
            pitch = msg.pitch
            yaw = msg.yaw
            self.attitude_msg.emit(roll, pitch, yaw)
            self.sensor_data.emit("Roll", roll)
            self.sensor_data.emit("Pitch", pitch)
            self.sensor_data.emit("Yaw", yaw)
            self.log_received.emit(f"🎯 Attitude: Roll={roll:.2f}, Pitch={pitch:.2f}, Yaw={yaw:.2f}")

    def stop(self):
        self.running = False
        if self.master:
            self.master.close()
            self.log_received.emit("🛑 Verbindung getrennt.")
