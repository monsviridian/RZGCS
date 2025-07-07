"""
DroneKit ViewModel - Qt-ViewModel für DroneKit-Integration
"""

import sys
import os
from typing import Dict, Any, Optional
from PySide6.QtCore import QObject, Property, Signal, Slot
from backend.rzgcs_dronekit.connector import DroneKitConnector

class DroneKitViewModel(QObject):
    """Qt-ViewModel für DroneKit-Integration"""
    
    # Signals für QML
    connectionStateChanged = Signal(bool)
    armedStateChanged = Signal(bool)
    flightModeChanged = Signal(str)
    gpsPositionChanged = Signal(float, float, float)
    attitudeChanged = Signal(float, float, float)
    batteryChanged = Signal(float)
    groundSpeedChanged = Signal(float)
    altitudeChanged = Signal(float)
    headingChanged = Signal(float)
    airSpeedChanged = Signal(float)
    climbRateChanged = Signal(float)
    gpsFixChanged = Signal(int)
    satelliteCountChanged = Signal(int)
    vibrationChanged = Signal(float, float, float)
    temperatureChanged = Signal(float)
    errorOccurred = Signal(str)
    logMessageReceived = Signal(str)
    
    # Mission Signals
    missionUploaded = Signal(int)
    missionDownloaded = Signal(int)
    missionStarted = Signal()
    missionPaused = Signal()
    missionResumed = Signal()
    missionCompleted = Signal()
    waypointReached = Signal(int)
    missionError = Signal(str)
    missionLog = Signal(str)
    
    # Control Signals
    armStatusChanged = Signal(bool)
    takeoffCompleted = Signal(float)
    landingCompleted = Signal()
    navigationCompleted = Signal(float, float, float)
    controlError = Signal(str)
    controlLog = Signal(str)
    
    # Parameter Signals
    parametersLoaded = Signal(int)
    parameterUpdated = Signal(str, float)
    parameterSet = Signal(str, float)
    parameterError = Signal(str)
    parameterLog = Signal(str)
    
    # Vehicle Signals
    vehicleInfoUpdated = Signal(dict)
    systemStatusChanged = Signal(str)
    vehicleReadyChanged = Signal(bool)
    vehicleLog = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._connector = None
        self._connection_string = ""
        
        # Status-Variablen
        self._is_connected = False
        self._is_armed = False
        self._flight_mode = "UNKNOWN"
        self._gps_lat = 0.0
        self._gps_lon = 0.0
        self._gps_alt = 0.0
        self._roll = 0.0
        self._pitch = 0.0
        self._yaw = 0.0
        self._battery = 0.0
        self._ground_speed = 0.0
        self._altitude = 0.0
        self._heading = 0.0
        self._air_speed = 0.0
        self._climb_rate = 0.0
        self._gps_fix = 0
        self._satellite_count = 0
        self._vibration_x = 0.0
        self._vibration_y = 0.0
        self._vibration_z = 0.0
        self._temperature = 0.0
        self._system_status = "UNKNOWN"
        self._vehicle_ready = False
        
    @Slot(str)
    def connectToDrone(self, connection_string: str):
        """Verbindet zur Drohne"""
        if self._connector:
            self._connector.disconnect()
            self._connector = None
            
        self._connector = DroneKitConnector(connection_string)
        
        # Signals verbinden
        self._connect_connector_signals()
        
        # Verbindung herstellen (synchron)
        if self._connector:
            success = self._connector.establish_connection()
            if not success:
                self.errorOccurred.emit("Connection failed")
    
    def _connect_connector_signals(self):
        """Verbindet alle Connector-Signals"""
        if not self._connector:
            return
            
        # Telemetrie-Signals
        self._connector.connection_status_changed.connect(self._on_connection_changed)
        self._connector.gps_position_updated.connect(self._on_gps_updated)
        self._connector.attitude_updated.connect(self._on_attitude_updated)
        self._connector.battery_updated.connect(self._on_battery_updated)
        self._connector.flight_mode_changed.connect(self._on_flight_mode_changed)
        self._connector.armed_status_changed.connect(self._on_armed_changed)
        self._connector.ground_speed_updated.connect(self._on_ground_speed_updated)
        self._connector.altitude_updated.connect(self._on_altitude_updated)
        self._connector.heading_updated.connect(self._on_heading_updated)
        self._connector.air_speed_updated.connect(self._on_air_speed_updated)
        self._connector.climb_rate_updated.connect(self._on_climb_rate_updated)
        self._connector.gps_fix_updated.connect(self._on_gps_fix_updated)
        self._connector.satellite_count_updated.connect(self._on_satellite_count_updated)
        self._connector.vibration_updated.connect(self._on_vibration_updated)
        self._connector.temperature_updated.connect(self._on_temperature_updated)
        self._connector.error_occurred.connect(self._on_error)
        self._connector.log_message.connect(self._on_log_message)
        
        # Mission-Signals
        self._connector.mission_uploaded.connect(self.missionUploaded.emit)
        self._connector.mission_downloaded.connect(self.missionDownloaded.emit)
        self._connector.mission_started.connect(self.missionStarted.emit)
        self._connector.mission_paused.connect(self.missionPaused.emit)
        self._connector.mission_resumed.connect(self.missionResumed.emit)
        self._connector.mission_completed.connect(self.missionCompleted.emit)
        self._connector.waypoint_reached.connect(self.waypointReached.emit)
        self._connector.mission_error.connect(self.missionError.emit)
        self._connector.mission_log.connect(self.missionLog.emit)
        
        # Control-Signals
        self._connector.arm_status_changed.connect(self.armStatusChanged.emit)
        self._connector.takeoff_completed.connect(self.takeoffCompleted.emit)
        self._connector.landing_completed.connect(self.landingCompleted.emit)
        self._connector.navigation_completed.connect(self.navigationCompleted.emit)
        self._connector.control_error.connect(self.controlError.emit)
        self._connector.control_log.connect(self.controlLog.emit)
        
        # Parameter-Signals
        self._connector.parameters_loaded.connect(self.parametersLoaded.emit)
        self._connector.parameter_updated.connect(self.parameterUpdated.emit)
        self._connector.parameter_set.connect(self.parameterSet.emit)
        self._connector.parameter_error.connect(self.parameterError.emit)
        self._connector.parameter_log.connect(self.parameterLog.emit)
        
        # Vehicle-Signals
        self._connector.vehicle_info_updated.connect(self.vehicleInfoUpdated.emit)
        self._connector.system_status_changed.connect(self._on_system_status_changed)
        self._connector.vehicle_ready_changed.connect(self._on_vehicle_ready_changed)
        self._connector.vehicle_log.connect(self.vehicleLog.emit)
    
    @Slot()
    def disconnectFromDrone(self):
        """Trennt Verbindung zur Drohne"""
        if self._connector:
            self._connector.close_connection()
            self._connector = None
    
    # Control-Slots
    @Slot(bool)
    def armDisarm(self, arm: bool):
        """Armt oder disarmed die Drohne"""
        if self._connector:
            self._connector.arm_disarm(arm)
    
    @Slot(float)
    def takeoff(self, altitude: float):
        """Takeoff"""
        if self._connector:
            self._connector.takeoff(altitude)
    
    @Slot()
    def land(self):
        """Landung"""
        if self._connector:
            self._connector.land()
    
    @Slot(float, float, float)
    def gotoPosition(self, lat: float, lon: float, alt: float):
        """Navigation zu Position"""
        if self._connector:
            self._connector.goto_position(lat, lon, alt)
    
    @Slot()
    def returnToLaunch(self):
        """Return to Launch"""
        if self._connector:
            self._connector.return_to_launch()
    
    # Mission-Slots
    @Slot('QVariantList')
    def uploadMission(self, waypoints):
        """Mission hochladen"""
        if self._connector:
            self._connector.upload_mission(waypoints)
    
    @Slot()
    def startMission(self):
        """Mission starten"""
        if self._connector:
            self._connector.start_mission()
    
    @Slot()
    def pauseMission(self):
        """Mission pausieren"""
        if self._connector:
            self._connector.pause_mission()
    
    @Slot()
    def resumeMission(self):
        """Mission fortsetzen"""
        if self._connector:
            self._connector.resume_mission()
    
    @Slot()
    def stopMission(self):
        """Mission stoppen"""
        if self._connector:
            self._connector.stop_mission()
    
    # Parameter-Slots
    @Slot()
    def loadParameters(self):
        """Parameter laden"""
        if self._connector:
            self._connector.load_parameters()
    
    @Slot(str, float)
    def setParameter(self, param_name: str, value: float):
        """Parameter setzen"""
        if self._connector:
            self._connector.set_parameter(param_name, value)
    
    # Callback-Handler
    def _on_connection_changed(self, connected: bool):
        self._is_connected = connected
        self.connectionStateChanged.emit(connected)
    
    def _on_armed_changed(self, armed: bool):
        self._is_armed = armed
        self.armedStateChanged.emit(armed)
    
    def _on_flight_mode_changed(self, mode: str):
        self._flight_mode = mode
        self.flightModeChanged.emit(mode)
    
    def _on_gps_updated(self, lat: float, lon: float, alt: float):
        self._gps_lat = lat
        self._gps_lon = lon
        self._gps_alt = alt
        self.gpsPositionChanged.emit(lat, lon, alt)
    
    def _on_attitude_updated(self, roll: float, pitch: float, yaw: float):
        self._roll = roll
        self._pitch = pitch
        self._yaw = yaw
        self.attitudeChanged.emit(roll, pitch, yaw)
    
    def _on_battery_updated(self, battery: float):
        self._battery = battery
        self.batteryChanged.emit(battery)
    
    def _on_ground_speed_updated(self, speed: float):
        self._ground_speed = speed
        self.groundSpeedChanged.emit(speed)
    
    def _on_altitude_updated(self, altitude: float):
        self._altitude = altitude
        self.altitudeChanged.emit(altitude)
    
    def _on_heading_updated(self, heading: float):
        self._heading = heading
        self.headingChanged.emit(heading)
    
    def _on_air_speed_updated(self, air_speed: float):
        self._air_speed = air_speed
        self.airSpeedChanged.emit(air_speed)
    
    def _on_climb_rate_updated(self, climb_rate: float):
        self._climb_rate = climb_rate
        self.climbRateChanged.emit(climb_rate)
    
    def _on_gps_fix_updated(self, gps_fix: int):
        self._gps_fix = gps_fix
        self.gpsFixChanged.emit(gps_fix)
    
    def _on_satellite_count_updated(self, satellite_count: int):
        self._satellite_count = satellite_count
        self.satelliteCountChanged.emit(satellite_count)
    
    def _on_vibration_updated(self, x: float, y: float, z: float):
        self._vibration_x = x
        self._vibration_y = y
        self._vibration_z = z
        self.vibrationChanged.emit(x, y, z)
    
    def _on_temperature_updated(self, temperature: float):
        self._temperature = temperature
        self.temperatureChanged.emit(temperature)
    
    def _on_system_status_changed(self, status: str):
        self._system_status = status
        self.systemStatusChanged.emit(status)
    
    def _on_vehicle_ready_changed(self, ready: bool):
        self._vehicle_ready = ready
        self.vehicleReadyChanged.emit(ready)
    
    def _on_error(self, error: str):
        self.errorOccurred.emit(error)
    
    def _on_log_message(self, message: str):
        self.logMessageReceived.emit(message)
    
    # Properties für QML
    @Property(bool, notify=connectionStateChanged)
    def isConnected(self):
        return self._is_connected
    
    @Property(bool, notify=armedStateChanged)
    def isArmed(self):
        return self._is_armed
    
    @Property(str, notify=flightModeChanged)
    def flightMode(self):
        return self._flight_mode
    
    @Property(float, notify=batteryChanged)
    def batteryLevel(self):
        return self._battery
    
    @Property(float, notify=groundSpeedChanged)
    def groundSpeed(self):
        return self._ground_speed
    
    @Property(float, notify=altitudeChanged)
    def altitude(self):
        return self._altitude
    
    @Property(float, notify=headingChanged)
    def heading(self):
        return self._heading
    
    @Property(float, notify=airSpeedChanged)
    def airSpeed(self):
        return self._air_speed
    
    @Property(float, notify=climbRateChanged)
    def climbRate(self):
        return self._climb_rate
    
    @Property(int, notify=gpsFixChanged)
    def gpsFix(self):
        return self._gps_fix
    
    @Property(int, notify=satelliteCountChanged)
    def satelliteCount(self):
        return self._satellite_count
    
    @Property(float, notify=temperatureChanged)
    def temperature(self):
        return self._temperature
    
    @Property(str, notify=systemStatusChanged)
    def systemStatus(self):
        return self._system_status
    
    @Property(bool, notify=vehicleReadyChanged)
    def vehicleReady(self):
        return self._vehicle_ready
    
    # Getter-Methoden für zusätzliche Daten
    def getTelemetryData(self):
        """Gibt Telemetrie-Daten zurück"""
        if self._connector:
            return self._connector.get_telemetry_data()
        return {}
    
    def getMissionStatus(self):
        """Gibt Mission-Status zurück"""
        if self._connector:
            return self._connector.get_mission_status()
        return {}
    
    def getControlStatus(self):
        """Gibt Control-Status zurück"""
        if self._connector:
            return self._connector.get_control_status()
        return {}
    
    def getParameterSummary(self):
        """Gibt Parameter-Zusammenfassung zurück"""
        if self._connector:
            return self._connector.get_parameter_summary()
        return {}
    
    def getVehicleSummary(self):
        """Gibt Vehicle-Zusammenfassung zurück"""
        if self._connector:
            return self._connector.get_vehicle_summary()
        return {}
    
    def getVehicleHealth(self):
        """Gibt Vehicle-Gesundheit zurück"""
        if self._connector:
            return self._connector.get_vehicle_health()
        return {}
    
    def getConnectionStatus(self):
        """Gibt Verbindungsstatus zurück"""
        if self._connector:
            return self._connector.get_connection_status()
        return {} 