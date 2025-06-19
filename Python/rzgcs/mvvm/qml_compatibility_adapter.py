#!/usr/bin/env python3
"""
QML Compatibility Adapter für MVVM
Bietet Kompatibilität zwischen den alten QML-Signalnamen und den neuen MVVM-Signalen,
während die COM-Port-Verbindung korrekt verarbeitet wird.
"""

from PySide6.QtCore import QObject, Signal, Slot, Property, QUrl, QTimer
from PySide6.QtQml import QQmlApplicationEngine

import os
import importlib
import sys
import time
import datetime
import re

class QMLCompatibilityAdapter(QObject):
    """
    Adapter-Klasse, die Kompatibilität zwischen QML und MVVM herstellt
    
    Diese Klasse empfängt die MVVM-Signale und sendet sie in QML-kompatiblen Formaten weiter,
    sodass die bestehenden QML-Files ohne Änderungen weiter funktionieren.
    """
    # Legacy-Signale für QML-Kompatibilität
    attitudeChanged = Signal(float, float, float)  # roll, pitch, yaw als separate Parameter
    attitude_msg = Signal(float, float, float)     # Legacy-Name
    gpsChanged = Signal(int, int)                  # numSat, fixType
    
    # WICHTIG: Verwende 'connectedChanged' als Signalnamen für QML-Kompatibilität
    connectedChanged = Signal(bool)                # Verbindungsstatus
    
    # Zusätzliche Signale, die in verschiedenen QML-Dateien verwendet werden
    portsRefreshed = Signal(list)                  # Für aktualisierte Ports-Liste
    availablePortsChanged = Signal(list)           # Für PreflightView.ui.qml
    
    # Telemetrie-Signale für QML
    batteryChanged = Signal(float, float, float)    # remaining_percent, voltage_v, current_a
    positionChanged = Signal(float, float, float)   # latitude_deg, longitude_deg, relative_altitude_m
    headingChanged = Signal(float)                  # heading (Yaw in Grad)
    flightModeChanged = Signal(str)                 # Flugmodus als String
    armedStateChanged = Signal(bool)                # Armed-Status
    
    # Signale für den Motortest (MotorTestView.ui.qml)
    motorStatusChanged = Signal(int, bool, str)     # motorNumber, isRunning, statusText
    logMessageAdded = Signal(str)                   # message
    testProgressChanged = Signal(int, str)          # progress, status
    testFinished = Signal(bool, str)                # success, message
    
    # Verbesserte Signale für FC-Nachrichten und Verbindungsstatus
    connectionStatusChanged = Signal(bool)
    batteryLevelChanged = Signal(float)
    fcImportantMessageReceived = Signal(str)
    
    # Signal für SensorViewModel-Änderungen
    sensorViewModelChanged = Signal()
    
    def __init__(self, drone_view_model, logger, parent=None):
        """Initialisierung des QML-Compatibility-Adapters
        
        Args:
            drone_view_model: ViewModel für die Drohne
            logger: Logger-Instanz
            parent: Elternobjekt
        """
        super().__init__(parent)
        self._drone_view_model = drone_view_model
        self._logger = logger
        
        # State tracken
        self._is_connected = False
        
        # Verbinde die Signale, falls vorhanden
        self._connect_signals()
        
        # Verbinde die Telemetrie-Signale, falls vorhanden
        self._connect_telemetry_signals()
    
    def _connect_signals(self):
        """Verbindet MVVM-Signale mit Legacy-Signalen"""
        # Attitude-Updates (dict zu einzelnen Parametern)
        self._drone_view_model.attitudeChanged.connect(self._handle_attitude)
        
        # GPS-Updates (dict zu einzelnen Parametern)
        self._drone_view_model.gpsInfoChanged.connect(self._handle_gps)
        
        # Verbindungs-Updates
        self._drone_view_model.connectionStateChanged.connect(self._handle_connection)
        
        # Flight Controller Nachrichten
        if hasattr(self._drone_view_model, 'messageReceived'):
            self._drone_view_model.messageReceived.connect(self._handle_fc_message)
            
        # Wichtige Systeminformationen
        if hasattr(self._drone_view_model, 'systemInfoReceived'):
            self._drone_view_model.systemInfoReceived.connect(self._handle_system_info)
    
    def _connect_telemetry_signals(self):
        """Verbindet die Telemetrie-Signale des MAVSDKConnectorMVVM mit den QML-Signalen"""
        # Prüfe, ob das ViewModel ein MAVSDKConnectorMVVM mit Signalen ist
        if hasattr(self._drone_view_model, 'mavsdk_connector') and \
           hasattr(self._drone_view_model.mavsdk_connector, 'signals'):
            
            signals = self._drone_view_model.mavsdk_connector.signals
            
            # Prüfen, welche Art von Signal-Objekt vorliegt (MAVSDKSignals vs. DroneSignalHub)
            self._logger.addLog("[INFO] Prüfe Signaltyp für Telemetrie-Verbindung")
            
            # Neue Signale (battery_updated) vs. alte Signale (battery_changed)
            if hasattr(signals, 'battery_updated'):
                # Neue MAVSDKSignals
                self._logger.addLog("[INFO] Verbinde mit neuen MAVSDKSignals")
                
                # Batterie-Updates
                signals.battery_updated.connect(self._on_battery_updated)
                
                # Positions-Updates
                signals.position_updated.connect(self._on_position_updated)
                
                # GPS-Info-Updates
                signals.gps_info_updated.connect(self._on_gps_info_updated)
                
                # Flugmodus-Änderungen
                signals.flight_mode_changed.connect(self._on_flight_mode_changed)
                
                # Verbinde den allgemeinen Telemetrie-Signal mit dem Backend
                # Dieser wird in mavsdk_rzgcs_main.py an das SensorViewModel weitergeleitet
                
                # Armed-Status-Änderungen
                signals.armed_state_changed.connect(self._on_armed_state_changed)
                
                # Verbindungsstatus-Änderungen
                signals.connection_state_changed.connect(self._on_connection_state_changed)
                
                # Neue erweiterte Telemetrie-Signale
                if hasattr(signals, 'in_air_changed'):
                    signals.in_air_changed.connect(self._on_in_air_changed)
                    
                if hasattr(signals, 'health_updated'):
                    signals.health_updated.connect(self._on_health_updated)
                    
                if hasattr(signals, 'health_all_ok_changed'):
                    signals.health_all_ok_changed.connect(self._on_health_all_ok_changed)
                    
                if hasattr(signals, 'heading_updated'):
                    signals.heading_updated.connect(self._on_heading_updated)
                    
                if hasattr(signals, 'angular_velocity_updated'):
                    signals.angular_velocity_updated.connect(self._on_angular_velocity_updated)
                    
                if hasattr(signals, 'status_text_received'):
                    signals.status_text_received.connect(self._on_status_text_received)
                    
                if hasattr(signals, 'altitude_updated'):
                    signals.altitude_updated.connect(self._on_altitude_updated)
                    
                if hasattr(signals, 'landed_state_changed'):
                    signals.landed_state_changed.connect(self._on_landed_state_changed)
                    
                if hasattr(signals, 'rc_status_updated'):
                    signals.rc_status_updated.connect(self._on_rc_status_updated)
                    
                # Parameter-Updates
                if hasattr(signals, 'parameters_updated'):
                    signals.parameters_updated.connect(self._on_parameters_updated)
                    
                if hasattr(signals, 'unix_epoch_time_updated'):
                    signals.unix_epoch_time_updated.connect(self._on_unix_epoch_time_updated)
                    
                # Fortgeschrittene Telemetrie-Signale
                if hasattr(signals, 'actuator_control_updated'):
                    signals.actuator_control_updated.connect(self._on_actuator_control_updated)
                    
                if hasattr(signals, 'actuator_output_updated'):
                    signals.actuator_output_updated.connect(self._on_actuator_output_updated)
                    
                if hasattr(signals, 'odometry_updated'):
                    signals.odometry_updated.connect(self._on_odometry_updated)
                    
                if hasattr(signals, 'distance_sensor_updated'):
                    signals.distance_sensor_updated.connect(self._on_distance_sensor_updated)
                    
                if hasattr(signals, 'scaled_pressure_updated'):
                    signals.scaled_pressure_updated.connect(self._on_scaled_pressure_updated)
                    
                if hasattr(signals, 'raw_imu_updated'):
                    signals.raw_imu_updated.connect(self._on_raw_imu_updated)
                
                self._logger.addLog("[INFO] Neue Telemetrie-Signale verbunden")
            else:
                # Ältere DroneSignalHub
                self._logger.addLog("[INFO] Verbinde mit bestehender DroneSignalHub")
                
                # Verbinde alte Signal-Namen mit unseren Callback-Methoden
                if hasattr(signals, 'battery_changed'):
                    signals.battery_changed.connect(self._on_battery_changed)
                
                if hasattr(signals, 'attitude_changed'):
                    signals.attitude_changed.connect(self._on_attitude_changed)
                
                if hasattr(signals, 'position_changed'):
                    signals.position_changed.connect(self._on_position_changed)
                
                if hasattr(signals, 'gps_info_changed'):
                    signals.gps_info_changed.connect(self._on_gps_info_changed)
                
                if hasattr(signals, 'flight_mode_changed'):
                    signals.flight_mode_changed.connect(self._on_flight_mode_changed)
                
                if hasattr(signals, 'armed_changed'):
                    signals.armed_changed.connect(self._on_armed_changed)
                
                if hasattr(signals, 'connection_established'):
                    signals.connection_established.connect(lambda: self._on_connection_state_changed(True))
                
                if hasattr(signals, 'connection_lost'):
                    signals.connection_lost.connect(lambda: self._on_connection_state_changed(False))
                
                self._logger.addLog("[INFO] Legacy Telemetrie-Signale verbunden")
                

    
    def _handle_attitude(self, attitude_dict):
        """Konvertiert Attitude-Dict in einzelne Parameter für QML"""
        roll = attitude_dict.get('roll_deg', 0.0)
        pitch = attitude_dict.get('pitch_deg', 0.0)
        yaw = attitude_dict.get('yaw_deg', 0.0)
        
        # Sende beide Signale für maximale Kompatibilität
        self.attitudeChanged.emit(roll, pitch, yaw)
        self.attitude_msg.emit(roll, pitch, yaw)
    
    def _handle_gps(self, gps_dict):
        """Konvertiert GPS-Dict in einzelne Parameter für QML"""
        num_satellites = gps_dict.get('num_satellites', 0)
        fix_type = gps_dict.get('fix_type', 0)
        
        self.gpsChanged.emit(num_satellites, fix_type)
    
    def _handle_connection(self, is_connected):
        """Verarbeitet Verbindungsstatus-Updates"""
        self._is_connected = is_connected
        self.connectedChanged.emit(is_connected)
        
    def _handle_connection_state_changed(self, is_connected):
        """Alternative Methode für Verbindungsstatus-Updates (für load_ports Kompatibilität)"""
        # Einfach an die Haupt-Handler-Methode weiterleiten
        self._handle_connection(is_connected)
    
    @Property(bool, notify=connectedChanged)
    def connected(self):
        """Property für QML: ob die Drohne verbunden ist"""
        # Stelle sicher, dass _is_connected existiert
        if not hasattr(self, '_is_connected'):
            self._is_connected = False
        return self._is_connected
        
    # Property wurde entfernt, da das SensorViewModel im Backend bereits vorhanden ist
    
    @Slot()
    def load_ports(self):
        """Lädt verfügbare Ports (Kompatibilitätsmethode für QML)"""
        # Signale verbinden
        if hasattr(self._drone_view_model, 'connectionStateChanged'):
            self._drone_view_model.connectionStateChanged.connect(self.connectionStatusChanged.emit)
            # Verbesserte Signalverbindung für Verbindungsstatus
            self._drone_view_model.connectionStateChanged.connect(self._handle_connection_state_changed)
        
        if hasattr(self._drone_view_model, 'batteryChanged'):
            self._drone_view_model.batteryChanged.connect(lambda battery: 
                self.batteryLevelChanged.emit(battery.get('remaining_percent', 0.0) if isinstance(battery, dict) else 0.0))
                
        # FC Important Message Signal verbinden
        if hasattr(self._drone_view_model, 'fcImportantMessageReceived'):
            self._drone_view_model.fcImportantMessageReceived.connect(self.fcImportantMessageReceived.emit)
            
        ports = []
        if hasattr(self._drone_view_model, 'refreshPorts'):
            self._drone_view_model.refreshPorts()
            
        # Gibt die verfügbaren Ports aus dem ViewModel zurück
        if hasattr(self._drone_view_model, 'ports'):
            ports = self._drone_view_model.ports
        else:
            # Fallback: Eigene Ports-Liste erstellen
            try:
                import serial.tools.list_ports
                ports = [port.device for port in serial.tools.list_ports.comports()]
            except Exception as e:
                print(f"[FEHLER] Konnte Ports nicht laden: {e}")
                
        # Signalisiere Veränderung der verfügbaren Ports
        self.portsRefreshed.emit(ports)
        self.availablePortsChanged.emit(ports)
        return ports
    
    @Slot(str)
    def setPort(self, port_name):
        """Setzt ausgewählten Port (Kompatibilitätsmethode für QML)"""
        self._selected_port = port_name
        if hasattr(self._drone_view_model, 'setSelectedPort'):
            self._drone_view_model.setSelectedPort(port_name)
        self.logMessageAdded.emit(f"[INFO] Port ausgewählt: {port_name}")
    
    @Slot(str)
    @Slot()
    def connect(self, connection_string=""):
        """
        Verbindet zur Drohne (Kompatibilitätsmethode für QML)
        
        Diese Methode nutzt die universelle connect-Methode des ViewModels,
        die alle Verbindungsformate intelligent verarbeitet.
        
        :param connection_string: Verbindungsstring (z.B. "COM3:115200", "COM3", "udp://127.0.0.1:14540")
                                  oder leer, um den zuletzt ausgewählten Port zu verwenden
        """
        print(f"[DEBUG] QMLCompatibilityAdapter.connect() aufgerufen mit: {connection_string}")
        # Wenn kein Verbindungsstring angegeben wurde, den zuletzt ausgewählten Port verwenden
        if not connection_string and hasattr(self, "_selected_port") and self._selected_port:
            connection_string = self._selected_port
            self.logMessageAdded.emit(f"[INFO] Verwende ausgewählten Port: {self._selected_port}")
            
        # Wenn immer noch kein Verbindungsstring vorhanden ist, abbrechen
        if not connection_string:
            self.logMessageAdded.emit("[FEHLER] Kein Verbindungsstring angegeben")
            return False
            
        # Bei der Drohne anmelden mit universeller connect-Methode
        try:
            # Bevorzugt die connectDrone-Methode verwenden (diese existiert im aktuellen ViewModel)
            if hasattr(self._drone_view_model, "connectDrone"):
                print(f"[DEBUG] Rufe _drone_view_model.connectDrone() auf mit: {connection_string}")
                return self._drone_view_model.connectDrone(connection_string)
            # Fallback auf die anderen Methoden (falls in anderen ViewModels vorhanden)
            elif hasattr(self._drone_view_model, "connect"):
                print(f"[DEBUG] Rufe _drone_view_model.connect() auf mit: {connection_string}")
                return self._drone_view_model.connect(connection_string)
            elif hasattr(self._drone_view_model, "connectToDrone"):
                print(f"[DEBUG] Rufe _drone_view_model.connectToDrone() auf mit: {connection_string}")
                return self._drone_view_model.connectToDrone(connection_string)
            else:
                print("[DEBUG] FEHLER: Keine passende connect-Methode im ViewModel gefunden")
                self.logMessageAdded.emit("[FEHLER] Keine passende connect-Methode im ViewModel gefunden")
                return False
        except Exception as e:
            print(f"[DEBUG] FEHLER beim Verbinden: {str(e)}")
            self.logMessageAdded.emit(f"[FEHLER] Verbindungsfehler: {str(e)}")
            return False
    
    @Slot()
    def disconnect(self):
        """Trennt die Verbindung (Kompatibilitätsmethode für QML)"""
        # Log-Nachricht ausgeben
        self.logMessageAdded.emit("[INFO] Trenne Verbindung...")
        
        # Versuche die disconnect-Methode zu finden und aufzurufen
        try:
            # Bevorzugt die disconnectDrone-Methode verwenden (diese existiert im aktuellen ViewModel)
            if hasattr(self._drone_view_model, "disconnectDrone"):
                return self._drone_view_model.disconnectDrone()
            # Fallback auf die disconnect-Methode (falls in anderen ViewModels vorhanden)
            elif hasattr(self._drone_view_model, "disconnect"):
                return self._drone_view_model.disconnect()
            else:
                self.logMessageAdded.emit("[FEHLER] Keine disconnect-Methode im ViewModel gefunden")
                return False
        except Exception as e:
            self.logMessageAdded.emit(f"[FEHLER] Fehler beim Trennen der Verbindung: {str(e)}")
            return False
    

            
    @Slot()
    def load_parameters(self):
        """Lädt Parameter vom Flight Controller (Kompatibilitätsmethode für QML)"""
        # Log-Nachricht ausgeben
        self.logMessageAdded.emit("[INFO] Lade Parameter vom Flight Controller...")
        
        # Versuche die Parameter-Lade-Methode zu finden und aufzurufen
        try:
            # Prüfe auf verschiedene mögliche Methoden-Namen
            if hasattr(self._drone_view_model, "load_parameters"):
                return self._drone_view_model.load_parameters()
            elif hasattr(self._drone_view_model, "loadParameters"):
                return self._drone_view_model.loadParameters()
            elif hasattr(self._drone_view_model, "get_parameters"):
                return self._drone_view_model.get_parameters()
            else:
                self.logMessageAdded.emit("[WARNUNG] Keine Parameter-Lade-Methode im ViewModel gefunden")
                self.fcImportantMessageReceived.emit("Parameter-Funktion nicht implementiert")
                return False
        except Exception as e:
            self.logMessageAdded.emit(f"[FEHLER] Fehler beim Laden der Parameter: {str(e)}")
            return False
    
    @Slot(bool)
    @Slot()
    def update_connection_status(self, is_connected=None):
        """Aktualisiert den Verbindungsstatus (Kompatibilitätsmethode für QML)"""
        if is_connected is None:
            # Lese den aktuellen Status aus dem ViewModel
            if hasattr(self._drone_view_model, '_model') and hasattr(self._drone_view_model._model, 'is_connected'):
                is_connected = self._drone_view_model._model.is_connected
            else:
                is_connected = self._is_connected
        
        self._handle_connection(is_connected)
        self.logMessageAdded.emit(f"[INFO] Verbindungsstatus aktualisiert: {'Verbunden' if is_connected else 'Getrennt'}")
        return is_connected
        
    # Verarbeitung von Flight Controller Nachrichten und Systeminformationen
    def _handle_fc_message(self, message):
        """Verarbeitet allgemeine Nachrichten vom Flight Controller"""
        print(f"[FC MESSAGE] {message}")
        # Sende die Nachricht an die UI
        self.logMessageAdded.emit(message)
        self.fcImportantMessageReceived.emit(message)
    
    def _handle_system_info(self, info_str):
        """Verarbeitet Systeminformationen vom Flight Controller"""
        self.fcImportantMessageReceived.emit(info_str)
    
    def _on_battery_updated(self, battery_info):
        """Callback für Battery-Updates"""
        try:
            self.batteryChanged.emit(
                battery_info['remaining_percent'],
                battery_info['voltage_v'],
                battery_info['current_a']
            )
            self.batteryLevelChanged.emit(battery_info['remaining_percent'])
        except Exception as e:
            self._logger.addLog(f"[FEHLER] Fehler bei Batterie-Update-Verarbeitung: {str(e)}")
    
    def _on_attitude_updated(self, attitude_info):
        """Callback für Attitude-Updates"""
        try:
            # Für alte QML-UIs beide Signale emittieren
            self.attitudeChanged.emit(
                attitude_info['roll_deg'],
                attitude_info['pitch_deg'],
                attitude_info['yaw_deg']
            )
            self.attitude_msg.emit(
                attitude_info['roll_deg'],
                attitude_info['pitch_deg'],
                attitude_info['yaw_deg']
            )
            
            # Heading separat emittieren
            self.headingChanged.emit(attitude_info['yaw_deg'])
        except Exception as e:
            self._logger.addLog(f"[FEHLER] Fehler bei Lage-Update-Verarbeitung: {str(e)}")
    
    def _on_position_updated(self, position_info):
        """Callback für Position-Updates"""
        try:
            self.positionChanged.emit(
                position_info['latitude_deg'],
                position_info['longitude_deg'],
                position_info['relative_altitude_m']
            )
        except Exception as e:
            self._logger.addLog(f"[FEHLER] Fehler bei Positions-Update-Verarbeitung: {str(e)}")
    
    def _on_gps_info_updated(self, gps_info):
        """Callback für GPS-Info-Updates"""
        try:
            self.gpsChanged.emit(
                gps_info['num_satellites'],
                gps_info['fix_type']
            )
        except Exception as e:
            self._logger.addLog(f"[FEHLER] Fehler bei GPS-Info-Update-Verarbeitung: {str(e)}")
    
    def _on_flight_mode_changed(self, flight_mode):
        """Callback für Flugmodus-Änderungen"""
        try:
            self.flightModeChanged.emit(flight_mode)
            # Wichtige Flugmodus-Änderungen auch als Nachricht anzeigen
            self.fcImportantMessageReceived.emit(f"Flugmodus: {flight_mode}")
        except Exception as e:
            self._logger.addLog(f"[FEHLER] Fehler bei Flugmodus-Update-Verarbeitung: {str(e)}")
    
    def _on_armed_state_changed(self, armed):
        """Callback für Armed-Status-Änderungen"""
        try:
            self.armedStateChanged.emit(armed)
            # Armed-Status-Änderungen als wichtige Nachricht anzeigen
            status = "ARMED" if armed else "DISARMED"
            self.fcImportantMessageReceived.emit(f"Flight Controller {status}")
        except Exception as e:
            self._logger.addLog(f"[FEHLER] Fehler bei Armed-Status-Update-Verarbeitung: {str(e)}")
    
    def _on_connection_state_changed(self, connected):
        """Callback für Verbindungsstatus-Änderungen"""
        try:
            self._is_connected = connected
            self.connectedChanged.emit(connected)
            self.connectionStatusChanged.emit(connected)
            
            # Bei Verbindung Parameter laden
            if connected:
                self._on_connection_established()
                
        except Exception as e:
            self._logger.addLog(f"[FEHLER] Fehler bei Verbindungsstatus-Update-Verarbeitung: {str(e)}")
    
    def _on_connection_established(self):
        """Wird aufgerufen, wenn eine Verbindung hergestellt wurde"""
        try:
            # Log-Nachricht
            self.logMessageAdded.emit("[INFO] Verbindung hergestellt, lade Parameter...")
            
            # Lade Parameter vom Flight Controller
            self.load_parameters()
        except Exception as e:
            self.logMessageAdded.emit(f"[FEHLER] Fehler beim Laden der Parameter: {str(e)}")
    
    # Legacy-Handler-Methoden für die alte DroneSignalHub
    
    def _on_battery_changed(self, battery_info):
        """Legacy-Handler für Batterie-Änderungen"""
        # Format konvertieren wenn nötig
        if isinstance(battery_info, dict):
            self._on_battery_updated(battery_info)
        else:
            # Alte Format: separate Werte oder anderes Objekt
            try:
                # Versuche als Objekt zu behandeln
                if hasattr(battery_info, 'remaining_percent') and hasattr(battery_info, 'voltage_v'):
                    battery_dict = {
                        'remaining_percent': battery_info.remaining_percent,
                        'voltage_v': battery_info.voltage_v,
                        'current_a': getattr(battery_info, 'current_a', 0.0)
                    }
                    self._on_battery_updated(battery_dict)
                # Falls es ein Tuple oder ähnliches ist
                elif isinstance(battery_info, (list, tuple)) and len(battery_info) >= 2:
                    battery_dict = {
                        'remaining_percent': battery_info[0],
                        'voltage_v': battery_info[1],
                        'current_a': battery_info[2] if len(battery_info) > 2 else 0.0
                    }
                    self._on_battery_updated(battery_dict)
                else:
                    self._logger.addLog(f"[WARNUNG] Unbekanntes Batterie-Info-Format: {type(battery_info)}")
            except Exception as e:
                self._logger.addLog(f"[FEHLER] Fehler bei Legacy-Batterie-Update: {str(e)}")
    
    def _on_attitude_changed(self, attitude_info):
        """Legacy-Handler für Lage-Änderungen"""
        # Format konvertieren wenn nötig
        if isinstance(attitude_info, dict):
            self._on_attitude_updated(attitude_info)
        else:
            try:
                # Versuche als Objekt zu behandeln
                if hasattr(attitude_info, 'roll_deg') and hasattr(attitude_info, 'pitch_deg'):
                    attitude_dict = {
                        'roll_deg': attitude_info.roll_deg,
                        'pitch_deg': attitude_info.pitch_deg,
                        'yaw_deg': attitude_info.yaw_deg
                    }
                    self._on_attitude_updated(attitude_dict)
                # Falls es ein Tuple oder ähnliches ist
                elif isinstance(attitude_info, (list, tuple)) and len(attitude_info) >= 3:
                    attitude_dict = {
                        'roll_deg': attitude_info[0],
                        'pitch_deg': attitude_info[1],
                        'yaw_deg': attitude_info[2]
                    }
                    self._on_attitude_updated(attitude_dict)
                else:
                    # Legacy-Format direkt an QML weitergeben
                    self.attitudeChanged.emit(
                        getattr(attitude_info, 'roll_deg', 0.0),
                        getattr(attitude_info, 'pitch_deg', 0.0),
                        getattr(attitude_info, 'yaw_deg', 0.0)
                    )
                    self.attitude_msg.emit(
                        getattr(attitude_info, 'roll_deg', 0.0),
                        getattr(attitude_info, 'pitch_deg', 0.0),
                        getattr(attitude_info, 'yaw_deg', 0.0)
                    )
                    self.headingChanged.emit(getattr(attitude_info, 'yaw_deg', 0.0))
            except Exception as e:
                self._logger.addLog(f"[FEHLER] Fehler bei Legacy-Lage-Update: {str(e)}")
    
    def _on_position_changed(self, position_info):
        """Legacy-Handler für Positions-Änderungen"""
        # Format konvertieren wenn nötig
        if isinstance(position_info, dict):
            self._on_position_updated(position_info)
        else:
            try:
                # Versuche als Objekt zu behandeln
                if hasattr(position_info, 'latitude_deg') and hasattr(position_info, 'longitude_deg'):
                    position_dict = {
                        'latitude_deg': position_info.latitude_deg,
                        'longitude_deg': position_info.longitude_deg,
                        'relative_altitude_m': getattr(position_info, 'relative_altitude_m', 0.0),
                        'absolute_altitude_m': getattr(position_info, 'absolute_altitude_m', 0.0)
                    }
                    self._on_position_updated(position_dict)
                else:
                    # Legacy-Format direkt an QML weitergeben
                    self.positionChanged.emit(
                        getattr(position_info, 'latitude_deg', 0.0),
                        getattr(position_info, 'longitude_deg', 0.0),
                        getattr(position_info, 'relative_altitude_m', 0.0)
                    )
            except Exception as e:
                self._logger.addLog(f"[FEHLER] Fehler bei Legacy-Positions-Update: {str(e)}")
    
    def _on_gps_info_changed(self, gps_info):
        """Legacy-Handler für GPS-Info-Änderungen"""
        # Format konvertieren wenn nötig
        if isinstance(gps_info, dict):
            self._on_gps_info_updated(gps_info)
        else:
            try:
                # Versuche als Objekt zu behandeln
                if hasattr(gps_info, 'num_satellites') and hasattr(gps_info, 'fix_type'):
                    gps_dict = {
                        'num_satellites': gps_info.num_satellites,
                        'fix_type': gps_info.fix_type
                    }
                    self._on_gps_info_updated(gps_dict)
                else:
                    # Legacy-Format direkt an QML weitergeben
                    self.gpsChanged.emit(
                        getattr(gps_info, 'num_satellites', 0),
                        getattr(gps_info, 'fix_type', 0)
                    )
            except Exception as e:
                self._logger.addLog(f"[FEHLER] Fehler bei Legacy-GPS-Info-Update: {str(e)}")
    
    def _on_armed_changed(self, armed):
        """Legacy-Handler für Armed-Status-Änderungen"""
        try:
            self._on_armed_state_changed(armed)
        except Exception as e:
            self._logger.addLog(f"[FEHLER] Fehler bei Legacy-Armed-Status-Update: {str(e)}")
    
    # Methoden für den Motortest
    @Slot(int)
    def startMotorTest(self, motorNumber):
        """Startet den Test für einen bestimmten Motor"""
        print(f"[INFO] Starte Test für Motor {motorNumber}")
        # Melde Motor als aktiv
        self.motorStatusChanged.emit(motorNumber, True, f"Motor {motorNumber} läuft")
        self.logMessageAdded.emit(f"Motor {motorNumber} Test gestartet")
        
        # Simuliere Fortschritt (in einer echten Implementierung würde hier die tatsächliche Motorsteuerung stattfinden)
        import threading
        def run_motor_test():
            import time
            # Fortschritt simulieren
            for i in range(0, 101, 10):
                self.testProgressChanged.emit(i, f"Motor {motorNumber} Test: {i}%")
                time.sleep(0.5)
            # Motor stoppen
            self.motorStatusChanged.emit(motorNumber, False, f"Motor {motorNumber} gestoppt")
            self.logMessageAdded.emit(f"Motor {motorNumber} Test abgeschlossen")
            self.testFinished.emit(True, "Test erfolgreich abgeschlossen")
        
        # Test in separatem Thread starten
        threading.Thread(target=run_motor_test, daemon=True).start()
    
    @Slot()
    def stopAllMotors(self):
        """Stoppt alle Motoren"""
        print("[INFO] Stoppe alle Motoren")
        for motor in range(1, 5):
            self.motorStatusChanged.emit(motor, False, f"Motor {motor} gestoppt")
        self.logMessageAdded.emit("Alle Motoren gestoppt")
        self.testFinished.emit(True, "Test abgebrochen")
    
    @Slot()
    def runMotorSequence(self):
        """Führt eine Testsequenz für alle Motoren durch"""
        print("[INFO] Starte Motortest-Sequenz")
        self.logMessageAdded.emit("Motortest-Sequenz gestartet")
        
        # Sequenz in separatem Thread starten
        import threading
        def run_sequence():
            import time
            for motor in range(1, 5):
                # Motor starten
                self.motorStatusChanged.emit(motor, True, f"Motor {motor} läuft")
                self.logMessageAdded.emit(f"Motor {motor} gestartet")
                self.testProgressChanged.emit(motor * 25, f"Teste Motor {motor}")
                
                # Warte 2 Sekunden
                time.sleep(2)
                
                # Motor stoppen
                self.motorStatusChanged.emit(motor, False, f"Motor {motor} gestoppt")
                self.logMessageAdded.emit(f"Motor {motor} gestoppt")
            
            # Sequenz abgeschlossen
            self.testFinished.emit(True, "Motortest-Sequenz abgeschlossen")
            self.testProgressChanged.emit(0, "Bereit")
        
        # Sequenz starten
        threading.Thread(target=run_sequence, daemon=True).start()
            
    # Weitere Methoden, die in QML verwendet werden
    
    @Slot()
    def refreshPorts(self):
        """Aktualisiert und gibt verfügbare Ports zurück"""
        ports = self.load_ports()
        self.portsRefreshed.emit(ports)
        return ports
        
    @Property(list)
    def ports(self):
        """Gibt die aktuell verfügbaren Ports zurück"""
        if hasattr(self._drone_view_model, 'ports'):
            return self._drone_view_model.ports
        else:
            return self.load_ports()
            
    # WICHTIG: Property 'availablePorts' für QML-Kompatibilität (PreflightView.ui.qml:497)
    @Property(list)
    def availablePorts(self):
        """Gibt verfügbare Ports für QML-Kompatibilität zurück"""
        return self.ports
        
    # --------------------------------
    # Neue Callback-Methoden für die erweiterten Telemetrie-Signale
    # --------------------------------
    
    def _on_in_air_changed(self, in_air):
        """Callback für In-Air-Status-Änderungen"""
        if hasattr(self._drone_view_model, 'setInAir'):
            self._drone_view_model.setInAir(in_air)
    
    def _on_health_updated(self, health_info):
        """Callback für Gesundheitsstatus-Updates"""
        if hasattr(self._drone_view_model, 'setHealthStatus'):
            self._drone_view_model.setHealthStatus(health_info)
    
    def _on_health_all_ok_changed(self, all_ok):
        """Callback für Gesamt-Gesundheitsstatus-Änderungen"""
        if hasattr(self._drone_view_model, 'setHealthAllOk'):
            self._drone_view_model.setHealthAllOk(all_ok)
    
    def _on_heading_updated(self, heading):
        """Callback für Heading-Updates"""
        if hasattr(self._drone_view_model, 'setHeading'):
            self._drone_view_model.setHeading(heading)
            
        # Compatibility-Signal für QML emittieren
        self.headingChanged.emit(heading)
    
    def _on_angular_velocity_updated(self, velocity_info):
        """Callback für Winkelgeschwindigkeits-Updates"""
        if hasattr(self._drone_view_model, 'setAngularVelocity'):
            self._drone_view_model.setAngularVelocity(velocity_info)
    
    def _on_status_text_received(self, text_info):
        """Callback für Status-Text-Nachrichten"""
        if hasattr(self._drone_view_model, 'setStatusText'):
            self._drone_view_model.setStatusText(text_info)
            
        # Wichtige Nachrichten in der UI anzeigen
        text = text_info.get("text", "")
        msg_type = text_info.get("type", "INFO")
        if "WARNING" in msg_type or "ERROR" in msg_type or "CRITICAL" in msg_type:
            self.fcImportantMessageReceived.emit(text)
    
    def _on_altitude_updated(self, altitude_info):
        """Callback für Höhen-Updates"""
        if hasattr(self._drone_view_model, 'setAltitudeInfo'):
            self._drone_view_model.setAltitudeInfo(altitude_info)
    
    def _on_landed_state_changed(self, state_str):
        """Callback für Landezustands-Änderungen"""
        if hasattr(self._drone_view_model, 'setLandedState'):
            self._drone_view_model.setLandedState(state_str)
    
    def _on_rc_status_updated(self, rc_info):
        """Callback für RC-Status-Updates"""
        if hasattr(self._drone_view_model, 'setRcStatus'):
            self._drone_view_model.setRcStatus(rc_info)
    
    def _on_unix_epoch_time_updated(self, time_us):
        """Callback für Unix-Zeit-Updates"""
        if hasattr(self._drone_view_model, 'setUnixEpochTime'):
            self._drone_view_model.setUnixEpochTime(time_us)
    
    def _on_actuator_control_updated(self, control_info):
        """Callback für Aktuator-Steuerungs-Updates"""
        if hasattr(self._drone_view_model, 'setActuatorControl'):
            self._drone_view_model.setActuatorControl(control_info)
    
    def _on_actuator_output_updated(self, output_info):
        """Callback für Aktuator-Ausgabe-Updates"""
        if hasattr(self._drone_view_model, 'setActuatorOutput'):
            self._drone_view_model.setActuatorOutput(output_info)
    
    def _on_odometry_updated(self, odometry_info):
        """Callback für Odometrie-Updates"""
        if hasattr(self._drone_view_model, 'setOdometry'):
            self._drone_view_model.setOdometry(odometry_info)
    
    def _on_distance_sensor_updated(self, distance_info):
        """Callback für Distanzsensor-Updates"""
        if hasattr(self._drone_view_model, 'setDistanceSensor'):
            self._drone_view_model.setDistanceSensor(distance_info)
    
    def _on_scaled_pressure_updated(self, pressure_info):
        """Callback für Drucksensor-Updates"""
        if hasattr(self._drone_view_model, 'setScaledPressure'):
            self._drone_view_model.setScaledPressure(pressure_info)
    
    def _on_raw_imu_updated(self, imu_info):
        """Callback für Raw IMU Updates"""
        if hasattr(self._drone_view_model, 'setRawImu'):
            self._drone_view_model.setRawImu(imu_info)
            
    def _on_parameters_updated(self, parameter_list):
        """Callback für Parameter-Updates"""
        if hasattr(self._drone_view_model, 'setParameters'):
            self._drone_view_model.setParameters(parameter_list)
            # Log-Nachricht für Debug-Zwecke
            if hasattr(self, '_logger'):
                self._logger.addLog(f"[INFO] {len(parameter_list)} Parameter empfangen")
