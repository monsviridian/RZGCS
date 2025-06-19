#!/usr/bin/env python3
"""
Einfaches MAVSDK-Testskript für serielle Verbindungen basierend auf offizieller Dokumentation
"""

import asyncio
import sys
from mavsdk import System

# Standard Konfiguration
COM_PORT = "COM8"  # Standardmäßig COM8, kann über Kommandozeile überschrieben werden
BAUDRATE = 115200  # Standardmäßig 115200

async def run():
    # Konfiguration aus Kommandozeilenargumenten übernehmen, falls vorhanden
    global COM_PORT
    if len(sys.argv) > 1:
        COM_PORT = sys.argv[1]
        
    # Verbindungs-URL gemäß MAVSDK-Dokumentation für Windows
    connection_url = f"serial://{COM_PORT}:{BAUDRATE}"
    
    print(f"[INFO] MAVSDK-Test wird mit folgender Verbindung gestartet: {connection_url}")
    
    # System-Objekt erstellen
    drone = System()
    
    # Verbindung herstellen
    print("[INFO] Verbinde mit Drohne...")
    try:
        await drone.connect(connection_url)
    except Exception as e:
        print(f"[FEHLER] Verbindungsfehler: {str(e)}")
        return
    
    print("[INFO] Warte auf Herstellung der Verbindung...")
    
    # Auf Verbindung warten (max. 30 Sekunden)
    try:
        async with asyncio.timeout(30):
            async for state in drone.core.connection_state():
                if state.is_connected:
                    print(f"[INFO] Verbindung hergestellt!")
                    break
    except asyncio.TimeoutError:
        print("[FEHLER] Timeout bei Verbindungsherstellung")
        return
        
    # Basis-Informationen abrufen
    print("[INFO] Informationen werden abgerufen...")
    
    try:
        # UUID abrufen
        uuid = await drone.info.get_identification()
        print(f"[INFO] Drohnen-UUID: {uuid.hardware_uid}")
    except Exception as e:
        print(f"[WARNUNG] Konnte UUID nicht abrufen: {str(e)}")
    
    try:
        # Systemstatus abrufen
        health = await drone.telemetry.health()
        print(f"[INFO] Systemstatus:")
        print(f"  - Gyroskop kalibriert: {health.is_gyrometer_calibration_ok}")
        print(f"  - Accelerometer kalibriert: {health.is_accelerometer_calibration_ok}")
        print(f"  - Magnetometer kalibriert: {health.is_magnetometer_calibration_ok}")
        print(f"  - Level kalibriert: {health.is_level_calibration_ok}")
        print(f"  - Lokale Position OK: {health.is_local_position_ok}")
        print(f"  - Globale Position OK: {health.is_global_position_ok}")
        print(f"  - Home Position OK: {health.is_home_position_ok}")
    except Exception as e:
        print(f"[WARNUNG] Konnte Gesundheitsstatus nicht abrufen: {str(e)}")
        
    print("[INFO] Test abgeschlossen.")

    # Verbindung trennen
    await drone.core.shutdown()

if __name__ == "__main__":
    # Asyncio Event-Loop starten
    asyncio.run(run())
