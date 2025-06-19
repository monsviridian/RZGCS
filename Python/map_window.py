"""
Eigenständiges Kartenfenster für RZGCS
"""

import os
import sys
import json
from PySide6.QtCore import QObject, Signal, Slot, QUrl, Qt, QTimer
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEnginePage

class DroneMapWindow(QMainWindow):
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
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        local_html_path = os.path.join(base_dir, 'RZGCSContent', 'cesium', 'flight_map_local.html')
        
        # Lade HTML
        abs_path = os.path.abspath(local_html_path)
        url = QUrl.fromLocalFile(abs_path)
        print(f"Lade Karte: {abs_path}")
        self.web_view.load(url)
        
        # Signale verbinden
        self.web_view.loadFinished.connect(self._on_load_finished)
        
        # Timer für Simulationsupdates
        self.sim_timer = QTimer(self)
        self.sim_timer.setInterval(200)  # 200ms = 5 Updates pro Sekunde
        self.sim_timer.timeout.connect(self._simulate_drone_movement)
        
        # Drohnen-Simulationsdaten
        self.center_lat = 51.5056
        self.center_lon = 7.4524
        self.sim_angle = 0
        self.altitude = 100
    
    def _on_load_finished(self, ok):
        if ok:
            print("Karte erfolgreich geladen!")
            # Starte Simulation
            self.sim_timer.start()
        else:
            print("Fehler beim Laden der Karte")
    
    def _simulate_drone_movement(self):
        """Simuliert die Drohnenbewegung"""
        # Kreisförmiger Pfad
        radius = 0.0008  # ca. 80m
        angle_rad = self.sim_angle * (3.14159 / 180)
        
        # Neue Position berechnen
        lat = self.center_lat + radius * math.sin(angle_rad)
        lon = self.center_lon + radius * math.cos(angle_rad)
        alt = 100 + 20 * math.sin(self.sim_angle / 10)
        speed = 10 + 5 * math.sin(self.sim_angle / 20)
        battery = 100 - (self.sim_angle / 3600)
        
        # Position in JavaScript aktualisieren
        js_code = f"""
        if (typeof updateDronePosition === 'function') {{
            updateDronePosition({lat}, {lon}, {alt}, {speed}, {battery});
        }}
        """
        self.web_view.page().runJavaScript(js_code)
        
        # Winkel erhöhen
        self.sim_angle = (self.sim_angle + 1) % 360
    
    def update_drone_position(self, lat, lon, alt, speed, battery):
        """Aktualisiert die Drohnenposition aus externen Daten"""
        js_code = f"""
        if (typeof updateDronePosition === 'function') {{
            updateDronePosition({lat}, {lon}, {alt}, {speed}, {battery});
        }}
        """
        self.web_view.page().runJavaScript(js_code)

if __name__ == "__main__":
    # Wenn direkt ausgeführt, starte eigenständige Anwendung
    import math
    app = QApplication(sys.argv)
    window = DroneMapWindow()
    window.show()
    sys.exit(app.exec())
