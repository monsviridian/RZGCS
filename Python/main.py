#!/usr/bin/env python3
"""
main.py - Hauptstartskript für RZGCS

Dieses Skript dient als Einstiegspunkt für die RZGCS-Anwendung.
Es importiert und startet dronekit_main.py mit allen notwendigen Konfigurationen.
"""

import sys
import os
from pathlib import Path

# Füge das aktuelle Verzeichnis zum Python-Pfad hinzu
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def main():
    """
    Hauptfunktion zum Starten der RZGCS-Anwendung
    """
    try:
        # Importiere das Hauptmodul
        from dronekit_main import main as dronekit_main_function
        
        print("=== RZGCS Starting ===")
        print(f"Working Directory: {os.getcwd()}")
        print(f"Python Path: {sys.executable}")
        print("=====================")
    
        # Starte die Hauptanwendung
        dronekit_main_function()
        
    except ImportError as e:
        print(f"Fehler beim Importieren von dronekit_main: {e}")
        print("Stelle sicher, dass alle Abhängigkeiten installiert sind:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"Unerwarteter Fehler beim Starten der Anwendung: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
