import time
import threading
from typing import Optional, Callable
from pymavlink import mavutil
from pymavlink.dialects.v20 import ardupilotmega as mavlink2

from .simulated_drone import SimulatedDrone
from .exceptions import ConnectionError, ConnectionTimeoutError

class SimulatedMAVLink:
    def __init__(self):
        self.drone = SimulatedDrone()
        self.connected = False
        self.heartbeat_interval = 1.0  # seconds
        self.sensor_interval = 0.1     # seconds
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._message_handlers: Dict[str, Callable] = {}
        
    def connect(self, connection_string: str = "simulator://") -> bool:
        """Connect to the simulated drone"""
        try:
            self.connected = True
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._run_simulation)
            self._thread.daemon = True
            self._thread.start()
            return True
        except Exception as e:
            raise ConnectionError(f"Failed to connect to simulated drone: {str(e)}")
            
    def disconnect(self):
        """Disconnect from the simulated drone"""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=2.0)
        self.connected = False
        
    def _run_simulation(self):
        """Main simulation loop"""
        last_heartbeat = time.time()
        last_sensor = time.time()
        
        while not self._stop_event.is_set():
            current_time = time.time()
            
            # Update drone state
            self.drone.update()
            
            # Send heartbeat
            if current_time - last_heartbeat >= self.heartbeat_interval:
                self._handle_message(self.drone.get_heartbeat())
                last_heartbeat = current_time
                
            # Send sensor data
            if current_time - last_sensor >= self.sensor_interval:
                self._handle_message(self.drone.get_system_status())
                self._handle_message(self.drone.get_attitude())
                self._handle_message(self.drone.get_global_position())
                self._handle_message(self.drone.get_gps_raw())
                last_sensor = current_time
                
            time.sleep(0.01)  # Small delay to prevent CPU overload
            
    def _handle_message(self, message: Dict):
        """Handle outgoing messages"""
        if message['type'] in self._message_handlers:
            self._message_handlers[message['type']](message)
            
    def register_message_handler(self, message_type: str, handler: Callable):
        """Register a handler for specific message types"""
        self._message_handlers[message_type] = handler
        
    def send_command(self, command: str, params: Dict = None) -> bool:
        """Send a command to the simulated drone"""
        if not self.connected:
            return False
            
        if command == "SET_MODE":
            return self.drone.set_mode(params.get('mode', 'STABILIZE'))
        elif command == "ARM":
            return self.drone.arm(params.get('arm', False))
        elif command == "REQUEST_PARAMETERS":
            params = self.drone.get_parameters()
            for param in params:
                self._handle_message({
                    'type': 'PARAM_VALUE',
                    'param_id': param['name'],
                    'param_value': param['value'],
                    'param_type': 9,  # FLOAT
                    'param_count': len(params),
                    'param_index': list(self.drone.parameters.keys()).index(param['name'])
                })
            return True
            
        return False 