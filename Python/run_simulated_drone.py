from backend.simulated_drone import SimulatedDrone
import time
import signal
import sys

class DroneService:
    def __init__(self):
        self.drone = None
        self.running = True
        
        # Signal handler für sauberes Beenden
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def signal_handler(self, signum, frame):
        """Behandelt Signale für sauberes Beenden."""
        print("\nBeende Drone-Service...")
        self.running = False

    def start(self):
        """Startet den Drone-Service."""
        try:
            print("Starte simulierte Drone...")
            self.drone = SimulatedDrone(port='udpin:localhost:14550')
            self.drone.connect()
            self.drone.start_simulation()
            
            # Setze initiale Position
            self.drone.set_target_position(51.1657, 10.4515, 0.0)
            
            print("Drone-Service läuft. Drücke Ctrl+C zum Beenden.")
            print("Verfügbare MAVLink-Nachrichten:")
            print("- HEARTBEAT")
            print("- GLOBAL_POSITION_INT")
            print("- ATTITUDE")
            print("- SYS_STATUS")
            print("- VFR_HUD")
            print("- STATUSTEXT")
            
            # Hauptschleife
            while self.running:
                time.sleep(0.1)
                
        except Exception as e:
            print(f"Fehler: {e}")
        finally:
            self.cleanup()

    def cleanup(self):
        """Räumt auf und beendet die Drone sauber."""
        if self.drone:
            print("Stoppe Simulation...")
            self.drone.stop_simulation()
            print("Schließe Verbindung...")
            self.drone.close()
            print("Drone-Service beendet.")

if __name__ == "__main__":
    service = DroneService()
    service.start() 