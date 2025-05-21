# RZGCS Message Handler Documentation

## Overview
The `MessageHandler` class is a core component of the RZGCS system responsible for processing, filtering, and distributing MAVLink messages between the drone (or simulator) and the application components. It implements a sophisticated message filtering system to reduce log spamming and ensure efficient communication.

## Key Features

### MAVLink Message Processing
- Handles all incoming MAVLink messages from connected drones or simulators
- Distributes messages to appropriate components via Qt signals
- Provides debugging output for message values
- Supports both real drone data and simulated data

### Advanced Message Filtering System
The `MessageHandler` implements a comprehensive filtering strategy that:

1. **Caches Message Values**: Keeps track of the most recent values for each message type
2. **Threshold-Based Filtering**: Only propagates messages when values change significantly
3. **Time-Based Filtering**: Enforces minimum intervals between logging the same message type
4. **Priority-Based Handling**: Ensures critical messages (like status texts) are always processed

This filtering system dramatically reduces log spamming when connected to a real flight controller while ensuring that important information is never missed.

## Class: MessageHandler

### Signals

| Signal | Parameters | Description |
|--------|------------|-------------|
| `heartbeat_received` | object | Emitted when a HEARTBEAT message is received |
| `attitude_received` | object | Emitted when an ATTITUDE message is received |
| `gps_received` | object | Emitted when a GLOBAL_POSITION_INT message is received |
| `battery_received` | object | Emitted when a SYS_STATUS message with battery info is received |
| `status_text_received` | object | Emitted when a STATUSTEXT message is received |
| `parameter_received` | object | Emitted when a PARAM_VALUE message is received |
| `vfr_hud_received` | object | Emitted when a VFR_HUD message is received |
| `error_occurred` | str | Emitted when an error occurs during message handling |

### Methods

#### `__init__(logger: Logger)`
Initializes the message handler with a logger instance.

#### `set_connection(connection, is_simulator=False)`
Sets the MAVLink connection to use and specifies if it's a simulator.

Parameters:
- `connection`: A MAVLink connection object
- `is_simulator`: Boolean indicating if the connection is to a simulator

#### `start()`
Starts message handling.

Returns:
- `bool`: True if successfully started, False otherwise

#### `stop()`
Stops message handling and resets simulator state if applicable.

#### `process_messages()`
Processes incoming MAVLink messages from the connection queue.
- Processes up to a maximum number of messages per cycle for better performance
- Routes each message to the appropriate handler based on message type
- Provides debugging output for important message values

### Message Filtering Implementation

#### `_update_message_filter(msg_type, msg_data, should_log)`
Implements the message filtering logic:

```python
def _update_message_filter(self, msg_type, msg_data, should_log):
    """
    Implements intelligent message filtering based on:
    1. Value changes that exceed thresholds
    2. Minimum time intervals between messages
    3. Message priority
    
    Returns True if message should be logged/processed
    """
    current_time = time.time()
    
    # Always process critical messages
    if msg_type in self._critical_messages:
        return True
        
    # Check if we've seen this message type before
    if msg_type not in self._last_message_data:
        # First time seeing this message type, initialize
        self._last_message_data[msg_type] = {
            'data': msg_data,
            'last_time': current_time
        }
        return True
        
    # Get last data and time for this message type
    last_data = self._last_message_data[msg_type]['data']
    last_time = self._last_message_data[msg_type]['last_time']
    
    # Check time-based filtering
    if current_time - last_time < self._min_message_interval[msg_type]:
        return False
        
    # Check value-based filtering if requested
    if should_log and self._should_log_value_change(msg_type, last_data, msg_data):
        # Update the stored values and time
        self._last_message_data[msg_type] = {
            'data': msg_data,
            'last_time': current_time
        }
        return True
        
    return False
```

#### Message Type-Specific Thresholds
The handler defines different thresholds for different message types:

```python
# Define thresholds for different message types
self._value_change_thresholds = {
    'ATTITUDE': {
        'roll': 0.05,   # ~3 degrees
        'pitch': 0.05,  # ~3 degrees
        'yaw': 0.08     # ~5 degrees
    },
    'GLOBAL_POSITION_INT': {
        'lat': 0.0001,  # ~10m
        'lon': 0.0001,  # ~10m
        'alt': 2.0      # 2m
    },
    'SYS_STATUS': {
        'voltage': 0.2,  # 0.2V
        'current': 0.5,  # 0.5A
        'remaining': 5   # 5%
    }
}
```

#### Minimum Time Intervals
The handler enforces minimum time intervals between logging the same message type:

```python
# Define minimum time between messages in seconds
self._min_message_interval = {
    'HEARTBEAT': 2.0,
    'ATTITUDE': 0.5,
    'GLOBAL_POSITION_INT': 1.0,
    'SYS_STATUS': 2.0,
    'VFR_HUD': 1.0,
    'STATUSTEXT': 0.0,  # Always log
    'PARAM_VALUE': 0.0  # Always log
}
```

#### Critical Messages
Certain message types are considered critical and are always processed:

```python
# Define critical messages that should always be processed
self._critical_messages = [
    'STATUSTEXT',
    'PARAM_VALUE',
    'COMMAND_ACK'
]
```

## Simulator Support

The message handler includes support for simulated data:

- `_send_simulated_data()`: Generates and sends simulated sensor data
- `_send_simulator_messages()`: Sends initial messages when in simulator mode
- `_update_simulator()`: Updates simulator state based on time

## Integration with Other Components

The `MessageHandler` interacts with several other key components:

1. **Logger**: For recording message activity
2. **SensorViewModel**: Receives processed sensor data via signals
3. **ParameterManager**: Receives parameter updates
4. **MAVLink Connection**: Sends and receives MAVLink messages

## Best Practices

1. **Configuring Thresholds**:
   Adjust the value change thresholds based on your application needs:
   - Lower thresholds for more precision (more messages)
   - Higher thresholds for reduced logging (fewer messages)

2. **Time Intervals**:
   Adjust minimum time intervals based on message importance:
   - Critical status messages: 0 seconds (always log)
   - Frequent sensor updates: 0.5-1.0 seconds
   - System status information: 2.0+ seconds

3. **Adding New Message Types**:
   When adding new message types, remember to:
   - Define appropriate thresholds
   - Set minimum time intervals
   - Decide if the message type is critical
   - Create signal handlers for distributing the message

## Example: How Filtering Works

Consider an ATTITUDE message with small roll/pitch changes:

1. Message arrives with roll=0.1, pitch=0.2
2. Last recorded values: roll=0.09, pitch=0.18
3. Changes: roll delta=0.01, pitch delta=0.02
4. Threshold for ATTITUDE roll/pitch is 0.05
5. Both deltas are below threshold → message is filtered out

When a significant change occurs:

1. Message arrives with roll=0.2, pitch=0.2
2. Last recorded values: roll=0.09, pitch=0.18
3. Changes: roll delta=0.11, pitch delta=0.02
4. Roll delta exceeds threshold → message is processed
5. Values and timestamp are updated in the cache
