from backend.mavlink_connector import MAVLinkConnector
import time
import asyncio
from PySide6.QtCore import QCoreApplication, QTimer
import sys
import qasync

class DroneController:
    def __init__(self):
        self.connector = None
        self.app = QCoreApplication(sys.argv)
        
    def on_gps_update(self, lat, lon):
        print(f"GPS Update: {lat:.6f}, {lon:.6f}")
        
    def on_attitude_update(self, roll, pitch, yaw):
        print(f"Attitude Update: Roll={roll:.1f}°, Pitch={pitch:.1f}°, Yaw={yaw:.1f}°")
        
    def on_sensor_update(self, sensor_name, value):
        print(f"Sensor Update: {sensor_name} = {value}")
        
    def on_connection_status(self, connected):
        print(f"Connection Status: {'Connected' if connected else 'Disconnected'}")
        
    def on_log_message(self, message):
        print(f"Log: {message}")
        
    async def connect_to_drone(self):
        # Erstelle MAVLink-Connector für die simulierte Drone
        self.connector = MAVLinkConnector('udpin:localhost:14550')
        
        # Verbinde Signale
        self.connector.gps_msg.connect(self.on_gps_update)
        self.connector.attitude_msg.connect(self.on_attitude_update)
        self.connector.sensor_data.connect(self.on_sensor_update)
        self.connector.connection_status.connect(self.on_connection_status)
        self.connector.log_received.connect(self.on_log_message)
        
        # Verbinde mit der Drone
        if await self.connector.connect_to_drone():
            print("Erfolgreich mit der simulierten Drone verbunden!")
            # Starte Monitoring
            await self.connector.start_monitoring()
            return True
        else:
            print("Verbindung zur simulierten Drone fehlgeschlagen!")
            return False
            
    async def disconnect_from_drone(self):
        if self.connector:
            await self.connector.disconnect_from_drone()
            print("Verbindung zur Drone getrennt")
            
    async def run(self):
        try:
            # Verbinde mit der Drone
            await self.connect_to_drone()
            
            # Warte auf Programmende
            while True:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            print("\nProgramm durch Benutzer beendet.")
        finally:
            # Trenne Verbindung
            await self.disconnect_from_drone()

if __name__ == "__main__":
    controller = DroneController()
    
    # Erstelle Event-Loop mit Qt-Integration
    loop = qasync.QEventLoop(controller.app)
    asyncio.set_event_loop(loop)
    
    try:
        loop.run_until_complete(controller.run())
    finally:
        loop.close() 