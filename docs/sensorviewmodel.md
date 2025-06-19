# RZGCS SensorViewModel Documentation

## Overview
The `SensorViewModel` class is a critical component in the RZGCS system that implements a Qt model-view pattern to efficiently present and update sensor data in the user interface. It serves as the bridge between the raw sensor data received via MAVLink messages and the UI components that display this information.

## Key Features

### Qt Model Integration
- Implements the `QAbstractListModel` for seamless integration with Qt's model-view framework
- Provides a robust data structure for sensor values with roles for different data aspects
- Enables efficient updates that minimize UI redraw operations

### Dynamic Sensor Management
- Supports runtime addition of new sensor types
- Allows updates to sensor values with change notifications
- Maintains a consistent data structure for all sensor types

### QML Integration
- Exposes sensor data to QML for modern UI development
- Provides methods for QML to query and interact with sensor data
- Enables reactive UI updates when sensor values change

## Class: SensorViewModel

### Roles

| Role | Value | Description |
|------|-------|-------------|
| `NameRole` | Qt.UserRole + 1 | The human-readable name of the sensor |
| `ValueRole` | Qt.UserRole + 2 | The current value of the sensor |
| `UnitRole` | Qt.UserRole + 3 | The unit of measurement for the sensor |
| `IdRole` | Qt.UserRole + 4 | The unique identifier for the sensor |

### Methods

#### `__init__()`
Initializes the sensor view model with an empty sensor list.

#### `roleNames()`
Returns the mapping between role IDs and their byte-string names for QML access.

Returns:
- `dict`: Mapping of role IDs to role names

#### `rowCount(parent=QModelIndex())`
Returns the number of sensors in the model.

Returns:
- `int`: Number of sensors

#### `data(index, role=Qt.DisplayRole)`
Returns the data for a specific sensor at the given index and role.

Parameters:
- `index`: The model index
- `role`: The role to get data for

Returns:
- The requested sensor data or None if invalid

#### `add_sensor(sensor_id, name, unit)`
Adds a new sensor to the model.

Parameters:
- `sensor_id`: The unique identifier for the sensor
- `name`: The human-readable name of the sensor
- `unit`: The unit of measurement for the sensor

#### `update_sensor(sensor_id, value)`
Updates the value of a sensor by its ID.

Parameters:
- `sensor_id`: The unique identifier of the sensor to update
- `value`: The new value for the sensor

#### `update_gps(lat, lon)`
Convenience method to update both latitude and longitude GPS sensors.

Parameters:
- `lat`: The latitude value
- `lon`: The longitude value

#### `get_all_sensors()`
Returns all sensor data as a list.

Returns:
- `QVariantList`: List of all sensor data

## Standard Sensors

The RZGCS system typically registers these standard sensors:

| Sensor ID | Name | Unit | Description |
|-----------|------|------|-------------|
| `altitude` | Altitude | m | Current altitude above ground level |
| `gps_lat` | Latitude | ° | GPS latitude coordinate |
| `gps_lon` | Longitude | ° | GPS longitude coordinate |
| `heading` | Heading | ° | Current heading direction |
| `roll` | Roll | ° | Roll angle |
| `pitch` | Pitch | ° | Pitch angle |
| `groundspeed` | Ground Speed | m/s | Speed relative to ground |
| `airspeed` | Air Speed | m/s | Speed relative to air |
| `battery_voltage` | Battery | V | Main battery voltage |
| `battery_current` | Current | A | Main battery current draw |
| `battery_remaining` | Battery | % | Remaining battery percentage |

## Integration with MAVLink Messages

The SensorViewModel is updated by the message handler when new MAVLink messages arrive:

```python
# In message_handler.py
def _handle_attitude(self, msg):
    # Extract and convert values
    roll_deg = math.degrees(msg.roll)
    pitch_deg = math.degrees(msg.pitch)
    yaw_deg = math.degrees(msg.yaw)
    
    # Update the sensor model
    self._sensor_model.update_sensor("roll", roll_deg)
    self._sensor_model.update_sensor("pitch", pitch_deg)
    self._sensor_model.update_sensor("heading", yaw_deg)
```

## QML Integration

The SensorViewModel is designed to be used in QML views:

```qml
import QtQuick
import QtQuick.Controls

ListView {
    width: parent.width
    height: parent.height
    model: sensorModel  // The SensorViewModel exposed from Python
    
    delegate: Rectangle {
        width: parent.width
        height: 50
        
        Row {
            spacing: 10
            
            Text {
                text: name  // Comes from NameRole
                font.bold: true
            }
            
            Text {
                text: value.toFixed(2) + " " + unit  // ValueRole and UnitRole
            }
        }
    }
}
```

## Best Practices

### Adding New Sensors

When adding new sensors to your system:

```python
# First register the sensor
sensor_model.add_sensor("current_waypoint", "Waypoint", "#")

# Later update it when new data is available
sensor_model.update_sensor("current_waypoint", mission.current_waypoint)
```

### Optimizing Updates

For performance-critical applications, consider:

1. Only update sensors when values have changed significantly
2. Group updates for related sensors to minimize model change notifications
3. Use the more specific update methods for common sensor groups

Example of efficient updates:

```python
# Instead of individual updates:
sensor_model.update_sensor("roll", roll_deg)
sensor_model.update_sensor("pitch", pitch_deg)
sensor_model.update_sensor("heading", yaw_deg)

# Consider creating a more efficient batch update:
sensor_model.update_attitude(roll_deg, pitch_deg, yaw_deg)  # A custom method
```

### Accessing Sensor Data Programmatically

To access sensor data from Python code:

```python
# Get all sensors
all_sensors = sensor_model.get_all_sensors()

# Find a specific sensor
altitude_sensor = next((s for s in all_sensors if s["id"] == "altitude"), None)
if altitude_sensor:
    current_altitude = altitude_sensor["value"]
```
