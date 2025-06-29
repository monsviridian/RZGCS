"""
QML-Kompatibilitäts-Aliase für RZGCS

Diese Datei definiert Aliase für verschiedene ViewModels und Connector-Klassen,
um Kompatibilität mit vorhandenen QML-Dateien zu gewährleisten.
"""

from PySide6.QtQml import QQmlEngine, QQmlContext


def register_frontend_qml_aliases(engine: QQmlEngine, components: dict):
    """
    Registriert Aliase für alle Frontend-Komponenten in der QML-Engine.
    
    Args:
        engine: Die QML-Engine
        components: Dictionary mit Komponenten, die registriert werden sollen
            - 'serial_connector': Der SerialConnector (DroneKit oder MAVLink)
            - 'sensor_viewmodel': Das SensorViewModel
            - 'mission_planner_viewmodel': Das MissionPlannerViewModel
            - 'message_manager': Der MessageManager
    """
    # Registriere Haupt-Komponenten (falls noch nicht registriert)
    if 'serial_connector' in components:
        engine.rootContext().setContextProperty("serialConnector", components['serial_connector'])
    
    if 'sensor_viewmodel' in components:
        engine.rootContext().setContextProperty("sensorViewModel", components['sensor_viewmodel'])
    
    if 'mission_planner_viewmodel' in components:
        engine.rootContext().setContextProperty("flightViewController", components['mission_planner_viewmodel'])
    
    if 'message_manager' in components:
        engine.rootContext().setContextProperty("messageManager", components['message_manager'])
    
    # Registriere Kompatibilitäts-Aliase für ältere QML-Dateien
    
    # Verbindungs-Aliase
    if 'serial_connector' in components:
        # Alias für SerialConnector
        engine.rootContext().setContextProperty("connectionViewModel", components['serial_connector'])
        engine.rootContext().setContextProperty("connectorViewModel", components['serial_connector'])
        engine.rootContext().setContextProperty("droneConnector", components['serial_connector'])
    
    # Sensor-Daten-Aliase
    if 'sensor_viewmodel' in components:
        # Aliase für SensorViewModel
        engine.rootContext().setContextProperty("parameterModel", components['sensor_viewmodel'])
        engine.rootContext().setContextProperty("telemetryViewModel", components['sensor_viewmodel'])
    
    # Mission-Aliase
    if 'mission_planner_viewmodel' in components:
        # Aliase für MissionPlannerViewModel
        engine.rootContext().setContextProperty("missionPlannerViewModel", components['mission_planner_viewmodel'])
        engine.rootContext().setContextProperty("missionViewModel", components['mission_planner_viewmodel'])
    
    # Nachrichten-Aliase
    if 'message_manager' in components:
        # Alias für MessageManager
        engine.rootContext().setContextProperty("logViewModel", components['message_manager'])
        engine.rootContext().setContextProperty("statusViewModel", components['message_manager'])

    print("Frontend-Kompatibilitäts-Aliase für QML erfolgreich registriert")
