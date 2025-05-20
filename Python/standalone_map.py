"""
Eigenständige 3D-Karten-Anwendung für RZGCS
"""

import os
import sys
import math
from PySide6.QtCore import QUrl, QTimer
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PySide6.QtWebEngineWidgets import QWebEngineView

class MapWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Fenster konfigurieren
        self.setWindowTitle("RZGCS 3D-Karte")
        self.resize(1024, 768)
        
        # Zentrales Widget erstellen
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout erstellen
        layout = QVBoxLayout(central_widget)
        
        # WebEngine-View erstellen
        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view)
        
        # HTML-Dateipfad ermitteln
        script_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(script_dir)
        html_path = os.path.join(parent_dir, "RZGCSContent", "cesium", "flight_map_local.html")
        print(f"Versuche, Karte zu laden: {html_path}")
        
        # Falls die Datei nicht existiert, erstellen wir eine einfache Version
        if not os.path.exists(html_path):
            print(f"HTML-Datei nicht gefunden: {html_path}")
            print("Erstelle einfache Test-HTML...")
            html_path = os.path.join(script_dir, "simple_map.html")
            with open(html_path, "w") as f:
                f.write("""
<!DOCTYPE html>
<html>
<head>
    <title>RZGCS Simple Map</title>
    <style>
        body { margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #111; color: white; }
        #mapContainer { width: 100%; height: 100vh; position: relative; background-color: #003366; }
        #drone { position: absolute; width: 30px; height: 30px; background-color: red; border-radius: 50%; 
                 border: 3px solid white; transform: translate(-50%, -50%); }
        .coordinates { position: absolute; bottom: 10px; left: 10px; background: rgba(0,0,0,0.7); padding: 10px; }
    </style>
</head>
<body>
    <div id="mapContainer">
        <div id="drone"></div>
        <div class="coordinates">
            Lat: <span id="lat">0.0</span> | 
            Lon: <span id="lon">0.0</span> | 
            Alt: <span id="alt">0.0</span>m
        </div>
    </div>

    <script>
        // Drone position
        let dronePosition = { lat: 51.5056, lon: 7.4524, alt: 100 };
        const drone = document.getElementById('drone');
        
        // Map dimensions for projection
        const mapWidth = window.innerWidth;
        const mapHeight = window.innerHeight;
        
        // Initial center coordinates (Dortmund)
        const centerLat = 51.5056;
        const centerLon = 7.4524;
        
        // Scale factor for converting geo coordinates to pixels
        const scale = 10000;
        
        function updateDronePosition(lat, lon, alt, speed, battery) {
            dronePosition.lat = lat;
            dronePosition.lon = lon;
            dronePosition.alt = alt;
            
            // Update displayed values
            document.getElementById('lat').textContent = lat.toFixed(6);
            document.getElementById('lon').textContent = lon.toFixed(6);
            document.getElementById('alt').textContent = alt.toFixed(1);
            
            // Convert geo to pixel coordinates (simple mercator-like projection)
            const x = mapWidth/2 + (lon - centerLon) * scale;
            const y = mapHeight/2 - (lat - centerLat) * scale;
            
            // Position the drone marker
            drone.style.left = x + 'px';
            drone.style.top = y + 'px';
        }
        
        // Initial positioning
        updateDronePosition(dronePosition.lat, dronePosition.lon, dronePosition.alt, 0, 100);
        
        // Function to receive messages from Qt
        window.receiveFromQt = function(message) {
            try {
                const data = JSON.parse(message);
                if (data.type === 'position') {
                    updateDronePosition(data.lat, data.lon, data.alt, data.speed, data.battery);
                }
            } catch (e) {
                console.error("Error processing message:", e);
            }
        };

        // Simulate movement for testing
        let angle = 0;
        setInterval(() => {
            angle += 2;
            if (angle > 360) angle = 0;
            
            // Circle pattern
            const radius = 0.005;
            const newLat = centerLat + radius * Math.sin(angle * Math.PI / 180);
            const newLon = centerLon + radius * Math.cos(angle * Math.PI / 180);
            const newAlt = 100 + 50 * Math.sin(angle * Math.PI / 180);
            
            updateDronePosition(newLat, newLon, newAlt, 10, 85);
        }, 200);
    </script>
</body>
</html>
                """)
        
        # Datei als URL laden
        file_url = QUrl.fromLocalFile(os.path.abspath(html_path))
        print(f"Lade URL: {file_url.toString()}")
        self.web_view.load(file_url)
        
        # Simulate drone for testing
        self.timer = QTimer(self)
        self.timer.setInterval(500)
        self.timer.timeout.connect(self.simulate_drone)
        self.timer.start()
        
        self.sim_angle = 0
        
    def simulate_drone(self):
        """Simuliert Drohnenbewegung durch JavaScript-Aufruf"""
        # Kreisförmiger Pfad
        self.sim_angle = (self.sim_angle + 5) % 360
        radius = 0.001
        center_lat = 51.5056
        center_lon = 7.4524
        
        lat = center_lat + radius * math.sin(self.sim_angle * math.pi / 180)
        lon = center_lon + radius * math.cos(self.sim_angle * math.pi / 180)
        alt = 100 + 50 * math.sin(self.sim_angle * math.pi / 180)
        speed = 10 + 5 * math.sin(self.sim_angle * math.pi / 20)
        battery = 100 - self.sim_angle / 10
        
        # Position über JavaScript aktualisieren
        position_json = f'{{"type":"position","lat":{lat},"lon":{lon},"alt":{alt},"speed":{speed},"battery":{battery}}}'
        js_code = f"window.receiveFromQt('{position_json}');"
        self.web_view.page().runJavaScript(js_code)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Aktiviere das WebEngine-Debugging (hilft bei der Fehlerbehebung)
    os.environ["QTWEBENGINE_REMOTE_DEBUGGING"] = "9222"
    
    window = MapWindow()
    window.show()
    
    sys.exit(app.exec())
