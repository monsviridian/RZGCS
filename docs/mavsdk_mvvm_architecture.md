# RZGCS MAVSDK-MVVM Architektur Dokumentation

## Übersicht

Die RZGCS (RoboZeppelin Ground Control Station) ist eine Bodenstation zur Steuerung von Drohnen, die auf einer MVVM-Architektur (Model-View-ViewModel) basiert und MAVSDK für die Kommunikation mit Drohnen verwendet. Die Anwendung bietet eine benutzerfreundliche Oberfläche mit QML und nutzt PySide6 als Qt-Binding für Python.

## Abhängigkeiten

### Kernabhängigkeiten
- **Python**: 3.10.0 oder höher
- **PySide6**: 6.8.2.1 oder höher (Qt-Binding für Python)
- **MAVSDK**: Neueste Version (für Drohnenkommunikation)
- **PySerial**: Neueste Version (für COM-Port-Verwaltung)

### Zusätzliche Abhängigkeiten
- **Material Design**: Für QML-Styling (via `QT_QUICK_CONTROLS_STYLE=Material`)
- **Threading**: Python-Standard-Threading-Modul für asynchrone Operationen
- **Asyncio**: Für asynchrone Kommunikation mit MAVSDK

## Installation

```bash
# Basis-Abhängigkeiten installieren
pip install PySide6==6.8.2.1
pip install mavsdk
pip install pyserial

# Repository klonen
git clone https://github.com/yourusername/RZGCS.git
cd RZGCS
```

## Projektstruktur

```
RZGCS/
├── Python/                 # Hauptverzeichnis für Python-Code
│   ├── backend/            # Backend-Services und Dienstprogramme
│   │   └── logger.py       # Logger-Implementierung
│   ├── rzgcs/              # Kern-RZGCS-Modul
│   │   ├── mvvm/           # MVVM-Implementierung
│   │   │   ├── service/    # Dienste (MAVSDK, Verbindungen, etc.)
│   │   │   │   └── mavsdk_connection_helper.py
│   │   │   ├── mavsdk_drone_view_model.py
│   │   │   ├── qml_compatibility_adapter.py
│   │   │   └── enhanced_drone_view_model.py
│   │   └── ui/             # UI-Helfer und -Adapter
│   │       └── qml_style_helper.py
│   ├── minimal_mavsdk_mvvm.py  # Minimales Beispiel
│   ├── mavsdk_rzgcs_mvvm.py    # Vollständige Integration
│   └── test_system_info_filter.py # Testskript
├── RZGCSContent/           # QML-Dateien und UI-Ressourcen
│   ├── App.qml             # Hauptanwendungs-QML
│   ├── FlightView.ui.qml   # Flugansicht
│   ├── PreflightView.ui.qml # Preflight-Ansicht
│   ├── MotorTestView.ui.qml # Motortest-Ansicht
│   └── Screen01.ui.qml     # Erste Bildschirmansicht
└── docs/                   # Dokumentation
    └── mavsdk_mvvm_architecture.md # Diese Datei
```

## Architektur

### MVVM-Architektur

Die RZGCS folgt dem Model-View-ViewModel (MVVM) Architekturmuster:

1. **Model**: Enthält die Kernlogik und Daten
   - MAVSDK-Dienste und -Datenstrukturen
   - Kommunikation mit der Drohne über MAVLink

2. **ViewModel**: Dient als Bindeglied zwischen Model und View
   - `MAVSDKDroneViewModel`: Hauptimplementierung für Drohnensteuerung
   - `QMLCompatibilityAdapter`: Brücke für QML-Kompatibilität
   - `EnhancedDroneViewModel`: Erweiterte Funktionen

3. **View**: Die Benutzeroberfläche
   - QML-Dateien (FlightView, PreflightView, MotorTestView)
   - Material Design-Styling

### Kommunikationsfluss

```
┌──────────────┐      ┌───────────────────┐      ┌───────────────┐
│ QML UI       │<─────┤ Compatibility     │<─────┤ DroneViewModel│
│ (View)       │      │ Adapter           │      │ (ViewModel)   │
└──────────────┘      └───────────────────┘      └───────┬───────┘
                                                         │
                                                  ┌──────▼───────┐
                                                  │ MAVSDK       │
                                                  │ (Model)      │
                                                  └──────┬───────┘
                                                         │
                                                  ┌──────▼───────┐
                                                  │ Drohne       │
                                                  │ (Hardware)   │
                                                  └──────────────┘
```

## Hauptkomponenten

### 1. MAVSDKConnectionHelper

Verantwortlich für die Verbindung zu Drohnen und die Verwaltung von Telemetrie-Streams.

**Hauptfunktionen:**
- `connect_to_drone`: Verbindet zur Drohne mit verschiedenen Verbindungstypen
- `subscribe_to_telemetry`: Abonniert Telemetrie-Datenströme
- `extract_baudrate`: Extrahiert Baudrate aus Verbindungsstrings

### 2. MAVSDKDroneViewModel

Hauptschnittstelle zwischen UI und Drohnen-Diensten.

**Wichtige Eigenschaften:**
- `ports`: Liste verfügbarer COM-Ports
- `is_connected`: Verbindungsstatus
- `attitude`: Lage-Informationen (Roll, Pitch, Yaw)

**Hauptmethoden:**
- `connectToDrone`: Verbindet zur Drohne
- `disconnect`: Trennt die Verbindung
- `refreshPorts`: Aktualisiert die Liste der verfügbaren Ports

### 3. QMLCompatibilityAdapter

Überbrückt die Lücke zwischen MVVM-Signalen und QML-Erwartungen.

**Hauptfunktionen:**
- Signalumwandlung für QML-Kompatibilität
- Einheitliche Methoden für QML-Zugriff
- Motorsteuerung und Animation

### 4. Logger

Spezialisierter Logger für Systemereignisse und Fehler.

**Besonderheiten:**
- Filterung von Systeminformationen
- Verbesserte Darstellung in der Preflight-View
- Hervorhebung wichtiger Informationen

## Verbindungssteuerung

### Unterstützte Verbindungsformate:

- **COM-Port**: `COM3` oder `COM3:115200` (mit Baudrate)
- **UDP**: `udp://127.0.0.1:14550`
- **TCP**: `tcp://192.168.1.1:5760`
- **Serial**: `serial:///dev/ttyACM0:57600`

### Verbindungsprozess:

1. Der Benutzer wählt einen Verbindungstyp aus
2. Der `QMLCompatibilityAdapter` empfängt den Befehl und leitet ihn weiter
3. `MAVSDKDroneViewModel` verarbeitet die Anfrage
4. `MAVSDKConnectionHelper` stellt die tatsächliche Verbindung her
5. Statusaktualisierungen werden zurück an die UI gesendet

## Motorsteuerung

Die Motorsteuerung ermöglicht Tests und Animation von Motoraktivitäten:

- **Einzelmotortest**: Aktiviert einen einzelnen Motor für Tests
- **Motorsequenz**: Führt eine Testsequenz für alle Motoren durch
- **Notabschaltung**: Stoppt alle Motoren sofort

## Systeminfo-Filterung

Der spezialisierte Filtermechanismus für die Preflight-View:

1. Filtert Systeminformationen:
   - Frame-Typ (z.B. "Quad X")
   - RCOut-Werte
   - Hardware (MicoAir743, ChibiOS)
   - ArduCopter-Version
   - PreArm-Warnungen

2. Verbessert die Anzeige:
   - Vergrößerter Log-Bereich (30% statt 10% der Höhe)
   - Größere Schrift (16px)
   - Hervorhebung (fett) für bessere Lesbarkeit

## Ausführungsscripte

### 1. minimal_mavsdk_mvvm.py

Minimalbeispiel für die MAVSDK-MVVM-Integration mit grundlegenden Funktionen.

```bash
python minimal_mavsdk_mvvm.py
```

### 2. mavsdk_rzgcs_mvvm.py

Vollständige RZGCS-Anwendung mit allen Funktionen.

```bash
python mavsdk_rzgcs_mvvm.py
```

### 3. test_system_info_filter.py

Testet die Systeminfo-Filterung mit simulierten Daten.

```bash
python test_system_info_filter.py
```

## Entwicklungsrichtlinien

### Code-Organisation

- Folgen Sie dem MVVM-Muster strikt
- Halten Sie Dienste in `service/`-Verzeichnissen
- UI-Logik gehört in ViewModel-Klassen
- Direkte Hardware-Kommunikation nur im Model

### Signalbenennung

- Verwenden Sie konsequente Namenskonventionen für Signale
- QML-Signale sollten mit 'Changed' enden (z.B. `attitudeChanged`)
- Für Kompatibilität mit vorhandenen QML-Dateien Legacy-Namen beibehalten

### Asynchrone Programmierung

- Verwenden Sie `asyncio` für MAVSDK-Kommunikation
- Verwenden Sie Threads für UI-blockierende Operationen
- Vermeiden Sie blockierende Aufrufe im Hauptthread

## Fehlerbehandlung

Die Anwendung implementiert robuste Fehlerbehandlung:

- Verbindungstimeouts mit anpassbarer Dauer
- Wiederherstellung nach Verbindungsabbrüchen
- Benutzerfreundliche Fehlermeldungen
- Umfangreiche Protokollierung für Debugging

## Zukünftige Erweiterungen

Mögliche Erweiterungen für zukünftige Versionen:

1. **Erweiterte Missionsplanung**: Waypoint-Verwaltung, Geofencing
2. **Verbesserte Telemetrie-Visualisierung**: 3D-Darstellung, Karten
3. **Multi-Drohnen-Unterstützung**: Verwaltung mehrerer Drohnenverbindungen
4. **Konfigurationsverwaltung**: Speichern und Laden von Drohnenkonfigurationen
5. **Autopilot-Integration**: Erweiterte ArduPilot/PX4-Integrationen

## Lizenz

[Ihre Lizenzinformationen hier]

## Mitwirkende

[Liste der Mitwirkenden]
