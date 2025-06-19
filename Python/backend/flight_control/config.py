"""
Konfiguration für die Flugsteuerung.
Definiert die Konfigurationsparameter für die Flugsteuerung.
"""

from typing import Dict, Any
from dataclasses import dataclass, field

@dataclass
class ConnectionConfig:
    """Verbindungskonfiguration"""
    type: str = "SERIAL"  # Verbindungstyp
    port: str = "COM3"    # Port
    baudrate: int = 115200 # Baudrate
    timeout: float = 1.0  # Timeout in Sekunden
    
@dataclass
class FlightConfig:
    """Flugkonfiguration"""
    max_altitude: float = 100.0  # Maximale Höhe in Metern
    max_speed: float = 10.0      # Maximale Geschwindigkeit in m/s
    max_acceleration: float = 2.0 # Maximale Beschleunigung in m/s²
    max_angular_velocity: float = 45.0 # Maximale Winkelgeschwindigkeit in Grad/s
    
@dataclass
class MissionConfig:
    """Missionskonfiguration"""
    default_altitude: float = 50.0  # Standardhöhe in Metern
    default_speed: float = 5.0      # Standardgeschwindigkeit in m/s
    default_loiter_time: float = 10.0 # Standardwartezeit in Sekunden
    default_loiter_radius: float = 10.0 # Standardkreisradius in Metern
    
@dataclass
class TelemetryConfig:
    """Telemetriekonfiguration"""
    update_rate: float = 0.1  # Aktualisierungsrate in Sekunden
    max_history: int = 1000   # Maximale Anzahl der gespeicherten Datenpunkte
    
@dataclass
class Config:
    """Hauptkonfiguration"""
    connection: ConnectionConfig = field(default_factory=ConnectionConfig)
    flight: FlightConfig = field(default_factory=FlightConfig)
    mission: MissionConfig = field(default_factory=MissionConfig)
    telemetry: TelemetryConfig = field(default_factory=TelemetryConfig)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Konvertiert die Konfiguration in ein Dictionary.
        
        Returns:
            Dictionary mit den Konfigurationsparametern
        """
        return {
            "connection": {
                "type": self.connection.type,
                "port": self.connection.port,
                "baudrate": self.connection.baudrate,
                "timeout": self.connection.timeout
            },
            "flight": {
                "max_altitude": self.flight.max_altitude,
                "max_speed": self.flight.max_speed,
                "max_acceleration": self.flight.max_acceleration,
                "max_angular_velocity": self.flight.max_angular_velocity
            },
            "mission": {
                "default_altitude": self.mission.default_altitude,
                "default_speed": self.mission.default_speed,
                "default_loiter_time": self.mission.default_loiter_time,
                "default_loiter_radius": self.mission.default_loiter_radius
            },
            "telemetry": {
                "update_rate": self.telemetry.update_rate,
                "max_history": self.telemetry.max_history
            }
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Config':
        """
        Erstellt eine Konfiguration aus einem Dictionary.
        
        Args:
            data: Dictionary mit den Konfigurationsparametern
            
        Returns:
            Konfigurationsobjekt
        """
        return cls(
            connection=ConnectionConfig(
                type=data["connection"]["type"],
                port=data["connection"]["port"],
                baudrate=data["connection"]["baudrate"],
                timeout=data["connection"]["timeout"]
            ),
            flight=FlightConfig(
                max_altitude=data["flight"]["max_altitude"],
                max_speed=data["flight"]["max_speed"],
                max_acceleration=data["flight"]["max_acceleration"],
                max_angular_velocity=data["flight"]["max_angular_velocity"]
            ),
            mission=MissionConfig(
                default_altitude=data["mission"]["default_altitude"],
                default_speed=data["mission"]["default_speed"],
                default_loiter_time=data["mission"]["default_loiter_time"],
                default_loiter_radius=data["mission"]["default_loiter_radius"]
            ),
            telemetry=TelemetryConfig(
                update_rate=data["telemetry"]["update_rate"],
                max_history=data["telemetry"]["max_history"]
            )
        ) 