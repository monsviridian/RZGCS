import pytest
import time
from backend.simulated_drone import SimulatedDrone

@pytest.fixture
def drone():
    """Fixture für die SimulatedDrone."""
    drone = SimulatedDrone(port='udpin:localhost:14550')
    drone.connect()
    drone.start_simulation()
    yield drone
    drone.stop_simulation()
    drone.close()

def test_drone_initialization(drone):
    """Test, dass die Drone korrekt initialisiert wird."""
    assert drone.state.lat == 0.0
    assert drone.state.lon == 0.0
    assert drone.state.alt == 0.0
    assert drone.state.battery_remaining == 100.0
    assert not drone.state.armed

def test_drone_movement(drone):
    """Test, dass die Drone sich korrekt bewegt."""
    # Setze Zielposition
    target_lat = 51.1657
    target_lon = 10.4515
    target_alt = 100.0
    
    drone.set_target_position(target_lat, target_lon, target_alt)
    
    # Warte kurz, damit sich die Drone bewegen kann
    time.sleep(2)
    
    # Überprüfe, ob sich die Position geändert hat
    assert drone.state.lat != 0.0
    assert drone.state.lon != 0.0
    assert drone.state.alt != 0.0

def test_battery_drain(drone):
    """Test, dass der Batteriestand realistisch abnimmt."""
    initial_battery = drone.state.battery_remaining
    
    # Setze Zielposition und warte
    drone.set_target_position(51.1657, 10.4515, 100.0)
    time.sleep(2)
    
    # Überprüfe, ob der Batteriestand abgenommen hat
    assert drone.state.battery_remaining < initial_battery
    assert drone.state.voltage < 12.0
    assert drone.state.current > 0.0

def test_flight_modes(drone):
    """Test, dass die Flugmodi korrekt funktionieren."""
    # Teste verschiedene Flugmodi
    modes = ["STABILIZE", "ALTHOLD", "LOITER", "RTL"]
    for mode in modes:
        drone.set_mode(mode)
        assert drone.state.mode == mode

def test_arming(drone):
    """Test, dass das Arming/Disarming korrekt funktioniert."""
    assert not drone.state.armed
    
    drone.arm()
    assert drone.state.armed
    
    drone.disarm()
    assert not drone.state.armed

def test_max_altitude(drone):
    """Test, dass die maximale Höhe eingehalten wird."""
    # Versuche, über die maximale Höhe zu fliegen
    drone.set_target_position(51.1657, 10.4515, 200.0)  # Höher als max_altitude
    time.sleep(1)
    
    # Überprüfe, ob die Höhe auf max_altitude begrenzt wurde
    assert drone.state.alt <= drone.max_altitude

def test_send_heartbeat(drone):
    """Test, dass der Heartbeat korrekt gesendet wird."""
    drone.send_heartbeat()
    # Hier könnten weitere Assertions hinzugefügt werden, um zu überprüfen, ob der Heartbeat empfangen wurde.

def test_send_global_position_int(drone):
    """Test, dass die globale Position korrekt gesendet wird."""
    # Korrekte Werte für die globale Position
    drone.send_global_position_int(510000000, 10000000, 1000)

def test_send_attitude(drone):
    """Test, dass die Attitude korrekt gesendet wird."""
    # Korrekte Werte für die Attitude
    drone.send_attitude(0.1, 0.2, 0.3)

def test_send_sys_status(drone):
    """Test, dass der Systemstatus korrekt gesendet wird."""
    # Korrekte Werte für den Systemstatus
    drone.send_sys_status(12000, 100, 80)

def test_send_vfr_hud(drone):
    """Test, dass die VFR HUD-Daten korrekt gesendet werden."""
    drone.send_vfr_hud(100, 10, 12, 90, 50, 1)
    # Hier könnten weitere Assertions hinzugefügt werden, um zu überprüfen, ob die VFR HUD-Daten empfangen wurden.

def test_send_statustext(drone):
    """Test, dass der Statustext korrekt gesendet wird."""
    drone.send_statustext(3, "Test status")
    # Hier könnten weitere Assertions hinzugefügt werden, um zu überprüfen, ob der Statustext empfangen wurde. 