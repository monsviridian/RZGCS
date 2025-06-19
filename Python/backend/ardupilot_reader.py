"""
Ardupilot Reader für MAVLink connections.
Verarbeitet MAVLink-Nachrichten von ArduPilot-Geräten.
"""

import os
from PySide6.QtCore import QObject, Signal, Slot, QTimer
from pymavlink import mavutil
import math

class ArdupilotReader(QObject):
    """
    Verarbeitet und liest MAVLink-Nachrichten von Ardupilot-Geräten.
    
    Signals:
        log_received: Emittiert Lognachrichten
        gps_msg: Emittiert GPS-Daten (lat, lon)
        attitude_msg: Emittiert Lagewinkel (roll, pitch, yaw)
    """
    
    log_received = Signal(str)
    gps_msg = Signal(float, float)
    attitude_msg = Signal(float, float, float)

    def __init__(self, port, baudrate, logger=None, sensor_model=None):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.master = None
        self._logger = logger
        self._sensor_model = sensor_model
        self.timer = None
        self._home_lat = None
        self._home_lon = None

    def connect_to_ardupilot(self):
        try:
            # Korrekte Übergabe von 'baudrate' (nicht 'baud')
            self.master = mavutil.mavlink_connection(self.port, self.baudrate)
            if self._logger:
                self._logger.addLog(f"[INFO] Verbunden mit {self.port}")
            else:
                print(f"[DEBUG] Verbunden mit {self.port}")
            self.log_received.emit(f"Verbunden mit {self.port}")

            # Heartbeat empfangen
            try:
                self.master.wait_heartbeat(timeout=10)
                if self._logger:
                    self._logger.addLog("[INFO] Heartbeat empfangen")
                else:
                    print("[DEBUG] Heartbeat empfangen")
                self.log_received.emit("HEARTBEAT empfangen")
            except Exception as e:
                if self._logger:
                    self._logger.addLog(f"[ERROR] Kein Heartbeat: {e}")
                else:
                    print(f"[ERROR] Kein Heartbeat: {e}")
                self.log_received.emit(f"❌ Kein HEARTBEAT: {e}")
                return False  # Verbindung fehlgeschlagen

            # Datenströme vom Autopilot aktiv anfordern
            self.master.mav.request_data_stream_send(
                self.master.target_system,
                self.master.target_component,
                mavutil.mavlink.MAV_DATA_STREAM_ALL,  # Alle Datenströme
                10,  # Frequenz in Hz
                1    # Aktivieren
            )
            if self._logger:
                self._logger.addLog("[INFO] Datenstream-Anforderung gesendet")
            else:
                print("[DEBUG] Datenstream-Anforderung gesendet")

            # Timer starten
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.read_mavlink_messages)
            self.timer.start(100)  # Alle 100ms abfragen
            if self._logger:
                self._logger.addLog("[INFO] Timer gestartet – Abfrage alle 100 ms")
            else:
                print("[DEBUG] Timer gestartet – Abfrage alle 100 ms")
            
            return True  # Verbindung erfolgreich
            
        except Exception as e:
            if self._logger:
                self._logger.addLog(f"[ERROR] MAVLink Fehler: {e}")
            else:
                print(f"[DEBUG] MAVLink Fehler: {e}")
            self.log_received.emit(f"Fehler beim MAVLink-Setup: {e}")
            return False  # Verbindung fehlgeschlagen

    def read_mavlink_messages(self):
        """Liest MAVLink-Nachrichten und verarbeitet sie entsprechend."""
        try:
            data = {}  # Initialisiere vor der Schleife
            while True:
                msg = self.master.recv_match(blocking=False)
                if not msg:
                    break  # Keine weiteren Nachrichten mehr

                msg_type = msg.get_type()
                msg_content = msg.to_dict()

                if msg_type not in ["HEARTBEAT", "TIMESYNC"]:
                    log_line = f"[{msg_type}] {msg_content}"
                    self.log_received.emit(log_line)

                if msg_type == "RAW_IMU":
                    data.update({
                        "accel_x": msg.xacc,
                        "accel_y": msg.yacc,
                        "accel_z": msg.zacc,
                        "gyro_x": msg.xgyro,
                        "gyro_y": msg.ygyro,
                        "gyro_z": msg.zgyro,
                    })
                    
                    # Wenn SensorModel verfügbar, aktualisiere die Werte
                    if self._sensor_model:
                        self._sensor_model.update_sensor_value('Accel X', msg.xacc)
                        self._sensor_model.update_sensor_value('Accel Y', msg.yacc)
                        self._sensor_model.update_sensor_value('Accel Z', msg.zacc)
                        self._sensor_model.update_sensor_value('Gyro X', msg.xgyro)
                        self._sensor_model.update_sensor_value('Gyro Y', msg.ygyro)
                        self._sensor_model.update_sensor_value('Gyro Z', msg.zgyro)

                elif msg_type == "ATTITUDE":
                    roll = math.degrees(msg.roll)
                    pitch = math.degrees(msg.pitch)
                    yaw = math.degrees(msg.yaw)
                    data.update({
                        "roll": roll,
                        "pitch": pitch,
                        "yaw": yaw,
                    })
                    
                    # Signale für UI-Updates senden
                    self.attitude_msg.emit(roll, pitch, yaw)
                    
                    # Wenn SensorModel verfügbar, aktualisiere die Werte
                    if self._sensor_model:
                        self._sensor_model.update_sensor_value('Roll', roll)
                        self._sensor_model.update_sensor_value('Pitch', pitch)
                        self._sensor_model.update_sensor_value('Yaw', yaw)

                elif msg_type == "GLOBAL_POSITION_INT":
                    lat = msg.lat / 1e7
                    lon = msg.lon / 1e7
                    alt = msg.relative_alt / 1000.0
                    data.update({"lat": lat, "lon": lon, "alt": alt})
                    
                    # Signale für UI-Updates senden
                    self.gps_msg.emit(lat, lon)
                    
                    # Wenn SensorModel verfügbar, aktualisiere die Werte
                    if self._sensor_model:
                        self._sensor_model.update_sensor_value('GPS Lat', lat)
                        self._sensor_model.update_sensor_value('GPS Lon', lon)
                        self._sensor_model.update_sensor_value('Altitude', alt)
                        
                    # Home-Position beim ersten GPS-Fix setzen
                    if self._home_lat is None or self._home_lon is None:
                        self._home_lat = lat
                        self._home_lon = lon
                        if self._logger:
                            self._logger.addLog(f"[INFO] Home Position gesetzt: {lat}, {lon}")
                    
                    # Distanz zur Home-Position berechnen
                    if self._home_lat is not None and self._home_lon is not None and self._sensor_model:
                        # Haversine-Formel zur Distanzberechnung
                        R = 6371000  # Erdradius in Metern
                        lat1_rad = math.radians(self._home_lat)
                        lat2_rad = math.radians(lat)
                        delta_lat = math.radians(lat - self._home_lat)
                        delta_lon = math.radians(lon - self._home_lon)
                        
                        a = (math.sin(delta_lat/2) * math.sin(delta_lat/2) + 
                             math.cos(lat1_rad) * math.cos(lat2_rad) * 
                             math.sin(delta_lon/2) * math.sin(delta_lon/2))
                        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
                        distance = R * c
                        
                        self._sensor_model.update_sensor_value('Home Distance', f"{distance:.1f}m")
                        self._sensor_model.update_sensor_value('Distance', f"{distance:.1f}m")
                
                elif msg_type == "VFR_HUD":
                    if self._logger:
                        self._logger.addLog(f"[VFR] Altitude: {msg.alt}m, Climb: {msg.climb}m/s")
                    
                    # Wenn SensorModel verfügbar, aktualisiere die Werte
                    if self._sensor_model:
                        self._sensor_model.update_sensor_value('Ground Speed', msg.groundspeed)
                        self._sensor_model.update_sensor_value('Airspeed', msg.airspeed)
                        self._sensor_model.update_sensor_value('Climb Rate', msg.climb)
                        self._sensor_model.update_sensor_value('Throttle', msg.throttle)
                        self._sensor_model.update_sensor_value('Heading', msg.heading)
                        
                elif msg_type == "SYS_STATUS":
                    voltage = msg.voltage_battery / 1000.0  # Umrechnung in Volt
                    current = msg.current_battery / 100.0   # Umrechnung in Ampere
                    remaining = msg.battery_remaining       # Prozentwert
                    
                    if self._logger:
                        self._logger.addLog(f"[BAT] Spannung: {voltage:.1f}V")
                    
                    # Wenn SensorModel verfügbar, aktualisiere die Werte
                    if self._sensor_model:
                        self._sensor_model.update_sensor_value('Battery', f"{voltage:.1f}V")
                        self._sensor_model.update_sensor_value('Current', f"{current:.1f}A")
                        self._sensor_model.update_sensor_value('Battery %', f"{remaining}%")
                
                elif msg_type == "HEARTBEAT":
                    armed = (msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED) != 0
                    mode = mavutil.mode_string_v10(msg)
                    self.log_received.emit(f"[HEARTBEAT] MODE: {mode}, ARMED: {armed}")
                    
                    # Flugmodus und Bewaffnungsstatus ins SensorModel eintragen
                    if self._sensor_model:
                        self._sensor_model.update_sensor_value('Flight Mode', mode)
                        self._sensor_model.update_sensor_value('Armed', "YES" if armed else "NO")

                elif msg_type == "STATUSTEXT":
                    status_msg = msg.text.decode('utf-8') if isinstance(msg.text, bytes) else str(msg.text)
                    self.log_received.emit(f"[LOG {msg.severity}] {status_msg}")
                    if self._logger:
                        self._logger.addLog(f"[FC] {status_msg}")

            if data:
                if self._logger and self._logger.isDebugMode():
                    print(data)  # Nur im Debug-Modus ausgeben
                    
        except Exception as e:
            self.log_received.emit(f"Fehler beim Abrufen der MAVLink-Nachricht: {e}")
            if self._logger:
                self._logger.addLog(f"[ERROR] MAVLink-Nachrichtenverarbeitung: {e}")
            else:
                print(f"[ERROR] MAVLink-Nachrichtenverarbeitung: {e}")

    def stop(self):
        """Stoppt den Timer und schließt die MAVLink-Verbindung."""
        if self.timer:
            self.timer.stop()
        
        if self.master:
            try:
                self.master.close()
                if self._logger:
                    self._logger.addLog("[INFO] MAVLink-Verbindung geschlossen")
            except Exception as e:
                if self._logger:
                    self._logger.addLog(f"[ERROR] Fehler beim Schließen der MAVLink-Verbindung: {e}")
