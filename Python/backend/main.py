from fastapi import FastAPI
from serial_connector import SerialConnector
from motor_controller import MotorController
from logger import Logger
from models import ConnectRequest, MotorTestRequest
from pydantic import BaseModel
from mavsdk_connector import MavsdkConnector

app = FastAPI()
serial_handler = SerialConnector()
motor_controller = MotorController(serial_handler)
logger = Logger()
mavsdk = MavsdkConnector()

@app.post("/connect")
def connect_to_flight_controller(data: ConnectRequest):
    success = serial_handler.connect(data.port, data.baudrate)
    return {"connected": success}

@app.post("/motor/test")
def test_motor(data: MotorTestRequest):
    motor_controller.test_motor(data.motor_id, data.throttle)
    return {"status": "running"}

@app.get("/logs")
def get_logs():
    return logger.read_logs()

@app.get("/parameters")
def get_parameters():
    return serial_handler.read_parameters()

class ConnectRequest(BaseModel):
    port: str
    baudrate: int
    autopilot: str

@app.post("/serial/connect")
async def connect_serial(req: ConnectRequest):
    if req.autopilot.lower() == "ardupilot":
        await mavsdk.connect(port=req.port, baudrate=req.baudrate)
        return {"status": "connected"} if mavsdk.is_connected() else {"status": "failed"}
    else:
        return {"error": f"Autopilot '{req.autopilot}' wird derzeit nicht unterstützt."}
