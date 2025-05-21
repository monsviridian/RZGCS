# RZGCS - Drone Control System

A user-friendly drone control software for Mac.

## Documentation

Detailed documentation for RZGCS is available in the following files:

### Core Components
- [Installation Guide](docs/installation.md) - Comprehensive installation instructions and dependencies
- [Exceptions Documentation](docs/exceptions.md) - Documentation of the exception system

### Communication and Data
- [Logger Documentation](docs/logger.md) - Documentation of the logging system with MAVLink filtering functions
- [Message Handler Documentation](docs/message_handler.md) - Documentation of the MAVLink message system with filtering functions
- [Serial Connector Documentation](docs/serial_connector.md) - Documentation of the connection system for drones

### Sensors and Parameters
- [SensorViewModel Documentation](docs/sensorviewmodel.md) - Documentation of the sensor data model
- [Parameter System Documentation](docs/parameter_system.md) - Documentation of the parameter management system

### Views and Control
- [Flight View Controller Documentation](docs/flight_view_controller.md) - Documentation of the flight view and map control
- [Motor Test Controller Documentation](docs/motor_test_controller.md) - Documentation of the motor test system

## Installation

1. **Install Python**
   - Visit [python.org](https://www.python.org/downloads/)
   - Download the latest Python version for Mac
   - Run the installer and follow the instructions

2. **Download Software**
   - Download the latest version of RZGCS
   - Extract the ZIP file to a folder of your choice

3. **Install Dependencies**
   - Open Terminal (via Spotlight search or Applications/Utilities)
   - Navigate to the RZGCS folder:
     ```bash
     cd /path/to/RZGCS
     ```
   - Run the installation script:
     ```bash
     ./install_mac.sh
     ```

## Starting the Software

1. **Simple Start**
   - Double-click on the `start_mac.command` file in the RZGCS folder
   - The software starts automatically

2. **Manual Start**
   - Open Terminal
   - Navigate to the RZGCS folder
   - Run:
     ```bash
     python main.py
     ```

## Usage

1. **Establishing Connection**
   - Select the correct COM port
   - Click on "Connect"

2. **Controlling the Drone**
   - Sensor data is displayed automatically
   - Logs show the status of the drone
   - Important warnings are highlighted in red

## Troubleshooting

If the software doesn't start:
1. Check if Python is installed correctly
2. Run the installation script again
3. Restart your computer

For additional problems, please contact support.

## System Requirements

- macOS 10.15 or newer
- Python 3.8 or newer
- 4GB RAM
- 500MB free disk space

## Features

- Real-time sensor monitoring
- MAVLink protocol integration
- Configurable logging system
- Motor control and testing
- User-friendly QML interface

## Development

### Code Quality

The project uses:
- Black for code formatting
- MyPy for static type checking
- Flake8 for linting

Running quality checks:
```bash
black Python/
mypy Python/
flake8 Python/
```

### Tests

Running tests:
```bash
pytest Python/tests/
```

## Project Structure

```
.
├── Python/
│   ├── backend/
│   │   ├── sensorviewmodel.py   # Sensor data model
│   │   ├── serial_connector.py  # Serial communication
│   │   ├── mavsdk_connector.py  # MAVLink integration
│   │   └── logger.py            # Logging system
│   └── tests/
│       └── test_sensorviewmodel.py
├── App/                        # QML frontend
└── requirements.txt
```

## Configuration

The application can be configured via environment variables or `config.json`:

- `DRONE_DEFAULT_PORT`: Serial port (default: COM8)
- `DRONE_DEFAULT_BAUDRATE`: Baud rate (default: 57600)
- `DRONE_LOG_LEVEL`: Log level (DEBUG, INFO, WARNING, ERROR)

## Error Handling

The system uses custom exceptions for various error scenarios:

- `ConnectionException`: Connection problems
- `SensorException`: Sensor errors
- `MotorException`: Motor errors
- `CalibrationException`: Calibration errors

## Contributing

1. Create a fork
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push the branch (`git push origin feature/AmazingFeature`)
5. Create a Pull Request

## License

This project is licensed under the MIT License. 