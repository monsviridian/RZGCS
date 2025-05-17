# RZGCS (Raspberry Ground Control Station)

## Overview
RZGCS is a modern, cross-platform ground control station for drones and vehicles using MAVLink (e.g. ArduPilot, PX4). It features a clean Qt/QML-based UI, live telemetry, parameter management, and sensor visualization.

## Features
- Serial MAVLink connection to flight controllers (ArduPilot, PX4, etc.)
- Live sensor data grid (GPS, attitude, battery, airspeed, etc.)
- Parameter table (Mission Planner style) with FC parameter loading
- Log view for connection and flight status
- Modular tabbed UI: Preflight, Parameter, Sensor, Flight
- Modern, dark-themed interface

## Installation

### 1. Install Python 3.9 or newer
- [Download Python](https://www.python.org/downloads/)
- Make sure to check "Add Python to PATH" during installation.

### 2. Clone this repository
```bash
git clone https://github.com/monsviridian/RZGCS.git
cd RZGCS
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. (Optional) Install additional tools for development
```bash
pip install pytest black mypy flake8
```

## Running the Application

### Windows, Linux, or Mac
```bash
python main.py
```

- Select the correct COM port and baudrate (usually 115200)
- Click 'Connect'
- Use the tabs: Preflight, Parameter, Sensoren, Flug

## Folder Structure
- `Python/backend/` — All Python backend logic (serial, MAVLink, models)
- `RZGCSContent/` — All QML UI files
- `main.py` — Application entry point
- `requirements.txt` — Python dependencies

## Parameter Table
- Click "Parameter vom FC laden" in the Parameter tab to fetch all parameters from the connected flight controller.
- The table displays: Name, Value, Default, Unit, Options, Description.
- (Default, Unit, Options, Description are placeholders unless you add metadata.)

## Development
- All QML UI is in `RZGCSContent/`.
- Backend is modular and testable (see `Python/tests/`).
- To run tests:
  ```bash
  pytest Python/tests/
  ```

## Cleaning Up
- Unused files, build folders, and bytecode caches are regularly cleaned.
- Only keep `requirements.txt` (not `requirement.txt`).

## License
MIT License (see LICENSE file)

## Authors
- Original: fuckheinerkleinehack
- English documentation: AI-assisted 