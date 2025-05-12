from PySide6.QtCore import QAbstractListModel, QModelIndex, Qt, Slot

class SensorViewModel(QAbstractListModel):
    NameRole = Qt.UserRole + 1
    ValueRole = Qt.UserRole + 2
    FormattedValueRole = Qt.UserRole + 3  # ✅ Neue Rolle für formatierten Text

    def __init__(self):
        super().__init__()
        self._sensors = [
            {"name": "IMU", "value": 0.0},
            {"name": "Speed", "value": 0.0},
            {"name": "Camera", "value": 0.0},
            {"name": "GPS", "value": 0.0},
            {"name": "VTX", "value": 0.0},
            {"name": "Analog Output", "value": 0.0},
            {"name": "Gimbal", "value": 0.0},
            {"name": "Servos", "value": 0.0},
            {"name": "Sonar", "value": 0.0},
            {"name": "LightSensor", "value": 0.0},
            {"name": "Kompass", "value": 0.0},
            {"name": "Optical Flow", "value": 0.0},
            {"name": "Joel", "value": 0.0}
        ]

    def rowCount(self, parent=QModelIndex()):
        return len(self._sensors)

    def data(self, index, role):
        if not index.isValid():
            print("[SensorViewModel] Invalid index")
            return None

        sensor = self._sensors[index.row()]
        print(f"[SensorViewModel] data() called for row {index.row()}, role={role}")

        if role == self.NameRole:
            return sensor["name"]
        elif role == self.ValueRole:
            return sensor["value"]
        elif role == self.FormattedValueRole:
            try:
                formatted = f"{float(sensor['value']):.2f}"
                print(f"[SensorViewModel] formatted value: {formatted}")
                return formatted
            except (ValueError, TypeError) as e:
                print(f"[SensorViewModel] Error formatting value: {e}")
                return "—"

        return None



    def roleNames(self):
        return {
            self.NameRole: b"name",
            self.ValueRole: b"value",
            self.FormattedValueRole: b"formattedValue"
        }

    @Slot(str, float)
    def update_sensor(self, name, value):
        print(f"[SensorViewModel] update_sensor called with: name='{name}', value={value}")

        for i, sensor in enumerate(self._sensors):
            print(f"[SensorViewModel] checking sensor: {sensor['name']}")
            if sensor["name"] == name:
                print(f"[SensorViewModel] Match found. Updating value of '{name}' to {value}")
                self._sensors[i]["value"] = value
                self.dataChanged.emit(self.index(i), self.index(i), [self.ValueRole, self.FormattedValueRole])
                break
        else:
            print(f"[SensorViewModel] WARNING: Sensor '{name}' not found!")
