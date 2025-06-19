from PySide6.QtCore import QObject, Signal, Slot, Property, QAbstractListModel, Qt, QModelIndex

class SensorViewModel(QAbstractListModel):
    NameRole = Qt.UserRole + 1
    ValueRole = Qt.UserRole + 2
    UnitRole = Qt.UserRole + 3
    IdRole = Qt.UserRole + 4

    def __init__(self):
        super().__init__()
        self._sensors = []

    def roleNames(self):
        return {
            self.NameRole: b"name",
            self.ValueRole: b"value",
            self.UnitRole: b"unit",
            self.IdRole: b"id"
        }

    def rowCount(self, parent=QModelIndex()):
        return len(self._sensors)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or index.row() >= len(self._sensors):
            return None
        sensor = self._sensors[index.row()]
        if role == self.NameRole:
            return sensor["name"]
        elif role == self.ValueRole:
            return sensor["value"]
        elif role == self.UnitRole:
            return sensor["unit"]
        elif role == self.IdRole:
            return sensor["id"]
        return None

    @Slot(str, str, str)
    def add_sensor(self, sensor_id, name, unit):
        self.beginInsertRows(QModelIndex(), len(self._sensors), len(self._sensors))
        self._sensors.append({
            "id": sensor_id,
            "name": name,
            "value": 0.0,
            "unit": unit
        })
        self.endInsertRows()

    @Slot(str, float)
    def update_sensor(self, sensor_id, value):
        for i, sensor in enumerate(self._sensors):
            if sensor["id"] == sensor_id:
                if sensor["value"] != value:
                    self._sensors[i]["value"] = value
                    index = self.index(i, 0)
                    self.dataChanged.emit(index, index, [self.ValueRole])
                break

    @Slot(float, float)
    def update_gps(self, lat, lon):
        self.update_sensor("gps_lat", lat)
        self.update_sensor("gps_lon", lon)

    @Slot(result='QVariantList')
    def get_all_sensors(self):
        return self._sensors





   