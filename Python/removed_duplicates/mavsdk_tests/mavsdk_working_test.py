#!/usr/bin/env python3
"""
Funktionierendes MAVSDK-Testskript basierend auf der bestehenden MAVSDKConnector-Implementierung
"""

import asyncio
import sys
import os
import subprocess
import time
from mavsdk import System

# Standard Konfiguration
COM_PORT = "COM8"  # Standardmäßig COM8, kann über Kommandozeile überschrieben werden
BAUDRATE = 115200  # Standardmäßig 115200
MAVSDK_SERVER_PATH = os.path.join(os.path.dirname(os.getcwd()), "mavsdk_server", "windows", "mavsdk-server.exe")
SERVER_PORT = 50051

async def run():
    # Konfiguration aus Kommandozeilenargumenten übernehmen, falls vorhanden
    global COM_PORT
    if len(sys.argv) > 1:
        COM_PORT = sys.argv[1]
    
    print(f"[INFO] MAVSDK-Test mit {COM_PORT}:{BAUDRATE} wird gestartet")
    print(f"[INFO] MAVSDK-Server-Pfad: {MAVSDK_SERVER_PATH}")
    
    # Prüfen, ob MAVSDK-Server existiert
    if not os.path.exists(MAVSDK_SERVER_PATH):
        print(f"[FEHLER] MAVSDK-Server nicht gefunden: {MAVSDK_SERVER_PATH}")
        return
    
    # Verbindungs-URL erstellen (Format: serial://COM8:115200)
    connection_url = f"serial://{COM_PORT}:{BAUDRATE}"
    
    # MAVSDK-Server mit korrekten Argumenten starten
    server_args = [
        MAVSDK_SERVER_PATH,
        "-p", str(SERVER_PORT),
        connection_url
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
        print("[INFO] Verbinde mit Drohne...")
        await drone.connect()
        
        print("[INFO] Warte auf Herstellung der Verbindung...")
        
        # Einfachere Methode verwenden, um zu prüfen, ob wir verbunden sind
        is_connected = False
        try:
            start_time = time.time()
            while time.time() - start_time < 15:  # 15 Sekunden Timeout
                try:
                    # Alternativer Ansatz zur Verbindungsprüfung
                    # Anstatt connection_state() zu verwenden, fragen wir eine einfache Information ab
                    # Wenn dies ohne Fehler funktioniert, sind wir verbunden
                    await drone.core.get_identification()
                    print("[INFO] Verbindung hergestellt!")
                    is_connected = True
                    break
                except asyncio.TimeoutError:
                    # Weiter warten
                    pass
                except Exception as e:
                    # Bei PX4-Drohnen kann es sein, dass get_identification() nicht verfügbar ist
                    # Versuchen wir es mit einem anderen Ansatz
                    try:
                        await drone.info.get_version()
                        print("[INFO] Verbindung hergestellt! (Versionsabfrage)")
                        is_connected = True
                        break
                    except Exception:
                        # Immer noch nicht verbunden, warten und erneut versuchen
                        pass
                
                # Kurze Pause
                await asyncio.sleep(0.5)
                
            if not is_connected:
                print("[FEHLER] Timeout bei Verbindungsherstellung")
        except Exception as e:
            print(f"[FEHLER] Fehler bei Verbindungsprüfung: {str(e)}")
        
        if is_connected:
            # Basis-Informationen abrufen
            print("[INFO] Informationen werden abgerufen...")
            
            try:
                # UUID abrufen
                uuid = await drone.info.get_identification()
                print(f"[INFO] Drohnen-UUID: {uuid.hardware_uid}")
            except Exception as e:
                print(f"[WARNUNG] Konnte UUID nicht abrufen: {str(e)}")
            
            try:
                # Systemstatus abrufen - korrekte Behandlung von asynchronen Generatoren
                async for health in drone.telemetry.health():
                    print(f"[INFO] Systemstatus:")
                    print(f"  - Gyroskop kalibriert: {health.is_gyrometer_calibration_ok}")
                    print(f"  - Accelerometer kalibriert: {health.is_accelerometer_calibration_ok}")
                    print(f"  - Magnetometer kalibriert: {health.is_magnetometer_calibration_ok}")
                    print(f"  - Level kalibriert: {health.is_level_calibration_ok}")
                    print(f"  - Lokale Position OK: {health.is_local_position_ok}")
                    print(f"  - Globale Position OK: {health.is_global_position_ok}")
                    print(f"  - Home Position OK: {health.is_home_position_ok}")
                    # Nur den ersten Wert verwenden und dann den Loop verlassen
                    break
            except Exception as e:
                print(f"[WARNUNG] Konnte Gesundheitsstatus nicht abrufen: {str(e)}")
                
            try:
                # GPS-Status abrufen - korrekte Behandlung von asynchronen Generatoren
                async for gps_info in drone.telemetry.gps_info():
                    print(f"[INFO] GPS-Status:")
                    print(f"  - Fix-Typ: {gps_info.fix_type}")
                    print(f"  - Satelliten sichtbar: {gps_info.num_satellites}")
                    # Nur den ersten Wert verwenden und dann den Loop verlassen
                    break
            except Exception as e:
                print(f"[WARNUNG] Konnte GPS-Status nicht abrufen: {str(e)}")
                
            print("[INFO] Test abgeschlossen.")
            
            # Verbindung trennen - korrekte Methode verwenden
            try:
                # In neueren MAVSDK-Versionen korrekt, wenn nicht möglich, verwende dispose
                await drone.core.shutdown()
            except AttributeError:
                # Fallback für ältere Versionen
                try:
                    await drone.dispose()
                except Exception:
                    # Wenn alles fehlschlägt, nichts tun - der Server wird sowieso beendet
                    pass
            
        else:
            print("[FEHLER] Konnte keine Verbindung zur Drohne herstellen.")
            
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
