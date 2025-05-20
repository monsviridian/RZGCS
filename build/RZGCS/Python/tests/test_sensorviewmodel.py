import pytest
from PySide6.QtCore import Qt
from backend.sensorviewmodel import SensorViewModel
from backend.exceptions import SensorException

@pytest.fixture
def model():
    """Fixture für ein frisches SensorViewModel für jeden Test."""
    return SensorViewModel()

def test_initial_sensor_count(model):
    """Test, dass die initiale Anzahl der Sensoren korrekt ist."""
    assert model.rowCount() == 13  # Anzahl der vordefinierten Sensoren

def test_sensor_roles(model):
    """Test, dass alle Rollen korrekt definiert sind."""
    roles = model.roleNames()
    assert roles[model.NameRole] == b"name"
    assert roles[model.ValueRole] == b"value"
    assert roles[model.FormattedValueRole] == b"formattedValue"

def test_sensor_data_access(model):
    """Test des Zugriffs auf Sensordaten."""
    index = model.index(0)  # Erster Sensor (Roll)
    
    # Test Sensor Name
    name = model.data(index, model.NameRole)
    assert name == "Roll"
    
    # Test Sensor Value
    value = model.data(index, model.ValueRole)
    assert value == 0.0
    
    # Test Formatted Value
    formatted = model.data(index, model.FormattedValueRole)
    assert formatted == "0.00"

def test_update_sensor(model):
    """Test der Sensor-Aktualisierung."""
    model.update_sensor("Roll", 45.123)
    
    index = model.index(0)
    value = model.data(index, model.ValueRole)
    formatted = model.data(index, model.FormattedValueRole)
    
    assert value == 45.123
    assert formatted == "45.12"

def test_invalid_sensor_update(model):
    """Test, dass eine Exception bei ungültigem Sensor geworfen wird."""
    with pytest.raises(SensorException):
        model.update_sensor("NonExistentSensor", 0.0)

def test_invalid_index(model):
    """Test des Verhaltens bei ungültigem Index."""
    invalid_index = model.index(999)  # Index außerhalb des gültigen Bereichs
    assert model.data(invalid_index, model.NameRole) is None

def test_formatted_value_with_invalid_data(model):
    """Test der Formatierung bei ungültigen Daten."""
    # Simuliere ungültige Daten (würde in der Praxis nicht vorkommen)
    model._sensors[0]["value"] = "invalid"
    
    index = model.index(0)
    formatted = model.data(index, model.FormattedValueRole)
    assert formatted == "—"  # Erwartetes Verhalten bei Formatierungsfehler 