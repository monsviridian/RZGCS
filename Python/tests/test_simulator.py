"""
Einfaches Testprogramm für den Simulator-Konnektor.
Stellt eine Verbindung zum MAVLink-Simulator her und empfängt Daten.
"""

import sys
import time
from PySide6.QtCore import QCoreApplication
from backend.logger import Logger
from backend.simulator_connector import SimulatorConnector

def main():
    app = QCoreApplication(sys.argv)
    
    # Logger für Statusausgaben initialisieren
    logger = Logger()
    
    # Logging-Ausgabe manuell in die Konsole leiten
    def log_to_console(message):
        print(f"[LOG] {message}")
    logger.new_log.connect(log_to_console)
    
    # Simulator-Konnektor initialisieren
    simulator = SimulatorConnector(logger)
    
    # Verbindungsstatus-Callbacks
    def on_connected_changed(connected):
        print(f"Verbindungsstatus geändert: {'Verbunden' if connected else 'Getrennt'}")
        
    def on_heartbeat():
        print("Heartbeat empfangen!")
        
    def on_message(msg):
        print(f"Nachricht empfangen: {msg.get_type()}")
        
    def on_error(error_msg):
        print(f"FEHLER: {error_msg}")
    
    # Signale verbinden
    simulator.connectionStatusChanged.connect(on_connected_changed)
    simulator.heartbeatReceived.connect(on_heartbeat)
    simulator.messageReceived.connect(on_message)
    simulator.errorOccurred.connect(on_error)
    
    # Mit Simulator verbinden
    print("Verbinde mit Simulator...")
    if simulator.connect():
        print("Erfolgreiche Verbindung! Empfange Daten für 10 Sekunden...")
        
        # 10 Sekunden laufen lassen und dann beenden
        timer_id = app.startTimer(10000)
        
        def cleanup():
            print("Beende Verbindung...")
            simulator.disconnect()
            print("Programm wird beendet.")
            app.quit()
            
        app.timerEvent = lambda event: cleanup() if event.timerId() == timer_id else None
        
        return app.exec()
    else:
        print("Verbindung fehlgeschlagen!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
