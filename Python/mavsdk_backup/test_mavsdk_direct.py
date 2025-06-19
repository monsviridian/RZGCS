#!/usr/bin/env python3
"""
Einfaches MAVSDK-Testskript um die direkte Verbindung mit einem COM-Port zu testen
"""

import asyncio
import sys
import time
import os
from mavsdk import System

# Konfiguration
COM_PORT = "COM8"  # Hier den gewünschten COM-Port eintragen
BAUDRATE = 115200  # Baudrate

async def run():
    print(f"[INFO] MAVSDK-Test wird gestartet mit {COM_PORT} bei {BAUDRATE} Baud")
    
    try:
        # Direkter Ansatz: Verbindung ohne separaten MAVSDK-Server
        # Verwende System() direkt mit der seriellen Verbindung als Parameter
        drone = System()
        print(f"[INFO] Verbinde direkt mit {COM_PORT} bei {BAUDRATE} Baud...")
        
        # Verschiedene Verbindungsformate ausprobieren
        connection_url = f"serial://{COM_PORT}:{BAUDRATE}"
        print(f"[INFO] Verwende Verbindungs-URL: {connection_url}")
        
        await drone.connect(connection_url)
        print("[INFO] Verbindungsversuch gestartet...")
        
        # Warte auf Verbindung
        print("[INFO] Warte auf Verbindung zur Drohne...")
        connection_timeout = 15  # Timeout in Sekunden
        start_time = time.time()
    except Exception as e:
        print(f"[FEHLER] Verbindungsfehler: {str(e)}")
        return
    
    try:
        # Erstelle Drone-Objekt mit expliziter Server-Adresse
        drone = System(mavsdk_server_address='localhost', port=50051)
        print("[INFO] Verbinde mit MAVSDK-Server über localhost:50051...")
        
        # Verbinde zur Drohne
        await drone.connect()
        
        # Warte auf Verbindung
        print("[INFO] Warte auf Verbindung zur Drohne...")
        connection_timeout = 10  # Timeout in Sekunden
        start_time = time.time()
        
        while not drone.is_connected:
            if time.time() - start_time > connection_timeout:
                print("[FEHLER] Timeout bei Verbindungsaufbau")
                break
            print(".", end="", flush=True)
            await asyncio.sleep(0.5)
        
        if drone.is_connected:
            print("\n[INFO] Verbindung erfolgreich hergestellt!")
            
            # Versuche, Basisinformationen abzurufen
            print("[INFO] Rufe Informationen ab...")
            
            try:
                # UUID abrufen
                uuid = await drone.info.get_identification()
                print(f"[INFO] Drohnen-UUID: {uuid.hardware_uid}")
            except Exception as e:
                print(f"[WARNUNG] Konnte UUID nicht abrufen: {str(e)}")
            
            try:
                # Fluginformationen abrufen
                position = await drone.telemetry.position()
                battery = await drone.telemetry.battery()
                armed = await drone.telemetry.armed()
                
                print(f"[INFO] Position: Lat {position.latitude_deg}, Lon {position.longitude_deg}, Alt {position.relative_altitude_m}m")
                print(f"[INFO] Batterie: {battery.remaining_percent*100:.1f}%")
                print(f"[INFO] Armed: {armed}")
            except Exception as e:
                print(f"[WARNUNG] Konnte Telemetrie nicht abrufen: {str(e)}")
            
            # Kurz warten, um alle Daten zu empfangen
            print("[INFO] Teste Verbindung für 5 Sekunden...")
            await asyncio.sleep(5)
            
            # Shutdown
            print("[INFO] Fahre Verbindung herunter...")
            await drone.core.shutdown()
        else:
            print("\n[FEHLER] Konnte keine Verbindung zur Drohne herstellen!")
    
    except Exception as e:
        print(f"[FEHLER] Fehler bei MAVSDK-Test: {str(e)}")
    
    finally:
        # MAVSDK-Server beenden
        print("[INFO] Beende MAVSDK-Server...")
        server_process.terminate()
        try:
            server_process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            print("[WARNUNG] MAVSDK-Server reagiert nicht, verwende kill...")
            server_process.kill()

if __name__ == "__main__":
    # Prüfe übergebenen COM-Port
    if len(sys.argv) > 1:
        COM_PORT = sys.argv[1]
        
    # Starte asyncio Event Loop
    print(f"[INFO] Starte MAVSDK-Test mit {COM_PORT}:{BAUDRATE}")
    asyncio.run(run())
