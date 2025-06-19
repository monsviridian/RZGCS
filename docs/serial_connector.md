# RZGCS Serial Connector Documentation

## Overview
The `SerialConnector` class is a critical component of the RZGCS system that manages communication between the ground station and drones or simulators. It handles serial port discovery, connection establishment, MAVLink protocol communication, and serves as the central hub for data flow between the drone and various application components.

## Key Features

### Connection Management
- Auto-discovery of available serial ports
- Configurable baud rates and connection parameters
- Support for both real drone connections and simulated connections
- Error handling and connection status reporting

### Data Flow Coordination
- Connects MAVLink messages to the UI components
- Routes sensor data to the appropriate view models
- Manages parameter discovery and updates
- Coordinates message filtering and processing

### Simulation Support
- Seamless switching between real and simulated connections
- Multiple simulator backend options
- Custom sensor data simulation

## Class: SerialConnector

### Signals

| Signal | Parameters | Description |
|--------|------------|-------------|
| `availablePortsChanged` | list | Emitted when the list of available serial ports changes |
| `connection_successful` | None | Emitted when a connection is successfully established |
| `gps_msg` | float, float | Emitted when GPS data is received (latitude, longitude) |
| `attitude_msg` | float, float, float | Emitted when attitude data is received (roll, pitch, yaw) |
| `connectedChanged` | bool | Emitted when connection status changes |
| `portChanged` | str | Emitted when the selected port changes |
| `baudRateChanged` | int | Emitted when the baud rate changes |
| `errorOccurred` | str | Emitted when a connection error occurs |
| `availableBaudRatesChanged` | list | Emitted when the list of available baud rates changes |
| `attitudeChanged` | float, float, float | Emitted when attitude data updates (roll, pitch, yaw) |
| `gpsChanged` | float, float, float | Emitted when GPS data updates (lat, lon, alt) |

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `connected` | bool | Whether a connection is currently established |
| `port` | str | The currently selected serial port |
| `baudRate` | int | The currently selected baud rate |
| `availablePorts` | list | List of available serial ports |
| `availableBaudRates` | list | List of available baud rates |

### Methods

#### `__init__(sensor_model, logger, parameter_model)`
Initializes the serial connector with the necessary models.

Parameters:
- `sensor_model`: Instance of SensorViewModel for data updates
- `logger`: Instance of Logger for recording events
- `parameter_model`: Instance of ParameterTableModel for parameter management

#### `connect_to_serial(port_name, baud_rate, use_simulator=False)`
Establishes a connection to a serial port or simulator.

Parameters:
- `port_name`: Name of the serial port to connect to
- `baud_rate`: Baud rate for the connection
- `use_simulator`: Whether to use the simulator instead of a real connection

Returns:
- `bool`: True if connection was successful, False otherwise

#### `disconnect()`
Disconnects from the current connection.

#### `refresh_ports()`
Refreshes the list of available serial ports.

#### `send_command(command_id, param1=0, param2=0, param3=0, param4=0, param5=0, param6=0, param7=0)`
Sends a MAVLink command to the connected drone.

Parameters:
- `command_id`: MAVLink command ID
- `param1`-`param7`: Command parameters

Returns:
- `bool`: True if command was sent successfully, False otherwise

#### `start_simulator(simulator_type="compatible")`
Starts a simulator of the specified type.

Parameters:
- `simulator_type`: Type of simulator to start ("compatible", "direct", or "mavlink")

Returns:
- `bool`: True if simulator was started successfully, False otherwise

## Connection Flow

The typical flow for establishing a connection:

1. **Discovery**: `refresh_ports()` to find available serial ports
2. **Selection**: UI selects port and baud rate
3. **Connection**: `connect_to_serial()` is called
4. **Initialization**:
   - Creates MAVLinkConnector
   - Initializes MessageHandler
   - Sets up parameter discovery
5. **Success**: `connection_successful` signal is emitted

## Simulator Options

### Compatible Simulator
Simulates a MAVLink-compatible device with realistic behavior.

```python
self._simulator = CompatibleSensorSimulator(self._logger)
```

### Direct Sensor Simulator
Directly updates sensor data without using MAVLink protocol.

```python
self._simulator = DirectSensorSimulator(self._sensor_model, self._logger)
```

### MAVLink Simulator
Full MAVLink protocol simulation with message passing.

```python
from backend.mavlink_simulator import MAVLinkSimulator
self._simulator = MAVLinkSimulator(self._logger)
```

## Error Handling

The connector implements robust error handling:

```python
try:
    # Connection attempt
except Exception as e:
    error_msg = f"❌ Connection error: {str(e)}"
    self._logger.addLog(error_msg)
    self.errorOccurred.emit(error_msg)
    return False
```

This ensures that connection failures are properly reported to the UI.

## Integration with MAVLink

SerialConnector acts as a bridge between the MAVLink protocol and the application:

```python
# Create MAVLink connection
mav_connection = mavutil.mavlink_connection(
    device, 
    baud=baud_rate,
    autoreconnect=True,
    source_system=255,
    source_component=0
)

# Create connector
self._mavlink_connector = MAVLinkConnector(
    mav_connection,
    self._logger
)

# Initialize message handler
self._message_handler.set_connection(
    self._mavlink_connector.get_connection()
)
```

## Integration with QML

The SerialConnector is designed to be exposed to QML:

```qml
// In QML file
Button {
    text: "Connect"
    onClicked: {
        serialConnector.connect_to_serial(
            portComboBox.currentText,
            parseInt(baudRateComboBox.currentText),
            useSimulatorCheckBox.checked
        )
    }
}

Text {
    text: serialConnector.connected ? "Connected" : "Disconnected"
    color: serialConnector.connected ? "green" : "red"
}
```

## Best Practices

1. **Port Management**
   Always refresh ports before attempting connections to ensure the latest list.

2. **Error Recovery**
   Implement retry logic for important connections:
   ```python
   retry_count = 0
   max_retries = 3
   
   while retry_count < max_retries:
       if self.connect_to_serial(port, baud):
           return True
       retry_count += 1
       time.sleep(1)  # Wait before retry
   ```

3. **Simulator Testing**
   Use the simulator option to test application behavior without an actual drone:
   ```python
   # To test with simulated data
   serial_connector.connect_to_serial("SIM", 57600, use_simulator=True)
   ```

4. **Command Safety**
   Always validate parameters before sending commands:
   ```python
   # Example of safe command sending
   def arm_motors(self, arm=True):
       if self.connected:
           param1 = 1.0 if arm else 0.0
           return self.send_command(
               mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
               param1
           )
       return False
   ```
