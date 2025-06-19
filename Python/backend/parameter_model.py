from PySide6.QtCore import QAbstractListModel, Qt, QModelIndex, Slot, Signal, QSortFilterProxyModel

class ParameterTableModel(QAbstractListModel):
    NameRole = Qt.UserRole + 1
    ValueRole = Qt.UserRole + 2
    DefaultValueRole = Qt.UserRole + 3
    UnitRole = Qt.UserRole + 4
    OptionsRole = Qt.UserRole + 5
    DescRole = Qt.UserRole + 6

    # Signals
    parametersLoaded = Signal()
    parameterChanged = Signal(str, str)  # Name des Parameters, neuer Wert

    def __init__(self):
        super().__init__()
        self._params = []

    def rowCount(self, parent=QModelIndex()):
        return len(self._params)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or index.row() >= len(self._params):
            return None
        param = self._params[index.row()]
        if role == self.NameRole:
            return param.get("name", "")
        elif role == self.ValueRole:
            return param.get("value", "")
        elif role == self.DefaultValueRole:
            return param.get("defaultValue", "")
        elif role == self.UnitRole:
            return param.get("unit", "")
        elif role == self.OptionsRole:
            return param.get("options", "")
        elif role == self.DescRole:
            return param.get("desc", "")
        return None

    def roleNames(self):
        return {
            self.NameRole: b"name",
            self.ValueRole: b"value",
            self.DefaultValueRole: b"defaultValue",
            self.UnitRole: b"unit",
            self.OptionsRole: b"options",
            self.DescRole: b"desc"
        }

    @Slot(list)
    def set_parameters(self, param_list):
        for p in param_list:
            if 'default' in p:
                p['defaultValue'] = p.pop('default')
        self.beginResetModel()
        self._params = param_list
        self.endResetModel()
        self.parametersLoaded.emit()

    @Slot(result='QVariantList')
    def get_parameters(self):
        return self._params
        
    @Slot(str, str, result=bool)
    def set_parameter_value(self, name, value):
        """Setzt den Wert eines Parameters"""
        try:
            print(f"Versuche Parameter zu setzen: {name} = {value}")
            # Finde den Parameter mit dem angegebenen Namen
            for i, param in enumerate(self._params):
                if param.get("name") == name:
                    print(f"Parameter {name} gefunden, aktualisiere Wert von {param.get('value')} zu {value}")
                    # Aktualisiere den Wert
                    param["value"] = value
                    # Emitiere das dataChanged-Signal
                    index = self.index(i, 0)
                    self.dataChanged.emit(index, index, [self.ValueRole])
                    # Parameter-Änderung signalisieren
                    self.parameterChanged.emit(name, value)
                    return True
            print(f"Parameter {name} nicht gefunden")
            return False
        except Exception as e:
            print(f"Fehler beim Setzen des Parameters: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return False
            
    @Slot(str, result='QVariantMap')
    def get_parameter_by_name(self, name):
        """Gibt einen Parameter anhand seines Namens zurück"""
        for param in self._params:
            if param.get("name") == name:
                return param
        return {}
        
    @Slot(str, result='QVariantList')
    def filter_parameters(self, search_text):
        """Filtert Parameter basierend auf dem Suchtext"""
        if not search_text:
            return self._params
        
        # Debug-Output
        print(f"Filtere {len(self._params)} Parameter nach '{search_text}'")
        
        search_text = search_text.lower()
        filtered_params = []
        
        for param in self._params:
            name = param.get("name", "").lower()
            desc = param.get("desc", "").lower()
            option = param.get("option", "").lower()
            value = str(param.get("value", "")).lower()
            
            if search_text in name or search_text in desc or search_text in option or search_text in value:
                filtered_params.append(param)
        
        # Debug-Output
        print(f"Filter-Ergebnis: {len(filtered_params)} Parameter gefunden")
        return filtered_params
        
    @Slot(dict)
    def add_parameter(self, param):
        # Standardisiere die Parameternamen
        if 'description' in param and 'desc' not in param:
            param['desc'] = param.pop('description')
        if 'default' in param and 'defaultValue' not in param:
            param['defaultValue'] = param.pop('default')
        
        # Füge Parameter zum Modell hinzu
        self.beginInsertRows(QModelIndex(), len(self._params), len(self._params))
        self._params.append(param)
        self.endInsertRows()
        self.parametersLoaded.emit()
    
    @Slot()
    def clear_parameters(self):
        self.beginResetModel()
        self._params = []
        self.endResetModel()