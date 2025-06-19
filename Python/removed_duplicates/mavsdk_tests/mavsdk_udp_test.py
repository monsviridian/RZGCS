#!/usr/bin/env python3
"""
MAVSDK-Testskript für UDP-Verbindung
"""

import asyncio
import os
import subprocess
import time
from mavsdk import System

# UDP-Port für die Verbindung
UDP_PORT = 14540
SERVER_PORT = 50051
MAVSDK_SERVER_PATH = os.path.join(os.path.dirname(os.getcwd()), "mavsdk_server", "windows", "mavsdk-server.exe")

async def run():
    print(f"[INFO] MAVSDK UDP-Test wird gestartet")
    print(f"[INFO] MAVSDK-Server-Pfad: {MAVSDK_SERVER_PATH}")
    
    if not os.path.exists(MAVSDK_SERVER_PATH):
        print(f"[FEHLER] MAVSDK-Server nicht gefunden: {MAVSDK_SERVER_PATH}")
        return
    
    # Verbindungs-URL für UDP
    connection_url = f"udp://:14540"
    server_args = [
        MAVSDK_SERVER_PATH,
        "-p", str(SERVER_PORT),
        f"-u={UDP_PORT}"  # UDP-Port zum Lauschen
    ]
    
    print(f"[INFO] Starte MAVSDK-Server mit Befehl: {' '.join(server_args)}")
    
    # MAVSDK-Server starten
    server_process = subprocess.Popen(server_args)
    print(f"[INFO] MAVSDK-Server gestartet mit PID: {server_process.pid}")
    
    # Kurz warten, bis der Server initialisiert ist
    print("[INFO] Warte 2 Sekunden, bis der Server bereit ist...")
    await asyncio.sleep(2)
    
    try:
        # System-Objekt mit expliziter Server-Adresse erstellen
        drone = System(mavsdk_server_address="localhost", port=SERVER_PORT)
        print("[INFO] System-Objekt erstellt mit expliziter Verbindung zum lokalen MAVSDK-Server")
        
        # Verbindung herstellen
        print("[INFO] Verbinde mit Drohne via UDP...")
        await drone.connect()
        
        print(f"[INFO] Warte auf UDP-Verbindung auf Port {UDP_PORT}...")
        print("[INFO] (Sie müssen sicherstellen, dass ein MAVLink-Gerät MAVLink-Pakete an diesen Port sendet)")
        
        # Auf Verbindung warten (max. 30 Sekunden)
        connected = False
        start_time = time.time()
        while not drone.is_connected:
            await asyncio.sleep(0.5)
            if time.time() - start_time > 30:
                print("[FEHLER] Timeout bei Verbindungsherstellung")
                break
            print(".", end="", flush=True)
            
        if drone.is_connected:
            print("\n[INFO] Verbindung hergestellt!")
            
            # Basis-Informationen abrufen
            print("[INFO] Informationen werden abgerufen...")
            
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
                
            print("[INFO] Test abgeschlossen.")
            
            # Verbindung trennen
            await drone.core.shutdown()
        else:
            print("\n[FEHLER] Konnte keine Verbindung zur Drohne herstellen.")
            
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
    # Asyncio Event-Loop starten
    asyncio.run(run())
