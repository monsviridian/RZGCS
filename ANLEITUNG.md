# RZGCS Installation and Usage Guide

## Installation

### Windows
1. Install Python 3.10 or newer from [python.org](https://www.python.org/downloads/)
2. Install Qt 6.8 or newer from [qt.io](https://www.qt.io/download)
3. Open a terminal in the project directory and run:
   ```
   pip install -r requirements.txt
   ```

### Mac
1. Install Python 3.10 or newer from [python.org](https://www.python.org/downloads/)
2. Install Qt 6.8 or newer from [qt.io](https://www.qt.io/download)
3. Open Terminal and run:
   ```
   chmod +x install_mac.sh
   ./install_mac.sh
   ```

## Starting the Application

### Windows
1. Open a terminal in the project directory
2. Run:
   ```
   python main.py
   ```

### Mac
1. Open Terminal
2. Navigate to the project directory
3. Run:
   ```
   python3 main.py
   ```

## Using the Application

### Connection
1. Click on "Connect" in the top menu
2. Select the correct COM port (Windows) or device (Mac)
3. Click "Connect"

### Flight Control
1. Use the "Flight" tab to view the map
2. The drone's position is shown on the map
3. Use the control panel to:
   - Prearm the drone
   - Set position
   - Arm/Disarm
   - Send mission plans

### Sensors
1. Use the "Sensors" tab to view:
   - GPS status
   - Battery level
   - Altitude
   - Speed
   - Heading
   - Flight mode

### Parameters
1. Use the "Parameters" tab to:
   - View all parameters
   - Change parameter values
   - Save parameters

### Logs
1. Use the "Logs" tab to view:
   - Connection status
   - Error messages
   - System messages
   - Flight data

## Troubleshooting

### Connection Issues
- Check if the correct port is selected
- Ensure the drone is powered on
- Try reconnecting

### Display Issues
- Check if Qt is properly installed
- Ensure all dependencies are installed
- Try restarting the application

### Other Issues
- Check the logs for error messages
- Ensure all requirements are met
- Try reinstalling the application

## Support
For support, please contact:
- Email: support@rzgcs.com
- Phone: +49 123 456789 