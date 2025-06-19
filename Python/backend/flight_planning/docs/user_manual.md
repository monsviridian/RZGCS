# Flugplanungs-Benutzerhandbuch

## Übersicht

Die Flugplanung ermöglicht die Erstellung, Verwaltung und Ausführung von Flugmissionen mit definierten Routen und Wegpunkten.

## Benutzeroberfläche

Die Benutzeroberfläche ist in drei Hauptbereiche unterteilt:

1. **Linke Seite**: Missions- und Routenverwaltung
2. **Mittlere Seite**: Wegpunktverwaltung
3. **Rechte Seite**: Log und Steuerung

### Missions- und Routenverwaltung

#### Missions-Panel

- **Status**: Zeigt den aktuellen Missionsstatus an
  - INACTIVE: Mission inaktiv
  - ACTIVE: Mission aktiv
  - PAUSED: Mission pausiert
  - COMPLETED: Mission abgeschlossen
  - ERROR: Mission fehlerhaft

- **Aktionen**
  - "Neue Mission": Erstellt eine neue Mission
  - "Mission starten": Startet die aktuelle Mission
  - "Pausieren/Fortsetzen": Pausiert oder setzt die Mission fort
  - "Mission beenden": Schließt die Mission ab
  - "Mission abbrechen": Bricht die Mission ab

#### Routen-Panel

- **Routen-Liste**: Zeigt alle Routen der aktuellen Mission an
- **Aktionen**
  - "Route hinzufügen": Fügt eine neue Route hinzu

### Wegpunktverwaltung

#### Wegpunkte-Panel

- **Wegpunkte-Liste**: Zeigt alle Wegpunkte der aktuellen Route an
- **Aktionen**
  - "Wegpunkt hinzufügen": Fügt einen neuen Wegpunkt hinzu
  - "Wegpunkt bearbeiten": Bearbeitet den ausgewählten Wegpunkt
  - "Wegpunkt löschen": Löscht den ausgewählten Wegpunkt

#### Aktueller Wegpunkt

- **Details**: Zeigt Details des ausgewählten Wegpunkts an
  - ID: Eindeutige ID des Wegpunkts
  - Typ: Typ des Wegpunkts
  - Aktion: Aktion am Wegpunkt
  - Position: Position des Wegpunkts (Latitude, Longitude, Altitude)

### Log und Steuerung

#### Log-Panel

- **Log-Liste**: Zeigt alle Events der Mission an
- **Letztes Event**: Zeigt das letzte Event an

#### Steuerungs-Panel

- **Aktionen**
  - "Nächster Wegpunkt": Geht zum nächsten Wegpunkt

## Missionsverwaltung

### Neue Mission erstellen

1. Klicken Sie auf "Neue Mission"
2. Geben Sie den Namen der Mission ein
3. Klicken Sie auf "OK"

### Mission starten

1. Wählen Sie die Mission aus
2. Klicken Sie auf "Mission starten"

### Mission pausieren

1. Während die Mission aktiv ist, klicken Sie auf "Pausieren"
2. Die Mission wird pausiert

### Mission fortsetzen

1. Während die Mission pausiert ist, klicken Sie auf "Fortsetzen"
2. Die Mission wird fortgesetzt

### Mission beenden

1. Während die Mission aktiv ist, klicken Sie auf "Mission beenden"
2. Die Mission wird abgeschlossen

### Mission abbrechen

1. Während die Mission aktiv oder pausiert ist, klicken Sie auf "Mission abbrechen"
2. Die Mission wird abgebrochen

## Routenverwaltung

### Neue Route hinzufügen

1. Klicken Sie auf "Route hinzufügen"
2. Geben Sie den Namen der Route ein
3. Klicken Sie auf "OK"

## Wegpunktverwaltung

### Neuen Wegpunkt hinzufügen

1. Wählen Sie die Route aus
2. Klicken Sie auf "Wegpunkt hinzufügen"
3. Geben Sie die Wegpunkt-Details ein:
   - Typ: TAKEOFF, LANDING, WAYPOINT, HOLD, SURVEY, ACTION
   - Aktion: NONE, PHOTO, VIDEO, SCAN, DROP, PICKUP
   - Position: Latitude, Longitude, Altitude
4. Klicken Sie auf "OK"

### Wegpunkt bearbeiten

1. Wählen Sie den Wegpunkt aus
2. Klicken Sie auf "Wegpunkt bearbeiten"
3. Ändern Sie die gewünschten Details
4. Klicken Sie auf "OK"

### Wegpunkt löschen

1. Wählen Sie den Wegpunkt aus
2. Klicken Sie auf "Wegpunkt löschen"
3. Bestätigen Sie die Löschung

## Missionssteuerung

### Zum nächsten Wegpunkt gehen

1. Während die Mission aktiv ist, klicken Sie auf "Nächster Wegpunkt"
2. Die Mission geht zum nächsten Wegpunkt

## Fehlerbehandlung

### Missionsfehler

Wenn ein Fehler auftritt:

1. Die Mission wird auf ERROR gesetzt
2. Eine Fehlermeldung wird angezeigt
3. Das Event wird im Log protokolliert

### Validierungsfehler

Wenn ein Validierungsfehler auftritt:

1. Eine Fehlermeldung wird angezeigt
2. Die Aktion wird abgebrochen
3. Das Event wird im Log protokolliert

### Kommandofehler

Wenn ein Kommandofehler auftritt:

1. Eine Fehlermeldung wird angezeigt
2. Die Aktion wird abgebrochen
3. Das Event wird im Log protokolliert

## Tipps und Tricks

### Effiziente Missionsplanung

1. Planen Sie die Route im Voraus
2. Verwenden Sie sinnvolle Wegpunkt-Typen
3. Definieren Sie klare Aktionen
4. Testen Sie die Mission vor dem Start

### Fehlervermeidung

1. Überprüfen Sie alle Eingaben
2. Validieren Sie die Route
3. Testen Sie die Mission
4. Überwachen Sie das Log

### Performance-Optimierung

1. Minimieren Sie die Anzahl der Wegpunkte
2. Verwenden Sie effiziente Routen
3. Optimieren Sie die Aktionen
4. Überwachen Sie die Performance

## Häufige Fragen

### Wie erstelle ich eine neue Mission?

1. Klicken Sie auf "Neue Mission"
2. Geben Sie den Namen ein
3. Klicken Sie auf "OK"

### Wie füge ich eine Route hinzu?

1. Klicken Sie auf "Route hinzufügen"
2. Geben Sie den Namen ein
3. Klicken Sie auf "OK"

### Wie füge ich einen Wegpunkt hinzu?

1. Wählen Sie die Route aus
2. Klicken Sie auf "Wegpunkt hinzufügen"
3. Geben Sie die Details ein
4. Klicken Sie auf "OK"

### Wie starte ich eine Mission?

1. Wählen Sie die Mission aus
2. Klicken Sie auf "Mission starten"

### Wie pausiere ich eine Mission?

1. Während die Mission aktiv ist, klicken Sie auf "Pausieren"

### Wie setze ich eine Mission fort?

1. Während die Mission pausiert ist, klicken Sie auf "Fortsetzen"

### Wie beende ich eine Mission?

1. Während die Mission aktiv ist, klicken Sie auf "Mission beenden"

### Wie breche ich eine Mission ab?

1. Während die Mission aktiv oder pausiert ist, klicken Sie auf "Mission abbrechen"

### Was bedeuten die verschiedenen Wegpunkt-Typen?

- TAKEOFF: Startpunkt
- LANDING: Landepunkt
- WAYPOINT: Normaler Wegpunkt
- HOLD: Wartepunkt
- SURVEY: Vermessungspunkt
- ACTION: Aktionspunkt

### Was bedeuten die verschiedenen Aktionen?

- NONE: Keine Aktion
- PHOTO: Foto aufnehmen
- VIDEO: Video aufnehmen
- SCAN: Scannen
- DROP: Abwerfen
- PICKUP: Aufnehmen

### Wie überwache ich die Mission?

1. Beobachten Sie den Missionsstatus
2. Überwachen Sie das Log
3. Verfolgen Sie den aktuellen Wegpunkt
4. Achten Sie auf Fehlermeldungen 