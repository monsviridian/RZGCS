# RZGCS Parameter Management System Documentation

## Overview
The Parameter Management System in RZGCS enables the ground control station to discover, view, filter, and modify parameters on the connected flight controller. This system is crucial for configuring drone behavior, calibrating sensors, and setting mission parameters. It consists of two main components: the `ParameterTableModel` and the `ParameterManager`.

## Key Features

### Parameter Discovery and Loading
- Automatic parameter discovery from flight controllers
- Support for loading parameters in batch or individually
- Efficient parameter storage and lookup

### Parameter Modification
- Direct parameter value modifications with type checking
- Parameter write confirmations
- Error handling for parameter update failures

### Parameter Organization
- Filtering and search capabilities
- Categorization of parameters
- Support for units, default values, and descriptions

## Component: ParameterTableModel

The `ParameterTableModel` class implements a Qt model for efficiently displaying and manipulating parameter data in the UI.

### Roles

| Role | Value | Description |
|------|-------|-------------|
| `NameRole` | Qt.UserRole + 1 | Parameter name identifier |
| `ValueRole` | Qt.UserRole + 2 | Current parameter value |
| `DefaultValueRole` | Qt.UserRole + 3 | Default parameter value |
| `UnitRole` | Qt.UserRole + 4 | Unit of measurement |
| `OptionsRole` | Qt.UserRole + 5 | Available options for the parameter |
| `DescRole` | Qt.UserRole + 6 | Parameter description |

### Signals

| Signal | Parameters | Description |
|--------|------------|-------------|
| `parametersLoaded` | None | Emitted when parameters are loaded |
| `parameterChanged` | str, str | Emitted when a parameter value changes (name, new value) |

### Methods

#### `set_parameters(param_list)`
Sets the full list of parameters in the model.

Parameters:
- `param_list`: List of parameter objects with name, value, etc.

#### `get_parameters()`
Returns all parameters as a list.

Returns:
- `QVariantList`: All parameters

#### `set_parameter_value(name, value)`
Sets the value of a specific parameter.

Parameters:
- `name`: The parameter name
- `value`: The new parameter value

Returns:
- `bool`: True if successful, False otherwise

#### `get_parameter_by_name(name)`
Retrieves a parameter by its name.

Parameters:
- `name`: The parameter name to look up

Returns:
- `QVariantMap`: The parameter object or empty dict if not found

#### `filter_parameters(search_text)`
Filters parameters based on a search string.

Parameters:
- `search_text`: Text to search for in parameter names and descriptions

Returns:
- `QVariantList`: Filtered list of parameters

#### `add_parameter(param)`
Adds a single parameter to the model.

Parameters:
- `param`: Parameter object with name, value, etc.

#### `clear_parameters()`
Clears all parameters from the model.

## Component: ParameterManager

The `ParameterManager` class handles the communication between the flight controller and the parameter model, managing parameter loading and updates.

### Signals

| Signal | Parameters | Description |
|--------|------------|-------------|
| `parametersLoaded` | list | Emitted when parameters are loaded from the flight controller |
| `parameterUpdated` | str, float | Emitted when a parameter is updated (name, value) |
| `errorOccurred` | str | Emitted when an error occurs during parameter operations |

### Methods

#### `__init__(parameter_model, logger)`
Initializes the parameter manager.

Parameters:
- `parameter_model`: Instance of ParameterTableModel
- `logger`: Instance of Logger for recording events

#### `set_connection(connection)`
Sets the MAVLink connection to use.

Parameters:
- `connection`: MAVLink connection object

#### `load_parameters()`
Loads all parameters from the flight controller.

#### `handle_parameter(msg)`
Handles an individual parameter message.

Parameters:
- `msg`: MAVLink PARAM_VALUE message

#### `set_parameter(name, value)`
Sets a parameter on the flight controller.

Parameters:
- `name`: Parameter name
- `value`: New parameter value

Returns:
- `bool`: True if successful, False otherwise

## Parameter Format

Each parameter is represented as a dictionary with the following fields:

```python
{
    "name": "PARAM_NAME",      # Parameter identifier (e.g., "COMPASS_ORIENT")
    "value": 1.0,              # Current value
    "defaultValue": 0.0,       # Default value
    "unit": "deg",             # Unit of measurement
    "options": "0:X,1:Y,2:Z",  # Available options for enum parameters
    "desc": "Orientation..."   # Description of the parameter
}
```

## Integration with MAVLink

The Parameter System interacts with the flight controller using MAVLink messages:

### Parameter Loading
```python
# Request all parameters
connection.param_fetch_all()

# Receive parameters
msg = connection.recv_match(type='PARAM_VALUE', blocking=True, timeout=2)
if msg:
    # Process parameter
    param = {
        "name": msg.param_id,
        "value": msg.param_value,
        # ... additional fields
    }
```

### Parameter Setting
```python
# Set parameter on flight controller
connection.param_set_send(param_name, param_value)
```

## Integration with QML

The Parameter System is designed to be used from QML interfaces:

```qml
import QtQuick
import QtQuick.Controls

ListView {
    width: parent.width
    height: parent.height
    model: parameterModel  // The ParameterTableModel exposed from Python
    
    delegate: Rectangle {
        width: parent.width
        height: 60
        
        Column {
            Text {
                text: name  // Name role
                font.bold: true
            }
            
            Row {
                spacing: 10
                
                Text {
                    text: value  // Value role
                }
                
                Text {
                    text: unit  // Unit role
                    visible: unit != ""
                }
            }
            
            Text {
                text: desc  // Description role
                font.italic: true
                font.pixelSize: 12
            }
        }
        
        // Parameter modification
        MouseArea {
            anchors.fill: parent
            onClicked: {
                // Open parameter editor
                parameterEditor.open(name, value, unit, desc)
            }
        }
    }
}
```

## Parameter Categories

Common parameter categories in ArduPilot and PX4 based systems:

| Category | Description | Examples |
|----------|-------------|----------|
| ARMING | Arming checks and requirements | ARMING_CHECK, ARMING_REQUIRE |
| COMPASS | Compass configuration | COMPASS_ORIENT, COMPASS_EXTERN |
| BATTERY | Battery monitoring | BATT_CAPACITY, BATT_MONITOR |
| GPS | GPS configuration | GPS_TYPE, GPS_HDOP_GOOD |
| RC | Remote control settings | RC_SPEED, RC_MAP_ROLL |
| SERVO | Servo output configuration | SERVO1_FUNCTION, SERVO_RATE |

## Best Practices

### Loading Parameters
```python
# Connect signal handlers before loading
parameter_manager.parametersLoaded.connect(on_parameters_loaded)
parameter_manager.errorOccurred.connect(on_error)

# Then load parameters
parameter_manager.load_parameters()
```

### Modifying Parameters
```python
# Simple parameter update
parameter_model.set_parameter_value("COMPASS_ORIENT", "2")

# Safe parameter update with verification
if parameter_model.set_parameter_value("BATT_CAPACITY", "10000"):
    print("Parameter updated successfully")
else:
    print("Parameter update failed")
```

### Filtering Parameters
```python
# Search for compass-related parameters
compass_params = parameter_model.filter_parameters("compass")

# Search for battery parameters
battery_params = parameter_model.filter_parameters("batt")
```

## Error Handling

The parameter system includes robust error handling:

```python
try:
    parameter_manager.set_parameter("INVALID_PARAM", 1.0)
except Exception as e:
    print(f"Parameter error: {str(e)}")
```

Error messages are also emitted through the `errorOccurred` signal, which can be connected to UI components to show errors to the user.

## Parameter File Management

The RZGCS system allows saving and loading parameter files:

1. **Saving Parameters**: Export current parameters to a file for backup
2. **Loading Parameters**: Import parameters from a file to configure a drone
3. **Parameter Comparison**: Compare current parameters with a file to identify differences

This capability is essential for fleet management and configuration version control.
