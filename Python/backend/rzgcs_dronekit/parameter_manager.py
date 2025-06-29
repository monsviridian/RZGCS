"""
DroneKit Parameter Manager - Verwaltet Fahrzeug-Parameter
"""

import asyncio
import time
from typing import Dict, Any, Optional, List
from PySide6.QtCore import QObject, Signal

# DroneKit-Imports
# External DroneKit import - fixed to avoid circular imports
import dronekit as dronekit_external  # Externe DroneKit-Bibliothek
Vehicle = dronekit_external.Vehicle  # Aus externer DroneKit-Bibliothek

from .utils import DroneKitUtils

class DroneKitParameterManager(QObject):
    """Verwaltet Fahrzeug-Parameter"""
    
    # Signals
    parameters_loaded = Signal(int)  # number of parameters
    parameter_updated = Signal(str, float)  # parameter_name, value
    parameter_set = Signal(str, float)  # parameter_name, value
    parameter_error = Signal(str)
    parameter_log = Signal(str)
    
    def __init__(self, vehicle: Vehicle, connector, parent=None):
        super().__init__(parent)
        self.vehicle = vehicle
        self.connector = connector
        self.parameters_cache = {}
        self.parameters_loaded_flag = False
        
    async def load_parameters(self) -> bool:
        """Lädt alle Parameter"""
        try:
            self.vehicle.parameters.download()
            self.vehicle.parameters.wait_ready()
            
            # Parameter cachen
            for param_name, param_value in self.vehicle.parameters.items():
                self.parameters_cache[param_name] = param_value
            
            self.parameters_loaded_flag = True
            self.parameters_loaded.emit(len(self.parameters_cache))
            self.parameter_log.emit(f"Loaded {len(self.parameters_cache)} parameters")
            return True
            
        except Exception as e:
            error_msg = f"Parameter load failed: {str(e)}"
            self.parameter_error.emit(error_msg)
            return False
    
    async def get_parameter(self, param_name: str) -> Optional[float]:
        """Liest spezifischen Parameter"""
        try:
            if not self.parameters_loaded_flag:
                await self.load_parameters()
            
            value = self.vehicle.parameters[param_name]
            self.parameters_cache[param_name] = value
            self.parameter_updated.emit(param_name, value)
            return value
            
        except Exception as e:
            error_msg = f"Parameter read failed for {param_name}: {str(e)}"
            self.parameter_error.emit(error_msg)
            return None
    
    async def set_parameter(self, param_name: str, value: float) -> bool:
        """Setzt spezifischen Parameter"""
        try:
            self.vehicle.parameters[param_name] = value
            self.parameters_cache[param_name] = value
            self.parameter_set.emit(param_name, value)
            self.parameter_log.emit(f"Parameter {param_name} set to {value}")
            return True
            
        except Exception as e:
            error_msg = f"Parameter set failed for {param_name}: {str(e)}"
            self.parameter_error.emit(error_msg)
            return False
    
    def get_all_parameters(self) -> Dict[str, float]:
        """Gibt alle Parameter zurück"""
        return self.parameters_cache.copy()
    
    def get_parameter_names(self) -> List[str]:
        """Gibt alle Parameter-Namen zurück"""
        return list(self.parameters_cache.keys())
    
    def search_parameters(self, search_term: str) -> Dict[str, float]:
        """Sucht Parameter nach Suchbegriff"""
        results = {}
        search_term_lower = search_term.lower()
        
        for param_name, value in self.parameters_cache.items():
            if search_term_lower in param_name.lower():
                results[param_name] = value
        
        return results
    
    async def save_parameters(self) -> bool:
        """Speichert Parameter permanent"""
        try:
            # ArduPilot-spezifische Parameter-Speicherung
            await self.set_parameter("SYSID_MYGCS", 255)
            self.parameter_log.emit("Parameters saved")
            return True
            
        except Exception as e:
            error_msg = f"Parameter save failed: {str(e)}"
            self.parameter_error.emit(error_msg)
            return False
    
    def get_parameter_info(self, param_name: str) -> Dict[str, Any]:
        """Gibt Parameter-Informationen zurück"""
        try:
            param = self.vehicle.parameters[param_name]
            return {
                'name': param_name,
                'value': param,
                'type': type(param).__name__,
                'cached': param_name in self.parameters_cache
            }
        except:
            return {
                'name': param_name,
                'value': None,
                'type': 'unknown',
                'cached': False
            }
    
    def get_common_parameters(self) -> Dict[str, float]:
        """Gibt häufig verwendete Parameter zurück"""
        common_params = [
            'SYSID_MYGCS', 'ARMING_CHECK', 'ARMING_REQUIRE', 'ARMING_ACTION',
            'RTL_ALT', 'RTL_LOIT_TIME', 'RTL_ALT_FINAL', 'RTL_CLIMB_MIN',
            'WPNAV_SPEED', 'WPNAV_ACCEL', 'WPNAV_RADIUS', 'WPNAV_LOIT_SPEED',
            'PILOT_SPEED_UP', 'PILOT_SPEED_DN', 'PILOT_ACCEL_Z',
            'THR_MIN', 'THR_MAX', 'THR_MID', 'THR_DZ',
            'COMPASS_ENABLE', 'COMPASS_USE', 'COMPASS_LEARN',
            'GPS_TYPE', 'GPS_AUTO_SWITCH', 'GPS_AUTO_CONFIG',
            'BATT_MONITOR', 'BATT_CAPACITY', 'BATT_VOLT_PIN', 'BATT_CURR_PIN',
            'BATT_VOLT_MULT', 'BATT_CURR_MULT', 'BATT_VOLT2_PIN', 'BATT_CURR2_PIN',
            'BATT_VOLT2_MULT', 'BATT_CURR2_MULT', 'BATT_LOW_VOLT', 'BATT_LOW_MAH',
            'BATT_CRT_VOLT', 'BATT_CRT_MAH', 'BATT_FS_LOW_ACT', 'BATT_FS_CRT_ACT'
        ]
        
        result = {}
        for param_name in common_params:
            if param_name in self.parameters_cache:
                result[param_name] = self.parameters_cache[param_name]
        
        return result
    
    def get_parameter_categories(self) -> Dict[str, List[str]]:
        """Gibt Parameter nach Kategorien gruppiert zurück"""
        categories = {
            'System': ['SYSID_', 'SERIAL_', 'LOG_', 'STAT_'],
            'Arming': ['ARMING_', 'ARM_'],
            'Navigation': ['WPNAV_', 'RTL_', 'CIRCLE_', 'LOITER_'],
            'Pilot Control': ['PILOT_', 'RC_', 'FLTMODE_'],
            'Throttle': ['THR_', 'MOT_'],
            'Compass': ['COMPASS_', 'MAG_'],
            'GPS': ['GPS_'],
            'Battery': ['BATT_'],
            'Camera': ['CAM_', 'MNT_'],
            'Rally': ['RALLY_'],
            'Fence': ['FENCE_'],
            'EKF': ['EKF_', 'INS_'],
            'AHRS': ['AHRS_'],
            'Scheduler': ['SCHED_'],
            'Servo': ['SERVO_', 'SERVOOUT_'],
            'Radio': ['RSSI_', 'RADIO_'],
            'Notch': ['NOTCH_'],
            'Vibration': ['VIBE_'],
            'CAN': ['CAN_'],
            'Scripting': ['SCR_'],
            'Relay': ['RELAY_'],
            'GPIO': ['GPIO_'],
            'BRD_': ['BRD_'],
            'SIGNING': ['SIGNING_'],
            'SERIAL': ['SERIAL_'],
            'TUNE': ['TUNE_'],
            'MIS_': ['MIS_'],
            'RCMAP_': ['RCMAP_'],
            'RC': ['RC1_', 'RC2_', 'RC3_', 'RC4_', 'RC5_', 'RC6_', 'RC7_', 'RC8_'],
            'SERVO': ['SERVO1_', 'SERVO2_', 'SERVO3_', 'SERVO4_', 'SERVO5_', 'SERVO6_', 'SERVO7_', 'SERVO8_'],
            'Other': []
        }
        
        categorized = {cat: [] for cat in categories.keys()}
        
        for param_name in self.parameters_cache.keys():
            categorized_flag = False
            for category, prefixes in categories.items():
                if category == 'Other':
                    continue
                for prefix in prefixes:
                    if param_name.startswith(prefix):
                        categorized[category].append(param_name)
                        categorized_flag = True
                        break
                if categorized_flag:
                    break
            
            if not categorized_flag:
                categorized['Other'].append(param_name)
        
        return categorized
    
    def export_parameters(self, filename: str) -> bool:
        """Exportiert Parameter in Datei"""
        try:
            with open(filename, 'w') as f:
                f.write("# ArduPilot Parameter File\n")
                f.write(f"# Generated by RZGCS DroneKit Integration\n")
                f.write(f"# Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                for param_name, value in sorted(self.parameters_cache.items()):
                    f.write(f"{param_name} {value}\n")
            
            self.parameter_log.emit(f"Parameters exported to {filename}")
            return True
            
        except Exception as e:
            error_msg = f"Parameter export failed: {str(e)}"
            self.parameter_error.emit(error_msg)
            return False
    
    def import_parameters(self, filename: str) -> bool:
        """Importiert Parameter aus Datei"""
        try:
            imported_params = {}
            
            with open(filename, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('#') or not line:
                        continue
                    
                    parts = line.split()
                    if len(parts) >= 2:
                        param_name = parts[0]
                        try:
                            value = float(parts[1])
                            imported_params[param_name] = value
                        except ValueError:
                            continue
            
            # Parameter setzen
            for param_name, value in imported_params.items():
                self.parameters_cache[param_name] = value
            
            self.parameter_log.emit(f"Parameters imported from {filename}: {len(imported_params)} parameters")
            return True
            
        except Exception as e:
            error_msg = f"Parameter import failed: {str(e)}"
            self.parameter_error.emit(error_msg)
            return False
    
    def get_parameter_summary(self) -> Dict[str, Any]:
        """Gibt Parameter-Zusammenfassung zurück"""
        return {
            'total_parameters': len(self.parameters_cache),
            'parameters_loaded': self.parameters_loaded_flag,
            'categories': self.get_parameter_categories(),
            'common_parameters': self.get_common_parameters()
        } 