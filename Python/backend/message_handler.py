from PySide6.QtCore import QObject, Signal, Slot, QTimer
from pymavlink import mavutil
from .logger import Logger
import time
import math
import re

class MessageHandler(QObject):
    """Handles MAVLink message processing and distribution"""
    
    # Signals for different message types
    heartbeat_received = Signal(object)
    attitude_received = Signal(object)
    gps_received = Signal(object)
    battery_received = Signal(object)
    status_text_received = Signal(object)
    parameter_received = Signal(object)
    vfr_hud_received = Signal(object)  # Signal for VFR_HUD
    raw_message_received = Signal(bytes)  # Signal for raw MAVLink messages
    error_occurred = Signal(str)
    
    def __init__(self, logger: Logger):
        super().__init__()
        self._logger = logger
        self._running = False
        self._mavlink_connection = None
        self._is_simulator = False
        
        # Timer für die verzögerte Aktualisierung bestimmter Meldungen
        self._delayed_message_timer = QTimer(self)
        self._delayed_message_timer.timeout.connect(self._update_delayed_messages)
        self._delayed_message_timer.start(60000)  # Alle 60 Sekunden aktualisieren
        
        # Cache für verzögerte Nachrichten
        self._servo_output_raw_cache = None
        self._rc_channels_cache = None
        self._mission_current_cache = None
        self._sys_status_cache = None
        
        # Cache für Kalibrierungsstatus
        self._calibration_status = {
            'compass': {'needed': False, 'in_progress': False, 'last_update': 0},
            'accel': {'needed': False, 'in_progress': False, 'last_update': 0},
            'level': {'needed': False, 'in_progress': False, 'last_update': 0}
        }
        
        # Zeitpunkt der letzten UI-Aktualisierung
        self._last_ui_update_time = time.time()
        
    def _handle_statustext(self, msg):
        """
        Process STATUSTEXT messages from the flight controller
        
        Args:
            msg (MAVLink_statustext_message): The received STATUSTEXT message
        """
        try:
            # Extract text from the message and decode it
            # Handle both string and byte array formats
            if isinstance(msg.text, str):
                text = msg.text
            else:
                # For byte arrays, convert each byte to char
                text = "".join([chr(x) for x in msg.text if x != 0])
            
            # Ensure severity is an integer
            try:
                severity = int(msg.severity)
            except (ValueError, TypeError):
                severity = 6  # Default to INFO level
            
            # Log the message based on severity
            severity_text = "INFO"
            if severity < 4:
                severity_text = "ERROR"
            elif severity < 5:
                severity_text = "WARNING"
            elif severity < 7:
                severity_text = "INFO"
            else:
                severity_text = "DEBUG"
                
            log_message = f"[{severity_text}] {text}"
            self._logger.addLog(log_message)
            
            # Send signal for further processing
            self.status_text_received.emit({
                'text': text,
                'severity': severity,
                'severity_text': severity_text
            })
            
            # Systeminformationen an SensorManager weiterleiten
            if hasattr(self, '_sensor_manager') and self._sensor_manager:
                # Prüfe, ob es sich um relevante Systeminformationen handelt
                if "ArduCopter" in text or "ArduPlane" in text or "Frame:" in text or \
                   "Frame Type:" in text or "MicroAir" in text or "ChibiOS" in text or \
                   "NuttX" in text or "VERSION" in text:
                    self._sensor_manager.handle_system_info(text)
                    
                    # SensorView initialisiert, falls noch nicht geschehen
                    if not self._sensor_view_initialized and not self._sensor_update_timer.isActive():
                        self._start_sensor_view_updates()
            
        except Exception as e:
            self._logger.addLog(f"Error processing STATUSTEXT: {str(e)}")
            
    def _update_sensor_view(self):
        """Aktualisiert die SensorView mit den aktuellen Daten"""
        try:
            # Wenn kein SensorManager vorhanden ist, abbrechen
            if not hasattr(self, '_sensor_manager') or not self._sensor_manager:
                return
                
            # Wenn keine Verbindung vorhanden ist, abbrechen
            if not self._mavlink_connection or not self._running:
                return
                
            # Wenn noch nicht initialisiert, Systeminformationen anfordern
            if not self._sensor_view_initialized:
                self._request_sensor_view_data()
                self._sensor_view_initialized = True
                
        except Exception as e:
            self._logger.addLog(f"Error updating sensor view: {str(e)}")
            
    def _start_sensor_view_updates(self):
        """Startet den Timer für regelmäßige Updates der SensorView"""
        if hasattr(self, '_sensor_update_timer'):
            self._sensor_update_timer.start()
            self._logger.addLog("✅ SensorView updates started")
            
    def _request_sensor_view_data(self):
        """Fordert Daten vom Flugcontroller für die SensorView an"""
        try:
            self._logger.addLog("📊 Requesting data for SensorView...")
            
            # Request system banner (ArduPilot-spezifisch)
            self._mavlink_connection.mav.command_long_send(
                self._mavlink_connection.target_system,
                self._mavlink_connection.target_component,
                mavutil.mavlink.MAV_CMD_DO_SEND_BANNER,  # Request system banner
                0,  # Confirmation
                0, 0, 0, 0, 0, 0, 0  # Parameters (not used)
            )
            
            # Request parameter list (enthält oft Systeminfos)
            self._mavlink_connection.param_fetch_list()
            
            # Request specific parameters that might contain system info
            param_list = ["FRAME_CLASS", "FRAME_TYPE", "HW_TYPE", "INS_PRODUCT_ID"]
            for param in param_list:
                self._mavlink_connection.param_fetch_one(param)
                
            # Fordere einen Status-Report an, um Systeminformationen zu bekommen
            self._mavlink_connection.mav.statustext_send(
                mavutil.mavlink.MAV_SEVERITY_INFO,
                b"REQUEST_SYSINFO"
            )
            
            # Fordere den SensorManager auf, Systeminformationen anzufordern
            if hasattr(self, '_sensor_manager') and self._sensor_manager:
                self._sensor_manager.request_system_info()
                
        except Exception as e:
            self._logger.addLog(f"Error requesting sensor view data: {str(e)}")
        
    def set_sensor_manager(self, sensor_manager):
        """Setzt den SensorManager für die Kommunikation mit der SensorView"""
        self._sensor_manager = sensor_manager
        # Timer für die Aktualisierung der SensorView einrichten
        self._sensor_update_timer = QTimer(self)
        self._sensor_update_timer.timeout.connect(self._update_sensor_view)
        self._sensor_update_timer.setInterval(500)  # Alle 0.5 Sekunden aktualisieren
        
        # Verbinde Signale mit dem SensorManager
        self.attitude_received.connect(self._sensor_manager.handle_attitude)
        self.gps_received.connect(self._sensor_manager.handle_gps)
        self.battery_received.connect(self._sensor_manager.handle_battery)
        self.vfr_hud_received.connect(self._sensor_manager.handle_vfr_hud)
        
        self._logger.addLog("✅ SensorManager für SensorView registriert")

    def set_connection(self, connection, is_simulator=False):
        """Set the MAVLink connection to use"""
        self._mavlink_connection = connection
        self._is_simulator = is_simulator
        
        # Flag zur Nachverfolgung, ob SensorView-Daten bereits einmal abgefragt wurden
        self._sensor_view_initialized = False
        
    def _send_message(self, msg):
        """Send a message via the MAVLink connection"""
        if not self._mavlink_connection:
            return False
            
    def process_raw_message(self, raw_message):
        """Verarbeitet eine rohe MAVLink-Nachricht direkt vom ConnectionManager.
        
        Diese Methode ist der Haupteinstiegspunkt für MAVLink-Nachrichten, die vom
        ConnectionManager empfangen wurden. Sie parst die Nachricht und leitet sie
        an den entsprechenden Handler weiter.
        
        Args:
            raw_message: Die rohe MAVLink-Nachricht als Byte-Array.
            
        Returns:
            bool: True wenn die Nachricht erfolgreich verarbeitet wurde, sonst False.
        """
        try:
            # Signal für rohe Nachrichten senden, falls jemand direkt darauf lauscht
            self.raw_message_received.emit(raw_message)
            
            # Nachricht mit pymavlink parsen
            if not self._mavlink_connection:
                self._logger.addLog("❌ Keine MAVLink-Verbindung für Nachrichtenverarbeitung")
                return False
            
            # Parse the message using pymavlink
            msg = self._mavlink_connection.mav.parse_char(raw_message)
            
            # If we successfully parsed a message, process it
            if msg is not None:
                return self._process_mavlink_message(msg)
            return False
        except Exception as e:
            self._logger.addLog(f"❌ Fehler bei der Verarbeitung einer MAVLink-Nachricht: {str(e)}")
            return False
    
    def _process_mavlink_message(self, msg):
        """Verarbeitet eine geparste MAVLink-Nachricht und emittiert entsprechende Signale.
        
        Diese interne Methode wird von process_raw_message und process_messages aufgerufen.
        Sie ist für die zentrale Nachrichtenverarbeitung und Signal-Emission zuständig.
        
        Args:
            msg: Die geparste MAVLink-Nachricht.
            
        Returns:
            bool: True wenn die Nachricht erfolgreich verarbeitet wurde, sonst False.
        """
        try:
            # Nachrichtentyp bestimmen und entsprechend behandeln
            msg_type = msg.get_type()
            
            # Filtere häufige Nachrichten anhand des in der Memory gespeicherten Mechanismus
            # Nur bestimmte Nachrichten loggen, um Spam zu reduzieren
            if msg_type == 'HEARTBEAT':
                # Heartbeat-Nachricht verarbeiten und Signal emittieren
                self.heartbeat_received.emit(msg)
                # An SensorManager weiterleiten, falls vorhanden
                if hasattr(self, '_sensor_manager') and self._sensor_manager:
                    self._sensor_manager.handle_heartbeat(msg)
                return True
                
            elif msg_type == 'ATTITUDE':
                # ATTITUDE-Nachricht verarbeiten und Signal emittieren
                self.attitude_received.emit(msg)
                # An SensorManager weiterleiten, falls vorhanden
                if hasattr(self, '_sensor_manager') and self._sensor_manager:
                    self._sensor_manager.handle_attitude(msg)
                return True
                
            elif msg_type == 'GPS_RAW_INT':
                # GPS-Nachricht verarbeiten und Signal emittieren
                self.gps_received.emit(msg)
                # An SensorManager weiterleiten, falls vorhanden
                if hasattr(self, '_sensor_manager') and self._sensor_manager:
                    self._sensor_manager.handle_gps(msg)
                return True
                
            elif msg_type == 'BATTERY_STATUS':
                # Batterie-Nachricht verarbeiten und Signal emittieren
                self.battery_received.emit(msg)
                # An SensorManager weiterleiten, falls vorhanden
                if hasattr(self, '_sensor_manager') and self._sensor_manager:
                    self._sensor_manager.handle_battery(msg)
                return True
                
            elif msg_type == 'STATUSTEXT':
                # StatusText-Nachricht an eigenen Handler weiterleiten
                self._handle_statustext(msg)
                return True
                
            elif msg_type == 'PARAM_VALUE':
                # Parameter-Nachricht verarbeiten und Signal emittieren
                self.parameter_received.emit(msg)
                return True
                
            elif msg_type == 'VFR_HUD':
                # VFR_HUD-Nachricht verarbeiten und Signal emittieren
                self.vfr_hud_received.emit(msg)
                # An SensorManager weiterleiten, falls vorhanden
                if hasattr(self, '_sensor_manager') and self._sensor_manager:
                    self._sensor_manager.handle_vfr_hud(msg)
                return True
                
            # Cache für verzögerte Nachrichten aktualisieren
            elif msg_type == 'SERVO_OUTPUT_RAW':
                self._servo_output_raw_cache = msg
                return True
                
            elif msg_type == 'RC_CHANNELS':
                self._rc_channels_cache = msg
                return True
                
            elif msg_type == 'MISSION_CURRENT':
                self._mission_current_cache = msg
                return True
                
            elif msg_type == 'SYS_STATUS':
                self._sys_status_cache = msg
                return True
                
            # Alle anderen Nachrichten werden ignoriert
            return False
            
        except Exception as e:
            self._logger.addLog(f"❌ Fehler bei der internen Nachrichtenverarbeitung: {str(e)}")
            return False
            
    def send_reboot_command(self):
        """
        Sendet einen Neustart-Befehl an den Flugcontroller.
        Verwendet den MAVLink-Befehl COMMAND_LONG mit MAV_CMD_PREFLIGHT_REBOOT_SHUTDOWN.
        
        Returns:
            bool: True, wenn der Befehl erfolgreich gesendet wurde, sonst False.
        """
        if not self._mavlink_connection:
            self._logger.addLog("[ERROR] Keine MAVLink-Verbindung zum Senden des Neustart-Befehls")
            return False
            
        try:
            # MAV_CMD_PREFLIGHT_REBOOT_SHUTDOWN = 246
            # Parameter 1: 1 = Reboot autopilot, 0 = Do nothing for autopilot
            # Parameter 2: 0 = Do nothing for onboard computer
            # Parameter 3: 0 = Do nothing for camera
            # Parameter 4: 0 = Do nothing for mount
            # Parameter 5-7: 0 (unused)
            self._logger.addLog("[INFO] Sende Neustart-Befehl an Flugcontroller...")
            
            # target_system und target_component sind in der Regel 1 und 1 für den Haupt-Flugcontroller
            target_system = 1
            target_component = 1
            
            # Sende den MAVLink-Befehl
            self._mavlink_connection.mav.command_long_send(
                target_system,          # target_system
                target_component,       # target_component
                246,                    # command (MAV_CMD_PREFLIGHT_REBOOT_SHUTDOWN)
                0,                      # confirmation (0 = first transmission)
                1,                      # param1 (1 = reboot autopilot)
                0,                      # param2 (0 = do nothing for onboard computer)
                0,                      # param3 (0 = do nothing for camera)
                0,                      # param4 (0 = do nothing for mount)
                0, 0, 0                 # param5-7 (unused)
            )
            
            self._logger.addLog("[OK] Neustart-Befehl erfolgreich gesendet")
            return True
            
        except Exception as e:
            self._logger.addLog(f"[ERROR] Fehler beim Senden des Neustart-Befehls: {str(e)}")
            return False
            
        try:
            self._mavlink_connection.write(msg.pack(self._mavlink_connection.mav))
            return True
        except Exception as e:
            self._logger.addLog(f"❌ Failed to send MAVLink message: {str(e)}")
            return False
            
    def start_compass_calibration(self):
        """
        Startet die Kompass-Kalibrierung.
        
        Returns:
            bool: True wenn der Befehl erfolgreich gesendet wurde, sonst False
        """
        try:
            if not self._mavlink_connection:
                self._logger.addLog("❌ Keine MAVLink-Verbindung verfügbar")
                return False
                
            # MAV_CMD_DO_START_MAG_CAL command
            # param1: Mask für Kompass (0xFF für alle Kompasse)
            # param2: 1 = Kalibrierung starten (0 = beenden)
            # param3: 0 = automatisch speichern (1 = nicht speichern)
            # param4: 0 = Startverzögerung
            # param5-7: nicht benutzt
            command = self._mavlink_connection.mav.command_long_encode(
                self._mavlink_connection.target_system,
                self._mavlink_connection.target_component,
                mavutil.mavlink.MAV_CMD_DO_START_MAG_CAL,
                0,  # confirmation
                0xFF,  # Alle Kompasse
                1,     # Starten
                0,     # Auto-speichern
                0,     # Keine Verzögerung
                0, 0, 0  # Nicht benutzt
            )
            
            result = self._send_message(command)
            if result:
                self._logger.addLog("✅ Kompass-Kalibrierung gestartet")
            else:
                self._logger.addLog("❌ Fehler beim Senden des Kompass-Kalibrierungsbefehls")
            return result
            
        except Exception as e:
            self._logger.addLog(f"❌ Fehler beim Starten der Kompass-Kalibrierung: {str(e)}")
            return False
            
    def cancel_compass_calibration(self):
        """
        Bricht die Kompass-Kalibrierung ab.
        
        Returns:
            bool: True wenn der Befehl erfolgreich gesendet wurde, sonst False
        """
        try:
            if not self._mavlink_connection:
                self._logger.addLog("❌ Keine MAVLink-Verbindung verfügbar")
                return False
                
            # MAV_CMD_DO_CANCEL_MAG_CAL command
            # param1: Mask für Kompass (0xFF für alle Kompasse)
            # param2-7: nicht benutzt
            command = self._mavlink_connection.mav.command_long_encode(
                self._mavlink_connection.target_system,
                self._mavlink_connection.target_component,
                mavutil.mavlink.MAV_CMD_DO_CANCEL_MAG_CAL,
                0,  # confirmation
                0xFF,  # Alle Kompasse
                0, 0, 0, 0, 0, 0  # Nicht benutzt
            )
            
            result = self._send_message(command)
            if result:
                self._logger.addLog("✅ Kompass-Kalibrierung abgebrochen")
            else:
                self._logger.addLog("❌ Fehler beim Senden des Abbruchbefehls")
            return result
            
        except Exception as e:
            self._logger.addLog(f"❌ Fehler beim Abbrechen der Kompass-Kalibrierung: {str(e)}")
            return False
            
    def accept_compass_calibration(self):
        """
        Akzeptiert und speichert die Kompass-Kalibrierung.
        
        Returns:
            bool: True wenn der Befehl erfolgreich gesendet wurde, sonst False
        """
        try:
            if not self._mavlink_connection:
                self._logger.addLog("❌ Keine MAVLink-Verbindung verfügbar")
                return False
                
            # MAV_CMD_DO_ACCEPT_MAG_CAL command
            # param1: Mask für Kompass (0xFF für alle Kompasse)
            # param2-7: nicht benutzt
            command = self._mavlink_connection.mav.command_long_encode(
                self._mavlink_connection.target_system,
                self._mavlink_connection.target_component,
                mavutil.mavlink.MAV_CMD_DO_ACCEPT_MAG_CAL,
                0,  # confirmation
                0xFF,  # Alle Kompasse
                0, 0, 0, 0, 0, 0  # Nicht benutzt
            )
            
            result = self._send_message(command)
            if result:
                self._logger.addLog("✅ Kompass-Kalibrierung akzeptiert und gespeichert")
            else:
                self._logger.addLog("❌ Fehler beim Speichern der Kalibrierungsdaten")
            return result
            
        except Exception as e:
            self._logger.addLog(f"❌ Fehler beim Akzeptieren der Kompass-Kalibrierung: {str(e)}")
            return False
            
    def start_accel_calibration(self):
        """
        Startet die Beschleunigungssensor-Kalibrierung.
        
        Returns:
            bool: True wenn der Befehl erfolgreich gesendet wurde, sonst False
        """
        try:
            if not self._mavlink_connection:
                self._logger.addLog("❌ Keine MAVLink-Verbindung verfügbar")
                return False
                
            # MAV_CMD_PREFLIGHT_CALIBRATION command
            # param1: Gyro (0 = nicht kalibrieren)
            # param2: Magnetometer (0 = nicht kalibrieren)
            # param3: Nullpunkt Barometer (0 = nicht kalibrieren)
            # param4: Nullpunkt RC (0 = nicht kalibrieren)
            # param5: Accelerometer (1 = kalibrieren)
            # param6: Kompass/Motor Interferenz (0 = nicht kalibrieren)
            # param7: nicht benutzt
            command = self._mavlink_connection.mav.command_long_encode(
                self._mavlink_connection.target_system,
                self._mavlink_connection.target_component,
                mavutil.mavlink.MAV_CMD_PREFLIGHT_CALIBRATION,
                0,  # confirmation
                0,   # Gyro
                0,   # Magnetometer
                0,   # Barometer
                0,   # RC
                1,   # Accelerometer
                0,   # Compass/Motor
                0    # Nicht benutzt
            )
            
            result = self._send_message(command)
            if result:
                self._logger.addLog("✅ Accelerometer-Kalibrierung gestartet")
            else:
                self._logger.addLog("❌ Fehler beim Senden des Accelerometer-Kalibrierungsbefehls")
            return result
            
        except Exception as e:
            self._logger.addLog(f"❌ Fehler beim Starten der Accelerometer-Kalibrierung: {str(e)}")
            return False
            
    def next_accel_calibration_step(self):
        """
        Bestätigt den aktuellen Schritt der Accelerometer-Kalibrierung und geht zum nächsten Schritt.
        
        Returns:
            bool: True wenn der Befehl erfolgreich gesendet wurde, sonst False
        """
        try:
            if not self._mavlink_connection:
                self._logger.addLog("❌ Keine MAVLink-Verbindung verfügbar")
                return False
                
            # MAV_CMD_ACCELCAL_VEHICLE_POS command
            # param1: Position (1-6 für verschiedene Positionen)
            command = self._mavlink_connection.mav.command_long_encode(
                self._mavlink_connection.target_system,
                self._mavlink_connection.target_component,
                mavutil.mavlink.MAV_CMD_ACCELCAL_VEHICLE_POS,
                0,  # confirmation
                1,  # Position (wird ignoriert, der Flugcontroller kennt den aktuellen Schritt)
                0, 0, 0, 0, 0, 0  # Nicht benutzt
            )
            
            result = self._send_message(command)
            if result:
                self._logger.addLog("✅ Nächster Schritt der Accelerometer-Kalibrierung")
            else:
                self._logger.addLog("❌ Fehler beim Senden des Befehls zum nächsten Kalibrierungsschritt")
            return result
            
        except Exception as e:
            self._logger.addLog(f"❌ Fehler beim Fortfahren mit der Accelerometer-Kalibrierung: {str(e)}")
            return False
            
    def start(self):
        """Start message handling"""
        if not self._mavlink_connection:
            error_msg = "❌ No MAVLink connection available"
            self._logger.addLog(error_msg)
            self.error_occurred.emit(error_msg)
            return False
            
        try:
            self._running = True
            self._logger.addLog("✅ Message handler started")
            
            # For simulator, send initial messages
            if self._is_simulator:
                self._send_simulator_messages()
                
            return True
        except Exception as e:
            error_msg = f"❌ Error starting message handler: {str(e)}"
            self._logger.addLog(error_msg)
            self.error_occurred.emit(error_msg)
            
    def _update_delayed_messages(self):
        """Aktualisiert die UI mit den gecachten Nachrichten (wird alle 60 Sekunden aufgerufen)"""
        try:
            current_time = time.time()
            time_diff = current_time - self._last_ui_update_time
            
            # Nur aktualisieren, wenn mindestens 60 Sekunden vergangen sind
            if time_diff < 60:
                return
                
            self._last_ui_update_time = current_time
            self._logger.addLog("Updating delayed message display...")
            
            # SERVO_OUTPUT_RAW verarbeiten
            if self._servo_output_raw_cache:
                try:
                    # Formatiere SERVO_OUTPUT_RAW-Daten
                    servo_values = []
                    for i in range(1, 9):  # Servo 1-8
                        attr_name = f'servo{i}_raw'
                        if hasattr(self._servo_output_raw_cache, attr_name):
                            servo_values.append(f"S{i}={getattr(self._servo_output_raw_cache, attr_name)}")
                    
                    if servo_values:
                        servo_info = "SERVO: " + ", ".join(servo_values)
                        self._logger.addSystemInfoLog(servo_info)
                except Exception as e:
                    self._logger.addLog(f"Error processing SERVO_OUTPUT_RAW: {str(e)}")
            
            # RC_CHANNELS verarbeiten
            if self._rc_channels_cache:
                try:
                    # Formatiere RC_CHANNELS-Daten
                    rc_values = []
                    for i in range(1, 9):  # RC 1-8
                        attr_name = f'chan{i}_raw'
                        if hasattr(self._rc_channels_cache, attr_name):
                            rc_values.append(f"RC{i}={getattr(self._rc_channels_cache, attr_name)}")
                    
                    if rc_values:
                        rc_info = "RC: " + ", ".join(rc_values)
                        self._logger.addSystemInfoLog(rc_info)
                except Exception as e:
                    self._logger.addLog(f"Error processing RC_CHANNELS: {str(e)}")
            
            # MISSION_CURRENT verarbeiten
            if self._mission_current_cache:
                try:
                    mission_info = f"Mission: WP#{self._mission_current_cache.seq}"
                    self._logger.addSystemInfoLog(mission_info)
                except Exception as e:
                    self._logger.addLog(f"Error processing MISSION_CURRENT: {str(e)}")
                    
            # SYS_STATUS verarbeiten (nur für System-Status, nicht Batterie)
            if self._sys_status_cache:
                try:
                    # Formatiere SYS_STATUS-Daten (ohne Batterie)
                    errors = []
                    if hasattr(self._sys_status_cache, 'errors_count1') and self._sys_status_cache.errors_count1 > 0:
                        errors.append(f"Errors: {self._sys_status_cache.errors_count1}")
                    
                    # CPU Last
                    if hasattr(self._sys_status_cache, 'load'):
                        cpu_load = self._sys_status_cache.load / 10.0  # In Prozent
                        status_info = f"CPU: {cpu_load:.1f}%"
                        if errors:
                            status_info += " | " + ", ".join(errors)
                        self._logger.addSystemInfoLog(status_info)
                except Exception as e:
                    self._logger.addLog(f"Error processing SYS_STATUS: {str(e)}")
        except Exception as e:
            self._logger.addLog(f"Error in delayed message update: {str(e)}")
        
    def process_messages(self):
        """Process incoming MAVLink messages"""
        if not self._running or not self._mavlink_connection:
            return
        
        # Process multiple messages in one cycle for better performance
        messages_processed = 0
        max_messages_per_cycle = 10  # Process up to 10 messages per cycle
            
        try:
            while messages_processed < max_messages_per_cycle:
                msg = self._mavlink_connection.recv_match(blocking=False)
                if not msg:
                    break  # No more messages in the queue
                    
                messages_processed += 1
                msg_type = msg.get_type()
                
                # Add important debug output for sensor values
                self._logger.addLog(f"Receiving MAVLink message: {msg_type}")
                
                if msg_type == 'HEARTBEAT':
                    self.heartbeat_received.emit(msg)
                    self._handle_heartbeat(msg)
                    
                    # Nur Armed/Disarmed Status als Systeminfo hinzufügen, Flugmodus entfernt
                    try:
                        armed = (msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED) != 0
                        status = "ARMED" if armed else "DISARMED"
                        self._logger.addSystemInfoLog(f"System {status}")
                    except Exception as e:
                        pass
                    
                elif msg_type == 'ATTITUDE':
                    self.attitude_received.emit(msg)
                    # Debug
                    try:
                        roll_deg = round(msg.roll * 180 / 3.14159, 1)
                        pitch_deg = round(msg.pitch * 180 / 3.14159, 1)
                        yaw_deg = round(msg.yaw * 180 / 3.14159, 1)
                        attitude_msg = f"Attitude: Roll={roll_deg}°, Pitch={pitch_deg}°, Yaw={yaw_deg}°"
                        self._logger.addLog(f"[DEBUG] {attitude_msg}")
                        
                        # Lagewinkel nicht mehr als Systeminfo hinzufügen
                        # (auf Wunsch des Benutzers entfernt)
                    except Exception as e:
                        pass
                    
                elif msg_type == 'GLOBAL_POSITION_INT':
                    self.gps_received.emit(msg)
                    # Debug
                    try:
                        lat = msg.lat / 1e7
                        lon = msg.lon / 1e7
                        alt = msg.relative_alt / 1000.0
                        gps_msg = f"GPS: Lat={lat:.6f}, Lon={lon:.6f}, Alt={alt:.1f}m"
                        self._logger.addLog(f"[DEBUG] {gps_msg}")
                        
                        # GPS-Position nicht mehr als Systeminfo hinzufügen
                        # (auf Wunsch des Benutzers entfernt)
                    except Exception as e:
                        pass
                        
                elif msg_type == 'SYS_STATUS':
                    # SYS_STATUS-Nachricht direkt an UI weitergeben für Batterieanzeige
                    self.battery_received.emit(msg)
                    
                    # Batterieinformationen verarbeiten
                    try:
                        voltage = msg.voltage_battery / 1000.0
                        current = msg.current_battery / 100.0
                        remaining = msg.battery_remaining
                        
                        # Cache SYS_STATUS-Nachricht für spätere Verwendung
                        self._sys_status_cache = msg
                        
                        # Batterieinformationen an SensorModel weitergeben für bessere PreflightView-Integration
                        if hasattr(self, '_sensor_manager') and self._sensor_manager:
                            self._sensor_manager.handle_battery(msg)
                        
                        # Nur Debug-Log, keine System-Info mehr (auf Wunsch des Benutzers)
                        battery_msg = f"Battery: {voltage:.1f}V, {current:.1f}A, {remaining}%"
                        self._logger.addLog(f"[DEBUG] {battery_msg}")
                    except Exception as e:
                        self._logger.addLog(f"Error processing battery status: {str(e)}")
                    
                elif msg_type == 'VFR_HUD':
                    self._mission_current_cache = msg
                    self._logger.addLog(f"MISSION_CURRENT cached for delayed display")
                    
                    # Wenn SensorManager vorhanden, MISSION_CURRENT direkt weitergeben
                    if hasattr(self, '_sensor_manager') and self._sensor_manager and hasattr(self._sensor_manager, 'handle_mission'):
                        self._sensor_manager.handle_mission(msg)
        except Exception as e:
            error_msg = f"Error in message processing: {str(e)}"
            self._logger.addLog(error_msg)
            self.error_occurred.emit(error_msg)
            
    def _handle_heartbeat(self, msg):
        """Handle heartbeat message"""
        try:
            armed = (msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED) != 0
            mode = mavutil.mode_string_v10(msg)
            
            # Flugmodus nicht mehr loggen (auf Wunsch des Benutzers entfernt)
            self._last_mode = mode
                
            # System/Component ID des Absenders speichern
            target_system = msg.get_srcSystem()
            target_component = msg.get_srcComponent()
            
            # Zeitpunkt des letzten Heartbeats speichern
            self._last_heartbeat_time = time.time()
            
            # Beim ersten Heartbeat die Datenströme anfordern
            if not hasattr(self, '_data_streams_requested') or not self._data_streams_requested.get(target_system, False):
                print(f"[INFO] Erster Heartbeat von System {target_system}. Fordere Datenströme an...")
                # Datenströme anfordern
                self.request_data_stream(target_system, target_component)
                # Markieren, dass wir Streams für dieses System angefordert haben
                if not hasattr(self, '_data_streams_requested'):
                    self._data_streams_requested = {}
                self._data_streams_requested[target_system] = True
        
            # Nur loggen, wenn sich der Status geändert hat und nicht beim ersten Aufruf
            if hasattr(self, '_last_armed'):
                if self._last_armed != armed:
                    status = "ARMED" if armed else "DISARMED"
                    # Zeitstempel für letzte Statusmeldung speichern
                    current_time = time.time()
                    if not hasattr(self, '_last_arm_status_time'):
                        self._last_arm_status_time = 0
                
                    # Status nur loggen, wenn sich tatsächlich etwas geändert hat
                    # und nicht zu häufig (mindestens 1 Sekunde Abstand)
                    # Aber nicht als [SYSTEM INFO] loggen, damit es nicht in den wichtigen Nachrichten erscheint
                    if current_time - self._last_arm_status_time > 1.0:
                        self._logger.addLog(f"System ist jetzt {status}")  # Normale Log-Meldung statt [SYSTEM INFO]
                        self._last_arm_status_time = current_time
        
            # Status immer aktualisieren, aber nicht immer loggen
            self._last_armed = armed
            
        except Exception as e:
            error_msg = f"❌ Error handling heartbeat: {str(e)}"
            self._logger.addLog(error_msg)
            self.error_occurred.emit(error_msg)
            
    def start_compass_calibration(self):
        """Sendet den MAVLink-Befehl, um die Kompass-Kalibrierung zu starten"""
        if not self._mavlink_connection or not self._running:
            error_msg = "❌ Keine MAVLink-Verbindung verfügbar"
            self._logger.addLog(error_msg)
            self.error_occurred.emit(error_msg)
            return False
            
        try:
            # MAV_CMD_DO_START_MAG_CAL - Kompass-Kalibrierung starten
            # Parameter 1: Bitmask für zu kalibrierende Kompasse (255 = alle)
            # Parameter 2: 1=Autodecline (automatisches Beenden), 0=Manuelle Bestätigung erforderlich
            # Parameter 3: 1=Autosave (automatisches Speichern), 0=Manuelles Speichern erforderlich
            # Parameter 4-7: Ungenutzt (0)
            self._mavlink_connection.mav.command_long_send(
                self._mavlink_connection.target_system,
                self._mavlink_connection.target_component,
                mavutil.mavlink.MAV_CMD_DO_START_MAG_CAL,
                0,  # Confirmation
                255,  # All compasses
                0,    # Manual acceptance required
                1,    # Auto save
                0, 0, 0, 0  # Unused parameters
            )
            self._logger.addLog("🧭 Kompass-Kalibrierung gestartet")
            return True
        except Exception as e:
            error_msg = f"❌ Fehler beim Starten der Kompass-Kalibrierung: {str(e)}"
            self._logger.addLog(error_msg)
            self.error_occurred.emit(error_msg)
            return False
            
    def cancel_compass_calibration(self):
        """Sendet den MAVLink-Befehl, um die Kompass-Kalibrierung abzubrechen"""
        if not self._mavlink_connection or not self._running:
            return False
            
        try:
            # MAV_CMD_DO_CANCEL_MAG_CAL - Kompass-Kalibrierung abbrechen
            self._mavlink_connection.mav.command_long_send(
                self._mavlink_connection.target_system,
                self._mavlink_connection.target_component,
                mavutil.mavlink.MAV_CMD_DO_CANCEL_MAG_CAL,
                0,  # Confirmation
                255,  # All compasses
                0, 0, 0, 0, 0, 0  # Unused parameters
            )
            self._logger.addLog("🧭 Kompass-Kalibrierung abgebrochen")
            return True
        except Exception as e:
            error_msg = f"❌ Fehler beim Abbrechen der Kompass-Kalibrierung: {str(e)}"
            self._logger.addLog(error_msg)
            self.error_occurred.emit(error_msg)
            return False
            
    def accept_compass_calibration(self):
        """Sendet den MAVLink-Befehl, um die Kompass-Kalibrierung zu akzeptieren"""
        if not self._mavlink_connection or not self._running:
            return False
            
        try:
            # MAV_CMD_DO_ACCEPT_MAG_CAL - Kompass-Kalibrierung akzeptieren
            self._mavlink_connection.mav.command_long_send(
                self._mavlink_connection.target_system,
                self._mavlink_connection.target_component,
                mavutil.mavlink.MAV_CMD_DO_ACCEPT_MAG_CAL,
                0,  # Confirmation
                255,  # All compasses
                0, 0, 0, 0, 0, 0  # Unused parameters
            )
            self._logger.addLog("✅ Kompass-Kalibrierung akzeptiert")
            return True
        except Exception as e:
            error_msg = f"❌ Fehler beim Akzeptieren der Kompass-Kalibrierung: {str(e)}"
            self._logger.addLog(error_msg)
            self.error_occurred.emit(error_msg)
            return False
            
    def start_accel_calibration(self):
        """Sendet den MAVLink-Befehl, um die Accelerometer-Kalibrierung zu starten"""
        if not self._mavlink_connection or not self._running:
            error_msg = "❌ Keine MAVLink-Verbindung verfügbar"
            self._logger.addLog(error_msg)
            self.error_occurred.emit(error_msg)
            return False
            
        try:
            # PREFLIGHT_CALIBRATION-Nachricht für Accelerometer-Kalibrierung
            # Parameter 1-7: [gyro_cal, mag_cal, ground_pressure, radio_cal, accel_cal, comp_arm_cal, param7]
            self._mavlink_connection.mav.command_long_send(
                self._mavlink_connection.target_system,
                self._mavlink_connection.target_component,
                mavutil.mavlink.MAV_CMD_PREFLIGHT_CALIBRATION,
                0,  # Confirmation
                0,  # No gyro calibration
                0,  # No mag calibration
                0,  # No ground pressure
                0,  # No radio calibration
                1,  # Accel calibration
                0,  # No compass/motor interference
                0   # Unused
            )
            self._logger.addLog("📊 Accelerometer-Kalibrierung gestartet")
            return True
        except Exception as e:
            error_msg = f"❌ Fehler beim Starten der Accelerometer-Kalibrierung: {str(e)}"
            self._logger.addLog(error_msg)
            self.error_occurred.emit(error_msg)
            return False
            
    def next_accel_calibration_step(self):
        """Sendet einen Befehl, um zum nächsten Schritt der Accelerometer-Kalibrierung zu gelangen"""
        if not self._mavlink_connection or not self._running:
            return False
            
        try:
            # ACK Command für den nächsten Schritt
            self._mavlink_connection.mav.command_ack_send(
                mavutil.mavlink.MAV_CMD_PREFLIGHT_CALIBRATION,
                mavutil.mavlink.MAV_RESULT_ACCEPTED
            )
            self._logger.addLog("📊 Nächster Schritt der Accelerometer-Kalibrierung")
            return True
        except Exception as e:
            error_msg = f"❌ Fehler beim Fortfahren der Accelerometer-Kalibrierung: {str(e)}"
            self._logger.addLog(error_msg)
            self.error_occurred.emit(error_msg)
            return False
            
    def _update_delayed_messages(self):
        """Aktualisiert die UI mit den gecachten Nachrichten (wird alle 60 Sekunden aufgerufen)"""
        try:
            current_time = time.time()
            time_diff = current_time - self._last_ui_update_time
            
            # Nur aktualisieren, wenn mindestens 60 Sekunden vergangen sind
            if time_diff < 60:
                return
                
            self._last_ui_update_time = current_time
            self._logger.addLog("Updating delayed message display...")
            
            # SERVO_OUTPUT_RAW verarbeiten
            if self._servo_output_raw_cache:
                try:
                    # Formatiere SERVO_OUTPUT_RAW-Daten
                    servo_values = []
                    for i in range(1, 9):  # Servo 1-8
                        attr_name = f'servo{i}_raw'
                        if hasattr(self._servo_output_raw_cache, attr_name):
                            servo_values.append(f"S{i}={getattr(self._servo_output_raw_cache, attr_name)}")
                    
                    if servo_values:
                        servo_info = "SERVO: " + ", ".join(servo_values)
                        self._logger.addSystemInfoLog(servo_info)
                except Exception as e:
                    self._logger.addLog(f"Error processing SERVO_OUTPUT_RAW: {str(e)}")
            
            # RC_CHANNELS verarbeiten
            if self._rc_channels_cache:
                try:
                    # Formatiere RC_CHANNELS-Daten
                    rc_values = []
                    for i in range(1, 9):  # RC 1-8
                        attr_name = f'chan{i}_raw'
                        if hasattr(self._rc_channels_cache, attr_name):
                            rc_values.append(f"RC{i}={getattr(self._rc_channels_cache, attr_name)}")
                    
                    if rc_values:
                        rc_info = "RC: " + ", ".join(rc_values)
                        self._logger.addSystemInfoLog(rc_info)
                except Exception as e:
                    self._logger.addLog(f"Error processing RC_CHANNELS: {str(e)}")
            
            # MISSION_CURRENT verarbeiten
            if self._mission_current_cache:
                try:
                    mission_info = f"Mission: WP#{self._mission_current_cache.seq}"
                    self._logger.addSystemInfoLog(mission_info)
                except Exception as e:
                    self._logger.addLog(f"Error processing MISSION_CURRENT: {str(e)}")
                    
            # SYS_STATUS verarbeiten (nur für System-Status, nicht Batterie)
            if self._sys_status_cache:
                try:
                    # Formatiere SYS_STATUS-Daten (ohne Batterie)
                    errors = []
                    if hasattr(self._sys_status_cache, 'errors_count1') and self._sys_status_cache.errors_count1 > 0:
                        errors.append(f"Errors: {self._sys_status_cache.errors_count1}")
                    
                    # CPU Last
                    if hasattr(self._sys_status_cache, 'load'):
                        cpu_load = self._sys_status_cache.load / 10.0  # In Prozent
                        status_info = f"CPU: {cpu_load:.1f}%"
                        if errors:
                            status_info += " | " + ", ".join(errors)
                        self._logger.addSystemInfoLog(status_info)
                except Exception as e:
                    self._logger.addLog(f"Error processing SYS_STATUS: {str(e)}")
        except Exception as e:
            self._logger.addLog(f"Error in delayed message update: {str(e)}")
            
    def request_data_streams(self):
        """Request data streams from the flight controller"""
        if not self._mavlink_connection:
            error_msg = "❌ No MAVLink connection available"
            self._logger.addLog(error_msg)
            self.error_occurred.emit(error_msg)
            
    def request_data_stream(self, target_system, target_component):
        """
        Fordert Datenströme vom Flugcontroller an
        
        Args:
            target_system: System-ID des Zielsystems (FC, normalerweise 1)
            target_component: Komponenten-ID des Zielsystems
        """
        if not self._mavlink_connection:
            self._logger.addLog("[ERROR] Kann keine Datenströme anfordern: keine MAVLink-Verbindung")
            return False
        
        try:
            self._logger.addLog(f"[INFO] Fordere Datenströme von System={target_system} Component={target_component} an")
            
            # Stream-Rate in Hz für verschiedene Streams
            stream_rates = {
                'POSITION': 2,         # Position (GPS)
                'EXTRA1': 5,           # Attitude (Roll/Pitch/Yaw)
                'EXTRA2': 2,           # VFR_HUD (Höhe, Geschwindigkeit, etc.)
                'EXTENDED_STATUS': 2,   # SYS_STATUS, etc.
                'RAW_SENSORS': 1,       # Rohdaten der Sensoren
                'RC_CHANNELS': 1        # RC Kanal Daten
            }
            
            for stream_id, rate in stream_rates.items():
                stream_id_num = getattr(mavutil.mavlink, f'MAV_DATA_STREAM_{stream_id}')
                self._logger.addLog(f"[DEBUG] Fordere Stream {stream_id} (ID={stream_id_num}) mit Rate={rate} Hz")
                
                # REQUEST_DATA_STREAM senden
                # target_system, target_component, stream_id, message_rate, start_stop (1=start)
                if hasattr(self._mavlink_connection, 'mav') and \
                   hasattr(self._mavlink_connection.mav, 'request_data_stream_send'):
                    self._mavlink_connection.mav.request_data_stream_send(
                        target_system,
                        target_component,
                        stream_id_num,
                        rate,  # Rate in Hz
                        1      # Start (1) oder Stop (0)
                    )
            
            self._logger.addLog("[INFO] Alle Datenströme wurden angefordert")
            return True
            
        except Exception as e:
            import traceback
            error_msg = f"❌ Error requesting data streams: {str(e)}"
            self._logger.addLog(error_msg)
            traceback.print_exc()
            self.error_occurred.emit(error_msg)
            return False

    def stop(self):
        """Stop message handling"""
        self._running = False
        self._logger.addLog("🛑 Message handler stopped")
        
        # Reset simulator state
        self._last_sim_time = None
        self._last_sim_position = None
        
    def _send_simulated_data(self):
        """Send simulated sensor data"""
        try:
            # Get current time
            current_time = time.time()
            
            # Initialize position if not set
            if not hasattr(self, '_last_sim_position'):
                self._last_sim_position = {
                    'lat': 511657000,  # Start position
                    'lon': 104515000,
                    'alt': 100000,     # Start altitude in cm
                    'time': current_time
                }
            
            # Calculate movement
            time_diff = current_time - self._last_sim_position['time']
            
            # Update GPS position (move slowly)
            self._last_sim_position['lat'] += int(100 * time_diff)  # Move 0.1m/s
            self._last_sim_position['lon'] += int(100 * time_diff)  # Move 0.1m/s
            self._last_sim_position['alt'] += int(100 * math.sin(time_diff / 10))  # Sinusoidal altitude

            # Clamp to valid MAVLink ranges
            # lat/lon: -90*1e7 ... +90*1e7 / -180*1e7 ... +180*1e7
            self._last_sim_position['lat'] = max(min(self._last_sim_position['lat'], 900000000), -900000000)
            self._last_sim_position['lon'] = max(min(self._last_sim_position['lon'], 1800000000), -1800000000)
            # alt: -1000000 ... +10000000 (in mm or cm, here cm)
            self._last_sim_position['alt'] = max(min(self._last_sim_position['alt'], 10000000), -1000000)

            # Send GPS position
            self._mavlink_connection.mav.global_position_int_send(
                int(current_time * 1e3),  # timestamp
                self._last_sim_position['lat'],  # lat
                self._last_sim_position['lon'],  # lon
                self._last_sim_position['alt'],  # alt
                0, 0, 0, 0, 0, 0
            )
            
            # Update attitude (smooth variations)
            self._mavlink_connection.mav.attitude_send(
                int(current_time * 1e3),  # timestamp
                0.1 * math.sin(current_time),  # roll
                0.1 * math.cos(current_time),  # pitch
                0.1 * math.sin(2 * current_time),  # yaw
                0, 0, 0
            )
            
            # Update battery status
            self._mavlink_connection.mav.sys_status_send(
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
            )
            
            # Update last position time
            self._last_sim_position['time'] = current_time
            
        except Exception as e:
            error_msg = f"❌ Error sending simulated data: {str(e)}"
            self._logger.addLog(error_msg)
            self.error_occurred.emit(error_msg)
            
    def _update_delayed_messages(self):
        """Aktualisiert die UI mit den gecachten Nachrichten (wird alle 60 Sekunden aufgerufen)"""
        try:
            current_time = time.time()
            time_diff = current_time - self._last_ui_update_time
            
            # Nur aktualisieren, wenn mindestens 60 Sekunden vergangen sind
            if time_diff < 60:
                return
                
            self._last_ui_update_time = current_time
            self._logger.addLog("Updating delayed message display...")
            
            # SERVO_OUTPUT_RAW verarbeiten
            if self._servo_output_raw_cache:
                try:
                    # Formatiere SERVO_OUTPUT_RAW-Daten
                    servo_values = []
                    for i in range(1, 9):  # Servo 1-8
                        attr_name = f'servo{i}_raw'
                        if hasattr(self._servo_output_raw_cache, attr_name):
                            servo_values.append(f"S{i}={getattr(self._servo_output_raw_cache, attr_name)}")
                    
                    if servo_values:
                        servo_info = "SERVO: " + ", ".join(servo_values)
                        self._logger.addSystemInfoLog(servo_info)
                except Exception as e:
                    self._logger.addLog(f"Error processing SERVO_OUTPUT_RAW: {str(e)}")
            
            # RC_CHANNELS verarbeiten
            if self._rc_channels_cache:
                try:
                    # Formatiere RC_CHANNELS-Daten
                    rc_values = []
                    for i in range(1, 9):  # RC 1-8
                        attr_name = f'chan{i}_raw'
                        if hasattr(self._rc_channels_cache, attr_name):
                            rc_values.append(f"RC{i}={getattr(self._rc_channels_cache, attr_name)}")
                    
                    if rc_values:
                        rc_info = "RC: " + ", ".join(rc_values)
                        self._logger.addSystemInfoLog(rc_info)
                except Exception as e:
                    self._logger.addLog(f"Error processing RC_CHANNELS: {str(e)}")
            
            # MISSION_CURRENT verarbeiten
            if self._mission_current_cache:
                try:
                    mission_info = f"Mission: WP#{self._mission_current_cache.seq}"
                    self._logger.addSystemInfoLog(mission_info)
                except Exception as e:
                    self._logger.addLog(f"Error processing MISSION_CURRENT: {str(e)}")
                    
            # SYS_STATUS verarbeiten (nur für System-Status, nicht Batterie)
            if self._sys_status_cache:
                try:
                    # Formatiere SYS_STATUS-Daten (ohne Batterie)
                    errors = []
                    if hasattr(self._sys_status_cache, 'errors_count1') and self._sys_status_cache.errors_count1 > 0:
                        errors.append(f"Errors: {self._sys_status_cache.errors_count1}")
                    
                    # CPU Last
                    if hasattr(self._sys_status_cache, 'load'):
                        cpu_load = self._sys_status_cache.load / 10.0  # In Prozent
                        status_info = f"CPU: {cpu_load:.1f}%"
                        if errors:
                            status_info += " | " + ", ".join(errors)
                        self._logger.addSystemInfoLog(status_info)
                except Exception as e:
                    self._logger.addLog(f"Error processing SYS_STATUS: {str(e)}")
        except Exception as e:
            self._logger.addLog(f"Error in delayed message update: {str(e)}")
            
    def request_system_info(self):
        """Request system information from the flight controller"""
        if not self._mavlink_connection:
            error_msg = "❌ No MAVLink connection available"
            self._logger.addLog(error_msg)
            self.error_occurred.emit(error_msg)
            
    def _update_delayed_messages(self):
        """Aktualisiert die UI mit den gecachten Nachrichten (wird alle 60 Sekunden aufgerufen)"""
        try:
            current_time = time.time()
            time_diff = current_time - self._last_ui_update_time
            
            # Nur aktualisieren, wenn mindestens 60 Sekunden vergangen sind
            if time_diff < 60:
                return
                
            self._last_ui_update_time = current_time
            self._logger.addLog("Updating delayed message display...")
            
            # SERVO_OUTPUT_RAW verarbeiten
            if self._servo_output_raw_cache:
                try:
                    # Formatiere SERVO_OUTPUT_RAW-Daten
                    servo_values = []
                    for i in range(1, 9):  # Servo 1-8
                        attr_name = f'servo{i}_raw'
                        if hasattr(self._servo_output_raw_cache, attr_name):
                            servo_values.append(f"S{i}={getattr(self._servo_output_raw_cache, attr_name)}")
                    
                    if servo_values:
                        servo_info = "SERVO: " + ", ".join(servo_values)
                        self._logger.addSystemInfoLog(servo_info)
                except Exception as e:
                    self._logger.addLog(f"Error processing SERVO_OUTPUT_RAW: {str(e)}")
            
            # RC_CHANNELS verarbeiten
            if self._rc_channels_cache:
                try:
                    # Formatiere RC_CHANNELS-Daten
                    rc_values = []
                    for i in range(1, 9):  # RC 1-8
                        attr_name = f'chan{i}_raw'
                        if hasattr(self._rc_channels_cache, attr_name):
                            rc_values.append(f"RC{i}={getattr(self._rc_channels_cache, attr_name)}")
                    
                    if rc_values:
                        rc_info = "RC: " + ", ".join(rc_values)
                        self._logger.addSystemInfoLog(rc_info)
                except Exception as e:
                    self._logger.addLog(f"Error processing RC_CHANNELS: {str(e)}")
            
            # MISSION_CURRENT verarbeiten
            if self._mission_current_cache:
                try:
                    mission_info = f"Mission: WP#{self._mission_current_cache.seq}"
                    self._logger.addSystemInfoLog(mission_info)
                except Exception as e:
                    self._logger.addLog(f"Error processing MISSION_CURRENT: {str(e)}")
                    
            # SYS_STATUS verarbeiten (nur für System-Status, nicht Batterie)
            if self._sys_status_cache:
                try:
                    # Formatiere SYS_STATUS-Daten (ohne Batterie)
                    errors = []
                    if hasattr(self._sys_status_cache, 'errors_count1') and self._sys_status_cache.errors_count1 > 0:
                        errors.append(f"Errors: {self._sys_status_cache.errors_count1}")
                    
                    # CPU Last
                    if hasattr(self._sys_status_cache, 'load'):
                        cpu_load = self._sys_status_cache.load / 10.0  # In Prozent
                        status_info = f"CPU: {cpu_load:.1f}%"
                        if errors:
                            status_info += " | " + ", ".join(errors)
                        self._logger.addSystemInfoLog(status_info)
                except Exception as e:
                    self._logger.addLog(f"Error processing SYS_STATUS: {str(e)}")
        except Exception as e:
            self._logger.addLog(f"Error in delayed message update: {str(e)}")
            return
            
        try:
            self._mavlink_connection.mav.request_data_stream_send(
                self._mavlink_connection.target_system,
                self._mavlink_connection.target_component,
                mavutil.mavlink.MAV_DATA_STREAM_ALL,
                10,  # 10 Hz
                1    # Enable
            )
            self._logger.addLog("📡 Data stream request sent")
            
            # Request system information after successful data stream request
            self.request_system_info()
        except Exception as e:
            error_msg = f"❌ Error requesting data streams: {str(e)}"
            self._logger.addLog(error_msg)
            self.error_occurred.emit(error_msg)
            
    def _update_delayed_messages(self):
        """Aktualisiert die UI mit den gecachten Nachrichten (wird alle 60 Sekunden aufgerufen)"""
        try:
            current_time = time.time()
            time_diff = current_time - self._last_ui_update_time
            
            # Nur aktualisieren, wenn mindestens 60 Sekunden vergangen sind
            if time_diff < 60:
                return
                
            self._last_ui_update_time = current_time
            self._logger.addLog("Updating delayed message display...")
            
            # SERVO_OUTPUT_RAW verarbeiten
            if self._servo_output_raw_cache:
                try:
                    # Formatiere SERVO_OUTPUT_RAW-Daten
                    servo_values = []
                    for i in range(1, 9):  # Servo 1-8
                        attr_name = f'servo{i}_raw'
                        if hasattr(self._servo_output_raw_cache, attr_name):
                            servo_values.append(f"S{i}={getattr(self._servo_output_raw_cache, attr_name)}")
                    
                    if servo_values:
                        servo_info = "SERVO: " + ", ".join(servo_values)
                        self._logger.addSystemInfoLog(servo_info)
                except Exception as e:
                    self._logger.addLog(f"Error processing SERVO_OUTPUT_RAW: {str(e)}")
            
            # RC_CHANNELS verarbeiten
            if self._rc_channels_cache:
                try:
                    # Formatiere RC_CHANNELS-Daten
                    rc_values = []
                    for i in range(1, 9):  # RC 1-8
                        attr_name = f'chan{i}_raw'
                        if hasattr(self._rc_channels_cache, attr_name):
                            rc_values.append(f"RC{i}={getattr(self._rc_channels_cache, attr_name)}")
                    
                    if rc_values:
                        rc_info = "RC: " + ", ".join(rc_values)
                        self._logger.addSystemInfoLog(rc_info)
                except Exception as e:
                    self._logger.addLog(f"Error processing RC_CHANNELS: {str(e)}")
            
            # MISSION_CURRENT verarbeiten
            if self._mission_current_cache:
                try:
                    mission_info = f"Mission: WP#{self._mission_current_cache.seq}"
                    self._logger.addSystemInfoLog(mission_info)
                except Exception as e:
                    self._logger.addLog(f"Error processing MISSION_CURRENT: {str(e)}")
                    
            # SYS_STATUS verarbeiten (nur für System-Status, nicht Batterie)
            if self._sys_status_cache:
                try:
                    # Formatiere SYS_STATUS-Daten (ohne Batterie)
                    errors = []
                    if hasattr(self._sys_status_cache, 'errors_count1') and self._sys_status_cache.errors_count1 > 0:
                        errors.append(f"Errors: {self._sys_status_cache.errors_count1}")
                    
                    # CPU Last
                    if hasattr(self._sys_status_cache, 'load'):
                        cpu_load = self._sys_status_cache.load / 10.0  # In Prozent
                        status_info = f"CPU: {cpu_load:.1f}%"
                        if errors:
                            status_info += " | " + ", ".join(errors)
                        self._logger.addSystemInfoLog(status_info)
                except Exception as e:
                    self._logger.addLog(f"Error processing SYS_STATUS: {str(e)}")
        except Exception as e:
            self._logger.addLog(f"Error in delayed message update: {str(e)}")
            
    def request_system_info(self):
        """Request system information from the flight controller"""
        if not self._mavlink_connection:
            error_msg = "❌ No MAVLink connection available"
            self._logger.addLog(error_msg)
            self.error_occurred.emit(error_msg)
            
    def _update_delayed_messages(self):
        """Aktualisiert die UI mit den gecachten Nachrichten (wird alle 60 Sekunden aufgerufen)"""
        try:
            current_time = time.time()
            time_diff = current_time - self._last_ui_update_time
            
            # Nur aktualisieren, wenn mindestens 60 Sekunden vergangen sind
            if time_diff < 60:
                return
                
            self._last_ui_update_time = current_time
            self._logger.addLog("Updating delayed message display...")
            
            # SERVO_OUTPUT_RAW verarbeiten
            if self._servo_output_raw_cache:
                try:
                    # Formatiere SERVO_OUTPUT_RAW-Daten
                    servo_values = []
                    for i in range(1, 9):  # Servo 1-8
                        attr_name = f'servo{i}_raw'
                        if hasattr(self._servo_output_raw_cache, attr_name):
                            servo_values.append(f"S{i}={getattr(self._servo_output_raw_cache, attr_name)}")
                    
                    if servo_values:
                        servo_info = "SERVO: " + ", ".join(servo_values)
                        self._logger.addSystemInfoLog(servo_info)
                except Exception as e:
                    self._logger.addLog(f"Error processing SERVO_OUTPUT_RAW: {str(e)}")
            
            # RC_CHANNELS verarbeiten
            if self._rc_channels_cache:
                try:
                    # Formatiere RC_CHANNELS-Daten
                    rc_values = []
                    for i in range(1, 9):  # RC 1-8
                        attr_name = f'chan{i}_raw'
                        if hasattr(self._rc_channels_cache, attr_name):
                            rc_values.append(f"RC{i}={getattr(self._rc_channels_cache, attr_name)}")
                    
                    if rc_values:
                        rc_info = "RC: " + ", ".join(rc_values)
                        self._logger.addSystemInfoLog(rc_info)
                except Exception as e:
                    self._logger.addLog(f"Error processing RC_CHANNELS: {str(e)}")
            
            # MISSION_CURRENT verarbeiten
            if self._mission_current_cache:
                try:
                    mission_info = f"Mission: WP#{self._mission_current_cache.seq}"
                    self._logger.addSystemInfoLog(mission_info)
                except Exception as e:
                    self._logger.addLog(f"Error processing MISSION_CURRENT: {str(e)}")
                    
            # SYS_STATUS verarbeiten (nur für System-Status, nicht Batterie)
            if self._sys_status_cache:
                try:
                    # Formatiere SYS_STATUS-Daten (ohne Batterie)
                    errors = []
                    if hasattr(self._sys_status_cache, 'errors_count1') and self._sys_status_cache.errors_count1 > 0:
                        errors.append(f"Errors: {self._sys_status_cache.errors_count1}")
                    
                    # CPU Last
                    if hasattr(self._sys_status_cache, 'load'):
                        cpu_load = self._sys_status_cache.load / 10.0  # In Prozent
                        status_info = f"CPU: {cpu_load:.1f}%"
                        if errors:
                            status_info += " | " + ", ".join(errors)
                        self._logger.addSystemInfoLog(status_info)
                except Exception as e:
                    self._logger.addLog(f"Error processing SYS_STATUS: {str(e)}")
        except Exception as e:
            self._logger.addLog(f"Error in delayed message update: {str(e)}")
            return
            
        try:
            # Send command to request system information
            self._logger.addLog("📋 Requesting system information...")
            
            # Manuell die gewünschten Systeminfos in das Log eintragen
            # Diese werden später durch die tatsächlichen Informationen überschrieben
            self._logger.addSystemInfoLog("Waiting for Frame information...")
            self._logger.addSystemInfoLog("Waiting for RCOut information...")
            self._logger.addSystemInfoLog("Waiting for Hardware information...")
            self._logger.addSystemInfoLog("Waiting for Firmware information...")
            self._logger.addSystemInfoLog("Waiting for PreArm checks...")
            # GPS und Batterie wurden auf Wunsch des Benutzers entfernt
            
            # Request ArduPilot specific system information using MAVLink command
            self._mavlink_connection.mav.command_long_send(
                self._mavlink_connection.target_system,
                self._mavlink_connection.target_component,
                mavutil.mavlink.MAV_CMD_DO_SEND_BANNER,  # Request system banner
                0,  # Confirmation
                0, 0, 0, 0, 0, 0, 0  # Parameters (not used)
            )
            
            # Request parameter list (this often triggers additional system info messages)
            self._mavlink_connection.param_fetch_list()
            
            # Request specific parameters that might contain system info
            param_list = ["FRAME_CLASS", "FRAME_TYPE", "HW_TYPE", "INS_PRODUCT_ID"]
            for param in param_list:
                self._mavlink_connection.param_fetch_one(param)
                
            # Fordere einen Status-Report an, um Systeminformationen zu bekommen
            self._mavlink_connection.mav.statustext_send(
                mavutil.mavlink.MAV_SEVERITY_INFO,
                b"REQUEST_SYSINFO"
            )
                
            self._logger.addLog("📋 System information requested")
        except Exception as e:
            error_msg = f"❌ Error requesting system info: {str(e)}"
            self._logger.addLog(error_msg)
            self.error_occurred.emit(error_msg)
            
    def _update_delayed_messages(self):
        """Aktualisiert die UI mit den gecachten Nachrichten (wird alle 60 Sekunden aufgerufen)"""
        try:
            current_time = time.time()
            time_diff = current_time - self._last_ui_update_time
            
            # Nur aktualisieren, wenn mindestens 60 Sekunden vergangen sind
            if time_diff < 60:
                return
                
            self._last_ui_update_time = current_time
            self._logger.addLog("Updating delayed message display...")
            
            # SERVO_OUTPUT_RAW verarbeiten
            if self._servo_output_raw_cache:
                try:
                    # Formatiere SERVO_OUTPUT_RAW-Daten
                    servo_values = []
                    for i in range(1, 9):  # Servo 1-8
                        attr_name = f'servo{i}_raw'
                        if hasattr(self._servo_output_raw_cache, attr_name):
                            servo_values.append(f"S{i}={getattr(self._servo_output_raw_cache, attr_name)}")
                    
                    if servo_values:
                        servo_info = "SERVO: " + ", ".join(servo_values)
                        self._logger.addSystemInfoLog(servo_info)
                except Exception as e:
                    self._logger.addLog(f"Error processing SERVO_OUTPUT_RAW: {str(e)}")
            
            # RC_CHANNELS verarbeiten
            if self._rc_channels_cache:
                try:
                    # Formatiere RC_CHANNELS-Daten
                    rc_values = []
                    for i in range(1, 9):  # RC 1-8
                        attr_name = f'chan{i}_raw'
                        if hasattr(self._rc_channels_cache, attr_name):
                            rc_values.append(f"RC{i}={getattr(self._rc_channels_cache, attr_name)}")
                    
                    if rc_values:
                        rc_info = "RC: " + ", ".join(rc_values)
                        self._logger.addSystemInfoLog(rc_info)
                except Exception as e:
                    self._logger.addLog(f"Error processing RC_CHANNELS: {str(e)}")
            
            # MISSION_CURRENT verarbeiten
            if self._mission_current_cache:
                try:
                    mission_info = f"Mission: WP#{self._mission_current_cache.seq}"
                    self._logger.addSystemInfoLog(mission_info)
                except Exception as e:
                    self._logger.addLog(f"Error processing MISSION_CURRENT: {str(e)}")
                    
            # SYS_STATUS verarbeiten (nur für System-Status, nicht Batterie)
            if self._sys_status_cache:
                try:
                    # Formatiere SYS_STATUS-Daten (ohne Batterie)
                    errors = []
                    if hasattr(self._sys_status_cache, 'errors_count1') and self._sys_status_cache.errors_count1 > 0:
                        errors.append(f"Errors: {self._sys_status_cache.errors_count1}")
                    
                    # CPU Last
                    if hasattr(self._sys_status_cache, 'load'):
                        cpu_load = self._sys_status_cache.load / 10.0  # In Prozent
                        status_info = f"CPU: {cpu_load:.1f}%"
                        if errors:
                            status_info += " | " + ", ".join(errors)
                        self._logger.addSystemInfoLog(status_info)
                except Exception as e:
                    self._logger.addLog(f"Error processing SYS_STATUS: {str(e)}")
        except Exception as e:
            self._logger.addLog(f"Error in delayed message update: {str(e)}")
            
    def __init__(self, logger: Logger):
        super().__init__()
        self._logger = logger
        self._running = False
        self._mavlink_connection = None
        self._is_simulator = False
        
        # Timer für die verzögerte Aktualisierung bestimmter Meldungen
        self._delayed_message_timer = QTimer(self)
        self._delayed_message_timer.timeout.connect(self._update_delayed_messages)
        self._delayed_message_timer.start(60000)  # Alle 60 Sekunden aktualisieren
        
        # Cache für verzögerte Nachrichten
        self._servo_output_raw_cache = None
        self._rc_channels_cache = None
        self._mission_current_cache = None
        self._sys_status_cache = None
        
        # Cache für Kalibrierungsstatus
        self._calibration_status = {
            'compass': {'needed': False, 'in_progress': False, 'last_update': 0},
            'accel': {'needed': False, 'in_progress': False, 'last_update': 0},
            'level': {'needed': False, 'in_progress': False, 'last_update': 0}
        }
        
        # Zeitpunkt der letzten UI-Aktualisierung
        self._last_ui_update_time = time.time()
            
    def _update_delayed_messages(self):
        """Aktualisiert die UI mit den gecachten Nachrichten (wird alle 60 Sekunden aufgerufen)"""
        try:
            current_time = time.time()
            time_diff = current_time - self._last_ui_update_time
            
            # Nur aktualisieren, wenn mindestens 60 Sekunden vergangen sind
            if time_diff < 60:
                return
                
            self._last_ui_update_time = current_time
            self._logger.addLog("Updating delayed message display...")
            
            # SERVO_OUTPUT_RAW verarbeiten
            if self._servo_output_raw_cache:
                try:
                    # Formatiere SERVO_OUTPUT_RAW-Daten
                    servo_values = []
                    for i in range(1, 9):  # Servo 1-8
                        attr_name = f'servo{i}_raw'
                        if hasattr(self._servo_output_raw_cache, attr_name):
                            servo_values.append(f"S{i}={getattr(self._servo_output_raw_cache, attr_name)}")
                    
                    if servo_values:
                        servo_info = "SERVO: " + ", ".join(servo_values)
                        self._logger.addSystemInfoLog(servo_info)
                except Exception as e:
                    self._logger.addLog(f"Error processing SERVO_OUTPUT_RAW: {str(e)}")
            
            # RC_CHANNELS verarbeiten
            if self._rc_channels_cache:
                try:
                    # Formatiere RC_CHANNELS-Daten
                    rc_values = []
                    for i in range(1, 9):  # RC 1-8
                        attr_name = f'chan{i}_raw'
                        if hasattr(self._rc_channels_cache, attr_name):
                            rc_values.append(f"RC{i}={getattr(self._rc_channels_cache, attr_name)}")
                    
                    if rc_values:
                        rc_info = "RC: " + ", ".join(rc_values)
                        self._logger.addSystemInfoLog(rc_info)
                except Exception as e:
                    self._logger.addLog(f"Error processing RC_CHANNELS: {str(e)}")
            
            # MISSION_CURRENT verarbeiten
            if self._mission_current_cache:
                try:
                    mission_info = f"Mission: WP#{self._mission_current_cache.seq}"
                    self._logger.addSystemInfoLog(mission_info)
                except Exception as e:
                    self._logger.addLog(f"Error processing MISSION_CURRENT: {str(e)}")
                    
            # SYS_STATUS verarbeiten (nur für System-Status, nicht Batterie)
            if self._sys_status_cache:
                try:
                    # Formatiere SYS_STATUS-Daten (ohne Batterie)
                    errors = []
                    if hasattr(self._sys_status_cache, 'errors_count1') and self._sys_status_cache.errors_count1 > 0:
                        errors.append(f"Errors: {self._sys_status_cache.errors_count1}")
                    
                    # CPU Last
                    if hasattr(self._sys_status_cache, 'load'):
                        cpu_load = self._sys_status_cache.load / 10.0  # In Prozent
                        status_info = f"CPU: {cpu_load:.1f}%"
                        if errors:
                            status_info += " | " + ", ".join(errors)
                        self._logger.addSystemInfoLog(status_info)
                except Exception as e:
                    self._logger.addLog(f"Error processing SYS_STATUS: {str(e)}")
        except Exception as e:
            self._logger.addLog(f"Error in delayed message update: {str(e)}")
            
    def _send_simulator_messages(self):
        """Send initial messages to the simulator"""
        try:
            if not self._mavlink_connection:
                self._logger.addLog("⚠️ No MAVLink connection available for simulator messages")
                return
                
            # Send initial heartbeat
            self._mavlink_connection.mav.heartbeat_send(
                mavutil.mavlink.MAV_TYPE_QUADROTOR,
                mavutil.mavlink.MAV_AUTOPILOT_GENERIC,
                0, 0, 0
            )
            
            # Send initial GPS position
            self._mavlink_connection.mav.global_position_int_send(
                int(time.time() * 1e3),  # timestamp
                511657000,  # lat (51.1657)
                104515000,  # lon (10.4515)
                0, 0, 0, 0, 0, 0
            )
            
            # Send initial attitude
            self._mavlink_connection.mav.attitude_send(
                int(time.time() * 1e3),  # timestamp
                0, 0, 0,  # roll, pitch, yaw
                0, 0, 0  # rollspeed, pitchspeed, yawspeed
            )
            
            # Send initial battery status
            self._mavlink_connection.mav.sys_status_send(
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
            )
            
        except Exception as e:
            error_msg = f"❌ Error sending simulator messages: {str(e)}"
            self._logger.addLog(error_msg)
            self.error_occurred.emit(error_msg)
            
    def _update_delayed_messages(self):
        """Aktualisiert die UI mit den gecachten Nachrichten (wird alle 60 Sekunden aufgerufen)"""
        try:
            current_time = time.time()
            time_diff = current_time - self._last_ui_update_time
            
            # Nur aktualisieren, wenn mindestens 60 Sekunden vergangen sind
            if time_diff < 60:
                return
                
            self._last_ui_update_time = current_time
            self._logger.addLog("Updating delayed message display...")
            
            # SERVO_OUTPUT_RAW verarbeiten
            if self._servo_output_raw_cache:
                try:
                    # Formatiere SERVO_OUTPUT_RAW-Daten
                    servo_values = []
                    for i in range(1, 9):  # Servo 1-8
                        attr_name = f'servo{i}_raw'
                        if hasattr(self._servo_output_raw_cache, attr_name):
                            servo_values.append(f"S{i}={getattr(self._servo_output_raw_cache, attr_name)}")
                    
                    if servo_values:
                        servo_info = "SERVO: " + ", ".join(servo_values)
                        self._logger.addSystemInfoLog(servo_info)
                except Exception as e:
                    self._logger.addLog(f"Error processing SERVO_OUTPUT_RAW: {str(e)}")
            
            # RC_CHANNELS verarbeiten
            if self._rc_channels_cache:
                try:
                    # Formatiere RC_CHANNELS-Daten
                    rc_values = []
                    for i in range(1, 9):  # RC 1-8
                        attr_name = f'chan{i}_raw'
                        if hasattr(self._rc_channels_cache, attr_name):
                            rc_values.append(f"RC{i}={getattr(self._rc_channels_cache, attr_name)}")
                    
                    if rc_values:
                        rc_info = "RC: " + ", ".join(rc_values)
                        self._logger.addSystemInfoLog(rc_info)
                except Exception as e:
                    self._logger.addLog(f"Error processing RC_CHANNELS: {str(e)}")
            
            # MISSION_CURRENT verarbeiten
            if self._mission_current_cache:
                try:
                    mission_info = f"Mission: WP#{self._mission_current_cache.seq}"
                    self._logger.addSystemInfoLog(mission_info)
                except Exception as e:
                    self._logger.addLog(f"Error processing MISSION_CURRENT: {str(e)}")
                    
            # SYS_STATUS verarbeiten (nur für System-Status, nicht Batterie)
            if self._sys_status_cache:
                try:
                    # Formatiere SYS_STATUS-Daten (ohne Batterie)
                    errors = []
                    if hasattr(self._sys_status_cache, 'errors_count1') and self._sys_status_cache.errors_count1 > 0:
                        errors.append(f"Errors: {self._sys_status_cache.errors_count1}")
                    
                    # CPU Last
                    if hasattr(self._sys_status_cache, 'load'):
                        cpu_load = self._sys_status_cache.load / 10.0  # In Prozent
                        status_info = f"CPU: {cpu_load:.1f}%"
                        if errors:
                            status_info += " | " + ", ".join(errors)
                        self._logger.addSystemInfoLog(status_info)
                except Exception as e:
                    self._logger.addLog(f"Error processing SYS_STATUS: {str(e)}")
        except Exception as e:
            self._logger.addLog(f"Error in delayed message update: {str(e)}")

    def _send_simulated_data(self):
        """Send simulated sensor data"""
        try:
            # Update GPS position (move slightly)
            self._mavlink_connection.mav.global_position_int_send(
                int(time.time() * 1e3),
                511657000 + int(time.time() * 1000),  # lat with slight movement
                104515000 + int(time.time() * 1000),  # lon with slight movement
                0, 0, 0, 0, 0, 0
            )
            
            # Update attitude (add some variation)
            self._mavlink_connection.mav.attitude_send(
                int(time.time() * 1e3),
                0.1 * math.sin(time.time()),  # roll
                0.1 * math.cos(time.time()),  # pitch
                0.1 * math.sin(2 * time.time()),  # yaw
                0, 0, 0
            )
            
            # Update battery status
            self._mavlink_connection.mav.sys_status_send(
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
            )
            
        except Exception as e:
            error_msg = f"❌ Error sending simulated data: {str(e)}"
            self._logger.addLog(error_msg)
            self.error_occurred.emit(error_msg)
            
    def _update_delayed_messages(self):
        """Aktualisiert die UI mit den gecachten Nachrichten (wird alle 60 Sekunden aufgerufen)"""
        try:
            current_time = time.time()
            time_diff = current_time - self._last_ui_update_time
            
            # Nur aktualisieren, wenn mindestens 60 Sekunden vergangen sind
            if time_diff < 60:
                return
                
            self._last_ui_update_time = current_time
            self._logger.addLog("Updating delayed message display...")
            
            # SERVO_OUTPUT_RAW verarbeiten
            if self._servo_output_raw_cache:
                try:
                    # Formatiere SERVO_OUTPUT_RAW-Daten
                    servo_values = []
                    for i in range(1, 9):  # Servo 1-8
                        attr_name = f'servo{i}_raw'
                        if hasattr(self._servo_output_raw_cache, attr_name):
                            servo_values.append(f"S{i}={getattr(self._servo_output_raw_cache, attr_name)}")
                    
                    if servo_values:
                        servo_info = "SERVO: " + ", ".join(servo_values)
                        self._logger.addSystemInfoLog(servo_info)
                except Exception as e:
                    self._logger.addLog(f"Error processing SERVO_OUTPUT_RAW: {str(e)}")
            
            # RC_CHANNELS verarbeiten
            if self._rc_channels_cache:
                try:
                    # Formatiere RC_CHANNELS-Daten
                    rc_values = []
                    for i in range(1, 9):  # RC 1-8
                        attr_name = f'chan{i}_raw'
                        if hasattr(self._rc_channels_cache, attr_name):
                            rc_values.append(f"RC{i}={getattr(self._rc_channels_cache, attr_name)}")
                    
                    if rc_values:
                        rc_info = "RC: " + ", ".join(rc_values)
                        self._logger.addSystemInfoLog(rc_info)
                except Exception as e:
                    self._logger.addLog(f"Error processing RC_CHANNELS: {str(e)}")
            
            # MISSION_CURRENT verarbeiten
            if self._mission_current_cache:
                try:
                    mission_info = f"Mission: WP#{self._mission_current_cache.seq}"
                    self._logger.addSystemInfoLog(mission_info)
                except Exception as e:
                    self._logger.addLog(f"Error processing MISSION_CURRENT: {str(e)}")
                    
            # SYS_STATUS verarbeiten (nur für System-Status, nicht Batterie)
            if self._sys_status_cache:
                try:
                    # Formatiere SYS_STATUS-Daten (ohne Batterie)
                    errors = []
                    if hasattr(self._sys_status_cache, 'errors_count1') and self._sys_status_cache.errors_count1 > 0:
                        errors.append(f"Errors: {self._sys_status_cache.errors_count1}")
                    
                    # CPU Last
                    if hasattr(self._sys_status_cache, 'load'):
                        cpu_load = self._sys_status_cache.load / 10.0  # In Prozent
                        status_info = f"CPU: {cpu_load:.1f}%"
                        if errors:
                            status_info += " | " + ", ".join(errors)
                        self._logger.addSystemInfoLog(status_info)
                except Exception as e:
                    self._logger.addLog(f"Error processing SYS_STATUS: {str(e)}")
        except Exception as e:
            self._logger.addLog(f"Error in delayed message update: {str(e)}")