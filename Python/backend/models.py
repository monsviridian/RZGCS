from pydantic import BaseModel

class ConnectRequest(BaseModel):
    port: str
    baudrate: int

class MotorTestRequest(BaseModel):
    motor_id: int
    throttle: float
