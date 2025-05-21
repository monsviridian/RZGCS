# RZGCS Exception System Documentation

## Overview
The exception system in RZGCS provides a structured way to handle and report errors that occur during application execution. It creates a hierarchy of exception types that allow for precise error handling based on the nature of the error.

## Base Exception Class

### `DroneException`

The foundation of the exception hierarchy is the `DroneException` class, which extends Python's built-in `Exception` class.

```python
class DroneException(Exception):
    """Base exception for all drone-related errors"""
    def __init__(self, message: str, error_code: Optional[int] = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)
```

#### Parameters:
- `message`: A descriptive string explaining the error
- `error_code`: An optional integer code that can be used for more precise error handling

## Specialized Exception Types

RZGCS defines several specialized exception types that extend `DroneException`:

### `ConnectionException`
Used for errors related to establishing or maintaining connections with the drone or other devices.

```python
class ConnectionException(DroneException):
    """Exception for connection errors"""
    pass
```

### `SensorException`
Raised when there are issues with sensor data acquisition or processing.

```python
class SensorException(DroneException):
    """Exception for sensor errors"""
    pass
```

### `MotorException`
Used for errors related to motor control or testing.

```python
class MotorException(DroneException):
    """Exception for motor errors"""
    pass
```

### `CalibrationException`
Raised during calibration procedures when issues are encountered.

```python
class CalibrationException(DroneException):
    """Exception for calibration errors"""
    pass
```

## Connection-Specific Exceptions

In addition to the drone-specific exceptions, RZGCS defines two more specialized connection-related exceptions:

### `ConnectionTimeoutError`
Raised specifically when a connection attempt times out.

```python
class ConnectionTimeoutError(Exception):
    """Raised when a connection attempt times out."""
    pass
```

### `ConnectionError`
Used for general connection failures that don't fall into the timeout category.

```python
class ConnectionError(Exception):
    """Raised when a connection attempt fails."""
    pass
```

## Best Practices for Exception Handling

1. **Catch Specific Exceptions First**
   Always catch the most specific exception types before catching more general ones:

   ```python
   try:
       # Connection code
   except ConnectionTimeoutError:
       # Handle timeout specifically
   except ConnectionException:
       # Handle other connection errors
   except DroneException:
       # Handle any other drone-related error
   except Exception:
       # Last resort for any other exception
   ```

2. **Include Contextual Information**
   When raising exceptions, include detailed information about the context:

   ```python
   raise ConnectionException(
       f"Failed to connect to port {port} with baud rate {baud_rate}",
       error_code=101
   )
   ```

3. **Log All Exceptions**
   Ensure all exceptions are logged for later analysis:

   ```python
   try:
       # Operation that might fail
   except DroneException as e:
       logger.addLog(f"Error: {e.message}, Code: {e.error_code}")
       # Re-raise or handle as appropriate
   ```

## Integration with UI

The exception system is designed to work with the RZGCS user interface through:

1. Signal emission from controllers when exceptions occur
2. Error dialogs or notifications in the QML interface
3. Log entries that record exception details

## Extending the Exception System

To add new exception types to the system:

1. Determine if the new exception fits within the existing hierarchy
2. Create a new class that extends the appropriate parent exception
3. Add docstrings to describe the specific error condition
4. Update error handling code to catch and handle the new exception type

Example:
```python
class NavigationException(DroneException):
    """Exception for navigation and waypoint-related errors"""
    pass
```
