from PySide6.QtCore import QObject, Signal, Slot
from .parameter_model import ParameterTableModel
from .logger import Logger

class ParameterManager(QObject):
    """Manages parameter data and updates"""
    
    # Signals
    parametersLoaded = Signal(list)  # Emits list of parameters
    parameterUpdated = Signal(str, float)  # Emits parameter name and value
    errorOccurred = Signal(str)  # Emits error message
    
    def __init__(self, parameter_model: ParameterTableModel, logger: Logger):
        super().__init__()
        self._parameter_model = parameter_model
        self._logger = logger
        self._mavlink_connection = None
        
    def set_connection(self, connection):
        """Set the MAVLink connection to use"""
        self._mavlink_connection = connection
        
    @Slot()
    def load_parameters(self):
        """Load parameters from the flight controller"""
        if not self._mavlink_connection:
            error_msg = "[ERR] Not connected to FC!"
            self._logger.addLog(error_msg)
            self.errorOccurred.emit(error_msg)
            return
            
        try:
            self._logger.addLog("[LOAD] Loading parameters from FC...")
            params = []
            self._mavlink_connection.param_fetch_all()
            
            while True:
                msg = self._mavlink_connection.recv_match(type='PARAM_VALUE', blocking=True, timeout=2)
                if not msg:
                    break
                    
                param = {
                    "name": msg.param_id,
                    "value": msg.param_value,
                    "defaultValue": "",  # Optional: add from XML
                    "unit": "",
                    "options": "",
                    "desc": ""
                }
                params.append(param)
                self.parameterUpdated.emit(param["name"], param["value"])
                
            if self._parameter_model:
                self._parameter_model.set_parameters(params)
                self.parametersLoaded.emit(params)
            self._logger.addLog(f"[OK] {len(params)} parameters loaded")
            
        except Exception as e:
            error_msg = f"[ERR] Error loading parameters: {str(e)}"
            self._logger.addLog(error_msg)
            self.errorOccurred.emit(error_msg)
            
    @Slot(object)
    def handle_parameter(self, msg):
        """Handle parameter message"""
        if not self._parameter_model:
            return
            
        try:
            param = {
                "name": msg.param_id,
                "value": msg.param_value,
                "defaultValue": "",
                "unit": "",
                "options": "",
                "desc": ""
            }
            self._parameter_model.add_parameter(param)
            self.parameterUpdated.emit(param["name"], param["value"])
        except Exception as e:
            error_msg = f"[ERR] Error handling parameter: {str(e)}"
            self._logger.addLog(error_msg)
            self.errorOccurred.emit(error_msg)
            
    @Slot(str, float)
    def set_parameter(self, name: str, value: float):
        """Set a parameter on the flight controller"""
        if not self._mavlink_connection:
            error_msg = "[ERR] Not connected to FC!"
            self._logger.addLog(error_msg)
            self.errorOccurred.emit(error_msg)
            return False
            
        try:
            self._mavlink_connection.param_set_send(name, value)
            self._logger.addLog(f"[OK] Parameter {name} set to {value}")
            self.parameterUpdated.emit(name, value)
            return True
        except Exception as e:
            error_msg = f"[ERR] Error setting parameter {name}: {str(e)}"
            self._logger.addLog(error_msg)
            self.errorOccurred.emit(error_msg)
            return False 