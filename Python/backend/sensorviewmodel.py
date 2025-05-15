from PySide6.QtCore import QAbstractListModel, QModelIndex, Qt, Slot
from typing import Any, Dict, List, Optional, Union
from .exceptions import SensorException

class SensorViewModel(QAbstractListModel):
    """
    A model for managing and displaying sensor data in a Qt application.
    
    Attributes:
        NameRole (int): Role for sensor name
        ValueRole (int): Role for sensor value
        FormattedValueRole (int): Role for formatted sensor value
        LatitudeRole (int): Role for GPS latitude
        LongitudeRole (int): Role for GPS longitude
    """
    
    NameRole = Qt.UserRole + 1
    ValueRole = Qt.UserRole + 2
    FormattedValueRole = Qt.UserRole + 3
    LatitudeRole = Qt.UserRole + 4
    LongitudeRole = Qt.UserRole + 5

    def __init__(self) -> None:
        """Initialize the SensorViewModel with default sensors."""
        super().__init__()
        self._sensors: List[Dict[str, Union[str, float]]] = []

    def add_sensor(self, sensor_id: str, name: str, unit: str) -> None:
        """
        Add a new sensor to the model.
        
        Args:
            sensor_id: Unique identifier for the sensor
            name: Display name of the sensor
            unit: Unit of the sensor value
            
        Raises:
            SensorException: If the sensor already exists
        """
        # Check if sensor already exists
        for sensor in self._sensors:
            if sensor["id"] == sensor_id:
                raise SensorException(f"Sensor with ID {sensor_id} already exists")
        
        # Add new sensor
        self.beginInsertRows(QModelIndex(), len(self._sensors), len(self._sensors))
        self._sensors.append({
            "id": sensor_id,
            "name": name,
            "value": 0.0,
            "unit": unit,
            "latitude": 0.0 if name == "GPS" else None,
            "longitude": 0.0 if name == "GPS" else None
        })
        self.endInsertRows()

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """Return the number of sensors."""
        return len(self._sensors)

    def data(self, index: QModelIndex, role: int) -> Optional[Union[str, float]]:
        """
        Return sensor data for the specified role.
        
        Args:
            index: Index of the requested sensor
            role: Role of the requested data
            
        Returns:
            The requested value or None for invalid index/role
        """
        if not index.isValid():
            print("[SensorViewModel] Invalid index")
            return None

        try:
            sensor = self._sensors[index.row()]
            
            if role == self.NameRole:
                return sensor.get("name", "Unknown")
            elif role == self.ValueRole:
                return sensor.get("value", 0.0)
            elif role == self.FormattedValueRole:
                try:
                    if sensor.get("name") == "GPS":
                        # Special formatting for GPS
                        lat = sensor.get("latitude", 0.0)
                        lon = sensor.get("longitude", 0.0)
                        return f"{lat:.6f}, {lon:.6f}"
                    else:
                        value = float(sensor.get("value", 0.0))
                        unit = sensor.get("unit", "")
                        formatted = f"{value:.2f}{unit}"
                        return formatted
                except (ValueError, TypeError) as e:
                    print(f"[SensorViewModel] Error formatting value: {e}")
                    return "—"
            elif role == self.LatitudeRole:
                return sensor.get("latitude", 0.0)
            elif role == self.LongitudeRole:
                return sensor.get("longitude", 0.0)
        except IndexError as e:
            raise SensorException(f"Invalid sensor index: {index.row()}")
        except Exception as e:
            raise SensorException(f"Error retrieving sensor data: {str(e)}")

        return None

    def roleNames(self) -> Dict[int, bytes]:
        """Return available roles and their names."""
        return {
            self.NameRole: b"name",
            self.ValueRole: b"value",
            self.FormattedValueRole: b"formattedValue",
            self.LatitudeRole: b"latitude",
            self.LongitudeRole: b"longitude"
        }

    @Slot(str, float)
    def update_sensor(self, sensor_id: str, value: float) -> None:
        """
        Update the value of a sensor.
        
        Args:
            sensor_id: ID of the sensor to update
            value: New sensor value
            
        Raises:
            SensorException: If the sensor is not found
        """
        try:
            for i, sensor in enumerate(self._sensors):
                if sensor["id"] == sensor_id:
                    self._sensors[i]["value"] = value
                    self.dataChanged.emit(
                        self.index(i), 
                        self.index(i), 
                        [self.ValueRole, self.FormattedValueRole]
                    )
                    return
            raise SensorException(f"Sensor not found: {sensor_id}")
        except Exception as e:
            raise SensorException(f"Error updating sensor: {str(e)}")

    @Slot(float, float)
    def update_gps(self, latitude: float, longitude: float) -> None:
        """
        Update GPS coordinates.
        
        Args:
            latitude: New latitude value
            longitude: New longitude value
        """
        try:
            for i, sensor in enumerate(self._sensors):
                if sensor["name"] == "GPS":
                    # Only update if position has changed significantly
                    if (abs(sensor["latitude"] - latitude) > 0.00001 or 
                        abs(sensor["longitude"] - longitude) > 0.00001):
                        
                        # Update both latitude and longitude
                        self._sensors[i]["latitude"] = latitude
                        self._sensors[i]["longitude"] = longitude
                        # Also update the value field for compatibility
                        self._sensors[i]["value"] = latitude  # Use latitude as the main value
                        
                        # Emit data changed signal for all relevant roles
                        self.dataChanged.emit(
                            self.index(i),
                            self.index(i),
                            [self.LatitudeRole, self.LongitudeRole, self.ValueRole, self.FormattedValueRole]
                        )
                        print(f"[SensorViewModel] GPS updated: {latitude:.6f}, {longitude:.6f}")
                    return
                    
            # If GPS sensor not found, create it
            self.add_sensor("gps", "GPS", "")
            self.update_gps(latitude, longitude)
            
        except Exception as e:
            print(f"[SensorViewModel] Error updating GPS: {str(e)}")





   