"""Sensor ViewModel.

Dieses ViewModel implementiert die Verbindung zwischen Backend und QML-UI für Sensordaten.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
from PySide6.QtCore import QObject, Signal, Slot, Property

from ..models.fleet_data import (
    FleetStatus,
    FleetMode,
    UAVStatus,
    UAVMode,
    NetworkTopology,
    EncryptionStatus,
    PositionData,
    VelocityData,
    AttitudeData,
    SensorData,
    ResourceData,
    RoutingTable,
    BandwidthAllocation,
    CommunicationData,
    UAVData,
    FleetData,
    FleetError,
    FleetValidationError,
    FleetCommandError,
    FleetStateError
)
from ..models.sensor_formatter import SensorDataFormatter

class SensorViewModel(QObject):
    """Sensor ViewModel.
    
    Dieses ViewModel implementiert die Verbindung zwischen Backend und QML-UI für Sensordaten.
    
    Attributes:
        _sensor_data: Sensordaten
        _selected_uav_id: Ausgewählte UAV-ID
        _last_update_time: Zeitstempel der letzten Aktualisierung
        
    Signals:
        sensor_data_changed: Wird ausgelöst, wenn sich die Sensordaten ändern
        selected_uav_changed: Wird ausgelöst, wenn sich die ausgewählte UAV ändert
    """
    
    # Signale
    sensor_data_changed = Signal()
    selected_uav_changed = Signal()
    
    def __init__(self):
        """Initialisierung."""
        super().__init__()
        # SensorData mit Standardwerten initialisieren
        self._sensor_data = SensorData()
        self._selected_uav_id = ""
        self._last_update_time = datetime.now()
        self._sensor_values = {}  # Cache for formatted sensor values
    
    @Property(str, notify=selected_uav_changed)
    def selected_uav_id(self) -> str:
        """Ausgewählte UAV-ID."""
        return self._selected_uav_id
    
    @selected_uav_id.setter
    def selected_uav_id(self, uav_id: str):
        """Ausgewählte UAV-ID setzen.
        
        Args:
            uav_id: UAV-ID
        """
        if self._selected_uav_id != uav_id:
            self._selected_uav_id = uav_id
            self.selected_uav_changed.emit()
    
    @Slot(str, result='QVariant')
    def get_sensor_value(self, name: str) -> Dict[str, Any]:
        """Get formatted sensor value with metadata.
        
        Args:
            name: Name of the sensor
            
        Returns:
            Dictionary with formatted value and metadata
        """
        value = getattr(self._sensor_data, name, 0.0)
        return SensorDataFormatter.get_display_value(name, value)
    
    @Slot(str, result=str)
    def get_formatted_value(self, name: str) -> str:
        """Get formatted sensor value as string.
        
        Args:
            name: Name of the sensor
            
        Returns:
            Formatted value string with unit
        """
        value = getattr(self._sensor_data, name, 0.0)
        return SensorDataFormatter.format_value(name, value)
    
    @Slot(str, result=bool)
    def is_sensor_valid(self, name: str) -> bool:
        """Check if a sensor value is valid.
        
        Args:
            name: Name of the sensor
            
        Returns:
            True if value is valid, False otherwise
        """
        value = getattr(self._sensor_data, name, 0.0)
        is_valid, _ = SensorDataFormatter.validate_value(name, value)
        return is_valid
    
    @Slot(str, result=str)
    def get_sensor_error(self, name: str) -> str:
        """Get error message for a sensor value.
        
        Args:
            name: Name of the sensor
            
        Returns:
            Error message if invalid, empty string if valid
        """
        value = getattr(self._sensor_data, name, 0.0)
        _, error = SensorDataFormatter.validate_value(name, value)
        return error or ""
    
    @Property(float, notify=sensor_data_changed)
    def last_update_seconds(self) -> float:
        """Time since last update in seconds."""
        delta = datetime.now() - self._last_update_time
        return delta.total_seconds()
    
    @Property(float, notify=sensor_data_changed)
    def roll(self) -> float:
        """Roll value in degrees."""
        return self._sensor_data.roll
    
    @Property(float, notify=sensor_data_changed)
    def pitch(self) -> float:
        """Pitch value in degrees."""
        return self._sensor_data.pitch
    
    @Property(float, notify=sensor_data_changed)
    def yaw(self) -> float:
        """Yaw value in degrees."""
        return self._sensor_data.yaw
    
    @Property(float, notify=sensor_data_changed)
    def battery_voltage(self) -> float:
        """Battery voltage in volts."""
        return self._sensor_data.battery_voltage
    
    @Property(float, notify=sensor_data_changed)
    def battery_current(self) -> float:
        """Battery current in amperes."""
        return self._sensor_data.battery_current
    
    @Property(float, notify=sensor_data_changed)
    def battery_percentage(self) -> float:
        """Battery percentage remaining."""
        return self._sensor_data.battery_percentage
    
    @Property(float, notify=sensor_data_changed)
    def groundspeed(self) -> float:
        """Ground speed in m/s."""
        return self._sensor_data.groundspeed
    
    @Property(float, notify=sensor_data_changed)
    def airspeed(self) -> float:
        """Air speed in m/s."""
        return self._sensor_data.airspeed
    
    @Property(float, notify=sensor_data_changed)
    def gps_latitude(self) -> float:
        """GPS latitude in degrees."""
        return self._sensor_data.gps_latitude
    
    @Property(float, notify=sensor_data_changed)
    def gps_longitude(self) -> float:
        """GPS longitude in degrees."""
        return self._sensor_data.gps_longitude
    
    @Property(float, notify=sensor_data_changed)
    def gps_altitude(self) -> float:
        """GPS altitude in meters."""
        return self._sensor_data.gps_altitude
    
    def update_sensor_data(self, sensor_data: SensorData):
        """Update sensor data.
        
        Args:
            sensor_data: New sensor data
        """
        self._sensor_data = sensor_data
        self._last_update_time = datetime.now()
        self._sensor_values.clear()  # Clear cache
        self.sensor_data_changed.emit()
    
    @Slot(str, float)
    def update_sensor_value(self, name: str, value: float):
        """Update a single sensor value.
        
        Args:
            name: Name of the sensor
            value: New value
        """
        if hasattr(self._sensor_data, name):
            old_value = getattr(self._sensor_data, name)
            setattr(self._sensor_data, name, value)
            self._last_update_time = datetime.now()
            if name in self._sensor_values:
                del self._sensor_values[name]  # Clear cached value
            self.sensor_data_changed.emit()
            
            # Debug logging
            print(f"SensorViewModel: Updated {name} from {old_value} to {value}")
        else:
            print(f"SensorViewModel: WARNING - No attribute '{name}' in SensorData")
    
    def update_from_telemetry(self, telemetry_type: str, telemetry_data: Dict[str, Any]):
        """Update from telemetry data.
        
        Args:
            telemetry_type: Type of telemetry data
            telemetry_data: Telemetry data dictionary
        """
        # Update timestamp
        self._last_update_time = datetime.now()
        
        # Update relevant sensor values based on telemetry type
        if telemetry_type == "ATTITUDE":
            self._sensor_data.roll = telemetry_data.get("roll", 0.0)
            self._sensor_data.pitch = telemetry_data.get("pitch", 0.0)
            self._sensor_data.yaw = telemetry_data.get("yaw", 0.0)
            self._sensor_data.heading = telemetry_data.get("heading", 0.0)
            
        elif telemetry_type == "GPS":
            self._sensor_data.gps_latitude = telemetry_data.get("lat", 0.0)
            self._sensor_data.gps_longitude = telemetry_data.get("lon", 0.0)
            self._sensor_data.gps_altitude = telemetry_data.get("alt", 0.0)
            self._sensor_data.gps_fix_type = telemetry_data.get("fix_type", 0.0)
            self._sensor_data.gps_satellites = telemetry_data.get("satellites_visible", 0)
            
        elif telemetry_type == "VFR_HUD":
            self._sensor_data.groundspeed = telemetry_data.get("groundspeed", 0.0)
            self._sensor_data.airspeed = telemetry_data.get("airspeed", 0.0)
            self._sensor_data.throttle = telemetry_data.get("throttle", 0.0)
            
        elif telemetry_type == "BATTERY":
            self._sensor_data.battery_voltage = telemetry_data.get("voltage", 0.0)
            self._sensor_data.battery_current = telemetry_data.get("current", 0.0)
            self._sensor_data.battery_percentage = telemetry_data.get("percentage", 0.0)
            
        # Clear cache and emit change signal
        self._sensor_values.clear()
        self.sensor_data_changed.emit()