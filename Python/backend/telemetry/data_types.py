"""
Datentypen für das Telemetrie-System.
Definiert die Struktur der Telemetrie-Daten.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional
from .enums import TelemetryDataType, TelemetryUnit

@dataclass
class TelemetryData:
    """Basisklasse für Telemetrie-Daten"""
    timestamp: datetime
    type: TelemetryDataType
    value: Any
    unit: TelemetryUnit
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Konvertiert die Daten in ein Dictionary.
        
        Returns:
            Dictionary mit den Daten
        """
        return {
            'timestamp': self.timestamp.isoformat(),
            'type': self.type.value,
            'value': self.value,
            'unit': self.unit.value
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TelemetryData':
        """
        Erstellt ein TelemetryData-Objekt aus einem Dictionary.
        
        Args:
            data: Dictionary mit den Daten
            
        Returns:
            TelemetryData-Objekt
        """
        return cls(
            timestamp=datetime.fromisoformat(data['timestamp']),
            type=TelemetryDataType(data['type']),
            value=data['value'],
            unit=TelemetryUnit(data['unit'])
        )

@dataclass
class PositionData(TelemetryData):
    """Daten für die Position des Flugzeugs"""
    latitude: float
    longitude: float
    altitude: float
    heading: float
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            'latitude': self.latitude,
            'longitude': self.longitude,
            'altitude': self.altitude,
            'heading': self.heading
        })
        return data

@dataclass
class MovementData(TelemetryData):
    """Daten für die Bewegung des Flugzeugs"""
    speed: float
    vertical_speed: float
    ground_speed: float
    air_speed: float
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            'speed': self.speed,
            'vertical_speed': self.vertical_speed,
            'ground_speed': self.ground_speed,
            'air_speed': self.air_speed
        })
        return data

@dataclass
class OrientationData(TelemetryData):
    """Daten für die Orientierung des Flugzeugs"""
    roll: float
    pitch: float
    yaw: float
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            'roll': self.roll,
            'pitch': self.pitch,
            'yaw': self.yaw
        })
        return data

@dataclass
class SystemData(TelemetryData):
    """Daten für das Flugzeug-System"""
    battery_level: float
    battery_voltage: float
    battery_current: float
    signal_strength: float
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            'battery_level': self.battery_level,
            'battery_voltage': self.battery_voltage,
            'battery_current': self.battery_current,
            'signal_strength': self.signal_strength
        })
        return data

@dataclass
class SensorData(TelemetryData):
    """Daten von den Sensoren"""
    gps_fix: int
    gps_satellites: int
    gps_hdop: float
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            'gps_fix': self.gps_fix,
            'gps_satellites': self.gps_satellites,
            'gps_hdop': self.gps_hdop
        })
        return data

@dataclass
class WeatherData(TelemetryData):
    """Wetterdaten"""
    temperature: float
    pressure: float
    humidity: float
    wind_speed: float
    wind_direction: float
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            'temperature': self.temperature,
            'pressure': self.pressure,
            'humidity': self.humidity,
            'wind_speed': self.wind_speed,
            'wind_direction': self.wind_direction
        })
        return data

class TelemetryDataFactory:
    """Factory für die Erstellung von Telemetrie-Daten"""
    
    @staticmethod
    def create_data(data_type: TelemetryDataType, value: Any, unit: TelemetryUnit) -> TelemetryData:
        """
        Erstellt ein TelemetryData-Objekt.
        
        Args:
            data_type: Typ der Daten
            value: Wert der Daten
            unit: Einheit der Daten
            
        Returns:
            TelemetryData-Objekt
        """
        return TelemetryData(
            timestamp=datetime.now(),
            type=data_type,
            value=value,
            unit=unit
        )
    
    @staticmethod
    def create_position_data(latitude: float, longitude: float, altitude: float, heading: float) -> PositionData:
        """
        Erstellt ein PositionData-Objekt.
        
        Args:
            latitude: Breitengrad
            longitude: Längengrad
            altitude: Höhe
            heading: Kurs
            
        Returns:
            PositionData-Objekt
        """
        return PositionData(
            timestamp=datetime.now(),
            type=TelemetryDataType.POSITION,
            value=None,
            unit=TelemetryUnit.METERS,
            latitude=latitude,
            longitude=longitude,
            altitude=altitude,
            heading=heading
        )
    
    @staticmethod
    def create_movement_data(speed: float, vertical_speed: float, ground_speed: float, air_speed: float) -> MovementData:
        """
        Erstellt ein MovementData-Objekt.
        
        Args:
            speed: Geschwindigkeit
            vertical_speed: Vertikale Geschwindigkeit
            ground_speed: Geschwindigkeit über Grund
            air_speed: Geschwindigkeit in der Luft
            
        Returns:
            MovementData-Objekt
        """
        return MovementData(
            timestamp=datetime.now(),
            type=TelemetryDataType.MOVEMENT,
            value=None,
            unit=TelemetryUnit.METERS_PER_SECOND,
            speed=speed,
            vertical_speed=vertical_speed,
            ground_speed=ground_speed,
            air_speed=air_speed
        )
    
    @staticmethod
    def create_orientation_data(roll: float, pitch: float, yaw: float) -> OrientationData:
        """
        Erstellt ein OrientationData-Objekt.
        
        Args:
            roll: Roll-Winkel
            pitch: Pitch-Winkel
            yaw: Yaw-Winkel
            
        Returns:
            OrientationData-Objekt
        """
        return OrientationData(
            timestamp=datetime.now(),
            type=TelemetryDataType.ORIENTATION,
            value=None,
            unit=TelemetryUnit.DEGREES,
            roll=roll,
            pitch=pitch,
            yaw=yaw
        )
    
    @staticmethod
    def create_system_data(battery_level: float, battery_voltage: float, battery_current: float, signal_strength: float) -> SystemData:
        """
        Erstellt ein SystemData-Objekt.
        
        Args:
            battery_level: Batteriestand
            battery_voltage: Batteriespannung
            battery_current: Batteriestrom
            signal_strength: Signalstärke
            
        Returns:
            SystemData-Objekt
        """
        return SystemData(
            timestamp=datetime.now(),
            type=TelemetryDataType.SYSTEM,
            value=None,
            unit=TelemetryUnit.PERCENT,
            battery_level=battery_level,
            battery_voltage=battery_voltage,
            battery_current=battery_current,
            signal_strength=signal_strength
        )
    
    @staticmethod
    def create_sensor_data(gps_fix: int, gps_satellites: int, gps_hdop: float) -> SensorData:
        """
        Erstellt ein SensorData-Objekt.
        
        Args:
            gps_fix: GPS-Fix
            gps_satellites: Anzahl der GPS-Satelliten
            gps_hdop: GPS HDOP
            
        Returns:
            SensorData-Objekt
        """
        return SensorData(
            timestamp=datetime.now(),
            type=TelemetryDataType.SENSOR,
            value=None,
            unit=TelemetryUnit.METERS,
            gps_fix=gps_fix,
            gps_satellites=gps_satellites,
            gps_hdop=gps_hdop
        )
    
    @staticmethod
    def create_weather_data(temperature: float, pressure: float, humidity: float, wind_speed: float, wind_direction: float) -> WeatherData:
        """
        Erstellt ein WeatherData-Objekt.
        
        Args:
            temperature: Temperatur
            pressure: Luftdruck
            humidity: Luftfeuchtigkeit
            wind_speed: Windgeschwindigkeit
            wind_direction: Windrichtung
            
        Returns:
            WeatherData-Objekt
        """
        return WeatherData(
            timestamp=datetime.now(),
            type=TelemetryDataType.WEATHER,
            value=None,
            unit=TelemetryUnit.CELSIUS,
            temperature=temperature,
            pressure=pressure,
            humidity=humidity,
            wind_speed=wind_speed,
            wind_direction=wind_direction
        ) 