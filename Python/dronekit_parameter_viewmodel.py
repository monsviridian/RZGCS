"""
DroneKit Parameter ViewModel für RZGCS
Stellt Parameter-Management-Funktionen aus DroneKit für die QML-UI bereit
"""

from PySide6.QtCore import QObject, Signal, Slot, Property, QAbstractListModel, Qt, QModelIndex, QTimer
from PySide6.QtGui import QGuiApplication
from typing import List, Dict, Any, Optional
import json
import time
import re

class ParameterListModel(QAbstractListModel):
    """
    Listenmodell für Parameter, das mit QML ListView verbunden werden kann
    """
    
    NameRole = Qt.UserRole + 1
    ValueRole = Qt.UserRole + 2
    TypeRole = Qt.UserRole + 3
    DescriptionRole = Qt.UserRole + 4
    ReadOnlyRole = Qt.UserRole + 5
    CategoryRole = Qt.UserRole + 6
    GroupRole = Qt.UserRole + 7
    DefaultValueRole = Qt.UserRole + 8
    MinValueRole = Qt.UserRole + 9
    MaxValueRole = Qt.UserRole + 10
    UnitsRole = Qt.UserRole + 11
    ModifiedRole = Qt.UserRole + 12
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._parameters = []
        self._filtered_parameters = []
        self._filter_text = ""
        self._show_modified_only = False
        self._modified_parameters = set()
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(300)
        self._search_timer.timeout.connect(self._performSearch)
        
    def roleNames(self):
        return {
            self.NameRole: b"NameRole",
            self.ValueRole: b"ValueRole", 
            self.TypeRole: b"TypeRole",
            self.DescriptionRole: b"DescriptionRole",
            self.ReadOnlyRole: b"ReadOnlyRole",
            self.CategoryRole: b"CategoryRole",
            self.GroupRole: b"GroupRole",
            self.DefaultValueRole: b"DefaultValueRole",
            self.MinValueRole: b"MinValueRole",
            self.MaxValueRole: b"MaxValueRole",
            self.UnitsRole: b"UnitsRole",
            self.ModifiedRole: b"ModifiedRole"
        }
        
    def rowCount(self, parent=QModelIndex()):
        """Gibt die Anzahl der Parameter zurück"""
        if parent.isValid():
            return 0
        count = len(self._filtered_parameters)
        print(f"[DEBUG] rowCount called, returning {count}")
        return count
        
    def data(self, index, role=Qt.DisplayRole):
        """Gibt die Daten für einen Parameter zurück"""
        if not index.isValid() or index.row() >= len(self._filtered_parameters):
            return None
            
        parameter = self._filtered_parameters[index.row()]
        
        if role == self.NameRole:
            return parameter.get("name", "")
        elif role == self.ValueRole:
            return parameter.get("value", 0)
        elif role == self.TypeRole:
            return parameter.get("type", "float")
        elif role == self.DescriptionRole:
            return parameter.get("description", "")
        elif role == self.ReadOnlyRole:
            return parameter.get("read_only", False)
        elif role == self.CategoryRole:
            return parameter.get("category", "Standard")
        elif role == self.GroupRole:
            return parameter.get("group", "Default")
        elif role == self.DefaultValueRole:
            return parameter.get("default_value", None)
        elif role == self.MinValueRole:
            return parameter.get("min_value", None)
        elif role == self.MaxValueRole:
            return parameter.get("max_value", None)
        elif role == self.UnitsRole:
            return parameter.get("units", "")
        elif role == self.ModifiedRole:
            return parameter.get("name", "") in self._modified_parameters
        else:
            return None

    def setParameters(self, parameters: List[Dict[str, Any]]):
        """Setzt die Parameter-Liste"""
        print(f"[DEBUG] setParameters called with {len(parameters)} parameters")
        self.beginResetModel()
        self._parameters = parameters
        print(f"[DEBUG] _parameters set to {len(self._parameters)} items")
        self._applyFilter(reset_model=False)
        self.endResetModel()
        
    def setFilterText(self, filter_text):
        """Setzt den Filtertext für die Parameter"""
        if self._filter_text != filter_text:
            self._filter_text = filter_text
            self._applyFilter()
            
    def setShowModifiedOnly(self, show_modified_only):
        """Setzt, ob nur geänderte Parameter angezeigt werden sollen"""
        if self._show_modified_only != show_modified_only:
            self._show_modified_only = show_modified_only
            self._applyFilter()
            
    def markAsModified(self, param_name):
        """Markiert einen Parameter als geändert"""
        self._modified_parameters.add(param_name)
        self._applyFilter()
        
    def clearModified(self):
        """Löscht alle Markierungen für geänderte Parameter"""
        self._modified_parameters.clear()
        self._applyFilter()
        
    def _performSearch(self):
        """Führt die erweiterte Suche aus (mit Regex und Multi-Wort-Suche)"""
        self._applyFilter()
        
    def _applyFilter(self, reset_model=True):
        """Wendet den Filter auf die Parameter an"""
        print(f"[DEBUG] _applyFilter called with {len(self._parameters)} parameters")
        if reset_model:
            self.beginResetModel()
        # Filter anwenden
        self._filtered_parameters = []
        if not self._filter_text and not self._show_modified_only:
            self._filtered_parameters = self._parameters.copy()
        else:
            search_strings = self._filter_text.split() if self._filter_text else []
            regex_list = []
            for search_item in search_strings:
                try:
                    regex = re.compile(search_item, re.IGNORECASE)
                    regex_list.append(regex)
                except re.error:
                    regex_list.append(None)
            for param in self._parameters:
                name = param.get("name", "").lower()
                description = param.get("description", "").lower()
                category = param.get("category", "").lower()
                group = param.get("group", "").lower()
                if search_strings:
                    all_match = True
                    for i, search_item in enumerate(search_strings):
                        regex = regex_list[i]
                        if regex:
                            if not (regex.search(name) or regex.search(description) or regex.search(category) or regex.search(group)):
                                all_match = False
                                break
                        else:
                            if not (search_item.lower() in name or search_item.lower() in description or search_item.lower() in category or search_item.lower() in group):
                                all_match = False
                                break
                    if not all_match:
                        continue
                if self._show_modified_only and name not in self._modified_parameters:
                    continue
                self._filtered_parameters.append(param)
        print(f"[DEBUG] After filtering: {len(self._filtered_parameters)} parameters remain")
        if reset_model:
            self.endResetModel()
        
    def getParameterByName(self, name):
        """Gibt einen Parameter anhand des Namens zurück"""
        for param in self._parameters:
            if param.get("name", "") == name:
                return param
        return None
        
    def updateParameter(self, name, value):
        """Aktualisiert den Wert eines Parameters"""
        for i, param in enumerate(self._parameters):
            if param.get("name", "") == name:
                param["value"] = value
                self._modified_parameters.add(name)
                
                # Index im gefilterten Modell finden und Signal emittieren
                for j, filtered_param in enumerate(self._filtered_parameters):
                    if filtered_param.get("name", "") == name:
                        index = self.index(j, 0)
                        self.dataChanged.emit(index, index, [self.ValueRole, self.ModifiedRole])
                        break
                break

    @Property(int, constant=True)
    def count(self):
        """Anzahl der Parameter im gefilterten Modell"""
        return len(self._filtered_parameters)


class ParameterCategory(QObject):
    """Repräsentiert eine Parameter-Kategorie"""
    
    def __init__(self, name, parent=None):
        super().__init__(parent)
        self._name = name
        self._groups = []
        self._parameters = []
        
    @Property(str, constant=True)
    def name(self):
        return self._name
        
    @Property(list, constant=True)
    def groups(self):
        return self._groups
        
    @Property(list, constant=True)
    def parameters(self):
        return self._parameters


class ParameterGroup(QObject):
    """Repräsentiert eine Parameter-Gruppe innerhalb einer Kategorie"""
    
    def __init__(self, name, category, parent=None):
        super().__init__(parent)
        self._name = name
        self._category = category
        self._parameters = []
        
    @Property(str, constant=True)
    def name(self):
        return self._name
        
    @Property(str, constant=True)
    def category(self):
        return self._category
        
    @Property(list, constant=True)
    def parameters(self):
        return self._parameters


class DroneKitParameterViewModel(QObject):
    """
    ViewModel für Parameter-Management mit DroneKit - Erweitert mit QGroundControl-Features
    """
    
    # Signale
    parametersChanged = Signal()
    parameterChanged = Signal(str, float)  # name, value
    refreshStarted = Signal()
    refreshCompleted = Signal(bool)  # success
    writeStarted = Signal(str)  # param_name
    writeCompleted = Signal(str, bool)  # param_name, success
    categoriesChanged = Signal()
    searchResultsChanged = Signal()
    
    def __init__(self, drone_connector=None, parent=None):
        """Initialisiert das ViewModel mit optionaler Verbindung zum Connector"""
        super().__init__(parent)
        self._drone_connector = drone_connector
        
        # Parameter-Modell
        self._parameter_model = ParameterListModel(self)
        self._categories = []
        self._current_category = None
        self._current_group = None
        self._last_refresh_time = 0
        self._refresh_in_progress = False
        self._write_queue = []
        self._search_results = []
        
        # Verbinde DroneKit-Signale wenn Connector vorhanden
        if self._drone_connector:
            self._connect_signals()
            
        print("DroneKitParameterViewModel initialisiert")
    
    def set_drone_connector(self, drone_connector):
        """Setzt den DroneKit-Connector und verbindet die Signale"""
        self._drone_connector = drone_connector
        self._connect_signals()
    
    def _connect_signals(self):
        """Verbindet alle DroneKit-Signale mit lokalen Slots"""
        if not self._drone_connector:
            return
            
        try:
            # Verbinde Signale vom DroneKit-Connector
            self._drone_connector.parameters_received.connect(self._on_parameters_received)
            self._drone_connector.parameter_updated.connect(self._on_parameter_updated)
            self._drone_connector.parameter_write_complete.connect(self._on_parameter_write_complete)
            
        except Exception as e:
            print(f"Fehler beim Verbinden der Parameter-Signale: {e}")
    
    # --- Event-Handler ---
    
    def _on_parameters_received(self, parameters):
        """
        Callback für empfangene Parameter
        """
        try:
            print(f"[DEBUG] _on_parameters_received called with {len(parameters)} parameters")
            param_list = []
            categories = {}
            
            # Parameter verarbeiten und kategorisieren
            for name, param_dict in parameters.items():
                value = param_dict.get("value", 0)
                param_type = param_dict.get("type", "float")
                description = param_dict.get("description", "")
                read_only = param_dict.get("read_only", False)
                category = self._categorize_parameter(name)
                group = self._categorize_group(name, category)
                
                # Kategorie und Gruppe verwalten
                if category not in categories:
                    categories[category] = {}
                if group not in categories[category]:
                    categories[category][group] = []
                categories[category][group].append(name)
                
                param_list.append({
                    "name": name,
                    "value": value,
                    "type": param_type,
                    "description": description,
                    "read_only": read_only,
                    "category": category,
                    "group": group,
                    "default_value": param_dict.get("default_value"),
                    "min_value": param_dict.get("min_value"),
                    "max_value": param_dict.get("max_value"),
                    "units": param_dict.get("units", "")
                })
            
            # Sortiere Parameter nach Namen
            param_list.sort(key=lambda x: x["name"])
            
            print(f"[DEBUG] Processed {len(param_list)} parameters, first few: {param_list[:3] if param_list else 'None'}")
            
            # Setze Parameter im Modell
            self._parameter_model.setParameters(param_list)
            
            # Kategorien und Gruppen erstellen
            self._build_categories(categories)
            
            # Status aktualisieren und Signal emittieren
            self._refresh_in_progress = False
            self._last_refresh_time = time.time()
            self.parametersChanged.emit()
            self.categoriesChanged.emit()
            self.refreshCompleted.emit(True)
            
            print(f"{len(param_list)} Parameter empfangen in {len(categories)} Kategorien")
            print(f"[DEBUG] ParameterModel count after setParameters: {self._parameter_model.count}")
            
        except Exception as e:
            print(f"Fehler bei der Verarbeitung der Parameter: {e}")
            import traceback
            traceback.print_exc()
            self._refresh_in_progress = False
            self.refreshCompleted.emit(False)
    
    def _build_categories(self, categories_dict):
        """Erstellt die Kategorien- und Gruppen-Struktur"""
        self._categories = []
        
        # Standard-Kategorie immer zuerst
        if "Standard" in categories_dict:
            standard_cat = ParameterCategory("Standard", self)
            for group_name, params in categories_dict["Standard"].items():
                group = ParameterGroup(group_name, "Standard", self)
                group._parameters = params
                standard_cat._groups.append(group)
            self._categories.append(standard_cat)
            
        # Andere Kategorien
        for cat_name, groups in categories_dict.items():
            if cat_name != "Standard":
                category = ParameterCategory(cat_name, self)
                for group_name, params in groups.items():
                    group = ParameterGroup(group_name, cat_name, self)
                    group._parameters = params
                    category._groups.append(group)
                self._categories.append(category)
                
        # Default-Kategorie immer zuletzt
        if "Default" in categories_dict:
            default_cat = ParameterCategory("Default", self)
            for group_name, params in categories_dict["Default"].items():
                group = ParameterGroup(group_name, "Default", self)
                group._parameters = params
                default_cat._groups.append(group)
            self._categories.append(default_cat)
    
    def _on_parameter_updated(self, name, value):
        """
        Callback für aktualisierte Parameter
        """
        self._parameter_model.updateParameter(name, value)
        self.parameterChanged.emit(name, value)
    
    def _on_parameter_write_complete(self, name, success):
        """
        Callback für abgeschlossenes Parameter-Schreiben
        """
        self.writeCompleted.emit(name, success)
        
        # Parameter aus der Schreibwarteschlange entfernen
        if name in self._write_queue:
            self._write_queue.remove(name)
            
        # Nächsten Parameter in der Warteschlange verarbeiten
        self._process_write_queue()
    
    def _process_write_queue(self):
        """
        Verarbeitet die Warteschlange für Parameter-Schreibvorgänge
        """
        if not self._write_queue or not self._drone_connector:
            return
            
        next_param = self._write_queue[0]
        param_data = self._parameter_model.getParameterByName(next_param)
        
        if param_data:
            self._drone_connector.write_parameter(
                next_param, 
                param_data.get("value", 0),
                param_data.get("type")
            )
    
    def _categorize_parameter(self, param_name):
        """
        Kategorisiert einen Parameter basierend auf seinem Namen
        """
        name_lower = param_name.lower()
        
        # Standard-Kategorien basierend auf QGroundControl
        if any(prefix in name_lower for prefix in ["wp_", "nav_", "rth_", "mission_"]):
            return "Navigation"
        elif any(prefix in name_lower for prefix in ["rc_", "radio_", "servo_"]):
            return "Radio"
        elif any(prefix in name_lower for prefix in ["pid_", "rate_", "att_", "ang_"]):
            return "Control"
        elif any(prefix in name_lower for prefix in ["compass_", "gps_", "imu_", "baro_"]):
            return "Sensors"
        elif any(prefix in name_lower for prefix in ["arm_", "disarm_", "failsafe_", "safety_"]):
            return "Safety"
        elif any(prefix in name_lower for prefix in ["log_", "serial_", "telem_"]):
            return "Logging"
        elif any(prefix in name_lower for prefix in ["camera_", "gimbal_", "mount_"]):
            return "Camera"
        elif any(prefix in name_lower for prefix in ["esc_", "mot_", "thr_"]):
            return "Motors"
        elif any(prefix in name_lower for prefix in ["batt_", "volt_", "curr_"]):
            return "Battery"
        elif any(prefix in name_lower for prefix in ["ahrs_", "ekf_", "ins_"]):
            return "AHRS"
        elif any(prefix in name_lower for prefix in ["arm_", "disarm_", "failsafe_"]):
            return "Arming"
        elif any(prefix in name_lower for prefix in ["sys_", "board_", "hardware_"]):
            return "System"
        else:
            return "Standard"
    
    def _categorize_group(self, param_name, category):
        """
        Kategorisiert einen Parameter in eine Gruppe innerhalb der Kategorie
        """
        name_lower = param_name.lower()
        
        # Gruppierung basierend auf Parameter-Namen
        if category == "Control":
            if "pid" in name_lower:
                return "PID"
            elif "rate" in name_lower:
                return "Rate"
            elif "att" in name_lower:
                return "Attitude"
            else:
                return "General"
        elif category == "Sensors":
            if "compass" in name_lower:
                return "Compass"
            elif "gps" in name_lower:
                return "GPS"
            elif "imu" in name_lower:
                return "IMU"
            else:
                return "General"
        else:
            return "Default"

    @Property(QObject, constant=True)
    def parameterModel(self):
        """Gibt das Parameter-Modell zurück"""
        return self._parameter_model

    @Property(list, notify=categoriesChanged)
    def categories(self):
        """Gibt die verfügbaren Kategorien zurück"""
        return self._categories

    @Property(bool)
    def refreshInProgress(self):
        """Gibt zurück, ob gerade ein Refresh läuft"""
        return self._refresh_in_progress

    @Slot()
    def refreshParameters(self):
        """
        Lädt alle Parameter neu vom Flugcontroller
        """
        if self._refresh_in_progress:
            print("[WARN] Parameter-Refresh bereits in Bearbeitung")
            return
            
        if not self._drone_connector:
            print("[ERROR] Kein DroneKit-Connector verfügbar")
            return
            
        if not self._drone_connector.is_connected():
            print("[ERROR] Keine Verbindung zum Flugcontroller")
            return
            
        print("Aktualisiere Parameter...")
        self._refresh_in_progress = True
        self.refreshStarted.emit()
        
        try:
            # Parameter vom Flugcontroller abrufen
            self._drone_connector.fetch_parameters()
        except Exception as e:
            print(f"[ERROR] Fehler beim Parameter-Refresh: {e}")
            self._refresh_in_progress = False
            self.refreshCompleted.emit(False)

    @Slot(str, float)
    def writeParameter(self, name, value):
        """
        Schreibt einen Parameter zum Flugcontroller
        """
        if not self._drone_connector:
            print(f"[ERROR] Kein DroneKit-Connector verfügbar für Parameter {name}")
            return
            
        if not self._drone_connector.is_connected():
            print(f"[ERROR] Keine Verbindung zum Flugcontroller für Parameter {name}")
            return
            
        print(f"[INFO] Schreibe Parameter {name} = {value}")
        self.writeStarted.emit(name)
        
        # Parameter zur Schreibwarteschlange hinzufügen
        if name not in self._write_queue:
            self._write_queue.append(name)
            
        # Parameter im lokalen Modell aktualisieren
        self._parameter_model.updateParameter(name, value)
        
        # Warteschlange verarbeiten
        self._process_write_queue()

    @Slot(str)
    def setFilterText(self, filter_text):
        """Setzt den Filtertext für die Parameter-Suche"""
        self._parameter_model.setFilterText(filter_text)

    @Slot(bool)
    def setShowModifiedOnly(self, show_modified_only):
        """Setzt, ob nur geänderte Parameter angezeigt werden sollen"""
        self._parameter_model.setShowModifiedOnly(show_modified_only)

    @Slot()
    def clearModified(self):
        """Löscht alle Markierungen für geänderte Parameter"""
        self._parameter_model.clearModified()

    @Slot(str, result=QObject)
    def getParameterByName(self, name):
        """Gibt einen Parameter anhand des Namens zurück"""
        return self._parameter_model.getParameterByName(name)

    @Slot(str, result='QVariant')  # QML-kompatibles Ergebnis
    def filter_parameters(self, search_string):
        """
        Filtert Parameter basierend auf einem Suchstring
        """
        if not search_string:
            return []
            
        results = []
        search_lower = search_string.lower()
        
        for param in self._parameter_model._parameters:
            name = param.get("name", "").lower()
            description = param.get("description", "").lower()
            category = param.get("category", "").lower()
            
            if (search_lower in name or 
                search_lower in description or 
                search_lower in category):
                results.append(param)
                
        return results

    @Slot(str, 'QVariant', result=bool)
    def set_parameter_value(self, name, value):
        """
        Setzt den Wert eines Parameters (QML-kompatibel)
        """
        try:
            # Parameter zum Flugcontroller schreiben
            self.writeParameter(name, float(value))
            return True
        except Exception as e:
            print(f"[ERROR] Fehler beim Setzen von Parameter {name}: {e}")
            return False

    # --- Erweiterte Features (QGroundControl-inspiriert) ---
    
    @Slot(str, result=bool)
    def saveToFile(self, filename):
        """Speichert alle Parameter in eine Datei"""
        try:
            if hasattr(self._drone_connector, 'save_parameters_to_file'):
                return self._drone_connector.save_parameters_to_file(filename)
            else:
                print("[ERROR] save_parameters_to_file nicht verfügbar")
                return False
        except Exception as e:
            print(f"[ERROR] Fehler beim Speichern: {e}")
            return False
    
    @Slot(str, result=bool)
    def loadFromFile(self, filename):
        """Lädt Parameter aus einer Datei"""
        try:
            if hasattr(self._drone_connector, 'load_parameters_from_file'):
                return self._drone_connector.load_parameters_from_file(filename)
            else:
                print("[ERROR] load_parameters_from_file nicht verfügbar")
                return False
        except Exception as e:
            print(f"[ERROR] Fehler beim Laden: {e}")
            return False
    
    @Slot()
    def resetAllToDefaults(self):
        """Setzt alle Parameter auf Standardwerte zurück"""
        print("[INFO] Reset aller Parameter auf Standardwerte")
        # TODO: Implementiere Reset-Funktionalität
        pass
    
    @Slot()
    def resetAllToVehicleConfiguration(self):
        """Setzt alle Parameter auf Fahrzeug-Konfiguration zurück"""
        print("[INFO] Reset aller Parameter auf Fahrzeug-Konfiguration")
        # TODO: Implementiere Reset-Funktionalität
        pass
    
    @Slot(str, str, result='QVariant')
    def buildDiffFromFile(self, filename):
        """Erstellt einen Diff zwischen aktuellen Parametern und einer Datei"""
        try:
            # TODO: Implementiere Diff-Funktionalität
            print(f"[INFO] Erstelle Diff für Datei: {filename}")
            return []
        except Exception as e:
            print(f"[ERROR] Fehler beim Erstellen des Diffs: {e}")
            return []
