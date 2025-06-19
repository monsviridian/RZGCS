# RZGCS Telemetrie-System

## Übersicht
Das Telemetrie-System ist ein zentraler Bestandteil des RZGCS und implementiert die Erfassung, Verarbeitung und Visualisierung von Flugzeugdaten. Die Implementierung orientiert sich an bewährten Praktiken von QGroundControl und MissionPlanner.

## Modulstruktur
```
telemetry/
├── __init__.py              # Modul-Initialisierung und Exports
├── telemetry_manager.py     # Hauptklasse für das Telemetrie-Management
├── data_types.py           # Definition der Telemetrie-Datentypen
├── data_processor.py       # Verarbeitung der Telemetrie-Daten
├── data_storage.py         # Speicherung der Telemetrie-Daten
├── data_visualization.py   # Visualisierung der Telemetrie-Daten
└── enums.py               # Enumerationen für Telemetrie-Daten
```

## Klassen-Dokumentation

### TelemetryManager (telemetry_manager.py)
Die Hauptklasse für das Telemetrie-Management, die alle Komponenten koordiniert.

#### Eigenschaften
- `status`: Aktueller Telemetrie-Status (Property)
- `data_rate`: Aktuelle Datenrate in Hz (Property)
- `last_update`: Zeitstempel der letzten Aktualisierung (Property)

#### Signale
- `dataReceived`: Wird bei Empfang neuer Daten ausgelöst
- `statusChanged`: Wird bei Statusänderungen ausgelöst
- `errorOccurred`: Wird bei Fehlern ausgelöst
- `dataRateChanged`: Wird bei Änderung der Datenrate ausgelöst

#### Methoden
```python
def start_telemetry(self) -> None:
    """Startet die Telemetrie-Erfassung"""

def stop_telemetry(self) -> None:
    """Stoppt die Telemetrie-Erfassung"""

def get_current_data(self) -> Dict:
    """
    Gibt die aktuellen Telemetrie-Daten zurück.
    
    Returns:
        Dictionary mit aktuellen Telemetrie-Daten
    """

def subscribe_to_data(self, data_type: str, callback: Callable) -> None:
    """
    Abonniert Updates für einen bestimmten Datentyp.
    
    Args:
        data_type: Typ der Telemetrie-Daten
        callback: Callback-Funktion für Updates
    """
```

### TelemetryData (data_types.py)
Basisklasse für Telemetrie-Daten.

#### Eigenschaften
- `timestamp`: Zeitstempel der Daten
- `type`: Typ der Daten
- `value`: Wert der Daten
- `unit`: Einheit der Daten

#### Methoden
```python
def to_dict(self) -> Dict:
    """Konvertiert die Daten in ein Dictionary"""

def from_dict(self, data: Dict) -> None:
    """Lädt die Daten aus einem Dictionary"""
```

### DataProcessor (data_processor.py)
Verarbeitet die rohen Telemetrie-Daten.

#### Methoden
```python
def process_data(self, raw_data: bytes) -> TelemetryData:
    """
    Verarbeitet rohe Telemetrie-Daten.
    
    Args:
        raw_data: Rohe Telemetrie-Daten
        
    Returns:
        Verarbeitete Telemetrie-Daten
    """

def validate_data(self, data: TelemetryData) -> bool:
    """
    Validiert Telemetrie-Daten.
    
    Args:
        data: Zu validierende Daten
        
    Returns:
        True wenn die Daten gültig sind, sonst False
    """
```

### DataStorage (data_storage.py)
Speichert Telemetrie-Daten.

#### Methoden
```python
def store_data(self, data: TelemetryData) -> None:
    """
    Speichert Telemetrie-Daten.
    
    Args:
        data: Zu speichernde Daten
    """

def load_data(self, start_time: datetime, end_time: datetime) -> List[TelemetryData]:
    """
    Lädt gespeicherte Telemetrie-Daten.
    
    Args:
        start_time: Startzeitpunkt
        end_time: Endzeitpunkt
        
    Returns:
        Liste der geladenen Telemetrie-Daten
    """
```

### DataVisualization (data_visualization.py)
Visualisiert Telemetrie-Daten.

#### Methoden
```python
def update_visualization(self, data: TelemetryData) -> None:
    """
    Aktualisiert die Visualisierung.
    
    Args:
        data: Zu visualisierende Daten
    """

def get_visualization_data(self) -> Dict:
    """
    Gibt die Visualisierungsdaten zurück.
    
    Returns:
        Dictionary mit Visualisierungsdaten
    """
```

## Integration in die Hauptanwendung

### 1. Connection Management Integration
```python
# In der Hauptanwendung
from backend.connection import ConnectionManager
from backend.telemetry import TelemetryManager

class MainApplication:
    def __init__(self):
        # Connection Manager initialisieren
        self.connection_manager = ConnectionManager()
        
        # Telemetry Manager initialisieren
        self.telemetry_manager = TelemetryManager()
        
        # Verbindung zwischen Connection und Telemetry herstellen
        self.connection_manager.messageReceived.connect(self.telemetry_manager.process_raw_data)
        
    def start_telemetry(self):
        # Verbindung herstellen
        settings = {
            'type': 'SERIAL',
            'port': 'COM1',
            'baudrate': 115200
        }
        self.connection_manager.connect(settings)
        
        # Telemetrie starten
        self.telemetry_manager.start_telemetry()
```

### 2. QML Integration
```qml
// In der QML-Oberfläche
import QtQuick
import QtQuick.Controls
import Backend 1.0

Item {
    // Telemetrie-Manager aus dem Backend
    property var telemetryManager: Backend.telemetryManager
    
    // Telemetrie-Daten anzeigen
    Text {
        text: "Höhe: " + telemetryManager.currentData.altitude + " m"
    }
    
    Text {
        text: "Geschwindigkeit: " + telemetryManager.currentData.speed + " m/s"
    }
    
    // Status anzeigen
    Text {
        text: "Status: " + telemetryManager.status
    }
    
    // Datenrate anzeigen
    Text {
        text: "Datenrate: " + telemetryManager.dataRate + " Hz"
    }
}
```

### 3. Datenverarbeitung
```python
# In der Hauptanwendung
class MainApplication:
    def __init__(self):
        # ... vorheriger Code ...
        
        # Callback für Telemetrie-Updates
        self.telemetry_manager.dataReceived.connect(self.handle_telemetry_data)
        
    def handle_telemetry_data(self, data):
        # Daten verarbeiten
        processed_data = self.telemetry_manager.data_processor.process_data(data)
        
        # Daten speichern
        self.telemetry_manager.data_storage.store_data(processed_data)
        
        # Visualisierung aktualisieren
        self.telemetry_manager.data_visualization.update_visualization(processed_data)
```

## Best Practices

1. **Datenverarbeitung**
   - Validierung aller eingehenden Daten
   - Effiziente Datenverarbeitung
   - Fehlerbehandlung implementieren

2. **Datenspeicherung**
   - Effiziente Speicherung der Daten
   - Regelmäßige Backups
   - Datenkompression wo sinnvoll

3. **Visualisierung**
   - Echtzeit-Updates
   - Benutzerfreundliche Darstellung
   - Konfigurierbare Anzeigen

4. **Performance**
   - Optimierte Datenverarbeitung
   - Effiziente Speichernutzung
   - Minimale Latenz

## Abhängigkeiten

- PySide6: Für QML-Integration
- numpy: Für Datenverarbeitung
- pandas: Für Datenanalyse
- matplotlib: Für Visualisierung
- sqlite3: Für Datenspeicherung

## Nächste Schritte

1. **Kurzfristig**
   - Implementierung der Basis-Telemetrie
   - Integration in die Hauptanwendung
   - Grundlegende Visualisierung

2. **Mittelfristig**
   - Erweiterte Datenverarbeitung
   - Verbesserte Visualisierung
   - Datenexport-Funktionen

3. **Langfristig**
   - KI-basierte Datenanalyse
   - Erweiterte Visualisierungsoptionen
   - Automatische Fehlererkennung 