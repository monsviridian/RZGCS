"""
DroneKit Mission ViewModel für RZGCS
Stellt Mission-Management-Funktionen aus DroneKit für die QML-UI bereit
"""

from PySide6.QtCore import QObject, Signal, Slot, Property
from typing import List, Dict, Any
import json
import math

class DroneKitMissionViewModel(QObject):
    """
    ViewModel für Missionsmanagement mit DroneKit.
    """
    
    # Signale für UI-Updates
    missionChanged = Signal()
    currentWaypointChanged = Signal(int)
    missionStarted = Signal(object)
    missionCompleted = Signal()
    missionAborted = Signal()
    waypointReached = Signal(int)
    missionProgress = Signal(float)
    missionUploadStarted = Signal()
    missionUploadCompleted = Signal(bool, str)  # success, message
    missionDownloadStarted = Signal()
    missionDownloadCompleted = Signal(bool, str)  # success, message
    
    def __init__(self, drone_connector=None, parent=None):
        """Initialisiert das ViewModel mit optionaler Verbindung zum Connector"""
        super().__init__(parent)
        self._drone_connector = drone_connector
        
        # Missionsdaten
        self._waypoints = []
        self._current_waypoint = -1
        self._mission_progress = 0.0
        self._active_mission = False
        self._mission_name = ""
        
        # Verbinde DroneKit-Signale wenn Connector vorhanden
        if self._drone_connector:
            self._connect_signals()
            
        print("DroneKitMissionViewModel initialisiert")
    
    def set_drone_connector(self, drone_connector):
        """Setzt den DroneKit-Connector und verbindet die Signale"""
        self._drone_connector = drone_connector
        self._connect_signals()
    
    def _connect_signals(self):
        """Verbindet alle DroneKit-Signale mit lokalen Slots"""
        if not self._drone_connector:
            return
            
        try:
            # Verbinde Signale vom DroneKit-Connector
            self._drone_connector.mission_received.connect(self._on_mission_received)
            self._drone_connector.waypoint_reached.connect(self._on_waypoint_reached)
            self._drone_connector.mission_completed.connect(self._on_mission_completed)
            self._drone_connector.mission_upload_complete.connect(self._on_mission_upload_complete)
            self._drone_connector.mission_download_complete.connect(self._on_mission_download_complete)
            
            # Weitere Mission-Signale können hier verbunden werden
        except Exception as e:
            print(f"Fehler beim Verbinden der Mission-Signale: {e}")
    
    # --- Event-Handler ---
    
    def _on_mission_received(self, mission_dict):
        """
        Callback für empfangene Missionsdaten
        """
        try:
            if isinstance(mission_dict, dict):
                self._waypoints = mission_dict.get("waypoints", [])
                self._mission_name = mission_dict.get("name", "Unbenannte Mission")
                self.missionChanged.emit()
                print(f"Mission empfangen: {self._mission_name} mit {len(self._waypoints)} Wegpunkten")
        except Exception as e:
            print(f"Fehler bei der Verarbeitung der Mission: {e}")
    
    def _on_waypoint_reached(self, waypoint_index):
        """
        Callback für erreichte Wegpunkte
        """
        self._current_waypoint = waypoint_index
        self.currentWaypointChanged.emit(waypoint_index)
        self.waypointReached.emit(waypoint_index)
        
        # Berechne Missionsfortschritt
        if len(self._waypoints) > 0:
            self._mission_progress = (waypoint_index + 1) / len(self._waypoints) * 100.0
            self.missionProgress.emit(self._mission_progress)
    
    def _on_mission_completed(self):
        """
        Callback für abgeschlossene Mission
        """
        self._active_mission = False
        self._current_waypoint = -1
        self._mission_progress = 100.0
        self.missionCompleted.emit()
        self.missionProgress.emit(self._mission_progress)
    
    def _on_mission_aborted(self):
        """
        Callback für abgebrochene Mission
        """
        self._active_mission = False
        self._mission_progress = 0.0
        self.missionAborted.emit()
        self.missionProgress.emit(self._mission_progress)
    
    def _on_mission_upload_complete(self, success, message):
        """
        Callback für abgeschlossenen Mission-Upload
        """
        self.missionUploadCompleted.emit(success, message)
    
    def _on_mission_download_complete(self, success, message):
        """
        Callback für abgeschlossenen Mission-Download
        """
        self.missionDownloadCompleted.emit(success, message)
    
    # --- Properties ---
    
    @Property(list, notify=missionChanged)
    def waypoints(self):
        """Gibt die Liste der Wegpunkte zurück"""
        return self._waypoints
    
    @Property(int, notify=currentWaypointChanged)
    def currentWaypoint(self):
        """Gibt den aktuellen Wegpunkt-Index zurück"""
        return self._current_waypoint
    
    @Property(float, notify=missionProgress)
    def missionProgress(self):
        """Gibt den Missionsfortschritt in Prozent zurück"""
        return self._mission_progress
    
    @Property(bool)
    def activeMission(self):
        """Gibt zurück, ob eine Mission aktiv ist"""
        return self._active_mission
    
    @Property(str, notify=missionChanged)
    def missionName(self):
        """Gibt den Namen der Mission zurück"""
        return self._mission_name
    
    # --- Slots ---
    
    @Slot()
    def downloadMission(self):
        """
        Lädt die aktuelle Mission vom Vehicle herunter
        """
        if not self._drone_connector or not self._drone_connector.is_connected():
            print("Keine Verbindung zum Vehicle")
            self.missionDownloadCompleted.emit(False, "Keine Verbindung zum Vehicle")
            return
            
        print("Lade Mission vom Vehicle...")
        self.missionDownloadStarted.emit()
        
        try:
            self._drone_connector.download_mission()
        except Exception as e:
            print(f"Fehler beim Herunterladen der Mission: {e}")
            self.missionDownloadCompleted.emit(False, str(e))
    
    @Slot(str)
    def uploadMission(self, mission_json):
        """
        Lädt eine Mission zum Vehicle hoch
        
        :param mission_json: Mission als JSON-String
        """
        if not self._drone_connector or not self._drone_connector.is_connected():
            print("Keine Verbindung zum Vehicle")
            self.missionUploadCompleted.emit(False, "Keine Verbindung zum Vehicle")
            return
            
        try:
            # JSON-String in Daten-Dictionary konvertieren
            mission_data = json.loads(mission_json)
            
            print(f"Lade Mission zum Vehicle... {mission_data.get('name', 'Unbenannte Mission')}")
            self.missionUploadStarted.emit()
            
            # Mission zum Vehicle hochladen
            self._drone_connector.upload_mission(mission_data)
            
        except json.JSONDecodeError as e:
            print(f"Fehler beim Parsen der Mission JSON: {e}")
            self.missionUploadCompleted.emit(False, f"Ungültiges JSON-Format: {str(e)}")
        except Exception as e:
            print(f"Fehler beim Hochladen der Mission: {e}")
            self.missionUploadCompleted.emit(False, str(e))
    
    @Slot()
    def clearMission(self):
        """Löscht die aktuelle Mission"""
        if not self._drone_connector:
            return
            
        try:
            self._drone_connector.clear_mission()
            self._waypoints = []
            self._current_waypoint = -1
            self._mission_progress = 0.0
            self._active_mission = False
            self._mission_name = ""
            self.missionChanged.emit()
            
        except Exception as e:
            print(f"Fehler beim Löschen der Mission: {e}")
    
    @Slot()
    def startMission(self):
        """Startet die aktuelle Mission"""
        if not self._drone_connector or not self._drone_connector.is_connected():
            print("Keine Verbindung zum Vehicle")
            return
            
        print("Starte Mission...")
        
        try:
            # Mission starten
            self._drone_connector.start_mission()
            
            # Status aktualisieren
            self._active_mission = True
            self._current_waypoint = 0
            self._mission_progress = 0.0
            
            # Signale emittieren
            self.currentWaypointChanged.emit(0)
            self.missionProgress.emit(0.0)
            self.missionStarted.emit({"name": self._mission_name, "waypoints": self._waypoints})
            
        except Exception as e:
            print(f"Fehler beim Starten der Mission: {e}")
    
    @Slot()
    def abortMission(self):
        """Bricht die aktuelle Mission ab"""
        if not self._drone_connector or not self._active_mission:
            return
            
        print("Breche Mission ab...")
        
        try:
            # Mission abbrechen
            self._drone_connector.abort_mission()
            
            # Status aktualisieren
            self._active_mission = False
            self._mission_progress = 0.0
            
            # Signal emittieren
            self.missionAborted.emit()
            
        except Exception as e:
            print(f"Fehler beim Abbrechen der Mission: {e}")
    
    @Slot(str)
    def setMissionFromJson(self, mission_json):
        """
        Setzt die Mission aus einem JSON-String
        
        :param mission_json: Mission als JSON-String
        """
        try:
            # JSON-String in Daten-Dictionary konvertieren
            mission_data = json.loads(mission_json)
            
            # Daten setzen
            self._waypoints = mission_data.get("waypoints", [])
            self._mission_name = mission_data.get("name", "Unbenannte Mission")
            self._current_waypoint = -1
            self._mission_progress = 0.0
            self._active_mission = False
            
            # Signal emittieren
            self.missionChanged.emit()
            
            print(f"Mission gesetzt: {self._mission_name} mit {len(self._waypoints)} Wegpunkten")
            
        except json.JSONDecodeError as e:
            print(f"Fehler beim Parsen der Mission JSON: {e}")
        except Exception as e:
            print(f"Fehler beim Setzen der Mission: {e}")
    
    @Slot(result=str)
    def getMissionAsJson(self):
        """
        Gibt die aktuelle Mission als JSON-String zurück
        """
        mission_data = {
            "name": self._mission_name,
            "waypoints": self._waypoints
        }
        
        try:
            return json.dumps(mission_data)
        except Exception as e:
            print(f"Fehler beim Konvertieren der Mission zu JSON: {e}")
            return "{}"
