class MotorController:
    def __init__(self, serial_handler):
        self.serial_handler = serial_handler

    def test_motor(self, motor_id, throttle):
        cmd = f"MOTOR_TEST {motor_id} {throttle}"
        self.serial_handler.send_command(cmd)
