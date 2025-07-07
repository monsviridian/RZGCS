# RZGCS Windows Deployment

## 🎯 Übersicht

Dieses Deployment enthält die vollständige RZGCS-Anwendung für Windows mit:
- **Portable Version** (ZIP-Archiv)
- **Windows-Installer** (Batch-Skript)
- **Ein-Klick-Start** ohne Python-Installation

## 📁 Dateien

### Portable Version
- **`RZGCS_Portable.zip`** - Portable Version zum direkten Ausführen
  - Enthält `RZGCS.exe` und alle Abhängigkeiten
  - Kann auf USB-Stick oder beliebigem Ordner entpackt werden
  - Keine Installation erforderlich

### Windows-Installer
- **`install_RZGCS.bat`** - Einfacher Windows-Installer
  - Installiert RZGCS in `C:\Program Files\RZGCS`
  - Erstellt Startmenü-Verknüpfung
  - Benötigt Administrator-Rechte

### Build-Dateien
- **`dist/RZGCS/`** - PyInstaller-Build-Verzeichnis
  - `RZGCS.exe` - Hauptanwendung (9MB)
  - `_internal/` - Alle Python-Abhängigkeiten

## 🚀 Installation

### Option 1: Portable Version
1. `RZGCS_Portable.zip` entpacken
2. `RZGCS.exe` doppelklicken
3. Fertig! 🎉

### Option 2: Windows-Installer
1. `install_RZGCS.bat` als Administrator ausführen
2. Installation bestätigen
3. RZGCS über Startmenü starten

## 🔧 Technische Details

### PyInstaller-Build
```bash
pyinstaller --clean --noconfirm --name RZGCS --windowed \
  --add-data "RZGCSContent;RZGCSContent" \
  --add-data "Python;Python" \
  --icon "RZGCSContent/Assets/logo_base.png" \
  Python/dronekit_main.py
```

### Eingebettete Komponenten
- ✅ PySide6 (Qt-Bindings)
- ✅ PyMAVLink (MAVLink-Protokoll)
- ✅ NumPy, Matplotlib
- ✅ Alle QML-Dateien und Assets
- ✅ Python-Backend-Module

### Systemanforderungen
- Windows 10/11 (64-bit)
- Keine Python-Installation erforderlich
- ~50MB Speicherplatz

## 🎨 Features

### UI-Komponenten
- **Connection View** - MAVLink-Verbindung
- **Flight View** - Flugdaten und Navigation
- **Parameter View** - Flugcontroller-Parameter
- **Firmware View** - Firmware-Management
- **Calibration View** - Sensor-Kalibrierung
- **MAVLink 2 Tab** - Erweiterte MAVLink-Features

### Backend-Features
- **PyMAVLink-Integration** - Direkte FC-Kommunikation
- **Parameter-Management** - Lesen/Schreiben von Parametern
- **Telemetrie** - GPS, Attitude, Battery
- **Kalibrierung** - Sensor-Kalibrierung
- **Firmware-Update** - FC-Firmware-Updates

## 🔍 Troubleshooting

### App startet nicht
- Prüfen Sie Windows Defender/Antivirus
- Als Administrator ausführen
- Visual C++ Redistributable installieren

### Keine Verbindung
- COM-Port-Treiber installieren
- Baudrate prüfen (Standard: 115200)
- FC muss MAVLink unterstützen

## 📝 Changelog

### Version 1.0
- ✅ PyInstaller-Build erfolgreich
- ✅ Logo integriert
- ✅ Portable Version erstellt
- ✅ Windows-Installer erstellt
- ✅ Ein-Klick-Start implementiert

## 🎯 Nächste Schritte

1. **macOS-Build** - App-Bundle mit DMG-Installer
2. **Linux-Build** - AppImage und DEB-Paket
3. **Auto-Updater** - Automatische Updates
4. **Code-Signing** - Digitale Signatur

---

**RZGCS Windows Deployment erfolgreich abgeschlossen!** 🎉 