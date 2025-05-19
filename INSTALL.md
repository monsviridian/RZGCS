# RZ Ground Control Station - Installationsanleitung

Die RZ Ground Control Station ist ein professionelles Werkzeug zur Steuerung und Überwachung von RZ-Drohnen. Diese Anleitung erklärt, wie Sie die Software auf verschiedenen Betriebssystemen installieren können.

## Installation der kompilierten Version

### Windows

1. Laden Sie die neueste `RZGCS-Windows.zip` von der Release-Seite herunter.
2. Entpacken Sie die ZIP-Datei an einen beliebigen Ort.
3. Starten Sie die Anwendung durch Doppelklick auf `RZGCS.exe`.
4. Bei der ersten Ausführung können Sie Windows-Sicherheitswarnungen erhalten - wählen Sie "Trotzdem ausführen".

### macOS

1. Laden Sie die neueste `RZGCS-macOS.dmg` von der Release-Seite herunter.
2. Öffnen Sie die DMG-Datei und ziehen Sie die RZGCS-Anwendung in Ihren Anwendungsordner.
3. Bei der ersten Ausführung müssen Sie möglicherweise:
   - Rechtsklick auf die App → Öffnen
   - In den Systemeinstellungen unter "Sicherheit" die Ausführung erlauben

### Linux (Debian/Ubuntu)

1. Laden Sie die neueste `rzgcs_1.0.0_amd64.deb` von der Release-Seite herunter.
2. Installieren Sie das Paket mit dem Befehl:
   ```
   sudo dpkg -i rzgcs_1.0.0_amd64.deb
   sudo apt-get install -f  # Falls Abhängigkeiten fehlen
   ```
3. Starten Sie die Anwendung über das Anwendungsmenü oder durch Eingabe von `rzgcs` im Terminal.

### Raspberry Pi (Raspberry Pi OS)

1. Laden Sie die neueste `rzgcs_1.0.0_armhf.deb` von der Release-Seite herunter.
2. Installieren Sie das Paket mit dem Befehl:
   ```
   sudo dpkg -i rzgcs_1.0.0_armhf.deb
   sudo apt-get install -f  # Falls Abhängigkeiten fehlen
   ```
3. Starten Sie die Anwendung über das Anwendungsmenü oder durch Eingabe von `rzgcs` im Terminal.

## Kompilierung aus dem Quellcode

### Voraussetzungen

- Python 3.8 oder höher
- Pip (Python-Paketmanager)
- Git (für den Quellcode-Download)

### Schritte zur Kompilierung

1. Klonen Sie das Repository:
   ```
   git clone https://github.com/rzrobotics/rzgcs.git
   cd rzgcs
   ```

2. Installieren Sie die Abhängigkeiten:
   ```
   pip install -r requirements.txt
   ```

3. Kompilieren Sie die Anwendung:

   **Windows:**
   ```
   python setup.py build_exe
   ```
   Die kompilierte Anwendung finden Sie im Ordner `build/RZGCS`.

   **macOS:**
   ```
   python setup.py bdist_mac
   ```
   Die App finden Sie im Ordner `dist`.

   **Linux:**
   ```
   python setup.py bdist_rpm  # Für RPM-basierte Systeme (Fedora, RHEL)
   # oder
   python setup.py bdist_deb  # Für Debian-basierte Systeme (mit zusätzlichem Tool)
   ```

4. (Optional) Erstellen Sie ein Installationspaket:
   ```
   python setup.py bdist_msi  # Windows MSI-Installer
   # oder
   python setup.py bdist_dmg  # macOS DMG-Datei
   ```

## Systemanforderungen

- **Betriebssystem**: Windows 10/11, macOS 10.14+, Ubuntu 20.04+, Raspberry Pi OS (Bullseye+)
- **RAM**: Mindestens 2GB (4GB empfohlen)
- **Prozessor**: Dual-Core 1.5 GHz oder höher
- **Grafikfähigkeiten**: OpenGL 2.0+ kompatible Grafikkarte
- **Laufwerksplatz**: Mindestens 200 MB freier Speicherplatz

## Verbindung mit Drohnen

Stellen Sie sicher, dass die entsprechenden Treiber für Ihre Flugsteuerung installiert sind:

- **Windows**: Benötigt möglicherweise zusätzliche USB-Treiber für FTDI- oder Silabs-Chips
- **macOS/Linux**: Sollte standardmäßig funktionieren, möglicherweise sind Berechtigungen für den seriellen Port erforderlich

## Fehlerbehebung

Bei Verbindungsproblemen:

1. Überprüfen Sie, ob der richtige COM-Port/Gerät ausgewählt ist
2. Stellen Sie sicher, dass die korrekte Baudrate eingestellt ist (Standard: 115200)
3. Überprüfen Sie die USB-Verbindung und Kabel

Bei Startproblemen:

1. Stellen Sie sicher, dass alle Abhängigkeiten installiert sind
2. Überprüfen Sie die Zugriffsrechte auf die Anwendungsdateien
3. Konsultieren Sie die Dokumentation oder wenden Sie sich an den Support

## Support und Updates

Besuchen Sie unsere Website für Updates und Support: [www.rz-robotics.com](https://www.rz-robotics.com)
