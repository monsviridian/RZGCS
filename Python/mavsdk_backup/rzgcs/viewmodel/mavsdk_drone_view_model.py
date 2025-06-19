#!/usr/bin/env python3
"""
MAVSDK Drone ViewModel - ViewModel für die Drohnensteuerung im MVVM-Pattern

Dieses ViewModel stellt die Verbindung zwischen der UI und dem MAVSDKConnectorMVVM her
und implementiert die entsprechende Geschäftslogik mit Unterstützung für Nachrichtenfilterung
und die spezielle Preflight-View für Systeminformationen.
"""

from PySide6.QtCore import QObject, Signal, Slot, Property, QTimer

from backend.mavsdk_connector_mvvm import MAVSDKConnectorMVVM
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
    parametersUpdated = Signal(list)
    inAirChanged = Signal(bool)          # Neues Signal: Flugstatus (in der Luft/am Boden)
    healthChanged = Signal(dict)         # Neues Signal: Gesundheitsstatus (detailliert)
    healthAllOkChanged = Signal(bool)    # Neues Signal: Gesamtgesundheitsstatus
    messageReceived = Signal(str)
    systemInfoReceived = Signal(str)  # Spezielles Signal für Systeminformationen (Preflight-View)
    errorOccurred = Signal(str)
    
    def __init__(self, logger: Logger, parent=None):
        """Initialisierung des DroneViewModel"""
        super().__init__(parent)
        
        # Logger
        self._logger = logger
        
        # MAVSDK-Connector
        self.mavsdk_connector = MAVSDKConnectorMVVM(logger)
        
        # Erstelle einen Alias für Kompatibilität mit bestehendem Code
        self._connector = self.mavsdk_connector
        
        # Verbinde die Signale des MAVSDK-Connectors
        self._connect_signals()
        
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
        
        # Port management
        self._available_ports = []
        self._connection_status = "Disconnected"
        self._status_message = "Ready to connect"
        
        # Scan for available ports on init
        self.refreshPorts()
        
        # Verbinde Signale und registriere Callbacks
        self._connect_signals()
        self._register_callbacks()
    
    def _connect_signals(self):
        """Verbindet die Signale des Connectors mit lokalen Slots"""
        # Hier überprüfen wir, ob der Connector bereits die neuen Signale hat
        if hasattr(self.mavsdk_connector, 'signals'):
            signals = self.mavsdk_connector.signals
            
            # Prüfen, welche Art von Signal-Objekt vorliegt (MAVSDKSignals vs. DroneSignalHub)
            if hasattr(signals, 'connection_state_changed'):
                # Neue MAVSDKSignals (wie von uns implementiert)
                self._logger.addLog("[INFO] Verwende neue MAVSDKSignals-Klasse")
                
                # Verbindungssignale
                signals.connection_state_changed.connect(self._on_connection_state_changed)
                
                # Telemetrie-Signale
                signals.armed_state_changed.connect(self._on_armed_state_changed)
                signals.flight_mode_changed.connect(self._on_flight_mode_changed)
                signals.gps_info_updated.connect(self._on_gps_info_updated)
                signals.battery_updated.connect(self._on_battery_updated)
                signals.attitude_updated.connect(self._on_attitude_updated)
                signals.position_updated.connect(self._on_position_updated)
                
                # Home-Position-Updates (falls verfügbar)
                if hasattr(signals, 'home_position_updated'):
                    signals.home_position_updated.connect(self._on_home_position_updated)
                    
                # Parameter-Updates (falls verfügbar)
                if hasattr(signals, 'parameters_updated'):
                    signals.parameters_updated.connect(self._on_parameters_updated)
                    
                # Neue Telemetrie-Signale (basierend auf dem MAVSDK-Beispiel)
                if hasattr(signals, 'in_air_changed'):
                    signals.in_air_changed.connect(self._on_in_air_changed)
                    
                if hasattr(signals, 'health_updated'):
                    signals.health_updated.connect(self._on_health_updated)
                    
                if hasattr(signals, 'health_all_ok_changed'):
                    signals.health_all_ok_changed.connect(self._on_health_all_ok_changed)
                    
                self._logger.addLog("[INFO] MAVSDK-Signale erfolgreich verbunden")
            else:
                # Ältere DroneSignalHub
                self._logger.addLog("[INFO] Verwende bestehende DroneSignalHub-Klasse")
                
                # Verbindungssignale
                if hasattr(signals, 'connection_established'):
                    signals.connection_established.connect(self._on_connected)
                if hasattr(signals, 'connection_lost'):
                    signals.connection_lost.connect(self._on_disconnected)
                if hasattr(signals, 'error_occurred'):
                    signals.error_occurred.connect(self._on_error_occurred)
                
                # Telemetrie-Signale (alte Namen)
                if hasattr(signals, 'armed_changed'):
                    signals.armed_changed.connect(self._on_armed_changed)
                if hasattr(signals, 'flight_mode_changed'):
                    signals.flight_mode_changed.connect(self._on_flight_mode_changed)
                if hasattr(signals, 'gps_info_changed'):
                    signals.gps_info_changed.connect(self._on_gps_info_changed)
                if hasattr(signals, 'battery_changed'):
                    signals.battery_changed.connect(self._on_battery_changed)
                if hasattr(signals, 'attitude_changed'):
                    signals.attitude_changed.connect(self._on_attitude_changed)
                if hasattr(signals, 'position_changed'):
                    signals.position_changed.connect(self._on_position_changed)
                if hasattr(signals, 'home_position_changed'):
                    signals.home_position_changed.connect(self._on_home_position_changed)
                if hasattr(signals, 'statustext_received'):
                    signals.statustext_received.connect(self._on_statustext_received)
                
                self._logger.addLog("[INFO] Legacy MAVSDK-Signale erfolgreich verbunden")
        else:
            self._logger.addLog("[WARNUNG] MAVSDK-Connector hat keine Signals-Eigenschaft")
        
        # Status-Texte (falls verfügbar)
        if hasattr(self.mavsdk_connector, 'signals') and hasattr(self.mavsdk_connector.signals, 'statustext_received'):
            self.mavsdk_connector.signals.statustext_received.connect(self._on_statustext_received)
    
    def _register_callbacks(self):
        """Registriert zusätzliche Callbacks beim Connector"""
        # Wird für ältere MAVSDK-Connector-Versionen verwendet
        pass
        
    # Neue Callback-Methoden für Telemetriedaten
    
    def _on_battery_updated(self, battery_info):
        """Verarbeitet Batterie-Updates vom MAVSDK-Connector"""
        self._battery_info = battery_info
        self.batteryChanged.emit(battery_info)
        self._logger.addLog(f"[DEBUG] Batterie: {battery_info['remaining_percent']:.1f}% ({battery_info['voltage_v']:.2f}V)")
    
    def _on_attitude_updated(self, attitude_info):
        """Verarbeitet Lage-Updates vom MAVSDK-Connector"""
        self._attitude = attitude_info
        self.attitudeChanged.emit(attitude_info)
        self.headingChanged.emit(attitude_info['yaw_deg'])
        # Lageänderungen werden häufig gesendet, deshalb kein Debug-Log
    
    def _on_position_updated(self, position_info):
        """Verarbeitet Positions-Updates vom MAVSDK-Connector"""
        self._position = position_info
        self.positionChanged.emit(position_info)
        # Positionsänderungen werden häufig gesendet, deshalb kein Debug-Log
    
    def _on_home_position_updated(self, home_position_info):
        """Verarbeitet Home-Position-Updates vom MAVSDK-Connector"""
        self._home_position = home_position_info
        self.homePositionChanged.emit(home_position_info)
        self._logger.addLog(f"[INFO] Home-Position aktualisiert: Lat={home_position_info['latitude_deg']:.6f}, Lon={home_position_info['longitude_deg']:.6f}")
    
    def _on_parameters_updated(self, param_list):
        """Verarbeitet Parameter-Updates vom MAVSDK-Connector"""
        # Log-Nachricht
        self._logger.addLog(f"[INFO] {len(param_list)} Parameter empfangen")
        
        # Emittiere das Signal für die UI-Komponenten
        self.parametersUpdated.emit(param_list)
        
        # System-Info-Nachricht für den Preflight-View
        self.systemInfoReceived.emit(f"Parameter erfolgreich geladen ({len(param_list)} Parameter)")
    
    def _on_in_air_changed(self, in_air):
        """Verarbeitet In-Air-Status-Updates vom MAVSDK-Connector"""
        # Status-Text
        status_text = "IN DER LUFT" if in_air else "AM BODEN"
        
        # Log-Nachricht
        self._logger.addLog(f"[INFO] Flugstatus: {status_text}")
        
        # Emittiere das Signal für die UI-Komponenten
        self.inAirChanged.emit(in_air)
        
        # System-Info-Nachricht für den Preflight-View
        self.systemInfoReceived.emit(f"Flugstatus: {status_text}")
    
    def _on_health_updated(self, health_info):
        """Verarbeitet Gesundheitsstatus-Updates vom MAVSDK-Connector"""
        # Log-Nachricht
        self._logger.addLog("[DEBUG] Gesundheitsstatus aktualisiert")
        
        # Emittiere das Signal für die UI-Komponenten
        self.healthChanged.emit(health_info)
        
        # Erstelle eine Übersicht für den Preflight-View
        calibration_status = "OK" if (health_info["is_gyrometer_calibration_ok"] and 
                                     health_info["is_accelerometer_calibration_ok"] and 
                                     health_info["is_magnetometer_calibration_ok"] and 
                                     health_info["is_level_calibration_ok"]) else "FEHLER"
        
        position_status = "OK" if (health_info["is_local_position_ok"] and 
                                 health_info["is_global_position_ok"] and 
                                 health_info["is_home_position_ok"]) else "FEHLER"
        
        # System-Info-Nachricht für den Preflight-View
        self.systemInfoReceived.emit(f"Kalibrierung: {calibration_status}, Position: {position_status}")
    
    def _on_health_all_ok_changed(self, health_all_ok):
        """Verarbeitet Gesamt-Gesundheitsstatus-Updates vom MAVSDK-Connector"""
        # Status-Text
        status_text = "OK" if health_all_ok else "FEHLER"
        
        # Log-Nachricht
        self._logger.addLog(f"[INFO] Gesamtstatus: {status_text}")
        
        # Emittiere das Signal für die UI-Komponenten
        self.healthAllOkChanged.emit(health_all_ok)
        
        # System-Info-Nachricht für den Preflight-View mit besonderer Markierung
        if health_all_ok:
            self.systemInfoReceived.emit("[SYSTEM OK] Alle Systeme funktionieren normal")
        else:
            self.systemInfoReceived.emit("[SYSTEM FEHLER] Prüfen Sie die Kalibrierung und Sensoren")
            
        # Bei Statuswechsel auch einen Fehler emittieren, wenn nicht OK
        if not health_all_ok:
            self.errorOccurred.emit("Gesundheitsstatus der Drohne ist nicht OK! Prüfen Sie die Kalibrierung und Sensoren.")
    
    def _on_gps_info_updated(self, gps_info):
        """Verarbeitet GPS-Info-Updates vom MAVSDK-Connector"""
        self._gps_info = gps_info
        self.gpsInfoChanged.emit(gps_info)
        self._logger.addLog(f"[DEBUG] GPS: Sats={gps_info['num_satellites']}, Fix={gps_info['fix_type']}")
    
    def _on_flight_mode_changed(self, flight_mode):
        """Verarbeitet Flugmodus-Änderungen vom MAVSDK-Connector"""
        self._flight_mode = flight_mode
        self.flightModeChanged.emit(flight_mode)
        # Wichtige Flugmodus-Änderungen als Systeminformation anzeigen
        self.systemInfoReceived.emit(f"Flugmodus: {flight_mode}")
        self._logger.addLog(f"[INFO] Flugmodus: {flight_mode}")
    
    def _on_armed_state_changed(self, armed):
        """Verarbeitet Armed-Status-Änderungen vom MAVSDK-Connector"""
        self._is_armed = armed
        self.armedStateChanged.emit(armed)
        # Armed-Status-Änderungen als Systeminformation anzeigen
        status = "ARMED" if armed else "DISARMED"
        self.systemInfoReceived.emit(f"Flight Controller {status}")
        self._logger.addLog(f"[INFO] Armed-Status: {status}")
    
    def _on_connection_state_changed(self, connected):
        """Verarbeitet Verbindungsstatus-Änderungen vom MAVSDK-Connector"""
        self._is_connected = connected
        self.connectionStateChanged.emit(connected)
        status = "VERBUNDEN" if connected else "GETRENNT"
        self._logger.addLog(f"[INFO] Verbindungsstatus: {status}") 
        # Dies stellt die Kompatibilität mit älteren Code-Teilen sicher
        self._connector.register_connection_callback(self._on_connected)
        self._connector.register_disconnection_callback(self._on_disconnected)
        
        # Telemetrie-Callbacks
        for telemetry_type in ['armed', 'flight_mode', 'gps_info', 'battery', 'attitude', 
                            'heading', 'position', 'home_position']:
            self._connector.register_telemetry_callback(telemetry_type, self._on_telemetry_update)
        
        self._connector.register_statustext_callback(self._on_statustext_received)
    
    # Signal-Definitionen für die Properties
    availablePortsChanged = Signal()
    connectionStatusChanged = Signal()
    statusMessageChanged = Signal()
    
    # Properties für die UI
    @Property(list, notify=availablePortsChanged)
    def availablePorts(self) -> list:
        """Gibt die Liste der verfügbaren COM-Ports zurück"""
        return self._available_ports
    
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
        import serial.tools.list_ports
        
        try:
            # Get all available COM ports
            ports = [port.device for port in serial.tools.list_ports.comports()]
            
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
    
    @Slot(str)
    def connectDrone(self, connection_string: str) -> None:
        """Stellt eine Verbindung zur Drohne her"""
        if not connection_string:
            self._update_status("Keine Verbindungsdaten angegeben", is_error=True)
            return
            
        self._update_status(f"Verbinde mit: {connection_string}")
        self._logger.addLog(f"[DEBUG] MAVSDKDroneViewModel.connectDrone() aufgerufen mit: {connection_string}")
        
        try:
            # Rufe die universelle connect-Methode auf, die die MAVSDK-Verbindung verwaltet
            if self._connector is not None:
                self._connector.connect(connection_string)
            else:
                self._update_status("Kein MAVSDK-Connector vorhanden", is_error=True)
        except Exception as e:
            error_msg = f"Verbindungsfehler: {str(e)}"
            self._update_status(error_msg, is_error=True)
            self.errorOccurred.emit(error_msg)
    @Slot()
    def disconnect(self) -> None:
        """Trennt die Verbindung zur Drohne"""
        self._update_status("Trenne Verbindung...")
        
        try:
            if self._connector is not None:
                self._connector.disconnect()
            else:
                self._update_status("Kein MAVSDK-Connector vorhanden", is_error=True)
        except Exception as e:
            error_msg = f"Fehler beim Trennen der Verbindung: {str(e)}"
            self._update_status(error_msg, is_error=True)
            if hasattr(self, 'errorOccurred'):
                self.errorOccurred.emit(error_msg)
    
    # Flag und Lock für Parameter-Abruf
    _parameters_loading = False
    _parameters_last_loaded = 0
    _parameters_loading_interval = 5  # Minimum Sekunden zwischen Parameter-Abrufen
    
    @Slot()
    def loadParameters(self) -> bool:
        """Lädt Parameter vom Flight Controller (wenn verbunden)
        
        Fügt eine Sperre ein, um wiederholte Aufrufe in kurzer Zeit zu verhindern.
        """
        import time
        current_time = time.time()
        
        # Vermeide wiederholte Parameter-Abrufe in kurzer Zeit
        if MAVSDKDroneViewModel._parameters_loading:
            self._logger.addLog("[INFO] Parameter werden bereits abgerufen, ignoriere redundanten Aufruf")
            return True
            
        # Prüfe, ob der letzte Abruf zu kurz her ist
        time_since_last_load = current_time - MAVSDKDroneViewModel._parameters_last_loaded
        if time_since_last_load < MAVSDKDroneViewModel._parameters_loading_interval:
            self._logger.addLog(f"[INFO] Parameter wurden erst vor {time_since_last_load:.1f}s abgerufen, ignoriere redundanten Aufruf")
            return True
        
        # Prüfe, ob _connector existiert und verbunden ist
        if self._connector is not None and self._is_connected:
            try:
                # Prüfe, ob die Methode existiert
                if hasattr(self._connector, 'get_parameters'):
                    # Setze Flag und starte asynchronen Prozess
                    MAVSDKDroneViewModel._parameters_loading = True
                    MAVSDKDroneViewModel._parameters_last_loaded = current_time
                    self._logger.addLog("[INFO] Starte Parameter-Abruf...")
                    
                    # Nach dem Aufruf wird _parameters_loading auf False gesetzt
                    self._connector.get_parameters()
                    
                    # Verzögertes Zurücksetzen des Flags (für den Fall, dass kein Signal empfangen wird)
                    def reset_flag():
                        import threading
                        import time
                        time.sleep(10)  # Warte maximal 10 Sekunden
                        MAVSDKDroneViewModel._parameters_loading = False
                    
                    threading.Thread(target=reset_flag, daemon=True).start()
                    return True
                else:
                    self._logger.addLog("[WARNUNG] MAVSDK-Connector unterstützt keine Parameter-Funktionalität")
                    return False
            except Exception as e:
                MAVSDKDroneViewModel._parameters_loading = False
                self._logger.addLog(f"[FEHLER] Fehler beim Laden der Parameter: {str(e)}")
                return False
        else:
            self._logger.addLog("[WARNUNG] Kein MAVSDK-Connector vorhanden oder nicht verbunden")
            MAVSDKDroneViewModel._parameters_loading = False
            return False
            return False
    # Callbacks für Verbindungsstatus
    def _on_connected(self) -> None:
        """Wird aufgerufen, wenn eine Verbindung hergestellt wurde"""
        self._is_connected = True
        self._connection_status = "Connected"
        self.connectionStateChanged.emit(True)
        self.connectionStatusChanged.emit()
        self._update_status("Verbindung hergestellt")
    
    def _on_disconnected(self) -> None:
        """Wird aufgerufen, wenn die Verbindung getrennt wurde"""
        self._is_connected = False
        self._connection_status = "Disconnected"
        self.connectionStateChanged.emit(False)
        self.connectionStatusChanged.emit()
        self._update_status("Verbindung getrennt")
    
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
    connected = Property(bool, is_connected, notify=connectionStateChanged)  # Alias für QML
    armedState = Property(bool, is_armed, notify=armedStateChanged)
    flightMode = Property(str, flight_mode, notify=flightModeChanged)
    
    # Slots für die UI
    
    @Slot(str)
    def connectDrone(self, connection_string: str) -> bool:
        """
        Verbindet mit einer Drohne über den angegebenen Verbindungsstring
        
        Args:
            connection_string: Verbindungsstring (z.B. 'COM3' oder 'udp://127.0.0.1:14550')
            
        Returns:
            bool: True, wenn die Verbindung erfolgreich gestartet wurde
        """
        print(f"[DEBUG] MAVSDKDroneViewModel.connectDrone() aufgerufen mit: {connection_string}")
        self._logger.addLog(f"[INFO] Verbinde mit {connection_string}...")
        
        # Bereits verbunden?
        if self._is_connected:
            self._update_status("Bereits verbunden. Trenne Verbindung zuerst.")
            self.disconnect()
        
        # Aktualisiere den Status
        self._update_status(f"Verbinde mit {connection_string}...")
        
        # Überprüfe, ob es sich um einen seriellen Port handelt
        if connection_string.startswith("COM") or "/dev/" in connection_string:
            # Standardbaudrate für serielle Verbindung (geändert auf 115200)
            baudrate = 115200
            
            # Prüfe, ob eine Baudrate angegeben wurde (Format: COM3:115200)
            port = connection_string
            if ":" in connection_string:
                port, baudrate_str = connection_string.split(":")
                try:
                    baudrate = int(baudrate_str)
                except ValueError:
                    self._logger.addLog(f"[WARNUNG] Ungültige Baudrate: {baudrate_str}, verwende Standardbaudrate 115200")
                    
            self._logger.addLog(f"[INFO] Verwende Baudrate: {baudrate} für Verbindung mit {port}")
            self.systemInfoReceived.emit(f"[SYSTEM INFO] Verbindungsversuch mit {port} bei {baudrate} Baud")
                
            success = self.connect_serial(port, baudrate)
            if success:
                self.systemInfoReceived.emit(f"[SYSTEM INFO] MAVSDK-Server erfolgreich gestartet für {port}")
            else:
                self.systemInfoReceived.emit(f"[SYSTEM INFO] MAVSDK-Server konnte nicht gestartet werden für {port}")
            return success
        
        # UDP-Format (z.B. udp://127.0.0.1:14550)
        elif connection_string.startswith("udp://"):
            self._logger.addLog(f"[INFO] Verbinde mit UDP: {connection_string}")
            self.systemInfoReceived.emit(f"[SYSTEM INFO] Verbindungsversuch mit UDP: {connection_string}")
            return self._connector.connect(connection_string)
        
        # TCP-Format (z.B. tcp://127.0.0.1:5760)
        elif connection_string.startswith("tcp://"):
            self._logger.addLog(f"[INFO] Verbinde mit TCP: {connection_string}")
            self.systemInfoReceived.emit(f"[SYSTEM INFO] Verbindungsversuch mit TCP: {connection_string}")
            return self._connector.connect(connection_string)
        
        # Unbekanntes Format
        else:
            error_msg = f"[FEHLER] Unbekanntes Verbindungsformat: {connection_string}"
            self._logger.addLog(error_msg)
            self.systemInfoReceived.emit(error_msg)
            return False
    
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
    def disconnectDrone(self) -> bool:
        """
        Alias für disconnect() - Trennt die Verbindung zur Drohne
        
        Returns:
            bool: True, wenn die Verbindung erfolgreich getrennt wurde
        """
        self._logger.addLog("[INFO] Trenne Verbindung (via disconnectDrone)...")
        return self.disconnect()
    
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
    
    # Signal-Handler
    
    def _on_connected(self):
        """Wird aufgerufen, wenn eine Verbindung hergestellt wurde"""
        self._is_connected = True
        self.connectionStateChanged.emit(True)
        self._logger.addLog("[INFO] Verbindung hergestellt")
    
    def _on_disconnected(self):
        """Wird aufgerufen, wenn die Verbindung getrennt wurde"""
        self._is_connected = False
        self.connectionStateChanged.emit(False)
        self._logger.addLog("[INFO] Verbindung getrennt")
    
    def _on_error_occurred(self, error_message: str):
        """Wird aufgerufen, wenn ein Fehler aufgetreten ist"""
        self.errorOccurred.emit(error_message)
    
    def _on_armed_changed(self, armed: bool):
        """Wird aufgerufen, wenn sich der Armed-Status geändert hat"""
        self._is_armed = armed
        self.armedStateChanged.emit(armed)
    
    def _on_flight_mode_changed(self, mode: str):
        """Wird aufgerufen, wenn sich der Flugmodus geändert hat"""
        self._flight_mode = mode
        self.flightModeChanged.emit(mode)
    
    def _on_gps_info_changed(self, data: dict):
        """Wird aufgerufen, wenn sich die GPS-Informationen geändert haben"""
        self._gps_info = data
        self.gpsInfoChanged.emit(data)
    
    def _on_battery_changed(self, data: dict):
        """Wird aufgerufen, wenn sich die Batterie-Informationen geändert haben"""
        self._battery_info = data
        self.batteryChanged.emit(data)
    
    def _on_attitude_changed(self, data: dict):
        """Wird aufgerufen, wenn sich die Lage der Drohne geändert hat"""
        self._attitude = data
        self.attitudeChanged.emit(data)
    
    def _on_heading_changed(self, heading: float):
        """Wird aufgerufen, wenn sich das Heading der Drohne geändert hat"""
        self.headingChanged.emit(heading)
    
    def _on_position_changed(self, data: dict):
        """Wird aufgerufen, wenn sich die Position der Drohne geändert hat"""
        self._position = data
        self.positionChanged.emit(data)
    
    def _on_home_position_changed(self, data: dict):
        """Wird aufgerufen, wenn sich die Home-Position der Drohne geändert hat"""
        self._home_position = data
        self.homePositionChanged.emit(data)
    
    def _on_statustext_received(self, text: str):
        """
        Wird aufgerufen, wenn ein Status-Text empfangen wurde
        
        Implementiert den speziellen Filtermechanismus für die Preflight-View,
        der Systeminformationen gezielt filtert und hervorhebt.
        """
        # Prüfen, ob es sich um eine Systeminformation handelt
        if text.startswith("[SYSTEM INFO]"):
            # Spezielle Behandlung für die Preflight-View
            # Dies nutzt den speziellen Filtermechanismus, der Systeminformationen
            # (Frame-Typ, RCOut, MicoAir743, ChibiOS, ArduCopter Version, PreArm-Warnungen)
            # gezielt filtert und mit größerer Schrift und Hervorhebung darstellt
            self.systemInfoReceived.emit(text)
        else:
            # Normale Nachricht
            self.messageReceived.emit(text)
    
    # Callback-Handler für die Callback-basierte API
    
    def _on_telemetry_update(self, data: dict):
        """
        Allgemeiner Handler für Telemetrie-Updates über das Callback-Interface
        
        Diese Methode wird aufgerufen, wenn ein Telemetrie-Callback aktiviert wird
        und leitet die Daten an die spezifischen Handler weiter.
        """
        telemetry_type = data.get('type', '')
        
        if telemetry_type == 'armed':
            self._on_armed_changed(data.get('armed', False))
        elif telemetry_type == 'flight_mode':
            self._on_flight_mode_changed(data.get('mode', "UNBEKANNT"))
        elif telemetry_type == 'heading':
            self._on_heading_changed(data.get('heading', 0.0))
        elif telemetry_type == 'position':
            self._on_position_changed(data)
        elif telemetry_type == 'attitude':
            self._on_attitude_changed(data)
        elif telemetry_type == 'battery':
            self._on_battery_changed(data)
        elif telemetry_type == 'gps_info':
            self._on_gps_info_changed(data)
        elif telemetry_type == 'home_position':
            self._on_home_position_changed(data)
