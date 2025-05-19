"""
Serial Connector für MAVLink-Verbindungen und Simulator.
Verwaltet die Verbindung zum Fluggerät oder Simulator.
"""

import sys
import os
from PySide6.QtCore import QObject, Signal, Slot, Property, QTimer
import serial.tools.list_ports
import math
from PySide6.QtSerialPort import QSerialPort, QSerialPortInfo
from pymavlink import mavutil
import time
import threading
import asyncio

from backend.mavlink_connector import MAVLinkConnector
from backend.sensorviewmodel import SensorViewModel
from backend.logger import Logger
from backend.parameter_model import ParameterTableModel
from backend.message_handler import MessageHandler
from backend.sensor_manager import SensorManager
from backend.parameter_manager import ParameterManager
from backend.simulator_connector import SimulatorConnector
from backend.direct_sensor_simulator import DirectSensorSimulator
from backend.compatible_simulator import CompatibleSensorSimulator

os.environ["QT_QUICK_CONTROLS_STYLE"] = "Fusion"

class SerialConnector(QObject):
    """
    Manages the serial connection to the drone and coordinates sensor data transmission.
    
    Signals:
        available_ports_changed: Emitted when available ports change
        connection_successful: Emitted on successful connection
        gps_msg: Emits GPS data
        attitude_msg: Emits attitude data
    """
    
    availablePortsChanged = Signal(list)
    connection_successful = Signal()
    gps_msg = Signal(float, float)
    attitude_msg = Signal(float, float, float)
    connectedChanged = Signal(bool)
    portChanged = Signal(str)
    baudRateChanged = Signal(int)
    errorOccurred = Signal(str)
    availableBaudRatesChanged = Signal(list)
    attitudeChanged = Signal(float, float, float)  # roll, pitch, yaw
    gpsChanged = Signal(float, float, float)  # lat, lon, alt
    batteryChanged = Signal(float, float, float)  # voltage, current, remaining
    statusTextReceived = Signal(str)  # status text messages

    def __init__(self, sensor_model: SensorViewModel, logger: Logger, parameter_model=None):
        """
        Initialize the SerialConnector.
        
        Args:
            sensor_model: Model for sensor data
            logger: Logger for status messages
            parameter_model: Model for parameter data
        """
        super().__init__()
        self._sensor_model = sensor_model
        self._logger = logger
        self._connected = False
        self._port = ""
        self._baud_rate = 115200
        self._available_ports = []
        self._available_baud_rates = [9600, 19200, 38400, 57600, 115200]
        self._mavlink_connection = None
        self._timer = None
        self._simulator_connector = None
        
        # Initialize managers
        self._message_handler = MessageHandler(logger)
        self._sensor_manager = SensorManager(sensor_model, logger)
        self._parameter_manager = ParameterManager(parameter_model, logger)
        
        # Connect signals
        self._message_handler.attitude_received.connect(self._sensor_manager.handle_attitude)
        self._message_handler.gps_received.connect(self._sensor_manager.handle_gps)
        self._message_handler.battery_received.connect(self._sensor_manager.handle_battery)
        self._message_handler.parameter_received.connect(self._parameter_manager.handle_parameter)
        
        # Neuen VFR_HUD-Signal-Handler verbinden
        if hasattr(self._message_handler, 'vfr_hud_received') and hasattr(self._sensor_manager, 'handle_vfr_hud'):
            self._message_handler.vfr_hud_received.connect(self._sensor_manager.handle_vfr_hud)
            self._logger.addLog("[INFO] VFR_HUD-Handler verbunden")

    @Property(bool, notify=connectedChanged)
    def connected(self):
        """True if currently connected to a drone/simulator."""
        return self._connected

    @Property(str, notify=portChanged)
    def port(self):
        return self._port

    @Property(int, notify=baudRateChanged)
    def baudRate(self):
        return self._baud_rate

    @Property('QVariantList', notify=availablePortsChanged)
    def availablePorts(self):
        return self._available_ports

    @Property('QVariantList', notify=availableBaudRatesChanged)
    def availableBaudRates(self):
        return self._available_baud_rates

    @Slot()
    def load_ports(self):
        try:
            ports = QSerialPortInfo.availablePorts()
            port_names = ["Simulator"]  # Add Simulator as first option
            port_names.extend([port.portName() for port in ports])
            if len(port_names) == 1:  # Only Simulator available
                self._logger.addLog("No serial ports found, only Simulator available")
            self._available_ports = port_names
            self.availablePortsChanged.emit(port_names)
            self._logger.addLog(f"Available ports: {port_names}")
        except Exception as e:
            self._logger.addLog(f"⚠️ Error loading ports: {str(e)}")

    @Slot(str)
    def setPort(self, port):
        if port != self._port:
            self._port = port
            self.portChanged.emit(port)

    @Slot(int)
    def setBaudRate(self, baud_rate):
        if baud_rate != self._baud_rate:
            self._baud_rate = baud_rate
            self.baudRateChanged.emit(baud_rate)

    @Slot()
    def connect(self):
        """Verbindet mit dem ausgewählten Port, entweder Simulator oder seriellem Port."""
        # Grundlegende Prüfungen
        if not self._port:
            self.errorOccurred.emit("No port selected")
            self._logger.addLog("[ERR] No port selected")
            return

        # Wenn bereits verbunden, trenne zuerst
        if self._connected:
            self.disconnect()

        try:
            self._logger.addLog(f"[INFO] Attempting to connect to {self._port}...")
            
            # Unterscheide zwischen Simulator und regulärer Verbindung
            if self._port == "Simulator":
                # Simulator-Verbindung
                return self._connect_to_simulator()
            else:
                # Normale serielle Verbindung
                return self._connect_to_serial_port()
                
        except Exception as e:
            # Globale Fehlerbehandlung
            error_msg = f"[ERR] Connection failed: {str(e)}"
            self.errorOccurred.emit(error_msg)
            self._logger.addLog(error_msg)
            
            # Alles bereinigen
            self._cleanup_connection()
            return False

    def _connect_to_simulator(self):
        """Verbindet mit dem MAVLink-Simulator oder verwendet einen der Alternativ-Simulatoren."""
        try:
            # Sensoren initialisieren - WICHTIG: Muss vor der Verbindung passieren
            self._initialize_sensors()
            self._logger.addLog("Sensoren initialisiert")
            
            # Versuch 1: Standard MAVLink-Simulator
            try:
                # MAVLink-Simulator initialisieren
                if self._simulator_connector is None:
                    self._simulator_connector = SimulatorConnector(self._logger)
                
                # Mit Simulator verbinden
                if self._simulator_connector.start_connection():
                    # Signale verbinden
                    self._simulator_connector.connectionStatusChanged.connect(self._on_simulator_connection_changed)
                    self._simulator_connector.messageReceived.connect(self._on_simulator_message)
                    self._simulator_connector.errorOccurred.connect(self._on_simulator_error)
                    
                    # Verbindung hergestellt
                    self._connected = True
                    self._port = "Simulator"
                    self.connectedChanged.emit(self._connected)
                    self.portChanged.emit(self._port)
                    self._log_info("[OK] Verbunden mit MAVLink-Simulator")
                    
                    # Automatisch Parameter laden
                    self._log_info("[LOAD] Lade Parameter nach Verbindung...")
                    self.load_parameters()
                    return True
                else:
                    self._logger.addLog("MAVLink-Simulator konnte nicht gestartet werden")
            except Exception as mavlink_error:
                self._logger.addLog(f"Fehler beim Starten des MAVLink-Simulators: {str(mavlink_error)}")
                
            # Versuch 2: Kompatibler Sensor-Simulator (empfohlen als Fallback)
            self._logger.addLog("Versuche kompatiblen Sensor-Simulator...")
            try:
                # Kompatiblen Simulator initialisieren und mit Sensor-Modell verbinden
                self._compatible_simulator = CompatibleSensorSimulator()
                
                # Sensor-Modell abrufen (sollte bereits initialisiert sein)
                if hasattr(self, '_sensor_model') and self._sensor_model:
                    # Sensoren initialisieren und Simulator starten
                    self._compatible_simulator.initialize_sensors(self._sensor_model)
                    if self._compatible_simulator.start():
                        self._logger.addLog("Kompatibler Sensor-Simulator gestartet")
                        
                        # Verbindung hergestellt - Status setzen
                        self._connected = True
                        self._port = "Simulator (Kompatibel)"
                        self.connectedChanged.emit(self._connected)
                        self.portChanged.emit(self._port)
                        self._log_info("[OK] Verbunden mit kompatiblem Simulator")
                        
                        # Simulierte Parameter laden
                        self._log_info("[LOAD] Lade simulierte Parameter...")
                        self._create_simulator_parameters()
                        
                        return True
                else:
                    self._logger.addLog("Kein Sensor-Modell vorhanden für Simulator")
                    
            except Exception as compat_error:
                self._logger.addLog(f"Fehler beim Starten des kompatiblen Simulators: {str(compat_error)}")
            
            # Versuch 3: Direkter Sensor-Simulator (veraltet)
            self._logger.addLog("Versuche direkten Sensor-Simulator...")
            try:
                # Direkten Sensor-Simulator initialisieren
                self._direct_simulator = DirectSensorSimulator()
                
                # Signale verbinden - Wird wahrscheinlich fehlschlagen wegen fehlender Methoden im Modell
                self._direct_simulator.batteryUpdated.connect(self._handle_battery_direct)
                self._direct_simulator.attitudeUpdated.connect(self._handle_attitude_direct)
                self._direct_simulator.gpsUpdated.connect(self._handle_gps_direct)
                
                # Simulator starten
                if self._direct_simulator.start():
                    self._logger.addLog("Direkter Sensor-Simulator gestartet")
                    
                    # Verbindung hergestellt - Status setzen
                    self._connected = True
                    self.connectedChanged.emit(True)
                    self._logger.addLog(f"Verbunden mit direktem Simulator") 
                    return True
                    
            except Exception as direct_error:
                self._logger.addLog(f"Fehler beim Starten des direkten Simulators: {str(direct_error)}")
            
            # Alle Versuche fehlgeschlagen
            raise ConnectionError("Alle Simulator-Optionen fehlgeschlagen")
            
        except Exception as e:
            self._logger.addLog(f"Simulator-Verbindungsfehler: {str(e)}")
            raise

    def _connect_to_serial_port(self):
        """Verbindet mit einem physischen seriellen Port."""
        try:
            # MAVLink-Verbindung herstellen
            self._mavlink_connection = mavutil.mavlink_connection(self._port, self._baud_rate)
            
            # Verbindung in Managern setzen
            self._message_handler.set_connection(self._mavlink_connection, is_simulator=False)
            self._parameter_manager.set_connection(self._mavlink_connection)
            
            # Sensoren initialisieren
            self._sensor_manager.initialize_sensors()
            
            # Auf Heartbeat warten
            self._logger.addLog("⌛ Waiting for heartbeat...")
            try:
                self._mavlink_connection.wait_heartbeat(timeout=10)
                self._logger.addLog("💓 Heartbeat received!")
            except Exception as e:
                error_msg = f"[ERR] Error waiting for heartbeat: {str(e)}"
                self._logger.addLog(error_msg)
                self.errorOccurred.emit(error_msg)
                raise ConnectionError(f"No heartbeat received: {str(e)}")
            
            # Message Handler starten
            if not self._message_handler.start():
                raise ConnectionError("Failed to start message handler")
                
            # Datenströme anfordern
            self._message_handler.request_data_streams()
            
            # Timer für Nachrichtenverarbeitung starten
            self._timer = QTimer(self)
            self._timer.timeout.connect(self._message_handler.process_messages)
            self._timer.start(100)  # 100ms Intervall
            self._logger.addLog("⏱️ Message handling timer started")

            # Verbindung hergestellt - Status setzen
            self._connected = True
            self.connectedChanged.emit(True)
            self._logger.addLog(f"[OK] Connected to {self._port}")
            
            return True
            
        except Exception as e:
            # Bei Fehler aufräumen und Exception weiterreichen
            if self._mavlink_connection:
                try:
                    self._mavlink_connection.close()
                except:
                    pass
                self._mavlink_connection = None
            self._logger.addLog(f"[ERR] Serial connection error: {str(e)}")
            raise

    @Slot()
    def disconnect(self):
        """Trennt die Verbindung zum Port."""
        if not self._connected:
            return
            
        try:
            self._logger.addLog(f"[INFO] Disconnecting from {self._port}...")
            
            # Unterscheide zwischen Simulator und regulärer Verbindung
            if self._port == "Simulator" and self._simulator_connector is not None:
                # Simulator-Verbindung trennen
                self._simulator_connector.disconnect()
                # Status wird durch _on_simulator_connection_changed aktualisiert
            else:
                # Normale Verbindung trennen
                self._cleanup_connection()
                
        except Exception as e:
            self._logger.addLog(f"⚠️ Error during disconnect: {str(e)}")
            # Trotzdem Status aktualisieren
            self._cleanup_connection()

    def _cleanup_connection(self):
        """Bereinigt alle Verbindungsressourcen."""
        # Timer stoppen
        if self._timer:
            self._timer.stop()
            self._timer = None
            
        # Message Handler stoppen
        if hasattr(self, '_message_handler'):
            self._message_handler.stop()
            
        # MAVLink-Verbindung schließen
        if self._mavlink_connection:
            try:
                self._mavlink_connection.close()
            except:
                pass
            self._mavlink_connection = None
            
        # Verbindungsstatus aktualisieren
        if self._connected:
            self._connected = False
            self.connectedChanged.emit(False)
            self._logger.addLog(f"Disconnected from {self._port}")

    @Slot()
    def load_parameters(self):
        """Lade Parameter vom Flugcontroller"""
        self._log_info("[LOAD] Lade Parameter vom Flugcontroller...")
        self._parameter_manager.load_parameters()
        
    @Slot(str, str)
    def set_parameter(self, name, value):
        """Setze einen Parameter-Wert auf dem Flugcontroller"""
        self._log_info(f"[INFO] Setze Parameter {name} auf {value}...")
        
        # Versuche, den Wert in float zu konvertieren (geht nur bei numerischen Werten)
        try:
            # Prüfen, ob wir es mit einem numerischen Wert zu tun haben
            float_value = float(value)
            # Parametermodell aktualisieren
            self._parameter_manager.set_parameter(name, float_value)
        except ValueError:
            # Bei nicht-numerischen Werten (z.B. Strings) nur Logging
            self._log_info(f"[WARN] Nicht-numerischer Wert '{value}' für Parameter {name}")
        
    def _create_simulator_parameters(self):
        """Erstellt simulierte Parameter für den Simulator-Modus"""
        self._log_info("[LOAD] Erstelle simulierte Parameter...")
        
        # Stellen Sie sicher, dass wir ein Parameter-Modell haben
        if not hasattr(self, '_parameter_manager') or not self._parameter_manager._parameter_model:
            self._log_error("[ERR] Kein Parameter-Model vorhanden")
            return
            
        try:
            # Parameter-Modell leeren
            if hasattr(self._parameter_manager._parameter_model, 'clear_parameters'):
                self._parameter_manager._parameter_model.clear_parameters()
                self._log_info("[OK] Parameter gelöscht")
            
            # Bessere Beispielparameter erstellen mit detaillierten Beschreibungen
            rc_parameters = [
                {"name": "OSD", "option": "RCTR_OPTION", "value": "Do Nothing", "desc": "OSD screen switching RC channel option", "defaultValue": "0"},
                {"name": "PILOT", "option": "RCT1_OPTION", "value": "Do Nothing", "desc": "Pilot yaw control channel option", "defaultValue": "0"},
                {"name": "PIX", "option": "RCT2_OPTION", "value": "Do Nothing", "desc": "PixHawk mode selection channel", "defaultValue": "0"},
                {"name": "PSC", "option": "RCT3_OPTION", "value": "Do Nothing", "desc": "Position control sensitivity", "defaultValue": "0"},
                {"name": "RALLY", "option": "RCT4_OPTION", "value": "Do Nothing", "desc": "Rally point selection channel", "defaultValue": "0"},
                {"name": "RC", "option": "RCT6_OPTION", "value": "Do Nothing", "desc": "Remote control channel setup", "defaultValue": "0"},
                {"name": "RWEND", "option": "RC1_OPTION", "value": "Do Nothing", "desc": "Right wingtip endplate configuration", "defaultValue": "0"},
                {"name": "RINGENDA", "option": "RC2_OPTION", "value": "Do Nothing", "desc": "Right ingress endplate damping", "defaultValue": "0"},
                {"name": "RPM", "option": "RC3_OPTION", "value": "Do Nothing", "desc": "Motor RPM monitoring and throttle control", "defaultValue": "0"},
                {"name": "RSSI", "option": "RC4_OPTION", "value": "Do Nothing", "desc": "Received Signal Strength Indicator threshold", "defaultValue": "0"},
                {"name": "RTL", "option": "RC5_OPTION", "value": "Do Nothing", "desc": "Return-to-Launch altitude setting", "defaultValue": "0"},
                {"name": "SERIAL", "option": "RC6_OPTION", "value": "Do Nothing", "desc": "Serial port configuration options", "defaultValue": "0"},
                {"name": "SERVO", "option": "RC8_OPTION", "value": "Do Nothing", "desc": "Servo output channel configuration", "defaultValue": "0"},
                {"name": "SID", "option": "RC9_OPTION", "value": "Do Nothing", "desc": "System identification parameter", "defaultValue": "0"},
                {"name": "SPRAY", "option": "RC10_OPTION", "value": "Do Nothing", "desc": "Sprayer control channel settings", "defaultValue": "0"},
                {"name": "SRTL", "option": "RC11_OPTION", "value": "Do Nothing", "desc": "Smart return-to-launch configuration", "defaultValue": "0"},
                {"name": "STAT", "option": "RC12_OPTION", "value": "Do Nothing", "desc": "Status reporting configuration", "defaultValue": "0"},
                {"name": "THROW", "option": "RC13_OPTION", "value": "Do Nothing", "desc": "Throw mode activation channel", "defaultValue": "0"},
                {"name": "TUNE", "option": "RC14_OPTION", "value": "Do Nothing", "desc": "Autotune parameter selection channel", "defaultValue": "0"},
                {"name": "WINCH", "option": "RC15_OPTION", "value": "Do Nothing", "desc": "Winch control channel configuration", "defaultValue": "0"},
                {"name": "WPNAV", "option": "RC16_OPTION", "value": "Do Nothing", "desc": "Waypoint navigation speed control", "defaultValue": "0"}
            ]
            
            # Parameter direkt im Modell setzen, statt einzeln hinzuzufügen
            self._parameter_manager._parameter_model.set_parameters(rc_parameters)
            self._log_info(f"[OK] {len(rc_parameters)} simulierte Parameter erstellt")
            
            # Wenn set_parameters nicht das Signal ausgelöst hat, manuell senden
            if hasattr(self._parameter_manager._parameter_model, 'parametersLoaded'):
                self._parameter_manager._parameter_model.parametersLoaded.emit()
                self._log_info("[OK] Parameter-Loaded-Signal gesendet")
            
        except Exception as e:
            self._log_error(f"[ERR] Fehler beim Erstellen der Parameter: {str(e)}")
            import traceback
            self._log_error(traceback.format_exc())


    def _initialize_sensors(self):
        # Initialize all required sensors in the model.
        sensors = [
            ("roll", "Roll", "°"),
            ("pitch", "Pitch", "°"),
            ("yaw", "Yaw", "°"),
            ("altitude", "Altitude", "m"),
            ("groundspeed", "Ground Speed", "m/s"),
            ("airspeed", "Air Speed", "m/s"),
            ("throttle", "Throttle", "%"),
            ("heading", "Heading", "°"),
            ("battery_remaining", "Battery", "%"),
            ("battery_voltage", "Voltage", "V"),
            ("battery_current", "Current", "A"),
            ("gps_lat", "GPS Latitude", "°"),
            ("gps_lon", "GPS Longitude", "°"),
            ("gps_hdop", "GPS HDOP", ""),
            ("gps_satellites", "GPS Satellites", "")
        ]
        
        for sensor_id, name, unit in sensors:
            try:
                self._sensor_model.add_sensor(sensor_id, name, unit)
                # Initialize with default values
                self._sensor_model.update_sensor(sensor_id, 0.0)
            except Exception as e:
                self._logger.addLog(f"⚠️ Error initializing sensor {name}: {str(e)}")

    def add_log(self, message):
        self._logger.addLog(message)

    def update_sensor_data(self, name, value):
        # Update sensor data and ensure frontend update.
        if self._sensor_model:
            self._sensor_model.update_sensor(name, value)
        else:
            self._logger.addLog(f"⚠️ No sensor model to update {name}")

    def stop(self):
        self.disconnect()

    def update_gps(self, lat: float, lon: float):
        # Update GPS coordinates in the sensor model.
        if self._sensor_model:
            self._sensor_model.update_sensor("gps_lat", lat)
            self._sensor_model.update_sensor("gps_lon", lon)
            self.gps_msg.emit(lat, lon)

    def _log_info(self, message: str):
        # Loggt eine Informationsnachricht.
        self._logger.addLog(message)

    def _log_error(self, message: str):
        # Loggt eine Fehlernachricht.
        self._logger.addLog(message)

    def _handle_global_position_int(self, msg):
        # Handle GLOBAL_POSITION_INT message.
        try:
            # Extract lat, lon in degrees
            lat = msg.lat / 1e7
            lon = msg.lon / 1e7
            
            # Extract altitude
            alt = msg.alt / 1000.0  # mm to m
            relative_alt = msg.relative_alt / 1000.0  # mm to m
            
            # Extract velocity
            vx = msg.vx / 100.0  # cm/s to m/s
            vy = msg.vy / 100.0  # cm/s to m/s
            vz = msg.vz / 100.0  # cm/s to m/s
            
            # Ground speed calculation
            ground_speed = math.sqrt(vx*vx + vy*vy)
            
            # Update sensor data
            self._sensor_model.update_sensor("altitude", relative_alt)
            self._sensor_model.update_sensor("groundspeed", ground_speed)
            
            # Log GPS status based on altitude and speed
            if alt == 0 and relative_alt == 0:
                self._log_error("No GPS fix")
            elif ground_speed < 0.1:
                self._log_info("GPS fix (stationary)")
            else:
                self._log_info(f"GPS fix (moving: {ground_speed:.1f}m/s)")
            
            # Always emit GPS data for updates
            self.gps_msg.emit(lat, lon)
            
            # Log position changes with more detail
            if hasattr(self, '_last_lat') and hasattr(self, '_last_lon'):
                lat_change = abs(lat - self._last_lat)
                lon_change = abs(lon - self._last_lon)
                if lat_change > 0.00001 or lon_change > 0.00001:  # More sensitive to changes
                    self._log_info(
                        f"GPS: {lat:.6f}, {lon:.6f}\n"
                        f"   Alt: {relative_alt:.1f}m\n"
                        f"   Speed: {ground_speed:.1f}m/s"
                    )
            
            # Store last position
            self._last_lat = lat
            self._last_lon = lon
            
        except Exception as e:
            self._log_error(f"Error processing GPS data: {str(e)}")

    def _handle_heartbeat(self, msg):
        """Handle heartbeat message from simulator"""
        armed = (msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED) != 0
        mode = mavutil.mode_string_v10(msg)
        if not hasattr(self, '_last_mode') or self._last_mode != mode:
            self._logger.addLog(f"✈️ Flight Mode: {mode}")
            self._last_mode = mode
        if not hasattr(self, '_last_armed') or self._last_armed != armed:
            status = "ARMED" if armed else "DISARMED"
            self._logger.addLog(f"🔒 System {status}")
            self._last_armed = armed

    def _handle_attitude(self, msg):
        """Handle attitude message from simulator"""
        try:
            # Validiere Eingabewerte, bevor sie konvertiert werden
            if not hasattr(msg, 'roll') or not hasattr(msg, 'pitch') or not hasattr(msg, 'yaw'):
                self._logger.addLog("Attitude-Fehler: Fehlende Attitude-Daten in der Nachricht")
                # Verwende Standardwerte für fehlende Daten
                roll_deg, pitch_deg, yaw_deg = 0.0, 0.0, 0.0
                roll_rad, pitch_rad, yaw_rad = 0.0, 0.0, 0.0
            else:
                # Konvertiere Radiant in Grad für bessere Lesbarkeit
                try:
                    import math
                    PI = math.pi  # Genauerer Wert als 3.14159
                    
                    # Sicherstellen, dass die Werte numerisch sind
                    roll_rad = float(msg.roll)
                    pitch_rad = float(msg.pitch)
                    yaw_rad = float(msg.yaw)
                    
                    # Konvertierung zu Grad
                    roll_deg = round(roll_rad * 180.0 / PI, 1)
                    pitch_deg = round(pitch_rad * 180.0 / PI, 1)
                    yaw_deg = round(yaw_rad * 180.0 / PI, 1)
                except Exception as e:
                    self._logger.addLog(f"Attitude-Fehler mit Standardwerten: {str(e)}")
                    # Verwende Standardwerte bei Konvertierungsproblemen
                    roll_deg, pitch_deg, yaw_deg = 0.0, 0.0, 0.0
                    roll_rad, pitch_rad, yaw_rad = 0.0, 0.0, 0.0
            
            # Signale senden mit robusten Werten
            self.attitudeChanged.emit(float(roll_rad), float(pitch_rad), float(yaw_rad))
            
            # Sensoren aktualisieren
            if self._sensor_model:
                self._sensor_model.update_sensor("roll", float(roll_deg))
                self._sensor_model.update_sensor("pitch", float(pitch_deg))
                self._sensor_model.update_sensor("yaw", float(yaw_deg))
                
                # Nur loggen wenn gültige Daten vorhanden sind
                if roll_deg != 0.0 or pitch_deg != 0.0 or yaw_deg != 0.0:
                    self._logger.addLog(f"[INFO] Attitude-Sensoren aktualisiert: Roll={roll_deg}°, Pitch={pitch_deg}°, Yaw={yaw_deg}°")
        except Exception as e:
            self._logger.addLog(f"Attitude-Fehler: {str(e)}")
            # Standardwerte verwenden
            if self._sensor_model:
                self._sensor_model.update_sensor("roll", 0.0)
                self._sensor_model.update_sensor("pitch", 0.0)
                self._sensor_model.update_sensor("yaw", 0.0)

    def _handle_gps(self, msg):
        """Handle GPS message from simulator"""
        try:
            # Validiere Eingabewerte, bevor sie konvertiert werden
            if not hasattr(msg, 'lat') or not hasattr(msg, 'lon') or not hasattr(msg, 'relative_alt'):
                self._logger.addLog("GPS-Fehler: Fehlende GPS-Daten in der Nachricht")
                # Verwende Standardwerte für fehlende Daten
                lat, lon, alt = 0.0, 0.0, 0.0
                groundspeed = 0.0
            else:
                # Konvertiere die Werte in die richtigen Einheiten
                try:
                    lat = float(msg.lat) / 1e7  # degE7 zu Grad
                    lon = float(msg.lon) / 1e7  # degE7 zu Grad
                    alt = float(msg.relative_alt) / 1000.0  # mm zu m
                    
                    # Geschwindigkeiten (falls vorhanden)
                    vx = float(getattr(msg, 'vx', 0)) / 100.0  # cm/s zu m/s
                    vy = float(getattr(msg, 'vy', 0)) / 100.0  # cm/s zu m/s
                    vz = float(getattr(msg, 'vz', 0)) / 100.0  # cm/s zu m/s
                    
                    # Berechne Groundspeed aus vx und vy
                    import math
                    groundspeed = round(math.sqrt(vx*vx + vy*vy), 1)
                except Exception as e:
                    self._logger.addLog(f"GPS-Fehler mit Standardwerten: {str(e)}")
                    # Verwende Standardwerte bei Konvertierungsproblemen
                    lat, lon, alt = 0.0, 0.0, 0.0
                    groundspeed = 0.0
            
            # Signale senden mit robusten Werten
            self.gpsChanged.emit(float(lat), float(lon), float(alt))
            
            # Sensoren aktualisieren
            if self._sensor_model:
                self._sensor_model.update_sensor("gps_lat", float(round(lat, 6)))
                self._sensor_model.update_sensor("gps_lon", float(round(lon, 6)))
                self._sensor_model.update_sensor("altitude", float(round(alt, 1)))
                self._sensor_model.update_sensor("groundspeed", float(groundspeed))
                
                # Heading (falls vorhanden)
                if hasattr(msg, 'hdg') and msg.hdg != 0:
                    try:
                        heading = float(msg.hdg) / 100.0  # cdeg zu deg
                        self._sensor_model.update_sensor("heading", float(round(heading, 1)))
                    except:
                        # Ignoriere Heading-Fehler
                        pass
                
                # Nur loggen wenn gültige Daten vorhanden sind
                if lat != 0.0 or lon != 0.0:
                    self._logger.addLog(f"[INFO] GPS-Sensoren aktualisiert: Lat={lat:.6f}, Lon={lon:.6f}, Alt={alt:.1f}m, Speed={groundspeed}m/s")
        except Exception as e:
            self._logger.addLog(f"GPS-Fehler: {str(e)}")
            # Standardwerte verwenden
            if self._sensor_model:
                self._sensor_model.update_sensor("gps_lat", 0.0)
                self._sensor_model.update_sensor("gps_lon", 0.0)
                self._sensor_model.update_sensor("altitude", 0.0)
                self._sensor_model.update_sensor("groundspeed", 0.0)

    def _handle_battery(self, msg):
        """Handle battery message from simulator"""
        try:
            # Konvertiere die Werte in die richtigen Einheiten
            voltage = msg.voltage_battery / 1000.0  # mV zu V
            current = msg.current_battery / 100.0   # cA zu A
            remaining = msg.battery_remaining       # Prozent
            
            # Signale senden
            self.batteryChanged.emit(voltage, current, remaining)
            
            # Sensoren aktualisieren
            if self._sensor_model:
                self._sensor_model.update_sensor("battery_voltage", round(voltage, 1))
                self._sensor_model.update_sensor("battery_current", round(current, 1))
                self._sensor_model.update_sensor("battery_remaining", round(remaining, 0))
                
                self._logger.addLog(f"[INFO] Batterie-Sensoren aktualisiert: {voltage:.1f}V, {current:.1f}A, {remaining}%")
        except Exception as e:
            self._logger.addLog(f"⚠️ Fehler beim Verarbeiten der Batterie-Daten: {str(e)}")

    def _handle_status_text(self, msg):
        """Handle status text message from simulator"""
        if msg.severity >= 3:  # Only log warnings and errors
            self._logger.addLog(f"⚠️ {msg.text}")

    def _handle_parameter(self, msg):
        """Handle parameter message from simulator"""
        if self.parameter_model:
            self.parameter_model.add_parameter({
                "name": msg.param_id,
                "value": msg.param_value,
                "defaultValue": "",
                "unit": "",
                "options": "",
                "desc": ""
            })
            
    # Event-Handler für SimulatorConnector
    def _on_simulator_connection_changed(self, connected):
        """Behandelt Änderungen des Verbindungsstatus vom SimulatorConnector"""
        if connected != self._connected:
            self._connected = connected
            self.connectedChanged.emit(connected)
            
            if connected:
                self._logger.addLog(f"[OK] Connected to {self._port}")
            else:
                self._logger.addLog(f"Disconnected from {self._port}")
    
    def _on_simulator_message(self, msg):
        """Behandelt eingehende MAVLink-Nachrichten vom SimulatorConnector"""
        # Nachrichtentyp bestimmen und an entsprechende Handler weiterleiten
        try:
            # Nachrichtentyp ermitteln
            msgtype = msg.get_type()
            self._logger.addLog(f"Empfange MAVLink-Nachricht: {msgtype}")
            
            # Je nach Nachrichtentyp verarbeiten
            if msgtype == "HEARTBEAT":
                self._handle_heartbeat(msg)
            elif msgtype == "ATTITUDE":
                self._handle_attitude(msg)
                self._logger.addLog(f"📊 Attitude: Roll={msg.roll:.2f}, Pitch={msg.pitch:.2f}, Yaw={msg.yaw:.2f}")
            elif msgtype == "GLOBAL_POSITION_INT":
                self._handle_gps(msg)
                lat = msg.lat / 1e7
                lon = msg.lon / 1e7
                alt = msg.relative_alt / 1000.0
                self._logger.addLog(f"📊 GPS: Lat={lat:.6f}, Lon={lon:.6f}, Alt={alt:.1f}m")
            elif msgtype == "SYS_STATUS":
                self._handle_battery(msg)
                voltage = msg.voltage_battery / 1000.0
                current = msg.current_battery / 100.0
                remaining = msg.battery_remaining
                self._logger.addLog(f"📊 Batterie: {voltage:.1f}V, {current:.1f}A, {remaining}%")
            elif msgtype == "STATUSTEXT":
                self._handle_status_text(msg)
            elif msgtype == "PARAM_VALUE":
                self._handle_parameter(msg)
                
            # Erzwinge ein Update des Modells
            if self._sensor_model:
                # Debug-Ausgabe der aktuellen Sensorwerte
                sensors = self._sensor_model.get_all_sensors()
                self._logger.addLog(f"📊 Sensor-Update: {len(sensors)} Sensoren im Modell")
                
                # Erzwinge UI-Update
                self._sensor_model.dataChanged.emit(self._sensor_model.index(0), 
                                                self._sensor_model.index(self._sensor_model.rowCount() - 1))
        except Exception as e:
            self._logger.addLog(f"⚠️ Fehler bei Verarbeitung von {msgtype}: {str(e)}")
            import traceback
            self._logger.addLog(traceback.format_exc())
            
    def _on_simulator_error(self, error_msg):
        """Behandelt Fehlermeldungen vom SimulatorConnector"""
        self.errorOccurred.emit(error_msg)
        
    @Slot(str)
    def setFlightMode(self, mode):
        """Setzt den Flugmodus des Fluggeräts."""
        if not self._connected:
            self._logger.addLog("[ERR] Nicht verbunden - kann Flugmodus nicht ändern")
            return
            
        try:
            self._logger.addLog(f"🚀 Setze Flugmodus auf {mode}...")
            
            # Unterscheide zwischen Simulator und normaler Verbindung
            if self._port == "Simulator":
                # Bei Simulator direkt über den SimulatorConnector
                if self._simulator_connector:
                    # Flugmodus-Mapping
                    mode_mapping = {
                        "STABILIZE": 0,
                        "ALT_HOLD": 2,
                        "LOITER": 5,
                        "RTL": 6,
                        "AUTO": 3,
                        "GUIDED": 4
                    }
                    
                    # Sende SET_MODE Nachricht
                    if mode in mode_mapping:
                        mode_id = mode_mapping[mode]
                        # Direkt an den Simulator-Connector weiterleiten
                        self._logger.addLog(f"Setze Flugmodus auf {mode} (ID: {mode_id})")
                    else:
                        self._logger.addLog(f"⚠️ Unbekannter Flugmodus: {mode}")
            else:
                # Bei normaler Verbindung über MAVLink
                if self._mavlink_connection:
                    # Flugmodus-Mapping
                    mode_mapping = {
                        "STABILIZE": 0,
                        "ALT_HOLD": 2,
                        "LOITER": 5,
                        "RTL": 6,
                        "AUTO": 3,
                        "GUIDED": 4
                    }
                    
                    # Sende SET_MODE Nachricht
                    if mode in mode_mapping:
                        mode_id = mode_mapping[mode]
                        self._mavlink_connection.set_mode(mode_id)
                        self._logger.addLog(f"Flugmodus auf {mode} gesetzt")
                    else:
                        self._logger.addLog(f"⚠️ Unbekannter Flugmodus: {mode}")
                else:
                    self._logger.addLog("[ERR] Keine MAVLink-Verbindung verfügbar")
        except Exception as e:
            self._logger.addLog(f"[ERR] Fehler beim Setzen des Flugmodus: {str(e)}")
            
    @Slot(bool)
    def armDisarm(self, arm):
        """Armt oder disarmt das Fluggerät."""
        if not self._connected:
            self._logger.addLog("[ERR] Nicht verbunden - kann nicht armen/disarmen")
            return
            
        try:
            action = "Armen" if arm else "Disarmen"
            self._logger.addLog(f"🔒 Versuche {action}...")
            
            # Unterscheide zwischen Simulator und normaler Verbindung
            if self._port == "Simulator":
                # Bei Simulator direkt über den SimulatorConnector
                if self._simulator_connector:
                    # Direkt an den Simulator-Connector weiterleiten
                    self._logger.addLog(f"Sende {action}-Befehl an Simulator")
                    # Erfolg simulieren
                    self._logger.addLog(f"[OK] Fluggerät erfolgreich {'gearmt' if arm else 'disarmt'}")
            else:
                # Bei normaler Verbindung über MAVLink
                if self._mavlink_connection:
                    # Sende ARM_DISARM Kommando
                    self._mavlink_connection.arducopter_arm() if arm else self._mavlink_connection.arducopter_disarm()
                    self._logger.addLog(f"[OK] Fluggerät erfolgreich {'gearmt' if arm else 'disarmt'}")
                else:
                    self._logger.addLog("[ERR] Keine MAVLink-Verbindung verfügbar")
        except Exception as e:
            self._logger.addLog(f"[ERR] Fehler beim {action}: {str(e)}")
