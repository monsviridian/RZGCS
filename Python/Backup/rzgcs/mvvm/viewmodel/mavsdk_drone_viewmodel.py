#!/usr/bin/env python3
"""
MAVSDK Drone ViewModel - ViewModel für die Drohnensteuerung im MVVM-Pattern

Dieses ViewModel stellt die Verbindung zwischen der UI und dem MAVSDKConnectorService her
und implementiert die entsprechende Geschäftslogik mit Unterstützung für Nachrichtenfilterung
und die spezielle Preflight-View für Systeminformationen.
"""

from PySide6.QtCore import QObject, Signal, Slot, Property, QTimer, QByteArray

from rzgcs.mvvm.model.drone_model import DroneModel
from rzgcs.mvvm.service.mavsdk_connector_service import MAVSDKConnectorService
from backend.logger import Logger


class MAVSDKDroneViewModel(QObject):
    """ViewModel für die Drohnensteuerung mit MAVSDK-Integration"""
    
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
    systemInfoReceived = Signal(str)  # Spezielles Signal für Systeminformationen (Preflight-View)
    errorOccurred = Signal(str)
    
    # Signal-Definitionen für die Properties
    availablePortsChanged = Signal()
    connectionStatusChanged = Signal()
    statusMessageChanged = Signal()
    
    def __init__(self, logger: Logger, parent=None):
        """Initialisierung des DroneViewModel"""
        super().__init__(parent)
        
        # Logger
        self._logger = logger
        
        # Datenmodell
        self._model = DroneModel()
        
        # MAVSDK-Connector Service
        self._connector_service = MAVSDKConnectorService(logger)
        
        # Port management
        self._available_ports = []
        self._connection_status = "Disconnected"
        self._status_message = "Ready to connect"
        
        # Verbinde Signale und registriere Callbacks
        self._connect_signals()
        self._register_callbacks()
        
        # Scan for available ports on init
        self.refreshPorts()
    
    def _connect_signals(self):
        """Verbindet die Signale des Connectors mit lokalen Slots"""
        # Verbindungssignale
        self._connector_service.signals.connection_established.connect(self._on_connected)
        self._connector_service.signals.connection_lost.connect(self._on_disconnected)
        self._connector_service.signals.error_occurred.connect(self._on_error_occurred)
        
        # Telemetrie-Signale
        self._connector_service.signals.armed_changed.connect(self._on_armed_changed)
        self._connector_service.signals.flight_mode_changed.connect(self._on_flight_mode_changed)
        self._connector_service.signals.gps_info_changed.connect(self._on_gps_info_changed)
        self._connector_service.signals.battery_changed.connect(self._on_battery_changed)
        self._connector_service.signals.attitude_changed.connect(self._on_attitude_changed)
        self._connector_service.signals.heading_changed.connect(self._on_heading_changed)
        self._connector_service.signals.position_changed.connect(self._on_position_changed)
        self._connector_service.signals.home_position_changed.connect(self._on_home_position_changed)
        
        # Status-Texte
        self._connector_service.signals.statustext_received.connect(self._on_statustext_received)
    
    def _register_callbacks(self):
        """Registriert zusätzliche Callbacks beim Connector"""
        # Verwendet das Callback-Interface zusätzlich zu den Signalen
        # Dies stellt die Kompatibilität mit älteren Code-Teilen sicher
        self._connector_service.register_connection_callback(self._on_connected)
        self._connector_service.register_disconnection_callback(self._on_disconnected)
        
        # Telemetrie-Callbacks
        for telemetry_type in ['armed', 'flight_mode', 'gps_info', 'battery', 'attitude', 
                            'heading', 'position', 'home_position']:
            self._connector_service.register_telemetry_callback(telemetry_type, self._on_telemetry_update)
        
        self._connector_service.register_statustext_callback(self._on_statustext_received)
    
    # Properties für die UI
    @Property(list, notify=availablePortsChanged)
    def availablePorts(self) -> list:
        """Gibt die Liste der verfügbaren COM-Ports zurück"""
        return self._available_ports
        
    # Compatibility property for QML UI (aliased to connection status)
    @Property(bool, notify=connectionStatusChanged)
    def connected(self) -> bool:
        """Gibt zurück, ob eine Verbindung besteht (QML-Kompatibilität)"""
        return self._model.is_connected
    
    @Property(str, notify=connectionStatusChanged)
    def connectionStatus(self) -> str:
        """Gibt den aktuellen Verbindungsstatus als String zurück"""
        return self._connection_status
    
    @Property(str, notify=statusMessageChanged)
    def statusMessage(self) -> str:
        """Gibt die aktuelle Statusmeldung zurück"""
        return self._status_message
    
    @Slot()
    def refreshPorts(self) -> None:
        """Aktualisiert die Liste der verfügbaren COM-Ports"""
        try:
            # Get all available ports from the connector service
            ports = self._connector_service.get_available_ports()
            
            if ports != self._available_ports:
                self._available_ports = ports
                self.availablePortsChanged.emit()
                
            if not ports:
                self._update_status("Keine COM-Ports gefunden")
            else:
                self._update_status(f"{len(ports)} COM-Port(s) gefunden")
                
        except Exception as e:
            self._update_status(f"Fehler beim Scannen der Ports: {str(e)}", is_error=True)
    
    def _update_status(self, message: str, is_error: bool = False) -> None:
        """Aktualisiert die Statusmeldung"""
        self._status_message = message
        self.statusMessageChanged.emit()
        
        # Use addLog method which is compatible with the custom Logger class
        log_message = f"[ERROR] {message}" if is_error else f"[INFO] {message}"
        self._logger.addLog(log_message)
    
    # QML compatibility methods
    @Slot()
    def load_ports(self):
        """Lädt die verfügbaren Ports (Kompatibilitätsmethode für QML)"""
        self.refreshPorts()
        
    @Slot(str)
    def setPort(self, port_name):
        """Setzt den ausgewählten Port (Kompatibilitätsmethode für QML)"""
        self._selected_port = port_name
        self._update_status(f"Port ausgewählt: {port_name}")
    
    @Slot(str)
    def connect(self, connection_string):
        """Universelle Verbindungsmethode (Kompatibilitätsmethode für QML)"""
        # Falls ein Port ausgewählt wurde und kein expliziter connection_string angegeben wurde
        if self._selected_port and not connection_string:
            connection_string = self._selected_port
            
        self.connectDrone(connection_string)
    
    @Slot(bool)
    def update_connection_status(self, is_connected):
        """Aktualisiert den Verbindungsstatus (Kompatibilitätsmethode für QML)"""
        # Dieser Slot wird vom QML aufgerufen, kann aber ignoriert werden,
        # da der Status direkt vom Service aktualisiert wird
        pass
        
    @Slot(str)
    def connectDrone(self, connection_string: str) -> None:
        """Stellt eine Verbindung zur Drohne her"""
        if not connection_string:
            self._update_status("Keine Verbindungsdaten angegeben", is_error=True)
            return
            
        self._update_status(f"Verbinde mit: {connection_string}")
        
        try:
            # Call the appropriate connect method based on the connection string
            if connection_string.startswith("udp:"):
                self._connector_service.connect_udp(connection_string)
            elif connection_string.startswith("tcp:"):
                self._connector_service.connect_tcp(connection_string)
            elif connection_string.startswith("simulator"):
                self._connector_service.connect_simulator()
            else:
                # Assume it's a serial connection
                if ":" in connection_string:
                    port, baudrate = connection_string.split(":", 1)
                    self._connector_service.connect_serial(port, int(baudrate or "57600"))
                else:
                    self._connector_service.connect_serial(connection_string, 57600)
                    
        except Exception as e:
            error_msg = f"Verbindungsfehler: {str(e)}"
            self._update_status(error_msg, is_error=True)
            self.errorOccurred.emit(error_msg)
    
    @Slot()
    def disconnect(self) -> None:
        """Trennt die Verbindung zur Drohne"""
        self._update_status("Trenne Verbindung...")
        self._connector_service.disconnect()
    
    # Callbacks für Verbindungsstatus
    def _on_connected(self) -> None:
        """Wird aufgerufen, wenn eine Verbindung hergestellt wurde"""
        self._model.is_connected = True
        self._connection_status = "Connected"
        self.connectionStateChanged.emit(True)
        self.connectionStatusChanged.emit()
        self._update_status("Verbindung hergestellt")
    
    def _on_disconnected(self) -> None:
        """Wird aufgerufen, wenn die Verbindung getrennt wurde"""
        self._model.is_connected = False
        self._connection_status = "Disconnected"
        self.connectionStateChanged.emit(False)
        self.connectionStatusChanged.emit()
        self._update_status("Verbindung getrennt")
    
    def _on_error_occurred(self, error_message: str) -> None:
        """Wird aufgerufen, wenn ein Fehler aufgetreten ist"""
        self._update_status(f"Fehler: {error_message}", is_error=True)
        self.errorOccurred.emit(error_message)
    
    # Telemetrie-Callbacks
    def _on_armed_changed(self, armed: bool) -> None:
        """Wird aufgerufen, wenn sich der Armed-Status ändert"""
        self._model.is_armed = armed
        self.armedStateChanged.emit(armed)
    
    def _on_flight_mode_changed(self, flight_mode: str) -> None:
        """Wird aufgerufen, wenn sich der Flugmodus ändert"""
        self._model.flight_mode = flight_mode
        self.flightModeChanged.emit(flight_mode)
    
    def _on_gps_info_changed(self, gps_info: dict) -> None:
        """Wird aufgerufen, wenn sich die GPS-Informationen ändern"""
        self._model.gps_info = gps_info
        self.gpsInfoChanged.emit(gps_info)
    
    def _on_battery_changed(self, battery_info: dict) -> None:
        """Wird aufgerufen, wenn sich die Batterieinformationen ändern"""
        self._model.battery = battery_info
        self.batteryChanged.emit(battery_info)
    
    def _on_attitude_changed(self, attitude: dict) -> None:
        """Wird aufgerufen, wenn sich die Lage ändert"""
        self._model.attitude = attitude
        self.attitudeChanged.emit(attitude)
    
    def _on_heading_changed(self, heading: float) -> None:
        """Wird aufgerufen, wenn sich der Heading ändert"""
        self._model.heading = heading
        self.headingChanged.emit(heading)
    
    def _on_position_changed(self, position: dict) -> None:
        """Wird aufgerufen, wenn sich die Position ändert"""
        self._model.position = position
        self.positionChanged.emit(position)
    
    def _on_home_position_changed(self, home_position: dict) -> None:
        """Wird aufgerufen, wenn sich die Home-Position ändert"""
        self._model.home_position = home_position
        self.homePositionChanged.emit(home_position)
    
    def _on_statustext_received(self, text: str) -> None:
        """Wird aufgerufen, wenn ein Status-Text empfangen wird"""
        # Spezielle Filterung für Systeminformationen
        if any(keyword in text for keyword in ["Frame type", "RCOut", "MicroAir743", "ChibiOS", "ArduCopter Version", "PreArm"]):
            self.systemInfoReceived.emit(text)
        
        # Generelle Nachricht immer emittieren
        self.messageReceived.emit(text)
    
    def _on_telemetry_update(self, data: any) -> None:
        """Generischer Callback für Telemetrie-Updates"""
        # Nichts tun, die spezifischen Callbacks werden verwendet
        pass
    
    # Exposed properties for QML
    @Property(bool, notify=connectionStateChanged)
    def connected(self) -> bool:
        """Gibt zurück, ob eine Verbindung zur Drohne besteht (Alias für is_connected)"""
        return self._model.is_connected
