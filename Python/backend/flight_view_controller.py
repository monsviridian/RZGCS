"""
FlightViewController - Controller für die 3D-Flight-Ansicht mit Cesium
Verbindet das QML-UI mit der Cesium-Kartenansicht und dem Backend
"""

import os
import sys
import subprocess
import math
from PySide6.QtCore import QObject, Signal, Slot, Property, QTimer
from PySide6.QtQml import QQmlApplicationEngine, QQmlComponent, QQmlContext
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl

from .flight_map_bridge import FlightMapView, FlightMapBridge

# Eigenständiges Kartenfenster
class MapWindow(QMainWindow):
    """Eigenständiges Fenster für die 3D-Karte"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("RZGCS - 3D Drohnenkarte")
        self.setGeometry(100, 100, 800, 600)
        
        # Zentrales Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # WebEngine-View
        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view)
        
        # HTML-Pfad bestimmen
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        local_html_path = os.path.join(base_dir, 'RZGCSContent', 'cesium', 'flight_map_local.html')
        
        # Lade HTML
        abs_path = os.path.abspath(local_html_path)
        url = QUrl.fromLocalFile(abs_path)
        print(f"Lade Karte: {abs_path}")
        self.web_view.load(url)
        
        # Signale verbinden
        self.web_view.loadFinished.connect(self._on_load_finished)
        
        # Simulationsdaten
        self.center_lat = 51.5056
        self.center_lon = 7.4524
        self.sim_angle = 0
        self.altitude = 100
    
    def _on_load_finished(self, ok):
        if ok:
            print("Karte erfolgreich geladen!")
        else:
            print("Fehler beim Laden der Karte")
    
    def update_drone_position(self, lat, lon, alt, speed, battery):
        """Aktualisiert die Drohnenposition"""
        js_code = f"""
        if (typeof updateDronePosition === 'function') {{
            updateDronePosition({lat}, {lon}, {alt}, {speed}, {battery});
        }}
        """
        self.web_view.page().runJavaScript(js_code)


class FlightViewController(QObject):
    """Controller für die Flight-View mit Cesium 3D-Karte."""
    
    # Signale, die an QML gesendet werden
    dronePositionChanged = Signal()
    
    # Signal für die Kartenumschaltung
    mapTypeChanged = Signal(int)  # 0 = 2D, 1 = 3D
    
    def __init__(self, engine, parent=None):
        super().__init__(parent)
        self.engine = engine
        self.map_view = None
        self.map_bridge = None
        self.map_window = None
        
        # Drohnenstatus
        self._drone_lat = 51.5056  # Standardwerte Dortmund
        self._drone_lon = 7.4524
        self._drone_alt = 100.0
        self._drone_speed = 0.0
        self._drone_battery = 100.0
        
        # Karten-Modus (0 = 2D, 1 = 3D)
        self._map_type = 0
        
        # Timer für Simulationszwecke (später entfernen)
        self.sim_timer = QTimer(self)
        self.sim_timer.setInterval(1000)  # 1 Sekunde
        self.sim_timer.timeout.connect(self.simulate_drone_movement)
        
        # Simulierte Wegpunkte für Test (später entfernen)
        self.sim_points = []
        self.sim_index = 0
        
        # Simulierten Flugpfad erstellen
        self.create_sim_flight_path()
    
    def initialize(self, root_item):
        """Initialisiert die Flight-View und verbindet sie mit dem QML-UI."""
        try:
            # QML-Kontext aktualisieren - suche nach FlightView
            try:
                # Versuche den übergeordneten FlightView zu finden
                flight_view = root_item.findChild(QObject, "flightView")
                if flight_view:
                    print("[INFO] FlightView gefunden")
                    
                    # Signal für Kartentyp-Änderung verbinden
                    if hasattr(flight_view, "mapTypeChanged"):
                        flight_view.mapTypeChanged.connect(self.on_map_type_changed)
                        print("[INFO] Map-Type-Signal verbunden")
                    
                    # Signal zum Öffnen der externen 3D-Karte verbinden
                    if hasattr(flight_view, "openExternalMap"):
                        flight_view.openExternalMap.connect(self.open_external_map)
                        print("[INFO] Open-External-Map-Signal verbunden")
            except Exception as e:
                print(f"[WARNUNG] Fehler beim Suchen von flightView: {str(e)}")
            
            # Simulation starten
            self.sim_timer.start()
            
            print("[INFO] FlightViewController erfolgreich initialisiert")
            return None
        except Exception as e:
            print(f"[FEHLER] Bei der Initialisierung des FlightViewController: {str(e)}")
            return None
    
    def create_sim_flight_path(self):
        """Erstellt einen simulierten Flugpfad für Testzwecke."""
        # Rechteckiger Pfad um den Startpunkt
        base_lat = self._drone_lat
        base_lon = self._drone_lon
        step = 0.001  # ~100m
        
        # Quadrat fliegen
        for i in range(20):
            self.sim_points.append((base_lat, base_lon + i * step, 100 + i * 5))
        
        for i in range(20):
            self.sim_points.append((base_lat + i * step, base_lon + 19 * step, 200))
        
        for i in range(20):
            self.sim_points.append((base_lat + 19 * step, base_lon + (19-i) * step, 200 - i * 5))
        
        for i in range(19):
            self.sim_points.append((base_lat + (19-i) * step, base_lon, 100))
    
    @Slot()
    def simulate_drone_movement(self):
        """Simuliert die Drohnenbewegung für Testzwecke."""
        if not self.sim_points:
            return
        
        # Nächsten Wegpunkt abrufen
        index = self.sim_index % len(self.sim_points)
        lat, lon, alt = self.sim_points[index]
        
        # Geschwindigkeit und Akku simulieren
        speed = 10.0 + (index % 5)
        battery = 100.0 - (index / len(self.sim_points) * 20.0)
        
        # Drohnenposition aktualisieren
        self.update_drone_position(lat, lon, alt, speed, battery)
        
        # Auch an die QML-Oberfläche senden für die 2D-Karte
        self.dronePositionChanged.emit()
        
        # Index inkrementieren
        self.sim_index += 1
        
        # Manuell die Karte nachführen lassen mit der Drohne
        if self.map_view and index % 10 == 0:  # Nur alle 10 Schritte anpassen
            self.center_on_drone()
    
    def update_drone_position(self, lat, lon, alt, speed=None, battery=None):
        """Aktualisiert die Drohnenposition und benachrichtigt die UI."""
        self._drone_lat = lat
        self._drone_lon = lon
        self._drone_alt = alt
        
        if speed is not None:
            self._drone_speed = speed
        
        if battery is not None:
            self._drone_battery = battery
        
        # Externe Karte aktualisieren, wenn sie offen ist
        if self.map_window is not None:
            try:
                self.map_window.update_drone_position(lat, lon, alt, self._drone_speed, self._drone_battery)
            except Exception as e:
                print(f"Fehler beim Aktualisieren der Kartenposition: {str(e)}")
        
        # QML benachrichtigen
        self.dronePositionChanged.emit()
    
    @Slot(float, float, float)
    def on_map_clicked(self, lat, lon, alt):
        """Verarbeitet Klicks auf die Karte."""
        print(f"Kartenklick bei: {lat}, {lon}, {alt}")
        # Hier könnten Wegpunkte gesetzt werden usw.
    
    @Slot(int)
    def on_map_type_changed(self, map_type):
        """Wird aufgerufen, wenn der Benutzer zwischen 2D und 3D wechselt."""
        print(f"Kartentyp geändert: {map_type}")
        self._map_type = map_type
        
        # Wenn auf 3D-Karte umgeschaltet wurde, öffne das separate Fenster
        if map_type == 1 and self.map_window is None:
            self._open_map_window()
    
    def _open_map_window(self):
        """Öffnet ein separates 3D-Kartenfenster"""
        try:
            # Erstelle das separate Kartenfenster
            self.map_window = MapWindow()
            self.map_window.show()
            print("3D-Kartenfenster wurde geöffnet")
        except Exception as e:
            print(f"Fehler beim Öffnen des 3D-Kartenfensters: {str(e)}")
    
    @Slot()
    def open_external_map(self):
        """Startet die externe 3D-Kartenanwendung"""
        print("\n\n[DEBUG] open_external_map() wurde aufgerufen!\n\n")
        try:
            # Pfad zum Script bestimmen
            current_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(current_dir)
            script_path = os.path.join(parent_dir, "standalone_map.py")
            
            print(f"[DEBUG] Script-Pfad: {script_path}")
            print(f"[DEBUG] Python-Interpreter: {sys.executable}")
            
            # Alternative: Direkter Start des Skripts mit einfachem Python-Call
            os.system(f'start cmd /k "{sys.executable}" "{script_path}"')
            print("[DEBUG] Externe 3D-Karte über os.system gestartet")
            
            # Als Backup auch via Popen versuchen
            try:
                subprocess.Popen([sys.executable, script_path], 
                                cwd=parent_dir, 
                                creationflags=subprocess.CREATE_NEW_CONSOLE)
                print("[DEBUG] Externe 3D-Karte auch über Popen gestartet")
            except Exception as sub_err:
                print(f"[DEBUG] Popen-Fehler: {str(sub_err)}")
            
            print("Externe 3D-Kartenanwendung wurde gestartet")
        except Exception as e:
            print(f"\n\n[FEHLER] Beim Starten der externen 3D-Karte: {str(e)}\n\n")
    
    @Slot()
    def center_on_drone(self):
        """Zentriert die Karte auf die aktuelle Drohnenposition."""
        if self.map_view:
            self.map_view.center_map(self._drone_lat, self._drone_lon, self._drone_alt)
    
    @Slot()
    def follow_drone(self):
        """Lässt die Kamera der Drohne folgen."""
        if self.map_view:
            self.map_view.follow_drone()
    
    @Slot(bool)
    def set_path_visible(self, visible):
        """Setzt die Sichtbarkeit des Pfades."""
        if self.map_view:
            self.map_view.set_path_visible(visible)
    
    @Slot()
    def clear_path(self):
        """Löscht den angezeigten Flugpfad."""
        if self.map_view:
            self.map_view.clear_path()
    
    # Properties für QML-Binding
    @Property(float, notify=dronePositionChanged)
    def droneLat(self):
        return self._drone_lat
    
    @Property(float, notify=dronePositionChanged)
    def droneLon(self):
        return self._drone_lon
    
    @Property(float, notify=dronePositionChanged)
    def droneAlt(self):
        return self._drone_alt
    
    @Property(float, notify=dronePositionChanged)
    def droneSpeed(self):
        return self._drone_speed
    
    @Property(float, notify=dronePositionChanged)
    def droneBattery(self):
        return self._drone_battery
