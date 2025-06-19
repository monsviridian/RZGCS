#!/usr/bin/env python3
"""
DroneViewModel - ViewModel für die Drohnensteuerung im MVVM-Pattern

Dieser ViewModel stellt die Verbindung zwischen der UI und dem EnhancedMAVSDKConnector her
und implementiert die entsprechende Geschäftslogik.
"""

from PySide6.QtCore import QObject, Signal, Slot, Property, QTimer

from backend.enhanced_mavsdk_connector import EnhancedMAVSDKConnector
from backend.logger import Logger


class DroneViewModel(QObject):
    """ViewModel für die Drohnensteuerung"""
    
    # Signale für die UI
    connectionStateChanged = Signal(bool)
    armedStateChanged = Signal(bool)
    flightModeChanged = Signal(str)
    gpsInfoChanged = Signal(dict)
    batteryChanged = Signal(dict)
    attitudeChanged = Signal(dict)
    headingChanged = Signal(float)
    positionChanged = Signal(dict)
    homePositionChanged = Signal(dict)
    messageReceived = Signal(str)
    errorOccurred = Signal(str)
    
    def __init__(self, logger: Logger, parent=None):
        """Initialisierung des DroneViewModel"""
        super().__init__(parent)
        
        # Logger
        self._logger = logger
        
        # MAVSDK-Connector
        self._connector = EnhancedMAVSDKConnector(logger)
        
        # Verbindungsstatus
        self._is_connected = False
        self._is_armed = False
        self._flight_mode = "UNBEKANNT"
        self._gps_info = {"num_satellites": 0, "fix_type": 0}
        self._battery_info = {"remaining_percent": 0.0, "voltage_v": 0.0, "current_a": 0.0}
        self._attitude = {"roll_deg": 0.0, "pitch_deg": 0.0, "yaw_deg": 0.0}
        self._position = {
            "latitude_deg": 0.0,
            "longitude_deg": 0.0,
            "absolute_altitude_m": 0.0,
            "relative_altitude_m": 0.0
        }
        self._home_position = {
            "latitude_deg": 0.0,
            "longitude_deg": 0.0,
            "absolute_altitude_m": 0.0,
            "relative_altitude_m": 0.0
        }
        
        # Signale verbinden
        self._connect_signals()
    
    def _connect_signals(self):
        """Verbindet die Signale des Connectors mit den Slots des ViewModels"""
        # Verbindungsstatus
        self._connector.connection_established.connect(self._on_connected)
        self._connector.connection_lost.connect(self._on_disconnected)
        self._connector.error_occurred.connect(self._on_error_occurred)
        
        # Telemetrie
        self._connector.armed_changed.connect(self._on_armed_changed)
        self._connector.flight_mode_changed.connect(self._on_flight_mode_changed)
        self._connector.gps_info_changed.connect(self._on_gps_info_changed)
        self._connector.battery_changed.connect(self._on_battery_changed)
        self._connector.attitude_changed.connect(self._on_attitude_changed)
        self._connector.heading_changed.connect(self._on_heading_changed)
        self._connector.position_changed.connect(self._on_position_changed)
        self._connector.home_position_changed.connect(self._on_home_position_changed)
        self._connector.statustext_received.connect(self._on_statustext_received)
    
    # Properties für die UI
    
    def is_connected(self) -> bool:
        """Gibt zurück, ob eine Verbindung zur Drohne besteht"""
        return self._is_connected
    
    def is_armed(self) -> bool:
        """Gibt zurück, ob die Drohne armiert ist"""
        return self._is_armed
    
    def flight_mode(self) -> str:
        """Gibt den aktuellen Flugmodus zurück"""
        return self._flight_mode
    
    def gps_info(self) -> dict:
        """Gibt die GPS-Informationen zurück"""
        return self._gps_info
    
    def battery_info(self) -> dict:
        """Gibt die Batterie-Informationen zurück"""
        return self._battery_info
    
    def attitude(self) -> dict:
        """Gibt die Lage der Drohne zurück"""
        return self._attitude
    
    def heading(self) -> float:
        """Gibt das Heading der Drohne zurück"""
        return self._attitude["yaw_deg"]
    
    def position(self) -> dict:
        """Gibt die Position der Drohne zurück"""
        return self._position
    
    def home_position(self) -> dict:
        """Gibt die Home-Position der Drohne zurück"""
        return self._home_position
    
    # Properties für QML
    connectionState = Property(bool, is_connected, notify=connectionStateChanged)
    armedState = Property(bool, is_armed, notify=armedStateChanged)
    flightMode = Property(str, flight_mode, notify=flightModeChanged)
    
    # Slots für die UI
    
    @Slot(str, int)
    def connect_serial(self, port: str, baudrate: int) -> bool:
        """
        Verbindet mit einer Drohne über einen seriellen Port
        
        Args:
            port: COM-Port oder Device (z.B. COM3, /dev/ttyACM0)
            baudrate: Baudrate (z.B. 57600, 115200)
            
        Returns:
            bool: True, wenn die Verbindung erfolgreich gestartet wurde
        """
        self._logger.addLog(f"[INFO] Verbinde mit {port} bei {baudrate} Baud...")
        return self._connector.connect_serial(port, baudrate)
    
    @Slot()
    def disconnect(self) -> bool:
        """
        Trennt die Verbindung zur Drohne
        
        Returns:
            bool: True, wenn die Verbindung erfolgreich getrennt wurde
        """
        self._logger.addLog("[INFO] Trenne Verbindung...")
        return self._connector.disconnect()
    
    @Slot()
    def arm(self) -> bool:
        """
        Armiert die Drohne
        
        Returns:
            bool: True, wenn der Armierungs-Befehl erfolgreich gesendet wurde
        """
        return self._connector.arm()
    
    @Slot()
    def disarm(self) -> bool:
        """
        Disarmiert die Drohne
        
        Returns:
            bool: True, wenn der Disarmierungs-Befehl erfolgreich gesendet wurde
        """
        return self._connector.disarm()
    
    @Slot()
    def takeoff(self) -> bool:
        """
        Lässt die Drohne starten
        
        Returns:
            bool: True, wenn der Takeoff-Befehl erfolgreich gesendet wurde
        """
        return self._connector.takeoff()
    
    @Slot()
    def land(self) -> bool:
        """
        Lässt die Drohne landen
        
        Returns:
            bool: True, wenn der Land-Befehl erfolgreich gesendet wurde
        """
        return self._connector.land()
    
    # Interne Slots für Connector-Signale
    
    def _on_connected(self):
        """Wird aufgerufen, wenn eine Verbindung hergestellt wurde"""
        self._is_connected = True
        self.connectionStateChanged.emit(True)
    
    def _on_disconnected(self):
        """Wird aufgerufen, wenn die Verbindung getrennt wurde"""
        self._is_connected = False
        self.connectionStateChanged.emit(False)
    
    def _on_error_occurred(self, error_message: str):
        """Wird aufgerufen, wenn ein Fehler aufgetreten ist"""
        self.errorOccurred.emit(error_message)
    
    def _on_armed_changed(self, armed: bool):
        """Wird aufgerufen, wenn sich der Armed-Status geändert hat"""
        self._is_armed = armed
        self.armedStateChanged.emit(armed)
    
    def _on_flight_mode_changed(self, flight_mode: str):
        """Wird aufgerufen, wenn sich der Flugmodus geändert hat"""
        self._flight_mode = flight_mode
        self.flightModeChanged.emit(flight_mode)
    
    def _on_gps_info_changed(self, gps_info: dict):
        """Wird aufgerufen, wenn sich die GPS-Informationen geändert haben"""
        self._gps_info = gps_info
        self.gpsInfoChanged.emit(gps_info)
    
    def _on_battery_changed(self, battery_info: dict):
        """Wird aufgerufen, wenn sich die Batterie-Informationen geändert haben"""
        self._battery_info = battery_info
        self.batteryChanged.emit(battery_info)
    
    def _on_attitude_changed(self, attitude: dict):
        """Wird aufgerufen, wenn sich die Lage der Drohne geändert hat"""
        self._attitude = attitude
        self.attitudeChanged.emit(attitude)
    
    def _on_heading_changed(self, heading: float):
        """Wird aufgerufen, wenn sich das Heading der Drohne geändert hat"""
        self.headingChanged.emit(heading)
    
    def _on_position_changed(self, position: dict):
        """Wird aufgerufen, wenn sich die Position der Drohne geändert hat"""
        self._position = position
        self.positionChanged.emit(position)
    
    def _on_home_position_changed(self, home_position: dict):
        """Wird aufgerufen, wenn sich die Home-Position der Drohne geändert hat"""
        self._home_position = home_position
        self.homePositionChanged.emit(home_position)
    
    def _on_statustext_received(self, statustext: str):
        """Wird aufgerufen, wenn ein Status-Text empfangen wurde"""
        self.messageReceived.emit(statustext)
