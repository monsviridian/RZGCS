"""
Datenprozessor für das Telemetrie-System.
Verarbeitet und validiert die Telemetrie-Daten.
"""

from typing import Dict, Any, Optional, List
import numpy as np
from datetime import datetime
from .data_types import (
    TelemetryData, PositionData, MovementData, OrientationData,
    SystemData, SensorData, WeatherData, TelemetryDataFactory
)
from .enums import TelemetryDataType, TelemetryUnit

class DataProcessor:
    """Verarbeitet und validiert Telemetrie-Daten"""
    
    def __init__(self):
        self._data_history: Dict[TelemetryDataType, List[TelemetryData]] = {}
        self._max_history_size = 1000  # Maximale Anzahl gespeicherter Datenpunkte pro Typ
        self._data_validators = {
            TelemetryDataType.LATITUDE: self._validate_latitude,
            TelemetryDataType.LONGITUDE: self._validate_longitude,
            TelemetryDataType.ALTITUDE: self._validate_altitude,
            TelemetryDataType.SPEED: self._validate_speed,
            TelemetryDataType.BATTERY_LEVEL: self._validate_battery_level,
            # Weitere Validatoren hier hinzufügen
        }
        
    def process_data(self, raw_data: bytes) -> Optional[TelemetryData]:
        """
        Verarbeitet rohe Telemetrie-Daten.
        
        Args:
            raw_data: Rohe Telemetrie-Daten
            
        Returns:
            Verarbeitete Telemetrie-Daten oder None bei Fehler
        """
        try:
            # Hier würde die tatsächliche Verarbeitung der MAVLink-Daten stattfinden
            # Dies ist nur ein Beispiel
            data_type = self._determine_data_type(raw_data)
            value = self._extract_value(raw_data)
            unit = self._determine_unit(data_type)
            
            # Daten erstellen
            data = TelemetryDataFactory.create_data(data_type, value, unit)
            
            # Daten validieren
            if not self.validate_data(data):
                return None
                
            # Daten zur Historie hinzufügen
            self._add_to_history(data)
            
            return data
            
        except Exception as e:
            print(f"Fehler bei der Datenverarbeitung: {str(e)}")
            return None
            
    def validate_data(self, data: TelemetryData) -> bool:
        """
        Validiert Telemetrie-Daten.
        
        Args:
            data: Zu validierende Daten
            
        Returns:
            True wenn die Daten gültig sind, sonst False
        """
        # Prüfen ob ein Validator für den Datentyp existiert
        validator = self._data_validators.get(data.type)
        if validator:
            return validator(data.value)
            
        # Wenn kein spezifischer Validator existiert, allgemeine Validierung
        return self._validate_general(data)
        
    def get_data_history(self, data_type: TelemetryDataType) -> List[TelemetryData]:
        """
        Gibt die Historie für einen bestimmten Datentyp zurück.
        
        Args:
            data_type: Typ der Daten
            
        Returns:
            Liste der gespeicherten Daten
        """
        return self._data_history.get(data_type, [])
        
    def get_statistics(self, data_type: TelemetryDataType) -> Dict[str, float]:
        """
        Berechnet Statistiken für einen Datentyp.
        
        Args:
            data_type: Typ der Daten
            
        Returns:
            Dictionary mit Statistiken
        """
        history = self.get_data_history(data_type)
        if not history:
            return {}
            
        values = [data.value for data in history]
        return {
            'min': float(np.min(values)),
            'max': float(np.max(values)),
            'mean': float(np.mean(values)),
            'std': float(np.std(values))
        }
        
    def _determine_data_type(self, raw_data: bytes) -> TelemetryDataType:
        """
        Bestimmt den Datentyp aus den rohen Daten.
        
        Args:
            raw_data: Rohe Telemetrie-Daten
            
        Returns:
            Bestimmter Datentyp
        """
        # Hier würde die tatsächliche Bestimmung des Datentyps stattfinden
        # Dies ist nur ein Beispiel
        return TelemetryDataType.ALTITUDE
        
    def _extract_value(self, raw_data: bytes) -> Any:
        """
        Extrahiert den Wert aus den rohen Daten.
        
        Args:
            raw_data: Rohe Telemetrie-Daten
            
        Returns:
            Extrahierter Wert
        """
        # Hier würde die tatsächliche Extraktion des Werts stattfinden
        # Dies ist nur ein Beispiel
        return 0.0
        
    def _determine_unit(self, data_type: TelemetryDataType) -> TelemetryUnit:
        """
        Bestimmt die Einheit für einen Datentyp.
        
        Args:
            data_type: Typ der Daten
            
        Returns:
            Bestimmte Einheit
        """
        # Mapping von Datentypen zu Einheiten
        unit_mapping = {
            TelemetryDataType.LATITUDE: TelemetryUnit.DEGREES,
            TelemetryDataType.LONGITUDE: TelemetryUnit.DEGREES,
            TelemetryDataType.ALTITUDE: TelemetryUnit.METERS,
            TelemetryDataType.SPEED: TelemetryUnit.METERS_PER_SECOND,
            TelemetryDataType.BATTERY_LEVEL: TelemetryUnit.PERCENT,
            # Weitere Mappings hier hinzufügen
        }
        return unit_mapping.get(data_type, TelemetryUnit.METERS)
        
    def _add_to_history(self, data: TelemetryData) -> None:
        """
        Fügt Daten zur Historie hinzu.
        
        Args:
            data: Zu speichernde Daten
        """
        if data.type not in self._data_history:
            self._data_history[data.type] = []
            
        self._data_history[data.type].append(data)
        
        # Historie auf maximale Größe beschränken
        if len(self._data_history[data.type]) > self._max_history_size:
            self._data_history[data.type] = self._data_history[data.type][-self._max_history_size:]
            
    def _validate_general(self, data: TelemetryData) -> bool:
        """
        Allgemeine Validierung von Telemetrie-Daten.
        
        Args:
            data: Zu validierende Daten
            
        Returns:
            True wenn die Daten gültig sind, sonst False
        """
        # Prüfen ob der Wert None ist
        if data.value is None:
            return False
            
        # Prüfen ob der Zeitstempel in der Zukunft liegt
        if data.timestamp > datetime.now():
            return False
            
        return True
        
    def _validate_latitude(self, value: float) -> bool:
        """Validiert Breitengrad"""
        return -90.0 <= value <= 90.0
        
    def _validate_longitude(self, value: float) -> bool:
        """Validiert Längengrad"""
        return -180.0 <= value <= 180.0
        
    def _validate_altitude(self, value: float) -> bool:
        """Validiert Höhe"""
        return -1000.0 <= value <= 100000.0  # -1000m bis 100km
        
    def _validate_speed(self, value: float) -> bool:
        """Validiert Geschwindigkeit"""
        return 0.0 <= value <= 1000.0  # 0 bis 1000 m/s
        
    def _validate_battery_level(self, value: float) -> bool:
        """Validiert Batteriestand"""
        return 0.0 <= value <= 100.0  # 0 bis 100 Prozent 