from PySide6.QtCore import QObject, Slot, Signal, Property, QTimer
from PySide6.QtQml import QmlElement
import math
import time

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
    
    @Slot(object)
    def initialize(self, message_handler):
        """
        Initialisiert den Controller und verbindet ihn mit dem Message Handler.
        
        Args:
            message_handler: Die Instanz des MessageHandler, um MAVLink-Befehle zu senden
        """
        print("Initialisiere CalibrationViewController")
        self._message_handler = message_handler
        
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
                
            # Timer für simulierte Daten starten (falls keine echten Daten empfangen werden)
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
        if not self._calibration_in_progress:
            return
            
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
                
            self._accel_values = [x, y, z]
            self.accelValueChanged.emit(x, y, z)
    
    # Kompass-Kalibrierung
    @Slot()
    def startCompassCalibration(self):
        """
        Startet die Kompass-Kalibrierung.
        """
        if not self._message_handler:
            print("Fehler: Kein Message Handler verfügbar")
            self.calibrationFinished.emit(False, "Fehler: Keine Verbindung zum Flugcontroller")
            return
            
        self._calibration_in_progress = True
        self._current_calibration_type = "compass"
        self._progress = 0.0
        
        # Sende MAVLink-Befehl zur Kompass-Kalibrierung
        result = self._message_handler.start_compass_calibration()
        
        if result:
            self.calibrationProgressChanged.emit(self._progress, "Rotieren Sie die Drohne in alle Richtungen")
            print("Kompass-Kalibrierung gestartet")
        else:
            self._calibration_in_progress = False
            self.calibrationFinished.emit(False, "Fehler beim Starten der Kompass-Kalibrierung")
    
    # Beschleunigungssensor-Kalibrierung
    @Slot()
    def startAccelCalibration(self):
        """
        Startet die Beschleunigungssensor-Kalibrierung.
        """
        if not self._message_handler:
            print("Fehler: Kein Message Handler verfügbar")
            self.calibrationFinished.emit(False, "Fehler: Keine Verbindung zum Flugcontroller")
            return
            
        self._calibration_in_progress = True
        self._current_calibration_type = "accel"
        self._progress = 0.0
        self._accel_step = 0
        
        # Sende MAVLink-Befehl zur Accelerometer-Kalibrierung
        result = self._message_handler.start_accel_calibration()
        
        if result:
            self.calibrationProgressChanged.emit(self._progress, "Platzieren Sie die Drohne horizontal")
            print("Accelerometer-Kalibrierung gestartet")
        else:
            self._calibration_in_progress = False
            self.calibrationFinished.emit(False, "Fehler beim Starten der Accelerometer-Kalibrierung")
    
    @Slot()
    def nextCalibrationStep(self):
        """Zum nächsten Schritt der aktuellen Kalibrierung gehen."""
        if not self._calibration_in_progress:
            return
            
        if self._current_calibration_type == "accel":
            # Erhöhe den Schritt für die Accelerometer-Kalibrierung
            result = self._message_handler.next_accel_calibration_step()
            if not result:
                self.calibrationFinished.emit(False, "Fehler beim Fortfahren mit der Kalibrierung")
                self._calibration_in_progress = False
                return
                
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
                self.calibrationProgressChanged.emit(self._progress, position_text[self._accel_step])
            else:
                # Kalibrierung abgeschlossen
                self._calibration_in_progress = False
                self.calibrationFinished.emit(True, "Beschleunigungssensor-Kalibrierung abgeschlossen")
        
        elif self._current_calibration_type == "compass":
            # Bei der Kompass-Kalibrierung akzeptieren wir die Kalibrierung,
            # wenn der Benutzer manuell zum nächsten Schritt übergeht
            result = self._message_handler.accept_compass_calibration()
            if result:
                self._calibration_in_progress = False
                self.calibrationFinished.emit(True, "Kompass-Kalibrierung erfolgreich abgeschlossen")
            else:
                self.calibrationFinished.emit(False, "Fehler beim Abschließen der Kompass-Kalibrierung")
                self._calibration_in_progress = False
    
    @Slot()
    def cancelCalibration(self):
        """
        Bricht die aktuelle Kalibrierung ab.
        """
        if not self._message_handler or not self._calibration_in_progress:
            return
        
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
            self.calibrationFinished.emit(False, "Kalibrierung abgebrochen")
        else:
            self.calibrationFinished.emit(False, "Fehler beim Abbrechen der Kalibrierung")
    
    # Gyroskop-Kalibrierung
    @Slot()
    def startGyroCalibration(self):
        """
        Startet die Gyroskop-Kalibrierung.
        """
        self._calibration_in_progress = True
        self._current_calibration_type = "gyro"
        self._progress = 0.0
        print("Starte Gyroskop-Kalibrierung")
        self.calibrationProgressChanged.emit(self._progress, "Halten Sie die Drohne still")
        # Hier würde die tatsächliche Initiierung der Kalibrierung erfolgen
    
    # RC-Kalibrierung
    @Slot()
    def startRCCalibration(self):
        """
        Startet die RC-Fernbedienungs-Kalibrierung.
        """
        self._calibration_in_progress = True
        self._current_calibration_type = "rc"
        self._progress = 0.0
        print("Starte RC-Kalibrierung")
        self.calibrationProgressChanged.emit(self._progress, "Bewegen Sie alle Sticks und Schalter")
        # Hier würde die tatsächliche Initiierung der Kalibrierung erfolgen
    
    @Slot()
    def saveRCCalibration(self):
        """
        Speichert die RC-Kalibrierungsdaten.
        """
        print("Speichere RC-Kalibrierung")
        # Hier würden die RC-Werte gespeichert werden
        self._calibration_in_progress = False
        self.calibrationFinished.emit(True, "RC-Kalibrierung gespeichert")
    
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
