"""
Protocol Connection Manager for RZGCS

This module manages connections to different MAVLink protocols (v1 and v2)
and provides a unified interface for protocol switching.
"""

import logging
from typing import Dict, Any, Optional, Union
from enum import Enum
from PySide6.QtCore import QObject, Signal, Property, Slot, QTimer

# Import existing connection components
from .mavlink_v2_integration import MAVLinkV2Integration

logger = logging.getLogger(__name__)

class ProtocolType(Enum):
    """Supported protocol types"""
    MAVLINK_V1 = "MAVLink v1"
    MAVLINK_V2 = "MAVLink v2"

class ProtocolConnectionManager(QObject):
    """Manages connections to different MAVLink protocols"""
    
    # Signals
    connectionStatusChanged = Signal(bool, str)  # isConnected, statusText
    protocolChanged = Signal(str)  # protocol type
    errorOccurred = Signal(str)  # error message
    statusMessage = Signal(str, int)  # message, type (for message panel)
    
    def __init__(self, mavlink_v2_backend):
        super().__init__()
        self._current_protocol = ProtocolType.MAVLINK_V1
        self._is_connected = False
        self._connection_string = ""
        self._mavlink_v1_connector = None  # Will be set from external connector
        self._mavlink_v2_backend = mavlink_v2_backend  # Instanz von außen
        self._message_manager = None  # Will be set from external message manager
        
        # Connect MAVLink v2 signals
        self._mavlink_v2_backend.connectionStatusChanged.connect(self._on_v2_connection_status_changed)
        self._mavlink_v2_backend.errorOccurred.connect(self._on_v2_error)
        
        logger.info("ProtocolConnectionManager initialized")
    
    @Property(str, notify=protocolChanged)
    def currentProtocol(self):
        """Current protocol type"""
        return self._current_protocol.value
    
    @Property(bool, notify=connectionStatusChanged)
    def isConnected(self):
        """Connection status"""
        return self._is_connected
    
    @Property(str, notify=connectionStatusChanged)
    def connectionString(self):
        """Current connection string"""
        return self._connection_string
    
    @Slot(str)
    def setProtocol(self, protocol: str):
        """Set the protocol type"""
        try:
            if protocol == "MAVLink v1":
                self._current_protocol = ProtocolType.MAVLINK_V1
            elif protocol == "MAVLink v2":
                self._current_protocol = ProtocolType.MAVLINK_V2
            else:
                raise ValueError(f"Unsupported protocol: {protocol}")
            
            self.protocolChanged.emit(self._current_protocol.value)
            self._send_status_message(f"Protocol switched to {self._current_protocol.value}", 1)
            logger.info(f"Protocol changed to: {self._current_protocol.value}")
        except Exception as e:
            logger.error(f"Failed to set protocol: {e}")
            self.errorOccurred.emit(f"Failed to set protocol: {e}")
            self._send_status_message(f"Failed to set protocol: {e}", 3)
    
    @Slot(str)
    def setConnectionString(self, connection_string: str):
        """Set the connection string"""
        self._connection_string = connection_string
        self._send_status_message(f"Connection string set: {connection_string}", 1)
        logger.info(f"Connection string set to: {connection_string}")
    
    @Slot()
    def connect(self):
        """Connect using the current protocol"""
        if self._current_protocol == ProtocolType.MAVLINK_V2:
            # Wenn MAVLink1 verbunden ist, trennen
            if self._mavlink_v1_connector and self._mavlink_v1_connector.isConnected:
                self._mavlink_v1_connector.disconnect_from_drone()
            # MAVLink2 verbinden
            self._mavlink_v2_backend.set_connection_string(self._connection_string)
            return self._mavlink_v2_backend.connect_mavlink()
        elif self._current_protocol == ProtocolType.MAVLINK_V1:
            # Wenn MAVLink2 verbunden ist, trennen
            if self._mavlink_v2_backend and self._mavlink_v2_backend.is_connected:
                self._mavlink_v2_backend.disconnect_mavlink()
            # MAVLink1 verbinden
            return self._mavlink_v1_connector.connect_to_drone(self._connection_string, self._baudrate)
        else:
            return False
    
    @Slot()
    def disconnect(self):
        """Disconnect from current protocol"""
        try:
            if self._current_protocol == ProtocolType.MAVLINK_V1:
                return self._disconnect_v1()
            elif self._current_protocol == ProtocolType.MAVLINK_V2:
                return self._disconnect_v2()
            else:
                raise ValueError(f"Unsupported protocol: {self._current_protocol}")
        except Exception as e:
            logger.error(f"Disconnection failed: {e}")
            self.errorOccurred.emit(f"Disconnection failed: {e}")
            return False
    
    def _connect_v1(self) -> bool:
        """Connect using MAVLink v1"""
        if not self._mavlink_v1_connector:
            error_msg = "MAVLink v1 connector not available"
            logger.error(error_msg)
            self.errorOccurred.emit(error_msg)
            self._send_status_message(error_msg, 3)
            return False
        
        try:
            self._send_status_message(f"Connecting to {self._connection_string} using MAVLink v1...", 1)
            
            # Use the existing MAVLink v1 connector
            success = self._mavlink_v1_connector.connectWithPort(
                self._connection_string
            )
            
            if success:
                logger.info("MAVLink v1 connection successful")
                self._is_connected = True
                self.connectionStatusChanged.emit(True, "Connected (MAVLink v1)")
                self._send_status_message("MAVLink v1 connection established successfully", 4)
            else:
                logger.error("MAVLink v1 connection failed")
                self.errorOccurred.emit("MAVLink v1 connection failed")
                self._send_status_message("MAVLink v1 connection failed", 3)
            
            return success
        except Exception as e:
            logger.error(f"MAVLink v1 connection error: {e}")
            self.errorOccurred.emit(f"MAVLink v1 connection error: {e}")
            self._send_status_message(f"MAVLink v1 connection error: {e}", 3)
            return False
    
    def _connect_v2(self) -> bool:
        """Connect using MAVLink v2"""
        try:
            self._send_status_message(f"Connecting to {self._connection_string} using MAVLink v2...", 1)
            
            # Set connection string for MAVLink v2 backend
            self._mavlink_v2_backend.set_connection_string(self._connection_string)
            
            # Use the MAVLink v2 backend
            success = self._mavlink_v2_backend.connect_mavlink()
            
            if success:
                logger.info("MAVLink v2 connection successful")
                self._is_connected = True
                self.connectionStatusChanged.emit(True, "Connected (MAVLink v2)")
                self._send_status_message("MAVLink v2 connection established successfully", 4)
            else:
                logger.error("MAVLink v2 connection failed")
                self.errorOccurred.emit("MAVLink v2 connection failed")
                self._send_status_message("MAVLink v2 connection failed", 3)
            
            return success
        except Exception as e:
            logger.error(f"MAVLink v2 connection error: {e}")
            self.errorOccurred.emit(f"MAVLink v2 connection error: {e}")
            self._send_status_message(f"MAVLink v2 connection error: {e}", 3)
            return False
    
    def _disconnect_v1(self) -> bool:
        """Disconnect from MAVLink v1"""
        if not self._mavlink_v1_connector:
            return True  # Already disconnected
        
        try:
            self._send_status_message("Disconnecting from MAVLink v1...", 2)
            self._mavlink_v1_connector.disconnect()
            self._is_connected = False
            self.connectionStatusChanged.emit(False, "Disconnected (MAVLink v1)")
            self._send_status_message("MAVLink v1 disconnected", 2)
            logger.info("MAVLink v1 disconnected")
            return True
        except Exception as e:
            logger.error(f"MAVLink v1 disconnection error: {e}")
            self.errorOccurred.emit(f"MAVLink v1 disconnection error: {e}")
            self._send_status_message(f"MAVLink v1 disconnection error: {e}", 3)
            return False
    
    def _disconnect_v2(self) -> bool:
        """Disconnect from MAVLink v2"""
        try:
            self._send_status_message("Disconnecting from MAVLink v2...", 2)
            self._mavlink_v2_backend.disconnect_mavlink()
            self._is_connected = False
            self.connectionStatusChanged.emit(False, "Disconnected (MAVLink v2)")
            self._send_status_message("MAVLink v2 disconnected", 2)
            logger.info("MAVLink v2 disconnected")
            return True
        except Exception as e:
            logger.error(f"MAVLink v2 disconnection error: {e}")
            self.errorOccurred.emit(f"MAVLink v2 disconnection error: {e}")
            self._send_status_message(f"MAVLink v2 disconnection error: {e}", 3)
            return False
    
    def _on_v2_connection_status_changed(self, is_connected: bool, status_text: str):
        """Handle MAVLink v2 connection status changes"""
        self._is_connected = is_connected
        self.connectionStatusChanged.emit(is_connected, status_text)
        self._send_status_message(f"MAVLink v2 status: {status_text}", 1 if is_connected else 2)
        logger.info(f"MAVLink v2 status: {status_text}")
    
    def _on_v2_error(self, error_message: str):
        """Handle MAVLink v2 errors"""
        self.errorOccurred.emit(error_message)
        self._send_status_message(f"MAVLink v2 error: {error_message}", 3)
        logger.error(f"MAVLink v2 error: {error_message}")
    
    def _send_status_message(self, message: str, message_type: int):
        """Send status message to message panel"""
        if self._message_manager:
            self._message_manager.addMessage(message, message_type)
        self.statusMessage.emit(message, message_type)
    
    @Slot(object)
    def setMavlinkV1Connector(self, connector):
        """Set the MAVLink v1 connector (called from external code)"""
        self._mavlink_v1_connector = connector
        self._send_status_message("MAVLink v1 connector initialized", 1)
        logger.info("MAVLink v1 connector set")
    
    @Slot(object)
    def setMessageManager(self, message_manager):
        """Set the message manager for status reporting"""
        self._message_manager = message_manager
        self._send_status_message("Protocol connection manager ready", 1)
        logger.info("Message manager set for protocol connection manager")
    
    @Property(object, constant=True)
    def mavlinkV2Backend(self):
        """Get the MAVLink v2 backend for QML access"""
        return self._mavlink_v2_backend
    
    @Property(object, constant=True)
    def mavlinkV1Connector(self):
        """Get the MAVLink v1 connector for QML access"""
        return self._mavlink_v1_connector 