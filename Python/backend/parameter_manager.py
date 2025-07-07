"""
Parameter Manager für RZGCS - Lädt und verwaltet MAVLink-Parameter
"""

import fnmatch
import math
import time
import struct
from typing import Dict, List, Optional, Any
from PySide6.QtCore import QObject, Signal, Property, Slot
from pymavlink import mavutil

class ParameterManager(QObject):
    """
    Parameter Manager für MAVLink-Parameter mit QML-Integration
    """
    
    # Signals für QML
    parametersLoaded = Signal(int)  # Anzahl geladener Parameter
    parameterUpdated = Signal(str, float, str)  # name, value, type
    parameterSet = Signal(str, float, bool)  # name, value, success
    loadingStatusChanged = Signal(bool, str)  # loading, status_text
    errorOccurred = Signal(str)  # error_message
    
    def __init__(self):
        super().__init__()
        self._parameters: Dict[str, Dict[str, Any]] = {}
        self._is_loading = False
        self._loading_status = "Bereit"
        self._mavlink_connection = None
        self._parameter_count = 0
        self._loaded_count = 0
        
        # Parameter die nicht von Dateien geladen werden sollen
        self.exclude_load = [
            'ARSPD_OFFSET',
            'CMD_INDEX',
            'CMD_TOTAL',
            'FENCE_TOTAL',
            'FORMAT_VERSION',
            'GND_ABS_PRESS',
            'GND_TEMP',
            'LOG_LASTFILE',
            'MIS_TOTAL',
            'SYSID_SW_MREV',
            'SYS_NUM_RESETS',
        ]
        
        self.mindelta = 0.000001
        print("[OK]ParameterManager initialisiert")
    
    def set_mavlink_connection(self, connection):
        """MAVLink-Verbindung setzen"""
        self._mavlink_connection = connection
        print(f"[OK]ParameterManager: MAVLink-Verbindung gesetzt: {connection}")
    
    @Property(bool, notify=loadingStatusChanged)
    def isLoading(self):
        return self._is_loading
    
    @Property(str, notify=loadingStatusChanged)
    def loadingStatus(self):
        return self._loading_status
    
    @Property(int, notify=parametersLoaded)
    def parameterCount(self):
        return self._parameter_count
    
    @Property(int, notify=parametersLoaded)
    def loadedCount(self):
        return self._loaded_count
        
    @Slot()
    def loadAllParameters(self):
        """Alle Parameter vom Flugcontroller laden"""
        if not self._mavlink_connection:
            self.errorOccurred.emit("Keine MAVLink-Verbindung verfügbar")
            return False
        
        self._is_loading = True
        self._loading_status = "Lade Parameter..."
        self.loadingStatusChanged.emit(True, "Lade Parameter...")
        
        try:
            print("[OK]ParameterManager: Starte Parameter-Load...")
            
            # Parameter-Liste anfordern
            self._mavlink_connection.param_list_send()
            
            # Parameter empfangen
            start_time = time.time()
            timeout = 30  # 30 Sekunden Timeout
            
            while time.time() - start_time < timeout:
                msg = self._mavlink_connection.recv_match(type='PARAM_VALUE', blocking=False)
                if msg is None:
                    time.sleep(0.1)
                    continue
                
                param_id = msg.param_id.decode('utf-8').rstrip('\x00')
                param_value = msg.param_value
                param_type = msg.param_type
                
                # Parameter speichern
                self._parameters[param_id] = {
                    'value': param_value,
                    'type': param_type,
                    'index': msg.param_index,
                    'count': msg.param_count
                }
                
                self._parameter_count = msg.param_count
                self._loaded_count = msg.param_index + 1
                
                # Status aktualisieren
                progress = (self._loaded_count / self._parameter_count) * 100
                self._loading_status = f"Lade Parameter... {self._loaded_count}/{self._parameter_count} ({progress:.1f}%)"
                self.loadingStatusChanged.emit(True, self._loading_status)
                
                # Signal für QML
                self.parameterUpdated.emit(param_id, param_value, self._get_param_type_name(param_type))
                
                # Prüfen ob alle Parameter geladen wurden
                if self._loaded_count >= self._parameter_count:
                    break
            
            # Loading beenden
            self._is_loading = False
            self._loading_status = f"Parameter geladen: {self._loaded_count}"
            self.loadingStatusChanged.emit(False, self._loading_status)
            
            self.parametersLoaded.emit(self._loaded_count)
            print(f"[OK]ParameterManager: {self._loaded_count} Parameter geladen")
            return True
            
        except Exception as e:
            self._is_loading = False
            self._loading_status = f"Fehler: {str(e)}"
            self.loadingStatusChanged.emit(False, self._loading_status)
            self.errorOccurred.emit(f"Fehler beim Laden der Parameter: {str(e)}")
            print(f"[ERROR]ParameterManager: Fehler beim Laden: {e}")
            return False
            
    @Slot(str, float)
    def setParameter(self, name: str, value: float):
        """Parameter setzen"""
        if not self._mavlink_connection:
            self.errorOccurred.emit("Keine MAVLink-Verbindung verfügbar")
            self.parameterSet.emit(name, value, False)
            return False
            
        try:
            # Parameter-Typ ermitteln
            param_type = None
            if name in self._parameters:
                param_type = self._parameters[name]['type']
            
            # Parameter setzen
            success = self._mavset(name, value, param_type)
            
            if success:
                # Lokalen Parameter aktualisieren
                if name in self._parameters:
                    self._parameters[name]['value'] = value
                else:
                    self._parameters[name] = {
                        'value': value,
                        'type': param_type or mavutil.mavlink.MAV_PARAM_TYPE_REAL32,
                        'index': 0,
                        'count': self._parameter_count
                    }
                
                self.parameterUpdated.emit(name, value, self._get_param_type_name(param_type))
                print(f"[OK]ParameterManager: Parameter {name} auf {value} gesetzt")
            
            self.parameterSet.emit(name, value, success)
            return success
            
        except Exception as e:
            self.errorOccurred.emit(f"Fehler beim Setzen von {name}: {str(e)}")
            self.parameterSet.emit(name, value, False)
            print(f"[ERROR]ParameterManager: Fehler beim Setzen von {name}: {e}")
            return False
    
    def _mavset(self, name: str, value: float, param_type=None, retries=3):
        """Parameter über MAVLink setzen"""
        got_ack = False
        
        if param_type is not None and param_type != mavutil.mavlink.MAV_PARAM_TYPE_REAL32:
            # Als Float für das Senden kodieren
            if param_type == mavutil.mavlink.MAV_PARAM_TYPE_UINT8:
                vstr = struct.pack(">xxxB", int(value))
            elif param_type == mavutil.mavlink.MAV_PARAM_TYPE_INT8:
                vstr = struct.pack(">xxxb", int(value))
            elif param_type == mavutil.mavlink.MAV_PARAM_TYPE_UINT16:
                vstr = struct.pack(">xxH", int(value))
            elif param_type == mavutil.mavlink.MAV_PARAM_TYPE_INT16:
                vstr = struct.pack(">xxh", int(value))
            elif param_type == mavutil.mavlink.MAV_PARAM_TYPE_UINT32:
                vstr = struct.pack(">I", int(value))
            elif param_type == mavutil.mavlink.MAV_PARAM_TYPE_INT32:
                vstr = struct.pack(">i", int(value))
            else:
                print(f"Parameter-Typ {param_type} für {name} nicht unterstützt")
                return False
            numeric_value, = struct.unpack(">f", vstr)
        else:
            if isinstance(value, str) and value.lower().startswith('0x'):
                numeric_value = int(value[2:], 16)
            else:
                numeric_value = float(value)
        
        while retries > 0 and not got_ack:
            retries -= 1
            self._mavlink_connection.param_set_send(name.upper(), numeric_value, parm_type=param_type)
            tstart = time.time()
            while time.time() - tstart < 1:
                ack = self._mavlink_connection.recv_match(type='PARAM_VALUE', blocking=False)
                if ack is None:
                    time.sleep(0.1)
                    continue
                if str(name).upper() == str(ack.param_id).upper():
                    got_ack = True
                    break
        
        if not got_ack:
            print(f"Timeout beim Setzen von {name} auf {numeric_value}")
            return False
        return True
    
    def _get_param_type_name(self, param_type):
        """Parameter-Typ als String zurückgeben"""
        if param_type is None:
            return "UNKNOWN"
        
        type_names = {
            mavutil.mavlink.MAV_PARAM_TYPE_UINT8: "UINT8",
            mavutil.mavlink.MAV_PARAM_TYPE_INT8: "INT8",
            mavutil.mavlink.MAV_PARAM_TYPE_UINT16: "UINT16",
            mavutil.mavlink.MAV_PARAM_TYPE_INT16: "INT16",
            mavutil.mavlink.MAV_PARAM_TYPE_UINT32: "UINT32",
            mavutil.mavlink.MAV_PARAM_TYPE_INT32: "INT32",
            mavutil.mavlink.MAV_PARAM_TYPE_REAL32: "REAL32"
        }
        return type_names.get(param_type, f"TYPE_{param_type}")
    
    @Slot(str)
    def saveToFile(self, filename: str):
        """Parameter in Datei speichern"""
        try:
            with open(filename, 'w') as f:
                keys = sorted(self._parameters.keys())
                count = 0
                for param_name in keys:
                    param_data = self._parameters[param_name]
                    value = param_data['value']
                    if isinstance(value, float):
                        f.write(f"{param_name:<16} {value}\n")
                    else:
                        f.write(f"{param_name:<16} {str(value)}\n")
                    count += 1
            
            print(f"[OK]ParameterManager: {count} Parameter in {filename} gespeichert")
            return True
            
        except Exception as e:
            self.errorOccurred.emit(f"Fehler beim Speichern: {str(e)}")
            print(f"[ERROR]ParameterManager: Fehler beim Speichern: {e}")
            return False
    
    @Slot(str)
    def loadFromFile(self, filename: str):
        """Parameter aus Datei laden"""
        try:
            with open(filename, 'r') as f:
                count = 0
                for line in f:
                    line = line.strip()
                    if not line or line[0] == "#":
                        continue
                    
                    line = line.replace(',', ' ')
                    parts = line.split()
                    if len(parts) != 2:
                        print(f"Ungültige Zeile: {line}")
                        continue
                    
                    param_name = parts[0]
                    value_str = parts[1].strip()
                    
                    # Parameter die nicht geladen werden sollen
                    if param_name in self.exclude_load:
                        continue
                    
                    # Wert konvertieren
                    if value_str.lower().startswith('0x'):
                        value = int(value_str[2:], 16)
                    else:
                        value = float(value_str)
                    
                    # Parameter setzen
                    if self.setParameter(param_name, value):
                        count += 1
            
            print(f"[OK]ParameterManager: {count} Parameter aus {filename} geladen")
            return True
            
        except Exception as e:
            self.errorOccurred.emit(f"Fehler beim Laden: {str(e)}")
            print(f"[ERROR]ParameterManager: Fehler beim Laden: {e}")
            return False 
    
    @Slot(str)
    def filterParameters(self, filter_text: str):
        """Parameter nach Filter-Text filtern"""
        filtered_params = {}
        filter_upper = filter_text.upper()
        
        for param_name, param_data in self._parameters.items():
            if filter_upper in param_name.upper():
                filtered_params[param_name] = param_data
        
        return filtered_params
    
    def getParameter(self, name: str) -> Optional[Dict[str, Any]]:
        """Parameter nach Name abrufen"""
        return self._parameters.get(name)
    
    def getAllParameters(self) -> Dict[str, Dict[str, Any]]:
        """Alle Parameter zurückgeben"""
        return self._parameters.copy()
    
    @Slot()
    def clearParameters(self):
        """Alle Parameter löschen"""
        self._parameters.clear()
        self._parameter_count = 0
        self._loaded_count = 0
        self.parametersLoaded.emit(0)
        print("[OK]ParameterManager: Alle Parameter gelöscht")
    
    def getParameterList(self) -> List[Dict[str, Any]]:
        """Parameter als Liste für QML zurückgeben"""
        param_list = []
        for name, data in sorted(self._parameters.items()):
            param_list.append({
                'name': name,
                'value': data['value'],
                'type': self._get_param_type_name(data['type']),
                'index': data['index']
            })
        return param_list 