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

class SensorViewModel(QObject):
    """Sensor ViewModel.
    
    Dieses ViewModel implementiert die Verbindung zwischen Backend und QML-UI für Sensordaten.
    
    Attributes:
        _sensor_data: Sensordaten
        _selected_uav_id: Ausgewählte UAV-ID
        
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
        self._sensor_data = SensorData(temperature=0.0, pressure=0.0, humidity=0.0)
        self._selected_uav_id = ""
    
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
    
    @Property(float, notify=sensor_data_changed)
    def battery_voltage(self) -> float:
        """Batteriespannung."""
        return self._sensor_data.battery_voltage
    
    @Property(float, notify=sensor_data_changed)
    def battery_current(self) -> float:
        """Batteriestrom."""
        return self._sensor_data.battery_current
    
    @Property(float, notify=sensor_data_changed)
    def battery_percentage(self) -> float:
        """Batterieprozentsatz."""
        return self._sensor_data.battery_percentage
    
    @Property(float, notify=sensor_data_changed)
    def battery_temperature(self) -> float:
        """Batterietemperatur."""
        return self._sensor_data.battery_temperature
    
    @Property(float, notify=sensor_data_changed)
    def motor_temperature(self) -> float:
        """Motortemperatur."""
        return self._sensor_data.motor_temperature
    
    @Property(float, notify=sensor_data_changed)
    def esc_temperature(self) -> float:
        """ESC-Temperatur."""
        return self._sensor_data.esc_temperature
    
    @Property(float, notify=sensor_data_changed)
    def gps_signal_strength(self) -> float:
        """GPS-Signalstärke."""
        return self._sensor_data.gps_signal_strength
    
    @Property(float, notify=sensor_data_changed)
    def gps_satellites(self) -> float:
        """GPS-Satelliten."""
        return self._sensor_data.gps_satellites
    
    @Property(float, notify=sensor_data_changed)
    def gps_hdop(self) -> float:
        """GPS-HDOP."""
        return self._sensor_data.gps_hdop
    
    @Property(float, notify=sensor_data_changed)
    def gps_vdop(self) -> float:
        """GPS-VDOP."""
        return self._sensor_data.gps_vdop
    
    @Property(float, notify=sensor_data_changed)
    def gps_pdop(self) -> float:
        """GPS-PDOP."""
        return self._sensor_data.gps_pdop
    
    @Property(float, notify=sensor_data_changed)
    def gps_fix_type(self) -> float:
        """GPS-Fix-Typ."""
        return self._sensor_data.gps_fix_type
    
    @Property(float, notify=sensor_data_changed)
    def gps_fix_quality(self) -> float:
        """GPS-Fix-Qualität."""
        return self._sensor_data.gps_fix_quality
    
    @Property(float, notify=sensor_data_changed)
    def gps_eph(self) -> float:
        """GPS-EPH."""
        return self._sensor_data.gps_eph
    
    @Property(float, notify=sensor_data_changed)
    def gps_epv(self) -> float:
        """GPS-EPV."""
        return self._sensor_data.gps_epv
    
    @Property(float, notify=sensor_data_changed)
    def gps_vel(self) -> float:
        """GPS-Geschwindigkeit."""
        return self._sensor_data.gps_vel
    
    @Property(float, notify=sensor_data_changed)
    def gps_cog(self) -> float:
        """GPS-Kurs über Grund."""
        return self._sensor_data.gps_cog
    
    @Property(float, notify=sensor_data_changed)
    def gps_speed_accuracy(self) -> float:
        """GPS-Geschwindigkeitsgenauigkeit."""
        return self._sensor_data.gps_speed_accuracy
    
    @Property(float, notify=sensor_data_changed)
    def gps_horizontal_accuracy(self) -> float:
        """GPS-horizontale Genauigkeit."""
        return self._sensor_data.gps_horizontal_accuracy
    
    @Property(float, notify=sensor_data_changed)
    def gps_vertical_accuracy(self) -> float:
        """GPS-vertikale Genauigkeit."""
        return self._sensor_data.gps_vertical_accuracy
    
    @Property(float, notify=sensor_data_changed)
    def gps_heading_accuracy(self) -> float:
        """GPS-Richtungsgenauigkeit."""
        return self._sensor_data.gps_heading_accuracy
    
    @Property(float, notify=sensor_data_changed)
    def gps_yaw_accuracy(self) -> float:
        """GPS-Gierwinkelgenauigkeit."""
        return self._sensor_data.gps_yaw_accuracy
    
    @Property(float, notify=sensor_data_changed)
    def gps_altitude_accuracy(self) -> float:
        """GPS-Höhengenauigkeit."""
        return self._sensor_data.gps_altitude_accuracy
    
    @Property(float, notify=sensor_data_changed)
    def gps_speed_accuracy_estimate(self) -> float:
        """GPS-Geschwindigkeitsgenauigkeitsschätzung."""
        return self._sensor_data.gps_speed_accuracy_estimate
    
    @Property(float, notify=sensor_data_changed)
    def gps_horizontal_accuracy_estimate(self) -> float:
        """GPS-horizontale Genauigkeitsschätzung."""
        return self._sensor_data.gps_horizontal_accuracy_estimate
    
    @Property(float, notify=sensor_data_changed)
    def gps_vertical_accuracy_estimate(self) -> float:
        """GPS-vertikale Genauigkeitsschätzung."""
        return self._sensor_data.gps_vertical_accuracy_estimate
    
    @Property(float, notify=sensor_data_changed)
    def gps_heading_accuracy_estimate(self) -> float:
        """GPS-Richtungsgenauigkeitsschätzung."""
        return self._sensor_data.gps_heading_accuracy_estimate
    
    @Property(float, notify=sensor_data_changed)
    def gps_yaw_accuracy_estimate(self) -> float:
        """GPS-Gierwinkelgenauigkeitsschätzung."""
        return self._sensor_data.gps_yaw_accuracy_estimate
    
    @Property(float, notify=sensor_data_changed)
    def gps_altitude_accuracy_estimate(self) -> float:
        """GPS-Höhengenauigkeitsschätzung."""
        return self._sensor_data.gps_altitude_accuracy_estimate
    
    def update_sensor_data(self, sensor_data: SensorData):
        """Sensordaten aktualisieren.
        
        Args:
            sensor_data: Sensordaten
        """
        self._sensor_data = sensor_data
        self.sensor_data_changed.emit()
        
    @Slot(str, float)
    def update_sensor_value(self, name: str, value: float):
        """Einzelnen Sensorwert aktualisieren.
        
        Args:
            name: Name des Sensors
            value: Sensorwert
        """
        # Direkter Zugriff auf die Attribute des SensorData-Objekts über Namen
        if hasattr(self._sensor_data, name):
            setattr(self._sensor_data, name, value)
        else:
            # Erweiterungsmöglichkeit für nicht direkt vorhandene Attribute
            print(f"Warnung: Sensordaten haben kein Attribut {name}")
            
        self.sensor_data_changed.emit()
    
    def update_from_telemetry(self, telemetry_type: str, telemetry_data: Dict[str, Any]):
        """Sensordaten aus Telemetriedaten aktualisieren.
        
        Args:
            telemetry_type: Art der Telemetriedaten (z.B. 'attitude', 'gps', 'battery')
            telemetry_data: Telemetriedaten als Dictionary
        """
        if telemetry_type == 'attitude':
            if 'roll' in telemetry_data:
                self.update_sensor_value('roll', telemetry_data['roll'])
            if 'pitch' in telemetry_data:
                self.update_sensor_value('pitch', telemetry_data['pitch'])
            if 'yaw' in telemetry_data:
                self.update_sensor_value('yaw', telemetry_data['yaw'])
        elif telemetry_type == 'gps':
            if 'lat' in telemetry_data:
                self.update_sensor_value('gps_lat', telemetry_data['lat'])
            if 'lon' in telemetry_data:
                self.update_sensor_value('gps_lon', telemetry_data['lon'])
            if 'alt' in telemetry_data:
                self.update_sensor_value('altitude', telemetry_data['alt'])
            if 'satellites' in telemetry_data:
                self.update_sensor_value('gps_satellites', telemetry_data['satellites'])
        elif telemetry_type == 'battery':
            if 'voltage' in telemetry_data:
                self.update_sensor_value('battery_voltage', telemetry_data['voltage'])
            if 'current' in telemetry_data:
                self.update_sensor_value('battery_current', telemetry_data['current'])
            if 'percentage' in telemetry_data:
                self.update_sensor_value('battery_percentage', telemetry_data['percentage'])
        elif telemetry_type == 'velocity':
            if 'groundspeed' in telemetry_data:
                self.update_sensor_value('groundspeed', telemetry_data['groundspeed'])
            if 'airspeed' in telemetry_data:
                self.update_sensor_value('airspeed', telemetry_data['airspeed'])
        # Signalisieren, dass sich Daten geändert haben
        self.sensor_data_changed.emit()
    
    @Slot(str, result=float)
    def findSensorByName(self, name: str) -> float:
        """Findet einen Sensorwert basierend auf dem Namen.
        
        Args:
            name: Name des Sensors
            
        Returns:
            Sensorwert als float, oder 0.0 wenn nicht gefunden
        """
        # Direkte Attribute des SensorData-Objekts prüfen
        if hasattr(self._sensor_data, name):
            value = getattr(self._sensor_data, name)
            return float(value) if value is not None else 0.0
        
        # Commonly used sensor names mapping
        sensor_mapping = {
            'roll': 'roll',
            'pitch': 'pitch', 
            'yaw': 'yaw',
            'altitude': 'altitude',
            'gps_lat': 'gps_lat',
            'gps_lon': 'gps_lon',
            'gps_latitude': 'gps_lat',
            'gps_longitude': 'gps_lon',
            'altitude_msl': 'altitude',
            'groundspeed': 'groundspeed',
            'airspeed': 'airspeed',
            'battery_voltage': 'battery_voltage',
            'battery_current': 'battery_current',
            'battery_percentage': 'battery_percentage',
            'satellites': 'gps_satellites',
            'gps_satellites': 'gps_satellites'
        }
        
        # Check mapped names
        if name in sensor_mapping:
            mapped_name = sensor_mapping[name]
            if hasattr(self._sensor_data, mapped_name):
                value = getattr(self._sensor_data, mapped_name)
                return float(value) if value is not None else 0.0
        
        # If not found, return 0
        print(f"Warnung: Sensor '{name}' nicht gefunden")
        return 0.0