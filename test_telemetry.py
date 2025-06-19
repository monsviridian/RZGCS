#!/usr/bin/env python
# Telemetrie-Monitor-Skript
import sys
import time
from pymavlink import mavutil
from datetime import datetime

print("===== MAVLink Telemetrie-Monitor =====")

# COM-Port definieren
port = "COM3"
baudrate = 115200

print(f"Verbindung zu {port} mit {baudrate} Baud wird hergestellt...")

try:
    # Verbindung herstellen
    connection = mavutil.mavlink_connection(
        device=port,
        baud=baudrate,
        source_system=255,
        source_component=0
    )
    
    print("Verbindung hergestellt. Warte auf Heartbeat...")
    msg = connection.wait_heartbeat(timeout=5)
    if msg:
        print(f"Heartbeat empfangen: {msg}")
        print(f"Fahrzeugtyp: {msg.type}, Autopilot: {msg.autopilot}")
        print(f"System-Status: {msg.system_status}")
        print(f"MAVLink-Version: {msg.mavlink_version}")
    else:
        print("WARNUNG: Kein Heartbeat empfangen!")
    
    print("\nTelemetriedaten-Monitor gestartet. Drücken Sie Strg+C zum Beenden.\n")
    print("Datum       | Zeit     | Nachrichtentyp       | Werte")
    print("-" * 80)
    
    # Telemetriedaten fortlaufend empfangen
    while True:
        # Auf nächste Nachricht warten
        msg = connection.recv_match(blocking=True, timeout=1.0)
        if msg:
            # Nach Nachrichtentyp filtern, um nur relevante Telemetrie zu zeigen
            msg_type = msg.get_type()
            
            # Datum und Uhrzeit für den Zeitstempel
            now = datetime.now()
            date_str = now.strftime("%Y-%m-%d")
            time_str = now.strftime("%H:%M:%S")
            
            # Verschiedene Nachrichtentypen mit spezifischen Informationen anzeigen
            if msg_type == "HEARTBEAT":
                print(f"{date_str} | {time_str} | HEARTBEAT           | Mode: {msg.custom_mode}, Status: {msg.system_status}")
            elif msg_type == "ATTITUDE":
                roll = round(msg.roll * 57.2958, 2)  # Konvertierung von rad zu grad
                pitch = round(msg.pitch * 57.2958, 2)
                yaw = round(msg.yaw * 57.2958, 2)
                print(f"{date_str} | {time_str} | ATTITUDE            | Roll: {roll}°, Pitch: {pitch}°, Yaw: {yaw}°")
            elif msg_type == "VFR_HUD":
                print(f"{date_str} | {time_str} | VFR_HUD             | Geschw: {msg.airspeed:.1f}m/s, Alt: {msg.alt:.1f}m, Kurs: {msg.heading}°")
            elif msg_type == "GLOBAL_POSITION_INT":
                lat = msg.lat / 1e7  # Konvertierung von 1E7 Format zu Grad
                lon = msg.lon / 1e7
                alt = msg.alt / 1000.0  # in Meter
                print(f"{date_str} | {time_str} | GLOBAL_POSITION_INT | Lat: {lat:.6f}, Lon: {lon:.6f}, Alt: {alt:.1f}m")
            elif msg_type == "SYS_STATUS":
                voltage = msg.voltage_battery / 1000.0 if hasattr(msg, 'voltage_battery') else 0  # in Volt
                current = msg.current_battery / 100.0 if hasattr(msg, 'current_battery') else 0   # in Ampere
                remaining = msg.battery_remaining if hasattr(msg, 'battery_remaining') else 0     # in Prozent
                print(f"{date_str} | {time_str} | SYS_STATUS          | Batt: {voltage:.2f}V, Strom: {current:.2f}A, Verbleibend: {remaining}%")
            elif msg_type == "STATUSTEXT":
                text = msg.text if hasattr(msg, 'text') else "Keine Nachricht"
                print(f"{date_str} | {time_str} | STATUSTEXT          | {text}")
            else:
                # Andere Nachrichtentypen nur bei Bedarf anzeigen
                if msg_type not in ["PARAM_VALUE", "RC_CHANNELS", "SERVO_OUTPUT_RAW", "COMMAND_ACK"]:
                    print(f"{date_str} | {time_str} | {msg_type.ljust(20)} | {msg}")

except KeyboardInterrupt:
    print("\nMonitor wurde durch Benutzer beendet.")
except Exception as e:
    print(f"\nFehler: {e}")
finally:
    if 'connection' in locals():
        connection.close()
    print("\nVerbindung geschlossen.")
