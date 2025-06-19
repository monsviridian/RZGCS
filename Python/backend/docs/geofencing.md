# Geofencing

## Übersicht

Das Geofencing-Modul implementiert eine virtuelle Grenze um den Flugbereich der UAV, die verhindert, dass die UAV in unerlaubte Bereiche fliegt. Die Implementierung folgt dem MVVM-Architekturmuster und bietet eine klare Trennung zwischen Daten, Geschäftslogik und Benutzeroberfläche.

## Architektur

### Model Layer
- `geofence_data.py`: Definiert die Datenmodelle für:
  - Geofence-Typen (Polygon, Kreis, Rechteck)
  - Geofence-Parameter
  - Geofence-Status
  - Geofence-Events
  - Geofence-Statistiken

### Service Layer
- `geofence_service.py`: Implementiert die Geschäftslogik für:
  - Geofence-Management
  - Kollisionserkennung
  - Grenzüberwachung
  - Notfallprozeduren
  - Event-Handling

### ViewModel Layer
- `geofence_viewmodel.py`: Stellt die Präsentationslogik bereit:
  - Properties für die View
  - Slots für Benutzerinteraktionen
  - Signal-Handling
  - Datenbindung

### View Layer
- `geofence_view.qml`: Implementiert die Benutzeroberfläche:
  - Geofence-Konfiguration
  - Status-Anzeige
  - Visualisierung
  - Warnungen
  - Statistiken

## Geofence-Typen

### Polygon
Definiert einen beliebigen Flugbereich durch eine Liste von Koordinaten.

**Parameter:**
- `vertices`: Liste von Koordinaten (lat, lon)
- `altitude_min`: Minimale Höhe in Metern
- `altitude_max`: Maximale Höhe in Metern
- `buffer_zone`: Pufferzone in Metern
- `action`: Aktion bei Grenzüberschreitung (WARN, RETURN, LAND)

### Kreis
Definiert einen kreisförmigen Flugbereich.

**Parameter:**
- `center`: Mittelpunkt (lat, lon)
- `radius`: Radius in Metern
- `altitude_min`: Minimale Höhe in Metern
- `altitude_max`: Maximale Höhe in Metern
- `buffer_zone`: Pufferzone in Metern
- `action`: Aktion bei Grenzüberschreitung

### Rechteck
Definiert einen rechteckigen Flugbereich.

**Parameter:**
- `north_west`: Nordwest-Ecke (lat, lon)
- `south_east`: Südost-Ecke (lat, lon)
- `altitude_min`: Minimale Höhe in Metern
- `altitude_max`: Maximale Höhe in Metern
- `buffer_zone`: Pufferzone in Metern
- `action`: Aktion bei Grenzüberschreitung

## Aktionen

### WARN
Gibt eine Warnung aus, wenn die UAV die Grenze überschreitet.

**Parameter:**
- `warning_distance`: Distanz für Warnung in Metern
- `warning_altitude`: Höhe für Warnung in Metern
- `warning_interval`: Warnintervall in Sekunden
- `warning_message`: Warnmeldung

### RETURN
Führt die UAV zum Startpunkt zurück.

**Parameter:**
- `return_altitude`: Rückkehrhöhe in Metern
- `return_speed`: Rückkehrgeschwindigkeit in m/s
- `return_heading`: Rückkehrkurs in Grad
- `return_timeout`: Timeout in Sekunden

### LAND
Lässt die UAV an der aktuellen Position landen.

**Parameter:**
- `landing_speed`: Landegeschwindigkeit in m/s
- `landing_altitude`: Landehöhe in Metern
- `landing_timeout`: Timeout in Sekunden
- `emergency_landing`: Notlandung aktivieren

## Integration

### Frontend-Integration
Die QML-View kann in die Hauptanwendung integriert werden:

```qml
import QtQuick
import QtQuick.Controls
import "qrc:/flight_control/views"

ApplicationWindow {
    // ...
    
    GeofenceView {
        id: geofenceView
        viewModel: geofenceViewModel
        // ...
    }
}
```

### Backend-Integration
Der Service kann in den FlightController integriert werden:

```python
from flight_control.services.geofence_service import GeofenceService

class FlightController:
    def __init__(self):
        self.geofence_service = GeofenceService()
        # ...
```

## Fehlerbehandlung

Das Modul implementiert verschiedene Fehlerklassen:
- `GeofenceError`: Basisklasse für alle Fehler
- `GeofenceConfigError`: Fehler bei der Konfiguration
- `GeofenceValidationError`: Fehler bei der Validierung
- `GeofenceActionError`: Fehler bei der Aktion
- `GeofenceTimeoutError`: Fehler bei Timeout

## Statistiken

Das Modul sammelt verschiedene Statistiken:
- Grenzüberschreitungen
- Warnungen
- Aktionen
- Timeouts
- Flugzeit innerhalb/außerhalb
- Distanz zur Grenze
- Höhenabweichungen

## Logging

Das Modul führt ein detailliertes Log:
- Geofence-Events
- Grenzüberschreitungen
- Warnungen
- Aktionen
- Fehler
- Statistiken

## Tests

### Unit Tests
- Test der Datenmodelle
- Test der Service-Logik
- Test der ViewModel-Funktionalität

### Integration Tests
- Test der Geofence-Erkennung
- Test der Aktionen
- Test der Fehlerbehandlung

### System Tests
- Test der vollständigen Funktionalität
- Test der Benutzerinteraktion
- Test der Performance

## Best Practices

1. **Geofence-Konfiguration**
   - Sinnvolle Grenzen
   - Ausreichende Pufferzonen
   - Klare Aktionen

2. **Grenzüberwachung**
   - Kontinuierliche Prüfung
   - Frühe Warnungen
   - Präzise Erkennung

3. **Aktionen**
   - Schnelle Reaktion
   - Sichere Manöver
   - Klare Prioritäten

4. **Performance**
   - Effiziente Berechnungen
   - Minimale Latenz
   - Optimierte Speichernutzung

5. **Sicherheit**
   - Redundante Systeme
   - Notfallprozeduren
   - Systemgrenzen

## Erweiterungen

Mögliche Erweiterungen des Moduls:
1. **Neue Geofence-Typen**
   - Ellipse
   - Freiform
   - Dynamische Grenzen

2. **Erweiterte Aktionen**
   - Automatische Umleitung
   - Höhenanpassung
   - Geschwindigkeitsanpassung

3. **Verbesserte Benutzeroberfläche**
   - 3D-Visualisierung
   - Echtzeit-Updates
   - Interaktive Konfiguration

4. **Integration mit anderen Systemen**
   - Wetterdaten
   - Luftraummanagement
   - Bodenstation 