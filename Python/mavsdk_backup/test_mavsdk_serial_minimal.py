#!/usr/bin/env python3
"""
Minimaler Test für MAVSDK-Verbindung über einen seriellen Port.
Dieser Skript versucht, den MAVSDK-Server manuell zu starten und eine Verbindung herzustellen.
"""

import asyncio
import os
import sys
import subprocess
import time
from mavsdk import System


async def run_test(port="COM8", baudrate=115200):
    """Test einer MAVSDK-Verbindung über seriellen Port"""
    
    # Finde den MAVSDK-Server
    import mavsdk
    mavsdk_dir = os.path.dirname(mavsdk.__file__)
    server_bin = os.path.join(mavsdk_dir, 'bin', 'mavsdk_server')
    if sys.platform == 'win32':
        server_bin += '.exe'
    
    if not os.path.isfile(server_bin):
        print(f"[FEHLER] MAVSDK-Server nicht gefunden unter: {server_bin}")
        # Suche nach alternativen Pfaden
        alternative_paths = []
        for path in sys.path:
            potential_path = os.path.join(path, 'mavsdk', 'bin', 'mavsdk_server.exe' if sys.platform == 'win32' else 'mavsdk_server')
            if os.path.isfile(potential_path):
                alternative_paths.append(potential_path)
                
        if alternative_paths:
            server_bin = alternative_paths[0]
            print(f"[INFO] Alternativer MAVSDK-Server gefunden: {server_bin}")
        else:
            print("[KRITISCH] Konnte keinen MAVSDK-Server finden!")
            return
    
    # Verbindungsstring erstellen
    connection_string = f"serial://{port}:{baudrate}"
    print(f"[INFO] Verbindungsversuch mit: {connection_string}")
    
    # MAVSDK-Server manuell starten
    print(f"[INFO] Starte MAVSDK-Server: {server_bin} {connection_string}")
    server_process = subprocess.Popen(
        [server_bin, connection_string],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Warte kurz, um zu sehen, ob der Prozess sofort fehlschlägt
    time.sleep(1.0)
    
    # Prüfe, ob der Prozess noch läuft
    if server_process.poll() is not None:
        # Prozess ist bereits beendet - das ist nicht gut
        stdout, stderr = server_process.communicate()
        print(f"[FEHLER] MAVSDK-Server beendet mit Code {server_process.returncode}")
        print(f"[FEHLER] STDOUT: {stdout}")
        print(f"[FEHLER] STDERR: {stderr}")
        return
    
    print(f"[INFO] MAVSDK-Server erfolgreich gestartet (PID: {server_process.pid})")
    
    try:
        # Mit dem lokalen Server verbinden
        drone = System()
        print("[INFO] Verbinde mit lokalem MAVSDK-Server...")
        await drone.connect()
        
        print("Warte auf Verbindung zum Flight Controller...")
        async for state in drone.core.connection_state():
            if state.is_connected:
                print(f"-- Verbunden mit Drohne!")
                break
        
        # Status-Text-Monitoring starten
        status_text_task = asyncio.create_task(print_status_text(drone))
        
        # Warte auf Benutzer-Abbruch
        print("\n--- Verbindung hergestellt! Drücke Strg+C zum Beenden ---")
        while True:
            await asyncio.sleep(1)
            
    except asyncio.CancelledError:
        print("Abbruch durch Benutzer.")
    except Exception as e:
        print(f"[FEHLER] Fehler bei der Verbindung: {e}")
    finally:
        # Aufräumen
        print("Beende MAVSDK-Server...")
        if server_process:
            server_process.terminate()


async def print_status_text(drone):
    """Überwacht die Status-Texte des Flight Controllers"""
    try:
        async for status_text in drone.telemetry.status_text():
            print(f"Status: {status_text.type}: {status_text.text}")
    except asyncio.CancelledError:
        return


if __name__ == "__main__":
    # COM-Port und Baudrate aus Kommandozeile übernehmen, falls angegeben
    port = sys.argv[1] if len(sys.argv) > 1 else "COM8"
    baudrate = int(sys.argv[2]) if len(sys.argv) > 2 else 115200
    
    print(f"\n=== MAVSDK Serieller Verbindungstest ===")
    print(f"Port: {port}, Baudrate: {baudrate}")
    
    # Asyncio-Loop starten
    try:
        asyncio.run(run_test(port, baudrate))
    except KeyboardInterrupt:
        print("\nProgramm durch Benutzer beendet.")
