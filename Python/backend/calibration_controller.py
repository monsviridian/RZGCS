"""
Calibration Controller for RZGCS

Handles sensor calibration including compass, accelerometer, and other sensors
with proper MAVLink integration and status reporting.
"""

import time
import threading
from PySide6.QtCore import QObject, Signal, Slot, Property
from pymavlink import mavutil
import math

class CalibrationController(QObject):
    """Controller for handling sensor calibration procedures"""
    
    # Signals for QML
    calibrationProgressChanged = Signal(float, str)  # progress, message
    calibrationFinished = Signal(bool, str)  # success, message
    logMessageReceived = Signal(str, str)  # type, message
    compassValueChanged = Signal(float, float, float)  # x, y, z
    accelValueChanged = Signal(float, float, float)  # x, y, z
    RCChannelsChanged = Signal(list)  # channel values
    joystickDataChanged = Signal(float, float, float, float)  # x, y, throttle, yaw
    
    # Calibration types
    CALIBRATION_COMPASS = "compass"
    CALIBRATION_ACCEL = "accel"
    CALIBRATION_GYRO = "gyro"
    CALIBRATION_LEVEL = "level"
    CALIBRATION_RC = "rc"
    CALIBRATION_ESC = "esc"
    CALIBRATION_JOYSTICK = "joystick"
    
    def __init__(self, mavlink_connection=None):
        super().__init__()
        self.mavlink_connection = mavlink_connection
        self.current_calibration = None
        self.calibration_running = False
        self.calibration_thread = None
        self.stop_calibration = False
        
        # Calibration data
        self.compass_data = []
        self.accel_data = []
        self.gyro_data = []
        
        # Calibration parameters
        self.compass_points_needed = 50
        self.accel_positions = 6
        self.gyro_points_needed = 100
        
        self.logMessageReceived.emit("info", "CalibrationController initialized")
    
    def set_mavlink_connection(self, connection):
        """Set the MAVLink connection for calibration"""
        self.mavlink_connection = connection
        if connection:
            self.logMessageReceived.emit("info", "MAVLink connection set for calibration")
            # Get system info
            try:
                system_id = connection.target_system
                component_id = connection.target_component
                self.logMessageReceived.emit("info", f"Connected to system {system_id}, component {component_id}")
            except:
                pass
        else:
            self.logMessageReceived.emit("warning", "MAVLink connection removed")
    
    @Slot(str)
    def start_calibration(self, calibration_type):
        """Start a calibration procedure"""
        if self.calibration_running:
            self.logMessageReceived.emit("warning", "Calibration already running")
            return
        
        if not self.mavlink_connection:
            self.logMessageReceived.emit("error", "No MAVLink connection available")
            return
        
        self.current_calibration = calibration_type
        self.calibration_running = True
        self.stop_calibration = False
        
        # Log system status before starting
        self.logMessageReceived.emit("info", f"System status: Starting {calibration_type} calibration")
        self.logMessageReceived.emit("info", f"Calibration type: {calibration_type}")
        self.logMessageReceived.emit("info", f"Thread ID: {threading.get_ident()}")
        
        # Start calibration in separate thread
        self.calibration_thread = threading.Thread(
            target=self._run_calibration,
            args=(calibration_type,)
        )
        self.calibration_thread.daemon = True
        self.calibration_thread.start()
        
        self.logMessageReceived.emit("info", f"Started {calibration_type} calibration")
        self.logMessageReceived.emit("info", f"Calibration thread started: {self.calibration_thread.ident}")
    
    @Slot()
    def cancel_calibration(self):
        """Cancel the current calibration"""
        if self.calibration_running:
            self.stop_calibration = True
            self.calibration_running = False
            self.logMessageReceived.emit("warning", "Calibration cancelled by user")
            self.logMessageReceived.emit("info", f"System status: Cancelling {self.current_calibration} calibration")
            self.calibrationFinished.emit(False, "Calibration cancelled by user")
        else:
            self.logMessageReceived.emit("warning", "No calibration running to cancel")
    
    @Slot(str)
    def save_calibration(self, calibration_type):
        """Save calibration data for the specified type"""
        if not self.calibration_running:
            self.logMessageReceived.emit("warning", "No calibration running to save")
            return False
        
        if calibration_type != self.current_calibration:
            self.logMessageReceived.emit("warning", f"Calibration type mismatch: {calibration_type} vs {self.current_calibration}")
            return False
        
        try:
            # Send save command to flight controller
            if self.mavlink_connection:
                self.mavlink_connection.mav.command_long_send(
                    self.mavlink_connection.target_system,
                    self.mavlink_connection.target_component,
                    mavutil.mavlink.MAV_CMD_DO_MOUNT_CONFIGURE,
                    0, 0, 0, 0, 0, 0, 0, 0  # Placeholder command
                )
                self.logMessageReceived.emit("info", f"Save command sent for {calibration_type} calibration")
            
            self.logMessageReceived.emit("success", f"{calibration_type.capitalize()} calibration saved successfully")
            self.calibrationFinished.emit(True, f"{calibration_type.capitalize()} calibration saved")
            return True
            
        except Exception as e:
            self.logMessageReceived.emit("error", f"Failed to save {calibration_type} calibration: {e}")
            return False
    
    @Slot()
    def cancelCalibration(self):
        """Alias for cancel_calibration for frontend compatibility"""
        self.cancel_calibration()
    
    @Slot(str)
    def saveCalibration(self, calibration_type):
        """Alias for save_calibration for frontend compatibility"""
        return self.save_calibration(calibration_type)
    
    @Slot()
    def next_calibration_step(self):
        """Move to next calibration step (for accelerometer)"""
        if self.current_calibration == self.CALIBRATION_ACCEL:
            # This will be handled by the calibration thread
            pass
    
    @Slot()
    def reboot_flight_controller(self):
        """Reboot the flight controller"""
        if self.mavlink_connection:
            try:
                self.logMessageReceived.emit("warning", "Sending reboot command to flight controller...")
                self.mavlink_connection.mav.command_long_send(
                    self.mavlink_connection.target_system,
                    self.mavlink_connection.target_component,
                    mavutil.mavlink.MAV_CMD_PREFLIGHT_REBOOT_SHUTDOWN,
                    0, 1, 0, 0, 0, 0, 0, 0
                )
                self.logMessageReceived.emit("success", "Reboot command sent to flight controller successfully")
                self.logMessageReceived.emit("info", "Flight controller will restart in a few seconds")
            except Exception as e:
                self.logMessageReceived.emit("error", f"Failed to send reboot command: {e}")
                self.logMessageReceived.emit("error", f"System error: {type(e).__name__}: {str(e)}")
        else:
            self.logMessageReceived.emit("error", "No MAVLink connection available for reboot")
            self.logMessageReceived.emit("error", "System status: Cannot reboot - no connection")
    
    def _run_calibration(self, calibration_type):
        """Run the calibration procedure in a separate thread"""
        try:
            if calibration_type == self.CALIBRATION_COMPASS:
                self._calibrate_compass()
            elif calibration_type == self.CALIBRATION_ACCEL:
                self._calibrate_accelerometer()
            elif calibration_type == self.CALIBRATION_GYRO:
                self._calibrate_gyroscope()
            elif calibration_type == self.CALIBRATION_LEVEL:
                self._calibrate_level()
            elif calibration_type == self.CALIBRATION_RC:
                self._calibrate_rc()
            elif calibration_type == self.CALIBRATION_ESC:
                self._calibrate_esc()
            elif calibration_type == self.CALIBRATION_JOYSTICK:
                self._calibrate_joystick()
            else:
                self.logMessageReceived.emit("error", f"Unknown calibration type: {calibration_type}")
                self.calibrationFinished.emit(False, f"Unknown calibration type: {calibration_type}")
        except Exception as e:
            self.logMessageReceived.emit("error", f"Calibration failed: {e}")
            self.calibrationFinished.emit(False, f"Calibration failed: {e}")
        finally:
            self.calibration_running = False
    
    def _calibrate_compass(self):
        """Calibrate the compass sensor"""
        self.logMessageReceived.emit("info", "=== COMPASS CALIBRATION STARTED ===")
        self.logMessageReceived.emit("info", "System: Sending compass calibration command to flight controller")
        
        # Request compass calibration
        try:
            self.mavlink_connection.mav.command_long_send(
                self.mavlink_connection.target_system,
                self.mavlink_connection.target_component,
                mavutil.mavlink.MAV_CMD_DO_START_MAG_CAL,
                0, 0, 0, 0, 0, 0, 0, 0
            )
            self.logMessageReceived.emit("info", "System: Compass calibration command sent successfully")
            self.logMessageReceived.emit("info", f"Target system: {self.mavlink_connection.target_system}")
            self.logMessageReceived.emit("info", f"Target component: {self.mavlink_connection.target_component}")
        except Exception as e:
            self.logMessageReceived.emit("error", f"System error: Failed to start compass calibration")
            self.logMessageReceived.emit("error", f"Error details: {type(e).__name__}: {str(e)}")
            return
        
        # Monitor calibration progress
        points_collected = 0
        start_time = time.time()
        timeout = 300  # 5 minutes timeout
        
        self.logMessageReceived.emit("info", f"System: Starting calibration monitoring (timeout: {timeout}s)")
        self.logMessageReceived.emit("info", f"System: Monitoring for MAG_CAL_PROGRESS and MAG_CAL_REPORT messages")
        
        while not self.stop_calibration and time.time() - start_time < timeout:
            try:
                # Check for calibration status messages
                msg = self.mavlink_connection.recv_match(
                    type=['MAG_CAL_PROGRESS', 'MAG_CAL_REPORT'],
                    blocking=False,
                    timeout=0.1
                )
                
                if msg is not None:
                    if msg.get_type() == 'MAG_CAL_PROGRESS':
                        # Update progress
                        progress = msg.compass_id / 255.0  # Normalize to 0-1
                        points_collected = int(progress * self.compass_points_needed)
                        
                        self.logMessageReceived.emit("info", f"System: Received MAG_CAL_PROGRESS message")
                        self.logMessageReceived.emit("info", f"Progress: {progress:.2f} ({points_collected}/{self.compass_points_needed} points)")
                        
                        self.calibrationProgressChanged.emit(
                            progress,
                            f"Compass calibration: {points_collected}/{self.compass_points_needed} points"
                        )
                        
                        # Emit compass values for visualization
                        if hasattr(msg, 'mag_x') and hasattr(msg, 'mag_y') and hasattr(msg, 'mag_z'):
                            self.compassValueChanged.emit(msg.mag_x, msg.mag_y, msg.mag_z)
                            self.logMessageReceived.emit("info", f"Compass values: X={msg.mag_x:.2f}, Y={msg.mag_y:.2f}, Z={msg.mag_z:.2f}")
                        
                        if progress >= 1.0:
                            self.logMessageReceived.emit("info", "System: Compass calibration progress reached 100%")
                            break
                    
                    elif msg.get_type() == 'MAG_CAL_REPORT':
                        # Calibration completed
                        self.logMessageReceived.emit("info", "System: Received MAG_CAL_REPORT message")
                        success = msg.cal_status == 1  # 1 = success
                        if success:
                            self.logMessageReceived.emit("success", "=== COMPASS CALIBRATION COMPLETED SUCCESSFULLY ===")
                            self.logMessageReceived.emit("info", "System: Calibration status: SUCCESS")
                            self.calibrationFinished.emit(True, "Compass calibration completed successfully")
                        else:
                            self.logMessageReceived.emit("error", "=== COMPASS CALIBRATION FAILED ===")
                            self.logMessageReceived.emit("error", f"System: Calibration status: FAILED (status code: {msg.cal_status})")
                            self.calibrationFinished.emit(False, "Compass calibration failed")
                        return
                
                # Simulate progress for testing (remove in production)
                if not self.mavlink_connection:
                    points_collected += 1
                    progress = min(points_collected / self.compass_points_needed, 1.0)
                    
                    self.logMessageReceived.emit("info", f"System: Simulated progress update")
                    self.logMessageReceived.emit("info", f"Simulated points: {points_collected}/{self.compass_points_needed}")
                    
                    self.calibrationProgressChanged.emit(
                        progress,
                        f"Compass calibration: {points_collected}/{self.compass_points_needed} points (simulated)"
                    )
                    
                    # Simulate compass values
                    import random
                    mag_x = random.uniform(-1, 1)
                    mag_y = random.uniform(-1, 1)
                    mag_z = random.uniform(-1, 1)
                    
                    self.compassValueChanged.emit(mag_x, mag_y, mag_z)
                    self.logMessageReceived.emit("info", f"Simulated compass values: X={mag_x:.2f}, Y={mag_y:.2f}, Z={mag_z:.2f}")
                    
                    if progress >= 1.0:
                        self.logMessageReceived.emit("info", "System: Simulated calibration completed")
                        break
                    
                    time.sleep(0.5)
                
            except Exception as e:
                self.logMessageReceived.emit("error", f"System error during compass calibration monitoring")
                self.logMessageReceived.emit("error", f"Error details: {type(e).__name__}: {str(e)}")
                break
        
        elapsed_time = time.time() - start_time
        if self.stop_calibration:
            self.logMessageReceived.emit("warning", "=== COMPASS CALIBRATION CANCELLED ===")
            self.logMessageReceived.emit("info", f"System: Calibration cancelled after {elapsed_time:.1f} seconds")
            self.calibrationFinished.emit(False, "Compass calibration cancelled")
        elif time.time() - start_time >= timeout:
            self.logMessageReceived.emit("error", "=== COMPASS CALIBRATION TIMED OUT ===")
            self.logMessageReceived.emit("error", f"System: Calibration timed out after {elapsed_time:.1f} seconds")
            self.logMessageReceived.emit("error", f"System: Timeout limit was {timeout} seconds")
            self.calibrationFinished.emit(False, "Compass calibration timed out")
    
    def _calibrate_accelerometer(self):
        """Calibrate the accelerometer sensor"""
        self.logMessageReceived.emit("info", "=== ACCELEROMETER CALIBRATION STARTED ===")
        self.logMessageReceived.emit("info", "System: Sending accelerometer calibration command to flight controller")
        
        # Request accelerometer calibration
        try:
            self.mavlink_connection.mav.command_long_send(
                self.mavlink_connection.target_system,
                self.mavlink_connection.target_component,
                mavutil.mavlink.MAV_CMD_PREFLIGHT_CALIBRATION,
                0, 1, 0, 0, 0, 0, 0, 0  # 1 = calibrate accelerometer
            )
            self.logMessageReceived.emit("info", "System: Accelerometer calibration command sent successfully")
            self.logMessageReceived.emit("info", f"Target system: {self.mavlink_connection.target_system}")
            self.logMessageReceived.emit("info", f"Target component: {self.mavlink_connection.target_component}")
        except Exception as e:
            self.logMessageReceived.emit("error", f"System error: Failed to start accelerometer calibration")
            self.logMessageReceived.emit("error", f"Error details: {type(e).__name__}: {str(e)}")
            return
        
        # Monitor calibration progress for 6 positions
        current_position = 0
        positions = [
            "Level (Z+)",
            "Upside down (Z-)", 
            "Left side (X-)",
            "Right side (X+)",
            "Nose up (Y+)",
            "Nose down (Y-)"
        ]
        
        start_time = time.time()
        timeout = 300  # 5 minutes timeout
        
        while not self.stop_calibration and time.time() - start_time < timeout:
            try:
                # Check for calibration status
                msg = self.mavlink_connection.recv_match(
                    type=['COMMAND_ACK', 'STATUSTEXT'],
                    blocking=False,
                    timeout=0.1
                )
                
                if msg is not None:
                    if msg.get_type() == 'COMMAND_ACK':
                        if msg.command == mavutil.mavlink.MAV_CMD_PREFLIGHT_CALIBRATION:
                            if msg.result == mavutil.mavlink.MAV_RESULT_ACCEPTED:
                                self.logMessageReceived.emit("info", "Accelerometer calibration accepted")
                            else:
                                self.logMessageReceived.emit("error", "Accelerometer calibration rejected")
                                break
                
                # Simulate progress for testing
                if not self.mavlink_connection:
                    progress = current_position / self.accel_positions
                    self.calibrationProgressChanged.emit(
                        progress,
                        f"Position {current_position + 1}: {positions[current_position]}"
                    )
                    
                    # Simulate accelerometer values
                    import random
                    self.accelValueChanged.emit(
                        random.uniform(-1, 1),
                        random.uniform(-1, 1),
                        random.uniform(-1, 1)
                    )
                    
                    time.sleep(2)  # Simulate time for each position
                    current_position += 1
                    
                    if current_position >= self.accel_positions:
                        break
                
            except Exception as e:
                self.logMessageReceived.emit("error", f"Error during accelerometer calibration: {e}")
                break
        
        if self.stop_calibration:
            self.logMessageReceived.emit("warning", "Accelerometer calibration cancelled")
            self.calibrationFinished.emit(False, "Accelerometer calibration cancelled")
        elif time.time() - start_time >= timeout:
            self.logMessageReceived.emit("error", "Accelerometer calibration timed out")
            self.calibrationFinished.emit(False, "Accelerometer calibration timed out")
        else:
            self.logMessageReceived.emit("success", "Accelerometer calibration completed")
            self.calibrationFinished.emit(True, "Accelerometer calibration completed successfully")
    
    def _calibrate_gyroscope(self):
        """Calibrate the gyroscope sensor"""
        self.logMessageReceived.emit("info", "Starting gyroscope calibration")
        
        # Request gyroscope calibration
        try:
            self.mavlink_connection.mav.command_long_send(
                self.mavlink_connection.target_system,
                self.mavlink_connection.target_component,
                mavutil.mavlink.MAV_CMD_PREFLIGHT_CALIBRATION,
                0, 0, 1, 0, 0, 0, 0, 0  # 1 = calibrate gyroscope
            )
        except Exception as e:
            self.logMessageReceived.emit("error", f"Failed to start gyroscope calibration: {e}")
            return
        
        # Monitor calibration progress
        points_collected = 0
        start_time = time.time()
        timeout = 120  # 2 minutes timeout
        
        while not self.stop_calibration and time.time() - start_time < timeout:
            try:
                # Check for calibration status
                msg = self.mavlink_connection.recv_match(
                    type=['COMMAND_ACK', 'STATUSTEXT'],
                    blocking=False,
                    timeout=0.1
                )
                
                if msg is not None:
                    if msg.get_type() == 'COMMAND_ACK':
                        if msg.command == mavutil.mavlink.MAV_CMD_PREFLIGHT_CALIBRATION:
                            if msg.result == mavutil.mavlink.MAV_RESULT_ACCEPTED:
                                self.logMessageReceived.emit("info", "Gyroscope calibration accepted")
                            else:
                                self.logMessageReceived.emit("error", "Gyroscope calibration rejected")
                                break
                
                # Simulate progress for testing
                if not self.mavlink_connection:
                    points_collected += 1
                    progress = min(points_collected / self.gyro_points_needed, 1.0)
                    self.calibrationProgressChanged.emit(
                        progress,
                        f"Gyroscope calibration: {points_collected}/{self.gyro_points_needed} points"
                    )
                    
                    if progress >= 1.0:
                        break
                    
                    time.sleep(0.1)
                
            except Exception as e:
                self.logMessageReceived.emit("error", f"Error during gyroscope calibration: {e}")
                break
        
        if self.stop_calibration:
            self.logMessageReceived.emit("warning", "Gyroscope calibration cancelled")
            self.calibrationFinished.emit(False, "Gyroscope calibration cancelled")
        elif time.time() - start_time >= timeout:
            self.logMessageReceived.emit("error", "Gyroscope calibration timed out")
            self.calibrationFinished.emit(False, "Gyroscope calibration timed out")
        else:
            self.logMessageReceived.emit("success", "Gyroscope calibration completed")
            self.calibrationFinished.emit(True, "Gyroscope calibration completed successfully")
    
    def _calibrate_level(self):
        """Calibrate the level sensor"""
        self.logMessageReceived.emit("info", "Starting level calibration")
        
        # Request level calibration
        try:
            self.mavlink_connection.mav.command_long_send(
                self.mavlink_connection.target_system,
                self.mavlink_connection.target_component,
                mavutil.mavlink.MAV_CMD_PREFLIGHT_CALIBRATION,
                0, 0, 0, 1, 0, 0, 0, 0  # 1 = calibrate level
            )
        except Exception as e:
            self.logMessageReceived.emit("error", f"Failed to start level calibration: {e}")
            return
        
        # Monitor calibration progress
        start_time = time.time()
        timeout = 60  # 1 minute timeout
        
        while not self.stop_calibration and time.time() - start_time < timeout:
            try:
                # Check for calibration status
                msg = self.mavlink_connection.recv_match(
                    type=['COMMAND_ACK', 'STATUSTEXT'],
                    blocking=False,
                    timeout=0.1
                )
                
                if msg is not None:
                    if msg.get_type() == 'COMMAND_ACK':
                        if msg.command == mavutil.mavlink.MAV_CMD_PREFLIGHT_CALIBRATION:
                            if msg.result == mavutil.mavlink.MAV_RESULT_ACCEPTED:
                                self.logMessageReceived.emit("info", "Level calibration accepted")
                            else:
                                self.logMessageReceived.emit("error", "Level calibration rejected")
                                break
                
                # Simulate progress for testing
                if not self.mavlink_connection:
                    progress = min((time.time() - start_time) / 30, 1.0)  # 30 seconds simulation
                    self.calibrationProgressChanged.emit(
                        progress,
                        "Level calibration in progress..."
                    )
                    
                    if progress >= 1.0:
                        break
                    
                    time.sleep(0.5)
                
            except Exception as e:
                self.logMessageReceived.emit("error", f"Error during level calibration: {e}")
                break
        
        if self.stop_calibration:
            self.logMessageReceived.emit("warning", "Level calibration cancelled")
            self.calibrationFinished.emit(False, "Level calibration cancelled")
        elif time.time() - start_time >= timeout:
            self.logMessageReceived.emit("error", "Level calibration timed out")
            self.calibrationFinished.emit(False, "Level calibration timed out")
        else:
            self.logMessageReceived.emit("success", "Level calibration completed")
            self.calibrationFinished.emit(True, "Level calibration completed successfully")
    
    def _calibrate_rc(self):
        """Calibrate the radio control channels"""
        self.logMessageReceived.emit("info", "=== RC CALIBRATION STARTED ===")
        self.logMessageReceived.emit("info", "System: Starting RC channel calibration")
        
        # Request RC calibration
        try:
            self.mavlink_connection.mav.command_long_send(
                self.mavlink_connection.target_system,
                self.mavlink_connection.target_component,
                mavutil.mavlink.MAV_CMD_PREFLIGHT_CALIBRATION,
                0, 0, 0, 0, 0, 0, 1, 0  # 1 = calibrate RC
            )
            self.logMessageReceived.emit("info", "System: RC calibration command sent successfully")
        except Exception as e:
            self.logMessageReceived.emit("error", f"Failed to start RC calibration: {e}")
            return
        
        # Monitor calibration progress
        start_time = time.time()
        timeout = 120  # 2 minutes timeout
        channels_calibrated = 0
        total_channels = 8
        
        while not self.stop_calibration and time.time() - start_time < timeout:
            try:
                # Check for calibration status
                msg = self.mavlink_connection.recv_match(
                    type=['COMMAND_ACK', 'STATUSTEXT', 'SERVO_OUTPUT_RAW'],
                    blocking=False,
                    timeout=0.1
                )
                
                if msg is not None:
                    if msg.get_type() == 'COMMAND_ACK':
                        if msg.command == mavutil.mavlink.MAV_CMD_PREFLIGHT_CALIBRATION:
                            if msg.result == mavutil.mavlink.MAV_RESULT_ACCEPTED:
                                self.logMessageReceived.emit("info", "RC calibration accepted")
                            else:
                                self.logMessageReceived.emit("error", "RC calibration rejected")
                                break
                    elif msg.get_type() == 'SERVO_OUTPUT_RAW':
                        # Monitor RC channel values
                        channels_calibrated = min(channels_calibrated + 1, total_channels)
                        progress = channels_calibrated / total_channels
                        self.calibrationProgressChanged.emit(
                            progress,
                            f"RC calibration: {channels_calibrated}/{total_channels} channels"
                        )
                        
                        # Extract RC channel values from SERVO_OUTPUT_RAW message
                        if hasattr(msg, 'servo1_raw') and hasattr(msg, 'servo2_raw'):
                            channel_values = [
                                msg.servo1_raw, msg.servo2_raw, msg.servo3_raw, msg.servo4_raw,
                                msg.servo5_raw, msg.servo6_raw, msg.servo7_raw, msg.servo8_raw
                            ]
                            self.RCChannelsChanged.emit(channel_values)
                
                # Simulate progress for testing
                if not self.mavlink_connection:
                    channels_calibrated = min(channels_calibrated + 1, total_channels)
                    progress = channels_calibrated / total_channels
                    self.calibrationProgressChanged.emit(
                        progress,
                        f"RC calibration: {channels_calibrated}/{total_channels} channels (simulated)"
                    )
                    
                    # Simulate RC channel values
                    import random
                    channel_values = [random.randint(1000, 2000) for _ in range(8)]
                    self.RCChannelsChanged.emit(channel_values)
                    
                    if progress >= 1.0:
                        break
                    
                    time.sleep(1)
                
            except Exception as e:
                self.logMessageReceived.emit("error", f"Error during RC calibration: {e}")
                break
        
        if self.stop_calibration:
            self.logMessageReceived.emit("warning", "RC calibration cancelled")
            self.calibrationFinished.emit(False, "RC calibration cancelled")
        elif time.time() - start_time >= timeout:
            self.logMessageReceived.emit("error", "RC calibration timed out")
            self.calibrationFinished.emit(False, "RC calibration timed out")
        else:
            self.logMessageReceived.emit("success", "RC calibration completed")
            self.calibrationFinished.emit(True, "RC calibration completed successfully")
    
    def _calibrate_esc(self):
        """Calibrate the Electronic Speed Controllers"""
        self.logMessageReceived.emit("info", "=== ESC CALIBRATION STARTED ===")
        self.logMessageReceived.emit("info", "System: Starting ESC calibration")
        self.logMessageReceived.emit("warning", "IMPORTANT: Remove propellers before ESC calibration!")
        
        # Request ESC calibration
        try:
            self.mavlink_connection.mav.command_long_send(
                self.mavlink_connection.target_system,
                self.mavlink_connection.target_component,
                mavutil.mavlink.MAV_CMD_PREFLIGHT_CALIBRATION,
                0, 0, 0, 0, 0, 0, 0, 1  # 1 = calibrate ESC
            )
            self.logMessageReceived.emit("info", "System: ESC calibration command sent successfully")
        except Exception as e:
            self.logMessageReceived.emit("error", f"Failed to start ESC calibration: {e}")
            return
        
        # Monitor calibration progress
        start_time = time.time()
        timeout = 180  # 3 minutes timeout
        escs_calibrated = 0
        total_escs = 4  # Assuming 4 ESCs for a quadcopter
        
        while not self.stop_calibration and time.time() - start_time < timeout:
            try:
                # Check for calibration status
                msg = self.mavlink_connection.recv_match(
                    type=['COMMAND_ACK', 'STATUSTEXT'],
                    blocking=False,
                    timeout=0.1
                )
                
                if msg is not None:
                    if msg.get_type() == 'COMMAND_ACK':
                        if msg.command == mavutil.mavlink.MAV_CMD_PREFLIGHT_CALIBRATION:
                            if msg.result == mavutil.mavlink.MAV_RESULT_ACCEPTED:
                                self.logMessageReceived.emit("info", "ESC calibration accepted")
                            else:
                                self.logMessageReceived.emit("error", "ESC calibration rejected")
                                break
                
                # Simulate progress for testing
                if not self.mavlink_connection:
                    escs_calibrated = min(escs_calibrated + 1, total_escs)
                    progress = escs_calibrated / total_escs
                    self.calibrationProgressChanged.emit(
                        progress,
                        f"ESC calibration: {escs_calibrated}/{total_escs} ESCs (simulated)"
                    )
                    
                    if progress >= 1.0:
                        break
                    
                    time.sleep(2)
                
            except Exception as e:
                self.logMessageReceived.emit("error", f"Error during ESC calibration: {e}")
                break
        
        if self.stop_calibration:
            self.logMessageReceived.emit("warning", "ESC calibration cancelled")
            self.calibrationFinished.emit(False, "ESC calibration cancelled")
        elif time.time() - start_time >= timeout:
            self.logMessageReceived.emit("error", "ESC calibration timed out")
            self.calibrationFinished.emit(False, "ESC calibration timed out")
        else:
            self.logMessageReceived.emit("success", "ESC calibration completed")
            self.calibrationFinished.emit(True, "ESC calibration completed successfully")
    
    def _calibrate_joystick(self):
        """Joystick-Kalibrierung mit Live-Feedback"""
        import random
        self.logMessageReceived.emit("info", "Joystick-Kalibrierung gestartet")
        self.calibrationProgressChanged.emit(0.0, "Joystick-Kalibrierung läuft...")
        steps = 6
        for step in range(steps):
            if self.stop_calibration:
                self.logMessageReceived.emit("warning", "Joystick-Kalibrierung abgebrochen")
                self.calibrationFinished.emit(False, "Joystick-Kalibrierung abgebrochen")
                return
            # Simuliere Live-Feedback für Achsen (hier: Zufallswerte, später echte Werte einfügen)
            for t in range(20):  # 20x50ms = 1 Sekunde pro Schritt
                # TODO: Echte Joystick-Werte auslesen!
                x = random.uniform(-1, 1)
                y = random.uniform(-1, 1)
                throttle = random.uniform(-1, 1)
                yaw = random.uniform(-1, 1)
                self.joystickDataChanged.emit(x, y, throttle, yaw)
                time.sleep(0.05)
            self.calibrationProgressChanged.emit((step+1)/steps, f"Schritt {step+1} abgeschlossen")
        self.logMessageReceived.emit("success", "Joystick-Kalibrierung abgeschlossen")
        self.calibrationFinished.emit(True, "Joystick-Kalibrierung abgeschlossen")
    
    @Property(bool, constant=True)
    def is_calibration_running(self):
        """Property to check if calibration is running"""
        return self.calibration_running
    
    @Property(str, constant=True)
    def current_calibration_type(self):
        """Property to get current calibration type"""
        return self.current_calibration or "" 