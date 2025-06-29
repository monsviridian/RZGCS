#!/usr/bin/env python
# Test-Skript, um eine direkte MAVLink-Verbindung zu testen
import sys
import time
import collections.abc
import collections
if not hasattr(collections, 'MutableMapping'):
    collections.MutableMapping = collections.abc.MutableMapping

from dronekit import connect

print("MAVLink-Verbindungstest mit verbesserten Parametern")

# COM-Port definieren
port = "COM3"
baudrate = 115200

print(f"Versuche Verbindung zu {port} mit {baudrate} Baud...")

try:
    # Normaler Verbindungsversuch
    print("Methode 1: Standard-Verbindung")
    vehicle = connect(port, wait_ready=True, baud=baudrate)
    print("Connected!")
    print("Mode:", vehicle.mode.name)
    vehicle.close()
    
except Exception as e:
    print(f"Fehler bei Methode 1: {e}")
    
    try:
        # Windows-spezifischer Verbindungsversuch
        print("\nMethode 2: Windows-spezifisch")
        alt_port = f"\\\\.\\{port}"
        print(f"Versuche mit alternativem Port-Format: {alt_port}")
        vehicle = connect(alt_port, wait_ready=True, baud=baudrate)
        print("Connected!")
        print("Mode:", vehicle.mode.name)
        vehicle.close()
        
    except Exception as e:
        print(f"Fehler bei Methode 2: {e}")
        
        try:
            # Mission Planner Stil mit kleingeschriebenem 'com'
            print("\nMethode 3: Mission Planner-Stil (com)")
            mp_port = f"com{port[3:]}" if port.startswith("COM") else port
            print(f"Versuche Mission Planner Format: {mp_port}")
            vehicle = connect(mp_port, wait_ready=True, baud=baudrate)
            print("Connected!")
            print("Mode:", vehicle.mode.name)
            vehicle.close()
            
        except Exception as e:
            print(f"Fehler bei Methode 3: {e}")
            print("\nAlle Verbindungsversuche fehlgeschlagen.")

print("\nTest abgeschlossen.")
