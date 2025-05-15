from pydantic import BaseSettings, Field
from typing import Dict, Optional
import json
import os

class DroneSettings(BaseSettings):
    """
    Konfigurationseinstellungen für die Drohnensteuerung.
    Verwendet Pydantic für Validierung und Umgebungsvariablen.
    """
    
    # Verbindungseinstellungen
    default_port: str = Field("COM8", description="Standard serieller Port")
    default_baudrate: int = Field(57600, description="Standard Baudrate")
    connection_timeout: float = Field(5.0, description="Verbindungs-Timeout in Sekunden")
    
    # Sensor-Einstellungen
    sensor_update_rate: float = Field(0.1, description="Sensor-Aktualisierungsrate in Sekunden")
    sensor_value_precision: int = Field(2, description="Nachkommastellen für Sensorwerte")
    
    # Logging-Einstellungen
    log_level: str = Field("INFO", description="Log-Level (DEBUG, INFO, WARNING, ERROR)")
    log_file: Optional[str] = Field(None, description="Pfad zur Log-Datei")
    
    # Motor-Einstellungen
    motor_test_duration: float = Field(2.0, description="Standarddauer für Motortests in Sekunden")
    max_motor_throttle: float = Field(0.5, description="Maximaler Motorschub (0-1)")
    
    # MAVLink-Einstellungen
    mavlink_system_id: int = Field(1, description="MAVLink System ID")
    mavlink_component_id: int = Field(1, description="MAVLink Komponenten ID")
    
    @classmethod
    def load_from_file(cls, filepath: str) -> 'DroneSettings':
        """Lädt die Konfiguration aus einer JSON-Datei."""
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return cls(**json.load(f))
        return cls()
    
    def save_to_file(self, filepath: str) -> None:
        """Speichert die Konfiguration in einer JSON-Datei."""
        with open(filepath, 'w') as f:
            json.dump(self.dict(), f, indent=4)
    
    class Config:
        env_prefix = "DRONE_"  # Umgebungsvariablen beginnen mit DRONE_ 