#!/usr/bin/env python3
"""
Listet alle QML-Dateien auf, die von dronekit_main.py über Importpfade erreichbar sind.
"""
import os
from pathlib import Path

# Hauptverzeichnis für QML-Content
qml_root = Path(__file__).parent / 'RZGCSContent'

qml_files = []
for root, dirs, files in os.walk(qml_root):
    for file in files:
        if file.endswith('.qml') or file.endswith('.ui.qml'):
            qml_files.append(str(Path(root) / file))

print(f"Gefundene QML-Dateien in {qml_root} und Unterordnern:")
for qml in sorted(qml_files):
    print(qml)

print(f"\nAnzahl QML-Dateien: {len(qml_files)}") 