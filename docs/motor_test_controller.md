# RZGCS Motor Test Controller Documentation

## Overview
The `MotorTestController` is a key component of the RZGCS system responsible for testing and diagnosing drone motors. It allows users to safely test individual motors, run sequential tests across all motors, or test all motors simultaneously with configurable throttle levels.

## Key Features

### Test Modes
- **Single Motor Test**: Test one motor at a time with manual selection
- **Sequential Test**: Automatically test each motor in sequence for diagnostics
- **All Motors Test**: Test all motors simultaneously for system verification

### Safety Features
- Controlled throttle limits (0-100%)
- Automatic test termination
- Safety checks before testing
- Emergency stop capability

### Real-time Feedback
- Motor status reporting
- RPM monitoring
- Test progress tracking
- Comprehensive logging

## Class: MotorTestController

### Signals

| Signal | Parameters | Description |
|--------|------------|-------------|
| `motorStatusChanged` | int, bool, str | Emitted when a motor's status changes (motor number, running state, status text) |
| `logMessageAdded` | str | Emitted when a new log message is generated |
| `testProgressChanged` | float, str | Emitted when test progress changes (progress percentage, status text) |
| `testFinished` | bool, str | Emitted when a test completes (success state, status text) |
| `motorRPMChanged` | int, int | Emitted when a motor's RPM changes (motor number, RPM value) |

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `_test_in_progress` | bool | Whether a test is currently running |
| `_test_mode` | str | Current test mode ("single", "sequence", or "all") |
| `_throttle` | float | Current throttle level (0-100%) |
| `_active_motors` | list | Status of each motor [motor1, motor2, motor3, motor4] |
| `_sequence_duration` | int | Duration in ms for each motor in sequence mode |

### Methods

#### `initialize(root_item)`
Initializes the controller and connects it to the QML root item.

Returns:
- `bool`: True if initialization was successful

#### `setTestMode(mode)`
Sets the test mode.

Parameters:
- `mode`: Test mode to set ("single", "sequence", or "all")

#### `setThrottle(throttle)`
Sets the motor throttle level.

Parameters:
- `throttle`: Throttle level (0-100%)

#### `testMotor(motor_number)`
Tests a specific motor in single test mode.

Parameters:
- `motor_number`: The motor to test (1-4)

#### `startTest()`
Starts the motor test according to the selected mode.

#### `stopTest()`
Stops all running motor tests.

#### `runSafetyCheck()`
Performs a safety check to ensure motors are operational.

#### `emergencyStop()`
Immediately stops all motors regardless of test state.

### Internal Methods

#### `_get_mode_description(mode)`
Gets a human-readable description of a test mode.

#### `_update_active_motors()`
Updates active motors based on current test mode and throttle.

#### `_sequence_step()`
Performs a step in the sequence test mode.

#### `_send_motor_command(motor_number, throttle)`
Sends a command to control a specific motor.

## Integration with MAVLink

The motor test controller sends MAVLink commands to control motors:

```python
def _send_motor_command(self, motor_number, throttle):
    """
    Sends a motor test command via MAVLink.
    
    Parameters:
        motor_number: Motor number (1-4)
        throttle: Throttle level (0-100%)
    """
    # Convert throttle from percentage to MAVLink-compatible value (usually 0-1000)
    mavlink_throttle = int(throttle * 10)
    
    # Log the command
    self.logMessageAdded.emit(f"Sending command to motor {motor_number}: {throttle:.0f}%")
    
    # In a real implementation, this would send the MAVLink command to the drone
    # Example:
    # mavlink_connection.mav.command_long_send(
    #     target_system, target_component,
    #     mavutil.mavlink.MAV_CMD_DO_MOTOR_TEST,
    #     0,  # Confirmation
    #     motor_number - 1,  # Motor instance (0-based in MAVLink)
    #     mavutil.mavlink.MOTOR_TEST_THROTTLE_PERCENT,  # Throttle type
    #     mavlink_throttle,  # Throttle value
    #     10,  # Test duration in seconds
    #     1,  # Number of motors to test
    #     0,  # Motor test order
    #     0)  # Empty
```

## Integration with QML

The controller is designed to be used from QML interfaces:

```qml
import RZGCS 1.0

Page {
    id: motorTestPage
    
    MotorTestController {
        id: motorTestController
        
        onMotorStatusChanged: function(motorNum, isRunning, statusText) {
            // Update motor display
            motorStatusText.text = statusText
            motorIndicators[motorNum-1].active = isRunning
        }
        
        onLogMessageAdded: function(message) {
            // Add to log display
            logView.append(message)
        }
        
        onTestProgressChanged: function(progress, status) {
            // Update progress bar
            testProgressBar.value = progress
            testStatusText.text = status
        }
    }
    
    Component.onCompleted: {
        motorTestController.initialize(motorTestPage)
    }
    
    // UI elements and controls
    Button {
        text: "Start Test"
        onClicked: motorTestController.startTest()
    }
    
    Button {
        text: "Stop Test"
        onClicked: motorTestController.stopTest()
    }
    
    Slider {
        from: 0
        to: 100
        value: 30
        onValueChanged: motorTestController.setThrottle(value)
    }
}
```

## Test Workflow

### Single Motor Test
1. Set mode to "single" using `setTestMode("single")`
2. Set desired throttle with `setThrottle(value)`
3. Start the test with `startTest()`
4. Click on individual motors to test them with `testMotor(number)`
5. Stop the test with `stopTest()`

### Sequence Test
1. Set mode to "sequence" using `setTestMode("sequence")`
2. Set desired throttle with `setThrottle(value)`
3. Start the test with `startTest()`
4. The controller automatically cycles through all motors
5. Test stops automatically after one cycle or can be stopped with `stopTest()`

### All Motors Test
1. Set mode to "all" using `setTestMode("all")`
2. Set desired throttle with `setThrottle(value)`
3. Start the test with `startTest()`
4. All motors activate simultaneously
5. Stop the test with `stopTest()`

## Safety Considerations

1. **Pre-flight Safety**: Always use motor tests with propellers removed when possible
2. **Throttle Limits**: Keep throttle levels low during initial testing
3. **Visual Confirmation**: Verify motor rotation direction during tests
4. **Emergency Stop**: Have the emergency stop button accessible during tests
5. **Physical Security**: Secure the drone properly before testing motors
