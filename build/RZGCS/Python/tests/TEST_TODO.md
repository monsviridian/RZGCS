# RZGCS Test Instructions

## Test Environment Setup
1. Install test dependencies:
   ```bash
   pip install pytest pytest-qt pytest-cov
   ```

2. Run tests with coverage:
   ```bash
   pytest --cov=backend tests/
   ```

## Test Categories

### 1. Connection Tests
- Test connection to different COM ports
- Test connection timeout handling
- Test reconnection logic
- Test connection error handling

Example test:
```python
def test_connection_timeout():
    connector = MavlinkConnector()
    with pytest.raises(ConnectionTimeoutError):
        connector.connect("COM99", timeout=1)
```

### 2. Sensor Data Tests
- Test GPS data parsing
- Test battery level updates
- Test altitude calculations
- Test speed calculations
- Test heading updates

Example test:
```python
def test_gps_data_parsing():
    connector = MavlinkConnector()
    test_data = {
        'lat': 51.1657,
        'lon': 10.4515,
        'alt': 100
    }
    result = connector._parse_gps_data(test_data)
    assert result['latitude'] == 51.1657
    assert result['longitude'] == 10.4515
    assert result['altitude'] == 100
```

### 3. UI Tests
- Test all buttons and controls
- Test map display
- Test sensor display updates
- Test parameter view
- Test log display

Example test:
```python
def test_arm_button(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)
    
    # Find and click arm button
    arm_button = window.findChild(QPushButton, "armButton")
    qtbot.mouseClick(arm_button, Qt.LeftButton)
    
    # Check if arm command was sent
    assert window.connector.last_command == "ARM"
```

### 4. Parameter Tests
- Test parameter reading
- Test parameter writing
- Test parameter validation
- Test parameter saving

Example test:
```python
def test_parameter_validation():
    connector = MavlinkConnector()
    # Test valid parameter
    assert connector.validate_parameter("MAX_ALT", 100) == True
    # Test invalid parameter
    assert connector.validate_parameter("MAX_ALT", -1) == False
```

### 5. Mission Tests
- Test mission plan parsing
- Test mission upload
- Test mission execution
- Test mission abort

Example test:
```python
def test_mission_parsing():
    connector = MavlinkConnector()
    test_mission = """
    QGC WPL 110
    0   0   0   16  0   0   0   0   51.1657  10.4515  100 1
    1   0   3   16  0   0   0   0   51.1658  10.4516  100 1
    """
    result = connector.parse_mission(test_mission)
    assert len(result) == 2
    assert result[0]['lat'] == 51.1657
```

## Test Priority
1. Connection Tests (Critical)
2. Sensor Data Tests (Critical)
3. Parameter Tests (High)
4. Mission Tests (High)
5. UI Tests (Medium)

## Test Coverage Goals
- Overall coverage: > 80%
- Critical components: > 90%
- UI components: > 70%

## How to Run Specific Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_connection.py

# Run specific test
pytest tests/test_connection.py::test_connection_timeout

# Run tests with coverage report
pytest --cov=backend --cov-report=html
```

## Test Data
Test data files are located in `Python/tests/test_data/`:
- `sample_mission.waypoints`
- `test_parameters.json`
- `sample_log.txt`

## Reporting Issues
When you find issues during testing:
1. Create a new issue in GitHub
2. Include:
   - Test case that failed
   - Expected behavior
   - Actual behavior
   - Steps to reproduce
   - Test environment details

## Test Environment Requirements
- Python 3.10+
- pytest
- pytest-qt
- pytest-cov
- Qt 6.8+
- MAVLink library
- Serial port access (for connection tests) 