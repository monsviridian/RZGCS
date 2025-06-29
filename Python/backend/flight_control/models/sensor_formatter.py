"""Sensor Data Formatter.

This module provides formatting and validation for sensor data values.
"""

from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class SensorUnit(Enum):
    """Sensor measurement units."""
    DEGREES = "°"
    METERS = "m"
    METERS_PER_SECOND = "m/s"
    KILOMETERS_PER_HOUR = "km/h"
    VOLTS = "V"
    AMPERES = "A"
    PERCENT = "%"
    CELSIUS = "°C"
    PRESSURE_HPA = "hPa"
    HUMIDITY_PERCENT = "%"
    COUNT = ""
    RATIO = ""

@dataclass
class SensorMetadata:
    """Metadata for a sensor value."""
    unit: SensorUnit
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    precision: int = 1
    conversion_factor: float = 1.0

class SensorDataFormatter:
    """Handles formatting and validation of sensor values."""
    
    # Mapping of sensor names to their metadata
    SENSOR_METADATA: Dict[str, SensorMetadata] = {
        # Attitude sensors
        "roll": SensorMetadata(SensorUnit.DEGREES, -180, 180, 1),
        "pitch": SensorMetadata(SensorUnit.DEGREES, -90, 90, 1),
        "yaw": SensorMetadata(SensorUnit.DEGREES, 0, 360, 1),
        "heading": SensorMetadata(SensorUnit.DEGREES, 0, 360, 1),
        
        # GPS sensors
        "gps_latitude": SensorMetadata(SensorUnit.DEGREES, -90, 90, 6),
        "gps_longitude": SensorMetadata(SensorUnit.DEGREES, -180, 180, 6),
        "gps_altitude": SensorMetadata(SensorUnit.METERS, None, None, 1),
        "groundspeed": SensorMetadata(SensorUnit.METERS_PER_SECOND, 0, None, 1),
        "airspeed": SensorMetadata(SensorUnit.METERS_PER_SECOND, 0, None, 1),
        "vertical_speed": SensorMetadata(SensorUnit.METERS_PER_SECOND, None, None, 1),
        "gps_satellites": SensorMetadata(SensorUnit.COUNT, 0, None, 0),
        "gps_hdop": SensorMetadata(SensorUnit.RATIO, 0, None, 2),
        "gps_vdop": SensorMetadata(SensorUnit.RATIO, 0, None, 2),
        "gps_fix_type": SensorMetadata(SensorUnit.COUNT, 0, 5, 0),
        
        # Battery sensors
        "battery_voltage": SensorMetadata(SensorUnit.VOLTS, 0, None, 2),
        "battery_current": SensorMetadata(SensorUnit.AMPERES, None, None, 2),
        "battery_percentage": SensorMetadata(SensorUnit.PERCENT, 0, 100, 1),
        "battery_temperature": SensorMetadata(SensorUnit.CELSIUS, None, None, 1),
        
        # Environmental sensors
        "temperature": SensorMetadata(SensorUnit.CELSIUS, None, None, 1),
        "pressure": SensorMetadata(SensorUnit.PRESSURE_HPA, 0, None, 1),
        "humidity": SensorMetadata(SensorUnit.HUMIDITY_PERCENT, 0, 100, 1),
        
        # Motor sensors
        "motor_temperature": SensorMetadata(SensorUnit.CELSIUS, None, None, 1),
        "esc_temperature": SensorMetadata(SensorUnit.CELSIUS, None, None, 1),
        "throttle": SensorMetadata(SensorUnit.PERCENT, 0, 100, 1),
    }
    
    @classmethod
    def get_metadata(cls, sensor_name: str) -> Optional[SensorMetadata]:
        """Get metadata for a sensor.
        
        Args:
            sensor_name: Name of the sensor
            
        Returns:
            SensorMetadata if found, None otherwise
        """
        return cls.SENSOR_METADATA.get(sensor_name)
    
    @classmethod
    def format_value(cls, sensor_name: str, value: float) -> str:
        """Format a sensor value according to its metadata.
        
        Args:
            sensor_name: Name of the sensor
            value: Value to format
            
        Returns:
            Formatted string with unit
        """
        metadata = cls.get_metadata(sensor_name)
        if metadata is None:
            return f"{value:.1f}"
            
        # Apply conversion factor
        display_value = value * metadata.conversion_factor
        
        # Format with specified precision
        formatted = f"{display_value:.{metadata.precision}f}"
        
        # Add unit if not empty
        if metadata.unit.value:
            formatted += f" {metadata.unit.value}"
            
        return formatted
    
    @classmethod
    def validate_value(cls, sensor_name: str, value: float) -> Tuple[bool, Optional[str]]:
        """Validate a sensor value against its metadata.
        
        Args:
            sensor_name: Name of the sensor
            value: Value to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        metadata = cls.get_metadata(sensor_name)
        if metadata is None:
            return True, None
            
        if metadata.min_value is not None and value < metadata.min_value:
            return False, f"Value {value} is below minimum {metadata.min_value}"
            
        if metadata.max_value is not None and value > metadata.max_value:
            return False, f"Value {value} is above maximum {metadata.max_value}"
            
        return True, None
    
    @classmethod
    def get_display_value(cls, sensor_name: str, value: float) -> Dict[str, Any]:
        """Get a complete display value object for a sensor.
        
        Args:
            sensor_name: Name of the sensor
            value: Raw sensor value
            
        Returns:
            Dictionary with formatted value and validation info
        """
        is_valid, error = cls.validate_value(sensor_name, value)
        formatted = cls.format_value(sensor_name, value)
        metadata = cls.get_metadata(sensor_name)
        
        return {
            "raw_value": value,
            "formatted_value": formatted,
            "is_valid": is_valid,
            "error_message": error,
            "unit": metadata.unit.value if metadata else None,
            "precision": metadata.precision if metadata else 1
        } 