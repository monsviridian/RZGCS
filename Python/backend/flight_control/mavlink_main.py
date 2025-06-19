import time
import threading
from pymavlink import mavutil
from PySide6.QtCore import QObject, Signal, Slot

class MAVLinkController(QObject):
    # Signale für Frontend
    state_changed = Signal(dict)
    mode_changed = Signal(str)
    error_occurred = Signal(str)
    mission_started = Signal(dict)
    mission_completed = Signal(dict)
    mission_aborted = Signal(dict)
    waypoint_reached = Signal(dict)
    mission_progress = Signal(float)
    safety_violation = Signal(str)
    safety_warning = Signal(str)
    safety_cleared = Signal(str)

    def __init__(self):
        super().__init__()
        self.connection = None
        self.running = False
        self.thread = None
        self.current_state = {
            "flight_phase": "DISARMED",
            "mode": "MANUAL",
            "armed": False,
            "position": {"lat": 0, "lon": 0, "alt": 0},
            "attitude": {"roll": 0, "pitch": 0, "yaw": 0},
            "velocity": {"vx": 0, "vy": 0, "vz": 0},
            "battery": {"voltage": 0, "current": 0, "remaining": 0},
            "sensors": {},
            "mission": None,
            "safety": {"violations": [], "warnings": []}
        }

    def connect_mavlink(self, connection_string="udpin:localhost:14550"):
        """Verbindet mit dem MAVLink-System"""
        try:
            self.connection = mavutil.mavlink_connection(connection_string)
            self.connection.wait_heartbeat()
            return True
        except Exception as e:
            self.error_occurred.emit(f"Verbindungsfehler: {str(e)}")
            return False

    def disconnect(self):
        """Trennt die Verbindung zum MAVLink-System"""
        self.running = False
        if self.thread:
            self.thread.join()
        if self.connection:
            self.connection.close()
            self.connection = None

    def start(self):
        """Startet den MAVLink-Controller"""
        if not self.connection:
            self.error_occurred.emit("Keine Verbindung zum MAVLink-System")
            return False

        self.running = True
        self.thread = threading.Thread(target=self._update_loop)
        self.thread.daemon = True
        self.thread.start()
        return True

    def stop(self):
        """Stoppt den MAVLink-Controller"""
        self.running = False
        if self.thread:
            self.thread.join()
        self.disconnect()

    def set_mode(self, mode):
        """Setzt den Flugmodus"""
        try:
            if not self.connection:
                raise Exception("Keine Verbindung zum MAVLink-System")

            # MAVLink-Modus setzen
            self.connection.set_mode(mode)
            self.current_state["mode"] = mode
            self.mode_changed.emit(mode)
            return True
        except Exception as e:
            self.error_occurred.emit(f"Fehler beim Setzen des Modus: {str(e)}")
            return False

    def start_mission(self, mission):
        """Startet eine Mission"""
        try:
            if not self.connection:
                raise Exception("Keine Verbindung zum MAVLink-System")

            # Mission starten
            self.current_state["mission"] = mission
            self.mission_started.emit(mission)
            return True
        except Exception as e:
            self.error_occurred.emit(f"Fehler beim Starten der Mission: {str(e)}")
            return False

    def abort_mission(self):
        """Bricht die aktuelle Mission ab"""
        try:
            if not self.connection:
                raise Exception("Keine Verbindung zum MAVLink-System")

            # Mission abbrechen
            self.current_state["mission"] = None
            self.mission_aborted.emit({"reason": "user_abort"})
            return True
        except Exception as e:
            self.error_occurred.emit(f"Fehler beim Abbrechen der Mission: {str(e)}")
            return False

    def _update_loop(self):
        """Hauptschleife für MAVLink-Updates"""
        while self.running:
            try:
                # MAVLink-Nachrichten empfangen
                msg = self.connection.recv_match(blocking=True, timeout=1.0)
                if msg is None:
                    continue

                # Nachrichtentyp verarbeiten
                if msg.get_type() == 'HEARTBEAT':
                    self._handle_heartbeat(msg)
                elif msg.get_type() == 'GLOBAL_POSITION_INT':
                    self._handle_position(msg)
                elif msg.get_type() == 'ATTITUDE':
                    self._handle_attitude(msg)
                elif msg.get_type() == 'SYS_STATUS':
                    self._handle_system_status(msg)
                elif msg.get_type() == 'MISSION_CURRENT':
                    self._handle_mission_current(msg)
                elif msg.get_type() == 'STATUSTEXT':
                    self._handle_status_text(msg)

            except Exception as e:
                self.error_occurred.emit(f"Fehler in Update-Schleife: {str(e)}")
                time.sleep(1.0)

    def _handle_heartbeat(self, msg):
        """Verarbeitet Heartbeat-Nachrichten"""
        # Flugphase aktualisieren
        if msg.system_status == mavutil.mavlink.MAV_STATE_ACTIVE:
            if not self.current_state["armed"]:
                self.current_state["flight_phase"] = "ARMED"
                self.state_changed.emit(self.current_state)
        elif msg.system_status == mavutil.mavlink.MAV_STATE_EMERGENCY:
            self.current_state["flight_phase"] = "EMERGENCY"
            self.state_changed.emit(self.current_state)
            self.safety_violation.emit("Notfallzustand erkannt")

    def _handle_position(self, msg):
        """Verarbeitet Positions-Nachrichten"""
        self.current_state["position"] = {
            "lat": msg.lat / 1e7,
            "lon": msg.lon / 1e7,
            "alt": msg.alt / 1000.0
        }
        self.state_changed.emit(self.current_state)

    def _handle_attitude(self, msg):
        """Verarbeitet Attitude-Nachrichten"""
        self.current_state["attitude"] = {
            "roll": msg.roll,
            "pitch": msg.pitch,
            "yaw": msg.yaw
        }
        self.state_changed.emit(self.current_state)

    def _handle_system_status(self, msg):
        """Verarbeitet System-Status-Nachrichten"""
        self.current_state["battery"] = {
            "voltage": msg.voltage_battery / 1000.0,
            "current": msg.current_battery / 100.0,
            "remaining": msg.battery_remaining
        }
        self.state_changed.emit(self.current_state)

    def _handle_mission_current(self, msg):
        """Verarbeitet Missions-Status-Nachrichten"""
        if self.current_state["mission"]:
            self.current_state["mission"]["current_waypoint"] = msg.seq
            self.waypoint_reached.emit({"waypoint": msg.seq})
            self.state_changed.emit(self.current_state)

    def _handle_status_text(self, msg):
        """Verarbeitet Status-Text-Nachrichten"""
        text = msg.text.decode('utf-8')
        if msg.severity >= mavutil.mavlink.MAV_SEVERITY_CRITICAL:
            self.safety_violation.emit(text)
        elif msg.severity >= mavutil.mavlink.MAV_SEVERITY_WARNING:
            self.safety_warning.emit(text) 