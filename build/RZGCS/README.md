# RZGCS - Drone Control System

Eine benutzerfreundliche Drohnen-Steuerungssoftware für Mac.

## Installation

1. **Python installieren**
   - Besuchen Sie [python.org](https://www.python.org/downloads/)
   - Laden Sie die neueste Python-Version für Mac herunter
   - Führen Sie den Installer aus und folgen Sie den Anweisungen

2. **Software herunterladen**
   - Laden Sie die neueste Version von RZGCS herunter
   - Entpacken Sie die ZIP-Datei in einen Ordner Ihrer Wahl

3. **Abhängigkeiten installieren**
   - Öffnen Sie das Terminal (über Spotlight-Suche oder Programme/Dienstprogramme)
   - Navigieren Sie zum RZGCS-Ordner:
     ```bash
     cd /Pfad/zu/RZGCS
     ```
   - Führen Sie das Installationsskript aus:
     ```bash
     ./install_mac.sh
     ```

## Starten der Software

1. **Einfacher Start**
   - Doppelklicken Sie auf die Datei `start_mac.command` im RZGCS-Ordner
   - Die Software startet automatisch

2. **Manueller Start**
   - Öffnen Sie das Terminal
   - Navigieren Sie zum RZGCS-Ordner
   - Führen Sie aus:
     ```bash
     python main.py
     ```

## Verwendung

1. **Verbindung herstellen**
   - Wählen Sie den richtigen COM-Port aus
   - Klicken Sie auf "Verbinden"

2. **Drohne steuern**
   - Die Sensordaten werden automatisch angezeigt
   - Logs zeigen den Status der Drohne
   - Wichtige Warnungen werden rot hervorgehoben

## Fehlerbehebung

Falls die Software nicht startet:
1. Prüfen Sie, ob Python korrekt installiert ist
2. Führen Sie das Installationsskript erneut aus
3. Starten Sie den Computer neu

Bei weiteren Problemen kontaktieren Sie bitte den Support.

## Systemanforderungen

- macOS 10.15 oder neuer
- Python 3.8 oder neuer
- 4GB RAM
- 500MB freier Speicherplatz

## Features

- Echtzeit-Sensorüberwachung
- MAVLink-Protokoll-Integration
- Konfigurierbares Logging-System
- Motorsteuerung und -tests
- Benutzerfreundliche QML-Oberfläche

## Entwicklung

### Codequalität

Das Projekt verwendet:
- Black für Codeformatierung
- MyPy für statische Typüberprüfung
- Flake8 für Linting

Ausführen der Qualitätschecks:
```bash
black Python/
mypy Python/
flake8 Python/
```

### Tests

Tests ausführen:
```bash
pytest Python/tests/
```

## Projektstruktur

```
.
├── Python/
│   ├── backend/
│   │   ├── sensorviewmodel.py   # Sensor-Datenmodell
│   │   ├── serial_connector.py  # Serielle Kommunikation
│   │   ├── mavsdk_connector.py # MAVLink-Integration
│   │   └── logger.py           # Logging-System
│   └── tests/
│       └── test_sensorviewmodel.py
├── App/                        # QML-Frontend
└── requirements.txt
```

## Konfiguration

Die Anwendung kann über Umgebungsvariablen oder `config.json` konfiguriert werden:

- `DRONE_DEFAULT_PORT`: Serieller Port (Standard: COM8)
- `DRONE_DEFAULT_BAUDRATE`: Baudrate (Standard: 57600)
- `DRONE_LOG_LEVEL`: Log-Level (DEBUG, INFO, WARNING, ERROR)

## Fehlerbehandlung

Das System verwendet benutzerdefinierte Exceptions für verschiedene Fehlerszenarien:

- `ConnectionException`: Verbindungsprobleme
- `SensorException`: Sensorfehler
- `MotorException`: Motorfehler
- `CalibrationException`: Kalibrierungsfehler

## Beitragen

1. Fork erstellen
2. Feature Branch erstellen (`git checkout -b feature/AmazingFeature`)
3. Änderungen committen (`git commit -m 'Add some AmazingFeature'`)
4. Branch pushen (`git push origin feature/AmazingFeature`)
5. Pull Request erstellen

## Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert. 