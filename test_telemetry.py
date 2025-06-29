#!/usr/bin/env python
# Telemetrie-Monitor-Skript
import collections.abc
import collections
if not hasattr(collections, 'MutableMapping'):
    collections.MutableMapping = collections.abc.MutableMapping

from dronekit import connect
import sys
from datetime import datetime
import time

print("===== MAVLink Telemetrie-Monitor =====")

# COM-Port definieren
port = "COM8"
baudrate = 115200

print(f"Verbindung zu {port} mit {baudrate} Baud wird hergestellt...")

try:
    vehicle = connect(port, wait_ready=True, baud=baudrate)
    print("Connected!")
    print("Mode:", vehicle.mode.name)
    print("\nTelemetriedaten-Monitor gestartet. Drücken Sie Strg+C zum Beenden.\n")
    print("Datum       | Zeit     | GPS | Battery | Attitude | Location")
    print("-" * 80)
    while True:
        print(f"GPS: {vehicle.gps_0} | Battery: {vehicle.battery} | Attitude: {vehicle.attitude} | Location: {vehicle.location.global_frame}")
        time.sleep(1)
except KeyboardInterrupt:
    print("\nMonitor wurde durch Benutzer beendet.")
except Exception as e:
    print(f"\nFehler: {e}")
finally:
    try:
        vehicle.close()
    except:
        pass
