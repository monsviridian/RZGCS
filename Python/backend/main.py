from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from serial_connector import SerialConnector
from motor_controller import MotorController
from logger import Logger
from models import ConnectRequest, MotorTestRequest
from pydantic import BaseModel
from mavsdk_connector import MavsdkConnector
import sys
import asyncio
from PySide6.QtCore import QObject
from mavlink_connector import create_connector, ConnectorType
from typing import Optional, Literal

app = FastAPI()
serial_handler = SerialConnector()
motor_controller = MotorController(serial_handler)
logger = Logger()
mavsdk = MavsdkConnector()

# CORS für Frontend-Zugriff erlauben
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Globale Instanz des DroneBackend
drone_backend = None

class DroneBackend(QObject):
    def __init__(self):
        super().__init__()
        self.connector = None
        self.logger = Logger()
        self.motor_controller = MotorController(None)  # Wird später initialisiert
        
    async def connect_drone(self, data: ConnectRequest) -> dict:
        """Verbindet mit der Drohne über den gewählten Connector"""
        try:
            # Bestehende Verbindung trennen
            if self.connector:
                await self.connector.disconnect()
            
            # Connector basierend auf Typ erstellen
            if data.connection_type == "mavsdk":
                if not data.connection_string:
                    raise ValueError("connection_string ist für MAVSDK erforderlich")
                    
                self.connector = create_connector(
                    ConnectorType.MAVSDK,
                    connection_string=data.connection_string
                )
            else:  # mavlink
                if not data.port:
                    raise ValueError("port ist für MAVLink erforderlich")
                    
                self.connector = create_connector(
                    ConnectorType.PYMAVLINK,
                    port=data.port,
                    baudrate=data.baudrate or 57600
                )
            
            # Verbindung herstellen
            if await self.connector.connect():
                # Monitoring im Hintergrund starten
                asyncio.create_task(self.connector.start_monitoring())
                return {"status": "connected", "message": f"Erfolgreich verbunden via {data.connection_type}"}
            else:
                raise ConnectionError("Verbindung konnte nicht hergestellt werden")
                
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Verbindungsfehler: {str(e)}"
            )
    
    async def disconnect_drone(self) -> dict:
        """Trennt die Verbindung zur Drohne"""
        if self.connector:
            await self.connector.disconnect()
            self.connector = None
            return {"status": "disconnected"}
        return {"status": "already_disconnected"}

class ConnectRequest(BaseModel):
    connection_type: Literal["mavsdk", "mavlink"]
    # Gemeinsame Parameter
    autopilot: str = "ardupilot"
    # MAVSDK Parameter
    connection_string: Optional[str] = "udp://:14540"
    # MAVLink Parameter
    port: Optional[str] = None
    baudrate: Optional[int] = 57600

@app.post("/connect")
async def connect(data: ConnectRequest):
    """Verbindungsendpunkt für MAVSDK und MAVLink"""
    return await drone_backend.connect_drone(data)

@app.post("/disconnect")
async def disconnect():
    """Trennt die aktive Drohnenverbindung"""
    return await drone_backend.disconnect_drone()

@app.get("/status")
def get_status():
    """Gibt den aktuellen Verbindungsstatus zurück"""
    return {
        "connected": drone_backend.connector is not None,
        "connector_type": drone_backend.connector.__class__.__name__ if drone_backend.connector else None
    }

@app.get("/logs")
def get_logs():
    """Gibt die aktuellen Logs zurück"""
    return drone_backend.logger.read_logs()

@app.post("/motor/test")
def test_motor(data: MotorTestRequest):
    motor_controller.test_motor(data.motor_id, data.throttle)
    return {"status": "running"}

@app.get("/parameters")
def get_parameters():
    return serial_handler.read_parameters()

@app.on_event("startup")
async def startup_event():
    """Wird beim Start des Servers ausgeführt"""
    global drone_backend
    drone_backend = DroneBackend()

def start_server(host: str = "127.0.0.1", port: int = 8000):
    """Startet den FastAPI Server"""
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    start_server()
