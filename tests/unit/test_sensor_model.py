"""
Unit tests for the SensorModel class.
"""
import pytest
from PySide6.QtCore import QObject, Signal, Slot
from unittest.mock import MagicMock, patch

class TestSensorModel:
    """Test cases for the SensorModel class."""
    
    @pytest.fixture
    def sensor_model(self, qtbot):
        """Create a SensorModel instance for testing."""
        from Python.sensor_model import SensorModel
        model = SensorModel()
        return model
    
    def test_initial_state(self, sensor_model):
        """Test the initial state of the SensorModel."""
        assert sensor_model._sensors == {}
        assert sensor_model._sensor_history == {}
        
    def test_update_sensor_value_new_sensor(self, sensor_model, qtbot):
        """Test updating a sensor value for a new sensor."""
        with qtbot.waitSignal(sensor_model.sensorUpdated) as blocker:
            sensor_model.update_sensor_value("gps", {"lat": 48.123, "lon": 11.456, "alt": 500.0})
        
        # Check the signal was emitted with correct data
        assert blocker.args == ["gps", {"lat": 48.123, "lon": 11.456, "alt": 500.0}]
        
        # Check the sensor data was stored
        assert sensor_model.get_sensor_value("gps") == {"lat": 48.123, "lon": 11.456, "alt": 500.0}
        
    def test_update_sensor_value_existing_sensor(self, sensor_model, qtbot):
        """Test updating an existing sensor's value."""
        # Initial update
        sensor_model.update_sensor_value("battery", {"voltage": 12.5, "current": 2.5})
        
        # Update existing sensor
        with qtbot.waitSignal(sensor_model.sensorUpdated) as blocker:
            sensor_model.update_sensor_value("battery", {"voltage": 12.3, "current": 3.0})
        
        # Check the signal was emitted with updated data
        assert blocker.args == ["battery", {"voltage": 12.3, "current": 3.0}]
        
    def test_get_sensor_value_nonexistent(self, sensor_model):
        """Test getting a non-existent sensor's value."""
        assert sensor_model.get_sensor_value("nonexistent") is None
        
    def test_get_sensor_history(self, sensor_model):
        """Test getting sensor history."""
        # Add some sensor updates
        sensor_model.update_sensor_value("temperature", {"value": 25.0})
        sensor_model.update_sensor_value("temperature", {"value": 25.5})
        sensor_model.update_sensor_value("temperature", {"value": 26.0})
        
        # Get history (default max_entries=10)
        history = sensor_model.get_sensor_history("temperature")
        assert len(history) == 3
        assert history[0]["value"] == 25.0
        assert history[-1]["value"] == 26.0
        
    def test_history_limiting(self, sensor_model):
        """Test that history is limited to the specified number of entries."""
        # Add more updates than the default history limit
        for i in range(15):
            sensor_model.update_sensor_value("test", {"value": i})
            
        # Should be limited to 10 entries by default
        history = sensor_model.get_sensor_history("test")
        assert len(history) == 10
        assert history[0]["value"] == 5  # First entry should be the 5th update (0-based)
        assert history[-1]["value"] == 14  # Last entry should be the most recent
        
    def test_clear_sensor_data(self, sensor_model):
        """Test clearing sensor data."""
        # Add some data
        sensor_model.update_sensor_value("test1", {"value": 1})
        sensor_model.update_sensor_value("test2", {"value": 2})
        
        # Clear all data
        sensor_model.clear_sensor_data()
        
        # Verify data is cleared
        assert sensor_model.get_sensor_value("test1") is None
        assert sensor_model.get_sensor_value("test2") is None
        assert sensor_model.get_sensor_history("test1") == []
        assert sensor_model.get_sensor_history("test2") == []
