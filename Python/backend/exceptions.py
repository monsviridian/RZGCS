from typing import Optional

class DroneException(Exception):
    """Base exception for all drone-related errors"""
    def __init__(self, message: str, error_code: Optional[int] = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class ConnectionException(DroneException):
    """Exception for connection errors"""
    pass

class SensorException(DroneException):
    """Exception for sensor errors"""
    pass

class MotorException(DroneException):
    """Exception for motor errors"""
    pass

class CalibrationException(DroneException):
    """Exception for calibration errors"""
    pass

class ConnectionTimeoutError(Exception):
    """Raised when a connection attempt times out."""
    pass

class ConnectionError(Exception):
    """Raised when a connection attempt fails."""
    pass 