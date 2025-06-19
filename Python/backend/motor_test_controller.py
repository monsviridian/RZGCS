from PySide6.QtCore import QObject, Signal, Property, Slot, QTimer
from typing import Optional
from PySide6.QtQml import QmlElement

QML_IMPORT_NAME = "RZGCS"
QML_IMPORT_MAJOR_VERSION = 1

@QmlElement
class MotorTestController(QObject):
    """
    Controller for the motor test view.
    This class provides functions for testing the motors.
    """
    
    # Signals
    motorStatusChanged = Signal(int, bool, str)  # Motor number, Running?, Status text
    logMessageAdded = Signal(str)  # Log message
    testProgressChanged = Signal(float, str)  # Progress, Status
    testFinished = Signal(bool, str)  # Successful?, Status text
    motorRPMChanged = Signal(int, int)  # Motor number, RPM
    
    def __init__(self, parent=None, logger=None):
        super().__init__(parent)
        
        self._logger = logger
        self._test_mode = "single"  # single, sequence, all
        self._throttle = 20.0  # Default 20%
        self._test_in_progress = False
        self._active_motors = [False, False, False, False]  # Motor 1-4 active?
        self._sequence_duration = 2000  # 2 seconds per motor
        self._current_sequence_motor = 0
        self._message_handler = None
        
        # Timer für die Sequenzsteuerung
        self._sequence_timer = QTimer(self)
        self._sequence_timer.timeout.connect(self._sequence_step)
        self._current_sequence_motor = 0
        self._sequence_duration = 1000  # ms per motor in the sequence
        
        if self._logger:
            self._logger.addLog("[INFO] MotorTestController initialisiert")
    
    @Slot()
    def initialize(self, root_item):
        """
        Initializes the controller and connects it to the QML root item.
        """
        print("Initializing MotorTestController")
        self.logMessageAdded.emit("Motor test controller initialized")
        if self._logger:
            self._logger.addLog("[INFO] MotorTestController initialisiert")
        return True
    
    @Slot(str)
    def setTestMode(self, mode):
        """
        Sets the test mode.
        mode: "single", "sequence" or "all"
        """
        if mode in ["single", "sequence", "all"]:
            self._test_mode = mode
            print(f"Test mode set to {mode}")
            self.logMessageAdded.emit(f"Test mode: {self._get_mode_description(mode)}")
            if self._logger:
                self._logger.addLog(f"[INFO] Testmodus: {mode}")
    
    def _get_mode_description(self, mode):
        if mode == "single":
            return "Single test (select one motor manually)"
        elif mode == "sequence":
            return "Sequence test (test motors one after another)"
        elif mode == "all":
            return "Test all motors simultaneously"
        return "Unknown mode"
    
    @Slot(float)
    def setThrottle(self, throttle):
        """
        Sets the motor power (0-100%).
        """
        self._throttle = max(0, min(100, throttle))
        # If we are in test mode, update the running motors
        if self._test_in_progress:
            self._update_active_motors()
            if self._logger:
                self._logger.addLog(f"[INFO] Drehzahl: {throttle}%")
            
    def _update_active_motors(self):
        """
        Updates the active motors based on the current test mode and throttle.
        """
        for i in range(4):
            if self._active_motors[i]:
                self._send_motor_command(i+1, self._throttle)
                self.motorRPMChanged.emit(i+1, int(self._throttle * 50))  # Simulierte RPM-Werte
    
    @Slot(int)
    def testMotor(self, motor_number):
        """
        Tests a specific motor (1-4).
        Only effective in single test mode.
        """
        if not self._test_in_progress:
            self.logMessageAdded.emit("Please start the test first with the 'Start Test' button")
            if self._logger:
                self._logger.addLog("[WARN] Motortest nicht gestartet")
            return
            
        if self._test_mode != "single":
            self.logMessageAdded.emit("Motor selection is only available in single test mode")
            if self._logger:
                self._logger.addLog("[WARN] Motorauswahl nur im Einzeltestmodus möglich")
            return
            
        # Motor index (0-3)
        idx = motor_number - 1
        if 0 <= idx < 4:
            # Toggle the motor status
            self._active_motors = [False, False, False, False]  # Reset all
            self._active_motors[idx] = True
            self._send_motor_command(motor_number, self._throttle)
            self.motorStatusChanged.emit(
                motor_number, True, f"Motor {motor_number} active with {self._throttle:.0f}% power")
            self.logMessageAdded.emit(f"Testing motor {motor_number} with {self._throttle:.0f}% power")
            self.motorRPMChanged.emit(motor_number, int(self._throttle * 50))  # Simulierter RPM-Wert
            if self._logger:
                self._logger.addLog(f"[INFO] Motor {motor_number} getestet mit {self._throttle:.0f}% Leistung")
    
    @Slot()
    def startTest(self):
        """
        Starts the motor test according to the selected mode.
        """
        if self._test_in_progress:
            self.stopTest()
            
        self._test_in_progress = True
        self.testProgressChanged.emit(0.0, "Test started")
        self.logMessageAdded.emit(f"Starting motor test in mode: {self._get_mode_description(self._test_mode)}")
        if self._logger:
            self._logger.addLog(f"[INFO] Motortest gestartet im Modus: {self._test_mode}")
        
        if self._test_mode == "sequence":
            # Start the sequence test
            self._current_sequence_motor = 0
            self._sequence_timer.start(self._sequence_duration)
            self._sequence_step()  # Execute the first step immediately
        elif self._test_mode == "all":
            # Activate all motors
            self._active_motors = [True, True, True, True]
            for i in range(4):
                self._send_motor_command(i+1, self._throttle)
                self.motorStatusChanged.emit(i+1, True, f"Motor {i+1} active")
                self.motorRPMChanged.emit(i+1, int(self._throttle * 50))  # Simulated RPM value
        else:  # "single" mode
            self.logMessageAdded.emit("Please select a motor by clicking on it")
            # First deactivate all motors
            self._active_motors = [False, False, False, False]
            for i in range(4):
                self._send_motor_command(i+1, 0)
                self.motorStatusChanged.emit(i+1, False, f"Motor {i+1} inactive")
                self.motorRPMChanged.emit(i+1, 0)
    
    def _sequence_step(self):
        """
        Executes a step in the sequence test.
        """
        if not self._test_in_progress or self._test_mode != "sequence":
            self._sequence_timer.stop()
            return
            
        # Deactivate all motors
        self._active_motors = [False, False, False, False]
        
        # Activate current motor
        self._active_motors[self._current_sequence_motor] = True
        motor_number = self._current_sequence_motor + 1
        
        # Send command
        self._send_motor_command(motor_number, self._throttle)
        self.motorStatusChanged.emit(
            motor_number, True, f"Motor {motor_number} active with {self._throttle:.0f}% power")
        self.logMessageAdded.emit(f"Testing motor {motor_number} with {self._throttle:.0f}% power")
        self.motorRPMChanged.emit(motor_number, int(self._throttle * 50))  # Simulated RPM value
        
        # Update progress (0-100%)
        progress = (self._current_sequence_motor / 4.0) * 100.0
        self.testProgressChanged.emit(progress, f"Testing motor {motor_number}")
        if self._logger:
            self._logger.addLog(f"[INFO] Motortest: {progress:.0f}%")
        
        # Move to next motor
        self._current_sequence_motor = (self._current_sequence_motor + 1) % 4
        
        # If we've reached the first motor again, stop after one round
        if self._current_sequence_motor == 0:
            self._sequence_timer.stop()
            self.stopTest()
    
    @Slot()
    def stopTest(self):
        """
        Stops all running motor tests.
        """
        self._test_in_progress = False
        self._sequence_timer.stop()
        
        # Stop all motors
        self._active_motors = [False, False, False, False]
        for i in range(4):
            self._send_motor_command(i+1, 0)
            self.motorStatusChanged.emit(i+1, False, f"Motor {i+1} stopped")
            self.motorRPMChanged.emit(i+1, 0)
            
        self.testFinished.emit(True, "Test finished")
        self.logMessageAdded.emit("Motor test stopped")
        if self._logger:
            self._logger.addLog("[INFO] Motortest gestoppt")
        
    @Slot(bool)
    def set_connected(self, connected=True):
        """Called when connection status changes"""
        if not connected and self._test_in_progress:
            # Stop any ongoing tests when connection is lost
            self.stopTest()
            if self._logger:
                self._logger.addLog("[WARN] Verbindung getrennt: Motorentest abgebrochen")
        
        self._connected = connected
        
        if self._logger:
            status = "verbunden" if connected else "getrennt"
            self._logger.addLog(f"[INFO] MotorTestController Status: {status}")
    
    def set_message_handler(self, message_handler):
        """Setzt den Message Handler für MAVLink-Kommunikation."""
        self._message_handler = message_handler
        
        if self._logger:
            self._logger.addLog("[INFO] MessageHandler im MotorTestController registriert")
    
    @Slot()
    def runSafetyCheck(self):
        """
        Performs a safety check to ensure that the motors are functioning properly.
        """
        self.logMessageAdded.emit("Performing safety check...")
        
        # In a real implementation, you would check the
        # motors and ESCs for correct connection and function
        
        # In this demo implementation, we only output status updates
        QTimer.singleShot(500, lambda: self.logMessageAdded.emit("Checking ESC connections..."))
        QTimer.singleShot(1000, lambda: self.logMessageAdded.emit("Checking motor connections..."))
        QTimer.singleShot(1500, lambda: self.logMessageAdded.emit("Testing motor response..."))
        QTimer.singleShot(2000, lambda: self.logMessageAdded.emit("Calibrating ESCs..."))
        QTimer.singleShot(2500, lambda: self.logMessageAdded.emit("Safety check completed. All motors are operational."))
    
    def _send_motor_command(self, motor_number, throttle):
        """
        Sendet einen Motorbefehl an die Hardware über MAVLink.
        
        Args:
            motor_number: Motornummer (1-4)
            throttle: Drehzahl in Prozent (0-100)
        """
        print(f"Sending motor command: Motor {motor_number}, Throttle: {throttle:.1f}%")
        
        # MAVLink Befehl senden, wenn ein Message Handler verfügbar ist
        if hasattr(self, '_message_handler') and self._message_handler is not None:
            try:
                # MAVLink command: COMMAND_LONG with MAV_CMD_DO_MOTOR_TEST
                # param1: Motor Nummer (1-basierend)
                # param2: Motor-Throttle-Typ (0=Prozent, 1=PWM, 2=RPM)
                # param3: Throttle (0-100%)
                # param4: Timeout (Sekunden)
                # param5: Motor Count (wie viele Motoren hat die Drohne)
                # param6: Motor Test Order (normal=0, aligned=1)
                # param7: unused
                self._message_handler.send_command_long(
                    mavlink_command=209,  # MAV_CMD_DO_MOTOR_TEST
                    param1=motor_number,   # Motor-Nummer
                    param2=0,              # Throttle-Typ: Prozent
                    param3=throttle,       # Throttle-Wert (0-100%)
                    param4=5.0,            # Timeout: 5 Sekunden
                    param5=4,              # Motor Count: Quadcopter hat 4 Motoren
                    param6=0               # Motor Test Order: normal
                )
                self.logMessageAdded.emit(f"MAVLink Befehl für Motor {motor_number} gesendet: {throttle:.1f}%")
            except Exception as e:
                self.logMessageAdded.emit(f"Fehler beim Senden des MAVLink Befehls: {str(e)}")
        else:
            self.logMessageAdded.emit("Kein Message Handler verfügbar, Motor-Test nur simuliert")
            # Im Debug-Modus simulieren wir die Befehle trotzdem
