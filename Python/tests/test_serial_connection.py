#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test-Script für SerialConnection und ConnectionManager
Detaillierte Debug-Ausgabe für Verbindungsprobleme
"""

import sys
import os
import traceback

# Pfad zum Python-Verzeichnis hinzufügen
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.connection.connection_types import SerialConnection
from backend.connection.connection_manager import ConnectionManager

def test_serial_connection_direct():
    """Teste direkt die SerialConnection-Klasse"""
    print("\n=== Test SerialConnection direkt ===")
    
    serial_conn = SerialConnection()
    
    # Verfügbare Ports auslesen und anzeigen
    try:
        ports = serial_conn.get_available_ports()
        print(f"Verfügbare Ports: {ports}")
    except Exception as e:
        print(f"FEHLER beim Abrufen verfügbarer Ports: {e}")
        traceback.print_exc()
    
    # Versuch mit COM3 (häufig verwendeter Port)
    test_port = "COM3"
    test_baudrate = 115200
    
    print(f"\nVersuche direkte Verbindung zu {test_port} mit {test_baudrate} Baud...")
    try:
        result = serial_conn.establish_connection(port=test_port, baudrate=test_baudrate)
        print(f"Verbindungsergebnis: {result}")
        
        if result:
            print(f"Verbindung erfolgreich! Port={serial_conn._port}, Baudrate={serial_conn._baudrate}")
        else:
            print(f"Verbindung fehlgeschlagen.")
    except Exception as e:
        print(f"EXCEPTION beim Verbindungsversuch: {e}")
        traceback.print_exc()

def test_connection_manager():
    """Teste die Verbindung über den ConnectionManager"""
    print("\n=== Test ConnectionManager ===")
    
    cm = ConnectionManager()
    
    # Verbindungseinstellungen
    settings = {
        'type': 'SERIAL',
        'port': 'COM3',
        'baudrate': 115200,
        'timeout': 5.0,
        'encryption': False
    }
    
    print(f"Verbindungseinstellungen: {settings}")
    
    try:
        result = cm.connect(settings)
        print(f"ConnectionManager.connect() Ergebnis: {result}")
        
        if result:
            print("Verbindung erfolgreich hergestellt!")
        else:
            print("Verbindung fehlgeschlagen.")
    except Exception as e:
        print(f"EXCEPTION im ConnectionManager: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    print("=== SerialConnection Debug-Test ===")
    print(f"Python-Version: {sys.version}")
    print(f"Plattform: {sys.platform}")
    
    # Tests ausführen
    test_serial_connection_direct()
    test_connection_manager()
