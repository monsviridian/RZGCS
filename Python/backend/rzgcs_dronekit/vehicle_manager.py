"""
DroneKit Vehicle Manager - Verwaltet Fahrzeug-Informationen und Status
"""

import time
from typing import Dict, Any, Optional
from PySide6.QtCore import QObject, Signal

# DroneKit-Imports
# External DroneKit import - fixed to avoid circular imports
import dronekit as dronekit_external  # Externe DroneKit-Bibliothek
Vehicle = dronekit_external.Vehicle  # Aus externer DroneKit-Bibliothek

from .utils import DroneKitUtils

class DroneKitVehicleManager(QObject):
    """Verwaltet Fahrzeug-Informationen und Status"""
    
    # Signals
    vehicle_info_updated = Signal(dict)
    system_status_changed = Signal(str)
    vehicle_ready_changed = Signal(bool)
    vehicle_log = Signal(str)
    
    def __init__(self, vehicle: Vehicle, connector, parent=None):
        super().__init__(parent)
        self.vehicle = vehicle
        self.connector = connector
        self.vehicle_info = {}
        self.system_status = "UNKNOWN"
        self.is_ready = False
        
    def update_vehicle_info(self):
        """Aktualisiert Fahrzeug-Informationen"""
        try:
            # Basis-Informationen
            info = {
                'system_id': getattr(self.vehicle, 'system_id', 0),
                'component_id': getattr(self.vehicle, 'component_id', 0),
                'autopilot_type': getattr(self.vehicle, 'autopilot_type', 'UNKNOWN'),
                'vehicle_type': getattr(self.vehicle, 'vehicle_type', 'UNKNOWN'),
                'is_armable': getattr(self.vehicle, 'is_armable', False),
                'is_armed': getattr(self.vehicle, 'armed', False),
                'mode': getattr(self.vehicle.mode, 'name', 'UNKNOWN'),
                'location': self._get_location_info(),
                'attitude': self._get_attitude_info(),
                'velocity': self._get_velocity_info(),
                'gps': self._get_gps_info(),
                'battery': self._get_battery_info(),
                'system_status': self._get_system_status(),
                'capabilities': self._get_capabilities(),
                'firmware_version': self._get_firmware_version(),
                'hardware_version': self._get_hardware_version(),
                'software_version': self._get_software_version()
            }
            
            self.vehicle_info = info
            self.vehicle_info_updated.emit(info)
            
            # System-Status prüfen
            new_status = info['system_status']
            if new_status != self.system_status:
                self.system_status = new_status
                self.system_status_changed.emit(new_status)
            
            # Ready-Status prüfen
            new_ready = info['is_armable']
            if new_ready != self.is_ready:
                self.is_ready = new_ready
                self.vehicle_ready_changed.emit(new_ready)
            
        except Exception as e:
            self.vehicle_log.emit(f"Vehicle info update failed: {str(e)}")
    
    def _get_location_info(self) -> Dict[str, Any]:
        """Gibt Standort-Informationen zurück"""
        try:
            location = self.vehicle.location
            return {
                'global_frame': {
                    'lat': getattr(location.global_frame, 'lat', 0),
                    'lon': getattr(location.global_frame, 'lon', 0),
                    'alt': getattr(location.global_frame, 'alt', 0)
                },
                'global_relative_frame': {
                    'lat': getattr(location.global_relative_frame, 'lat', 0),
                    'lon': getattr(location.global_relative_frame, 'lon', 0),
                    'alt': getattr(location.global_relative_frame, 'alt', 0)
                },
                'local_frame': {
                    'north': getattr(location.local_frame, 'north', 0),
                    'east': getattr(location.local_frame, 'east', 0),
                    'down': getattr(location.local_frame, 'down', 0)
                }
            }
        except:
            return {
                'global_frame': {'lat': 0, 'lon': 0, 'alt': 0},
                'global_relative_frame': {'lat': 0, 'lon': 0, 'alt': 0},
                'local_frame': {'north': 0, 'east': 0, 'down': 0}
            }
    
    def _get_attitude_info(self) -> Dict[str, Any]:
        """Gibt Attitude-Informationen zurück"""
        try:
            attitude = self.vehicle.attitude
            return {
                'roll': getattr(attitude, 'roll', 0),
                'pitch': getattr(attitude, 'pitch', 0),
                'yaw': getattr(attitude, 'yaw', 0),
                'rollspeed': getattr(attitude, 'rollspeed', 0),
                'pitchspeed': getattr(attitude, 'pitchspeed', 0),
                'yawspeed': getattr(attitude, 'yawspeed', 0)
            }
        except:
            return {
                'roll': 0, 'pitch': 0, 'yaw': 0,
                'rollspeed': 0, 'pitchspeed': 0, 'yawspeed': 0
            }
    
    def _get_velocity_info(self) -> Dict[str, Any]:
        """Gibt Geschwindigkeits-Informationen zurück"""
        try:
            velocity = self.vehicle.velocity
            return {
                'north': getattr(velocity, 'north', 0),
                'east': getattr(velocity, 'east', 0),
                'down': getattr(velocity, 'down', 0)
            }
        except:
            return {'north': 0, 'east': 0, 'down': 0}
    
    def _get_gps_info(self) -> Dict[str, Any]:
        """Gibt GPS-Informationen zurück"""
        try:
            gps = self.vehicle.gps_0
            return {
                'fix_type': getattr(gps, 'fix_type', 0),
                'satellites_visible': getattr(gps, 'satellites_visible', 0),
                'eph': getattr(gps, 'eph', 0),
                'epv': getattr(gps, 'epv', 0),
                'hdop': getattr(gps, 'hdop', 0),
                'vdop': getattr(gps, 'vdop', 0)
            }
        except:
            return {
                'fix_type': 0, 'satellites_visible': 0,
                'eph': 0, 'epv': 0, 'hdop': 0, 'vdop': 0
            }
    
    def _get_battery_info(self) -> Dict[str, Any]:
        """Gibt Batterie-Informationen zurück"""
        try:
            battery = self.vehicle.battery
            return {
                'level': getattr(battery, 'level', 0),
                'voltage': getattr(battery, 'voltage', 0),
                'current': getattr(battery, 'current', 0)
            }
        except:
            return {'level': 0, 'voltage': 0, 'current': 0}
    
    def _get_system_status(self) -> str:
        """Gibt System-Status zurück"""
        try:
            status_mapping = {
                0: "UNINIT",
                1: "BOOT",
                2: "CALIBRATING",
                3: "ACTIVE",
                4: "CRITICAL",
                5: "EMERGENCY",
                6: "POWEROFF",
                7: "FLIGHT_TERMINATION"
            }
            status_code = getattr(self.vehicle, 'system_status', 0)
            return status_mapping.get(status_code, "UNKNOWN")
        except:
            return "UNKNOWN"
    
    def _get_capabilities(self) -> Dict[str, bool]:
        """Gibt Fahrzeug-Capabilities zurück"""
        try:
            return {
                'is_armable': getattr(self.vehicle, 'is_armable', False),
                'is_guided': hasattr(self.vehicle, 'simple_goto'),
                'is_guided_mode_enabled': getattr(self.vehicle, 'is_guided_mode_enabled', False),
                'has_gps': hasattr(self.vehicle, 'gps_0'),
                'has_battery': hasattr(self.vehicle, 'battery'),
                'has_attitude': hasattr(self.vehicle, 'attitude'),
                'has_velocity': hasattr(self.vehicle, 'velocity'),
                'has_location': hasattr(self.vehicle, 'location'),
                'has_parameters': hasattr(self.vehicle, 'parameters'),
                'has_commands': hasattr(self.vehicle, 'commands')
            }
        except:
            return {
                'is_armable': False,
                'is_guided': False,
                'is_guided_mode_enabled': False,
                'has_gps': False,
                'has_battery': False,
                'has_attitude': False,
                'has_velocity': False,
                'has_location': False,
                'has_parameters': False,
                'has_commands': False
            }
    
    def _get_firmware_version(self) -> Dict[str, Any]:
        """Gibt Firmware-Version zurück"""
        try:
            version = self.vehicle.version
            return {
                'major': getattr(version, 'major', 0),
                'minor': getattr(version, 'minor', 0),
                'patch': getattr(version, 'patch', 0),
                'release_type': getattr(version, 'release_type', 'UNKNOWN'),
                'release_version': getattr(version, 'release_version', 'UNKNOWN')
            }
        except:
            return {
                'major': 0, 'minor': 0, 'patch': 0,
                'release_type': 'UNKNOWN', 'release_version': 'UNKNOWN'
            }
    
    def _get_hardware_version(self) -> str:
        """Gibt Hardware-Version zurück"""
        try:
            return getattr(self.vehicle, 'hardware_version', 'UNKNOWN')
        except:
            return "UNKNOWN"
    
    def _get_software_version(self) -> str:
        """Gibt Software-Version zurück"""
        try:
            return getattr(self.vehicle, 'software_version', 'UNKNOWN')
        except:
            return "UNKNOWN"
    
    def get_vehicle_info(self) -> Dict[str, Any]:
        """Gibt aktuelle Fahrzeug-Informationen zurück"""
        return self.vehicle_info.copy()
    
    def get_system_status(self) -> str:
        """Gibt aktuellen System-Status zurück"""
        return self.system_status
    
    def is_vehicle_ready(self) -> bool:
        """Prüft ob Fahrzeug bereit ist"""
        return self.is_ready
    
    def get_vehicle_summary(self) -> Dict[str, Any]:
        """Gibt Fahrzeug-Zusammenfassung zurück"""
        return {
            'system_id': self.vehicle_info.get('system_id', 0),
            'autopilot_type': self.vehicle_info.get('autopilot_type', 'UNKNOWN'),
            'vehicle_type': self.vehicle_info.get('vehicle_type', 'UNKNOWN'),
            'firmware_version': self.vehicle_info.get('firmware_version', {}),
            'system_status': self.system_status,
            'is_ready': self.is_ready,
            'is_armed': self.vehicle_info.get('is_armed', False),
            'mode': self.vehicle_info.get('mode', 'UNKNOWN'),
            'capabilities': self.vehicle_info.get('capabilities', {})
        }
    
    def get_vehicle_health(self) -> Dict[str, Any]:
        """Gibt Fahrzeug-Gesundheitsstatus zurück"""
        try:
            return {
                'gps_health': self._get_gps_health(),
                'battery_health': self._get_battery_health(),
                'system_health': self._get_system_health(),
                'overall_health': self._get_overall_health()
            }
        except:
            return {
                'gps_health': 'UNKNOWN',
                'battery_health': 'UNKNOWN',
                'system_health': 'UNKNOWN',
                'overall_health': 'UNKNOWN'
            }
    
    def _get_gps_health(self) -> str:
        """Bewertet GPS-Gesundheit"""
        try:
            gps_info = self.vehicle_info.get('gps', {})
            fix_type = gps_info.get('fix_type', 0)
            satellites = gps_info.get('satellites_visible', 0)
            
            if fix_type >= 3 and satellites >= 6:
                return "GOOD"
            elif fix_type >= 2 and satellites >= 4:
                return "FAIR"
            else:
                return "POOR"
        except:
            return "UNKNOWN"
    
    def _get_battery_health(self) -> str:
        """Bewertet Batterie-Gesundheit"""
        try:
            battery_info = self.vehicle_info.get('battery', {})
            level = battery_info.get('level', 0)
            voltage = battery_info.get('voltage', 0)
            
            if level > 50 and voltage > 3.5:
                return "GOOD"
            elif level > 20 and voltage > 3.2:
                return "FAIR"
            else:
                return "POOR"
        except:
            return "UNKNOWN"
    
    def _get_system_health(self) -> str:
        """Bewertet System-Gesundheit"""
        try:
            status = self.system_status
            if status == "ACTIVE":
                return "GOOD"
            elif status in ["CALIBRATING", "BOOT"]:
                return "FAIR"
            else:
                return "POOR"
        except:
            return "UNKNOWN"
    
    def _get_overall_health(self) -> str:
        """Bewertet Gesamt-Gesundheit"""
        try:
            gps_health = self._get_gps_health()
            battery_health = self._get_battery_health()
            system_health = self._get_system_health()
            
            health_scores = {
                'GOOD': 3,
                'FAIR': 2,
                'POOR': 1,
                'UNKNOWN': 0
            }
            
            avg_score = (health_scores[gps_health] + 
                        health_scores[battery_health] + 
                        health_scores[system_health]) / 3
            
            if avg_score >= 2.5:
                return "GOOD"
            elif avg_score >= 1.5:
                return "FAIR"
            else:
                return "POOR"
        except:
            return "UNKNOWN" 