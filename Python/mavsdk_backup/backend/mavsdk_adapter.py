"""
MAVSDK-Adapter für RZGCS
Verbindet den MAVSDK-Connector mit der bestehenden Anwendung
"""

from PySide6.QtCore import QObject, Signal, Slot
from .mavsdk_connector import MAVSDKConnector
from .mavsdk_sensor_manager import MAVSDKSensorManager
from .logger import Logger


class MAVSDKAdapter(QObject):
    """Adapter-Klasse, die MAVSDK mit der bestehenden Anwendung verbindet"""
    
    # Signale aus dem MAVLink-System
    connection_established = Signal()
    connection_lost = Signal()
    error_occurred = Signal(str)
    
    def __init__(self, logger: Logger):
        """Initialisiert den MAVSDK-Adapter
        
        Args:
            logger: Logger-Instanz für die Protokollierung
        """
        super().__init__()
        self._logger = logger
        
        # MAVSDK-Komponenten erstellen
        self._connector = MAVSDKConnector(self._logger)
        self._sensor_manager = MAVSDKSensorManager(self._logger)
        
        # Signale verbinden
        self._connector.connected.connect(self._handle_connected)
        self._connector.disconnected.connect(self._handle_disconnected)
        self._connector.error_occurred.connect(self._handle_error)
        
        # Telemetrie-Signale mit dem SensorManager verbinden
        self._connector.position_received.connect(self._sensor_manager.handle_position)
        self._connector.attitude_received.connect(self._sensor_manager.handle_attitude)
        self._connector.battery_received.connect(self._sensor_manager.handle_battery)
        self._connector.gps_info_received.connect(self._sensor_manager.handle_gps_info)
        self._connector.actuator_output_status_received.connect(self._sensor_manager.handle_actuator_output)
        
        self._logger.addLog("MAVSDK-Adapter initialisiert")
    
    def get_connector(self):
        """Gibt den MAVSDK-Connector zurück
        
        Returns:
            MAVSDKConnector: Die Connector-Instanz
        """
        return self._connector
    
    def get_sensor_manager(self):
        """Gibt den MAVSDK-SensorManager zurück
        
        Returns:
            MAVSDKSensorManager: Die SensorManager-Instanz
        """
        return self._sensor_manager
    
    def initialize_sensor_model(self, model):
        """Initialisiert das Sensor-Modell
        
        Args:
            model: Das SensorViewModel
        """
        self._sensor_manager.initialize_model(model)
    
    @Slot()
    def _handle_connected(self):
        """Behandelt das Verbindungshergestellt-Signal"""
        self._sensor_manager.set_connected()
        self.connection_established.emit()
    
    @Slot()
    def _handle_disconnected(self):
        """Behandelt das Verbindungsverloren-Signal"""
        self._sensor_manager.set_disconnected()
        self.connection_lost.emit()
    
    @Slot(str)
    def _handle_error(self, error_msg):
        """Behandelt Fehlermeldungen
        
        Args:
            error_msg: Die Fehlermeldung
        """
        self.error_occurred.emit(error_msg)
