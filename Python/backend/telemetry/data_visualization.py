"""
Visualisierung für das Telemetrie-System.
Visualisiert Telemetrie-Daten in Echtzeit.
"""

from typing import Dict, Any, List, Optional
import numpy as np
from datetime import datetime, timedelta
from .data_types import TelemetryData
from .enums import TelemetryDataType, TelemetryUnit

class DataVisualization:
    """Visualisiert Telemetrie-Daten"""
    
    def __init__(self):
        self._data_buffer: Dict[TelemetryDataType, List[TelemetryData]] = {}
        self._buffer_size = 100  # Anzahl der Datenpunkte im Buffer
        self._update_interval = 0.1  # Update-Intervall in Sekunden
        self._last_update = datetime.now()
        
    def update_visualization(self, data: TelemetryData) -> None:
        """
        Aktualisiert die Visualisierung.
        
        Args:
            data: Zu visualisierende Daten
        """
        # Prüfen ob Update-Intervall abgelaufen ist
        current_time = datetime.now()
        if (current_time - self._last_update).total_seconds() < self._update_interval:
            return
            
        # Daten zum Buffer hinzufügen
        if data.type not in self._data_buffer:
            self._data_buffer[data.type] = []
            
        self._data_buffer[data.type].append(data)
        
        # Buffer-Größe begrenzen
        if len(self._data_buffer[data.type]) > self._buffer_size:
            self._data_buffer[data.type] = self._data_buffer[data.type][-self._buffer_size:]
            
        self._last_update = current_time
        
    def get_visualization_data(self) -> Dict[str, Any]:
        """
        Gibt die Visualisierungsdaten zurück.
        
        Returns:
            Dictionary mit Visualisierungsdaten
        """
        result = {}
        
        for data_type, data_list in self._data_buffer.items():
            if not data_list:
                continue
                
            # Zeitstempel und Werte extrahieren
            timestamps = [d.timestamp for d in data_list]
            values = [d.value for d in data_list]
            
            # Statistiken berechnen
            stats = self._calculate_statistics(values)
            
            # Visualisierungsdaten erstellen
            result[data_type.value] = {
                'timestamps': timestamps,
                'values': values,
                'unit': data_list[0].unit.value,
                'statistics': stats
            }
            
        return result
        
    def get_data_for_type(self, data_type: TelemetryDataType) -> Optional[Dict[str, Any]]:
        """
        Gibt die Visualisierungsdaten für einen bestimmten Datentyp zurück.
        
        Args:
            data_type: Typ der Daten
            
        Returns:
            Dictionary mit Visualisierungsdaten oder None
        """
        data_list = self._data_buffer.get(data_type)
        if not data_list:
            return None
            
        # Zeitstempel und Werte extrahieren
        timestamps = [d.timestamp for d in data_list]
        values = [d.value for d in data_list]
        
        # Statistiken berechnen
        stats = self._calculate_statistics(values)
        
        return {
            'timestamps': timestamps,
            'values': values,
            'unit': data_list[0].unit.value,
            'statistics': stats
        }
        
    def get_latest_value(self, data_type: TelemetryDataType) -> Optional[Dict[str, Any]]:
        """
        Gibt den neuesten Wert für einen Datentyp zurück.
        
        Args:
            data_type: Typ der Daten
            
        Returns:
            Dictionary mit dem neuesten Wert oder None
        """
        data_list = self._data_buffer.get(data_type)
        if not data_list:
            return None
            
        latest_data = data_list[-1]
        return {
            'timestamp': latest_data.timestamp,
            'value': latest_data.value,
            'unit': latest_data.unit.value
        }
        
    def get_data_range(self, data_type: TelemetryDataType) -> Optional[Dict[str, Any]]:
        """
        Gibt den Wertebereich für einen Datentyp zurück.
        
        Args:
            data_type: Typ der Daten
            
        Returns:
            Dictionary mit Min- und Max-Wert oder None
        """
        data_list = self._data_buffer.get(data_type)
        if not data_list:
            return None
            
        values = [d.value for d in data_list]
        return {
            'min': float(np.min(values)),
            'max': float(np.max(values)),
            'unit': data_list[0].unit.value
        }
        
    def clear_buffer(self, data_type: Optional[TelemetryDataType] = None) -> None:
        """
        Löscht den Datenbuffer.
        
        Args:
            data_type: Optional: Löscht nur den Buffer für diesen Datentyp
        """
        if data_type:
            self._data_buffer.pop(data_type, None)
        else:
            self._data_buffer.clear()
            
    def _calculate_statistics(self, values: List[float]) -> Dict[str, float]:
        """
        Berechnet Statistiken für eine Liste von Werten.
        
        Args:
            values: Liste von Werten
            
        Returns:
            Dictionary mit Statistiken
        """
        if not values:
            return {}
            
        return {
            'min': float(np.min(values)),
            'max': float(np.max(values)),
            'mean': float(np.mean(values)),
            'std': float(np.std(values))
        }
        
    def get_trend(self, data_type: TelemetryDataType, window_size: int = 10) -> Optional[Dict[str, Any]]:
        """
        Berechnet den Trend für einen Datentyp.
        
        Args:
            data_type: Typ der Daten
            window_size: Größe des Zeitfensters
            
        Returns:
            Dictionary mit Trend-Daten oder None
        """
        data_list = self._data_buffer.get(data_type)
        if not data_list or len(data_list) < window_size:
            return None
            
        # Werte extrahieren
        values = [d.value for d in data_list]
        
        # Trend berechnen (einfache lineare Regression)
        x = np.arange(len(values))
        slope, intercept = np.polyfit(x, values, 1)
        
        # Trend-Linie berechnen
        trend_line = slope * x + intercept
        
        return {
            'slope': float(slope),
            'intercept': float(intercept),
            'trend_line': trend_line.tolist(),
            'unit': data_list[0].unit.value
        }
        
    def get_moving_average(self, data_type: TelemetryDataType, window_size: int = 10) -> Optional[Dict[str, Any]]:
        """
        Berechnet den gleitenden Durchschnitt für einen Datentyp.
        
        Args:
            data_type: Typ der Daten
            window_size: Größe des Zeitfensters
            
        Returns:
            Dictionary mit Durchschnitts-Daten oder None
        """
        data_list = self._data_buffer.get(data_type)
        if not data_list or len(data_list) < window_size:
            return None
            
        # Werte extrahieren
        values = [d.value for d in data_list]
        
        # Gleitenden Durchschnitt berechnen
        moving_avg = np.convolve(values, np.ones(window_size)/window_size, mode='valid')
        
        return {
            'values': moving_avg.tolist(),
            'unit': data_list[0].unit.value
        } 