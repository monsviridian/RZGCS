# Parameter Management System - DroneKit/PyMAVLink Integration

## Übersicht

Das Parameter-Management-System wurde erfolgreich in die RZGCS-Anwendung integriert und ermöglicht das automatische Laden, Anzeigen, Bearbeiten und Speichern von MAVLink-Parametern vom Flugcontroller.

## Implementierte Komponenten

### 1. ParameterManager (backend/parameter_manager.py)

**Hauptfunktionen:**
- Automatisches Laden aller Parameter vom Flugcontroller nach Verbindung
- Parameter setzen mit korrekter Typ-Konvertierung (UINT8, INT8, UINT16, INT16, UINT32, INT32, REAL32)
- Parameter in Datei speichern und laden
- Filterung von Parametern nach Namen
- QML-kompatible Signals für UI-Updates

**Wichtige Methoden:**
```python
loadAllParameters()  # Lädt alle Parameter vom FC
setParameter(name, value)  # Setzt einen Parameter
saveToFile(filename)  # Speichert Parameter in Datei
loadFromFile(filename)  # Lädt Parameter aus Datei
filterParameters(filter_text)  # Filtert Parameter
```

**Signals:**
- `parametersLoaded(count)` - Parameter geladen
- `parameterUpdated(name, value, type)` - Parameter aktualisiert
- `parameterSet(name, value, success)` - Parameter gesetzt
- `loadingStatusChanged(loading, status)` - Loading-Status geändert
- `errorOccurred(error)` - Fehler aufgetreten

### 2. DroneKitParameterViewModel (dronekit_parameter_viewmodel.py)

**QML-Integration:**
- ParameterListModel für Parameter-Liste
- Properties für QML-Zugriff
- Slots für QML-Aktionen
- Automatische UI-Updates

**Properties:**
- `parameterModel` - Parameter-Liste für QML
- `refreshInProgress` - Loading-Status
- `categories` - Parameter-Kategorien

**Slots:**
- `refreshParameters()` - Parameter laden
- `writeParameter(name, value)` - Parameter setzen
- `setFilterText(text)` - Filter setzen
- `setShowModifiedOnly(show)` - Nur geänderte anzeigen
- `clearModified()` - Änderungen löschen
- `set_parameter_value(name, value)` - Parameter-Wert setzen

### 3. ParameterTab.qml

**UI-Features:**
- Moderne, responsive Benutzeroberfläche
- Parameter-Tabelle mit editierbaren Werten
- Live-Filterung nach Parameter-Namen
- Loading-Indikator während des Ladens
- Status-Anzeige
- Speichern/Laden von Parameter-Dateien

**Funktionen:**
- Automatisches Laden nach Verbindung
- Direkte Bearbeitung von Parameter-Werten
- Filterung in Echtzeit
- Fehlerbehandlung mit MessageManager-Integration

## Integration in die Hauptanwendung

### dronekit_main.py

**Initialisierung:**
```python
# Parameter-Manager erstellen
parameter_manager = ParameterManager()
parameter_viewmodel = DroneKitParameterViewModel(serial_connector)

# Mit MAVLink-Verbindung verbinden
serial_connector.connectedChanged.connect(lambda connected: 
    parameter_manager.set_mavlink_connection(
        serial_connector.mavlink_connector.connection if connected else None
    )
)

# ParameterViewModel mit SerialConnector verbinden
serial_connector.connectedChanged.connect(lambda connected:
    parameter_viewmodel.set_drone_connector(serial_connector if connected else None)
)

# Automatisches Parameter-Laden nach Verbindung
serial_connector.connectedChanged.connect(lambda connected:
    parameter_viewmodel.refreshParameters() if connected else None
)
```

**QML-Context Properties:**
```python
engine.rootContext().setContextProperty("parameterViewModel", parameter_viewmodel)
engine.rootContext().setContextProperty("parameterModel", parameter_viewmodel.parameterModel)
```

## Automatischer Workflow

1. **Verbindung herstellen** → MAVLink-Connector verbindet sich mit FC
2. **ParameterManager initialisieren** → ParameterManager erhält MAVLink-Verbindung
3. **ParameterViewModel verbinden** → DroneKitParameterViewModel erhält SerialConnector
4. **Parameter automatisch laden** → refreshParameters() wird aufgerufen
5. **UI-Updates** → Parameter werden in der Tabelle angezeigt
6. **Benutzer-Interaktion** → Parameter können bearbeitet, gefiltert und gespeichert werden

## Parameter-Typen Unterstützung

Das System unterstützt alle MAVLink-Parameter-Typen:
- **UINT8** - 8-bit unsigned integer
- **INT8** - 8-bit signed integer  
- **UINT16** - 16-bit unsigned integer
- **INT16** - 16-bit signed integer
- **UINT32** - 32-bit unsigned integer
- **INT32** - 32-bit signed integer
- **REAL32** - 32-bit float

## Parameter-Kategorien

Das System kategorisiert Parameter automatisch:
- **Armierung** - ARMING_*
- **Batterie** - BATT_*
- **Board** - BRD_*
- **Kompass** - COMPASS_*
- **EKF** - EK2_*, EK3_*
- **Geo-Fence** - FENCE_*
- **Flugmodi** - FLTMODE*
- **GPS** - GPS_*
- **IMU** - INS_*
- **Logging** - LOG_*
- **Mission** - MIS_*
- **Motor** - MOT_*
- **Pilot** - PILOT_*
- **Fernbedienung** - RC*
- **Servos** - SERVO*
- **Telemetrie** - SR0_*, SR1_*, SR2_*, SR3_*

## Datei-Format

Parameter werden im Standard-MAVLink-Format gespeichert:
```
PARAMETER_NAME    value
PARAMETER_NAME2   value2
```

## Fehlerbehandlung

- **Verbindungsfehler** → Automatische Fehlermeldungen über MessageManager
- **Parameter-Lade-Fehler** → Timeout nach 30 Sekunden
- **Parameter-Set-Fehler** → 3 Retry-Versuche mit ACK-Prüfung
- **Datei-Fehler** → Exception-Handling mit Benutzer-Feedback

## Performance-Optimierungen

- **Lazy Loading** → Parameter werden nur bei Bedarf geladen
- **Efficient Updates** → Nur geänderte Parameter werden aktualisiert
- **Memory Management** → Parameter werden effizient im Dictionary gespeichert
- **UI Responsiveness** → Loading-Indikatoren und Status-Updates
- **Write Queue** → Parameter-Schreibvorgänge werden in Warteschlange verarbeitet

## Verwendung

### Automatisch (nach Verbindung)
1. Verbindung zum Flugcontroller herstellen
2. Parameter werden automatisch geladen
3. Parameter-Tab zeigt alle verfügbaren Parameter

### Manuell
1. "Laden"-Button klicken → Parameter neu laden
2. Filter-Text eingeben → Parameter filtern
3. Parameter-Wert bearbeiten → Enter drücken zum Speichern
4. "Speichern"-Button → Parameter in Datei speichern

## Nächste Schritte

- [ ] Parameter-Gruppen und Kategorien
- [ ] Parameter-Backup und -Wiederherstellung
- [ ] Parameter-Vergleich zwischen Dateien
- [ ] Parameter-Validierung und -Bereiche
- [ ] Erweiterte Filter-Optionen
- [ ] Parameter-Statistiken und -Analysen

## Technische Details

### MAVLink-Protokoll
- Verwendet `PARAM_VALUE` Messages zum Laden
- Verwendet `PARAM_SET` Messages zum Setzen
- Automatische ACK-Prüfung für zuverlässige Übertragung

### QML-Integration
- Context Properties für einfachen Zugriff
- Signals/Slots für reaktive Updates
- Model/View-Pattern für effiziente Darstellung

### Threading
- Parameter-Laden läuft asynchron
- UI bleibt während des Ladens responsiv
- Thread-sichere Signal-Kommunikation

### Schreibwarteschlange
- Parameter-Schreibvorgänge werden in Warteschlange verarbeitet
- Verhindert Überlastung des Flugcontrollers
- Automatische Fehlerbehandlung und Wiederholung

Das Parameter-Management-System ist vollständig funktionsfähig und bereit für den produktiven Einsatz! 