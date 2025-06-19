"""
FlightMapBridge - Brücke zwischen RZGCS und Cesium-3D-Karte
Ermöglicht die bidirektionale Kommunikation zwischen Python-Backend und Cesium JS
"""

import os
import json
import sys
from PySide6.QtCore import QObject, Signal, Slot, Property, QUrl, Qt
from PySide6.QtWidgets import QVBoxLayout, QWidget, QLabel
from PySide6.QtGui import QColor, QFont

# Importiere unsere einfache Kartenansicht
from .simple_map_view import SimpleMapView

# Flag für WebEngine setzen wir auf False, um unsere eigene Implementierung zu verwenden
HAS_WEBENGINE = False
print("[INFO] Verwende vereinfachte 2D-Kartenansicht anstelle von WebEngine")

class FlightMapBridge(QObject):
    """Brücke für die Kommunikation zwischen Python und JavaScript."""
    
    # Signale für Events vom JavaScript zurück zu Python
    mapClicked = Signal(float, float, float)  # lat, lon, alt
    waypointAdded = Signal(float, float, float)  # lat, lon, alt
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._logged_in = False
        self._current_lat = 52.5200  # Berlin als Standardwert
        self._current_lon = 13.4050
        self._current_alt = 100.0
        self._current_speed = 0.0
        self._current_battery = 100.0
        self._path_visible = True
    
    @Slot(str)
    def receiveMessage(self, message):
        """Empfängt Nachrichten vom JavaScript."""
        try:
            data = json.loads(message)
            
            if data["type"] == "mapClick":
                # Klickereignis auf der Karte
                self.mapClicked.emit(data["lat"], data["lon"], data["alt"])
            elif data["type"] == "waypointAdded":
                # Wegpunkt wurde hinzugefügt
                self.waypointAdded.emit(data["lat"], data["lon"], data["alt"])
        except Exception as e:
            print(f"Fehler beim Verarbeiten der Nachricht: {str(e)}")
    
    @Slot(float, float, float)
    def updateDronePosition(self, lat, lon, alt):
        """Aktualisiert die Drohnenposition auf der Karte."""
        self._current_lat = lat
        self._current_lon = lon
        self._current_alt = alt
        
        message = {
            "type": "position",
            "lat": lat,
            "lon": lon,
            "alt": alt,
            "speed": self._current_speed,
            "battery": self._current_battery
        }
        
        self.sendToJavaScript(json.dumps(message))
    
    @Slot(float, float, float, float, float)
    def updateDroneState(self, lat, lon, alt, speed, battery):
        """Aktualisiert alle Informationen der Drohne auf der Karte."""
        self._current_lat = lat
        self._current_lon = lon
        self._current_alt = alt
        self._current_speed = speed
        self._current_battery = battery
        
        message = {
            "type": "position",
            "lat": lat,
            "lon": lon,
            "alt": alt,
            "speed": speed,
            "battery": battery
        }
        
        self.sendToJavaScript(json.dumps(message))
    
    @Slot(float, float, float, float, float)
    def centerMap(self, lat, lon, alt, heading=0, pitch=-30):
        """Zentriert die Karte auf eine bestimmte Position."""
        message = {
            "type": "centerMap",
            "lat": lat,
            "lon": lon,
            "alt": alt,
            "heading": heading,
            "pitch": pitch
        }
        
        self.sendToJavaScript(json.dumps(message))
    
    @Slot()
    def clearPath(self):
        """Löscht den angezeigten Flugpfad."""
        message = {
            "type": "clearPath"
        }
        
        self.sendToJavaScript(json.dumps(message))
    
    @Slot()
    def followDrone(self):
        """Lässt die Kamera der Drohne folgen."""
        message = {
            "type": "followDrone"
        }
        
        self.sendToJavaScript(json.dumps(message))
    
    @Slot(bool)
    def setPathVisible(self, visible):
        """Setzt die Sichtbarkeit des Pfades."""
        self._path_visible = visible
        message = {
            "type": "setPathVisible",
            "visible": visible
        }
        
        self.sendToJavaScript(json.dumps(message))
    
    @Slot(str)
    def sendToJavaScript(self, message):
        """Sendet eine Nachricht an JavaScript (wird in QML aufgerufen)."""
        # Diese Methode wird von QML aufgerufen, um Nachrichten an JS zu senden
        pass
    
    # Properties für QML-Binding
    @Property(float)
    def currentLat(self):
        return self._current_lat
    
    @Property(float)
    def currentLon(self):
        return self._current_lon
    
    @Property(float)
    def currentAlt(self):
        return self._current_alt
    
    @Property(float)
    def currentSpeed(self):
        return self._current_speed
    
    @Property(float)
    def currentBattery(self):
        return self._current_battery
    
    @Property(bool)
    def pathVisible(self):
        return self._path_visible


class FlightMapView(QWidget):
    """Widget für die Darstellung der Flugkarte."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Bridge für die Kommunikation
        self.bridge = FlightMapBridge(self)
        
        print("[INFO] Initialisiere vereinfachte 2D-Kartenansicht...")
        
        # Verwende unsere garantiert funktionierende SimpleMapView
        try:
            # Erstelle die einfache Kartenansicht
            self.map_view = SimpleMapView(self)
            self.layout.addWidget(self.map_view)
            
            # Verbinde Signale und Slots
            self.map_view.positionClicked.connect(self.bridge.mapClicked)
            
            # Definiere die Funktion zum Senden von Daten an die Karte
            self.bridge.sendToJavaScript = self.send_to_map_view
            
            print("[INFO] 2D-Kartenansicht erfolgreich initialisiert")
        except Exception as e:
            print(f"[FEHLER] Beim Initialisieren der 2D-Karte: {str(e)}")
            self._create_fallback_view()
    
    def _create_fallback_view(self):
        """Erstellt eine Fallback-Ansicht wenn die Karte nicht initialisiert werden kann."""
        label = QLabel("Kartenansicht nicht verfügbar\n\nEs ist ein Fehler bei der Initialisierung\nder Karte aufgetreten.")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("background-color: #003366; color: white; font-size: 14pt;")
        self.layout.addWidget(label)
        print("Warnung: Kartenansicht konnte nicht initialisiert werden")
    
    def send_to_map_view(self, message):
        """Sendet eine Nachricht an die Kartenansicht."""
        if hasattr(self, 'map_view'):
            try:
                # JSON-Nachricht parsen und an die Karte weiterleiten
                data = json.loads(message)
                if data.get('type') == 'position':
                    # Drohnenposition aktualisieren
                    self.map_view.update_drone_position(
                        data.get('lat'), 
                        data.get('lon'), 
                        data.get('alt'),
                        data.get('heading'),
                        data.get('speed'),
                        data.get('battery')
                    )
            except Exception as e:
                print(f"[FEHLER] Beim Senden an MapView: {str(e)}")
        else:
            print("[WARNUNG] Kann keine Nachricht senden: MapView nicht verfügbar")
    
    def update_drone_position(self, lat, lon, alt, speed=None, battery=None, heading=None):
        """Aktualisiert die Drohnenposition."""
        data = {
            'type': 'position',
            'lat': lat,
            'lon': lon,
            'alt': alt
        }
        
        if speed is not None:
            data['speed'] = speed
        
        if battery is not None:
            data['battery'] = battery
            
        if heading is not None:
            data['heading'] = heading
        
        self.bridge.sendToJavaScript(json.dumps(data))
    
    def center_map(self, lat, lon, alt, heading=0, pitch=-30):
        """Zentriert die Karte auf eine bestimmte Position."""
        try:
            self.bridge.centerMap(lat, lon, alt, heading, pitch)
        except Exception as e:
            print(f"[FEHLER] Beim Zentrieren der Karte: {str(e)}")
    
    def clear_path(self):
        """Löscht den angezeigten Flugpfad."""
        try:
            self.bridge.clearPath()
        except Exception as e:
            print(f"[FEHLER] Beim Löschen des Pfades: {str(e)}")
    
    def follow_drone(self):
        """Lässt die Kamera der Drohne folgen."""
        try:
            self.bridge.followDrone()
        except Exception as e:
            print(f"[FEHLER] Beim Folgen der Drohne: {str(e)}")
    
    def set_path_visible(self, visible):
        """Setzt die Sichtbarkeit des Pfades."""
        try:
            self.bridge.setPathVisible(visible)
        except Exception as e:
            print(f"[FEHLER] Beim Ändern der Pfadsichtbarkeit: {str(e)}")
