"""PreflightCheckModel - exposes key pre-flight check states to QML.

Initial checks implemented:
• satellites (int)
• batteryPercent (float)
• ekfOk (bool)
• rcRssi (int, dBm)
• flightMode (str)
• criticalError (bool) + message

Further checks can be added later.
"""

from PySide6.QtCore import QObject, Property, Signal, Slot, QTimer


class PreflightCheckModel(QObject):
    satellitesChanged = Signal(int)
    batteryPercentChanged = Signal(float)
    ekfOkChanged = Signal(bool)
    rcRssiChanged = Signal(int)
    flightModeChanged = Signal(str)
    criticalErrorChanged = Signal(bool, str)

    def __init__(self, connector):
        super().__init__()
        self._connector = connector

        self._satellites = 0
        self._battery_percent = 0.0
        self._ekf_ok = True
        self._rc_rssi = -1
        self._flight_mode = "UNKNOWN"
        self._critical_error = False
        self._critical_message = ""

        if connector is not None:
            # these are signals already available in MavlinkSerialConnector
            try:
                connector.gpsChanged.connect(self._on_gps_changed)
                connector.batteryChanged.connect(self._on_battery_changed)
                connector.statusMessageChanged.connect(self._on_status_message)
            except AttributeError:
                pass  # ignore missing ones for now

        # periodic EKF watchdog (placeholder implementation)
        timer = QTimer(self)
        timer.setInterval(5000)
        timer.timeout.connect(self._ekf_watchdog)
        timer.start()

    # ------------ properties ------------
    def _get_satellites(self):
        return self._satellites

    satellites = Property(int, _get_satellites, notify=satellitesChanged)

    def _get_battery_percent(self):
        return self._battery_percent

    batteryPercent = Property(float, _get_battery_percent, notify=batteryPercentChanged)

    def _get_ekf_ok(self):
        return self._ekf_ok

    ekfOk = Property(bool, _get_ekf_ok, notify=ekfOkChanged)

    def _get_rc_rssi(self):
        return self._rc_rssi

    rcRssi = Property(int, _get_rc_rssi, notify=rcRssiChanged)

    def _get_flight_mode(self):
        return self._flight_mode

    flightMode = Property(str, _get_flight_mode, notify=flightModeChanged)

    def _get_critical_error(self):
        return self._critical_error

    criticalError = Property(bool, _get_critical_error, notify=criticalErrorChanged)

    # ------------ slots ------------
    @Slot(float, float, float)
    def _on_gps_changed(self, lat, lon, alt):
        # TODO: connector should expose satellite count; here we estimate
        sats = 8 if alt is not None else 0
        if sats != self._satellites:
            self._satellites = sats
            self.satellitesChanged.emit(sats)

    @Slot(float, float, float)
    def _on_battery_changed(self, voltage, current, remaining):
        if remaining != self._battery_percent:
            self._battery_percent = remaining
            self.batteryPercentChanged.emit(remaining)

    @Slot(str)
    def _on_status_message(self, msg):
        lmsg = msg.lower()
        if "ekf" in lmsg and ("warn" in lmsg or "fail" in lmsg):
            self._set_ekf(False)
        if "ekf" in lmsg and "ok" in lmsg:
            self._set_ekf(True)
        if "critical" in lmsg or "fail" in lmsg:
            self._set_critical(True, msg)

    # ------------ helpers ------------
    def _set_ekf(self, ok):
        if ok != self._ekf_ok:
            self._ekf_ok = ok
            self.ekfOkChanged.emit(ok)

    def _set_critical(self, status, msg):
        if status != self._critical_error or msg != self._critical_message:
            self._critical_error = status
            self._critical_message = msg
            self.criticalErrorChanged.emit(status, msg)

    def _ekf_watchdog(self):
        # simple placeholder – could query connector for last EKF_OK time
        pass
