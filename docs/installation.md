# RZGCS Installation Guide

## System Requirements

### Minimum Hardware Requirements
- CPU: Intel Core i5 or equivalent
- RAM: 8 GB
- Disk space: 1 GB
- Graphics: DirectX 11 or OpenGL 4.3 compatible

### Supported Operating Systems
- Windows 10/11 (64-bit)
- Linux (Ubuntu 20.04 LTS or later)
- macOS 11 (Big Sur) or later

## Installation Guide

### Prerequisites
Before installing RZGCS, ensure you have:
1. Python 3.10 or later installed
2. Git (for cloning the repository)
3. PIP (Python package manager)

### Step 1: Clone the Repository
```bash
git clone https://github.com/your-organization/RZGCS.git
cd RZGCS
```

### Step 2: Set Up Python Environment
It's recommended to use a virtual environment:

#### Windows
```bash
python -m venv venv
venv\Scripts\activate
```

#### Linux/macOS
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure the Environment
1. Copy `config.example.ini` to `config.ini`
2. Edit `config.ini` to set your preferences and connection parameters

### Step 5: Run the Application
```bash
python main.py
```

## Dependencies

RZGCS relies on several key dependencies to function properly:

### Core Dependencies
- **PySide6 >= 6.5.0**: Qt framework for Python, used for UI components
- **pymavlink >= 2.4.37**: Library for MAVLink communication with drones
- **pyserial >= 3.5**: Serial communication library for connecting to hardware
- **numpy >= 1.24.0**: Numerical computing library, used for calculations
- **pydantic >= 2.0.0**: Data validation library

### Packaging Tools
- **cx_Freeze >= 6.15.0**: For creating standalone executables
- **wheel >= 0.40.0**: For creating Python wheel packages
- **pyinstaller >= 5.11.0**: Alternative packaging tool

### Development Dependencies
- **pytest >= 7.3.1**: Testing framework
- **pytest-qt >= 4.2.0**: Qt testing add-on
- **pytest-asyncio >= 0.21.0**: Asynchronous testing
- **black >= 23.3.0**: Code formatter
- **mypy >= 1.3.0**: Static type checking
- **flake8 >= 6.0.0**: Linting tool

## Hardware Connectivity

### Supported Flight Controllers
- Pixhawk series
- ArduPilot compatible boards
- Other MAVLink-compatible flight controllers

### Connection Methods
- USB/Serial
- Telemetry radio
- Network (UDP/TCP)

## Building from Source

### Creating a Standalone Executable

#### Windows
```bash
python setup.py build
```
The executable will be created in the `build/` directory.

#### Linux
```bash
python setup.py build
```

#### macOS
```bash
python setup.py build
```

### Creating a Python Package
```bash
python setup.py bdist_wheel
```

## Troubleshooting

### Common Installation Issues

#### Missing Dependencies
If you encounter errors about missing dependencies:
```bash
pip install -r requirements.txt --upgrade
```

#### Serial Port Access Issues
- **Windows**: Ensure you have the correct COM port
- **Linux**: Add your user to the 'dialout' group
- **macOS**: Install any necessary drivers for your serial device

#### OpenGL/Graphics Issues
Ensure your graphics drivers are up to date. RZGCS requires OpenGL 4.3 or DirectX 11.

#### Python Version Compatibility
If you encounter errors related to Python version incompatibility:
```bash
python --version
```
Ensure you're using Python 3.10 or later.

## Advanced Configuration

### Custom MAVLink Message Filtering

RZGCS implements a sophisticated MAVLink message filtering system that:

1. Caches recent values of each message type
2. Filters messages based on configurable thresholds
3. Enforces minimum time intervals between logging
4. Prioritizes critical messages

To configure these thresholds, edit the following file:
```
Python/backend/message_handler.py
```

### Performance Optimization

For systems with limited resources, consider:

1. Reducing the UI update frequency in `config.ini`
2. Lowering the logging verbosity
3. Disabling 3D visualization if not needed

## Getting Help

If you encounter issues not covered in this documentation:

1. Check the project's issue tracker
2. Review the logs (`logs/` directory)
3. Contact the development team at support@example.com
