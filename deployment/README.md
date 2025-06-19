# RZGCS Deployment Guide

Diese Anleitung erklu00e4rt, wie Sie RZGCS fu00fcr verschiedene Plattformen bauen und verteilen ku00f6nnen.

## Voraussetzungen

- Python 3.8 oder neuer
- PyQt5
- PyInstaller (`pip install pyinstaller`)
- Qt-Entwicklungstools fu00fcr die jeweilige Plattform

## Deployment fu00fcr alle Plattformen

Verwenden Sie das Hauptskript, um den Build-Prozess zu starten:

```
powershell -ExecutionPolicy Bypass -File build_all.ps1
```

Dieses Skript fu00fchrt Sie durch den Prozess und ermu00f6glicht die Auswahl der Zielplattform.

## Plattformspezifische Anweisungen

### Windows

1. Fu00fchren Sie das Windows-Build-Skript aus:
   ```
   powershell -ExecutionPolicy Bypass -File build_windows.ps1
   ```

2. Fu00fcr die Installer-Erstellung wird Inno Setup benu00f6tigt:
   - Herunterladen von [Inno Setup](https://jrsoftware.org/isdl.php)
   - Installieren und sicherstellen, dass es im Standardpfad installiert ist

3. Die fertige Setup-Datei befindet sich in `build/installer/RZGCS_Setup.exe`

### macOS

1. Fu00fchren Sie das macOS-Build-Skript auf einem Mac aus:
   ```
   chmod +x build_macos.sh
   ./build_macos.sh
   ```

2. Die App befindet sich in `build/macos/RZGCS.app`
3. Der DMG-Installer ist in `build/installer/RZGCS_Installer.dmg`

### Linux

1. Fu00fchren Sie das Linux-Build-Skript auf einem Linux-System aus:
   ```
   chmod +x build_linux.sh
   ./build_linux.sh
   ```

2. Die ausfu00fchrbare Datei befindet sich in `build/linux/RZGCS/RZGCS`
3. Fu00fcr AppImage-Erstellung wird `appimagetool` benu00f6tigt
4. Fu00fcr DEB-Pakete wird `dpkg-deb` benu00f6tigt

### Raspberry Pi OS

1. Fu00fchren Sie das Raspberry Pi-Build-Skript auf einem Raspberry Pi aus:
   ```
   chmod +x build_raspberrypi.sh
   ./build_raspberrypi.sh
   ```

2. Die ausfu00fchrbare Datei befindet sich in `build/raspberrypi/RZGCS/RZGCS`
3. Das Installationspaket ist in `build/installer/RZGCS-RaspberryPi.tar.gz`

## Cross-Plattform-Hinweise

- Die Skripte sind so konzipiert, dass sie die richtige Qt-Version automatisch finden und einbinden
- Achten Sie darauf, dass alle Abhu00e4ngigkeiten korrekt eingebunden sind
- Fu00fcr Raspberry Pi OS-Builds ku00f6nnen zusu00e4tzliche Qt-Pakete erforderlich sein

## Lizenzierung

Beachten Sie, dass die erstellten Installationspakete alle Lizenzinformationen aus LICENSE.md und THIRD_PARTY_LICENSES.md enthalten. Diese werden wu00e4hrend der Installation angezeigt und mit der Anwendung installiert.

## Bekannte Probleme

- Auf einigen Linux-Distributionen ku00f6nnen zusu00e4tzliche Bibliotheken erforderlich sein
- macOS-Builds mu00fcssen auf einem Mac erstellt werden
- Fu00fcr optimale Performance auf dem Raspberry Pi sollte eine Raspberry Pi 4 mit mindestens 4GB RAM verwendet werden
