"""
Base class for drone connectors
"""

from abc import ABC, abstractmethod
from PySide6.QtCore import QObject, Signal

# Create a common metaclass that inherits from both QObject and ABC metaclasses
class DroneConnectorMeta(type(QObject), type(ABC)):
    pass

class DroneConnectorBase(QObject, ABC, metaclass=DroneConnectorMeta):
    """Base class for drone connectors"""
    
    # Common signals for all connector implementations
    log_received = Signal(str)  # Logging messages
    gps_msg = Signal(float, float)  # Latitude, Longitude
    attitude_msg = Signal(float, float, float)  # Roll, Pitch, Yaw
    sensor_data = Signal(str, float)  # Sensor name, value
    connection_status = Signal(bool)  # Connection status
    
    def __init__(self):
        """Initializes the base class"""
        super().__init__()
        self.running = False
        self.debug = False
        
    @abstractmethod
    async def connect_to_drone(self) -> bool:
        """
        Establishes connection to the drone.
        
        Returns:
            bool: True if connection was successful
        """
        pass
        
    @abstractmethod
    async def disconnect_from_drone(self) -> None:
        """Disconnects from the drone"""
        pass
        
    @abstractmethod
    async def start_monitoring(self) -> None:
        """Starts monitoring the drone data"""
        pass
        
    @abstractmethod
    def stop(self) -> None:
        """Stops the connection"""
        pass
        
    def _log_info(self, message: str) -> None:
        """Logs an info message"""
        if self.debug:
            print(f"[{self.__class__.__name__}] {message}")
        self.log_received.emit(message)
        
    def _log_error(self, message: str) -> None:
        """Logs an error message"""
        print(f"[{self.__class__.__name__}] ❌ {message}")
        self.log_received.emit(f"❌ {message}")
        
    def _update_connection_status(self, connected: bool) -> None:
        """Updates the connection status"""
        self.connection_status.emit(connected)
        if self.debug:
            status = "✅ Connected" if connected else "❌ Disconnected"
            self._log_info(status) 