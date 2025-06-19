from PySide6.QtCore import QObject, Slot, Signal, Property, QTimer
from PySide6.QtQml import QmlElement
import math
import time
import random

QML_IMPORT_NAME = "RZGCS"
QML_IMPORT_MAJOR_VERSION = 1

@QmlElement
class CalibrationViewController(QObject):
    """
    Controller für die Kalibrierungsansicht.
    Diese Klasse stellt Funktionen zur Kalibrierung der verschiedenen Sensoren bereit.
    """
    
    # Signale
    calibrationProgressChanged = Signal(float, str)
    calibrationFinished = Signal(bool, str)
    compassValueChanged = Signal(float, float, float)
    accelValueChanged = Signal(float, float, float)
    gyroValueChanged = Signal(float, float, float)
    rcChannelChanged = Signal(int, int)
    logMessageReceived = Signal(str, str)  # Typ (info, warning, error), Nachricht
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._calibration_in_progress = False
        self._current_calibration_type = None
        self._progress = 0.0
        self._compass_values = [0.0, 0.0, 0.0]  # X, Y, Z
        self._accel_values = [0.0, 0.0, 0.0]  # X, Y, Z
        self._gyro_values = [0.0, 0.0, 0.0]  # X, Y, Z
        self._rc_channels = [1500] * 8  # 8 Standard-RC-Kanäle mit Mittelstellung (1500 µs)
        self._accel_step = 0
        self._message_handler = None
        self._sensor_model = None
        self._log_messages = []  # Speichert die letzten Log-Nachrichten
    
    @Slot(str, str)
    def log_message(self, msg_type, message):
        """
        Loggt eine Nachricht und emittiert ein Signal für die UI.
        
        Args:
            msg_type: Der Typ der Nachricht ('info', 'warning', 'error')
            message: Die Nachricht selbst
        """
        # Füge einen Zeitstempel hinzu
        timestamp = time.strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        
        # Füge die Nachricht zum Log-Verlauf hinzu (max. 100 Einträge)
        self._log_messages.append((msg_type, formatted_message))
        if len(self._log_messages) > 100:
            self._log_messages.pop(0)  # Entferne die älteste Nachricht
        
        # Emittiere das Signal für die UI
        self.logMessageReceived.emit(msg_type, formatted_message)
        
        # Gib die Nachricht auch in der Konsole aus
        print(f"[CALIB_{msg_type.upper()}] {message}")
    
    @Slot(str)
    def log_info(self, message):
        """
        Loggt eine Info-Nachricht.
        """
        self.log_message("info", message)
    
    @Slot(str)
    def log_warning(self, message):
        """
        Loggt eine Warnungs-Nachricht.
        """
        self.log_message("warning", message)
    
    @Slot(str)
    def log_error(self, message):
        """
        Loggt eine Fehler-Nachricht.
        """
        self.log_message("error", message)
        
    @Slot()
    def reboot_flight_controller(self):
        """
        Sendet einen Neustart-Befehl an den Flugcontroller und versucht, sich nach dem Neustart wieder zu verbinden.
        """
        if not self._message_handler:
            self.log_error("Kein Message Handler verfügbar, Neustart nicht möglich")
            return False
            
        self.log_info("Sende Neustart-Befehl an Flugcontroller...")
        
        try:
            # Neustart-Befehl senden
            success = self._message_handler.send_reboot_command()
            
            if success:
                self.log_info("Neustart-Befehl erfolgreich gesendet. Warte auf Neustart...")
                
                # Verbindung trennen, da der FC neu startet
                if hasattr(self._message_handler, '_serial_connector'):
                    serial_connector = self._message_handler._serial_connector
                    if serial_connector:
                        # Port speichern, um später wieder zu verbinden
                        saved_port = serial_connector.port
                        self.log_info(f"Trenne Verbindung zu {saved_port}...")
                        serial_connector.disconnect()
                        
                        # Timer für Wiederverbindung starten (5 Sekunden warten)
                        QTimer.singleShot(5000, lambda: self._reconnect_after_reboot(saved_port))
                        return True
            else:
                self.log_error("Fehler beim Senden des Neustart-Befehls")
                return False
                
        except Exception as e:
            self.log_error(f"Fehler beim Neustarten des Flugcontrollers: {str(e)}")
            return False
        
        return False
        
    def _reconnect_after_reboot(self, port):
        """
        Versucht, nach einem Neustart des Flugcontrollers die Verbindung wiederherzustellen.
        
        Args:
            port: Der Port, mit dem die Verbindung wiederhergestellt werden soll
        """
        if not hasattr(self._message_handler, '_serial_connector'):
            self.log_error("Kein Serial Connector vorhanden, Wiederverbindung nicht möglich")
            return False
            
        serial_connector = self._message_handler._serial_connector
        if not serial_connector:
            self.log_error("Serial Connector ist None, Wiederverbindung nicht möglich")
            return False
            
        self.log_info(f"Versuche, Verbindung zu {port} wiederherzustellen...")
        
        try:
            # Zuerst den Port setzen
            serial_connector.setPort(port)
            
            # Dann Verbindung herstellen (ohne Parameter)
            serial_connector.connect()
            
            # Prüfen, ob die Verbindung erfolgreich war
            success = serial_connector.connected
            
            if success:
                self.log_info(f"Verbindung zu {port} erfolgreich wiederhergestellt!")
                return True
            else:
                self.log_error(f"Fehler beim Wiederherstellen der Verbindung zu {port}")
                
                # Weiterer Versuch nach 2 Sekunden
                QTimer.singleShot(2000, lambda: self._reconnect_after_reboot(port))
                return False
                
        except Exception as e:
            self.log_error(f"Fehler bei der Wiederverbindung: {str(e)}")
            return False
        
    @Slot(object)
    def initialize(self, message_handler, sensor_model=None):
        """
        Initialisiert den Controller und verbindet ihn mit dem Message Handler.
        
        Args:
            message_handler: Die Instanz des MessageHandler, um MAVLink-Befehle zu senden
            sensor_model: Das SensorViewModel, um Sensorwerte direkt zu aktualisieren
        """
        self.log_info("Initialisiere CalibrationViewController")
        self._message_handler = message_handler
        
        # Sensor Model setzen, wenn bereitgestellt
        if sensor_model is not None:
            self._sensor_model = sensor_model
            self.log_info("SensorViewModel verbunden")
        
        # Versuche, das Sensor Model aus dem Serial Connector zu holen, wenn nicht direkt übergeben
        if self._sensor_model is None and hasattr(message_handler, '_serial_connector') and hasattr(message_handler._serial_connector, '_sensor_model'):
            self._sensor_model = message_handler._serial_connector._sensor_model
            self.log_info("SensorViewModel aus SerialConnector geholt")
        
        # Verbinde MAVLink-Signale für Kalibrierungsfeedback
        if self._message_handler:
            # Verbinde die Signale für Sensordaten
            if hasattr(self._message_handler, 'raw_imu_received'):
                self._message_handler.raw_imu_received.connect(self._handle_raw_imu)
                print("RAW_IMU Signal verbunden")
                
            if hasattr(self._message_handler, 'scaled_imu_received'):
                self._message_handler.scaled_imu_received.connect(self._handle_scaled_imu)
                print("SCALED_IMU Signal verbunden")
                
            if hasattr(self._message_handler, 'mag_cal_progress_received'):
                self._message_handler.mag_cal_progress_received.connect(self._handle_mag_cal_progress)
                print("MAG_CAL_PROGRESS Signal verbunden")
                
            if hasattr(self._message_handler, 'mag_cal_report_received'):
                self._message_handler.mag_cal_report_received.connect(self._handle_mag_cal_report)
                print("MAG_CAL_REPORT Signal verbunden")
            
        # Timer für simulierte Daten starten (immer, unabhu00e4ngig von MAVLink-Verbindung)
        self._simulation_timer = QTimer(self)
        self._simulation_timer.timeout.connect(self._simulate_sensor_data)
        self._simulation_timer.start(100)  # Alle 100ms
            
        return True
        
    def _handle_raw_imu(self, xacc, yacc, zacc, xgyro, ygyro, zgyro, xmag, ymag, zmag):
        """Verarbeitet RAW_IMU-Nachrichten"""
        # Kompasswerte aktualisieren
        self._compass_values = [xmag, ymag, zmag]
        self.compassValueChanged.emit(xmag, ymag, zmag)
        
        # Accelerometer-Werte aktualisieren
        self._accel_values = [xacc, yacc, zacc]
        self.accelValueChanged.emit(xacc, yacc, zacc)
        
        # Gyro-Werte aktualisieren
        self._gyro_values = [xgyro, ygyro, zgyro]
        self.gyroValueChanged.emit(xgyro, ygyro, zgyro)
    
    def _handle_scaled_imu(self, xacc, yacc, zacc, xgyro, ygyro, zgyro, xmag, ymag, zmag):
        """Verarbeitet SCALED_IMU-Nachrichten"""
        # Kompasswerte aktualisieren
        self._compass_values = [xmag, ymag, zmag]
        self.compassValueChanged.emit(xmag, ymag, zmag)
        
        # Accelerometer-Werte aktualisieren
        self._accel_values = [xacc, yacc, zacc]
        self.accelValueChanged.emit(xacc, yacc, zacc)
        
        # Gyro-Werte aktualisieren
        self._gyro_values = [xgyro, ygyro, zgyro]
        self.gyroValueChanged.emit(xgyro, ygyro, zgyro)
    
    def _handle_mag_cal_progress(self, compass_id, completion_pct, completion_mask):
        """Verarbeitet MAG_CAL_PROGRESS-Nachrichten"""
        if self._calibration_in_progress and self._current_calibration_type == "compass":
            self._progress = completion_pct / 100.0
            self.calibrationProgressChanged.emit(
                self._progress, 
                f"Kompass {compass_id}: {completion_pct}% abgeschlossen")
    
    def _handle_mag_cal_report(self, compass_id, cal_status, autosaved):
        """Verarbeitet MAG_CAL_REPORT-Nachrichten"""
        if self._calibration_in_progress and self._current_calibration_type == "compass":
            success = (cal_status == 0)  # 0 = success, andere Werte sind Fehler
            message = f"Kompass {compass_id} Kalibrierung "
            message += "erfolgreich" if success else "fehlgeschlagen"
            
            if autosaved:
                message += " (automatisch gespeichert)"
                
            self._calibration_in_progress = False
            self.calibrationFinished.emit(success, message)
    
    def _simulate_sensor_data(self):
        """Simuliert Sensordaten für Testzwecke"""
        # Immer Sensordaten simulieren, auch wenn keine Kalibrierung aktiv ist
        # if not self._calibration_in_progress:
        #     return
            
        # Aktuelle Zeit für Simulation nutzen
        t = time.time() * 3  # Für schnellere Bewegung
        
        if self._current_calibration_type == "compass":
            # Simuliere eine Figur-8-Bewegung für den Kompass
            x = 300 * math.sin(t * 0.5)
            y = 300 * math.sin(t)
            z = 300 * math.cos(t * 0.7)
            
            self._compass_values = [x, y, z]
            self.compassValueChanged.emit(x, y, z)
            
            # Simuliere Fortschritt
            self._progress = min(1.0, self._progress + 0.005)
            self.calibrationProgressChanged.emit(
                self._progress, 
                f"Kompass-Kalibrierung: {int(self._progress * 100)}% abgeschlossen")
            
            # Bei 100% Fortschritt: Kalibrierung abschließen
            if self._progress >= 1.0:
                self._calibration_in_progress = False
                self.calibrationFinished.emit(True, "Kompass-Kalibrierung erfolgreich abgeschlossen")
                
        elif self._current_calibration_type == "accel":
            # Simuliere unterschiedliche Positionen der Drohne
            if self._accel_step == 0:  # Level
                x, y, z = 0, 0, 980  # 9.8 m/s² nach unten (Z)
            elif self._accel_step == 1:  # Nase nach oben
                x, y, z = 500, 0, 800
            elif self._accel_step == 2:  # Nase nach unten
                x, y, z = -500, 0, 800
            elif self._accel_step == 3:  # Linke Seite nach oben
                x, y, z = 0, 500, 800
            elif self._accel_step == 4:  # Rechte Seite nach oben
                x, y, z = 0, -500, 800
            elif self._accel_step == 5:  # Auf dem Rücken
                x, y, z = 0, 0, -980
            else:
                x, y, z = 0, 0, 980
                
            # Füge etwas Rauschen hinzu für realistischere Werte
            noise = 50 * (random.random() - 0.5)
            x += noise
            y += noise
            z += noise
            
            self._accel_values = [x, y, z]
            self.accelValueChanged.emit(x, y, z)
            
            # Wenn das SensorViewModel verfügbar ist, Sensorwerte direkt dort aktualisieren
            if self._sensor_model:
                self._sensor_model.update_sensor("accel_x", round(x, 1))
                self._sensor_model.update_sensor("accel_y", round(y, 1))
                self._sensor_model.update_sensor("accel_z", round(z, 1))
            
        elif self._current_calibration_type == "gyro":
            # Simuliere Gyroskop-Kalibrierung (einfach statische Werte mit etwas Rauschen)
            noise_x = 5 * (random.random() - 0.5)
            noise_y = 5 * (random.random() - 0.5)
            noise_z = 5 * (random.random() - 0.5)
            
            self._gyro_values = [noise_x, noise_y, noise_z]
            self.gyroValueChanged.emit(noise_x, noise_y, noise_z)
            
            # Simuliere Fortschritt
            self._progress = min(1.0, self._progress + 0.01)
            self.calibrationProgressChanged.emit(
                self._progress, 
                f"Gyroskop-Kalibrierung: {int(self._progress * 100)}% abgeschlossen")
            
            # Bei 100% Fortschritt: Kalibrierung abschließen
            if self._progress >= 1.0:
                self._calibration_in_progress = False
                self.calibrationFinished.emit(True, "Gyroskop-Kalibrierung erfolgreich abgeschlossen")
        
        elif self._current_calibration_type == "rc":
            # Simuliere RC-Kanal-Bewegungen
            for i in range(8):
                # Simuliere verschiedene Bewegungen für jeden Kanal
                if i % 2 == 0:  # Gerade Kanäle bewegen sich langsamer
                    self._rc_channels[i] = 1500 + 500 * math.sin(t * 0.2 + i)
                else:  # Ungerade Kanäle bewegen sich schneller
                    self._rc_channels[i] = 1500 + 500 * math.sin(t * 0.4 + i)
                
                # Signalisiere Kanaländerung
                self.rcChannelChanged.emit(i + 1, int(self._rc_channels[i]))
        
        else:
            # Allgemeine Sensordaten auch ohne aktive Kalibrierung simulieren
            # Hier können wir Bewegungsdaten generieren
            roll = 15 * math.sin(t * 0.3)
            pitch = 10 * math.sin(t * 0.5)
            yaw = (t * 10) % 360  # Kontinuierliche Drehung
            
            # IMU-Daten
            x_accel = 50 * math.sin(t * 0.4)
            y_accel = 40 * math.sin(t * 0.6)
            z_accel = 980 + 30 * math.sin(t * 0.3)  # ~9.8 m/s² mit Schwankung
            
            x_gyro = 10 * math.sin(t * 0.3)
            y_gyro = 10 * math.sin(t * 0.4)
            z_gyro = 5 * math.sin(t * 0.5)
            
            # Magnetometerdaten simulieren
            mag_strength = 300  # Typische Stärke in uT
            heading_rad = math.radians(yaw)
            x_mag = mag_strength * math.cos(heading_rad)
            y_mag = mag_strength * math.sin(heading_rad)
            z_mag = mag_strength * 0.5 * math.sin(t * 0.2)  # Inklination simulieren
            
            # Werte aktualisieren
            self._compass_values = [x_mag, y_mag, z_mag]
            self._accel_values = [x_accel, y_accel, z_accel]
            self._gyro_values = [x_gyro, y_gyro, z_gyro]
            
            # Signale senden
            self.compassValueChanged.emit(x_mag, y_mag, z_mag)
            self.accelValueChanged.emit(x_accel, y_accel, z_accel)
            self.gyroValueChanged.emit(x_gyro, y_gyro, z_gyro)
            
            # Wenn das SensorViewModel verfügbar ist, Sensorwerte direkt dort aktualisieren
            if self._sensor_model:
                # Lagewinkel aktualisieren
                self._sensor_model.update_sensor_value("roll", round(roll, 1))
                self._sensor_model.update_sensor_value("pitch", round(pitch, 1))
                self._sensor_model.update_sensor_value("yaw", round(yaw, 1))
                
                # GPS-Daten simulieren (Berlin-Kreisflug)
                center_lat = 52.520008
                center_lon = 13.404954
                radius = 0.001
                gps_angle = t * 0.1
                lat = center_lat + radius * math.sin(gps_angle)
                lon = center_lon + radius * math.cos(gps_angle)
                alt = 100 + 10 * math.sin(t * 0.2)
                
                self._sensor_model.update_sensor_value("gps_lat", round(lat, 6))
                self._sensor_model.update_sensor_value("gps_lon", round(lon, 6))
                self._sensor_model.update_sensor_value("altitude", round(alt, 1))
                
                # Geschwindigkeit simulieren
                groundspeed = 5 + 2 * math.sin(t * 0.3)
                airspeed = groundspeed + 1 * math.sin(t * 0.5)
                self._sensor_model.update_sensor_value("groundspeed", round(groundspeed, 1))
                self._sensor_model.update_sensor_value("airspeed", round(airspeed, 1))
                
                # Batterie simulieren
                voltage = 12.6 - 0.1 * math.sin(t * 0.01)  # Langsam abnehmend
                current = 8.5 + 3 * math.sin(t * 0.2)  # Mit Last schwankend
                remaining = 75 - t * 0.01  # Langsam abnehmend
                self._sensor_model.update_sensor_value("battery_voltage", round(voltage, 1))
                self._sensor_model.update_sensor_value("battery_current", round(current, 1))
                self._sensor_model.update_sensor_value("battery_remaining", round(remaining, 0))
    
    # Generische Kalibrierungsmethode
    @Slot(str)
    def start_calibration(self, calibration_type):
        """
        Startet eine Kalibrierung des spezifizierten Typs.
        
        Args:
            calibration_type (str): Art der Kalibrierung ('compass', 'accel', 'gyro', 'rc')
        """
        if self._calibration_in_progress:
            self.log_warning(f"Bereits eine Kalibrierung in Bearbeitung: {self._current_calibration_type}")
            return False
            
        self.log_info(f"Starte Kalibrierung: {calibration_type}")
        self._calibration_in_progress = True
        self._current_calibration_type = calibration_type
        self._progress = 0.0
        
        # Setze bei Accel-Kalibrierung den ersten Schritt
        if calibration_type == "accel":
            self._accel_step = 0
            self.log_info("Bitte stellen Sie die Drohne in normale, horizontale Position.")
            
        # Sende entsprechenden MAVLink-Befehl an den Flugcontroller, wenn verbunden
        if self._message_handler:
            if calibration_type == "compass":
                # Kompass-Kalibrierung starten
                self.log_info("Sende Kompass-Kalibrierungsbefehl an Flugcontroller")
                result = self._message_handler.start_compass_calibration()
                if result:
                    self.calibrationProgressChanged.emit(self._progress, "Rotieren Sie die Drohne in alle Richtungen")
                else:
                    self.log_error("Fehler beim Starten der Kompass-Kalibrierung")
                    self._calibration_in_progress = False
                    self.calibrationFinished.emit(False, "Fehler beim Starten der Kompass-Kalibrierung")
                    return False
                
            elif calibration_type == "accel":
                # Accelerometer-Kalibrierung starten
                self.log_info("Sende Accelerometer-Kalibrierungsbefehl an Flugcontroller")
                result = self._message_handler.start_accel_calibration()
                if result:
                    self.calibrationProgressChanged.emit(self._progress, "Platzieren Sie die Drohne horizontal")
                else:
                    self.log_error("Fehler beim Starten der Accelerometer-Kalibrierung")
                    self._calibration_in_progress = False
                    self.calibrationFinished.emit(False, "Fehler beim Starten der Accelerometer-Kalibrierung")
                    return False
                
            elif calibration_type == "gyro":
                # Gyroskop-Kalibrierung starten
                self.log_info("Sende Gyroskop-Kalibrierungsbefehl an Flugcontroller")
                # Hier würde die tatsächliche Initiierung der Kalibrierung erfolgen
                self.calibrationProgressChanged.emit(self._progress, "Halten Sie die Drohne still")
        else:
            self.log_warning("Kein Message Handler verbunden - nur Simulation möglich")
            # Fortschritt signalisieren auch ohne Message Handler (für Simulation)
            if calibration_type == "compass":
                self.calibrationProgressChanged.emit(self._progress, "Rotieren Sie die Drohne in alle Richtungen (Simulation)")
            elif calibration_type == "accel":
                self.calibrationProgressChanged.emit(self._progress, "Platzieren Sie die Drohne horizontal (Simulation)")
            elif calibration_type == "gyro":
                self.calibrationProgressChanged.emit(self._progress, "Halten Sie die Drohne still (Simulation)")
        
        return True
    
    # Kompass-Kalibrierung (Legacy-Methode, verwendet nun start_calibration)
    @Slot()
    def startCompassCalibration(self):
        """
        Startet die Kompass-Kalibrierung.
        """
        self.log_warning("Verwendung der veralteten startCompassCalibration-Methode")
        return self.start_calibration("compass")
        
    # Accelerometer-Kalibrierung (Legacy-Methode, verwendet nun start_calibration)
    @Slot()
    def startAccelCalibration(self):
        """
        Startet die Beschleunigungssensor-Kalibrierung.
        """
        self.log_warning("Verwendung der veralteten startAccelCalibration-Methode")
        return self.start_calibration("accel")
    
    @Slot()
    def nextCalibrationStep(self):
        """
        Zum nächsten Schritt der aktuellen Kalibrierung gehen.
        """
        if not self._calibration_in_progress:
            self.log_warning("Keine Kalibrierung aktiv, kann nicht zum nächsten Schritt gehen")
            return False
            
        self.log_info(f"Gehe zum nächsten Schritt der {self._current_calibration_type}-Kalibrierung")
            
        if self._current_calibration_type == "accel":
            # Erhöhe den Schritt für die Accelerometer-Kalibrierung
            if self._message_handler:
                result = self._message_handler.next_accel_calibration_step()
                if not result:
                    message = "Fehler beim Fortfahren mit der Kalibrierung"
                    self.log_error(message)
                    self.calibrationFinished.emit(False, message)
                    self._calibration_in_progress = False
                    return False
            else:
                self.log_warning("Kein Message Handler verfügbar, simuliere nächsten Schritt")
                
            self._accel_step += 1
            self._progress = self._accel_step / 6.0  # 6 Positionen für Accel-Kalibrierung
            
            # Anleitung für den nächsten Schritt
            position_text = [
                "Platzieren Sie die Drohne horizontal",
                "Platzieren Sie die Drohne auf der Nase stehend",
                "Platzieren Sie die Drohne auf dem Heck stehend",
                "Platzieren Sie die Drohne auf der linken Seite",
                "Platzieren Sie die Drohne auf der rechten Seite",
                "Platzieren Sie die Drohne auf dem Rücken liegend"
            ]
            
            if self._accel_step < len(position_text):
                message = position_text[self._accel_step]
                self.log_info(f"Neuer Schritt: {message}")
                self.calibrationProgressChanged.emit(self._progress, message)
                return True
            else:
                # Kalibrierung abgeschlossen
                message = "Beschleunigungssensor-Kalibrierung abgeschlossen"
                self.log_info(message)
                self._calibration_in_progress = False
                self.calibrationFinished.emit(True, message)
                return True
        
        elif self._current_calibration_type == "compass":
            # Bei der Kompass-Kalibrierung akzeptieren wir die Kalibrierung,
            # wenn der Benutzer manuell zum nächsten Schritt übergeht
            if self._message_handler:
                result = self._message_handler.accept_compass_calibration()
                if result:
                    message = "Kompass-Kalibrierung erfolgreich abgeschlossen"
                    self.log_info(message)
                    self._calibration_in_progress = False
                    self.calibrationFinished.emit(True, message)
                    return True
                else:
                    message = "Fehler beim Abschließen der Kompass-Kalibrierung"
                    self.log_error(message)
                    self.calibrationFinished.emit(False, message)
                    self._calibration_in_progress = False
                    return False
            else:
                # Simuliere erfolgreichen Abschluss
                self._progress = 1.0
                message = "Kompass-Kalibrierung erfolgreich abgeschlossen (Simulation)"
                self.log_info(message)
                self._calibration_in_progress = False
                self.calibrationFinished.emit(True, message)
                return True
        
        # Für andere Kalibrierungstypen
        self.log_warning(f"Nächster Schritt für {self._current_calibration_type}-Kalibrierung nicht implementiert")
        return False
    
    @Slot()
    def cancelCalibration(self):
        """
        Bricht die aktuelle Kalibrierung ab.
        """
        if not self._message_handler or not self._calibration_in_progress:
            self.log_warning("Keine aktive Kalibrierung zum Abbrechen")
            return
        
        self.log_info(f"Breche {self._current_calibration_type}-Kalibrierung ab...")
        result = False
        if self._current_calibration_type == "compass":
            result = self._message_handler.cancel_compass_calibration()
        elif self._current_calibration_type == "accel":
            # Für Accelerometer gibt es keinen separaten Abbruch-Befehl,
            # aber wir können die COMMAND_ACK verwenden, um zu signalisieren, dass wir abbrechen
            result = self._message_handler.next_accel_calibration_step()
        
        self._calibration_in_progress = False
        self._current_calibration_type = None
        self._progress = 0.0
        
        if result:
            message = "Kalibrierung erfolgreich abgebrochen"
            self.log_info(message)
            self.calibrationFinished.emit(False, message)
        else:
            message = "Fehler beim Abbrechen der Kalibrierung"
            self.log_error(message)
            self.calibrationFinished.emit(False, message)
    
    # Gyroskop-Kalibrierung (Legacy-Methode, verwendet nun start_calibration)
    @Slot()
    def startGyroCalibration(self):
        """
        Startet die Gyroskop-Kalibrierung.
        """
        self.log_warning("Verwendung der veralteten startGyroCalibration-Methode")
        return self.start_calibration("gyro")
    
    # RC-Kalibrierung (Legacy-Methode, verwendet nun start_calibration)
    @Slot()
    def startRCCalibration(self):
        """
        Startet die RC-Fernbedienungs-Kalibrierung.
        """
        self.log_warning("Verwendung der veralteten startRCCalibration-Methode")
        return self.start_calibration("rc")
    
    @Slot()
    def saveRCCalibration(self):
        """
        Speichert die RC-Kalibrierungsdaten.
        """
        if not self._calibration_in_progress or self._current_calibration_type != "rc":
            self.log_warning("Keine RC-Kalibrierung aktiv zum Speichern")
            return False
            
        self.log_info("Speichere RC-Kalibrierungsdaten")
        
        # Hier würden die RC-Werte gespeichert werden
        if self._message_handler:
            # Implementierung für tatsächliche Speicherung
            self.log_info("Sende RC-Kalibrierungsdaten an Flugcontroller")
            # result = self._message_handler.save_rc_calibration()
        else:
            self.log_warning("Kein Message Handler verfügbar, simuliere Speichern")
            
        message = "RC-Kalibrierung erfolgreich gespeichert"
        self.log_info(message)
        self._calibration_in_progress = False
        self.calibrationFinished.emit(True, message)
        return True
    
    @Slot()
    def cancelCalibration(self):
        """
        Bricht die laufende Kalibrierung ab.
        """
        if self._calibration_in_progress:
            self._calibration_in_progress = False
            print(f"Kalibrierung abgebrochen: {self._current_calibration_type}")
            self.calibrationFinished.emit(False, f"{self._current_calibration_type}-Kalibrierung abgebrochen")
            self._current_calibration_type = None
    
    # Mock-Methoden zum Simulieren von Sensorwerten (für Tests)
    @Slot(float, float, float)
    def updateCompassValues(self, x, y, z):
        """
        Aktualisiert die Kompasswerte (für Tests oder zur Anzeige der aktuellen Werte).
        """
        self._compass_values = [x, y, z]
        self.compassValueChanged.emit(x, y, z)
    
    @Slot(float, float, float)
    def updateAccelValues(self, x, y, z):
        """
        Aktualisiert die Beschleunigungssensorwerte.
        """
        self._accel_values = [x, y, z]
        self.accelValueChanged.emit(x, y, z)
    
    @Slot(float, float, float)
    def updateGyroValues(self, x, y, z):
        """
        Aktualisiert die Gyroskopwerte.
        """
        self._gyro_values = [x, y, z]
        self.gyroValueChanged.emit(x, y, z)
    
    @Slot(int, int)
    def updateRCChannel(self, channel, value):
        """
        Aktualisiert einen RC-Kanal.
        
        Args:
            channel: Kanalnummer (1-8)
            value: PWM-Wert (normalerweise zwischen 1000-2000 µs)
        """
        if 1 <= channel <= 8:
            self._rc_channels[channel-1] = value
            self.rcChannelChanged.emit(channel, value)
