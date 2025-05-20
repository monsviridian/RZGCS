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

# Versuche WebEngine-Module zu importieren, biete Fallback wenn nicht verfügbar
try:
    from PySide6.QtWebChannel import QWebChannel
    from PySide6.QtWebEngineWidgets import QWebEngineView
    HAS_WEBENGINE = True
except ImportError:
    HAS_WEBENGINE = False
    print("[WARNUNG] QtWebEngine nicht verfügbar - 3D-Karte wird durch Platzhalter ersetzt")

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
    """Widget für die Darstellung der Cesium-3D-Karte."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Bridge für die Kommunikation
        self.bridge = FlightMapBridge(self)
        
        # HTML-Pfad bestimmen - verwende die lokale Version
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        # Wenn die lokale Version existiert, verwende diese, ansonsten die normale Version
        local_html_path = os.path.join(base_dir, 'RZGCSContent', 'cesium', 'flight_map_local.html')
        normal_html_path = os.path.join(base_dir, 'RZGCSContent', 'cesium', 'flight_map.html')
        
        if os.path.exists(local_html_path):
            html_path = local_html_path
            print(f"[INFO] Verwende lokale Kartenversion: {local_html_path}")
        else:
            html_path = normal_html_path
            print(f"[INFO] Verwende Standard-Kartenversion: {normal_html_path}")
        
        if HAS_WEBENGINE:
            try:
                # WebEngine-View erstellen
                self.webview = QWebEngineView(self)
                self.layout.addWidget(self.webview)
                
                # WebChannel für die Kommunikation zwischen QML/Python und JavaScript
                self.channel = QWebChannel()
                self.channel.registerObject("flightMap", self.bridge)
                self.webview.page().setWebChannel(self.channel)
                
                # JavaScript-Funktion definieren, um Nachrichten zu senden
                self.bridge.sendToJavaScript = self.send_to_javascript
                
                # Debugging ist in dieser Version nicht verfügbar
                # Alternativer Debug-Ansatz durch Logging
                print("[DEBUG] WebEngine wird initialisiert")
                
                # Ladefortschritt überwachen
                self.webview.loadStarted.connect(lambda: print("[DEBUG] WebEngine: Laden gestartet"))
                self.webview.loadFinished.connect(lambda ok: print(f"[DEBUG] WebEngine: Laden beendet: {'Erfolgreich' if ok else 'Fehlgeschlagen'}"))
                
                # HTML-Datei laden
                abs_path = os.path.abspath(html_path)
                url = QUrl.fromLocalFile(abs_path)
                print(f"[INFO] 3D-Karte wird geladen: {abs_path} (URL: {url.toString()})")
                self.webview.load(url)
            except Exception as e:
                print(f"[FEHLER] Beim Laden der 3D-Karte: {str(e)}")
                self._create_fallback_view()
        else:
            self._create_fallback_view()
    
    def _create_fallback_view(self):
        """Erstellt eine Fallback-Ansicht wenn WebEngine nicht verfügbar ist."""
        label = QLabel("3D-Karte nicht verfügbar\n\nStellen Sie sicher, dass PySide6 mit\nWebEngine-Unterstützung installiert ist.")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("background-color: #333333; color: #cccccc;")
        font = QFont()
        font.setPointSize(12)
        label.setFont(font)
        self.layout.addWidget(label)
    
    def send_to_javascript(self, message):
        """Sendet eine Nachricht an JavaScript."""
        if HAS_WEBENGINE and hasattr(self, 'webview'):
            try:
                js = f"window.receiveFromQt('{message}');"
                self.webview.page().runJavaScript(js)
            except Exception as e:
                print(f"[FEHLER] Beim Senden an JavaScript: {str(e)}")
    
    def update_drone_position(self, lat, lon, alt, speed=None, battery=None):
        """Aktualisiert die Drohnenposition."""
        try:
            if speed is not None and battery is not None:
                self.bridge.updateDroneState(lat, lon, alt, speed, battery)
            else:
                self.bridge.updateDronePosition(lat, lon, alt)
        except Exception as e:
            print(f"[FEHLER] Beim Aktualisieren der Drohnenposition: {str(e)}")
    
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
