"""
DroneKit-Integration Beispiel-Anwendung
Demonstriert die Verwendung der DroneKit-Integration in RZGCS
"""

import asyncio
import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLabel, QTextEdit, QLineEdit, QGroupBox, QGridLayout, QProgressBar, QComboBox
from PySide6.QtCore import QTimer, Signal, QObject, Slot

# Pfad zum backend-Modul hinzufügen
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from backend.rzgcs_dronekit.connector import DroneKitConnector

class DroneKitExampleApp(QMainWindow):
    """Beispiel-Anwendung für DroneKit-Integration"""
    
    def __init__(self):
        super().__init__()
        self.connector = None
        self.setup_ui()
        self.setup_connector()
        
    def setup_ui(self):
        """UI-Setup"""
        self.setWindowTitle("RZGCS DroneKit Integration Example")
        self.setGeometry(100, 100, 800, 600)
        
        # Haupt-Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout
        layout = QVBoxLayout(central_widget)
        
        # Connection-Gruppe
        connection_group = QGroupBox("Connection")
        connection_layout = QGridLayout(connection_group)
        
        self.connection_input = QLineEdit("udp://127.0.0.1:14550")
        self.connect_button = QPushButton("Connect")
        self.disconnect_button = QPushButton("Disconnect")
        self.connection_status = QLabel("Disconnected")
        
        connection_layout.addWidget(QLabel("Connection String:"), 0, 0)
        connection_layout.addWidget(self.connection_input, 0, 1)
        connection_layout.addWidget(self.connect_button, 0, 2)
        connection_layout.addWidget(self.disconnect_button, 0, 3)
        connection_layout.addWidget(QLabel("Status:"), 1, 0)
        connection_layout.addWidget(self.connection_status, 1, 1)
        
        layout.addWidget(connection_group)
        
        # Telemetry-Gruppe
        telemetry_group = QGroupBox("Telemetry")
        telemetry_layout = QGridLayout(telemetry_group)
        
        self.gps_label = QLabel("GPS: N/A")
        self.altitude_label = QLabel("Altitude: N/A")
        self.battery_label = QLabel("Battery: N/A")
        self.flight_mode_label = QLabel("Flight Mode: N/A")
        self.armed_label = QLabel("Armed: N/A")
        self.ground_speed_label = QLabel("Ground Speed: N/A")
        self.heading_label = QLabel("Heading: N/A")
        self.satellites_label = QLabel("Satellites: N/A")
        
        telemetry_layout.addWidget(self.gps_label, 0, 0)
        telemetry_layout.addWidget(self.altitude_label, 0, 1)
        telemetry_layout.addWidget(self.battery_label, 0, 2)
        telemetry_layout.addWidget(self.flight_mode_label, 1, 0)
        telemetry_layout.addWidget(self.armed_label, 1, 1)
        telemetry_layout.addWidget(self.ground_speed_label, 1, 2)
        telemetry_layout.addWidget(self.heading_label, 2, 0)
        telemetry_layout.addWidget(self.satellites_label, 2, 1)
        
        layout.addWidget(telemetry_group)
        
        # Control-Gruppe
        control_group = QGroupBox("Control")
        control_layout = QGridLayout(control_group)
        
        self.arm_button = QPushButton("Arm")
        self.disarm_button = QPushButton("Disarm")
        self.takeoff_button = QPushButton("Takeoff")
        self.land_button = QPushButton("Land")
        self.rtl_button = QPushButton("RTL")
        
        control_layout.addWidget(self.arm_button, 0, 0)
        control_layout.addWidget(self.disarm_button, 0, 1)
        control_layout.addWidget(self.takeoff_button, 0, 2)
        control_layout.addWidget(self.land_button, 1, 0)
        control_layout.addWidget(self.rtl_button, 1, 1)
        
        layout.addWidget(control_group)
        
        # Mission-Gruppe
        mission_group = QGroupBox("Mission")
        mission_layout = QGridLayout(mission_group)
        
        self.upload_mission_button = QPushButton("Upload Mission")
        self.start_mission_button = QPushButton("Start Mission")
        self.pause_mission_button = QPushButton("Pause Mission")
        self.resume_mission_button = QPushButton("Resume Mission")
        self.stop_mission_button = QPushButton("Stop Mission")
        
        mission_layout.addWidget(self.upload_mission_button, 0, 0)
        mission_layout.addWidget(self.start_mission_button, 0, 1)
        mission_layout.addWidget(self.pause_mission_button, 0, 2)
        mission_layout.addWidget(self.resume_mission_button, 1, 0)
        mission_layout.addWidget(self.stop_mission_button, 1, 1)
        
        layout.addWidget(mission_group)
        
        # Parameter-Gruppe
        parameter_group = QGroupBox("Parameters")
        parameter_layout = QGridLayout(parameter_group)
        
        self.load_params_button = QPushButton("Load Parameters")
        self.param_name_input = QLineEdit("RTL_ALT")
        self.param_value_input = QLineEdit("100")
        self.set_param_button = QPushButton("Set Parameter")
        
        parameter_layout.addWidget(self.load_params_button, 0, 0)
        parameter_layout.addWidget(QLabel("Parameter:"), 1, 0)
        parameter_layout.addWidget(self.param_name_input, 1, 1)
        parameter_layout.addWidget(QLabel("Value:"), 1, 2)
        parameter_layout.addWidget(self.param_value_input, 1, 3)
        parameter_layout.addWidget(self.set_param_button, 1, 4)
        
        layout.addWidget(parameter_group)
        
        # Log-Gruppe
        log_group = QGroupBox("Log")
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(150)
        self.clear_log_button = QPushButton("Clear Log")
        
        log_layout.addWidget(self.log_text)
        log_layout.addWidget(self.clear_log_button)
        
        layout.addWidget(log_group)
        
        # Button-Connections
        self.connect_button.clicked.connect(self.connect_to_drone)
        self.disconnect_button.clicked.connect(self.disconnect_from_drone)
        self.arm_button.clicked.connect(self.arm_drone)
        self.disarm_button.clicked.connect(self.disarm_drone)
        self.takeoff_button.clicked.connect(self.takeoff_drone)
        self.land_button.clicked.connect(self.land_drone)
        self.rtl_button.clicked.connect(self.rtl_drone)
        self.upload_mission_button.clicked.connect(self.upload_mission)
        self.start_mission_button.clicked.connect(self.start_mission)
        self.pause_mission_button.clicked.connect(self.pause_mission)
        self.resume_mission_button.clicked.connect(self.resume_mission)
        self.stop_mission_button.clicked.connect(self.stop_mission)
        self.load_params_button.clicked.connect(self.load_parameters)
        self.set_param_button.clicked.connect(self.set_parameter)
        self.clear_log_button.clicked.connect(self.clear_log)
        
        # Initialer Status
        self.update_ui_state(False)
        
    def setup_connector(self):
        """Connector-Setup"""
        self.connector = DroneKitConnector("")
        
        # Signals verbinden
        self.connector.connection_status_changed.connect(self.on_connection_changed)
        self.connector.gps_position_updated.connect(self.on_gps_updated)
        self.connector.altitude_updated.connect(self.on_altitude_updated)
        self.connector.battery_updated.connect(self.on_battery_updated)
        self.connector.flight_mode_changed.connect(self.on_flight_mode_changed)
        self.connector.armed_status_changed.connect(self.on_armed_changed)
        self.connector.ground_speed_updated.connect(self.on_ground_speed_updated)
        self.connector.heading_updated.connect(self.on_heading_updated)
        self.connector.satellite_count_updated.connect(self.on_satellite_count_updated)
        self.connector.error_occurred.connect(self.on_error)
        self.connector.log_message.connect(self.on_log_message)
        
        # Mission-Signals
        self.connector.mission_uploaded.connect(self.on_mission_uploaded)
        self.connector.mission_started.connect(self.on_mission_started)
        self.connector.mission_completed.connect(self.on_mission_completed)
        self.connector.mission_error.connect(self.on_mission_error)
        
        # Control-Signals
        self.connector.arm_status_changed.connect(self.on_arm_status_changed)
        self.connector.takeoff_completed.connect(self.on_takeoff_completed)
        self.connector.landing_completed.connect(self.on_landing_completed)
        self.connector.control_error.connect(self.on_control_error)
        
        # Parameter-Signals
        self.connector.parameters_loaded.connect(self.on_parameters_loaded)
        self.connector.parameter_set.connect(self.on_parameter_set)
        self.connector.parameter_error.connect(self.on_parameter_error)
        
    def update_ui_state(self, connected: bool):
        """Aktualisiert UI-Status"""
        self.connect_button.setEnabled(not connected)
        self.disconnect_button.setEnabled(connected)
        self.arm_button.setEnabled(connected)
        self.disarm_button.setEnabled(connected)
        self.takeoff_button.setEnabled(connected)
        self.land_button.setEnabled(connected)
        self.rtl_button.setEnabled(connected)
        self.upload_mission_button.setEnabled(connected)
        self.start_mission_button.setEnabled(connected)
        self.pause_mission_button.setEnabled(connected)
        self.resume_mission_button.setEnabled(connected)
        self.stop_mission_button.setEnabled(connected)
        self.load_params_button.setEnabled(connected)
        self.set_param_button.setEnabled(connected)
        
    # Connection-Slots
    @Slot()
    def connect_to_drone(self):
        """Verbindet zur Drohne"""
        connection_string = self.connection_input.text()
        self.connector.connection_string = connection_string
        asyncio.create_task(self.connector.connect())
        
    @Slot()
    def disconnect_from_drone(self):
        """Trennt Verbindung zur Drohne"""
        self.connector.disconnect()
        
    # Control-Slots
    @Slot()
    def arm_drone(self):
        """Armt die Drohne"""
        self.connector.arm_disarm(True)
        
    @Slot()
    def disarm_drone(self):
        """Disarmed die Drohne"""
        self.connector.arm_disarm(False)
        
    @Slot()
    def takeoff_drone(self):
        """Takeoff"""
        self.connector.takeoff(50.0)  # 50m Höhe
        
    @Slot()
    def land_drone(self):
        """Landung"""
        self.connector.land()
        
    @Slot()
    def rtl_drone(self):
        """Return to Launch"""
        self.connector.return_to_launch()
        
    # Mission-Slots
    @Slot()
    def upload_mission(self):
        """Lädt Beispiel-Mission hoch"""
        waypoints = [
            {'lat': 52.5200, 'lon': 13.4050, 'alt': 50.0},  # Berlin
            {'lat': 52.5200, 'lon': 13.4150, 'alt': 50.0},  # 1km östlich
            {'lat': 52.5300, 'lon': 13.4150, 'alt': 50.0},  # 1km nördlich
            {'lat': 52.5300, 'lon': 13.4050, 'alt': 50.0},  # 1km westlich
            {'lat': 52.5200, 'lon': 13.4050, 'alt': 50.0}   # Zurück zum Start
        ]
        self.connector.upload_mission(waypoints)
        
    @Slot()
    def start_mission(self):
        """Startet Mission"""
        self.connector.start_mission()
        
    @Slot()
    def pause_mission(self):
        """Pausiert Mission"""
        self.connector.pause_mission()
        
    @Slot()
    def resume_mission(self):
        """Setzt Mission fort"""
        self.connector.resume_mission()
        
    @Slot()
    def stop_mission(self):
        """Stoppt Mission"""
        self.connector.stop_mission()
        
    # Parameter-Slots
    @Slot()
    def load_parameters(self):
        """Lädt Parameter"""
        self.connector.load_parameters()
        
    @Slot()
    def set_parameter(self):
        """Setzt Parameter"""
        param_name = self.param_name_input.text()
        try:
            param_value = float(self.param_value_input.text())
            self.connector.set_parameter(param_name, param_value)
        except ValueError:
            self.log_message(f"Invalid parameter value: {self.param_value_input.text()}")
            
    @Slot()
    def clear_log(self):
        """Löscht Log"""
        self.log_text.clear()
        
    # Signal-Handler
    def on_connection_changed(self, connected: bool):
        """Handler für Verbindungsstatus"""
        status = "Connected" if connected else "Disconnected"
        self.connection_status.setText(status)
        self.update_ui_state(connected)
        self.log_message(f"Connection: {status}")
        
    def on_gps_updated(self, lat: float, lon: float, alt: float):
        """Handler für GPS-Updates"""
        self.gps_label.setText(f"GPS: {lat:.6f}, {lon:.6f}")
        
    def on_altitude_updated(self, altitude: float):
        """Handler für Altitude-Updates"""
        self.altitude_label.setText(f"Altitude: {altitude:.1f}m")
        
    def on_battery_updated(self, battery: float):
        """Handler für Battery-Updates"""
        self.battery_label.setText(f"Battery: {battery:.0f}%")
        
    def on_flight_mode_changed(self, mode: str):
        """Handler für Flight-Mode-Updates"""
        self.flight_mode_label.setText(f"Flight Mode: {mode}")
        
    def on_armed_changed(self, armed: bool):
        """Handler für Armed-Status-Updates"""
        status = "Armed" if armed else "Disarmed"
        self.armed_label.setText(f"Armed: {status}")
        
    def on_ground_speed_updated(self, speed: float):
        """Handler für Ground-Speed-Updates"""
        self.ground_speed_label.setText(f"Ground Speed: {speed:.1f}m/s")
        
    def on_heading_updated(self, heading: float):
        """Handler für Heading-Updates"""
        self.heading_label.setText(f"Heading: {heading:.1f}°")
        
    def on_satellite_count_updated(self, satellites: int):
        """Handler für Satellite-Count-Updates"""
        self.satellites_label.setText(f"Satellites: {satellites}")
        
    def on_error(self, error: str):
        """Handler für Fehler"""
        self.log_message(f"ERROR: {error}")
        
    def on_log_message(self, message: str):
        """Handler für Log-Nachrichten"""
        self.log_message(message)
        
    # Mission-Handler
    def on_mission_uploaded(self, waypoint_count: int):
        """Handler für Mission-Upload"""
        self.log_message(f"Mission uploaded: {waypoint_count} waypoints")
        
    def on_mission_started(self):
        """Handler für Mission-Start"""
        self.log_message("Mission started")
        
    def on_mission_completed(self):
        """Handler für Mission-Abschluss"""
        self.log_message("Mission completed")
        
    def on_mission_error(self, error: str):
        """Handler für Mission-Fehler"""
        self.log_message(f"Mission error: {error}")
        
    # Control-Handler
    def on_arm_status_changed(self, armed: bool):
        """Handler für Arm-Status"""
        status = "Armed" if armed else "Disarmed"
        self.log_message(f"Vehicle {status}")
        
    def on_takeoff_completed(self, altitude: float):
        """Handler für Takeoff-Abschluss"""
        self.log_message(f"Takeoff completed at {altitude:.1f}m")
        
    def on_landing_completed(self):
        """Handler für Landung-Abschluss"""
        self.log_message("Landing completed")
        
    def on_control_error(self, error: str):
        """Handler für Control-Fehler"""
        self.log_message(f"Control error: {error}")
        
    # Parameter-Handler
    def on_parameters_loaded(self, param_count: int):
        """Handler für Parameter-Load"""
        self.log_message(f"Parameters loaded: {param_count}")
        
    def on_parameter_set(self, param_name: str, value: float):
        """Handler für Parameter-Set"""
        self.log_message(f"Parameter set: {param_name} = {value}")
        
    def on_parameter_error(self, error: str):
        """Handler für Parameter-Fehler"""
        self.log_message(f"Parameter error: {error}")
        
    def log_message(self, message: str):
        """Loggt Nachricht"""
        self.log_text.append(f"[{asyncio.get_event_loop().time():.1f}] {message}")
        self.log_text.ensureCursorVisible()

def main():
    """Hauptfunktion"""
    app = QApplication(sys.argv)
    
    # Event-Loop für asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Timer für asyncio-Events
    timer = QTimer()
    timer.timeout.connect(lambda: loop.stop() or loop.run_forever())
    timer.start(10)  # 10ms
    
    # Hauptfenster
    window = DroneKitExampleApp()
    window.show()
    
    # Event-Loop starten
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 