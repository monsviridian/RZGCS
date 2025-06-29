"""
MAVLink Protocol Implementation
Based on QGroundControl's MAVLinkProtocol
"""

import time
from typing import Optional, Dict, Any
from pymavlink import mavutil
from pymavlink.dialects.v20 import ardupilotmega as mavlink
from PySide6.QtCore import QObject, Signal, QTimer
from dronekit import connect

class MAVLinkProtocol(QObject):
    """
    Handles low-level MAVLink communication.
    Similar to QGroundControl's MAVLinkProtocol implementation.
    """
    
    # Signals
    message_received = Signal(object)  # Emitted when a MAVLink message is received
    connection_status_changed = Signal(bool)  # True if connected
    protocol_status_changed = Signal(str)  # Status message
    error_occurred = Signal(str)  # Error message
    
    # Constants
    HEARTBEAT_TIMEOUT = 5.0  # Seconds until connection is considered dead
    MAX_RECONNECT_ATTEMPTS = 3
    RECONNECT_DELAY = 1.0
    
    def __init__(self):
        super().__init__()
        self.connection = None
        self._system_id = None
        self._component_id = None
        self._last_heartbeat = 0
        self._reconnect_attempts = 0
        self._connection_state = "disconnected"
        self._heartbeat_timer = QTimer()
        self._heartbeat_timer.timeout.connect(self._check_heartbeat)
        self._heartbeat_timer.start(1000)  # Check every second
        self.debug = False
        
    def _log_info(self, message: str) -> None:
        """Logs an info message"""
        if self.debug:
            print(f"[MAVLinkProtocol] {message}")
        self.protocol_status_changed.emit(message)
        
    def _log_error(self, message: str) -> None:
        """Logs an error message"""
        print(f"[MAVLinkProtocol] ❌ {message}")
        self.error_occurred.emit(message)
        
    def _update_connection_state(self, new_state: str) -> None:
        """Updates the connection state"""
        if self._connection_state != new_state:
            self._connection_state = new_state
            self.connection_status_changed.emit(new_state == "connected")
            if self.debug:
                self._log_info(f"🔄 Connection state: {new_state}")
                
    def _check_heartbeat(self) -> None:
        """Checks if we're still receiving heartbeats"""
        if self._connection_state == "connected":
            if time.time() - self._last_heartbeat > self.HEARTBEAT_TIMEOUT:
                self._log_error("No heartbeat received")
                self._update_connection_state("error")
                self._try_reconnect()
                
    def _try_reconnect(self) -> None:
        """Attempts to reconnect"""
        if self._reconnect_attempts < self.MAX_RECONNECT_ATTEMPTS:
            self._reconnect_attempts += 1
            self._log_info(f"Reconnection attempt {self._reconnect_attempts}/{self.MAX_RECONNECT_ATTEMPTS}")
            self._update_connection_state("connecting")
            # Reconnection will be handled by the connector
        else:
            self._log_error("Maximum reconnection attempts reached")
            self._update_connection_state("error")
            
    def connect_to_port(self, port: str, baudrate: int) -> bool:
        """
        Stellt eine Verbindung zum seriellen Port her.
        
        Args:
            port: Serieller Port (z.B. COM3, /dev/ttyACM0)
            baudrate: Baudrate (z.B. 57600, 115200)
            
        Returns:
            bool: True wenn die Verbindung erfolgreich war
        """
        try:
            self._update_connection_state("connecting")
            # Use DroneKit connect for serial
            vehicle = connect(port, wait_ready=True, baud=baudrate)
            self.vehicle = vehicle
            self._log_info("Connected!")
            self._update_connection_state("connected")
            return True
        except Exception as e:
            self._log_error(f"Connection error: {e}")
            self._update_connection_state("error")
            return False
            
    def send_message(self, message: mavlink.MAVLink_message) -> bool:
        """
        Sendet eine MAVLink-Nachricht.
        
        Args:
            message: MAVLink-Nachricht zum Senden
            
        Returns:
            bool: True wenn die Nachricht erfolgreich gesendet wurde
        """
        if not self.connection or self._connection_state != "connected":
            self._log_error("Keine aktive Verbindung")
            return False
            
        try:
            self.connection.mav.send(message)
            return True
        except Exception as e:
            self._log_error(f"Fehler beim Senden der Nachricht: {str(e)}")
            return False
            
    def receive_message(self) -> Optional[mavlink.MAVLink_message]:
        """
        Empfängt eine MAVLink-Nachricht.
        
        Returns:
            Optional[mavlink.MAVLink_message]: Empfangene Nachricht oder None
        """
        if not self.connection:
            return None
            
        try:
            msg = self.connection.recv_match(blocking=False)
            if msg:
                if msg.get_type() == 'HEARTBEAT':
                    self._last_heartbeat = time.time()
                self.message_received.emit(msg)
            return msg
        except Exception as e:
            self._log_error(f"Fehler beim Empfangen der Nachricht: {str(e)}")
            return None
            
    def request_data_stream(self, stream_id: int, rate: int) -> bool:
        """
        Requests a data stream from the vehicle.
        
        Args:
            stream_id: MAVLink stream ID
            rate: Requested rate in Hz
            
        Returns:
            bool: True if request was sent successfully
        """
        if not self.connection or not self._system_id or not self._component_id:
            return False
            
        try:
            self.connection.mav.request_data_stream_send(
                self._system_id,
                self._component_id,
                stream_id,
                rate,
                1  # Start
            )
            return True
        except Exception as e:
            self._log_error(f"Error requesting data stream: {str(e)}")
            return False
            
    def close(self) -> None:
        """Closes the connection"""
        try:
            if self.connection:
                self.connection.close()
            self._heartbeat_timer.stop()
            self._update_connection_state("disconnected")
            self._log_info("Connection closed")
        except Exception as e:
            self._log_error(f"Error closing connection: {str(e)}")
        finally:
            self.connection = None
            self._system_id = None
            self._component_id = None 