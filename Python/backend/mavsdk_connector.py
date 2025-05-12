import asyncio
from PySide6.QtCore import QObject, Signal, Slot, QThread
from mavsdk import System
import mavlink
import unittest.mock
from datetime import datetime


from .sensorviewmodel import SensorViewModel
from .logger import Logger

class MAVSDKConnector(QObject):
    connected_changed = Signal(bool)  # Signal für den Verbindungsstatus
    telemetry_updated = Signal(float, float, float)  # latitude, longitude, altitude
    gps_status_changed = Signal(bool)  # Signal für GPS-Status
    calibration_status_changed = Signal(bool)  # Signal für Kalibrierungsstatus
    status_message_received = Signal(str)

    def __init__(self, logger: Logger, sensor: SensorViewModel ):
        super().__init__()
       
        self.drone = System(mavsdk_server_address="localhost", port=50051)
        self._event_loop = asyncio.new_event_loop()
        self._thread = QThread()
        self.moveToThread(self._thread)
        self._thread.started.connect(self._start_event_loop)
        self._thread.finished.connect(self._event_loop.stop)
        self._thread.start()
        self.logger = logger
        self.sensor = sensor
        self.gps_available = False
        self.calibration_needed = False
        

    @Slot()
    def _start_event_loop(self):
        asyncio.set_event_loop(self._event_loop)
        self._event_loop.run_forever()

    @Slot(str, int)
    def connect_mav(self, port: str, baudrate: int):
        print("calin connect mav")
        url = f"serial://{port}:{baudrate}"
        asyncio.run_coroutine_threadsafe(self._do_connect(url), self._event_loop)

    async def _do_connect(self, url: str):
        try:
            # Verbindung zum Autopilot herstellen
            print("do_connect")
            await self.drone.connect(system_address=url)
            async for state in self.drone.core.connection_state():
                if state.is_connected:
                    self.connected_changed.emit(True)
                    print("Erfolgriche verbinund")
                    self.logger.add_log("Verbindung zum Autopiloten erfolgreich")
                    asyncio.create_task(self._observe_telemetry())
                    asyncio.create_task(self._observe_status_text())
                    asyncio.create_task(self._observe_calibration())


                    break
                else:
                    self.connected_changed.emit(False)
                    self.logger.add_log("Verbindung zum Autopiloten fehlgeschlagen")
                    print("fehler")
        except Exception as e:
            self.connected_changed.emit(False)
            self.logger.add_log(f"Fehler beim Verbinden: {str(e)}")

    async def _observe_telemetry(self):
        
        async for pos in self.drone.telemetry.position():
            
            print("observe telemetri")
            latitude = pos.latitude_deg
            longitude = pos.longitude_deg
            altitude = pos.relative_altitude_m
            print("telemetri")
            print(pos)
            self.telemetry_updated.emit(latitude, longitude, altitude)
            


            # GPS-Daten prüfen
            if latitude == 0.0 and longitude == 0.0:
                if not self.gps_available:
                    self.gps_available = True
                    
                    self.gps_status_changed.emit(False)  # GPS fehlt
                    self.logger.add_log("GPS-Daten nicht verfügbar")
            else:
                if self.gps_available:
                    self.gps_available = False
                    
                    self.gps_status_changed.emit(True)  # GPS verfügbar

            # Kalibrierung prüfen (z.B. Herzschlagnachricht oder Sensorstatus)
            calibration_status = await self._check_calibration()
            print("calibration sattion")
            print(calibration_status)
            if calibration_status == "not_calibrated" and not self.calibration_needed:
                self.calibration_needed = True
                self.calibration_status_changed.emit(True)  # Kalibrierung erforderlich
                self.logger.add_log("Kalibrierung erforderlich")
            elif calibration_status == "calibrated" and self.calibration_needed:
                self.calibration_needed = False
                self.calibration_status_changed.emit(False)  # Kalibrierung abgeschlossen
                self.logger.add_log("Kalibrierung abgeschlossen")

    async def _check_calibration(self):
        print("check cal")
        async for health in self.drone.telemetry.health():
            print("health")
            print(health)
            if (not health.is_accelerometer_calibration_ok or
                not health.is_magnetometer_calibration_ok or
                not health.is_gyrometer_calibration_ok):
                return "not_calibrated"
            else:
                return "calibrated"

    async def _observe_calibration(self):
        print("observe")
        async for health in self.drone.telemetry.health():
            if (not health.is_accelerometer_calibration_ok or
                not health.is_magnetometer_calibration_ok or
                not health.is_gyrometer_calibration_ok):
                if not self.calibration_needed:
                    self.calibration_needed = True
                    self.calibration_status_changed.emit(True)
                    self.logger.add_log("Kalibrierung erforderlich")
            else:
                if self.calibration_needed:
                    self.calibration_needed = False
                    self.calibration_status_changed.emit(False)
                    self.logger.add_log("Kalibrierung abgeschlossen")
            await asyncio.sleep(2)  # alle 2 Sekunden prüfen

    async def _observe_status_text(self):
        async for status in self.drone.telemetry.status_text():
            timestamp = datetime.now().strftime("%H:%M:%S")
            msg_type = status.type.name  # z.B. 'CRITICAL'
            text = status.text.strip()
            formatted_log = f"[{timestamp}|MAVLink] {msg_type}: {text}"
            print(formatted_log)
            self.logger.add_log(formatted_log)
            self.status_message_received.emit(formatted_log)    
    

    @Slot()
    def disarm(self):
        asyncio.run_coroutine_threadsafe(self.drone.action.disarm(), self._event_loop)

    def cleanup(self):
        self._event_loop.call_soon_threadsafe(self._event_loop.stop)
        self._thread.quit()
        self._thread.wait()
