from backend.simulated_drone import SimulatedDrone
import time

def main():
    # Drone initialisieren
    print("Initialisiere Drone...")
    drone = SimulatedDrone(port='udpin:localhost:14550')
    drone.connect()
    
    # Simulation starten
    print("Starte Simulation...")
    drone.start_simulation()
    
    # Drone armen
    print("Arme Drone...")
    drone.arm()
    
    # Flugmodus setzen
    print("Setze Flugmodus auf GUIDED...")
    drone.set_mode("GUIDED")
    
    # Startposition setzen (Beispielkoordinaten)
    start_lat = 51.1657
    start_lon = 10.4515
    start_alt = 10.0
    
    print(f"Fliege zu Startposition: {start_lat}, {start_lon}, {start_alt}m")
    drone.set_target_position(start_lat, start_lon, start_alt)
    
    # Warten bis die Drone die Startposition erreicht hat
    time.sleep(5)
    
    # Höher fliegen
    print("Steige auf 50m Höhe...")
    drone.set_target_position(start_lat, start_lon, 50.0)
    time.sleep(5)
    
    # Einige Flugmanöver ausführen
    print("Führe Flugmanöver aus...")
    
    # Nach Norden fliegen
    print("Fliege nach Norden...")
    drone.set_target_position(start_lat + 0.001, start_lon, 50.0)
    time.sleep(5)
    
    # Nach Osten fliegen
    print("Fliege nach Osten...")
    drone.set_target_position(start_lat + 0.001, start_lon + 0.001, 50.0)
    time.sleep(5)
    
    # Zurück zum Startpunkt
    print("Fliege zurück zum Startpunkt...")
    drone.set_target_position(start_lat, start_lon, 50.0)
    time.sleep(5)
    
    # Landen
    print("Lande...")
    drone.set_target_position(start_lat, start_lon, 0.0)
    time.sleep(5)
    
    # Drone disarmen
    print("Disarme Drone...")
    drone.disarm()
    
    # Simulation stoppen
    print("Stoppe Simulation...")
    drone.stop_simulation()
    
    # Verbindung schließen
    print("Schließe Verbindung...")
    drone.close()
    
    print("Drone erfolgreich gelandet!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgramm durch Benutzer beendet.")
    except Exception as e:
        print(f"Fehler: {e}") 