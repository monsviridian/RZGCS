from PySide6.QtCore import QObject, Signal, Slot, Property
import logging

class StatusOverviewController(QObject):
    """Controller für die Statusübersichtsansicht"""
    
    # Signale für Statusänderungen
    vehicleInfoChanged = Signal()
    radioStatusChanged = Signal()
    flightModesChanged = Signal()
    sensorsStatusChanged = Signal()
    powerStatusChanged = Signal()
    safetyStatusChanged = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._logger = logging.getLogger(__name__)
        
        # Fahrzeuginformationen
        self._frame_class = "Unbekannt"
        self._frame_type = "Unbekannt"
        self._firmware_version = "Unbekannt"
        self._vehicle_ready = False
        
        # Radio-Status
        self._radio_ok = False
        self._roll_channel = "Channel 1"
        self._pitch_channel = "Channel 2"
        self._yaw_channel = "Channel 4"
        self._throttle_channel = "Channel 3"
        
        # Flugmodi
        self._flight_modes = [
            "Unbekannt", "Unbekannt", "Unbekannt",
            "Unbekannt", "Unbekannt", "Unbekannt"
        ]
        self._flight_modes_ok = False
        
        # Sensorstatus
        self._compass_status = "Unbekannt"
        self._accel_status = "Unbekannt"
        self._baro_status = "Unbekannt"
        self._imu_status = "Unbekannt"
        self._sensors_ok = False
        
        # Power-Status
        self._batt1_monitor = "Unbekannt"
        self._batt1_capacity = "Unbekannt"
        self._batt2_monitor = "Unbekannt"
        self._power_ok = True
        
        # Safety-Einstellungen
        self._arming_checks = "Unbekannt"
        self._manual_arming = "Unbekannt"
        self._batt_low_failsafe = "Unbekannt"
        self._batt_critical_failsafe = "Unbekannt"
        self._geofence = "Unbekannt"
        self._rtl_altitude = "Unbekannt"
    
    # --- Fahrzeuginformationen ---
    @Property(str, notify=vehicleInfoChanged)
    def frame_class(self):
        return self._frame_class
    
    @frame_class.setter
    def frame_class(self, value):
        if self._frame_class != value:
            self._frame_class = value
            self.vehicleInfoChanged.emit()
    
    @Property(str, notify=vehicleInfoChanged)
    def frame_type(self):
        return self._frame_type
    
    @frame_type.setter
    def frame_type(self, value):
        if self._frame_type != value:
            self._frame_type = value
            self.vehicleInfoChanged.emit()
    
    @Property(str, notify=vehicleInfoChanged)
    def firmware_version(self):
        return self._firmware_version
    
    @firmware_version.setter
    def firmware_version(self, value):
        if self._firmware_version != value:
            self._firmware_version = value
            self.vehicleInfoChanged.emit()
    
    @Property(bool, notify=vehicleInfoChanged)
    def vehicle_ready(self):
        return self._vehicle_ready
    
    @vehicle_ready.setter
    def vehicle_ready(self, value):
        if self._vehicle_ready != value:
            self._vehicle_ready = value
            self.vehicleInfoChanged.emit()
    
    # --- Radio-Status ---
    @Property(bool, notify=radioStatusChanged)
    def radio_ok(self):
        return self._radio_ok
    
    @radio_ok.setter
    def radio_ok(self, value):
        if self._radio_ok != value:
            self._radio_ok = value
            self.radioStatusChanged.emit()
    
    @Property(str, notify=radioStatusChanged)
    def roll_channel(self):
        return self._roll_channel
    
    @roll_channel.setter
    def roll_channel(self, value):
        if self._roll_channel != value:
            self._roll_channel = value
            self.radioStatusChanged.emit()
    
    @Property(str, notify=radioStatusChanged)
    def pitch_channel(self):
        return self._pitch_channel
    
    @pitch_channel.setter
    def pitch_channel(self, value):
        if self._pitch_channel != value:
            self._pitch_channel = value
            self.radioStatusChanged.emit()
    
    @Property(str, notify=radioStatusChanged)
    def yaw_channel(self):
        return self._yaw_channel
    
    @yaw_channel.setter
    def yaw_channel(self, value):
        if self._yaw_channel != value:
            self._yaw_channel = value
            self.radioStatusChanged.emit()
    
    @Property(str, notify=radioStatusChanged)
    def throttle_channel(self):
        return self._throttle_channel
    
    @throttle_channel.setter
    def throttle_channel(self, value):
        if self._throttle_channel != value:
            self._throttle_channel = value
            self.radioStatusChanged.emit()
    
    # --- Flugmodi ---
    @Property(list, notify=flightModesChanged)
    def flight_modes(self):
        return self._flight_modes
    
    @flight_modes.setter
    def flight_modes(self, value):
        if self._flight_modes != value:
            self._flight_modes = value
            self.flightModesChanged.emit()
    
    @Property(bool, notify=flightModesChanged)
    def flight_modes_ok(self):
        return self._flight_modes_ok
    
    @flight_modes_ok.setter
    def flight_modes_ok(self, value):
        if self._flight_modes_ok != value:
            self._flight_modes_ok = value
            self.flightModesChanged.emit()
    
    # --- Sensoren ---
    @Property(str, notify=sensorsStatusChanged)
    def compass_status(self):
        return self._compass_status
    
    @compass_status.setter
    def compass_status(self, value):
        if self._compass_status != value:
            self._compass_status = value
            self.sensorsStatusChanged.emit()
    
    @Property(str, notify=sensorsStatusChanged)
    def accel_status(self):
        return self._accel_status
    
    @accel_status.setter
    def accel_status(self, value):
        if self._accel_status != value:
            self._accel_status = value
            self.sensorsStatusChanged.emit()
    
    @Property(str, notify=sensorsStatusChanged)
    def baro_status(self):
        return self._baro_status
    
    @baro_status.setter
    def baro_status(self, value):
        if self._baro_status != value:
            self._baro_status = value
            self.sensorsStatusChanged.emit()
    
    @Property(str, notify=sensorsStatusChanged)
    def imu_status(self):
        return self._imu_status
    
    @imu_status.setter
    def imu_status(self, value):
        if self._imu_status != value:
            self._imu_status = value
            self.sensorsStatusChanged.emit()
    
    @Property(bool, notify=sensorsStatusChanged)
    def sensors_ok(self):
        return self._sensors_ok
    
    @sensors_ok.setter
    def sensors_ok(self, value):
        if self._sensors_ok != value:
            self._sensors_ok = value
            self.sensorsStatusChanged.emit()
    
    # --- Power ---
    @Property(str, notify=powerStatusChanged)
    def batt1_monitor(self):
        return self._batt1_monitor
    
    @batt1_monitor.setter
    def batt1_monitor(self, value):
        if self._batt1_monitor != value:
            self._batt1_monitor = value
            self.powerStatusChanged.emit()
    
    @Property(str, notify=powerStatusChanged)
    def batt1_capacity(self):
        return self._batt1_capacity
    
    @batt1_capacity.setter
    def batt1_capacity(self, value):
        if self._batt1_capacity != value:
            self._batt1_capacity = value
            self.powerStatusChanged.emit()
    
    @Property(str, notify=powerStatusChanged)
    def batt2_monitor(self):
        return self._batt2_monitor
    
    @batt2_monitor.setter
    def batt2_monitor(self, value):
        if self._batt2_monitor != value:
            self._batt2_monitor = value
            self.powerStatusChanged.emit()
    
    @Property(bool, notify=powerStatusChanged)
    def power_ok(self):
        return self._power_ok
    
    @power_ok.setter
    def power_ok(self, value):
        if self._power_ok != value:
            self._power_ok = value
            self.powerStatusChanged.emit()
    
    # --- Safety ---
    @Property(str, notify=safetyStatusChanged)
    def arming_checks(self):
        return self._arming_checks
    
    @arming_checks.setter
    def arming_checks(self, value):
        if self._arming_checks != value:
            self._arming_checks = value
            self.safetyStatusChanged.emit()
    
    @Property(str, notify=safetyStatusChanged)
    def manual_arming(self):
        return self._manual_arming
    
    @manual_arming.setter
    def manual_arming(self, value):
        if self._manual_arming != value:
            self._manual_arming = value
            self.safetyStatusChanged.emit()
    
    @Property(str, notify=safetyStatusChanged)
    def batt_low_failsafe(self):
        return self._batt_low_failsafe
    
    @batt_low_failsafe.setter
    def batt_low_failsafe(self, value):
        if self._batt_low_failsafe != value:
            self._batt_low_failsafe = value
            self.safetyStatusChanged.emit()
    
    @Property(str, notify=safetyStatusChanged)
    def batt_critical_failsafe(self):
        return self._batt_critical_failsafe
    
    @batt_critical_failsafe.setter
    def batt_critical_failsafe(self, value):
        if self._batt_critical_failsafe != value:
            self._batt_critical_failsafe = value
            self.safetyStatusChanged.emit()
    
    @Property(str, notify=safetyStatusChanged)
    def geofence(self):
        return self._geofence
    
    @geofence.setter
    def geofence(self, value):
        if self._geofence != value:
            self._geofence = value
            self.safetyStatusChanged.emit()
    
    @Property(str, notify=safetyStatusChanged)
    def rtl_altitude(self):
        return self._rtl_altitude
    
    @rtl_altitude.setter
    def rtl_altitude(self, value):
        if self._rtl_altitude != value:
            self._rtl_altitude = value
            self.safetyStatusChanged.emit()
    
    # Verarbeitung eingehender MAVLink-Nachrichten
    @Slot(float, float, float)
    def handle_attitude(self, roll, pitch, yaw):
        """Verarbeitet Attitude-Updates (Roll, Pitch, Yaw)"""
        # Aktualisiert intern die Fahrzeuglage, kann für Status-Anzeige verwendet werden
        self._vehicle_ready = True  # Wenn wir Attitude-Daten bekommen, ist das Fahrzeug bereit
        self.vehicleInfoChanged.emit()
    
    @Slot(float, float, float)
    def handle_gps(self, lat, lon, alt):
        """Verarbeitet GPS-Updates (Latitude, Longitude, Altitude)"""
        # GPS-Daten können für Status-Anzeige verwendet werden
        pass
        
    @Slot(bool)
    def handle_connection_change(self, connected):
        """Verarbeitet Änderungen im Verbindungsstatus"""
        # Wenn verbunden, setzen wir bestimmte Status
        if connected:
            self._vehicle_ready = True
            self.vehicleInfoChanged.emit()
        else:
            self._vehicle_ready = False
            self.vehicleInfoChanged.emit()
    
    @Slot(object)
    def handle_sys_status(self, msg):
        """Verarbeitung der SYS_STATUS-Nachricht"""
        # Sensoren-Status aktualisieren
        sensors_present = msg.onboard_control_sensors_present
        sensors_enabled = msg.onboard_control_sensors_enabled
        sensors_health = msg.onboard_control_sensors_health
        
        # TODO: Spezifische Sensor-Flags verarbeiten
        # Beispiel (Pseudocode):
        # self._compass_status = "OK" if (sensors_health & MAV_SYS_STATUS_SENSOR_3D_MAG) else "Fehler"
        # self._accel_status = "OK" if (sensors_health & MAV_SYS_STATUS_SENSOR_3D_ACCEL) else "Fehler"
        
        # Battery-Status
        self._power_ok = msg.battery_remaining > 20 if msg.battery_remaining >= 0 else True
        self.powerStatusChanged.emit()
        self.sensorsStatusChanged.emit()
    
    @Slot(object)
    def handle_rc_channels(self, msg):
        """Verarbeitung der RC_CHANNELS-Nachricht"""
        # Radio ist okay, wenn RSSI > 0
        if hasattr(msg, 'rssi'):
            self._radio_ok = msg.rssi > 0
        else:
            # Fallback: Radio ist okay, wenn wir die Nachricht bekommen
            self._radio_ok = True
        
        self.radioStatusChanged.emit()
    
    @Slot(str, object)
    def handle_parameter_update(self, param_name, param_value):
        """Verarbeitung von Parameter-Updates"""
        if param_name.startswith("FRAME_"):
            if param_name == "FRAME_CLASS":
                frame_classes = {
                    0: "Quad", 1: "Hexa", 2: "Octa", 3: "Octa Quad", 4: "Y6",
                    5: "Heli", 6: "Single", 7: "Coax", 8: "Bicopter"
                }
                self._frame_class = frame_classes.get(int(param_value), f"Unbekannt ({param_value})")
                self.vehicleInfoChanged.emit()
            elif param_name == "FRAME_TYPE":
                frame_types = {
                    0: "+", 1: "X", 2: "V", 3: "H", 4: "V-Tail",
                    5: "A-Tail", 6: "Y6B", 7: "Y6F", 8: "BetaFlightX"
                }
                self._frame_type = frame_types.get(int(param_value), f"Unbekannt ({param_value})")
                self.vehicleInfoChanged.emit()
        elif param_name.startswith("FLTMODE"):
            # Flugmodi-Parameter verarbeiten
            try:
                mode_num = int(param_name.replace("FLTMODE", "")) - 1
                if 0 <= mode_num < len(self._flight_modes):
                    flight_modes = {
                        0: "Stabilize", 1: "Acro", 2: "AltHold", 3: "Auto", 
                        4: "Guided", 5: "Loiter", 6: "RTL", 7: "Circle", 
                        8: "Position", 9: "Land", 10: "PosHold", 11: "Brake",
                        13: "Throw", 14: "Avoid_ADSB", 15: "Guided_NoGPS", 16: "Smart_RTL",
                        17: "FlowHold", 18: "Follow", 19: "ZigZag", 20: "SystemID",
                        21: "Heli_Autorotate", 22: "Auto RTL"
                    }
                    self._flight_modes[mode_num] = flight_modes.get(int(param_value), f"Modus {param_value}")
                    self._flight_modes_ok = True
                    self.flightModesChanged.emit()
            except ValueError:
                pass
        elif param_name.startswith("BRD_SAFETY_"):
            # Safety-Parameter verarbeiten
            if param_name == "BRD_SAFETY_ENABLE":
                self._arming_checks = "Enabled" if int(param_value) == 1 else "Disabled"
                self.safetyStatusChanged.emit()
        elif param_name.startswith("BATT"):
            # Batterie-Parameter verarbeiten
            if param_name == "BATT_MONITOR":
                batt_monitors = {
                    0: "Disabled", 3: "Analog Voltage Only", 4: "Analog Voltage and Current", 
                    5: "Solo", 6: "Bebop", 7: "SMBus-Maxell", 8: "UAVCAN-BatteryInfo",
                    9: "BLHeli ESC", 10: "SumOfFollowing", 11: "FuelFlow", 12: "FuelLevelPWM"
                }
                self._batt1_monitor = batt_monitors.get(int(param_value), f"Unknown ({param_value})")
                self.powerStatusChanged.emit()
            elif param_name == "BATT_CAPACITY":
                self._batt1_capacity = f"{param_value} mAh"
                self.powerStatusChanged.emit()
        elif param_name == "COMPASS_ENABLE":
            # Compass-Parameter verarbeiten
            if int(param_value) == 1:
                self._compass_status = "Enabled"
            else:
                self._compass_status = "Disabled"
            self.sensorsStatusChanged.emit()
        elif param_name == "INS_ACCEL_FILTER":
            # Beschleunigungssensor-Parameter
            self._accel_status = f"Filter: {param_value} Hz"
            self.sensorsStatusChanged.emit()
        elif param_name == "FENCE_ENABLE":
            # GeoFence-Parameter
            self._geofence = "Enabled" if int(param_value) == 1 else "Disabled"
            self.safetyStatusChanged.emit()
        elif param_name == "RTL_ALT":
            # RTL-Höhe
            self._rtl_altitude = f"{param_value} cm"
            self.safetyStatusChanged.emit()
    
    # Diese Methode ist nicht mehr erforderlich, da wir keine message_received-Signals haben
    # aber wir behalten sie für zukünftige Erweiterungen
    @Slot(dict)
    def update_status_from_message(self, message_data):
        """Aktualisiert Status basierend auf MAVLink-Nachricht (aktuell nicht verwendet)"""
        pass
