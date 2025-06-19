"""
Telemetrie-Manager für das RZGCS.
Verwaltet und koordiniert alle Telemetrie-Komponenten.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from PySide6.QtCore import QObject, Signal, Property, Slot, QTimer
from PySide6.QtQml import QmlElement

from .data_types import TelemetryData, TelemetryDataFactory
from .data_processor import DataProcessor
from .data_storage import DataStorage
from .data_visualization import DataVisualization
from .enums import TelemetryStatus, TelemetryDataType
from ..connection.connection_manager import ConnectionManager

QML_IMPORT_NAME = "RZGCS.Telemetry"
QML_IMPORT_MAJOR_VERSION = 1

@QmlElement
class TelemetryManager(QObject):
    """Hauptklasse für die Telemetrie-Verwaltung"""
    
    # Signale
    statusChanged = Signal(TelemetryStatus)
    errorOccurred = Signal(str)
    dataReceived = Signal(TelemetryDataType, float, str)  # type, value, unit
    dataProcessed = Signal(TelemetryDataType, dict)  # type, processed_data
    visualizationUpdated = Signal(dict)  # visualization_data
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Komponenten initialisieren
        self._processor = DataProcessor()
        self._storage = DataStorage()
        self._visualization = DataVisualization()
        
        # Status und Timer
        self._status = TelemetryStatus.DISCONNECTED
        self._error_message = ""
        self._update_timer = QTimer()
        self._update_timer.timeout.connect(self._update_visualization)
        self._update_timer.start(100)  # 100ms Update-Intervall
        
        # Verbindung zum Connection Manager
        self._connection_manager = None
        
    @Property(TelemetryStatus, notify=statusChanged)
    def status(self) -> TelemetryStatus:
        """Gibt den aktuellen Status zurück"""
        return self._status
        
    @Property(str, notify=errorOccurred)
    def error_message(self) -> str:
        """Gibt die letzte Fehlermeldung zurück"""
        return self._error_message
        
    def set_connection_manager(self, connection_manager: ConnectionManager) -> None:
        """
        Setzt den Connection Manager.
        
        Args:
            connection_manager: Connection Manager Instanz
        """
        self._connection_manager = connection_manager
        self._connection_manager.messageReceived.connect(self._handle_message)
        
    @Slot()
    def start_telemetry(self) -> None:
        """Startet die Telemetrie"""
        if not self._connection_manager:
            self._set_error("Kein Connection Manager verfügbar")
            return
            
        if self._connection_manager.status != "CONNECTED":
            self._set_error("Keine Verbindung verfügbar")
            return
            
        self._set_status(TelemetryStatus.CONNECTED)
        self._processor.start_processing()
        self._storage.start_storage()
        
    @Slot()
    def stop_telemetry(self) -> None:
        """Stoppt die Telemetrie"""
        self._set_status(TelemetryStatus.DISCONNECTED)
        self._processor.stop_processing()
        self._storage.stop_storage()
        self._visualization.clear_buffer()
        
    @Slot(TelemetryDataType)
    def get_current_data(self, data_type: TelemetryDataType) -> Optional[Dict[str, Any]]:
        """
        Gibt die aktuellen Daten für einen Datentyp zurück.
        
        Args:
            data_type: Typ der Daten
            
        Returns:
            Dictionary mit den Daten oder None
        """
        return self._visualization.get_latest_value(data_type)
        
    @Slot(TelemetryDataType)
    def get_data_history(self, data_type: TelemetryDataType) -> List[Dict[str, Any]]:
        """
        Gibt die Historie für einen Datentyp zurück.
        
        Args:
            data_type: Typ der Daten
            
        Returns:
            Liste von Dictionaries mit den Daten
        """
        return self._processor.get_data_history(data_type)
        
    @Slot(TelemetryDataType)
    def get_data_statistics(self, data_type: TelemetryDataType) -> Dict[str, float]:
        """
        Gibt Statistiken für einen Datentyp zurück.
        
        Args:
            data_type: Typ der Daten
            
        Returns:
            Dictionary mit Statistiken
        """
        return self._processor.get_statistics(data_type)
        
    @Slot(TelemetryDataType)
    def get_data_visualization(self, data_type: TelemetryDataType) -> Optional[Dict[str, Any]]:
        """
        Gibt die Visualisierungsdaten für einen Datentyp zurück.
        
        Args:
            data_type: Typ der Daten
            
        Returns:
            Dictionary mit Visualisierungsdaten oder None
        """
        return self._visualization.get_data_for_type(data_type)
        
    @Slot(TelemetryDataType, int)
    def get_data_trend(self, data_type: TelemetryDataType, window_size: int = 10) -> Optional[Dict[str, Any]]:
        """
        Gibt den Trend für einen Datentyp zurück.
        
        Args:
            data_type: Typ der Daten
            window_size: Größe des Zeitfensters
            
        Returns:
            Dictionary mit Trend-Daten oder None
        """
        return self._visualization.get_trend(data_type, window_size)
        
    @Slot(TelemetryDataType, int)
    def get_moving_average(self, data_type: TelemetryDataType, window_size: int = 10) -> Optional[Dict[str, Any]]:
        """
        Gibt den gleitenden Durchschnitt für einen Datentyp zurück.
        
        Args:
            data_type: Typ der Daten
            window_size: Größe des Zeitfensters
            
        Returns:
            Dictionary mit Durchschnitts-Daten oder None
        """
        return self._visualization.get_moving_average(data_type, window_size)
        
    @Slot(str)
    def export_data(self, file_path: str) -> bool:
        """
        Exportiert die gespeicherten Daten.
        
        Args:
            file_path: Pfad zur Export-Datei
            
        Returns:
            True wenn erfolgreich, sonst False
        """
        try:
            self._storage.export_data(file_path)
            return True
        except Exception as e:
            self._set_error(f"Fehler beim Exportieren: {str(e)}")
            return False
            
    @Slot(str)
    def import_data(self, file_path: str) -> bool:
        """
        Importiert Daten.
        
        Args:
            file_path: Pfad zur Import-Datei
            
        Returns:
            True wenn erfolgreich, sonst False
        """
        try:
            self._storage.import_data(file_path)
            return True
        except Exception as e:
            self._set_error(f"Fehler beim Importieren: {str(e)}")
            return False
            
    def _handle_message(self, message: bytes) -> None:
        """
        Verarbeitet eingehende Nachrichten.
        
        Args:
            message: Eingehende Nachricht
        """
        try:
            # Nachricht verarbeiten
            data = self._processor.process_data(message)
            if not data:
                return
                
            # Daten speichern
            self._storage.store_data(data)
            
            # Visualisierung aktualisieren
            self._visualization.update_visualization(data)
            
            # Signale senden
            self.dataReceived.emit(data.type, data.value, data.unit.value)
            self.dataProcessed.emit(data.type, data.to_dict())
            
        except Exception as e:
            self._set_error(f"Fehler bei der Nachrichtenverarbeitung: {str(e)}")
            
    def _update_visualization(self) -> None:
        """Aktualisiert die Visualisierung"""
        if self._status == TelemetryStatus.CONNECTED:
            visualization_data = self._visualization.get_visualization_data()
            self.visualizationUpdated.emit(visualization_data)
            
    def _set_status(self, status: TelemetryStatus) -> None:
        """
        Setzt den Status.
        
        Args:
            status: Neuer Status
        """
        if self._status != status:
            self._status = status
            self.statusChanged.emit(status)
            
    def _set_error(self, message: str) -> None:
        """
        Setzt eine Fehlermeldung.
        
        Args:
            message: Fehlermeldung
        """
        self._error_message = message
        self.errorOccurred.emit(message)
        self._set_status(TelemetryStatus.ERROR) 