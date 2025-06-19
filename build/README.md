# RZ Ground Control Station

## Überblick

Die RZ Ground Control Station ist eine professionelle Bodenanwendung zur Steuerung und Überwachung von RZ-Drohnen. Diese Software unterstützt die Konfiguration, Überwachung und Steuerung aller RZ-Drohnenmodelle und bietet eine intuitive 3D-Visualisierung in Echtzeit.

## Inhaltsverzeichnis

1. [Systemanforderungen](#systemanforderungen)
2. [Installation](#installation)
   - [Windows](#windows-installation)
   - [macOS](#macos-installation)
   - [Linux](#linux-installation)
   - [Raspberry Pi](#raspberry-pi-installation)
3. [Starten der Anwendung](#starten-der-anwendung)
4. [Funktionen](#funktionen)
5. [Fehlerbehebung](#fehlerbehebung)
6. [Support](#support)

## Systemanforderungen

- **Betriebssystem**:
  - Windows 10/11
  - macOS 10.14 oder höher
  - Ubuntu 20.04 oder höher
  - Raspberry Pi OS (Bullseye oder höher)
- **Hardware**:
  - Prozessor: Dual-Core 1.5 GHz oder höher
  - RAM: Mindestens 2GB (4GB empfohlen)
  - Grafikfähigkeiten: OpenGL 2.0+ kompatible Grafikkarte
  - Speicherplatz: Mindestens 200 MB freier Speicherplatz
- **Software**:
  - Python 3.8 oder höher

## Installation

### Windows-Installation

1. Entpacken Sie die Datei `RZGCS-distribution.zip` an einen beliebigen Ort.
2. Stellen Sie sicher, dass Python 3.8 oder höher installiert ist.
   - Falls nicht, laden Sie es von [python.org](https://www.python.org/downloads/) herunter und installieren Sie es. 
   - **Wichtig**: Aktivieren Sie die Option "Add Python to PATH" während der Installation.
3. Führen Sie die Datei `install.bat` im entpackten Ordner aus, um alle erforderlichen Abhängigkeiten zu installieren.
4. Optional: Führen Sie `create_shortcut.bat` aus, um eine Desktop-Verknüpfung zu erstellen.

### macOS-Installation

1. Entpacken Sie die Datei `RZGCS-distribution.zip` an einen beliebigen Ort.
2. Stellen Sie sicher, dass Python 3.8 oder höher installiert ist.
   - Falls nicht, installieren Sie es über Homebrew: `brew install python` oder laden Sie es von [python.org](https://www.python.org/downloads/) herunter.
3. Öffnen Sie das Terminal und navigieren Sie zum entpackten Ordner:
   ```bash
   cd /pfad/zum/entpackten/RZGCS-Ordner
   ```
4. Installieren Sie die erforderlichen Abhängigkeiten:
   ```bash
   pip3 install -r requirements.txt
   ```
5. Erstellen Sie ein Startskript:
   ```bash
   echo '#!/bin/bash' > start_rzgcs.sh
   echo 'cd "$(dirname "$0")"' >> start_rzgcs.sh
   echo 'python3 Python/main.py' >> start_rzgcs.sh
   chmod +x start_rzgcs.sh
   ```

### Linux-Installation

1. Entpacken Sie die Datei `RZGCS-distribution.zip` an einen beliebigen Ort.
2. Stellen Sie sicher, dass Python 3.8 oder höher installiert ist:
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip python3-venv
   ```
3. Öffnen Sie das Terminal und navigieren Sie zum entpackten Ordner:
   ```bash
   cd /pfad/zum/entpackten/RZGCS-Ordner
   ```
4. Installieren Sie die erforderlichen Abhängigkeiten:
   ```bash
   pip3 install -r requirements.txt
   ```
5. Erstellen Sie ein Startskript:
   ```bash
   echo '#!/bin/bash' > start_rzgcs.sh
   echo 'cd "$(dirname "$0")"' >> start_rzgcs.sh
   echo 'python3 Python/main.py' >> start_rzgcs.sh
   chmod +x start_rzgcs.sh
   ```
6. Optional: Erstellen Sie einen Desktop-Eintrag:
   ```bash
   echo '[Desktop Entry]' > ~/.local/share/applications/rzgcs.desktop
   echo 'Name=RZ Ground Control Station' >> ~/.local/share/applications/rzgcs.desktop
   echo 'Exec=/pfad/zum/entpackten/RZGCS-Ordner/start_rzgcs.sh' >> ~/.local/share/applications/rzgcs.desktop
   echo 'Icon=/pfad/zum/entpackten/RZGCS-Ordner/Assets/icon.svg' >> ~/.local/share/applications/rzgcs.desktop
   echo 'Type=Application' >> ~/.local/share/applications/rzgcs.desktop
   echo 'Categories=Utility;Science;' >> ~/.local/share/applications/rzgcs.desktop
   ```

### Raspberry Pi-Installation

1. Entpacken Sie die Datei `RZGCS-distribution.zip` an einen beliebigen Ort.
2. Stellen Sie sicher, dass die erforderlichen Pakete installiert sind:
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip python3-pyqt5 python3-opengl
   ```
3. Installieren Sie die erforderlichen Python-Abhängigkeiten:
   ```bash
   pip3 install -r requirements.txt
   ```
4. Erstellen Sie ein Startskript:
   ```bash
   echo '#!/bin/bash' > start_rzgcs.sh
   echo 'cd "$(dirname "$0")"' >> start_rzgcs.sh
   echo 'python3 Python/main.py' >> start_rzgcs.sh
   chmod +x start_rzgcs.sh
   ```
5. Für eine optimale Leistung empfehlen wir, die GPU-Speicherzuweisung anzupassen:
   ```bash
   sudo nano /boot/config.txt
   ```
   Fügen Sie die folgende Zeile hinzu oder bearbeiten Sie sie:
   ```
   gpu_mem=128
   ```

## Starten der Anwendung

### Windows
Doppelklicken Sie auf `start_rzgcs.bat` oder auf die von Ihnen erstellte Desktop-Verknüpfung.

### macOS/Linux/Raspberry Pi
Führen Sie das Skript `start_rzgcs.sh` aus:
```bash
./start_rzgcs.sh
```

## Funktionen

Die RZ Ground Control Station bietet folgende Funktionen:

- **RZ Store**: Durchsuchen und Visualisieren verschiedener RZ-Drohnenmodelle in 3D
- **Preflight-Checks**: Überprüfen der Drohnensysteme vor dem Flug
- **Parametereinstellungen**: Anpassen von Flugcontroller-Parametern
- **Sensordaten**: Echtzeit-Anzeige aller Sensordaten
- **Flugansicht**: Steuerung und Überwachung der Drohne während des Fluges
- **Sprachunterstützung**: Vollständig in Englisch und mehrsprachig erweiterbar

## Fehlerbehebung

### Verbindungsprobleme

- **Drohne wird nicht erkannt**:
  - Überprüfen Sie, ob die Drohne eingeschaltet ist
  - Stellen Sie sicher, dass der richtige COM-Port/Gerät ausgewählt ist
  - Überprüfen Sie die USB-Verbindung und Kabel

### Anwendungsprobleme

- **Anwendung startet nicht**:
  - Überprüfen Sie, ob Python korrekt installiert ist
  - Stellen Sie sicher, dass alle Abhängigkeiten installiert wurden
  - Überprüfen Sie die Konsole auf Fehlermeldungen

- **3D-Ansicht wird nicht angezeigt**:
  - Überprüfen Sie, ob Ihre Grafikkarte OpenGL 2.0 oder höher unterstützt
  - Aktualisieren Sie Ihre Grafiktreiber

## Support

Bei Fragen oder Problemen wenden Sie sich bitte an:

- E-Mail: support@rz-robotics.com
- Website: [www.rz-robotics.com](https://www.rz-robotics.com)
- Telefon: +49 123 456789

---

© 2025 RZ Robotics GmbH. Alle Rechte vorbehalten.
