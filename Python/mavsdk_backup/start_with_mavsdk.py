#!/usr/bin/env python3
"""
Start-Skript für RZGCS mit MAVSDK-Integration
Verwendet den vorhandenen MAVSDK-Connector und alle anderen bestehenden Klassen
"""
import os
import sys
import argparse
from pathlib import Path

# Pfad anpassen, damit wir alle Module finden können
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)

# Importiere notwendige Module aus der Anwendung
from backend.logger import Logger
from backend.sensorviewmodel import SensorViewModel
from backend.mavsdk_connector import MAVSDKConnector
from backend.sensor_manager import SensorManager

# Hauptfunktion anpassen und importieren
from main import main as original_main

# MAVSDK-optimierte Hauptfunktion
def main():
    """Startet die RZGCS-Anwendung mit MAVSDK-Connector anstelle des Standard-Connectors"""
    # Kommandozeilenargumente parsen
    parser = argparse.ArgumentParser(description='RZGCS mit MAVSDK-Integration')
    parser.add_argument('--connection', '-c', default='udp://:14550',
                      help='Verbindungsstring (z.B. udp://:14550 oder serial:///dev/ttyACM0:57600)')
    args = parser.parse_args()
    
    # Umgebungsvariable setzen, um in main.py den MAVSDK-Connector zu verwenden
    os.environ['USE_MAVSDK'] = '1'
    os.environ['MAVSDK_CONNECTION'] = args.connection
    
    # Originale Hauptfunktion aufrufen
    return original_main()

if __name__ == "__main__":
    sys.exit(main())
