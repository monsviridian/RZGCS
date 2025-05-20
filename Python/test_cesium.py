"""
Einfaches Testprogramm für die Cesium 3D-Karte
Dient zum Testen, ob die WebEngine-Integration grundsätzlich funktioniert
"""

import os
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl

class CesiumTestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cesium 3D-Karte Test")
        self.setGeometry(100, 100, 800, 600)
        
        # Zentrales Widget mit Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # WebEngine-View erstellen
        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view)
        
        # HTML-Pfad bestimmen
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        html_path = os.path.join(base_dir, 'RZGCSContent', 'cesium', 'flight_map.html')
        
        # Status-Callbacks
        self.web_view.loadStarted.connect(lambda: print("Laden gestartet..."))
        self.web_view.loadFinished.connect(lambda ok: print(f"Laden beendet: {'Erfolgreich' if ok else 'Fehlgeschlagen'}"))
        
        # URL auf Konsole ausgeben
        abs_path = os.path.abspath(html_path)
        url = QUrl.fromLocalFile(abs_path)
        print(f"Lade HTML-Datei: {abs_path}")
        print(f"URL: {url.toString()}")
        
        # HTML-Datei laden
        self.web_view.load(url)
        
        # Bei Ladefehlern Konsole aktivieren
        self.web_view.page().webChannel().registerObject("console", self)

def main():
    app = QApplication(sys.argv)
    window = CesiumTestWindow()
    window.show()
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
