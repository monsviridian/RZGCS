# RZGCS macOS Deployment Guide

## Voraussetzungen

- macOS 10.15 oder höher
- Qt 6.2 oder höher
- Python 3.8 oder höher
- PySide6

## Build-Umgebung einrichten

1. Installieren Sie die Abhängigkeiten:

```bash
pip install PySide6 pymavlink base64
```

2. Stellen Sie sicher, dass Qt für macOS korrekt installiert ist

## Anwendung für macOS verpacken

### Methode 1: Py2App

Py2App ist ein Tool, das Python-Anwendungen in eigenständige macOS-Anwendungen umwandelt.

1. Installieren Sie py2app:

```bash
pip install py2app
```

2. Erstellen Sie eine `setup.py`-Datei im Hauptverzeichnis:

```python
from setuptools import setup

APP = ['Python/main.py']
DATA_FILES = [
    ('RZGCSContent', ['RZGCSContent']),
    ('Assets', ['Assets']),
    ('Python', ['Python']),
    ('RZGCS', ['RZGCS'])
]
OPTIONS = {
    'argv_emulation': True,
    'packages': ['PySide6'],
    'includes': ['PySide6.QtCore', 'PySide6.QtGui', 'PySide6.QtQml', 'pymavlink'],
    'iconfile': 'Assets/icon.icns',
    'plist': {
        'CFBundleName': 'RZGCS',
        'CFBundleDisplayName': 'RZGCS Drone Control',
        'CFBundleVersion': '1.0.0',
        'CFBundleIdentifier': 'com.rzgcs.dronecontrol',
        'NSHumanReadableCopyright': 'Copyright © 2025 RZGCS',
        'CFBundleDevelopmentRegion': 'English'
    }
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
```

3. Führen Sie den Build-Befehl aus:

```bash
python setup.py py2app
```

### Methode 2: Qt für macOS Deployment

1. Verwenden Sie `macdeployqt` (Teil von Qt):

```bash
macdeployqt RZGCS.app -qmldir=RZGCSContent
```

## Signieren der Anwendung

Für die Distribution im App Store oder außerhalb des App Stores müssen Sie die App signieren:

```bash
codesign --force --sign "Developer ID Application: YOUR_DEVELOPER_ID" RZGCS.app
```

## DMG-Datei erstellen

Für die einfache Distribution können Sie eine DMG-Datei erstellen:

```bash
hdiutil create -volname "RZGCS" -srcfolder RZGCS.app -ov -format UDZO RZGCS.dmg
```

## Notizen zur macOS-Kompatibilität

- Dateipfade: Stellen Sie sicher, dass alle Dateipfade plattformunabhängig sind
- Berechtigungen: Die Anwendung benötigt Berechtigungen für den Zugriff auf serielle Ports
- Sandboxing: Für App Store Distribution müssen Sie das Sandboxing einrichten

## Bekannte Probleme

- Die Lizenzprüfung muss für jeden Plattform-Fingerabdruck angepasst werden
- USB-Geräte-Erkennung funktioniert auf macOS anders als auf Windows
