"""
Telemetrie-Manager für die Flugsteuerung.
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum
from PySide6.QtCore import QObject, Signal

@dataclass
class TelemetryData:
    """Telemetrie-Daten"""
    position: Dict[str, float]
    attitude: Dict[str, float]
    velocity: Dict[str, float]
    battery: Dict[str, float]
    gps: Dict[str, Any]
    rc: Dict[str, float]

class TelemetryManager(QObject):
    """Manager für Telemetrie-Daten"""
    
    # Signale
    data_received = Signal(TelemetryData)
    error_occurred = Signal(str)
    
    def __init__(self):
        """Initialisiert den Telemetrie-Manager"""
        super().__init__()
        self._data = TelemetryData(
            position={"lat": 0.0, "lon": 0.0, "alt": 0.0},
            attitude={"roll": 0.0, "pitch": 0.0, "yaw": 0.0},
            velocity={"vx": 0.0, "vy": 0.0, "vz": 0.0},
            battery={"voltage": 0.0, "current": 0.0, "remaining": 0.0},
            gps={"fix": 0, "satellites": 0, "hdop": 0.0},
            rc={"ch1": 0.0, "ch2": 0.0, "ch3": 0.0, "ch4": 0.0}
        )
        
    def get_data(self) -> TelemetryData:
        """Gibt die aktuellen Telemetrie-Daten zurück"""
        return self._data
        
    def update_data(self, data: TelemetryData):
        """Aktualisiert die Telemetrie-Daten"""
        self._data = data
        self.data_received.emit(data)
        
    def get_position(self) -> Dict[str, float]:
        """Gibt die aktuelle Position zurück"""
        return self._data.position
        
    def get_attitude(self) -> Dict[str, float]:
        """Gibt die aktuelle Attitude zurück"""
        return self._data.attitude
        
    def get_velocity(self) -> Dict[str, float]:
        """Gibt die aktuelle Geschwindigkeit zurück"""
        return self._data.velocity
        
    def get_battery(self) -> Dict[str, float]:
        """Gibt die aktuellen Batterie-Daten zurück"""
        return self._data.battery
        
    def get_gps(self) -> Dict[str, Any]:
        """Gibt die aktuellen GPS-Daten zurück"""
        return self._data.gps
        
    def get_rc(self) -> Dict[str, float]:
        """Gibt die aktuellen RC-Daten zurück"""
        return self._data.rc 