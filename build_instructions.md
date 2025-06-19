# RZ Ground Control Station - Build-Anleitung

Diese Anleitung beschreibt den Prozess zur Erstellung von Installationspaketen für Windows, macOS, Linux und Raspberry Pi.

## Vorbereitungen

1. Stellen Sie sicher, dass alle Abhängigkeiten installiert sind:
   ```
   pip install -r requirements.txt
   ```

2. Testen Sie die Anwendung vor dem Paketieren:
   ```
   cd Python
   python main.py
   ```

## Windows-Paket erstellen

### Mit cx_Freeze (empfohlen)

1. Führen Sie den Build-Befehl aus:
   ```
   python setup.py build_exe
   ```

2. Erstellen Sie einen Windows-Installer (MSI):
   ```
   python setup.py bdist_msi
   ```

3. Die fertige Anwendung finden Sie im Ordner `build/RZGCS`
4. Das Installationspaket (MSI) finden Sie im Ordner `dist`

### Mit PyInstaller (Alternative)

1. Erstellen Sie eine spec-Datei:
   ```
   pyi-makespec --windowed --icon=Assets/icon.ico --name=RZGCS Python/main.py
   ```

2. Bearbeiten Sie die RZGCS.spec-Datei, um alle Ressourcen einzubinden
   
3. Erstellen Sie die ausführbare Datei:
   ```
   pyinstaller RZGCS.spec
   ```

4. Die fertige Anwendung finden Sie im Ordner `dist/RZGCS`

## macOS-Paket erstellen

1. Erstellen Sie eine macOS-App:
   ```
   python setup.py bdist_mac
   ```

2. Erstellen Sie eine DMG-Datei (optional, erfordert create-dmg):
   ```
   create-dmg \
     --volname "RZ Ground Control Station" \
     --volicon "Assets/icon.icns" \
     --window-pos 200 120 \
     --window-size 800 400 \
     --icon-size 100 \
     --icon "RZGCS.app" 200 190 \
     --hide-extension "RZGCS.app" \
     --app-drop-link 600 185 \
     "dist/RZGCS-1.0.0.dmg" \
     "dist/RZGCS.app"
   ```

## Linux-Paket erstellen

### Debian/Ubuntu (DEB-Paket)

1. Installieren Sie die erforderlichen Werkzeuge:
   ```
   pip install stdeb
   ```

2. Erstellen Sie das DEB-Paket:
   ```
   python setup.py --command-packages=stdeb.command bdist_deb
   ```

3. Das fertige Paket finden Sie im Ordner `deb_dist`

### Fedora/RHEL (RPM-Paket)

1. Erstellen Sie das RPM-Paket:
   ```
   python setup.py bdist_rpm
   ```

2. Das fertige Paket finden Sie im Ordner `dist`

## Raspberry Pi (ARM)

Für Raspberry Pi müssen Sie auf dem Pi-Gerät selbst oder in einer Arm-Umgebung kompilieren:

1. Klonen Sie das Repository auf dem Raspberry Pi
2. Installieren Sie die Abhängigkeiten:
   ```
   pip install -r requirements.txt
   ```
3. Erstellen Sie das Paket:
   ```
   python setup.py --command-packages=stdeb.command bdist_deb
   ```

## Startmenü-Integrationen

### Desktop-Dateien für Linux/Raspberry Pi

Erstellen Sie eine `.desktop`-Datei:

```
[Desktop Entry]
Name=RZ Ground Control Station
Comment=Kontrollstation für RZ-Drohnen
Exec=/usr/bin/rzgcs
Icon=/usr/share/pixmaps/rzgcs.png
Terminal=false
Type=Application
Categories=Utility;Science;
```

## Veröffentlichungs-Checkliste

Bevor Sie ein Paket veröffentlichen:

1. **Testen Sie die Installation** auf einem sauberen System
2. **Verifizieren Sie alle Funktionen** nach der Installation
3. **Überprüfen Sie Startmenü-Einträge** und Icons
4. **Bestätigen Sie Hardware-Kompatibilität** mit verschiedenen Flugsteuerungen
5. **Schreiben Sie Release Notes** mit Änderungen und neuen Features

## Kontinuierliche Integration (CI)

Für ein professionelles Setup empfehlen wir die Einrichtung einer CI-Pipeline mit:

- Automatische Builds für alle Plattformen
- Automatisierte Tests
- Versionierung und Tag-basierte Veröffentlichung
- Verteilung an ein Software-Repository oder eine Download-Seite

Dies kann mit GitHub Actions, GitLab CI oder Jenkins umgesetzt werden.
