"""
Mission Planner ViewModel - Stellt die DroneKit Mission-Funktionalität für QML bereit
"""

from PySide6.QtCore import QObject, Signal, Slot, Property, QUrl
from typing import List, Dict, Any, Optional

# Sichere DroneKit-Imports mit Fallback
try:
    from dronekit import Vehicle, VehicleMode
    DRONEKIT_AVAILABLE = True
except ImportError:
    # Fallback-Klassen wenn DroneKit nicht verfügbar ist
    class Vehicle:
        pass
    class VehicleMode:
        pass
    DRONEKIT_AVAILABLE = False
    print("WARNUNG: DroneKit nicht verfügbar - Mission-Funktionalität wird eingeschränkt")

# Import des Mission Handlers - mit direktem Import statt über das Modul
try:
    from backend.rzgcs_dronekit.mission_handler import DroneKitMissionHandler
    MISSION_HANDLER_AVAILABLE = True
except ImportError:
    DroneKitMissionHandler = None
    MISSION_HANDLER_AVAILABLE = False
    print("WARNUNG: DroneKit Mission Handler nicht verfügbar")


class MissionPlannerViewModel(QObject):
    """
    ViewModel für FlightView/Mission Planner
    Stellt die Mission-Funktionalität für die QML-Oberfläche bereit
    """

    # Signals
    missionUploaded = Signal(int)  # Anzahl der Wegpunkte
    missionDownloaded = Signal(int)  # Anzahl der Wegpunkte
    missionStarted = Signal()
    missionPaused = Signal()
    missionResumed = Signal()
    missionCompleted = Signal()
    waypointReached = Signal(int)  # Wegpunkt-Index
    missionError = Signal(str)
    missionLog = Signal(str)
    dronePositionChanged = Signal(float, float, float)  # lat, lon, alt
    droneHeadingChanged = Signal(float)  # heading in Grad
    waypointListChanged = Signal()  # <-- NEU: Signal für QML

    def __init__(self, serialConnector, parent=None):
        """
        Initialisiert das Mission Planner ViewModel
        
        Args:
            serialConnector: Die SerialConnector-Instanz
            parent: Das Elternobjekt
        """
        super().__init__(parent)
        self._serialConnector = serialConnector
        self._vehicle = None
        self._mission_handler = None
        self._waypoints = []
        self._current_waypoint = 0
        self._total_waypoints = 0
        self._mission_running = False
        
        # Position und Ausrichtung der Drohne
        self._drone_lat = 50.110924  # Default: Frankfurt
        self._drone_lon = 8.682127
        self._drone_alt = 100.0
        self._drone_heading = 0.0
        
        # Home- und Ziel-Positionen
        self._home_lat = 50.110924
        self._home_lon = 8.682127
        self._home_alt = 0.0
        self._target_lat = 50.111000
        self._target_lon = 8.683000
        self._target_alt = 50.0
        
        # Testdaten für Waypoints (werden beim Start angezeigt)
        self._waypoints = [
            {'lat': 50.110924, 'lon': 8.682127, 'alt': 100, 'type': 'waypoint', 'index': 0},
            {'lat': 50.111, 'lon': 8.683, 'alt': 110, 'type': 'waypoint', 'index': 1},
            {'lat': 50.112, 'lon': 8.684, 'alt': 120, 'type': 'waypoint', 'index': 2}
        ]
        
        # Verbinden der SerialConnector-Signals
        if self._serialConnector:
            self._serialConnector.connectedChanged.connect(self._on_connection_changed)
    
    def _on_connection_changed(self):
        """Handler für Verbindungsänderungen"""
        if self._serialConnector.connected:
            # Verbunden: Mission Handler initialisieren
            self._vehicle = self._serialConnector.get_vehicle()
            if self._vehicle and DRONEKIT_AVAILABLE and MISSION_HANDLER_AVAILABLE:
                try:
                    self._mission_handler = DroneKitMissionHandler(self._vehicle, self._serialConnector)
                    
                    # Verbinde Mission Handler Signals
                    self._mission_handler.mission_uploaded.connect(self.missionUploaded.emit)
                    self._mission_handler.mission_downloaded.connect(self.missionDownloaded.emit)
                    self._mission_handler.mission_started.connect(self.missionStarted.emit)
                    self._mission_handler.mission_paused.connect(self.missionPaused.emit)
                    self._mission_handler.mission_resumed.connect(self.missionResumed.emit)
                    self._mission_handler.mission_completed.connect(self.missionCompleted.emit)
                    self._mission_handler.waypoint_reached.connect(self.waypointReached.emit)
                    self._mission_handler.mission_error.connect(self.missionError.emit)
                    self._mission_handler.mission_log.connect(self.missionLog.emit)
                    
                    # Position-Updates überwachen
                    if hasattr(self._vehicle, 'location') and hasattr(self._vehicle.location, 'global_frame'):
                        self._update_position()
                        
                except Exception as e:
                    self.missionError.emit(f"Fehler beim Initialisieren des Mission Handlers: {str(e)}")
            else:
                if not DRONEKIT_AVAILABLE:
                    self.missionError.emit("DroneKit nicht verfügbar - Mission-Funktionalität eingeschränkt")
                elif not MISSION_HANDLER_AVAILABLE:
                    self.missionError.emit("Mission Handler nicht verfügbar - Mission-Funktionalität eingeschränkt")
        else:
            # Verbindung getrennt: Mission Handler zurücksetzen
            self._mission_handler = None
            self._vehicle = None
    
    def _update_position(self):
        """Aktualisiert die Drohnenposition aus dem Fahrzeug"""
        if self._vehicle and hasattr(self._vehicle, 'location') and hasattr(self._vehicle.location, 'global_frame'):
            location = self._vehicle.location.global_frame
            if location and hasattr(location, 'lat') and hasattr(location, 'lon'):
                self._drone_lat = location.lat
                self._drone_lon = location.lon
                self._drone_alt = location.alt
                self.dronePositionChanged.emit(self._drone_lat, self._drone_lon, self._drone_alt)
            
            if hasattr(self._vehicle, 'attitude') and hasattr(self._vehicle.attitude, 'yaw'):
                # Umrechnung von Radians in Grad
                import math
                self._drone_heading = math.degrees(self._vehicle.attitude.yaw) % 360
                self.droneHeadingChanged.emit(self._drone_heading)
    
    # --- Positions-Properties ---
    
    @Property(float)
    def droneLatitude(self):
        """Gibt die aktuelle Breite der Drohne zurück"""
        return self._drone_lat
    
    @Property(float)
    def droneLongitude(self):
        """Gibt die aktuelle Länge der Drohne zurück"""
        return self._drone_lon
    
    @Property(float)
    def droneAltitude(self):
        """Gibt die aktuelle Höhe der Drohne zurück"""
        return self._drone_alt
    
    @Property(float)
    def droneHeading(self):
        """Gibt die aktuelle Ausrichtung der Drohne zurück"""
        return self._drone_heading
    
    # --- Home- und Ziel-Positionen ---
    
    @Property(float)
    def homeLatitude(self):
        """Gibt die Home-Breite zurück"""
        return self._home_lat
    
    @Property(float)
    def homeLongitude(self):
        """Gibt die Home-Länge zurück"""
        return self._home_lon
    
    @Property(float)
    def homeAltitude(self):
        """Gibt die Home-Höhe zurück"""
        return self._home_alt
    
    @Property(float)
    def targetLatitude(self):
        """Gibt die Ziel-Breite zurück"""
        return self._target_lat
    
    @Property(float)
    def targetLongitude(self):
        """Gibt die Ziel-Länge zurück"""
        return self._target_lon
    
    @Property(float)
    def targetAltitude(self):
        """Gibt die Ziel-Höhe zurück"""
        return self._target_alt
    
    @Property('QVariantList', notify=waypointListChanged)
    def waypointList(self):
        """Gibt die aktuelle Liste der Wegpunkte für QML zurück"""
        # Erstelle erweiterte Liste mit Home, Waypoints und Ziel
        result = []
        
        # Home-Position hinzufügen
        result.append({
            'latitude': self._home_lat,
            'longitude': self._home_lon,
            'altitude': self._home_alt,
            'type': 'home',
            'index': -1,
            'label': 'HOME'
        })
        
        # Waypoints hinzufügen
        for i, wp in enumerate(self._waypoints):
            result.append({
                'latitude': wp['lat'],
                'longitude': wp['lon'],
                'altitude': wp['alt'],
                'type': wp.get('type', 'waypoint'),
                'index': wp.get('index', i),
                'label': f'WP{i+1}'
            })
        
        # Ziel-Position hinzufügen
        result.append({
            'latitude': self._target_lat,
            'longitude': self._target_lon,
            'altitude': self._target_alt,
            'type': 'target',
            'index': len(self._waypoints),
            'label': 'TARGET'
        })
        
        return result
    
    # --- Mission Management ---
    
    @Slot()
    def refreshMission(self):
        """Lädt die aktuelle Mission vom Fahrzeug herunter"""
        if not DRONEKIT_AVAILABLE or not MISSION_HANDLER_AVAILABLE:
            self.missionError.emit("DroneKit oder Mission Handler nicht verfügbar")
            return
            
        if self._mission_handler:
            try:
                self._mission_handler.download_mission()
                self.missionLog.emit("Lade Mission vom Fahrzeug...")
            except Exception as e:
                self.missionError.emit(f"Fehler beim Laden der Mission: {str(e)}")
    
    @Slot(list)
    def uploadMission(self, waypoints):
        """Lädt eine Mission auf das Fahrzeug hoch"""
        if not DRONEKIT_AVAILABLE or not MISSION_HANDLER_AVAILABLE:
            self.missionError.emit("DroneKit oder Mission Handler nicht verfügbar")
            return
            
        if self._mission_handler:
            try:
                self._mission_handler.upload_mission(waypoints)
                self._waypoints = waypoints
                self._total_waypoints = len(waypoints)
                self.missionLog.emit(f"Lade Mission mit {len(waypoints)} Wegpunkten hoch...")
            except Exception as e:
                self.missionError.emit(f"Fehler beim Hochladen der Mission: {str(e)}")
    
    @Slot()
    def startMission(self):
        """Startet die Mission"""
        if not DRONEKIT_AVAILABLE or not MISSION_HANDLER_AVAILABLE:
            self.missionError.emit("DroneKit oder Mission Handler nicht verfügbar")
            return
            
        if self._mission_handler:
            try:
                self._mission_handler.start_mission()
                self._mission_running = True
                self.missionLog.emit("Mission wird gestartet...")
            except Exception as e:
                self.missionError.emit(f"Fehler beim Starten der Mission: {str(e)}")
    
    @Slot()
    def pauseMission(self):
        """Pausiert die Mission"""
        if not DRONEKIT_AVAILABLE or not MISSION_HANDLER_AVAILABLE:
            self.missionError.emit("DroneKit oder Mission Handler nicht verfügbar")
            return
            
        if self._mission_handler:
            try:
                self._mission_handler.pause_mission()
                self.missionLog.emit("Mission wird pausiert...")
            except Exception as e:
                self.missionError.emit(f"Fehler beim Pausieren der Mission: {str(e)}")
    
    @Slot()
    def resumeMission(self):
        """Setzt die Mission fort"""
        if not DRONEKIT_AVAILABLE or not MISSION_HANDLER_AVAILABLE:
            self.missionError.emit("DroneKit oder Mission Handler nicht verfügbar")
            return
            
        if self._mission_handler:
            try:
                self._mission_handler.resume_mission()
                self.missionLog.emit("Mission wird fortgesetzt...")
            except Exception as e:
                self.missionError.emit(f"Fehler beim Fortsetzen der Mission: {str(e)}")
    
    @Slot()
    def stopMission(self):
        """Stoppt die Mission"""
        if not DRONEKIT_AVAILABLE or not MISSION_HANDLER_AVAILABLE:
            self.missionError.emit("DroneKit oder Mission Handler nicht verfügbar")
            return
            
        if self._mission_handler:
            try:
                self._mission_handler.stop_mission()
                self._mission_running = False
                self.missionLog.emit("Mission wird gestoppt...")
            except Exception as e:
                self.missionError.emit(f"Fehler beim Stoppen der Mission: {str(e)}")
    
    @Slot(float, float)
    def centerOnCoordinates(self, lat, lon):
        """Zentriert die Karte auf die angegebenen Koordinaten"""
        # Dies ist eine UI-Funktion, die an die FlightView weitergeleitet wird
        self.missionLog.emit(f"Karte zentriert auf: {lat}, {lon}")
    
    @Slot()
    def centerOnDrone(self):
        """Zentriert die Karte auf die Drohnenposition"""
        # Dies ist eine UI-Funktion, die an die FlightView weitergeleitet wird
        self.centerOnCoordinates(self._drone_lat, self._drone_lon)
    
    @Slot(float, float, float)
    def addWaypoint(self, lat, lon, alt):
        """
        Fügt einen Wegpunkt zur Mission hinzu
        
        Args:
            lat: Breitengrad
            lon: Längengrad  
            alt: Höhe in Metern
        """
        print(f"[MISSION] addWaypoint called: {lat}, {lon}, {alt}")
        
        # Wegpunkt zur lokalen Liste hinzufügen
        waypoint = {
            'lat': lat,
            'lon': lon,
            'alt': alt,
            'command': 16,  # MAV_CMD_NAV_WAYPOINT
            'frame': 0,     # MAV_FRAME_GLOBAL
            'autocontinue': 1
        }
        
        self._waypoints.append(waypoint)
        self._total_waypoints = len(self._waypoints)
        
        print(f"[MISSION] Waypoint added. Total waypoints: {self._total_waypoints}")
        print(f"[MISSION] Aktuelle Waypoints: {self._waypoints}")
        
        # Mission Handler benachrichtigen, falls verfügbar
        if self._mission_handler:
            try:
                self._mission_handler.add_waypoint(waypoint)
                print(f"[MISSION] Waypoint sent to mission handler")
            except Exception as e:
                print(f"[MISSION] Error sending waypoint to mission handler: {e}")
        
        # Signal für QML senden
        self.missionLog.emit(f"Wegpunkt hinzugefügt: {lat:.6f}, {lon:.6f}, {alt}m")
        print("[DEBUG] Sende waypointListChanged.emit() nach addWaypoint")
        self.waypointListChanged.emit()  # <-- NEU: QML benachrichtigen
        
        return True
    
    @Slot(float, float, float)
    def addWaypointToBackend(self, lat, lon, alt):
        """
        Fügt einen Wegpunkt über verschiedene Backends hinzu (für MAVLink2Tab)
        
        Args:
            lat: Breitengrad
            lon: Längengrad  
            alt: Höhe in Metern
        """
        print(f"[MISSION] addWaypointToBackend called: {lat}, {lon}, {alt}")
        
        # Standard addWaypoint aufrufen
        result = self.addWaypoint(lat, lon, alt)
        
        print(f"[MISSION] Nach addWaypointToBackend: Aktuelle Waypoints: {self._waypoints}")
        print("[DEBUG] Sende waypointListChanged.emit() nach addWaypointToBackend (zur Sicherheit)")
        self.waypointListChanged.emit()  # Doppelt zur Sicherheit
        
        # Zusätzlich: Über SerialConnector senden, falls verfügbar
        if self._serialConnector and hasattr(self._serialConnector, 'mavlink_connector'):
            try:
                # MAVLink-Nachricht senden
                if hasattr(self._serialConnector.mavlink_connector, 'connection'):
                    connection = self._serialConnector.mavlink_connector.connection
                    if connection:
                        # MAVLink waypoint message senden
                        from pymavlink import mavutil
                        connection.mav.mission_item_send(
                            connection.target_system,
                            connection.target_component,
                            len(self._waypoints) - 1,  # Index
                            0,  # Frame
                            16,  # MAV_CMD_NAV_WAYPOINT
                            0, 0,  # Current, autocontinue
                            0, 0, 0, 0,  # Params 1-4
                            lat, lon, alt  # Params 5-7
                        )
                        print(f"[MISSION] MAVLink waypoint message sent")
            except Exception as e:
                print(f"[MISSION] Error sending MAVLink waypoint: {e}")
        
        return result
    
    # --- Erweiterte Mission Planning Funktionen ---
    
    @Slot(float, float, float)
    def setHomePosition(self, lat, lon, alt):
        """Setzt die Home-Position"""
        self._home_lat = lat
        self._home_lon = lon
        self._home_alt = alt
        self.missionLog.emit(f"Home-Position gesetzt: {lat:.6f}, {lon:.6f}, {alt}m")
        self.waypointListChanged.emit()
        print(f"[MISSION] Home-Position gesetzt: {lat}, {lon}, {alt}")
    
    @Slot(float, float, float)
    def setTargetPosition(self, lat, lon, alt):
        """Setzt die Ziel-Position"""
        self._target_lat = lat
        self._target_lon = lon
        self._target_alt = alt
        self.missionLog.emit(f"Ziel-Position gesetzt: {lat:.6f}, {lon:.6f}, {alt}m")
        self.waypointListChanged.emit()
        print(f"[MISSION] Ziel-Position gesetzt: {lat}, {lon}, {alt}")
    
    @Slot()
    def setCurrentPositionAsHome(self):
        """Setzt die aktuelle Drohnenposition als Home"""
        self.setHomePosition(self._drone_lat, self._drone_lon, self._drone_alt)
    
    @Slot()
    def generateRoute(self):
        """Generiert automatisch eine Route zwischen Home und Ziel"""
        if len(self._waypoints) == 0:
            # Einfache Route: Home -> Ziel
            mid_lat = (self._home_lat + self._target_lat) / 2
            mid_lon = (self._home_lon + self._target_lon) / 2
            mid_alt = (self._home_alt + self._target_alt) / 2
            
            # Wegpunkt in der Mitte hinzufügen
            self.addWaypoint(mid_lat, mid_lon, mid_alt)
            self.missionLog.emit("Automatische Route generiert: Home -> Wegpunkt -> Ziel")
        else:
            self.missionLog.emit("Route bereits vorhanden - keine automatische Generierung")
    
    @Slot(int, float, float, float)
    def updateWaypointPosition(self, index, lat, lon, alt):
        """Aktualisiert die Position eines bestehenden Wegpunkts"""
        if 0 <= index < len(self._waypoints):
            self._waypoints[index]['lat'] = lat
            self._waypoints[index]['lon'] = lon
            self._waypoints[index]['alt'] = alt
            self.missionLog.emit(f"Wegpunkt {index+1} aktualisiert: {lat:.6f}, {lon:.6f}, {alt}m")
            self.waypointListChanged.emit()
            print(f"[MISSION] Wegpunkt {index} aktualisiert: {lat}, {lon}, {alt}")
        else:
            self.missionError.emit(f"Ungültiger Wegpunkt-Index: {index}")
    
    @Slot(int)
    def removeWaypoint(self, index):
        """Entfernt einen Wegpunkt"""
        if 0 <= index < len(self._waypoints):
            removed = self._waypoints.pop(index)
            self._total_waypoints = len(self._waypoints)
            self.missionLog.emit(f"Wegpunkt {index+1} entfernt")
            self.waypointListChanged.emit()
            print(f"[MISSION] Wegpunkt {index} entfernt: {removed}")
        else:
            self.missionError.emit(f"Ungültiger Wegpunkt-Index: {index}")
    
    @Slot()
    def clearWaypoints(self):
        """Löscht alle Wegpunkte"""
        if not DRONEKIT_AVAILABLE or not MISSION_HANDLER_AVAILABLE:
            self.missionError.emit("DroneKit oder Mission Handler nicht verfügbar")
            return
            
        if self._mission_handler:
            try:
                self._mission_handler.clear_mission()
                self._waypoints = []
                self._total_waypoints = 0
                self.missionLog.emit("Alle Wegpunkte gelöscht")
                self.waypointListChanged.emit()  # <-- NEU: QML benachrichtigen
            except Exception as e:
                self.missionError.emit(f"Fehler beim Löschen der Wegpunkte: {str(e)}")
    
    @Slot(float, float, float, float, int)
    def createCircleMission(self, center_lat, center_lon, altitude, radius, points=8):
        """Erstellt eine Kreismission"""
        if not DRONEKIT_AVAILABLE or not MISSION_HANDLER_AVAILABLE:
            self.missionError.emit("DroneKit oder Mission Handler nicht verfügbar")
            return []
            
        if self._mission_handler:
            try:
                result_future = self._mission_handler.create_circle_mission(
                    center_lat, center_lon, altitude, radius, points
                )
                self.missionLog.emit(f"Kreismission erstellt mit {points} Punkten")
                return result_future  # Gibt Future zurück
            except Exception as e:
                self.missionError.emit(f"Fehler beim Erstellen der Kreismission: {str(e)}")
                return []
    
    @Slot(float, float, float, float, int, int)
    def createSurveyMission(self, center_lat, center_lon, altitude, spacing, rows, cols):
        """Erstellt eine Survey-Mission (Raster)"""
        if not DRONEKIT_AVAILABLE or not MISSION_HANDLER_AVAILABLE:
            self.missionError.emit("DroneKit oder Mission Handler nicht verfügbar")
            return []
            
        if self._mission_handler:
            try:
                result_future = self._mission_handler.create_survey_mission(
                    center_lat, center_lon, altitude, spacing, rows, cols
                )
                self.missionLog.emit(f"Survey-Mission erstellt mit {rows}x{cols} Punkten")
                return result_future  # Gibt Future zurück
            except Exception as e:
                self.missionError.emit(f"Fehler beim Erstellen der Survey-Mission: {str(e)}")
                return []
