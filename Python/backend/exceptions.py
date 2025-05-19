from typing import Optional

class DroneException(Exception):
    """Basis-Exception für alle drohnenbezogenen Fehler"""
    def __init__(self, message: str, error_code: Optional[int] = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class ConnectionException(DroneException):
    """Exception für Verbindungsfehler"""
    pass

class SensorException(DroneException):
    """Exception für Sensorfehler"""
    pass

class MotorException(DroneException):
    """Exception für Motorfehler"""
    pass

class CalibrationException(DroneException):
    """Exception für Kalibrierungsfehler"""
    pass

class ConnectionTimeoutError(Exception):
    """Raised when a connection attempt times out."""
    pass

class ConnectionError(Exception):
    """Raised when a connection attempt fails."""
    pass 