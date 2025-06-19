"""
Einfaches Script zum Starten der Kartenanwendung.
Dieses Script kann direkt durch Ausführen gestartet werden.
"""

import os
import sys
import subprocess

# Pfad zum Script bestimmen
current_dir = os.path.dirname(os.path.abspath(__file__))
script_path = os.path.join(current_dir, "standalone_map.py")

print(f"Starte 3D-Kartenanwendung: {script_path}")

# Starte das Skript
os.system(f'start cmd /k python "{script_path}"')

print("3D-Kartenanwendung wurde gestartet. Dieses Fenster kann geschlossen werden.")
