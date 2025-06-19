import threading
import time
import math
from pymavlink import mavutil
from PySide6.QtCore import QObject, Signal

class MAVLinkSimulator(QObject):
    """Simulates MAVLink messages for testing purposes"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._running = False
        self._thread = None
        
    def start(self):
        """Start the simulator"""
        try:
            # Create UDP connection (send to 14551)
            self._connection = mavutil.mavlink_connection(
                'udpout:localhost:14551',
                source_system=1,
                source_component=1,
                dialect='ardupilotmega'
            )
            
            self._running = True
            self._thread = threading.Thread(target=self._run)
            self._thread.daemon = True
            self._thread.start()
            return True
            
        except Exception as e:
            print(f"Failed to start simulator: {str(e)}")
            return False
            
    def stop(self):
        """Stop the simulator"""
        self._running = False
        if self._thread:
            self._thread.join()
        if hasattr(self, '_connection'):
            try:
                self._connection.close()
            except:
                pass
            self._connection = None
            
    def _run(self):
        """Main simulation loop"""
        start_time = time.time()
        lat = 51.1657  # Start latitude
        lon = 10.4515  # Start longitude
        altitude = 100.0  # Start altitude
        roll = 0.0
        pitch = 0.0
        yaw = 0.0
        
        while self._running:
            try:
                current_time = time.time()
                
                # Update position (smooth movement)
                lat += 0.00001 * (current_time - start_time)  # Move north
                lon += 0.00001 * (current_time - start_time)  # Move east
                altitude = 100 + 10 * math.sin(current_time / 10)  # Sinusoidal altitude

                # Clamp values to valid ranges
                lat = max(min(lat, 90.0), -90.0)
                lon = max(min(lon, 180.0), -180.0)
                altitude = max(min(altitude, 10000.0), -100.0)  # -100m to 10km
                
                # Update attitude (smooth variations)
                roll = 0.1 * math.sin(current_time)
                pitch = 0.1 * math.cos(current_time)
                yaw = 0.1 * math.sin(2 * current_time)
                
                # Send heartbeat to maintain connection
                self._connection.mav.heartbeat_send(
                    mavutil.mavlink.MAV_TYPE_QUADROTOR,
                    mavutil.mavlink.MAV_AUTOPILOT_GENERIC,
                    0, 0, 0
                )
                
                # Send GPS position - alle Parameter korrekt übergeben
                self._connection.mav.global_position_int_send(
                    int(current_time * 1e3),  # timestamp (ms)
                    int(lat * 1e7),           # latitude (degE7)
                    int(lon * 1e7),           # longitude (degE7)
                    int(altitude * 1000),     # altitude AMSL (mm)
                    int(altitude * 1000),     # relative altitude (mm)
                    int(0.5 * 100),           # ground speed X (cm/s)
                    int(0.5 * 100),           # ground speed Y (cm/s)
                    int(0.0 * 100),           # ground speed Z (cm/s)
                    int(yaw * 100)            # heading (cdeg)
                )
                
                # Send attitude - alle Parameter korrekt übergeben
                self._connection.mav.attitude_send(
                    int(current_time * 1e3),  # timestamp (ms)
                    roll,                     # roll (rad)
                    pitch,                    # pitch (rad)
                    yaw,                      # yaw (rad)
                    0.01,                     # rollspeed (rad/s)
                    0.01,                     # pitchspeed (rad/s)
                    0.01                      # yawspeed (rad/s)
                )
                
                # Send battery status - mit realistischen Werten
                self._connection.mav.sys_status_send(
                    0b00000000000001111111111111111111,  # onboard_control_sensors_present
                    0b00000000000001111111111111111111,  # onboard_control_sensors_enabled
                    0b00000000000001111111111111111111,  # onboard_control_sensors_health
                    500,                                 # load (0-1000)
                    int(11.5 * 1000),                   # voltage_battery (mV)
                    int(10.5 * 100),                    # current_battery (cA)
                    75,                                  # battery_remaining (%)
                    0, 0, 0, 0, 0                       # andere Felder
                )
                
                # Reset start time for next iteration
                start_time = current_time
                
                # Wait a bit before next update
                time.sleep(0.1)
                
            except Exception as e:
                print(f"Simulator error: {str(e)}")
                break
                
    def __del__(self):
        self.stop()
