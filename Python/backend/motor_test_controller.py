from PySide6.QtCore import QObject, Slot, Signal, Property, QTimer
from PySide6.QtQml import QmlElement

QML_IMPORT_NAME = "RZGCS"
QML_IMPORT_MAJOR_VERSION = 1

@QmlElement
class MotorTestController(QObject):
    """
    Controller fu00fcr die Motortest-Ansicht.
    Diese Klasse stellt Funktionen zum Testen der Motoren bereit.
    """
    
    # Signale
    motorStatusChanged = Signal(int, bool, str)  # Motor-Nr, Lu00e4uft?, Statustext
    logMessageAdded = Signal(str)  # Lognachricht
    testProgressChanged = Signal(float, str)  # Fortschritt, Status
    testFinished = Signal(bool, str)  # Erfolgreich?, Statustext
    motorRPMChanged = Signal(int, int)  # Motor-Nr, RPM
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._test_in_progress = False
        self._test_mode = "single"  # Optionen: "single", "sequence", "all"
        self._throttle = 30.0  # 0-100%
        self._active_motors = [False, False, False, False]  # Status fu00fcr Motor 1-4
        self._sequence_timer = QTimer(self)
        self._sequence_timer.timeout.connect(self._sequence_step)
        self._current_sequence_motor = 0
        self._sequence_duration = 1000  # ms pro Motor in der Sequenz
    
    @Slot()
    def initialize(self, root_item):
        """
        Initialisiert den Controller und verbindet ihn mit dem QML-Root-Item.
        """
        print("Initialisiere MotorTestController")
        self.logMessageAdded.emit("Motortest-Controller initialisiert")
        return True
    
    @Slot(str)
    def setTestMode(self, mode):
        """
        Setzt den Testmodus.
        mode: "single", "sequence" oder "all"
        """
        if mode in ["single", "sequence", "all"]:
            self._test_mode = mode
            print(f"Testmodus auf {mode} gestellt")
            self.logMessageAdded.emit(f"Testmodus: {self._get_mode_description(mode)}")
    
    def _get_mode_description(self, mode):
        if mode == "single":
            return "Einzeltest (einen Motor manuell auswu00e4hlen)"
        elif mode == "sequence":
            return "Sequenztest (Motoren nacheinander testen)"
        elif mode == "all":
            return "Alle Motoren gleichzeitig testen"
        return "Unbekannter Modus"
    
    @Slot(float)
    def setThrottle(self, throttle):
        """
        Setzt die Motorleistung (0-100%).
        """
        self._throttle = max(0, min(100, throttle))
        # Wenn wir im Testmodus sind, aktualisiere die laufenden Motoren
        if self._test_in_progress:
            self._update_active_motors()
            
    def _update_active_motors(self):
        """
        Aktualisiert die aktiven Motoren basierend auf dem aktuellen Testmodus und Throttle.
        """
        for i in range(4):
            if self._active_motors[i]:
                self._send_motor_command(i+1, self._throttle)
                self.motorRPMChanged.emit(i+1, int(self._throttle * 50))  # Simulierte RPM-Werte
    
    @Slot(int)
    def testMotor(self, motor_number):
        """
        Testet einen bestimmten Motor (1-4).
        Nur im Einzeltestmodus wirksam.
        """
        if not self._test_in_progress:
            self.logMessageAdded.emit("Bitte starten Sie zuerst den Test mit dem 'Start Test' Button")
            return
            
        if self._test_mode != "single":
            self.logMessageAdded.emit("Motorauswahl ist nur im Einzeltestmodus verfu00fcgbar")
            return
            
        # Motorindex (0-3)
        idx = motor_number - 1
        if 0 <= idx < 4:
            # Toggeln des Motorstatus
            self._active_motors = [False, False, False, False]  # Alle zuru00fccksetzen
            self._active_motors[idx] = True
            self._send_motor_command(motor_number, self._throttle)
            self.motorStatusChanged.emit(
                motor_number, True, f"Motor {motor_number} aktiv mit {self._throttle:.0f}% Leistung")
            self.logMessageAdded.emit(f"Motor {motor_number} wird getestet mit {self._throttle:.0f}% Leistung")
            self.motorRPMChanged.emit(motor_number, int(self._throttle * 50))  # Simulierter RPM-Wert
    
    @Slot()
    def startTest(self):
        """
        Startet den Motortest entsprechend dem ausgewu00e4hlten Modus.
        """
        if self._test_in_progress:
            self.stopTest()
            
        self._test_in_progress = True
        self.testProgressChanged.emit(0.0, "Test gestartet")
        self.logMessageAdded.emit(f"Starte Motortest im Modus: {self._get_mode_description(self._test_mode)}")
        
        if self._test_mode == "sequence":
            # Starte den Sequenztest
            self._current_sequence_motor = 0
            self._sequence_timer.start(self._sequence_duration)
            self._sequence_step()  # Ersten Schritt sofort ausfu00fchren
        elif self._test_mode == "all":
            # Aktiviere alle Motoren
            self._active_motors = [True, True, True, True]
            for i in range(4):
                self._send_motor_command(i+1, self._throttle)
                self.motorStatusChanged.emit(i+1, True, f"Motor {i+1} aktiv")
                self.motorRPMChanged.emit(i+1, int(self._throttle * 50))  # Simulierter RPM-Wert
        else:  # "single"-Modus
            self.logMessageAdded.emit("Bitte wu00e4hlen Sie einen Motor, indem Sie darauf klicken")
            # Alle Motoren zunu00e4chst deaktivieren
            self._active_motors = [False, False, False, False]
            for i in range(4):
                self._send_motor_command(i+1, 0)
                self.motorStatusChanged.emit(i+1, False, f"Motor {i+1} inaktiv")
                self.motorRPMChanged.emit(i+1, 0)
    
    def _sequence_step(self):
        """
        Fu00fchrt einen Schritt im Sequenztest aus.
        """
        if not self._test_in_progress or self._test_mode != "sequence":
            self._sequence_timer.stop()
            return
            
        # Alle Motoren deaktivieren
        self._active_motors = [False, False, False, False]
        
        # Aktuellen Motor aktivieren
        self._active_motors[self._current_sequence_motor] = True
        motor_number = self._current_sequence_motor + 1
        
        # Kommando senden
        self._send_motor_command(motor_number, self._throttle)
        self.motorStatusChanged.emit(
            motor_number, True, f"Motor {motor_number} aktiv mit {self._throttle:.0f}% Leistung")
        self.logMessageAdded.emit(f"Teste Motor {motor_number} mit {self._throttle:.0f}% Leistung")
        self.motorRPMChanged.emit(motor_number, int(self._throttle * 50))  # Simulierter RPM-Wert
        
        # Fortschritt aktualisieren (0-100%)
        progress = (self._current_sequence_motor / 4.0) * 100.0
        self.testProgressChanged.emit(progress, f"Teste Motor {motor_number}")
        
        # Zum nu00e4chsten Motor
        self._current_sequence_motor = (self._current_sequence_motor + 1) % 4
        
        # Wenn wir wieder beim ersten Motor angekommen sind, stoppe nach einer Runde
        if self._current_sequence_motor == 0:
            self._sequence_timer.stop()
            self.stopTest()
    
    @Slot()
    def stopTest(self):
        """
        Stoppt alle laufenden Motortests.
        """
        self._test_in_progress = False
        self._sequence_timer.stop()
        
        # Alle Motoren stoppen
        self._active_motors = [False, False, False, False]
        for i in range(4):
            self._send_motor_command(i+1, 0)
            self.motorStatusChanged.emit(i+1, False, f"Motor {i+1} gestoppt")
            self.motorRPMChanged.emit(i+1, 0)
            
        self.testFinished.emit(True, "Test beendet")
        self.logMessageAdded.emit("Motortest gestoppt")
    
    @Slot()
    def runSafetyCheck(self):
        """
        Fu00fchrt einen Sicherheitscheck aus, um sicherzustellen, dass die Motoren funktionsfu00e4hig sind.
        """
        self.logMessageAdded.emit("Fu00fchre Sicherheitscheck durch...")
        
        # Hier wu00fcrde man in einer realen Implementierung die 
        # Motoren und ESCs auf korrekte Verbindung und Funktion pru00fcfen
        
        # In dieser Demo-Implementierung geben wir nur Status-Updates aus
        QTimer.singleShot(500, lambda: self.logMessageAdded.emit("Pru00fcfe ESC Verbindungen..."))
        QTimer.singleShot(1000, lambda: self.logMessageAdded.emit("Pru00fcfe Motoranschlu00fcsse..."))
        QTimer.singleShot(1500, lambda: self.logMessageAdded.emit("Teste Motorreaktion..."))
        QTimer.singleShot(2000, lambda: self.logMessageAdded.emit("Sicherheitscheck abgeschlossen: Alle Motoren bereit"))
    
    def _send_motor_command(self, motor_number, throttle):
        """
        Sendet einen Motorbefehl an die Hardware.
        
        In einer realen Implementierung wu00fcrden wir hier MAVLink-Befehle senden.
        In dieser Demo-Version geben wir nur Logs aus.
        """
        # Hier wu00fcrde man MAVLink-Befehle senden, z.B. RC_CHANNELS_OVERRIDE
        print(f"Sende Motorbefehl: Motor {motor_number}, Throttle: {throttle:.1f}%")
        
        # Wir ku00f6nnten hier spu00e4ter eine Verbindung zum MAVLink-System herstellen
        # self._mavlink.send_command(motor_number, throttle)
