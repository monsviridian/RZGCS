"""
RZGCS Backend - Hauptklasse für die QML-Integration
"""

from PySide6.QtCore import QObject, Signal, Slot, Property
from PySide6.QtQml import QmlElement

# QML Import Definitionen
QML_IMPORT_NAME = "RZGCS"
QML_IMPORT_MAJOR_VERSION = 1

@QmlElement
class Backend(QObject):
    # Status-Signale
    stateChanged = Signal(dict)  # Enthält den aktuellen Systemzustand
    modeChanged = Signal(str)    # Aktueller Flugmodus
    errorOccurred = Signal(str)  # Fehlermeldungen
    
    # Missions-Signale
    missionStarted = Signal(dict)    # Mission gestartet
    missionCompleted = Signal(dict)  # Mission abgeschlossen
    missionAborted = Signal(dict)    # Mission abgebrochen
    waypointReached = Signal(dict)   # Wegpunkt erreicht
    missionProgress = Signal(float)  # Missionsfortschritt
    
    # Safety-Signale
    safetyViolation = Signal(str)  # Sicherheitsverletzung
    safetyWarning = Signal(str)    # Sicherheitswarnung
    safetyCleared = Signal(str)    # Sicherheitsstatus normal
    
    def __init__(self):
        super().__init__()
        self._connected = False
        self._current_mode = "UNKNOWN"
        self._current_state = {
            "attitude": {"roll": 0, "pitch": 0, "yaw": 0},
            "position": {"lat": 0, "lon": 0, "alt": 0},
            "flight_phase": "DISCONNECTED"
        }
    
    @Property(bool, notify=stateChanged)
    def connected(self):
        return self._connected
    
    @Slot()
    def connect(self):
        """Verbindung zum Fluggerät herstellen"""
        # TODO: Implementiere die tatsächliche Verbindungslogik
        self._connected = True
        self.stateChanged.emit(self._current_state)
    
    @Slot()
    def disconnect(self):
        """Verbindung zum Fluggerät trennen"""
        # TODO: Implementiere die tatsächliche Trennung
        self._connected = False
        self._current_state["flight_phase"] = "DISCONNECTED"
        self.stateChanged.emit(self._current_state)
    
    @Slot(str)
    def setMode(self, mode):
        """Flugmodus ändern"""
        self._current_mode = mode
        self.modeChanged.emit(mode)
    
    @Slot(dict)
    def updateState(self, state):
        """Systemzustand aktualisieren"""
        self._current_state.update(state)
        self.stateChanged.emit(self._current_state) 