from PySide6.QtCore import QObject, Signal, Slot
from pymavlink import mavutil
from .logger import Logger
import time
import math

class MessageHandler(QObject):
    """Handles MAVLink message processing and distribution"""
    
    # Signals for different message types
    heartbeat_received = Signal(object)
    attitude_received = Signal(object)
    gps_received = Signal(object)
    battery_received = Signal(object)
    status_text_received = Signal(object)
    parameter_received = Signal(object)
    vfr_hud_received = Signal(object)  # Neues Signal für VFR_HUD
    error_occurred = Signal(str)
    
    def __init__(self, logger: Logger):
        super().__init__()
        self._logger = logger
        self._running = False
        self._mavlink_connection = None
        self._is_simulator = False
        
    def set_connection(self, connection, is_simulator=False):
        """Set the MAVLink connection to use"""
        self._mavlink_connection = connection
        self._is_simulator = is_simulator
        
    def start(self):
        """Start message handling"""
        if not self._mavlink_connection:
            error_msg = "❌ No MAVLink connection available"
            self._logger.addLog(error_msg)
            self.error_occurred.emit(error_msg)
            return False
            
        try:
            self._running = True
            self._logger.addLog("✅ Message handler started")
            
            # For simulator, send initial messages
            if self._is_simulator:
                self._send_simulator_messages()
                
            return True
        except Exception as e:
            error_msg = f"❌ Error starting message handler: {str(e)}"
            self._logger.addLog(error_msg)
            self.error_occurred.emit(error_msg)
            return False
        
    def stop(self):
        """Stop message handling"""
        self._running = False
        self._logger.addLog("🛑 Message handler stopped")
        
        # Reset simulator state
        self._last_sim_time = None
        self._last_sim_position = None
        
    def _send_simulated_data(self):
        """Send simulated sensor data"""
        try:
            # Get current time
            current_time = time.time()
            
            # Initialize position if not set
            if not hasattr(self, '_last_sim_position'):
                self._last_sim_position = {
                    'lat': 511657000,  # Start position
                    'lon': 104515000,
                    'alt': 100000,     # Start altitude in cm
                    'time': current_time
                }
            
            # Calculate movement
            time_diff = current_time - self._last_sim_position['time']
            
            # Update GPS position (move slowly)
            self._last_sim_position['lat'] += int(100 * time_diff)  # Move 0.1m/s
            self._last_sim_position['lon'] += int(100 * time_diff)  # Move 0.1m/s
            self._last_sim_position['alt'] += int(100 * math.sin(time_diff / 10))  # Sinusoidal altitude

            # Clamp to valid MAVLink ranges
            # lat/lon: -90*1e7 ... +90*1e7 / -180*1e7 ... +180*1e7
            self._last_sim_position['lat'] = max(min(self._last_sim_position['lat'], 900000000), -900000000)
            self._last_sim_position['lon'] = max(min(self._last_sim_position['lon'], 1800000000), -1800000000)
            # alt: -1000000 ... +10000000 (in mm or cm, here cm)
            self._last_sim_position['alt'] = max(min(self._last_sim_position['alt'], 10000000), -1000000)

            # Send GPS position
            self._mavlink_connection.mav.global_position_int_send(
                int(current_time * 1e3),  # timestamp
                self._last_sim_position['lat'],  # lat
                self._last_sim_position['lon'],  # lon
                self._last_sim_position['alt'],  # alt
                0, 0, 0, 0, 0, 0
            )
            
            # Update attitude (smooth variations)
            self._mavlink_connection.mav.attitude_send(
                int(current_time * 1e3),  # timestamp
                0.1 * math.sin(current_time),  # roll
                0.1 * math.cos(current_time),  # pitch
                0.1 * math.sin(2 * current_time),  # yaw
                0, 0, 0
            )
            
            # Update battery status
            self._mavlink_connection.mav.sys_status_send(
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
            )
            
            # Update last position time
            self._last_sim_position['time'] = current_time
            
        except Exception as e:
            error_msg = f"❌ Error sending simulated data: {str(e)}"
            self._logger.addLog(error_msg)
            self.error_occurred.emit(error_msg)
        
    def process_messages(self):
        """Process incoming MAVLink messages"""
        if not self._running or not self._mavlink_connection:
            return
        
        # Mehrere Nachrichten in einem Zyklus verarbeiten für bessere Leistung
        messages_processed = 0
        max_messages_per_cycle = 10  # Verarbeite bis zu 10 Nachrichten pro Zyklus
            
        try:
            while messages_processed < max_messages_per_cycle:
                msg = self._mavlink_connection.recv_match(blocking=False)
                if not msg:
                    break  # Keine weiteren Nachrichten in der Warteschlange
                    
                messages_processed += 1
                msg_type = msg.get_type()
                
                # Wichtige Debug-Ausgabe für Sensorwerte hinzufügen
                self._logger.addLog(f"Empfange MAVLink-Nachricht: {msg_type}")
                
                if msg_type == 'HEARTBEAT':
                    self.heartbeat_received.emit(msg)
                    self._handle_heartbeat(msg)
                    
                elif msg_type == 'ATTITUDE':
                    self.attitude_received.emit(msg)
                    # Debug
                    try:
                        roll_deg = round(msg.roll * 180 / 3.14159, 1)
                        pitch_deg = round(msg.pitch * 180 / 3.14159, 1)
                        yaw_deg = round(msg.yaw * 180 / 3.14159, 1)
                        self._logger.addLog(f"[DEBUG] Attitude: Roll={roll_deg}°, Pitch={pitch_deg}°, Yaw={yaw_deg}°")
                    except:
                        pass
                    
                elif msg_type == 'GLOBAL_POSITION_INT':
                    self.gps_received.emit(msg)
                    # Debug
                    try:
                        lat = msg.lat / 1e7
                        lon = msg.lon / 1e7
                        alt = msg.relative_alt / 1000.0
                        self._logger.addLog(f"[DEBUG] GPS: Lat={lat:.6f}, Lon={lon:.6f}, Alt={alt:.1f}m")
                    except:
                        pass
                    
                elif msg_type == 'SYS_STATUS':
                    self.battery_received.emit(msg)
                    # Debug
                    try:
                        voltage = msg.voltage_battery / 1000.0
                        current = msg.current_battery / 100.0
                        remaining = msg.battery_remaining
                        self._logger.addLog(f"[DEBUG] Batterie: {voltage:.1f}V, {current:.1f}A, {remaining}%")
                    except:
                        pass
                    
                elif msg_type == 'VFR_HUD':
                    # Direktes Signal für VFR_HUD hinzufügen
                    try:
                        airspeed = msg.airspeed
                        groundspeed = msg.groundspeed
                        self._logger.addLog(f"[DEBUG] Geschwindigkeit: Air={airspeed:.1f}m/s, Ground={groundspeed:.1f}m/s")
                        
                        # VFR_HUD-Signal direkt an SensorModel weiterleiten 
                        # Signal speziell für VFR_HUD erstellen
                        self.vfr_hud_received.emit(msg)
                    except Exception as vfr_error:
                        self._logger.addLog(f"Fehler bei VFR_HUD: {str(vfr_error)}")
                        pass
                    
                elif msg_type == 'STATUSTEXT':
                    self.status_text_received.emit(msg)
                    
                elif msg_type == 'PARAM_VALUE':
                    self.parameter_received.emit(msg)
                    
        except Exception as e:
            error_msg = f"Error bei Nachrichtenverarbeitung: {str(e)}"
            self._logger.addLog(error_msg)
            self.error_occurred.emit(error_msg)
            
    def _handle_heartbeat(self, msg):
        """Handle heartbeat message"""
        try:
            armed = (msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED) != 0
            mode = mavutil.mode_string_v10(msg)
            
            if not hasattr(self, '_last_mode') or self._last_mode != mode:
                self._logger.addLog(f"✈️ Flight Mode: {mode}")
                self._last_mode = mode
                
            if not hasattr(self, '_last_armed') or self._last_armed != armed:
                status = "ARMED" if armed else "DISARMED"
                self._logger.addLog(f"🔒 System {status}")
                self._last_armed = armed
                
        except Exception as e:
            error_msg = f"❌ Error handling heartbeat: {str(e)}"
            self._logger.addLog(error_msg)
            self.error_occurred.emit(error_msg)
            
    def request_data_streams(self):
        """Request data streams from the flight controller"""
        if not self._mavlink_connection:
            error_msg = "❌ No MAVLink connection available"
            self._logger.addLog(error_msg)
            self.error_occurred.emit(error_msg)
            return
            
        try:
            self._mavlink_connection.mav.request_data_stream_send(
                self._mavlink_connection.target_system,
                self._mavlink_connection.target_component,
                mavutil.mavlink.MAV_DATA_STREAM_ALL,
                10,  # 10 Hz
                1    # Enable
            )
            self._logger.addLog("📡 Data stream request sent")
        except Exception as e:
            error_msg = f"❌ Error requesting data streams: {str(e)}"
            self._logger.addLog(error_msg)
            self.error_occurred.emit(error_msg)
            
    def _send_simulator_messages(self):
        """Send initial messages to the simulator"""
        try:
            if not self._mavlink_connection:
                self._logger.addLog("⚠️ No MAVLink connection available for simulator messages")
                return
                
            # Send initial heartbeat
            self._mavlink_connection.mav.heartbeat_send(
                mavutil.mavlink.MAV_TYPE_QUADROTOR,
                mavutil.mavlink.MAV_AUTOPILOT_GENERIC,
                0, 0, 0
            )
            
            # Send initial GPS position
            self._mavlink_connection.mav.global_position_int_send(
                int(time.time() * 1e3),  # timestamp
                511657000,  # lat (51.1657)
                104515000,  # lon (10.4515)
                0, 0, 0, 0, 0, 0
            )
            
            # Send initial attitude
            self._mavlink_connection.mav.attitude_send(
                int(time.time() * 1e3),  # timestamp
                0, 0, 0,  # roll, pitch, yaw
                0, 0, 0  # rollspeed, pitchspeed, yawspeed
            )
            
            # Send initial battery status
            self._mavlink_connection.mav.sys_status_send(
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
            )
            
        except Exception as e:
            error_msg = f"❌ Error sending simulator messages: {str(e)}"
            self._logger.addLog(error_msg)
            self.error_occurred.emit(error_msg)

    def _send_simulated_data(self):
        """Send simulated sensor data"""
        try:
            # Update GPS position (move slightly)
            self._mavlink_connection.mav.global_position_int_send(
                int(time.time() * 1e3),
                511657000 + int(time.time() * 1000),  # lat with slight movement
                104515000 + int(time.time() * 1000),  # lon with slight movement
                0, 0, 0, 0, 0, 0
            )
            
            # Update attitude (add some variation)
            self._mavlink_connection.mav.attitude_send(
                int(time.time() * 1e3),
                0.1 * math.sin(time.time()),  # roll
                0.1 * math.cos(time.time()),  # pitch
                0.1 * math.sin(2 * time.time()),  # yaw
                0, 0, 0
            )
            
            # Update battery status
            self._mavlink_connection.mav.sys_status_send(
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
            )
            
        except Exception as e:
            error_msg = f"❌ Error sending simulated data: {str(e)}"
            self._logger.addLog(error_msg)
            self.error_occurred.emit(error_msg)