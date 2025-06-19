#!/usr/bin/env python3
"""
Startskript für RZGCS mit korrekter Pfadkonfiguration
"""

import os
import sys
import subprocess

def main():
    # Projektverzeichnis finden
    current_dir = os.path.dirname(os.path.abspath(__file__))
    python_dir = os.path.join(current_dir, "Python")
    
    # Pythonpfad setzen
    sys.path.insert(0, python_dir)
    
    # RZGCS als Modul ausführen
    print("Starte RZGCS mit MAVSDK-Integration...")
    from rzgcs.application import main
    sys.exit(main())

if __name__ == "__main__":
    main()
