"""
DroneKit Parameter ViewModel für RZGCS
Stellt Parameter-Management-Funktionen aus DroneKit für die QML-UI bereit
"""

from PySide6.QtCore import QObject, Signal, Slot, Property, QAbstractListModel, Qt, QModelIndex
from typing import List, Dict, Any, Optional
import json
import time

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
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._parameters = []
        self._filtered_parameters = []
        self._filter_text = ""
        self._show_modified_only = False
        self._modified_parameters = set()
        
    def rowCount(self, parent=QModelIndex()):
        """Gibt die Anzahl der Parameter zurück"""
        if parent.isValid():
            return 0
        return len(self._filtered_parameters)
        
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
            return parameter.get("category", "Allgemein")
            
        return None
        
    def roleNames(self):
        """Gibt die Rollennamen für QML zurück"""
        return {
            self.NameRole: b"name",
            self.ValueRole: b"value",
            self.TypeRole: b"paramType",
            self.DescriptionRole: b"description",
            self.ReadOnlyRole: b"readOnly",
            self.CategoryRole: b"category"
        }
        
    def setParameters(self, parameters: List[Dict[str, Any]]):
        """Setzt die Parameter-Liste"""
        self.beginResetModel()
        self._parameters = parameters
        self._applyFilter()
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
        
    def _applyFilter(self):
        """Wendet den Filter auf die Parameter an"""
        self.beginResetModel()
        
        # Filter anwenden
        self._filtered_parameters = []
        for param in self._parameters:
            name = param.get("name", "").lower()
            description = param.get("description", "").lower()
            category = param.get("category", "").lower()
            
            # Text-Filter anwenden
            if self._filter_text:
                filter_text = self._filter_text.lower()
                if not (filter_text in name or filter_text in description or filter_text in category):
                    continue
                    
            # Filter für geänderte Parameter anwenden
            if self._show_modified_only and name not in self._modified_parameters:
                continue
                
            self._filtered_parameters.append(param)
            
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
                        self.dataChanged.emit(index, index, [self.ValueRole])
                        break
                break


class DroneKitParameterViewModel(QObject):
    """
    ViewModel für Parameter-Management mit DroneKit
    """
    
    # Signale
    parametersChanged = Signal()
    parameterChanged = Signal(str, float)  # name, value
    refreshStarted = Signal()
    refreshCompleted = Signal(bool)  # success
    writeStarted = Signal(str)  # param_name
    writeCompleted = Signal(str, bool)  # param_name, success
    
    def __init__(self, drone_connector=None, parent=None):
        """Initialisiert das ViewModel mit optionaler Verbindung zum Connector"""
        super().__init__(parent)
        self._drone_connector = drone_connector
        
        # Parameter-Modell
        self._parameter_model = ParameterListModel(self)
        self._categories = []
        self._last_refresh_time = 0
        self._refresh_in_progress = False
        self._write_queue = []
        
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
            param_list = []
            categories = set()
            
            # Parameter verarbeiten
            for name, param_dict in parameters.items():
                value = param_dict.get("value", 0)
                param_type = param_dict.get("type", "float")
                description = param_dict.get("description", "")
                read_only = param_dict.get("read_only", False)
                category = self._categorize_parameter(name)
                
                categories.add(category)
                
                param_list.append({
                    "name": name,
                    "value": value,
                    "type": param_type,
                    "description": description,
                    "read_only": read_only,
                    "category": category
                })
            
            # Sortiere Parameter nach Namen
            param_list.sort(key=lambda x: x["name"])
            
            # Setze Parameter im Modell
            self._parameter_model.setParameters(param_list)
            
            # Kategorien aktualisieren
            self._categories = sorted(list(categories))
            
            # Status aktualisieren und Signal emittieren
            self._refresh_in_progress = False
            self._last_refresh_time = time.time()
            self.parametersChanged.emit()
            self.refreshCompleted.emit(True)
            
            print(f"{len(param_list)} Parameter empfangen in {len(categories)} Kategorien")
            
        except Exception as e:
            print(f"Fehler bei der Verarbeitung der Parameter: {e}")
            self._refresh_in_progress = False
            self.refreshCompleted.emit(False)
    
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
            
        # Nächsten Parameter schreiben
        param_name = self._write_queue[0]
        param = self._parameter_model.getParameterByName(param_name)
        
        if param:
            self.writeStarted.emit(param_name)
            value = param.get("value", 0)
            self._drone_connector.write_parameter(param_name, value)
    
    def _categorize_parameter(self, param_name):
        """
        Ordnet einen Parameter anhand des Namens einer Kategorie zu
        """
        param_prefixes = {
            "ARMING_": "Armierung",
            "BATT_": "Batterie",
            "BRD_": "Board",
            "CAN_": "CAN Bus",
            "COMPASS_": "Kompass",
            "EK2_": "EKF2",
            "EK3_": "EKF3",
            "FENCE_": "Geo-Fence",
            "FLTMODE": "Flugmodi",
            "GPS_": "GPS",
            "INS_": "IMU",
            "LOG_": "Logging",
            "MIS_": "Mission",
            "MOT_": "Motor",
            "PILOT_": "Pilot",
            "RC": "Fernbedienung",
            "SERVO": "Servos",
            "SR0_": "Telemetrie",
            "SR1_": "Telemetrie",
            "SR2_": "Telemetrie",
            "SR3_": "Telemetrie"
        }
        
        # Nach Präfix suchen
        for prefix, category in param_prefixes.items():
            if param_name.startswith(prefix):
                return category
                
        return "Allgemein"
    
    # --- Properties ---
    
    @Property(QObject, constant=True)
    def parameterModel(self):
        """Gibt das Parameter-Modell zurück"""
        return self._parameter_model
    
    @Property(list, notify=parametersChanged)
    def categories(self):
        """Gibt die verfügbaren Kategorien zurück"""
        return self._categories
    
    @Property(bool)
    def refreshInProgress(self):
        """Gibt zurück, ob gerade eine Aktualisierung läuft"""
        return self._refresh_in_progress
    
    # --- Slots ---
    
    @Slot()
    def refreshParameters(self):
        """
        Aktualisiert die Parameter vom Vehicle
        """
        if not self._drone_connector or not self._drone_connector.is_connected():
            print("Keine Verbindung zum Vehicle")
            self.refreshCompleted.emit(False)
            return
            
        # Prüfen, ob die letzte Aktualisierung weniger als 2 Sekunden her ist
        if time.time() - self._last_refresh_time < 2.0 and self._parameter_model.rowCount() > 0:
            print("Parameter wurden kürzlich aktualisiert")
            self.refreshCompleted.emit(True)
            return
            
        print("Aktualisiere Parameter...")
        self._refresh_in_progress = True
        self.refreshStarted.emit()
        
        try:
            # Parameter vom Vehicle abrufen
            self._drone_connector.fetch_parameters()
            
        except Exception as e:
            print(f"Fehler beim Aktualisieren der Parameter: {e}")
            self._refresh_in_progress = False
            self.refreshCompleted.emit(False)
    
    @Slot(str, float)
    def writeParameter(self, name, value):
        """
        Schreibt einen Parameter-Wert zum Vehicle
        
        :param name: Name des Parameters
        :param value: Neuer Wert des Parameters
        """
        if not self._drone_connector or not self._drone_connector.is_connected():
            print(f"Keine Verbindung zum Vehicle, kann Parameter {name} nicht schreiben")
            self.writeCompleted.emit(name, False)
            return
            
        # Parameter im Modell aktualisieren
        self._parameter_model.updateParameter(name, value)
        
        # Parameter zur Schreibwarteschlange hinzufügen
        if name not in self._write_queue:
            self._write_queue.append(name)
            
            # Wenn dies der einzige Parameter in der Warteschlange ist, sofort verarbeiten
            if len(self._write_queue) == 1:
                self._process_write_queue()
                
    @Slot(str)
    def setFilterText(self, filter_text):
        """Setzt den Filtertext für die Parameter"""
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
        """Filtert die Parameter anhand einer Suchzeichenkette
        
        Diese Methode wird von der QML UI aufgerufen und gibt ein QML-kompatibles
        Ergebnis zurück.
        
        :param search_string: Die Suchzeichenkette
        :return: Eine gefilterte Liste von Parametern
        """
        print(f"DroneKitParameterViewModel: Filtere Parameter mit '{search_string}'")
        
        # Den Filter im Modell anwenden
        self._parameter_model.setFilterText(search_string)
        
        # Gefilterte Parameter zurückgeben
        # Für die QML ListView müssen wir das Modell selbst zurückgeben
        return self._parameter_model
    
    @Slot(str, 'QVariant', result=bool)
    def set_parameter_value(self, name, value):
        """Setzt den Wert eines Parameters
        
        Diese Methode wird von der QML UI aufgerufen und aktualisiert
        sowohl das lokale Modell als auch den Parameter im Fahrzeug.
        
        :param name: Name des Parameters
        :param value: Neuer Wert des Parameters (als String oder Zahl)
        :return: True bei Erfolg, False bei Fehler
        """
        print(f"DroneKitParameterViewModel: Setze Parameter {name}={value}")
        
        # Versuchen, den Wert korrekt zu konvertieren
        try:
            # Zuerst versuchen wir eine Float-Konvertierung
            float_value = float(value)
            
            # Parameter im lokalen Modell aktualisieren
            self._parameter_model.updateParameter(name, float_value)
            
            # Parameter ans Fahrzeug senden (falls verbunden)
            self.writeParameter(name, float_value)
            
            return True
            
        except (ValueError, TypeError) as e:
            print(f"Fehler beim Konvertieren des Parameter-Werts: {e}")
            return False
