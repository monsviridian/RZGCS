import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../Python/backend/flight_control')))
import mavlink_main
from PySide6.QtCore import QObject, Signal, Slot, Property
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtGui import QGuiApplication

class BackendBridge(QObject):
    # Signale für QML
    stateChanged = Signal(dict)
    modeChanged = Signal(str)
    errorOccurred = Signal(str)
    missionStarted = Signal(dict)
    missionCompleted = Signal(dict)
    missionAborted = Signal(dict)
    waypointReached = Signal(dict)
    missionProgress = Signal(float)
    safetyViolation = Signal(str)
    safetyWarning = Signal(str)
    safetyCleared = Signal(str)

    def __init__(self):
        super().__init__()
        self.mavlink = mavlink_main.MAVLinkController()
        self.current_state = {}
        self.current_mode = "DISARMED"
        
        # Verbinde MAVLink-Signale
        self.mavlink.state_changed.connect(self._on_state_changed)
        self.mavlink.mode_changed.connect(self._on_mode_changed)
        self.mavlink.error_occurred.connect(self._on_error)
        self.mavlink.mission_started.connect(self._on_mission_started)
        self.mavlink.mission_completed.connect(self._on_mission_completed)
        self.mavlink.mission_aborted.connect(self._on_mission_aborted)
        self.mavlink.waypoint_reached.connect(self._on_waypoint_reached)
        self.mavlink.mission_progress.connect(self._on_mission_progress)
        self.mavlink.safety_violation.connect(self._on_safety_violation)
        self.mavlink.safety_warning.connect(self._on_safety_warning)
        self.mavlink.safety_cleared.connect(self._on_safety_cleared)

    @Slot()
    def connect(self):
        """Verbindet mit dem MAVLink-System"""
        try:
            self.mavlink.connect_mavlink()
            return True
        except Exception as e:
            self.errorOccurred.emit(str(e))
            return False

    @Slot()
    def disconnect(self):
        """Trennt die Verbindung zum MAVLink-System"""
        try:
            self.mavlink.disconnect()
            return True
        except Exception as e:
            self.errorOccurred.emit(str(e))
            return False

    @Slot(str)
    def set_mode(self, mode):
        """Setzt den Flugmodus"""
        try:
            self.mavlink.set_mode(mode)
            return True
        except Exception as e:
            self.errorOccurred.emit(str(e))
            return False

    @Slot(dict)
    def start_mission(self, mission):
        """Startet eine Mission"""
        try:
            self.mavlink.start_mission(mission)
            return True
        except Exception as e:
            self.errorOccurred.emit(str(e))
            return False

    @Slot()
    def abort_mission(self):
        """Bricht die aktuelle Mission ab"""
        try:
            self.mavlink.abort_mission()
            return True
        except Exception as e:
            self.errorOccurred.emit(str(e))
            return False

    # Signal-Handler
    def _on_state_changed(self, state):
        self.current_state = state
        self.stateChanged.emit(state)

    def _on_mode_changed(self, mode):
        self.current_mode = mode
        self.modeChanged.emit(mode)

    def _on_error(self, error):
        self.errorOccurred.emit(error)

    def _on_mission_started(self, mission):
        self.missionStarted.emit(mission)

    def _on_mission_completed(self, mission):
        self.missionCompleted.emit(mission)

    def _on_mission_aborted(self, mission):
        self.missionAborted.emit(mission)

    def _on_waypoint_reached(self, waypoint):
        self.waypointReached.emit(waypoint)

    def _on_mission_progress(self, progress):
        self.missionProgress.emit(progress)

    def _on_safety_violation(self, message):
        self.safetyViolation.emit(message)

    def _on_safety_warning(self, message):
        self.safetyWarning.emit(message)

    def _on_safety_cleared(self, message):
        self.safetyCleared.emit(message)

def main():
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()

    # Registriere Backend-Bridge
    backend = BackendBridge()
    engine.rootContext().setContextProperty("backend", backend)

    # Lade QML
    qml_file = os.path.join(os.path.dirname(__file__), "App.qml")
    engine.load(QUrl.fromLocalFile(qml_file))

    if not engine.rootObjects():
        sys.exit(-1)

    # Starte MAVLink-Controller
    backend.mavlink.start()

    # Starte Anwendung
    sys.exit(app.exec()) 