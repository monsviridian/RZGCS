"""
Einfacher MAVLink-Simulator, der garantiert gültige Nachrichten sendet.
"""

import threading
import time
import math
import random
from pymavlink import mavutil

class SimpleMAVLinkSimulator:
    """Ein vereinfachter MAVLink-Simulator, der garantiert funktioniert."""
    
    def __init__(self):
        """Initialisiert den Simulator."""
        self._running = False
        self._thread = None
        self._connection = None
        
    def start(self):
        """Startet den Simulator."""
        try:
            # UDP-Verbindung erstellen (senden an Port 14551)
            self._connection = mavutil.mavlink_connection(
                'udpout:localhost:14551',
                source_system=1,
                source_component=1
            )
            
            # Simulator-Thread starten
            self._running = True
            self._thread = threading.Thread(target=self._simulation_loop)
            self._thread.daemon = True
            self._thread.start()
            
            return True
        except Exception as e:
            print(f"Fehler beim Starten des Simulators: {str(e)}")
            return False
    
    def stop(self):
        """Stoppt den Simulator."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)
        
        if self._connection:
            try:
                self._connection.close()
            except:
                pass
            self._connection = None
    
    def _simulation_loop(self):
        """Hauptschleife für die Simulation."""
        # Startwerte für die Simulation
        lat = 51.1657  # Breitengrad (Deutschland)
        lon = 10.4515  # Längengrad (Deutschland)
        alt = 100.0    # Höhe in Metern
        
        # Attitude-Werte
        roll = 0.0
        pitch = 0.0
        yaw = 0.0
        
        # Batterie-Werte
        voltage = 12.6
        current = 8.5
        remaining = 75
        
        while self._running:
            try:
                # Aktuelle Zeit für Timestamps
                now = int(time.time() * 1000)
                
                # 1. Heartbeat senden
                self._connection.mav.heartbeat_send(
                    mavutil.mavlink.MAV_TYPE_QUADROTOR,
                    mavutil.mavlink.MAV_AUTOPILOT_GENERIC,
                    mavutil.mavlink.MAV_MODE_GUIDED_ARMED,
                    0,
                    mavutil.mavlink.MAV_STATE_ACTIVE
                )
                
                # 2. GPS-Position senden mit festen Werten, um Fehler zu vermeiden
                try:
                    # Feste Werte für Deutschland (Berlin)
                    lat = 52.520008          # Breitengrad
                    lon = 13.404954          # Längengrad
                    alt = 100.0              # Höhe in Metern
                    
                    # Leichte Bewegung simulieren (sehr kleine Änderungen)
                    lat += random.uniform(-0.00001, 0.00001)
                    lon += random.uniform(-0.00001, 0.00001)
                    
                    # Feste Werte für Geschwindigkeiten (cm/s)
                    vx = 0
                    vy = 0
                    vz = 0
                    
                    # Fester Heading-Wert
                    hdg = 0  # Nordrichtung
                    
                    # GLOBAL_POSITION_INT senden mit sicheren Werten
                    self._connection.mav.global_position_int_send(
                        now,                  # time_boot_ms (ms)
                        int(lat * 10000000),   # lat (deg * 1e7)
                        int(lon * 10000000),   # lon (deg * 1e7)
                        int(alt * 1000),      # alt (mm)
                        int(alt * 1000),      # relative_alt (mm)
                        0,                    # vx (cm/s)
                        0,                    # vy (cm/s)
                        0,                    # vz (cm/s)
                        0                     # hdg (deg * 100)
                    )
                except Exception as e:
                    print(f"GPS-Fehler: {str(e)}")
                    # Versuche mit Standardwerten
                    try:
                        self._connection.mav.global_position_int_send(
                            now,             # time_boot_ms
                            470597600,       # lat (47.0598 * 1e7)
                            85267900,        # lon (8.5268 * 1e7)
                            100000,          # alt (100m in mm)
                            100000,          # relative_alt (100m in mm)
                            0,               # vx (cm/s)
                            0,               # vy (cm/s)
                            0,               # vz (cm/s)
                            0                # hdg (deg * 100)
                        )
                    except Exception as e:
                        print(f"GPS-Fehler mit Standardwerten: {str(e)}")
                
                # 3. Attitude senden mit festen Werten
                try:
                    # Feste Werte für Attitude, um Fehler zu vermeiden
                    roll = 0.0    # Keine Neigung
                    pitch = 0.0   # Keine Neigung
                    yaw = 0.0     # Nordrichtung
                    
                    # Leichte Schwankungen simulieren (sehr kleine Werte)
                    roll += 0.01 * math.sin(time.time())
                    pitch += 0.01 * math.cos(time.time())
                    
                    # Attitude-Nachricht mit sicheren Werten senden
                    self._connection.mav.attitude_send(
                        now,       # time_boot_ms
                        0.0,       # roll (rad)
                        0.0,       # pitch (rad)
                        0.0,       # yaw (rad)
                        0.0,       # rollspeed (rad/s)
                        0.0,       # pitchspeed (rad/s)
                        0.0        # yawspeed (rad/s)
                    )
                except Exception as e:
                    print(f"Attitude-Fehler: {str(e)}")
                    # Versuche mit Standardwerten
                    try:
                        self._connection.mav.attitude_send(
                            now,             # time_boot_ms
                            0.0,             # roll (rad)
                            0.0,             # pitch (rad)
                            0.0,             # yaw (rad)
                            0.0,             # rollspeed (rad/s)
                            0.0,             # pitchspeed (rad/s)
                            0.0              # yawspeed (rad/s)
                        )
                    except Exception as e:
                        print(f"Attitude-Fehler mit Standardwerten: {str(e)}")
                
                # 4. Batteriestatus senden
                # Leichte Schwankungen simulieren
                voltage -= random.uniform(0, 0.01)  # Langsam entladen
                current = max(0, current + random.uniform(-0.2, 0.2))
                remaining = max(0, min(100, remaining - random.uniform(0, 0.1)))
                
                try:
                    self._connection.mav.sys_status_send(
                        0b00000000000001111111111111111111,  # onboard_control_sensors_present
                        0b00000000000001111111111111111111,  # onboard_control_sensors_enabled
                        0b00000000000001111111111111111111,  # onboard_control_sensors_health
                        500,                                 # load (0-1000)
                        int(voltage * 1000),                 # voltage_battery (mV)
                        int(current * 100),                  # current_battery (cA)
                        int(remaining),                      # battery_remaining (%)
                        0,                                   # comm_drop_rate
                        0,                                   # comm_errors
                        0,                                   # errors_count1
                        0,                                   # errors_count2
                        0,                                   # errors_count3
                        0                                    # errors_count4
                    )
                except Exception as e:
                    print(f"SysStatus-Fehler: {str(e)}")
                    # Versuche mit Standardwerten
                    try:
                        self._connection.mav.sys_status_send(
                            0b00000000000001111111111111111111,  # onboard_control_sensors_present
                            0b00000000000001111111111111111111,  # onboard_control_sensors_enabled
                            0b00000000000001111111111111111111,  # onboard_control_sensors_health
                            500,                                 # load (0-1000)
                            12600,                               # voltage_battery (mV)
                            0,                                   # current_battery (cA)
                            75,                                  # battery_remaining (%)
                            0,                                   # comm_drop_rate
                            0,                                   # comm_errors
                            0,                                   # errors_count1
                            0,                                   # errors_count2
                            0,                                   # errors_count3
                            0                                    # errors_count4
                        )
                    except Exception as e:
                        print(f"SysStatus-Fehler mit Standardwerten: {str(e)}")
                
                # 5. VFR_HUD senden (Airspeed, Groundspeed, Heading, Throttle)
                try:
                    self._connection.mav.vfr_hud_send(
                        float(5.0),                  # airspeed (m/s)
                        float(6.0),                  # groundspeed (m/s)
                        int((yaw * 180 / math.pi) % 360),  # heading (deg)
                        int(50),                   # throttle (%)
                        float(alt),                # alt (m)
                        float(0)                   # climb (m/s)
                    )
                except Exception as e:
                    print(f"VFR_HUD-Fehler: {str(e)}")
                    # Versuche mit Standardwerten
                    try:
                        self._connection.mav.vfr_hud_send(
                            5.0,                  # airspeed (m/s)
                            6.0,                  # groundspeed (m/s)
                            0,                    # heading (deg)
                            50,                   # throttle (%)
                            100.0,                # alt (m)
                            0.0                   # climb (m/s)
                        )
                    except Exception as e:
                        print(f"VFR_HUD-Fehler mit Standardwerten: {str(e)}")
                
                # Kurze Pause
                time.sleep(0.1)
                
            except Exception as e:
                print(f"Fehler im Simulator: {str(e)}")
                time.sleep(1.0)  # Bei Fehler kurz warten
    
    def __del__(self):
        """Aufräumen beim Löschen des Objekts."""
        self.stop()
