# RZGCS - Ground Control Station

## Installation

### Voraussetzungen
- Python 3.8 oder höher
- Qt 6.2 oder höher
- PySide6
- pymavlink
- CMake 3.16 oder höher

### Abhängigkeiten installieren
```bash
pip install -r requirements.txt
```

### Kompilieren
```bash
mkdir build
cd build
cmake ..
cmake --build .
```

### Ausführen
```bash
./rzgcs
```

## Funktionen

### Flugphasen
- DISARMED: System deaktiviert
- ARMED: System aktiviert
- TAKEOFF: Startphase
- FLYING: Normaler Flugbetrieb
- LANDING: Landephase
- LANDED: Gelandet
- ERROR: Fehlerzustand
- EMERGENCY: Notfallzustand

### Hauptkomponenten
- Preflight-Check
- Parameter-Verwaltung
- Sensor-Überwachung
- Kalibrierung
- Motor-Test
- Flugsteuerung
- Angel-Mode
- Lizenzverwaltung
- Support
- SITL-Simulation
- Store

### Sicherheit
- Automatische Fehlererkennung
- Sicherheitsüberwachung
- Notfallprozeduren
- Missionsüberwachung

## Entwicklung

### Projektstruktur
```
RZGCSContent/
├── RZGCS/
│   ├── main.py              # Hauptanwendung
│   ├── backend_bridge.py    # Backend-Integration
│   ├── App.qml             # Hauptfenster
│   ├── FlightPhaseIndicator.qml  # Flugphasen-Anzeige
│   └── ...                 # Weitere QML-Komponenten
```

### MAVLink-Integration
- Automatische Verbindungserkennung
- Echtzeit-Telemetrie
- Missionssteuerung
- Fehlerbehandlung

### Frontend
- Modernes Qt/QML-Interface
- Responsive Design
- Echtzeit-Updates
- Intuitive Bedienung

## Lizenz
Proprietär - Alle Rechte vorbehalten 