"""
Datenspeicher für das Telemetrie-System.
Speichert und lädt Telemetrie-Daten.
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
import os
from .data_types import TelemetryData, TelemetryDataFactory
from .enums import TelemetryDataType

class DataStorage:
    """Speichert und lädt Telemetrie-Daten"""
    
    def __init__(self, storage_dir: str = "telemetry_data"):
        """
        Initialisiert den Datenspeicher.
        
        Args:
            storage_dir: Verzeichnis für die Datenspeicherung
        """
        self._storage_dir = Path(storage_dir)
        self._storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Datenbank-Verbindung
        self._db_path = self._storage_dir / "telemetry.db"
        self._conn = None
        self._cursor = None
        
        # Datenbank initialisieren
        self._init_database()
        
    def _init_database(self) -> None:
        """Initialisiert die SQLite-Datenbank"""
        self._conn = sqlite3.connect(str(self._db_path))
        self._cursor = self._conn.cursor()
        
        # Tabelle für Telemetrie-Daten erstellen
        self._cursor.execute("""
            CREATE TABLE IF NOT EXISTS telemetry_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                type TEXT NOT NULL,
                value REAL,
                unit TEXT NOT NULL,
                data_json TEXT NOT NULL
            )
        """)
        
        # Indizes erstellen
        self._cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp ON telemetry_data(timestamp)
        """)
        self._cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_type ON telemetry_data(type)
        """)
        
        self._conn.commit()
        
    def store_data(self, data: TelemetryData) -> None:
        """
        Speichert Telemetrie-Daten.
        
        Args:
            data: Zu speichernde Daten
        """
        if not self._cursor:
            return
            
        # Daten in JSON konvertieren
        data_json = json.dumps(data.to_dict())
        
        # Daten in Datenbank speichern
        self._cursor.execute("""
            INSERT INTO telemetry_data (timestamp, type, value, unit, data_json)
            VALUES (?, ?, ?, ?, ?)
        """, (
            data.timestamp.isoformat(),
            data.type.value,
            data.value,
            data.unit.value,
            data_json
        ))
        
        self._conn.commit()
        
    def load_data(self, start_time: datetime, end_time: datetime, data_type: Optional[TelemetryDataType] = None) -> List[TelemetryData]:
        """
        Lädt gespeicherte Telemetrie-Daten.
        
        Args:
            start_time: Startzeitpunkt
            end_time: Endzeitpunkt
            data_type: Optional: Typ der zu ladenden Daten
            
        Returns:
            Liste der geladenen Telemetrie-Daten
        """
        if not self._cursor:
            return []
            
        # SQL-Query erstellen
        query = """
            SELECT data_json FROM telemetry_data
            WHERE timestamp BETWEEN ? AND ?
        """
        params = [start_time.isoformat(), end_time.isoformat()]
        
        # Datentyp-Filter hinzufügen
        if data_type:
            query += " AND type = ?"
            params.append(data_type.value)
            
        # Daten laden
        self._cursor.execute(query, params)
        rows = self._cursor.fetchall()
        
        # Daten in TelemetryData-Objekte konvertieren
        result = []
        for row in rows:
            data_dict = json.loads(row[0])
            data = TelemetryDataFactory.create_data(
                TelemetryDataType(data_dict['type']),
                data_dict['value'],
                data_dict['unit']
            )
            result.append(data)
            
        return result
        
    def get_data_types(self) -> List[TelemetryDataType]:
        """
        Gibt alle gespeicherten Datentypen zurück.
        
        Returns:
            Liste der Datentypen
        """
        if not self._cursor:
            return []
            
        self._cursor.execute("""
            SELECT DISTINCT type FROM telemetry_data
        """)
        rows = self._cursor.fetchall()
        
        return [TelemetryDataType(row[0]) for row in rows]
        
    def get_data_range(self, data_type: TelemetryDataType) -> Dict[str, datetime]:
        """
        Gibt den Zeitbereich der gespeicherten Daten zurück.
        
        Args:
            data_type: Typ der Daten
            
        Returns:
            Dictionary mit Start- und Endzeitpunkt
        """
        if not self._cursor:
            return {}
            
        self._cursor.execute("""
            SELECT MIN(timestamp), MAX(timestamp)
            FROM telemetry_data
            WHERE type = ?
        """, (data_type.value,))
        
        row = self._cursor.fetchone()
        if not row or not row[0] or not row[1]:
            return {}
            
        return {
            'start': datetime.fromisoformat(row[0]),
            'end': datetime.fromisoformat(row[1])
        }
        
    def clear_data(self, before_time: Optional[datetime] = None) -> None:
        """
        Löscht gespeicherte Daten.
        
        Args:
            before_time: Optional: Löscht nur Daten vor diesem Zeitpunkt
        """
        if not self._cursor:
            return
            
        if before_time:
            self._cursor.execute("""
                DELETE FROM telemetry_data
                WHERE timestamp < ?
            """, (before_time.isoformat(),))
        else:
            self._cursor.execute("DELETE FROM telemetry_data")
            
        self._conn.commit()
        
    def export_data(self, file_path: str, start_time: datetime, end_time: datetime, data_type: Optional[TelemetryDataType] = None) -> bool:
        """
        Exportiert Daten in eine JSON-Datei.
        
        Args:
            file_path: Pfad der Export-Datei
            start_time: Startzeitpunkt
            end_time: Endzeitpunkt
            data_type: Optional: Typ der zu exportierenden Daten
            
        Returns:
            True wenn der Export erfolgreich war, sonst False
        """
        try:
            # Daten laden
            data = self.load_data(start_time, end_time, data_type)
            
            # Daten in JSON konvertieren
            export_data = [d.to_dict() for d in data]
            
            # JSON-Datei speichern
            with open(file_path, 'w') as f:
                json.dump(export_data, f, indent=2)
                
            return True
            
        except Exception as e:
            print(f"Fehler beim Exportieren der Daten: {str(e)}")
            return False
            
    def import_data(self, file_path: str) -> bool:
        """
        Importiert Daten aus einer JSON-Datei.
        
        Args:
            file_path: Pfad der Import-Datei
            
        Returns:
            True wenn der Import erfolgreich war, sonst False
        """
        try:
            # JSON-Datei laden
            with open(file_path, 'r') as f:
                import_data = json.load(f)
                
            # Daten in TelemetryData-Objekte konvertieren und speichern
            for data_dict in import_data:
                data = TelemetryDataFactory.create_data(
                    TelemetryDataType(data_dict['type']),
                    data_dict['value'],
                    data_dict['unit']
                )
                self.store_data(data)
                
            return True
            
        except Exception as e:
            print(f"Fehler beim Importieren der Daten: {str(e)}")
            return False
            
    def __del__(self):
        """Schließt die Datenbank-Verbindung"""
        if self._conn:
            self._conn.close() 