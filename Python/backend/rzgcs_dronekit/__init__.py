"""
DroneKit-Python Integration für RZGCS
Ground Control Station mit DroneKit-Python Unterstützung
"""

# Python 3.13 Kompatibilitätsfix
import collections.abc
import collections
if not hasattr(collections, 'MutableMapping'):
    collections.MutableMapping = collections.abc.MutableMapping

# Keine direkten Imports, um zirkuläre Abhängigkeiten zu vermeiden
# Stattdessen werden Module dynamisch importiert wenn benötigt

__version__ = "1.0.0"
__author__ = "RZGCS Team"

__all__ = [
    'DroneKitConnector',
    'DroneKitVehicleManager', 
    'DroneKitTelemetryHandler',
    'DroneKitMissionHandler',
    'DroneKitControlHandler',
    'DroneKitParameterManager',
    'DroneKitConnectionManager',
    'DroneKitUtils'
]

# Helper-Funktion für lazy imports
def get_class(class_name):
    """Dynamischer Import von Klassen aus diesem Modul"""
    if class_name == 'DroneKitConnector':
        from .connector import DroneKitConnector
        return DroneKitConnector
    elif class_name == 'DroneKitVehicleManager':
        from .vehicle_manager import DroneKitVehicleManager
        return DroneKitVehicleManager
    elif class_name == 'DroneKitTelemetryHandler':
        from .telemetry_handler import DroneKitTelemetryHandler
        return DroneKitTelemetryHandler
    elif class_name == 'DroneKitMissionHandler':
        from .mission_handler import DroneKitMissionHandler
        return DroneKitMissionHandler
    elif class_name == 'DroneKitControlHandler':
        from .control_handler import DroneKitControlHandler
        return DroneKitControlHandler
    elif class_name == 'DroneKitParameterManager':
        from .parameter_manager import DroneKitParameterManager
        return DroneKitParameterManager
    elif class_name == 'DroneKitConnectionManager':
        from .connection_manager import DroneKitConnectionManager
        return DroneKitConnectionManager
    elif class_name == 'DroneKitUtils':
        from .utils import DroneKitUtils
        return DroneKitUtils
    else:
        raise ImportError(f"Klasse {class_name} nicht gefunden")