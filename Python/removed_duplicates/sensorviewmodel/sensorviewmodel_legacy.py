from PySide6.QtCore import QObject, Signal, Slot, Property, QAbstractListModel, Qt, QModelIndex, QMetaObject
import json

class SensorViewModel(QAbstractListModel):
    NameRole = Qt.UserRole + 1
    ValueRole = Qt.UserRole + 2
    UnitRole = Qt.UserRole + 3
    IdRole = Qt.UserRole + 4
    
    # Signal für QML-Sensor-Updates
    sensorQmlUpdated = Signal(str, 'QVariant', str)

    def __init__(self):
        super().__init__()
        self._sensors = []
        self._qml_object = None

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
    
    @Slot(QObject)
    def register_qml_object(self, qml_object):
        """Registriert das QML-Objekt für direkte Aktualisierungen"""
        self._qml_object = qml_object
        
    @Slot(str, 'QVariant', str)
    def updateQmlSensor(self, name, value, unit=""):
        """Aktualisiert einen Sensor im QML-Modell"""
        # Signal emittieren, das vom QML-Objekt empfangen werden kann
        self.sensorQmlUpdated.emit(name, value, unit)
        
        # Wenn QML-Objekt registriert ist, direkt update_sensor aufrufen
        if self._qml_object is not None:
            # Daten konvertieren, wenn nötig
            value_variant = value
            if isinstance(value, dict):
                # QML kann keine komplexen Python-Objekte direkt verarbeiten,
                # also konvertieren wir sie zu Strings
                value_variant = json.dumps(value)
                
            # QML-Methode direkt aufrufen
            QMetaObject.invokeMethod(
                self._qml_object,
                "update_sensor",
                Qt.DirectConnection,
                None,  # returnType
                name,  # name
                value_variant,  # value
                unit   # unit
            )