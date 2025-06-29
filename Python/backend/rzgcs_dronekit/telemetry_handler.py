"""
DroneKit Telemetry Handler - Verwaltet Telemetrie-Streaming und Callbacks
"""

import time
import math
from typing import Dict, Any, Optional, Callable
from PySide6.QtCore import QObject, Signal

# DroneKit-Imports
# External DroneKit import - fixed to avoid circular imports
import dronekit as dronekit_external  # Externe DroneKit-Bibliothek
Vehicle = dronekit_external.Vehicle  # Aus externer DroneKit-Bibliothek


from .utils import DroneKitUtils

class DroneKitTelemetryHandler(QObject):
    """Verwaltet Telemetrie-Streaming und Callbacks mit Rate-Limiting"""
    
    # Signals für Qt-Integration
    gps_position_updated = Signal(float, float, float)  # lat, lon, alt
    attitude_updated = Signal(float, float, float)      # roll, pitch, yaw
    battery_updated = Signal(float)                     # battery_percent
    flight_mode_changed = Signal(str)
    armed_status_changed = Signal(bool)
    ground_speed_updated = Signal(float)
    altitude_updated = Signal(float)
    heading_updated = Signal(float)
    air_speed_updated = Signal(float)
    climb_rate_updated = Signal(float)
    gps_fix_updated = Signal(int)                       # gps_fix_type
    satellite_count_updated = Signal(int)
    vibration_updated = Signal(float, float, float)     # x, y, z vibration
    temperature_updated = Signal(float)                 # temperature
    
    def __init__(self, vehicle: Vehicle, connector, parent=None):
        super().__init__(parent)
        self.vehicle = vehicle
        self.connector = connector
        self.callbacks_registered = False
        
        # Rate-Limiting Konfiguration
        self.update_rates = {
            'gps': 1.0,      # 1 Hz
            'attitude': 5.0,  # 5 Hz
            'battery': 0.2,   # 5 Sekunden
            'vfr_hud': 2.0,   # 2 Hz
            'gps_raw': 1.0,   # 1 Hz
            'sys_status': 0.2, # 5 Sekunden
            'vibration': 1.0,  # 1 Hz
            'temperature': 0.5 # 2 Sekunden
        }
        
        # Cache für letzte Updates
        self.last_update = {}
        self.telemetry_cache = {}
        
        # Callback-Referenzen (verhindert Garbage Collection)
        self._callbacks = []
        
    def setup_telemetry_callbacks(self):
        """Registriert alle Telemetrie-Callbacks mit Rate-Limiting"""
        if self.callbacks_registered:
            return
            
        # GPS-Position (GPS_RAW_INT)
        @self.vehicle.on_message('GPS_RAW_INT')
        def gps_callback(self, name, message):
            current_time = time.time()
            if DroneKitUtils.rate_limit(current_time, 
                                      self.last_update.get('gps', 0), 
                                      self.update_rates['gps']):
                lat = message.lat / 1e7
                lon = message.lon / 1e7
                alt = message.alt / 1000.0
                
                self.telemetry_cache['gps'] = (lat, lon, alt)
                self.gps_position_updated.emit(lat, lon, alt)
                self.last_update['gps'] = current_time
                
                # GPS-Fix und Satelliten-Count
                gps_fix = message.fix_type
                satellites = message.satellites_visible
                self.telemetry_cache['gps_fix'] = gps_fix
                self.telemetry_cache['satellites'] = satellites
                self.gps_fix_updated.emit(gps_fix)
                self.satellite_count_updated.emit(satellites)
        
        # Attitude
        @self.vehicle.on_message('ATTITUDE')
        def attitude_callback(self, name, message):
            current_time = time.time()
            if DroneKitUtils.rate_limit(current_time, 
                                      self.last_update.get('attitude', 0), 
                                      self.update_rates['attitude']):
                roll = math.degrees(message.roll)
                pitch = math.degrees(message.pitch)
                yaw = math.degrees(message.yaw)
                
                self.telemetry_cache['attitude'] = (roll, pitch, yaw)
                self.attitude_updated.emit(roll, pitch, yaw)
                self.last_update['attitude'] = current_time
        
        # Battery (SYS_STATUS)
        @self.vehicle.on_message('SYS_STATUS')
        def battery_callback(self, name, message):
            current_time = time.time()
            if DroneKitUtils.rate_limit(current_time, 
                                      self.last_update.get('battery', 0), 
                                      self.update_rates['battery']):
                battery_percent = message.battery_remaining
                self.telemetry_cache['battery'] = battery_percent
                self.battery_updated.emit(battery_percent)
                self.last_update['battery'] = current_time
        
        # Flight Mode und Armed Status (HEARTBEAT)
        @self.vehicle.on_message('HEARTBEAT')
        def heartbeat_callback(self, name, message):
            # Flight mode aus custom_mode extrahieren
            flight_mode = DroneKitUtils.decode_flight_mode(message.custom_mode)
            self.telemetry_cache['flight_mode'] = flight_mode
            self.flight_mode_changed.emit(flight_mode)
            
            # Armed status
            armed = bool(message.system_status == 3)  # MAV_STATE_ACTIVE
            self.telemetry_cache['armed'] = armed
            self.armed_status_changed.emit(armed)
            
            # Heartbeat für Connection Manager
            if hasattr(self.connector, 'connection_manager'):
                self.connector.connection_manager.update_heartbeat()
        
        # Ground Speed, Altitude, Heading (VFR_HUD)
        @self.vehicle.on_message('VFR_HUD')
        def vfr_hud_callback(self, name, message):
            current_time = time.time()
            if DroneKitUtils.rate_limit(current_time, 
                                      self.last_update.get('vfr_hud', 0), 
                                      self.update_rates['vfr_hud']):
                ground_speed = message.groundspeed
                altitude = message.alt
                heading = message.heading
                air_speed = message.airspeed
                climb_rate = message.climb
                
                self.telemetry_cache['ground_speed'] = ground_speed
                self.telemetry_cache['altitude'] = altitude
                self.telemetry_cache['heading'] = heading
                self.telemetry_cache['air_speed'] = air_speed
                self.telemetry_cache['climb_rate'] = climb_rate
                
                self.ground_speed_updated.emit(ground_speed)
                self.altitude_updated.emit(altitude)
                self.heading_updated.emit(heading)
                self.air_speed_updated.emit(air_speed)
                self.climb_rate_updated.emit(climb_rate)
                self.last_update['vfr_hud'] = current_time
        
        # Vibration
        @self.vehicle.on_message('VIBRATION')
        def vibration_callback(self, name, message):
            current_time = time.time()
            if DroneKitUtils.rate_limit(current_time, 
                                      self.last_update.get('vibration', 0), 
                                      self.update_rates['vibration']):
                vibration_x = message.vibration_x
                vibration_y = message.vibration_y
                vibration_z = message.vibration_z
                
                self.telemetry_cache['vibration'] = (vibration_x, vibration_y, vibration_z)
                self.vibration_updated.emit(vibration_x, vibration_y, vibration_z)
                self.last_update['vibration'] = current_time
        
        # Temperature (falls verfügbar)
        @self.vehicle.on_message('SCALED_PRESSURE')
        def temperature_callback(self, name, message):
            current_time = time.time()
            if DroneKitUtils.rate_limit(current_time, 
                                      self.last_update.get('temperature', 0), 
                                      self.update_rates['temperature']):
                temperature = message.temperature / 100.0  # Convert from centidegrees
                self.telemetry_cache['temperature'] = temperature
                self.temperature_updated.emit(temperature)
                self.last_update['temperature'] = current_time
        
        # Callbacks speichern (verhindert Garbage Collection)
        self._callbacks = [
            gps_callback, attitude_callback, battery_callback, 
            heartbeat_callback, vfr_hud_callback, vibration_callback,
            temperature_callback
        ]
        
        self.callbacks_registered = True
    
    def get_telemetry_data(self) -> Dict[str, Any]:
        """Gibt alle aktuellen Telemetrie-Daten zurück"""
        return self.telemetry_cache.copy()
    
    def get_specific_telemetry(self, data_type: str) -> Any:
        """Gibt spezifische Telemetrie-Daten zurück"""
        return self.telemetry_cache.get(data_type)
    
    def set_update_rate(self, data_type: str, rate: float):
        """Setzt Update-Rate für spezifischen Telemetrie-Typ"""
        if data_type in self.update_rates:
            self.update_rates[data_type] = rate
    
    def get_update_rates(self) -> Dict[str, float]:
        """Gibt alle Update-Rates zurück"""
        return self.update_rates.copy()
    
    def clear_telemetry_cache(self):
        """Löscht Telemetrie-Cache"""
        self.telemetry_cache.clear()
        self.last_update.clear()
    
    def get_telemetry_summary(self) -> Dict[str, Any]:
        """Gibt Telemetrie-Zusammenfassung zurück"""
        summary = {}
        
        # GPS
        if 'gps' in self.telemetry_cache:
            lat, lon, alt = self.telemetry_cache['gps']
            summary['gps'] = {
                'position': DroneKitUtils.format_coordinate(lat, lon),
                'altitude': DroneKitUtils.format_altitude(alt),
                'fix_type': self.telemetry_cache.get('gps_fix', 0),
                'satellites': self.telemetry_cache.get('satellites', 0)
            }
        
        # Attitude
        if 'attitude' in self.telemetry_cache:
            roll, pitch, yaw = self.telemetry_cache['attitude']
            summary['attitude'] = {
                'roll': f"{roll:.1f}°",
                'pitch': f"{pitch:.1f}°",
                'yaw': f"{yaw:.1f}°"
            }
        
        # Flight Status
        summary['flight_status'] = {
            'mode': self.telemetry_cache.get('flight_mode', 'UNKNOWN'),
            'armed': self.telemetry_cache.get('armed', False),
            'battery': DroneKitUtils.format_battery(self.telemetry_cache.get('battery', 0))
        }
        
        # Speed and Position
        summary['speed_position'] = {
            'ground_speed': DroneKitUtils.format_speed(self.telemetry_cache.get('ground_speed', 0)),
            'air_speed': DroneKitUtils.format_speed(self.telemetry_cache.get('air_speed', 0)),
            'altitude': DroneKitUtils.format_altitude(self.telemetry_cache.get('altitude', 0)),
            'heading': f"{self.telemetry_cache.get('heading', 0):.1f}°",
            'climb_rate': f"{self.telemetry_cache.get('climb_rate', 0):.1f} m/s"
        }
        
        return summary
    
    def remove_callbacks(self):
        """Entfernt alle registrierten Callbacks"""
        if hasattr(self.vehicle, 'remove_all_callbacks'):
            self.vehicle.remove_all_callbacks()
        
        self._callbacks.clear()
        self.callbacks_registered = False 