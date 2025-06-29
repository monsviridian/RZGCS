#!/usr/bin/env python
# Telemetrie-Logger-Integration für die PreflightView
import sys
import time
from pymavlink import mavutil
from datetime import datetime
import collections.abc
import collections
if not hasattr(collections, 'MutableMapping'):
    collections.MutableMapping = collections.abc.MutableMapping

from dronekit import connect

# Importieren der Logger-Klasse, falls vorhanden (für Tests)
try:
    from Python.backend.logger import Logger
    has_logger = True
    print("Logger-Klasse erfolgreich importiert")
except ImportError:
    has_logger = False
    print("Logger-Klasse konnte nicht importiert werden, nutze Fallback")
    
class TelemetryLogger:
    def __init__(self, port="COM3", baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.vehicle = None
        self.logger = Logger() if has_logger else None
        self.connected = False
        
        # MAVLink-Nachrichtentypen, die als Telemetrie geloggt werden sollen
        self.telemetry_types = [
            "HEARTBEAT", 
            "ATTITUDE",
            "VFR_HUD", 
            "GLOBAL_POSITION_INT",
            "SYS_STATUS",
            "GPS_RAW_INT",
            "STATUSTEXT"
        ]
        
        print(f"TelemetryLogger initialisiert für {port} mit {baudrate} Baud")
        
    def connect(self):
        """Verbindung zur seriellen Schnittstelle herstellen"""
        try:
            print(f"Verbindung zu {self.port} wird hergestellt...")
            self.vehicle = connect(self.port, wait_ready=True, baud=self.baudrate)
            print("Connected!")
            print("Mode:", self.vehicle.mode.name)
            self.connected = True
            self.log_system_info(f"[SYSTEM INFO] Verbunden mit {self.port} bei {self.baudrate} Baud")
            self.log_system_info(f"[SYSTEM INFO] Fahrzeugtyp: {self.vehicle.type}, Autopilot: {self.vehicle.autopilot}")
            return True
        except Exception as e:
            print(f"Fehler beim Verbinden: {e}")
            return False
    
    def log_system_info(self, message):
        """Log als Systeminformation hinzufügen"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        
        # In die Konsole ausgeben
        print(log_entry)
        
        # Zum Logger hinzufügen, wenn verfügbar
        if self.logger:
            self.logger.addSystemInfoLog(message)
    
    def run(self):
        """Telemetrie empfangen und als Logs ausgeben"""
        if not self.connected or not self.vehicle:
            print("Nicht verbunden")
            return
            
        print("\nTelemetrie-Monitor gestartet. Drücken Sie Strg+C zum Beenden.\n")
        
        try:
            # Telemetriedaten fortlaufend empfangen
            while True:
                # Auf nächste Nachricht warten
                msg = self.vehicle.recv_match(blocking=True, timeout=1.0)
                if not msg:
                    continue
                    
                msg_type = msg.get_type()
                
                # Nur gewünschte Telemetrietypen verarbeiten
                if msg_type in self.telemetry_types:
                    # Verschiedene Nachrichtentypen mit spezifischen Informationen formatieren
                    if msg_type == "HEARTBEAT":
                        status_text = "STANDBY"
                        if hasattr(msg, 'system_status'):
                            if msg.system_status == 3:
                                status_text = "AKTIV"
                            elif msg.system_status == 4:
                                status_text = "KRITISCH"
                            elif msg.system_status == 5:
                                status_text = "NOTFALL"
                        self.log_system_info(f"[HEARTBEAT] Status: {status_text}, Mode: {msg.custom_mode}")
                    elif msg_type == "ATTITUDE":
                        roll = round(msg.roll * 57.2958, 1)  # Konvertierung von rad zu grad
                        pitch = round(msg.pitch * 57.2958, 1)
                        yaw = round(msg.yaw * 57.2958, 1)
                        self.log_system_info(f"[ATTITUDE] Roll: {roll}°, Pitch: {pitch}°, Yaw: {yaw}°")
                    elif msg_type == "VFR_HUD":
                        self.log_system_info(f"[FLIGHT] Speed: {msg.airspeed:.1f}m/s, Alt: {msg.alt:.1f}m, Climb: {msg.climb:.1f}m/s")
                    elif msg_type == "GLOBAL_POSITION_INT":
                        lat = msg.lat / 1e7  # Konvertierung von 1E7 Format zu Grad
                        lon = msg.lon / 1e7
                        alt = msg.alt / 1000.0  # in Meter
                        self.log_system_info(f"[GPS] Lat: {lat:.6f}, Lon: {lon:.6f}, Alt: {alt:.1f}m")
                    elif msg_type == "SYS_STATUS":
                        voltage = msg.voltage_battery / 1000.0 if hasattr(msg, 'voltage_battery') else 0  # in Volt
                        current = msg.current_battery / 100.0 if hasattr(msg, 'current_battery') else 0   # in Ampere
                        remaining = msg.battery_remaining if hasattr(msg, 'battery_remaining') else 0     # in Prozent
                        self.log_system_info(f"[BATTERY] {voltage:.2f}V, {current:.2f}A, Verbleibend: {remaining}%")
                    elif msg_type == "GPS_RAW_INT":
                        fix_type = "KEIN FIX"
                        if hasattr(msg, 'fix_type'):
                            if msg.fix_type == 2:
                                fix_type = "2D FIX"
                            elif msg.fix_type == 3:
                                fix_type = "3D FIX"
                            elif msg.fix_type >= 4:
                                fix_type = "DGPS FIX"
                        satellites = msg.satellites_visible if hasattr(msg, 'satellites_visible') else 0
                        self.log_system_info(f"[GPS] Typ: {fix_type}, Satelliten: {satellites}")
                    elif msg_type == "STATUSTEXT":
                        text = msg.text if hasattr(msg, 'text') else "Keine Nachricht"
                        severity = msg.severity if hasattr(msg, 'severity') else 0
                        if severity <= 3:  # Nur wichtige Meldungen (EMERGENCY, ALERT, CRITICAL, ERROR)
                            self.log_system_info(f"[STATUS] {text}")
                
        except KeyboardInterrupt:
            print("\nTelemetrie-Monitor wurde durch Benutzer beendet.")
        except Exception as e:
            print(f"\nFehler: {e}")
        finally:
            if self.vehicle:
                self.vehicle.close()
                print("\nVerbindung geschlossen.")

    def close(self):
        if self.vehicle:
            self.vehicle.close()

if __name__ == "__main__":
    # Port und Baudrate definieren (optional über Kommandozeilenparameter)
    port = sys.argv[1] if len(sys.argv) > 1 else "COM3"
    baudrate = int(sys.argv[2]) if len(sys.argv) > 2 else 115200
    
    # Logger initialisieren und starten
    logger = TelemetryLogger(port=port, baudrate=baudrate)
    if logger.connect():
        logger.run()
    else:
        print("Verbindung konnte nicht hergestellt werden.")
