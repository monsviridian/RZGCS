#!/usr/bin/env python3
"""
Einfacher Test für SITL-Verbindung
"""

# Python 3.13 Kompatibilitätsfix für DroneKit
import collections.abc
import collections
if not hasattr(collections, 'MutableMapping'):
    collections.MutableMapping = collections.abc.MutableMapping

import time
from dronekit import connect

def test_sitl_connection():
    """Teste Verbindung zu SITL"""
    print("Teste SITL-Verbindung...")
    
    try:
        # Verbinde zu SITL
        print("Verbinde zu 127.0.0.1:5760...")
        vehicle = connect('127.0.0.1:5760', wait_ready=True, timeout=30)
        
        print("✓ Verbindung erfolgreich!")
        print(f"Vehicle: {vehicle}")
        print(f"Mode: {vehicle.mode.name}")
        print(f"Armed: {vehicle.armed}")
        print(f"GPS: {vehicle.gps_0}")
        
        # Schließe Verbindung
        vehicle.close()
        print("✓ Verbindung geschlossen")
        
    except Exception as e:
        print(f"✗ Fehler: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_sitl_connection() 