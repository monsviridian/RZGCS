"""
Flight ViewModel für die Flugsteuerung.
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum
from PySide6.QtCore import QObject, Signal, Property, Slot

from ..services.telemetry_service import TelemetryService
from ..services.connection_service import ConnectionService
from ..enums import FlightMode, ControlMode, ConnectionStatus

@dataclass
class FlightState:
    """Flugzustand"""
    mode: FlightMode
    control_mode: ControlMode
    connection_status: ConnectionStatus
    armed: bool
    position: Dict[str, float]
    attitude: Dict[str, float]
    velocity: Dict[str, float]
    battery: Dict[str, float]
    gps: Dict[str, Any]
    rc: Dict[str, float]

class FlightViewModel(QObject):
    """ViewModel für die Flugsteuerung"""
    
    # Signale
    stateChanged = Signal(FlightState)
    errorOccurred = Signal(str)
    
    def __init__(self, telemetry_service: TelemetryService, connection_service: ConnectionService):
        """Initialisiert das Flight ViewModel"""
        super().__init__()
        self.telemetry_service = telemetry_service
        self.connection_service = connection_service
        self._state = FlightState(
            mode=FlightMode.UNKNOWN,
            control_mode=ControlMode.UNKNOWN,
            connection_status=ConnectionStatus.DISCONNECTED,
            armed=False,
            position={"lat": 0.0, "lon": 0.0, "alt": 0.0},
            attitude={"roll": 0.0, "pitch": 0.0, "yaw": 0.0},
            velocity={"vx": 0.0, "vy": 0.0, "vz": 0.0},
            battery={"voltage": 0.0, "current": 0.0, "remaining": 0.0},
            gps={"fix": 0, "satellites": 0, "hdop": 0.0},
            rc={"ch1": 0.0, "ch2": 0.0, "ch3": 0.0, "ch4": 0.0}
        )
        
    def get_state(self) -> FlightState:
        """Gibt den aktuellen Flugzustand zurück"""
        return self._state
        
    @Slot()
    def connect(self):
        """Stellt die Verbindung her"""
        self.connection_service.connect()
        
    @Slot()
    def disconnect(self):
        """Trennt die Verbindung"""
        self.connection_service.disconnect()
        
    @Slot()
    def arm(self):
        """Armt den Copter"""
        # TODO: Implementiere Arming
        pass
        
    @Slot()
    def disarm(self):
        """Disarmt den Copter"""
        # TODO: Implementiere Disarming
        pass
        
    @Slot(float)
    def set_throttle(self, throttle: float):
        """Setzt den Schub"""
        # TODO: Implementiere Schub-Steuerung
        pass
        
    @Slot(float)
    def set_roll(self, roll: float):
        """Setzt den Roll-Winkel"""
        # TODO: Implementiere Roll-Steuerung
        pass
        
    @Slot(float)
    def set_pitch(self, pitch: float):
        """Setzt den Pitch-Winkel"""
        # TODO: Implementiere Pitch-Steuerung
        pass
        
    @Slot(float)
    def set_yaw(self, yaw: float):
        """Setzt den Yaw-Winkel"""
        # TODO: Implementiere Yaw-Steuerung
        pass 