"""
SimulatedDrone Class

This class simulates a drone with realistic physics and behavior for testing purposes.
It can send MAVLink messages to simulate various drone behaviors and states.

Usage:
    drone = SimulatedDrone(port='udpin:localhost:14550')
    drone.connect()
    drone.start_simulation()  # Starts the simulation loop
    drone.set_target_position(51.1657, 10.4515, 100)  # Set target position
    time.sleep(10)  # Let the drone fly
    drone.stop_simulation()  # Stop the simulation
    drone.close()
"""

import time
import math
import threading
from pymavlink import mavutil
from dataclasses import dataclass
from typing import Tuple, Optional

@dataclass
class DroneState:
    """Represents the current state of the drone."""
    lat: float = 51.1657  # Start position in Germany
    lon: float = 10.4515
    alt: float = 0.0
    roll: float = 0.0
    pitch: float = 0.0
    yaw: float = 0.0
    groundspeed: float = 0.0
    airspeed: float = 0.0
    battery_remaining: float = 100.0
    voltage: float = 12.0
    current: float = 0.0
    mode: str = "STABILIZE"
    armed: bool = False

class SimulatedDrone:
    def __init__(self, port='udpin:localhost:14550'):
        self.port = port
        self.mavlink_connection = None
        self.state = DroneState()
        self.target_position: Optional[Tuple[float, float, float]] = None
        self.simulation_running = False
        self.simulation_thread: Optional[threading.Thread] = None
        self.last_update_time = time.time()
        
        # Drone parameters
        self.max_speed = 10.0  # m/s
        self.max_altitude = 120.0  # meters
        self.battery_capacity = 5200  # mAh
        self.current_draw = 0.0  # mA
        
    def connect(self):
        """Establishes a connection to the simulated drone."""
        self.mavlink_connection = mavutil.mavlink_connection(self.port)
        print(f"Connected to simulated drone on {self.port}")

    def start_simulation(self):
        """Starts the simulation loop in a separate thread."""
        if not self.simulation_running:
            self.simulation_running = True
            self.simulation_thread = threading.Thread(target=self._simulation_loop)
            self.simulation_thread.daemon = True
            self.simulation_thread.start()
            print("Simulation started")

    def stop_simulation(self):
        """Stops the simulation loop."""
        self.simulation_running = False
        if self.simulation_thread:
            self.simulation_thread.join()
            print("Simulation stopped")

    def _simulation_loop(self):
        """Main simulation loop that updates drone state and sends messages."""
        while self.simulation_running:
            current_time = time.time()
            dt = current_time - self.last_update_time
            self.last_update_time = current_time
            
            self._update_state(dt)
            self._send_all_messages()
            time.sleep(0.1)  # 10Hz update rate

    def _update_state(self, dt: float):
        """Updates the drone state based on physics and current commands."""
        if self.target_position:
            target_lat, target_lon, target_alt = self.target_position
            
            # Calculate distance to target
            lat_diff = target_lat - self.state.lat
            lon_diff = target_lon - self.state.lon
            alt_diff = target_alt - self.state.alt
            
            # Update position with realistic movement
            distance = math.sqrt(lat_diff**2 + lon_diff**2)
            if distance > 0.0001:  # If not at target (using smaller threshold for GPS coordinates)
                # Calculate movement speed
                speed = min(self.max_speed, distance / dt)
                self.state.groundspeed = speed
                
                # Update position with smaller steps for GPS coordinates
                self.state.lat += (lat_diff / distance) * speed * dt * 0.0001
                self.state.lon += (lon_diff / distance) * speed * dt * 0.0001
                self.state.alt += (alt_diff / abs(alt_diff)) * min(2.0, abs(alt_diff)) * dt
                
                # Update attitude based on movement - with safety checks
                if abs(lat_diff) > 0.0001 or abs(lon_diff) > 0.0001:
                    self.state.roll = math.atan2(lat_diff, lon_diff)
                    self.state.yaw = math.atan2(lon_diff, lat_diff)
                else:
                    self.state.roll = 0.0
                    self.state.yaw = 0.0
                
                if distance > 0.0001:
                    self.state.pitch = math.atan2(alt_diff, distance)
                else:
                    self.state.pitch = 0.0
                
                # Update battery
                self.current_draw = 2000 + speed * 100  # More current at higher speeds
                self.state.battery_remaining -= (self.current_draw / self.battery_capacity) * dt * 100
                self.state.voltage = 12.0 * (self.state.battery_remaining / 100.0)
                self.state.current = self.current_draw
                
                # Debug output
                print(f"Debug - Position: lat={self.state.lat:.6f}, lon={self.state.lon:.6f}, alt={self.state.alt:.1f}")

    def _send_all_messages(self):
        """Sends all relevant MAVLink messages with current state."""
        self.send_heartbeat()
        self.send_global_position_int(
            self.state.lat,
            self.state.lon,
            self.state.alt
        )
        self.send_attitude(self.state.roll, self.state.pitch, self.state.yaw)
        self.send_sys_status(
            int(self.state.voltage * 1000),
            int(self.state.current),
            int(self.state.battery_remaining)
        )
        self.send_vfr_hud(
            self.state.alt,
            self.state.groundspeed,
            self.state.airspeed,
            int(math.degrees(self.state.yaw)),
            50,  # throttle
            0.0  # climb rate
        )

    def set_target_position(self, lat: float, lon: float, alt: float):
        """Sets the target position for the drone to fly to."""
        self.target_position = (lat, lon, min(alt, self.max_altitude))

    def set_mode(self, mode: str):
        """Sets the flight mode of the drone."""
        self.state.mode = mode
        print(f"Flight mode changed to {mode}")

    def arm(self):
        """Arms the drone."""
        self.state.armed = True
        print("Drone armed")

    def disarm(self):
        """Disarms the drone."""
        self.state.armed = False
        print("Drone disarmed")

    def send_heartbeat(self):
        """Sends a heartbeat message."""
        self.mavlink_connection.mav.heartbeat_send(
            mavutil.mavlink.MAV_TYPE_QUADROTOR,
            mavutil.mavlink.MAV_AUTOPILOT_ARDUPILOTMEGA,
            mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
            0,
            mavutil.mavlink.MAV_STATE_ACTIVE
        )

    def send_global_position_int(self, lat, lon, alt):
        """Sends a global position message."""
        try:
            # Convert to integers with proper scaling
            lat_int = int(lat * 1e7)
            lon_int = int(lon * 1e7)
            alt_int = int(alt * 1000)
            
            # Ensure values are within valid ranges for MAVLink
            lat_int = max(-90 * 1e7, min(90 * 1e7, lat_int))  # Valid latitude range
            lon_int = max(-180 * 1e7, min(180 * 1e7, lon_int))  # Valid longitude range
            alt_int = max(-1000000, min(1000000, alt_int))  # Reasonable altitude range
            
            # Set other required values
            relative_alt = 0
            vx = 0
            vy = 0
            vz = 0
            hdg = 0
            
            print(f"Debug - Sending position: lat={lat_int}, lon={lon_int}, alt={alt_int}, hdg={hdg}")
            
            # Send the message
            self.mavlink_connection.mav.global_position_int_send(
                int(time.time() * 1000),  # time_boot_ms
                int(lat_int),             # lat
                int(lon_int),             # lon
                int(alt_int),             # alt
                int(relative_alt),        # relative_alt
                int(vx),                  # vx
                int(vy),                  # vy
                int(vz),                  # vz
                int(hdg)                  # hdg
            )
        except Exception as e:
            print(f"Error sending global position: {str(e)}")
            print(f"Values: lat={lat}, lon={lon}, alt={alt}")
            print(f"Converted: lat_int={lat_int}, lon_int={lon_int}, alt_int={alt_int}, hdg={hdg}")

    def _safe_angle(self, value):
        import math
        try:
            value = float(value)
            if math.isnan(value) or math.isinf(value):
                return 0.0
            while value < -math.pi:
                value += 2 * math.pi
            while value > math.pi:
                value -= 2 * math.pi
            return value
        except Exception:
            return 0.0

    def send_attitude(self, roll, pitch, yaw):
        """Sends an attitude message."""
        try:
            # Sanitize angles
            roll = self._safe_angle(roll)
            pitch = self._safe_angle(pitch)
            yaw = self._safe_angle(yaw)
            
            # Additional safety check
            if any(map(lambda x: not isinstance(x, float) or math.isnan(x) or math.isinf(x), [roll, pitch, yaw])):
                print(f"Invalid attitude values detected: roll={roll}, pitch={pitch}, yaw={yaw}")
                return
                
            # Ensure angles are within valid ranges
            roll = max(-math.pi, min(math.pi, roll))
            pitch = max(-math.pi, min(math.pi, pitch))
            yaw = max(-math.pi, min(math.pi, yaw))
            
            print(f"Debug - Attitude: roll={roll}, pitch={pitch}, yaw={yaw}")
            
            # Convert to float32 for MAVLink
            time_boot_ms = int(time.time() * 1000)
            roll = float(roll)
            pitch = float(pitch)
            yaw = float(yaw)
            rollspeed = float(0.0)
            pitchspeed = float(0.0)
            yawspeed = float(0.0)
            
            # Send the message
            self.mavlink_connection.mav.attitude_send(
                time_boot_ms,
                roll,
                pitch,
                yaw,
                rollspeed,
                pitchspeed,
                yawspeed
            )
        except Exception as e:
            print(f"Error sending attitude: {str(e)}")
            print(f"Values: roll={roll}, pitch={pitch}, yaw={yaw}")

    def send_sys_status(self, voltage, current, remaining):
        """Sends a system status message."""
        try:
            # Ensure values are within valid ranges
            voltage = max(0, min(65535, voltage))
            current = max(0, min(65535, current))
            remaining = max(0, min(100, remaining))
            
            # Send the message with correct number of arguments
            self.mavlink_connection.mav.sys_status_send(
                voltage,      # onboard_control_sensors_present
                voltage,      # onboard_control_sensors_enabled
                voltage,      # onboard_control_sensors_health
                current,      # load
                voltage,      # voltage_battery
                current,      # current_battery
                remaining,    # battery_remaining
                current,      # drop_rate_comm
                current,      # errors_comm
                current,      # errors_count1
                current,      # errors_count2
                current,      # errors_count3
                current,      # errors_count4
                0            # onboard_control_sensors_present_extended
            )
        except Exception as e:
            print(f"Error sending system status: {str(e)}")
            print(f"Values: voltage={voltage}, current={current}, remaining={remaining}")

    def send_vfr_hud(self, alt, groundspeed, airspeed, heading, throttle, climb):
        """Sends VFR HUD data."""
        self.mavlink_connection.mav.vfr_hud_send(
            airspeed,
            groundspeed,
            heading,
            throttle,
            alt,
            climb
        )

    def send_statustext(self, severity, text):
        """Sends a status text message."""
        self.mavlink_connection.mav.statustext_send(
            severity,
            text.encode()
        )

    def close(self):
        """Closes the connection to the simulated drone."""
        self.stop_simulation()
        if self.mavlink_connection:
            self.mavlink_connection.close()
            print("Connection to simulated drone closed") 