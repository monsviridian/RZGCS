# Autonome Flugmodi

## Übersicht

Das autonome Flugmodul implementiert verschiedene Flugmodi für die UAV-Steuerung, die eine präzise und sichere Flugführung ermöglichen. Die Implementierung folgt dem MVVM-Architekturmuster und bietet eine klare Trennung zwischen Daten, Geschäftslogik und Benutzeroberfläche.

## Architektur

### Model Layer
- `autonomous_data.py`: Definiert die Datenmodelle für:
  - Flugmodi (Position Hold, Return to Launch, Follow Me, Waypoint)
  - Status und Parameter
  - Zustand und Statistiken
  - Events und Logs
  - Fehlerbehandlung

### Service Layer
- `autonomous_service.py`: Implementiert die Geschäftslogik für:
  - Modus-Management
  - Parameter-Validierung
  - Zustandsaktualisierung
  - Fortschrittsberechnung
  - Statistik-Sammlung
  - Event-Handling

### ViewModel Layer
- `autonomous_viewmodel.py`: Stellt die Präsentationslogik bereit:
  - Properties für die View
  - Slots für Benutzerinteraktionen
  - Signal-Handling
  - Datenbindung

### View Layer
- `autonomous_view.qml`: Implementiert die Benutzeroberfläche:
  - Modus-Auswahl
  - Parameter-Konfiguration
  - Status-Anzeige
  - Positionsanzeige
  - Statistik-Darstellung

## Flugmodi

### Position Hold
Hält die UAV an einer festen Position und Höhe.

**Parameter:**
- `target_altitude`: Zielhöhe in Metern
- `target_heading`: Zielkurs in Grad
- `position_tolerance`: Toleranz für Positionsabweichung in Metern
- `heading_tolerance`: Toleranz für Kursabweichung in Grad
- `max_speed`: Maximale Geschwindigkeit in m/s
- `wind_compensation`: Windkompensation aktivieren/deaktivieren

### Return to Launch
Führt die UAV zum Startpunkt zurück.

**Parameter:**
- `return_altitude`: Rückkehrhöhe in Metern
- `approach_altitude`: Anflughöhe in Metern
- `approach_speed`: Anfluggeschwindigkeit in m/s
- `landing_speed`: Landegeschwindigkeit in m/s
- `max_speed`: Maximale Geschwindigkeit in m/s
- `abort_altitude`: Abbruchhöhe in Metern

### Follow Me
Folgt einem bewegten Ziel in konstantem Abstand.

**Parameter:**
- `target_distance`: Zieldistanz in Metern
- `target_altitude`: Zielhöhe in Metern
- `max_speed`: Maximale Geschwindigkeit in m/s
- `min_distance`: Minimale Distanz in Metern
- `max_distance`: Maximale Distanz in Metern
- `altitude_offset`: Höhenoffset in Metern

### Waypoint
Fliegt eine vordefinierte Route ab.

**Parameter:**
- `waypoint_radius`: Waypoint-Radius in Metern
- `waypoint_speed`: Waypoint-Geschwindigkeit in m/s
- `waypoint_altitude`: Waypoint-Höhe in Metern
- `waypoint_heading`: Waypoint-Kurs in Grad
- `waypoint_loiter_time`: Loiter-Zeit in Sekunden
- `waypoint_loiter_radius`: Loiter-Radius in Metern

## Integration

### Frontend-Integration
Die QML-View kann in die Hauptanwendung integriert werden:

```qml
import QtQuick
import QtQuick.Controls
import "qrc:/flight_control/views"

ApplicationWindow {
    // ...
    
    AutonomousView {
        id: autonomousView
        viewModel: autonomousViewModel
        // ...
    }
}
```

### Backend-Integration
Der Service kann in den FlightController integriert werden:

```python
from flight_control.services.autonomous_service import AutonomousService

class FlightController:
    def __init__(self):
        self.autonomous_service = AutonomousService()
        # ...
```

## Fehlerbehandlung

Das Modul implementiert verschiedene Fehlerklassen:
- `AutonomousError`: Basisklasse für alle Fehler
- `ModeActivationError`: Fehler bei der Modusaktivierung
- `ParameterError`: Fehler bei den Parametern
- `PositionError`: Fehler bei der Positionsbestimmung
- `HeadingError`: Fehler bei der Kursbestimmung
- `SpeedError`: Fehler bei der Geschwindigkeitsbestimmung
- `AltitudeError`: Fehler bei der Höhenbestimmung

## Statistiken

Das Modul sammelt verschiedene Statistiken:
- Flugzeit und Distanz
- Geschwindigkeiten (Durchschnitt, Max, Min)
- Höhen (Durchschnitt, Max, Min)
- Moduswechsel und Fehler
- Erfolgsrate
- Batterieverbrauch
- Modus-spezifische Zeiten

## Logging

Das Modul führt ein detailliertes Log:
- Events mit Zeitstempel
- Modus- und Statusänderungen
- Positions- und Kursaktualisierungen
- Fehler und Warnungen
- Statistiken

## Tests

### Unit Tests
- Test der Datenmodelle
- Test der Service-Logik
- Test der ViewModel-Funktionalität

### Integration Tests
- Test der Modus-Übergänge
- Test der Parameter-Validierung
- Test der Fehlerbehandlung

### System Tests
- Test der vollständigen Funktionalität
- Test der Benutzerinteraktion
- Test der Performance

## Best Practices

1. **Modus-Aktivierung**
   - Prüfen der Systemvoraussetzungen
   - Validieren der Parameter
   - Sichere Übergänge zwischen Modi

2. **Parameter-Konfiguration**
   - Sinnvolle Standardwerte
   - Grenzen für Parameter
   - Validierung der Eingaben

3. **Fehlerbehandlung**
   - Sofortige Reaktion auf Fehler
   - Klare Fehlermeldungen
   - Automatische Wiederherstellung

4. **Performance**
   - Effiziente Zustandsaktualisierung
   - Optimierte Berechnungen
   - Minimale Latenz

5. **Sicherheit**
   - Prüfung der Systemgrenzen
   - Notfallprozeduren
   - Redundante Systeme

## Erweiterungen

Mögliche Erweiterungen des Moduls:
1. **Neue Flugmodi**
   - Orbit
   - Survey
   - Formation

2. **Erweiterte Parameter**
   - Wetterabhängige Anpassungen
   - Batterieoptimierung
   - Kollisionsvermeidung

3. **Verbesserte Benutzeroberfläche**
   - 3D-Visualisierung
   - Echtzeit-Telemetrie
   - Erweiterte Statistiken

4. **Integration mit anderen Systemen**
   - Wetterdaten
   - Luftraummanagement
   - Bodenstation 