"""
Testprogramm für die vereinfachte lokale Kartenansicht
"""

import os
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtCore import QUrl, Qt, QObject, Signal, Slot

class WebConsole(QObject):
    """Handler für JavaScript-Konsole"""
    message_received = Signal(str)
    
    @Slot(str)
    def log(self, message):
        print(f"JS-Konsole: {message}")
        self.message_received.emit(message)

class CustomWebPage(QWebEnginePage):
    def javaScriptConsoleMessage(self, level, message, line, source):
        # JavaScript-Konsolenausgaben abfangen
        level_str = ["Info", "Warnung", "Fehler"][level] if level < 3 else "Unbekannt"
        print(f"JS [{level_str}] {message} (Zeile {line}) in {source}")

class MapTestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RZGCS - Karten-Test")
        self.setGeometry(100, 100, 1024, 768)
        
        # Zentrales Widget mit Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # WebEngine-View erstellen
        self.web_view = QWebEngineView()
        
        # Eigene WebPage mit Konsolenausgabe setzen
        self.web_page = CustomWebPage()
        self.web_view.setPage(self.web_page)
        
        layout.addWidget(self.web_view)
        
        # HTML-Pfad bestimmen - verwende die lokale Version
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        html_path = os.path.join(base_dir, 'RZGCSContent', 'cesium', 'flight_map_local.html')
        
        # Status-Callbacks
        self.web_view.loadStarted.connect(lambda: print("Laden gestartet..."))
        self.web_view.loadFinished.connect(self.on_load_finished)
        
        # URL auf Konsole ausgeben
        abs_path = os.path.abspath(html_path)
        self.url = QUrl.fromLocalFile(abs_path)
        print(f"Lade HTML-Datei: {abs_path}")
        print(f"URL: {self.url.toString()}")
        
        # HTML-Datei laden
        self.web_view.load(self.url)
    
    def on_load_finished(self, ok):
        status = "Erfolgreich" if ok else "Fehlgeschlagen"
        print(f"Laden beendet: {status}")
        if ok:
            print("Karte wurde erfolgreich geladen!")
            
            # Teste die Kommunikation mit JavaScript
            js_code = """
            console.log('Python sendet Nachricht an JavaScript');
            if (typeof receiveFromQt === 'function') {
                receiveFromQt('{"type":"position","lat":51.5065,"lon":7.4534,"alt":120,"speed":15,"battery":90}');
                console.log('Positionsdaten gesendet');
            } else {
                console.log('FEHLER: receiveFromQt-Funktion nicht gefunden');
            }
            """
            self.web_view.page().runJavaScript(js_code)
        else:
            print("FEHLER: Karte konnte nicht geladen werden.")
            # Status überprüfen und Fehler anzeigen
            self.web_view.page().runJavaScript(
                "document.documentElement.outerHTML",
                0,
                lambda result: print(f"HTML-Inhalt: {result[:500]}...")
            )

def main():
    app = QApplication(sys.argv)
    window = MapTestWindow()
    window.show()
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
