#!/usr/bin/env python3
"""
PyMAVLink Connector - Einfache Alternative zu DroneKit
"""

import time
import threading
from PySide6.QtCore import QObject, Signal, QTimer
from pymavlink import mavutil

class MavlinkConnector(QObject):
    """Einfacher PyMAVLink-Connector"""
    
    # Signals
    connected = Signal()
    disconnected = Signal()
    connection_failed = Signal(str)  # error message
    gps_updated = Signal(float, float, float)  # lat, lon, alt
    attitude_updated = Signal(float, float, float)  # roll, pitch, yaw
    battery_updated = Signal(float)  # voltage
    status_updated = Signal(str)  # status message
    
    def __init__(self):
        super().__init__()
        self.connection = None
        self.is_connected = False
        self.connection_thread = None
        self.stop_event = threading.Event()
        
    def connect_to_vehicle(self, connection_string: str):
        """Verbindung zum Fahrzeug herstellen"""
        try:
            print(f"[MAVLINK] Verbinde zu: {connection_string}")
            
            # Verbindung herstellen
            self.connection = mavutil.mavlink_connection(connection_string)
            
            # Warten auf Heartbeat
            print("[MAVLINK] Warte auf Heartbeat...")
            self.connection.wait_heartbeat(timeout=10)
            print("[MAVLINK] Heartbeat empfangen!")
            
            self.is_connected = True
            self.connected.emit()
            self.status_updated.emit("Verbunden")
            
            # Telemetrie-Thread starten
            self.stop_event.clear()
            self.connection_thread = threading.Thread(target=self._telemetry_loop, daemon=True)
            self.connection_thread.start()
            
            return True
            
        except Exception as e:
            error_msg = f"Verbindung fehlgeschlagen: {str(e)}"
            print(f"[MAVLINK] {error_msg}")
            self.connection_failed.emit(error_msg)
            self.status_updated.emit("Verbindung fehlgeschlagen")
            return False
    
    def disconnect(self):
        """Verbindung trennen"""
        print("[MAVLINK] Trenne Verbindung...")
        self.stop_event.set()
        
        if self.connection:
            try:
                self.connection.close()
            except:
                pass
            finally:
                self.connection = None
        
        self.is_connected = False
        self.disconnected.emit()
        self.status_updated.emit("Getrennt")
    
    def _telemetry_loop(self):
        """Hauptschleife für Telemetrie-Empfang"""
        while not self.stop_event.is_set():
            try:
                # Nachrichten empfangen
                msg = self.connection.recv_match(blocking=True, timeout=1.0)
                
                if msg is None:
                    continue
                
                # GPS-Daten
                if msg.get_type() == 'GPS_RAW_INT':
                    lat = msg.lat / 1e7
                    lon = msg.lon / 1e7
                    alt = msg.alt / 1000.0
                    self.gps_updated.emit(lat, lon, alt)
                
                # Attitude-Daten
                elif msg.get_type() == 'ATTITUDE':
                    roll = msg.roll
                    pitch = msg.pitch
                    yaw = msg.yaw
                    self.attitude_updated.emit(roll, pitch, yaw)
                
                # Battery-Daten
                elif msg.get_type() == 'SYS_STATUS':
                    voltage = msg.voltage_battery / 1000.0  # mV to V
                    self.battery_updated.emit(voltage)
                
                # Heartbeat
                elif msg.get_type() == 'HEARTBEAT':
                    print(f"[MAVLINK] Heartbeat von System {msg.get_srcSystem()}")
                
            except Exception as e:
                print(f"[MAVLINK] Telemetrie-Fehler: {e}")
                if not self.stop_event.is_set():
                    self.connection_failed.emit(f"Telemetrie-Fehler: {str(e)}")
                break
        
        print("[MAVLINK] Telemetrie-Loop beendet")
    
    def send_command(self, command_id, params=None):
        """Befehl senden"""
        if not self.is_connected or not self.connection:
            return False
        
        try:
            if params is None:
                params = [0, 0, 0, 0, 0, 0, 0]
            
            self.connection.mav.command_long_send(
                self.connection.target_system,
                self.connection.target_component,
                command_id,
                0,  # confirmation
                *params
            )
            return True
        except Exception as e:
            print(f"[MAVLINK] Fehler beim Senden des Befehls: {e}")
            return False
    
    def get_connection_status(self):
        """Aktuellen Verbindungsstatus zurückgeben"""
        return {
            'connected': self.is_connected,
            'connection': str(self.connection) if self.connection else None
        }

# Test-Funktion
def test_mavlink_connection():
    """Teste PyMAVLink-Verbindung"""
    print("Teste PyMAVLink-Verbindung...")
    
    connector = MavlinkConnector()
    
    # Signal-Handler
    def on_connected():
        print("✓ Verbunden!")
    
    def on_gps(lat, lon, alt):
        print(f"GPS: {lat:.6f}, {lon:.6f}, {alt:.1f}m")
    
    def on_attitude(roll, pitch, yaw):
        print(f"Attitude: Roll={roll:.2f}°, Pitch={pitch:.2f}°, Yaw={yaw:.2f}°")
    
    def on_battery(voltage):
        print(f"Battery: {voltage:.2f}V")
    
    def on_error(error):
        print(f"✗ Fehler: {error}")
    
    # Signals verbinden
    connector.connected.connect(on_connected)
    connector.gps_updated.connect(on_gps)
    connector.attitude_updated.connect(on_attitude)
    connector.battery_updated.connect(on_battery)
    connector.connection_failed.connect(on_error)
    
    # Verbindung testen
    success = connector.connect_to_vehicle('127.0.0.1:5760')
    
    if success:
        # 10 Sekunden Telemetrie empfangen
        time.sleep(10)
        connector.disconnect()
    
    return success

if __name__ == "__main__":
    test_mavlink_connection() 