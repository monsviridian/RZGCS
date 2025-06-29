"""
DroneKit Control Handler - Verwaltet direkte Steuerung der Drohne
"""

import asyncio
import time
import math
from typing import Optional, Tuple
from PySide6.QtCore import QObject, Signal

# DroneKit-Imports
# External DroneKit import - fixed to avoid circular imports
import dronekit as dronekit_external  # Externe DroneKit-Bibliothek
Vehicle = dronekit_external.Vehicle  # Aus externer DroneKit-Bibliothek
VehicleMode = dronekit_external.VehicleMode  # Aus externer DroneKit-Bibliothek
LocationGlobal = dronekit_external.LocationGlobal  # Aus externer DroneKit-Bibliothek
LocationGlobalRelative = dronekit_external.LocationGlobalRelative  # Aus externer DroneKit-Bibliothek

from pymavlink import mavutil

from .utils import DroneKitUtils

class DroneKitControlHandler(QObject):
    """Verwaltet direkte Steuerung der Drohne im GUIDED-Modus"""
    
    # Signals
    arm_status_changed = Signal(bool)
    takeoff_completed = Signal(float)  # altitude
    landing_completed = Signal()
    navigation_completed = Signal(float, float, float)  # lat, lon, alt
    control_error = Signal(str)
    control_log = Signal(str)
    
    def __init__(self, vehicle: Vehicle, connector, parent=None):
        super().__init__(parent)
        self.vehicle = vehicle
        self.connector = connector
        self.is_armed = False
        self.is_flying = False
        self.current_altitude = 0.0
        
    async def arm_disarm(self, arm: bool) -> bool:
        """Armt oder disarmed die Drohne"""
        try:
            if arm:
                # Pre-flight checks
                if not self.vehicle.is_armable:
                    raise ValueError("Vehicle not armable")
                
                # GUIDED-Modus aktivieren
                self.vehicle.mode = VehicleMode("GUIDED")
                await asyncio.sleep(1)
                
                # Arming
                self.vehicle.armed = True
                self.control_log.emit("Arming vehicle...")
                
                # Warten auf Armed-Status
                timeout = time.time() + 10
                while not self.vehicle.armed and time.time() < timeout:
                    await asyncio.sleep(0.1)
                
                if self.vehicle.armed:
                    self.is_armed = True
                    self.arm_status_changed.emit(True)
                    self.control_log.emit("Vehicle armed successfully")
                    return True
                else:
                    raise TimeoutError("Arming timeout")
            else:
                # Disarming
                self.vehicle.armed = False
                self.control_log.emit("Disarming vehicle...")
                
                # Warten auf Disarmed-Status
                timeout = time.time() + 10
                while self.vehicle.armed and time.time() < timeout:
                    await asyncio.sleep(0.1)
                
                if not self.vehicle.armed:
                    self.is_armed = False
                    self.arm_status_changed.emit(False)
                    self.control_log.emit("Vehicle disarmed successfully")
                    return True
                else:
                    raise TimeoutError("Disarming timeout")
                    
        except Exception as e:
            error_msg = f"Arm/Disarm failed: {str(e)}"
            self.control_error.emit(error_msg)
            return False
    
    async def takeoff(self, altitude: float) -> bool:
        """Takeoff auf spezifische Höhe"""
        try:
            # GUIDED-Modus prüfen
            if self.vehicle.mode.name != "GUIDED":
                self.vehicle.mode = VehicleMode("GUIDED")
                await asyncio.sleep(1)
            
            # Arming prüfen
            if not self.vehicle.armed:
                raise ValueError("Vehicle must be armed for takeoff")
            
            # Takeoff
            self.vehicle.simple_takeoff(altitude)
            self.control_log.emit(f"Takeoff to {altitude}m initiated")
            
            # Warten auf Takeoff-Abschluss
            timeout = time.time() + 60  # 60 Sekunden Timeout
            while time.time() < timeout:
                current_alt = self.vehicle.location.global_relative_frame.alt
                if current_alt >= altitude * 0.95:  # 95% der Zielhöhe
                    self.is_flying = True
                    self.current_altitude = current_alt
                    self.takeoff_completed.emit(current_alt)
                    self.control_log.emit(f"Takeoff completed at {current_alt:.1f}m")
                    return True
                await asyncio.sleep(0.5)
            
            raise TimeoutError("Takeoff timeout")
            
        except Exception as e:
            error_msg = f"Takeoff failed: {str(e)}"
            self.control_error.emit(error_msg)
            return False
    
    async def land(self) -> bool:
        """Landung initiieren"""
        try:
            self.vehicle.mode = VehicleMode("LAND")
            self.control_log.emit("Landing initiated")
            
            # Warten auf Landung
            timeout = time.time() + 120  # 2 Minuten Timeout
            while time.time() < timeout:
                if self.vehicle.location.global_relative_frame.alt < 0.5:
                    self.is_flying = False
                    self.landing_completed.emit()
                    self.control_log.emit("Landing completed")
                    return True
                await asyncio.sleep(0.5)
            
            raise TimeoutError("Landing timeout")
            
        except Exception as e:
            error_msg = f"Landing failed: {str(e)}"
            self.control_error.emit(error_msg)
            return False
    
    async def goto_position(self, lat: float, lon: float, alt: float) -> bool:
        """Navigation zu spezifischer Position"""
        try:
            # GUIDED-Modus prüfen
            if self.vehicle.mode.name != "GUIDED":
                self.vehicle.mode = VehicleMode("GUIDED")
                await asyncio.sleep(1)
            
            # Position setzen
            target_location = LocationGlobal(lat, lon, alt)
            self.vehicle.simple_goto(target_location)
            
            self.control_log.emit(f"Navigating to {lat:.6f}, {lon:.6f}, {alt}m")
            
            # Warten auf Ankunft
            timeout = time.time() + 300  # 5 Minuten Timeout
            while time.time() < timeout:
                current_location = self.vehicle.location.global_frame
                distance = self._calculate_distance(
                    current_location.lat, current_location.lon,
                    lat, lon
                )
                
                if distance < 5.0:  # 5 Meter Toleranz
                    self.navigation_completed.emit(lat, lon, alt)
                    self.control_log.emit("Navigation completed")
                    return True
                
                await asyncio.sleep(1)
            
            raise TimeoutError("Navigation timeout")
            
        except Exception as e:
            error_msg = f"Navigation failed: {str(e)}"
            self.control_error.emit(error_msg)
            return False
    
    async def goto_position_relative(self, north: float, east: float, down: float) -> bool:
        """Navigation zu relativer Position"""
        try:
            # GUIDED-Modus prüfen
            if self.vehicle.mode.name != "GUIDED":
                self.vehicle.mode = VehicleMode("GUIDED")
                await asyncio.sleep(1)
            
            # Relative Position setzen
            target_location = LocationGlobalRelative(north, east, down)
            self.vehicle.simple_goto(target_location)
            
            self.control_log.emit(f"Navigating relative: N{north}m, E{east}m, D{down}m")
            
            # Warten auf Ankunft
            timeout = time.time() + 300  # 5 Minuten Timeout
            while time.time() < timeout:
                current_location = self.vehicle.location.local_frame
                distance = math.sqrt(
                    (current_location.north - north)**2 +
                    (current_location.east - east)**2 +
                    (current_location.down - down)**2
                )
                
                if distance < 2.0:  # 2 Meter Toleranz
                    self.navigation_completed.emit(north, east, down)
                    self.control_log.emit("Relative navigation completed")
                    return True
                
                await asyncio.sleep(1)
            
            raise TimeoutError("Relative navigation timeout")
            
        except Exception as e:
            error_msg = f"Relative navigation failed: {str(e)}"
            self.control_error.emit(error_msg)
            return False
    
    async def set_velocity(self, vx: float, vy: float, vz: float) -> bool:
        """Geschwindigkeitssteuerung"""
        try:
            # GUIDED-Modus prüfen
            if self.vehicle.mode.name != "GUIDED":
                self.vehicle.mode = VehicleMode("GUIDED")
                await asyncio.sleep(1)
            
            # MAVLink-Nachricht für Geschwindigkeitssteuerung
            msg = self.vehicle.message_factory.set_position_target_local_ned_encode(
                0,       # time_boot_ms
                0, 0,    # target system, target component
                mavutil.mavlink.MAV_FRAME_LOCAL_NED,  # frame
                0b0000111111000111,  # type_mask (only velocities)
                0, 0, 0,  # x, y, z positions
                vx, vy, vz,  # x, y, z velocities
                0, 0, 0,  # x, y, z acceleration
                0, 0)     # yaw, yaw_rate
            
            self.vehicle.send_mavlink(msg)
            self.control_log.emit(f"Velocity set: VX={vx:.1f}, VY={vy:.1f}, VZ={vz:.1f} m/s")
            return True
            
        except Exception as e:
            error_msg = f"Velocity control failed: {str(e)}"
            self.control_error.emit(error_msg)
            return False
    
    async def set_velocity_body(self, vx: float, vy: float, vz: float) -> bool:
        """Geschwindigkeitssteuerung im Body-Frame"""
        try:
            # GUIDED-Modus prüfen
            if self.vehicle.mode.name != "GUIDED":
                self.vehicle.mode = VehicleMode("GUIDED")
                await asyncio.sleep(1)
            
            # MAVLink-Nachricht für Body-Frame Geschwindigkeitssteuerung
            msg = self.vehicle.message_factory.set_position_target_local_ned_encode(
                0,       # time_boot_ms
                0, 0,    # target system, target component
                mavutil.mavlink.MAV_FRAME_BODY_NED,  # frame (Body-Frame)
                0b0000111111000111,  # type_mask (only velocities)
                0, 0, 0,  # x, y, z positions
                vx, vy, vz,  # x, y, z velocities
                0, 0, 0,  # x, y, z acceleration
                0, 0)     # yaw, yaw_rate
            
            self.vehicle.send_mavlink(msg)
            self.control_log.emit(f"Body velocity set: VX={vx:.1f}, VY={vy:.1f}, VZ={vz:.1f} m/s")
            return True
            
        except Exception as e:
            error_msg = f"Body velocity control failed: {str(e)}"
            self.control_error.emit(error_msg)
            return False
    
    async def set_yaw(self, yaw: float, relative: bool = False) -> bool:
        """Yaw-Steuerung"""
        try:
            # GUIDED-Modus prüfen
            if self.vehicle.mode.name != "GUIDED":
                self.vehicle.mode = VehicleMode("GUIDED")
                await asyncio.sleep(1)
            
            # Yaw-Nachricht senden
            msg = self.vehicle.message_factory.command_long_encode(
                0, 0,    # target system, target component
                mavutil.mavlink.MAV_CMD_CONDITION_YAW,  # command
                0,       # confirmation
                yaw,     # param1: yaw angle
                0,       # param2: yaw angular rate
                1 if relative else 0,  # param3: relative angle
                0,       # param4: direction
                0, 0, 0  # param5-7: unused
            )
            
            self.vehicle.send_mavlink(msg)
            self.control_log.emit(f"Yaw set to {yaw:.1f}° ({'relative' if relative else 'absolute'})")
            return True
            
        except Exception as e:
            error_msg = f"Yaw control failed: {str(e)}"
            self.control_error.emit(error_msg)
            return False
    
    async def return_to_launch(self) -> bool:
        """Return to Launch"""
        try:
            self.vehicle.mode = VehicleMode("RTL")
            self.control_log.emit("Return to Launch initiated")
            return True
        except Exception as e:
            error_msg = f"RTL failed: {str(e)}"
            self.control_error.emit(error_msg)
            return False
    
    async def loiter(self, radius: float = 50.0) -> bool:
        """Loiter-Modus aktivieren"""
        try:
            self.vehicle.mode = VehicleMode("LOITER")
            self.control_log.emit(f"Loiter mode activated (radius: {radius}m)")
            return True
        except Exception as e:
            error_msg = f"Loiter failed: {str(e)}"
            self.control_error.emit(error_msg)
            return False
    
    def get_control_status(self) -> dict:
        """Gibt aktuellen Steuerungsstatus zurück"""
        return {
            'armed': self.is_armed,
            'flying': self.is_flying,
            'current_altitude': self.current_altitude,
            'mode': self.vehicle.mode.name if self.vehicle else "UNKNOWN",
            'location': {
                'lat': self.vehicle.location.global_frame.lat if self.vehicle else 0,
                'lon': self.vehicle.location.global_frame.lon if self.vehicle else 0,
                'alt': self.vehicle.location.global_frame.alt if self.vehicle else 0
            }
        }
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Berechnet Distanz zwischen zwei GPS-Koordinaten"""
        R = 6371000  # Erdradius in Metern
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat / 2) * math.sin(delta_lat / 2) +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lon / 2) * math.sin(delta_lon / 2))
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c 