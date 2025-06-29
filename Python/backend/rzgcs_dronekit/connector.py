"""
DroneKit Connector - Hauptverbindungsklasse für DroneKit-Integration
"""

# Python 3.13 Kompatibilitätsfix für DroneKit/pymavlink
import collections.abc
import collections
if not hasattr(collections, 'MutableMapping'):
    collections.MutableMapping = collections.abc.MutableMapping

import threading
import time
import asyncio
from typing import Optional, Dict, Any
from PySide6.QtCore import QObject, Signal, QTimer, Slot

# DroneKit-Imports
# External DroneKit import - fixed to avoid circular imports
import dronekit as dronekit_external  # Externe DroneKit-Bibliothek
connect = dronekit_external.connect  # Aus externer DroneKit-Bibliothek
Vehicle = dronekit_external.Vehicle  # Aus externer DroneKit-Bibliothek
VehicleMode = dronekit_external.VehicleMode  # Aus externer DroneKit-Bibliothek


from .connection_manager import DroneKitConnectionManager
from .telemetry_handler import DroneKitTelemetryHandler
from .control_handler import DroneKitControlHandler
from .mission_handler import DroneKitMissionHandler
from .parameter_manager import DroneKitParameterManager
from .vehicle_manager import DroneKitVehicleManager
from .utils import DroneKitUtils
from .custom_vehicle import RZGCSVehicle

class DroneKitConnector(QObject):
    """Hauptverbindungsklasse für DroneKit-Integration"""
    
    # Signals
    connection_status_changed = Signal(bool)  # connected
    gps_position_updated = Signal(float, float, float)  # lat, lon, alt
    attitude_updated = Signal(float, float, float)  # roll, pitch, yaw
    battery_updated = Signal(float, float)  # voltage, level
    mode_changed = Signal(str)  # mode name
    armed_changed = Signal(bool)  # armed status
    log_message = Signal(str)  # log message
    error_occurred = Signal(str)  # error message
    
    # Mission Signals
    mission_uploaded = Signal(int)
    mission_downloaded = Signal(int)
    mission_started = Signal()
    mission_paused = Signal()
    mission_resumed = Signal()
    mission_completed = Signal()
    waypoint_reached = Signal(int)
    mission_error = Signal(str)
    mission_log = Signal(str)
    
    # Control Signals
    arm_status_changed = Signal(bool)
    takeoff_completed = Signal(float)
    landing_completed = Signal()
    navigation_completed = Signal(float, float, float)
    control_error = Signal(str)
    control_log = Signal(str)
    
    # Parameter Signals
    parameters_loaded = Signal(int)
    parameter_updated = Signal(str, float)
    parameter_set = Signal(str, float)
    parameter_error = Signal(str)
    parameter_log = Signal(str)
    
    # Vehicle Signals
    vehicle_info_updated = Signal(dict)
    system_status_changed = Signal(str)
    vehicle_ready_changed = Signal(bool)
    vehicle_log = Signal(str)
    
    def __init__(self, connection_string: str, parent=None):
        super().__init__(parent)
        self.connection_string = connection_string
        self.vehicle: Optional[RZGCSVehicle] = None
        self.is_connected = False
        
        # Manager
        self.connection_manager = None
        self.telemetry_handler = None
        self.control_handler = None
        self.mission_handler = None
        self.parameter_manager = None
        self.vehicle_manager = None
        
        # Threading
        self.stop_event = threading.Event()
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self._update_status)
        
        self.log_message.emit("DroneKitConnector initialisiert")
    
    def establish_connection(self) -> bool:
        """Verbindet zur Drohne"""
        try:
            # Connection Manager erstellen
            self.connection_manager = DroneKitConnectionManager()
            
            # Verbindung herstellen (synchron)
            self.vehicle = self.connection_manager.establish_connection(self.connection_string)
            
            if not self.vehicle:
                self.error_occurred.emit("Verbindung fehlgeschlagen")
                return False
            
            # Manager initialisieren
            self._initialize_managers()
            
            # Telemetrie-Callbacks einrichten
            self.telemetry_handler.setup_telemetry_callbacks()
            
            # Heartbeat-Monitoring starten
            self.connection_manager.start_heartbeat_monitoring()
            
            # Status-Update-Timer starten
            self.update_timer.start(100)  # 10 Hz
            
            self.is_connected = True
            self.connection_status_changed.emit(True)
            self.log_message.emit("Verbindung erfolgreich hergestellt")
            
            return True
            
        except Exception as e:
            error_msg = f"Verbindungsfehler: {str(e)}"
            self.error_occurred.emit(error_msg)
            self.log_message.emit(error_msg)
            return False
    
    def _initialize_managers(self):
        """Initialisiert alle Manager"""
        # Telemetrie Handler
        self.telemetry_handler = DroneKitTelemetryHandler(self.vehicle, self)
        self._connect_telemetry_signals()
        
        # Control Handler
        self.control_handler = DroneKitControlHandler(self.vehicle, self)
        self._connect_control_signals()
        
        # Mission Handler
        self.mission_handler = DroneKitMissionHandler(self.vehicle, self)
        self._connect_mission_signals()
        
        # Parameter Manager
        self.parameter_manager = DroneKitParameterManager(self.vehicle, self)
        self._connect_parameter_signals()
        
        # Vehicle Manager
        self.vehicle_manager = DroneKitVehicleManager(self.vehicle, self)
        self._connect_vehicle_signals()
    
    def _connect_telemetry_signals(self):
        """Verbindet Telemetrie-Signals"""
        self.telemetry_handler.gps_position_updated.connect(self.gps_position_updated.emit)
        self.telemetry_handler.attitude_updated.connect(self.attitude_updated.emit)
        self.telemetry_handler.battery_updated.connect(self.battery_updated.emit)
        self.telemetry_handler.flight_mode_changed.connect(self.mode_changed.emit)
        self.telemetry_handler.armed_status_changed.connect(self.armed_changed.emit)
        self.telemetry_handler.ground_speed_updated.connect(self.ground_speed_updated.emit)
        self.telemetry_handler.altitude_updated.connect(self.altitude_updated.emit)
        self.telemetry_handler.heading_updated.connect(self.heading_updated.emit)
        self.telemetry_handler.air_speed_updated.connect(self.air_speed_updated.emit)
        self.telemetry_handler.climb_rate_updated.connect(self.climb_rate_updated.emit)
        self.telemetry_handler.gps_fix_updated.connect(self.gps_fix_updated.emit)
        self.telemetry_handler.satellite_count_updated.connect(self.satellite_count_updated.emit)
        self.telemetry_handler.vibration_updated.connect(self.vibration_updated.emit)
        self.telemetry_handler.temperature_updated.connect(self.temperature_updated.emit)
    
    def _connect_control_signals(self):
        """Verbindet Control-Signals"""
        self.control_handler.arm_status_changed.connect(self.arm_status_changed.emit)
        self.control_handler.takeoff_completed.connect(self.takeoff_completed.emit)
        self.control_handler.landing_completed.connect(self.landing_completed.emit)
        self.control_handler.navigation_completed.connect(self.navigation_completed.emit)
        self.control_handler.control_error.connect(self.control_error.emit)
        self.control_handler.control_log.connect(self.control_log.emit)
    
    def _connect_mission_signals(self):
        """Verbindet Mission-Signals"""
        self.mission_handler.mission_uploaded.connect(self.mission_uploaded.emit)
        self.mission_handler.mission_downloaded.connect(self.mission_downloaded.emit)
        self.mission_handler.mission_started.connect(self.mission_started.emit)
        self.mission_handler.mission_paused.connect(self.mission_paused.emit)
        self.mission_handler.mission_resumed.connect(self.mission_resumed.emit)
        self.mission_handler.mission_completed.connect(self.mission_completed.emit)
        self.mission_handler.waypoint_reached.connect(self.waypoint_reached.emit)
        self.mission_handler.mission_error.connect(self.mission_error.emit)
        self.mission_handler.mission_log.connect(self.mission_log.emit)
    
    def _connect_parameter_signals(self):
        """Verbindet Parameter-Signals"""
        self.parameter_manager.parameters_loaded.connect(self.parameters_loaded.emit)
        self.parameter_manager.parameter_updated.connect(self.parameter_updated.emit)
        self.parameter_manager.parameter_set.connect(self.parameter_set.emit)
        self.parameter_manager.parameter_error.connect(self.parameter_error.emit)
        self.parameter_manager.parameter_log.connect(self.parameter_log.emit)
    
    def _connect_vehicle_signals(self):
        """Verbindet Vehicle-Signals"""
        self.vehicle_manager.vehicle_info_updated.connect(self.vehicle_info_updated.emit)
        self.vehicle_manager.system_status_changed.connect(self.system_status_changed.emit)
        self.vehicle_manager.vehicle_ready_changed.connect(self.vehicle_ready_changed.emit)
        self.vehicle_manager.vehicle_log.connect(self.vehicle_log.emit)
    
    def _update_status(self):
        """Update-Methode für den Status"""
        # Diese Methode wird vom QTimer aufgerufen
        # Hier können zusätzliche Qt-spezifische Updates erfolgen
        pass
    
    def close_connection(self):
        """Trennt die Verbindung zur Drohne"""
        try:
            # Monitoring stoppen
            self.stop_event.set()
            
            # Manager aufräumen
            if self.telemetry_handler:
                self.telemetry_handler.remove_callbacks()
            
            if self.connection_manager:
                self.connection_manager.close_connection()
            
            # Vehicle schließen
            if self.vehicle:
                self.vehicle.close()
                self.vehicle = None
            
            # Timer stoppen
            self.update_timer.stop()
            
            self.is_connected = False
            self.connection_status_changed.emit(False)
            self.log_message.emit("DroneKit connection closed")
            
        except Exception as e:
            error_msg = f"Error during disconnect: {str(e)}"
            self.error_occurred.emit(error_msg)
    
    # Convenience-Methoden für einfachen Zugriff
    
    @Slot(bool)
    def arm_disarm(self, arm: bool):
        """Armt oder disarmed die Drohne"""
        if self.control_handler:
            self.control_handler.arm_disarm(arm)
    
    @Slot(float)
    def takeoff(self, altitude: float):
        """Takeoff"""
        if self.control_handler:
            self.control_handler.takeoff(altitude)
    
    @Slot()
    def land(self):
        """Landung"""
        if self.control_handler:
            self.control_handler.land()
    
    @Slot(float, float, float)
    def goto_position(self, lat: float, lon: float, alt: float):
        """Navigation zu Position"""
        if self.control_handler:
            self.control_handler.goto_position(lat, lon, alt)
    
    @Slot()
    def return_to_launch(self):
        """Return to Launch"""
        if self.control_handler:
            self.control_handler.return_to_launch()
    
    @Slot('QVariantList')
    def upload_mission(self, waypoints):
        """Mission hochladen"""
        if self.mission_handler:
            asyncio.create_task(self.mission_handler.upload_mission(waypoints))
    
    @Slot()
    def start_mission(self):
        """Mission starten"""
        if self.mission_handler:
            asyncio.create_task(self.mission_handler.start_mission())
    
    @Slot()
    def pause_mission(self):
        """Mission pausieren"""
        if self.mission_handler:
            asyncio.create_task(self.mission_handler.pause_mission())
    
    @Slot()
    def resume_mission(self):
        """Mission fortsetzen"""
        if self.mission_handler:
            asyncio.create_task(self.mission_handler.resume_mission())
    
    @Slot()
    def stop_mission(self):
        """Mission stoppen"""
        if self.mission_handler:
            asyncio.create_task(self.mission_handler.stop_mission())
    
    @Slot()
    def load_parameters(self):
        """Parameter laden"""
        if self.parameter_manager:
            asyncio.create_task(self.parameter_manager.load_parameters())
    
    @Slot(str, float)
    def set_parameter(self, param_name: str, value: float):
        """Parameter setzen"""
        if self.parameter_manager:
            asyncio.create_task(self.parameter_manager.set_parameter(param_name, value))
    
    # Getter-Methoden
    
    def get_telemetry_data(self) -> Dict[str, Any]:
        """Gibt Telemetrie-Daten zurück"""
        return self.telemetry_cache.copy()
    
    def get_mission_status(self) -> Dict[str, Any]:
        """Gibt Mission-Status zurück"""
        if self.mission_handler:
            return self.mission_handler.get_mission_status()
        return {}
    
    def get_control_status(self) -> Dict[str, Any]:
        """Gibt Control-Status zurück"""
        if self.control_handler:
            return self.control_handler.get_control_status()
        return {}
    
    def get_parameter_summary(self) -> Dict[str, Any]:
        """Gibt Parameter-Zusammenfassung zurück"""
        if self.parameter_manager:
            return self.parameter_manager.get_parameter_summary()
        return {}
    
    def get_vehicle_summary(self) -> Dict[str, Any]:
        """Gibt Vehicle-Zusammenfassung zurück"""
        if self.vehicle_manager:
            return self.vehicle_manager.get_vehicle_summary()
        return {}
    
    def get_vehicle_health(self) -> Dict[str, Any]:
        """Gibt Vehicle-Gesundheit zurück"""
        if self.vehicle_manager:
            return self.vehicle_manager.get_vehicle_health()
        return {}
    
    def get_connection_status(self) -> Dict[str, Any]:
        """Gibt Verbindungsstatus zurück"""
        if self.connection_manager:
            return self.connection_manager.get_connection_status()
        return {}
    
    # Properties für QML
    
    @property
    def connected(self) -> bool:
        return self.is_connected
    
    @property
    def vehicle_ready(self) -> bool:
        if self.vehicle_manager:
            return self.vehicle_manager.is_vehicle_ready()
        return False
    
    @property
    def flight_mode(self) -> str:
        if self.vehicle:
            return self.vehicle.mode.name
        return "UNKNOWN"
    
    @property
    def armed(self) -> bool:
        if self.vehicle:
            return self.vehicle.armed
        return False 