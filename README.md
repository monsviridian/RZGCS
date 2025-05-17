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

## Requirements
- Python 3.9+
- PySide6
- pymavlink
- (Optional) pytest for tests

Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage
1. **Connect your flight controller** via USB/serial.
2. **Start the application:**
   ```bash
   python main.py
   ```
3. **Select the correct COM port and baudrate** (usually 115200).
4. **Click 'Connect'.**
5. Use the tabs:
   - **Preflight:** Connection, status, and basic controls
   - **Parameter:** Load and view all FC parameters in a table
   - **Sensoren:** Live sensor grid (GPS, attitude, battery, etc.)
   - **Flug:** (Flight) - for future flight controls/visualization

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