# Flugsteuerungs-System

Das Flugsteuerungs-System ist ein zentraler Bestandteil des RZGCS und ermöglicht die Steuerung und Überwachung von UAVs (Unmanned Aerial Vehicles).

## Architektur

Das System ist in drei Hauptkomponenten aufgeteilt:

1. **Datenmodelle** (`models/`)
   - Definieren die Datenstrukturen und Zustände
   - Implementieren Validierungslogik
   - Verwalten Fehlerbehandlung

2. **Service** (`services/`)
   - Implementiert die Geschäftslogik
   - Verwaltet den Flugzustand
   - Führt Flugoperationen aus
   - Sammelt Statistiken
   - Führt Logging durch

3. **ViewModel** (`viewmodels/`)
   - Verbindet Service und UI
   - Verwaltet UI-Zustand
   - Leitet Benutzerinteraktionen weiter
   - Aktualisiert UI-Daten

## Funktionalitäten

### 1. Flugmodi
- **STABILIZE**: Stabilisierungsmodus
- **ALTHOLD**: Höhenhaltemodus
- **LOITER**: Positionierungsmodus
- **RTL**: Return-to-Launch
- **AUTO**: Automatischer Modus
- **GUIDED**: Geführter Modus
- **MANUAL**: Manueller Modus

### 2. Flugstatus
- **INACTIVE**: Inaktiv
- **READY**: Bereit
- **ARMING**: Wird scharfgeschaltet
- **ARMED**: Scharfgeschaltet
- **TAKING_OFF**: Startet
- **FLYING**: Im Flug
- **LANDING**: Landet
- **ERROR**: Fehlerzustand

### 3. Flugoperationen
- Aktivierung/Deaktivierung
- Scharfschalten/Entschärfen
- Moduswechsel
- Start
- Landung
- Positionsaktualisierungen
- Geschwindigkeitsaktualisierungen

### 4. Statistiken
- Gesamtflüge
- Gesamtflugzeit
- Gesamtdistanz
- Maximale Höhe
- Maximale Geschwindigkeit
- Landungen/Starts
- Fehler
- Moduswechsel

### 5. Logging
- Event-Protokollierung
- Fehlerprotokollierung
- Statusänderungen
- Moduswechsel
- Flugoperationen

### 6. Fehlerbehandlung
- Validierungsfehler
- Befehlsfehler
- Modusfehler
- Allgemeine Fehler

## Benutzeroberfläche

Die Benutzeroberfläche bietet:

1. **Statusanzeige**
   - Aktiver Status
   - Fehlerstatus
   - Flugmodus
   - Flugstatus
   - Arming-Status

2. **Steuerungselemente**
   - Aktivierung/Deaktivierung
   - Arming/Disarming
   - Modusauswahl
   - Start/Landung

3. **Statistik-Dashboard**
   - Flugstatistiken
   - Echtzeit-Updates
   - Grafische Darstellung

4. **Log-Viewer**
   - Event-Liste
   - Fehlerprotokoll
   - Statusänderungen

## Sicherheit

Das System implementiert mehrere Sicherheitsmaßnahmen:

1. **Validierung**
   - Modusvalidierung
   - Statusvalidierung
   - Positionsvalidierung
   - Geschwindigkeitsvalidierung

2. **Fehlerbehandlung**
   - Robuste Fehlerbehandlung
   - Benutzerbenachrichtigungen
   - Fehlerprotokollierung

3. **Zustandsverwaltung**
   - Sichere Zustandsübergänge
   - Statusüberwachung
   - Automatische Fehlerbehandlung

## Erweiterbarkeit

Das System ist modular aufgebaut und kann erweitert werden:

1. **Neue Flugmodi**
   - Modus-Definition
   - Modus-Logik
   - UI-Integration

2. **Neue Statistiken**
   - Statistik-Definition
   - Datenerfassung
   - UI-Darstellung

3. **Neue Operationen**
   - Operations-Definition
   - Service-Integration
   - UI-Integration

## Verwendung

### Service-Initialisierung
```python
service = FlightControlService()
service.activate()
```

### Moduswechsel
```python
service.set_mode(FlightMode.STABILIZE)
```

### Start/Landung
```python
service.arm()
service.takeoff()
service.land()
service.disarm()
```

### Positionsaktualisierung
```python
service.update_position({
    'latitude': 48.137154,
    'longitude': 11.576124,
    'altitude': 100.0
})
```

### Geschwindigkeitsaktualisierung
```python
service.update_velocity({
    'vx': 10.0,
    'vy': 0.0,
    'vz': 0.0
})
```

## Fehlerbehandlung

### Validierungsfehler
```python
try:
    service.set_mode(FlightMode.STABILIZE)
except FlightValidationError as e:
    print(f"Validierungsfehler: {e}")
```

### Befehlsfehler
```python
try:
    service.takeoff()
except FlightCommandError as e:
    print(f"Befehlsfehler: {e}")
```

### Modusfehler
```python
try:
    service.set_mode(FlightMode.AUTO)
except FlightModeError as e:
    print(f"Modusfehler: {e}") 