# RZGCS Flight View Controller Documentation

## Overview
The Flight View Controller is a core component of the RZGCS system responsible for visualizing and controlling drone flight operations. It provides both 2D and 3D map views, drone position tracking, mission planning capabilities, and flight control commands. This controller serves as the bridge between the MAVLink communication layer and the user interface, offering a comprehensive flight operations platform.

## Key Components

### FlightViewController
The main controller class that coordinates flight view functionality and connects QML UI elements with Python backend operations.

### SimpleMapWidget
A lightweight 2D map widget that visualizes drone position, heading, path, and key flight metrics when the 3D view is not available or appropriate.

## Key Features

### Map Visualization
- **Dual View Modes**: Toggle between 2D simplified view and 3D terrain view
- **Drone Tracking**: Real-time visualization of drone position, heading, and path
- **Terrain Visualization**: In 3D mode, display realistic terrain and elevation data
- **Flight Path History**: Track and display the drone's historical flight path
- **Mission Waypoints**: Display and edit mission waypoints on the map

### Flight Control
- **Mission Planning**: Add, edit, and remove waypoints for autonomous flight
- **Mission Execution**: Start and monitor autonomous missions
- **Direct Controls**: Manual flight control commands (RTH, Land, Emergency Stop)
- **Safety Features**: One-click return-to-home and emergency stop functions

## Class: FlightViewController

### Signals

| Signal | Parameters | Description |
|--------|------------|-------------|
| `dronePositionChanged` | None | Emitted when the drone position changes |
| `mapTypeChanged` | int | Emitted when the map type changes (0=2D, 1=3D) |

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `_drone_lat` | float | Current drone latitude |
| `_drone_lon` | float | Current drone longitude |
| `_drone_alt` | float | Current drone altitude (meters) |
| `_drone_speed` | float | Current drone speed (m/s) |
| `_drone_battery` | float | Current battery level (percent) |
| `_map_type` | int | Current map type (0=2D, 1=3D) |

### Methods

#### `__init__(engine, parent=None)`
Initializes the Flight View Controller.

Parameters:
- `engine`: QML engine for UI interaction
- `parent`: Parent QObject

#### `initialize(root_item)`
Initializes the Flight View and connects it to the QML UI.

Parameters:
- `root_item`: Root QML item

Returns:
- `bool`: True if initialization was successful

#### `simulate_drone_movement()`
Simulates drone movement for testing purposes.

#### `update_drone_position(lat, lon, alt, heading=0, speed=0, battery=100)`
Updates the drone position on the map.

Parameters:
- `lat`: Latitude
- `lon`: Longitude
- `alt`: Altitude in meters
- `heading`: Drone heading in degrees
- `speed`: Drone speed in m/s
- `battery`: Battery level in percent

#### `set_map_type(map_type)`
Sets the map type.

Parameters:
- `map_type`: Map type (0=2D, 1=3D)

#### `open_external_map()`
Opens the external 3D map in a separate window.

#### `center_on_drone()`
Centers the map view on the current drone position.

#### `add_waypoint()`
Adds a waypoint at the current drone position.

#### `start_mission()`
Starts the autonomous mission following the defined waypoints.

#### `land()`
Commands the drone to perform an automatic landing procedure.

#### `return_to_home()`
Commands the drone to return to the launch/home position.

#### `emergency_stop()`
Performs an emergency stop of the drone.

## Class: SimpleMapWidget

A QWidget-based 2D map display that shows drone position, heading, path, and flight information.

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `drone_lat` | float | Drone latitude |
| `drone_lon` | float | Drone longitude |
| `drone_alt` | float | Drone altitude (meters) |
| `drone_heading` | float | Drone heading (degrees) |
| `drone_speed` | float | Drone speed (m/s) |
| `drone_battery` | float | Battery level (percent) |
| `drone_path` | list | History of drone positions |
| `center_lat` | float | Map center latitude |
| `center_lon` | float | Map center longitude |
| `zoom` | float | Map zoom level |
| `show_grid` | bool | Whether to show coordinate grid |
| `show_path` | bool | Whether to show drone path |

### Methods

#### `paintEvent(event)`
Draws the 2D map view.

#### `update_drone_position(lat, lon, alt, heading=0, speed=0, battery=100)`
Updates the drone position on the map.

Parameters:
- `lat`: Latitude
- `lon`: Longitude
- `alt`: Altitude
- `heading`: Heading in degrees
- `speed`: Speed in m/s
- `battery`: Battery level in percent

#### `geo_to_screen(lat, lon)`
Converts geographic coordinates to screen coordinates.

Returns:
- `tuple`: (x, y) screen coordinates

#### `draw_grid(painter)`
Draws a coordinate grid on the map.

#### `draw_path(painter)`
Draws the drone's historical path.

#### `draw_info_panel(painter)`
Draws an information panel with flight data.

## Integration with QML

The Flight View Controller is designed to integrate with QML UI:

```qml
// In QML file
Rectangle {
    id: map3DContainer
    objectName: "map3DContainer"
    
    // Function called from Python to embed the native widget
    function setNativeWindowId(winId) {
        // Set native window for embedding
    }
}

Button {
    text: "Center on Drone"
    onClicked: flightViewController.center_on_drone()
}

Button {
    text: "Add Waypoint"
    onClicked: flightViewController.add_waypoint()
}

Button {
    text: "Start Mission"
    onClicked: flightViewController.start_mission()
}

Button {
    text: "Return to Home"
    onClicked: flightViewController.return_to_home()
}
```

## Integration with MAVLink

The Flight View Controller processes drone position data from MAVLink messages:

```python
# Handling GLOBAL_POSITION_INT messages
def handle_position(msg):
    lat = msg.lat / 1e7  # Convert from int32 to degrees
    lon = msg.lon / 1e7
    alt = msg.relative_alt / 1000.0  # Convert from mm to meters
    
    # Update the flight view
    flight_view_controller.update_drone_position(lat, lon, alt)
```

## 3D Map Visualization

The Flight View Controller supports a rich 3D map visualization that:

1. Displays satellite imagery and terrain data
2. Shows 3D models of the drone and other aircraft
3. Visualizes waypoints and flight paths in 3D space
4. Provides interactive navigation controls
5. Supports mission planning with drag-and-drop waypoints

## Mission Planning Features

The controller provides mission planning capabilities:

1. **Waypoint Creation**: Add points on the map to create a flight path
2. **Mission Parameters**: Configure altitude, speed, and actions for each waypoint
3. **Mission Validation**: Check mission parameters for safety and feasibility
4. **Mission Simulation**: Preview the planned mission before execution
5. **Mission Upload/Download**: Transfer mission data to/from the drone

## Best Practices

### Working with the Map Views

1. **Map Type Selection**:
   - Use 2D view for simplified visualization and lower resource usage
   - Use 3D view for terrain awareness and immersive planning

2. **Performance Optimization**:
   - Limit path history length when tracking long missions
   - Use simplified rendering for low-resource environments
   - Consider using the external map view for complex missions

3. **Flight Control Safety**:
   - Always confirm flight control commands with the user
   - Implement fail-safe mechanisms for all operations
   - Provide clear visual feedback for safety-critical actions

### Extending the Flight View

To add custom flight view features:

1. Add new methods to `FlightViewController`
2. Expose these methods to QML
3. Connect appropriate signals between Python and QML
4. Update the map visualization as needed

Example:
```python
# Adding a geofence visualization feature
@Slot(list)
def set_geofence(self, coordinates):
    """Set and display a geofence boundary."""
    if self.map_widget:
        self.map_widget.set_geofence_coordinates(coordinates)
        self.map_widget.update()
```
