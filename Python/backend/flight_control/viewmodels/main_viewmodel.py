"""
Haupt-ViewModel für die Flugsteuerung.
Koordiniert alle ViewModels und implementiert die Hauptpräsentationslogik.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime

from PySide6.QtCore import QObject, Signal, Slot, Property

from .flight_viewmodel import FlightViewModel
from .mission_viewmodel import MissionViewModel
from .telemetry_viewmodel import TelemetryViewModel
from .connection_viewmodel import ConnectionViewModel

from ..models.flight_data import Position, FlightState, Mission, MissionPlan
from ..enums import FlightStatus, FlightMode, ConnectionStatus, ConnectionType

class MainViewModel(QObject):
    """Implementiert die Hauptpräsentationslogik für die Flugsteuerung"""
    
    # Signale
    error_occurred = Signal(str)
    
    def __init__(self):
        """Initialisiert das ViewModel"""
        super().__init__()
        
        # ViewModels
        self._flight_viewmodel = FlightViewModel()
        self._mission_viewmodel = MissionViewModel()
        self._telemetry_viewmodel = TelemetryViewModel()
        self._connection_viewmodel = ConnectionViewModel()
        
        # Signale verbinden
        self._flight_viewmodel.error_occurred.connect(self._on_error)
        self._mission_viewmodel.error_occurred.connect(self._on_error)
        self._telemetry_viewmodel.error_occurred.connect(self._on_error)
        self._connection_viewmodel.error_occurred.connect(self._on_error)
        
    # Properties
    @Property(FlightViewModel)
    def flight_viewmodel(self) -> FlightViewModel:
        """Gibt das Flug-ViewModel zurück"""
        return self._flight_viewmodel
        
    @Property(MissionViewModel)
    def mission_viewmodel(self) -> MissionViewModel:
        """Gibt das Missions-ViewModel zurück"""
        return self._mission_viewmodel
        
    @Property(TelemetryViewModel)
    def telemetry_viewmodel(self) -> TelemetryViewModel:
        """Gibt das Telemetrie-ViewModel zurück"""
        return self._telemetry_viewmodel
        
    @Property(ConnectionViewModel)
    def connection_viewmodel(self) -> ConnectionViewModel:
        """Gibt das Verbindungs-ViewModel zurück"""
        return self._connection_viewmodel
        
    # Slots
    @Slot()
    def initialize(self) -> bool:
        """
        Initialisiert das System.
        
        Returns:
            True wenn erfolgreich, sonst False
        """
        try:
            # Verbindung herstellen
            if not self._connection_viewmodel.connect():
                return False
                
            # Flugzustand initialisieren
            if not self._flight_viewmodel.initialize():
                return False
                
            # Missionen laden
            if not self._mission_viewmodel.load_missions():
                return False
                
            return True
            
        except Exception as e:
            self._on_error(f"Fehler bei der Initialisierung: {str(e)}")
            return False
            
    @Slot()
    def shutdown(self) -> bool:
        """
        Fährt das System herunter.
        
        Returns:
            True wenn erfolgreich, sonst False
        """
        try:
            # Missionen speichern
            if not self._mission_viewmodel.save_missions():
                return False
                
            # Flugzustand zurücksetzen
            if not self._flight_viewmodel.reset():
                return False
                
            # Verbindung trennen
            if not self._connection_viewmodel.disconnect():
                return False
                
            return True
            
        except Exception as e:
            self._on_error(f"Fehler beim Herunterfahren: {str(e)}")
            return False
            
    @Slot(str)
    def export_config(self, file_path: str) -> bool:
        """
        Exportiert die Konfiguration.
        
        Args:
            file_path: Dateipfad
            
        Returns:
            True wenn erfolgreich, sonst False
        """
        try:
            # Verbindungsdaten exportieren
            if not self._connection_viewmodel.export_connection(file_path + ".connection"):
                return False
                
            # Telemetriedaten exportieren
            if not self._telemetry_viewmodel.export_telemetry(file_path + ".telemetry"):
                return False
                
            # Missionen exportieren
            if not self._mission_viewmodel.export_missions(file_path + ".missions"):
                return False
                
            return True
            
        except Exception as e:
            self._on_error(f"Fehler beim Exportieren der Konfiguration: {str(e)}")
            return False
            
    @Slot(str)
    def import_config(self, file_path: str) -> bool:
        """
        Importiert die Konfiguration.
        
        Args:
            file_path: Dateipfad
            
        Returns:
            True wenn erfolgreich, sonst False
        """
        try:
            # Verbindungsdaten importieren
            if not self._connection_viewmodel.import_connection(file_path + ".connection"):
                return False
                
            # Telemetriedaten importieren
            if not self._telemetry_viewmodel.import_telemetry(file_path + ".telemetry"):
                return False
                
            # Missionen importieren
            if not self._mission_viewmodel.import_missions(file_path + ".missions"):
                return False
                
            return True
            
        except Exception as e:
            self._on_error(f"Fehler beim Importieren der Konfiguration: {str(e)}")
            return False
            
    # Signal-Handler
    def _on_error(self, message: str) -> None:
        """
        Handler für Fehlermeldungen.
        
        Args:
            message: Fehlermeldung
        """
        self.error_occurred.emit(message) 