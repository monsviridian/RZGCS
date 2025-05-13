import asyncio
import threading
from PySide6.QtCore import QObject, Signal, Slot, QThread
from mavsdk import System
from datetime import datetime

from .sensorviewmodel import SensorViewModel
from .logger import Logger
from pymavlink import mavutil


class MAVSDKConnector(QObject):
    connected_changed = Signal(bool)
    telemetry_updated = Signal(float, float, float)  # latitude, longitude, altitude
    gps_status_changed = Signal(bool)
    calibration_status_changed = Signal(bool)
    status_message_received = Signal(str)

    def __init__(self, logger: Logger, sensor: SensorViewModel):
        super().__init__()
        self.logger = logger
        self.sensor = sensor

        # MAVSDK-Instanz
        self.drone = System(mavsdk_server_address="localhost", port=50051)

        # Event-Loop und Thread für asynchrone Operationen
        self._event_loop = asyncio.new_event_loop()
        self._thread = QThread()
        self.moveToThread(self._thread)
        self._thread.started.connect(self._start_event_loop)
        self._thread.finished.connect(self._event_loop.stop)
        self._thread.start()

        # Statusvariablen
        self.gps_available = False
        self.calibration_needed = False

    @Slot()
    def _start_event_loop(self):
        asyncio.set_event_loop(self._event_loop)
        self._event_loop.run_forever()

    @Slot(str, int)
    def connect_mav(self, port: str, baudrate: int):
        url = f"serial://{port}:{baudrate}"
        asyncio.run_coroutine_threadsafe(self._do_connect(url), self._event_loop)

    async def _do_connect(self, url: str):
        try:
            await self.drone.connect(system_address=url)

            # Verbindung erfolgreich, starte Sensorbeobachtungen
            async for state in self.drone.core.connection_state():
                if state.is_connected:
                    self.connected_changed.emit(True)
                    self.logger.add_log("Verbindung zum Autopiloten erfolgreich")

                    # Starte Telemetrie- und Statusbeobachtungen
                    asyncio.create_task(self._observe_telemetry())
                    asyncio.create_task(self._observe_status_text())
                    asyncio.create_task(self._observe_calibration())
                    asyncio.create_task(self._observe_speed())
                    asyncio.create_task(self._observe_imu())
                    asyncio.create_task(self._observe_gps_info())
                    self._start_mavlink_thread()



                    break
                else:
                    self.connected_changed.emit(False)
                    self.logger.add_log("Verbindung zum Autopiloten fehlgeschlagen")

        except Exception as e:
            self.connected_changed.emit(False)
            self.logger.add_log(f"Fehler beim Verbinden: {str(e)}")

    async def _observe_telemetry(self):
        self.logger.add_log("Starte Telemetrie-Beobachtung")

        try:
            async for pos in self.drone.telemetry.position():
                print("posiioz")
                print(pos)
                latitude = pos.latitude_deg
                longitude = pos.longitude_deg
                altitude = pos.relative_altitude_m

                self.logger.add_log("Position empfangen", str(pos))
                print(f"GPS: lat={latitude}, lon={longitude}, alt={altitude}")

                self.telemetry_updated.emit(latitude, longitude, altitude)
                self.sensor.update_sensor("GPS", 1.0 if latitude and longitude else 0.0)

                await asyncio.sleep(1)  # Verhindert Überlastung
        except Exception as e:
            self.logger.add_log("Fehler in _observe_telemetry", str(e))
            print(f"Fehler in _observe_telemetry: {e}")
            
    def _start_mavlink_thread(self):
        def _listen():
            mav = mavutil.mavlink_connection("udp:127.0.0.1:14540")
            while True:
                msg = mav.recv_match(blocking=True)
                if msg:
                    self.logger.add_log("[MAVLINK]", f"{msg.get_type()}: {msg.to_dict()}")

        thread = threading.Thread(target=_listen, daemon=True)
        thread.start()

    async def _observe_gps_info(self):
        self.logger.add_log("Starte _observe_gps_info()")
        try:
            async for gps_info in self.drone.telemetry.raw_gps():
                num_satellites = gps_info.num_satellites
                fix_type = gps_info.fix_type.name  # Enum: NO_GPS, NO_FIX, FIX_2D, FIX_3D, etc.

                self.logger.add_log(f"GPS Satelliten: {num_satellites}, Fix-Typ: {fix_type}")
                gps_ok = gps_info.fix_type.value >= 3  # FIX_3D oder besser

                self.sensor.update_sensor("GPS_Satellites", num_satellites)
                self.sensor.update_sensor("GPS_Fix", gps_info.fix_type.value)
                self.gps_status_changed.emit(gps_ok)

                await asyncio.sleep(2)
        except Exception as e:
            self.logger.add_log("Fehler in _observe_gps_info()", str(e))

    async def _observe_speed(self):
        self.logger.add_log("Starte _observe_speed()")
        async for velocity in self.drone.telemetry.velocity_ned():
            speed = (velocity.north_m_s**2 + velocity.east_m_s**2 + velocity.down_m_s**2)**0.5
            self.logger.add_log("Velocity empfangen", str(velocity))

            self.logger.add_log("speed", str(speed))
            self.sensor.update_sensor("Speed", speed)

    async def _observe_calibration(self):
        self.logger.add_log("Starte _observe_calibration() (DEBUG-MODUS – Kalibrierung ignoriert)")
        self.calibration_needed = False
        self.calibration_status_changed.emit(False)
        
        # Nur ein einziges Mal ausführen, nicht endlos prüfen
        return


    async def _observe_status_text(self):
        self.logger.add_log("Starte _observe_status()")
        async for status in self.drone.telemetry.status_text():
            self.logger.add_log("Flug Status abfrage")
            timestamp = datetime.now().strftime("%H:%M:%S")
            msg_type = status.type.name
            text = status.text.strip()
            formatted_log = f"[{timestamp}|MAVLink] {msg_type}: {text}"
            self.logger.add_log(formatted_log)
            self.status_message_received.emit(formatted_log)

    async def _observe_imu(self):
        self.logger.add_log("Starte _observe_imu()")
        try:
            async for imu in self.drone.telemetry.imu():
                self.logger.add_log("IMU empfangen", str(imu))
                self.sensor.update_sensor("Gyro_X", imu.angular_velocity_fr_body.x_rad_s)
        except Exception as e:
            self.logger.add_log("Fehler in _observe_imu()", str(e))

    @Slot()
    def disarm(self):
        asyncio.run_coroutine_threadsafe(self.drone.action.disarm(), self._event_loop)

    def cleanup(self):
        self._event_loop.call_soon_threadsafe(self._event_loop.stop)
        self._thread.quit()
        self._thread.wait()
