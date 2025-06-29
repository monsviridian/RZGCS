# backend/mavlink_connector.py

import threading, time, subprocess, sys, os
from PySide6.QtCore import QObject, Signal, QTimer, Slot
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
import asyncio
from enum import Enum
import pathlib
from pymavlink import mavutil
from pymavlink.dialects.v20 import ardupilotmega as mavlink
import serial
import math

from backend.mavlink_protocol import MAVLinkProtocol
from backend.drone_connector_base import DroneConnectorBase
from backend.exceptions import ConnectionTimeoutError, ConnectionError

class ConnectorType(Enum):
    PYMAVLINK = "pymavlink"
    MAVSDK = "mavsdk"
    DRONEKIT = "dronekit"  # NEU: DroneKit-Unterstützung

def get_mavsdk_server_path() -> str:
    """Ermittelt den Pfad zum MAVSDK-Server basierend auf dem Betriebssystem"""
    # Basis-Pfad zum Projekt-Ordner
    base_path = pathlib.Path(__file__).parent.parent.parent
    mavsdk_path = base_path / "mavsdk_server"
    
    if sys.platform == "win32":
        server_path = mavsdk_path / "windows" / "mavsdk-server.exe"
    elif sys.platform == "darwin":  # macOS
        # Prüfe beide möglichen Speicherorte für macOS
        server_path_1 = mavsdk_path / "mac" / "mavsdk-server"
        server_path_2 = mavsdk_path / "macos" / "mavsdk-server"
        
        if server_path_1.exists():
            server_path = server_path_1
        elif server_path_2.exists():
            server_path = server_path_2
        else:
            # Versuche den Server im aktuellen Verzeichnis zu finden (für Entwicklungsumgebungen)
            server_path = mavsdk_path / "mavsdk-server"
    else:  # Linux
        server_path = mavsdk_path / "linux" / "mavsdk-server"
    
    if not server_path.exists():
        raise FileNotFoundError(
            f"MAVSDK-Server nicht gefunden in: {server_path}\n"
            f"Bitte stellen Sie sicher, dass der Server im richtigen Ordner liegt:\n"
            f"- Windows: mavsdk_server/windows/mavsdk-server.exe\n"
            f"- macOS: mavsdk_server/mac/mavsdk-server\n"
            f"- Linux: mavsdk_server/linux/mavsdk-server"
        )
    
    # Unter Unix-Systemen müssen wir die Ausführungsrechte setzen
    if sys.platform != "win32":
        server_path.chmod(0o755)
    
    return str(server_path)

# Metaclass-Konflikt lösen
class DroneConnectorMeta(type(QObject), type(ABC)):
    pass

class DroneConnectorBase(QObject, ABC, metaclass=DroneConnectorMeta):
    """Basis-Klasse für Drohnen-Verbindungen"""
    
    # Gemeinsame Signals für alle Connector-Implementierungen
    log_received = Signal(str)  # Logging-Nachrichten
    gps_msg = Signal(float, float)  # Latitude, Longitude
    attitude_msg = Signal(float, float, float)  # Roll, Pitch, Yaw
    sensor_data = Signal(str, float)  # Sensor-Name, Wert
    connection_status = Signal(bool)  # Verbindungsstatus

    def __init__(self):
        """Initialisiert die Basisklasse"""
        super().__init__()
        self.running = False
        self.debug = True
        self._is_connecting = False

    @abstractmethod
    async def connect_to_drone(self) -> bool:
        """
        Stellt eine Verbindung zur Drohne her.
        Returns:
            bool: True wenn die Verbindung erfolgreich war, False sonst
        """
        pass

    @abstractmethod
    async def disconnect_from_drone(self) -> None:
        """Trennt die Verbindung zur Drohne"""
        pass

    @abstractmethod
    async def start_monitoring(self) -> None:
        """Startet das Monitoring der Drohnendaten"""
        pass
        
    @abstractmethod
    def stop(self) -> None:
        """Beendet die Verbindung synchron"""
        pass

    def _emit_log(self, message: str) -> None:
        """Sendet eine Log-Nachricht"""
        if self.debug:
            self.log_received.emit(message)

    def _emit_connection_status(self, connected: bool) -> None:
        """Aktualisiert den Verbindungsstatus"""
        self.connection_status.emit(connected)
        if self.debug:
            status = "✅ Verbunden" if connected else "❌ Getrennt"
            self._emit_log(status)

class DroneKitConnector(DroneConnectorBase):
    """DroneKit-basierte Implementierung"""
    
    def __init__(self, connection_string: str):
        """Initialisiert den DroneKit-Connector"""
        super().__init__()
        self.connection_string = connection_string
        self.dronekit_connector = None
        
    async def connect_to_drone(self) -> bool:
        """
        Implementiert die abstrakte connect_to_drone-Methode der Basisklasse.
        Returns:
            bool: True wenn die Verbindung erfolgreich war, False sonst
        """
        try:
            # DroneKit-Connector importieren und erstellen
            from backend.rzgcs_dronekit.connector import DroneKitConnector as DKConnector
            
            self.dronekit_connector = DKConnector(self.connection_string)
            
            # Verbindung herstellen (synchron, nicht async)
            success = self.dronekit_connector.establish_connection()
            
            if success:
                # Signals verbinden
                self.dronekit_connector.connection_status_changed.connect(self._on_connection_changed)
                self.dronekit_connector.gps_position_updated.connect(self._on_gps_updated)
                self.dronekit_connector.attitude_updated.connect(self._on_attitude_updated)
                self.dronekit_connector.battery_updated.connect(self._on_battery_updated)
                self.dronekit_connector.flight_mode_changed.connect(self._on_flight_mode_changed)
                self.dronekit_connector.armed_status_changed.connect(self._on_armed_changed)
                self.dronekit_connector.ground_speed_updated.connect(self._on_ground_speed_updated)
                self.dronekit_connector.altitude_updated.connect(self._on_altitude_updated)
                self.dronekit_connector.heading_updated.connect(self._on_heading_updated)
                self.dronekit_connector.error_occurred.connect(self._on_error)
                self.dronekit_connector.log_message.connect(self._on_log)
                
                self.running = True
                self._emit_connection_status(True)
                return True
            else:
                return False
                
        except Exception as e:
            self._emit_log(f"DroneKit connection failed: {str(e)}")
            return False
        
    async def disconnect_from_drone(self) -> None:
        """
        Implementiert die abstrakte disconnect_from_drone-Methode der Basisklasse.
        """
        if self.dronekit_connector:
            self.dronekit_connector.close_connection()
            self.dronekit_connector = None
        
        self.running = False
        self._emit_connection_status(False)
        
    async def start_monitoring(self) -> None:
        """
        Implementiert die abstrakte start_monitoring-Methode der Basisklasse.
        """
        # DroneKit-Connector startet Monitoring automatisch
        pass
        
    def stop(self) -> None:
        """
        Implementiert die abstrakte stop-Methode der Basisklasse.
        """
        if self.dronekit_connector:
            self.dronekit_connector.close_connection()
            self.dronekit_connector = None
        
        self.running = False
        self._emit_connection_status(False)
    
    # Signal-Handler für DroneKit-Events
    def _on_connection_changed(self, connected: bool):
        """Handler für Verbindungsstatus-Änderungen"""
        self._emit_connection_status(connected)
    
    def _on_gps_updated(self, lat: float, lon: float, alt: float):
        """Handler für GPS-Updates"""
        self.gps_msg.emit(lat, lon)
        self.sensor_data.emit("GPS Altitude", alt)
    
    def _on_attitude_updated(self, roll: float, pitch: float, yaw: float):
        """Handler für Attitude-Updates"""
        self.attitude_msg.emit(roll, pitch, yaw)
        self.sensor_data.emit("Roll", roll)
        self.sensor_data.emit("Pitch", pitch)
        self.sensor_data.emit("Yaw", yaw)
    
    def _on_battery_updated(self, battery: float):
        """Handler für Battery-Updates"""
        self.sensor_data.emit("Battery %", battery)
    
    def _on_flight_mode_changed(self, mode: str):
        """Handler für Flight-Mode-Updates"""
        self.sensor_data.emit("Flight Mode", 0)  # Numerischer Wert für Kompatibilität
        self._emit_log(f"Flight Mode: {mode}")
    
    def _on_armed_changed(self, armed: bool):
        """Handler für Armed-Status-Updates"""
        self.sensor_data.emit("Armed", 1 if armed else 0)
        self._emit_log(f"Armed: {armed}")
    
    def _on_ground_speed_updated(self, speed: float):
        """Handler für Ground-Speed-Updates"""
        self.sensor_data.emit("Groundspeed", speed)
    
    def _on_altitude_updated(self, altitude: float):
        """Handler für Altitude-Updates"""
        self.sensor_data.emit("Altitude", altitude)
    
    def _on_heading_updated(self, heading: float):
        """Handler für Heading-Updates"""
        self.sensor_data.emit("Heading", heading)
    
    def _on_error(self, error: str):
        """Handler für Fehler"""
        self._emit_log(f"DroneKit Error: {error}")
    
    def _on_log(self, message: str):
        """Handler für Log-Nachrichten"""
        self._emit_log(f"DroneKit: {message}")

class MAVSDKConnector(DroneConnectorBase):
    """MAVSDK-basierte Implementierung"""
    
    def __init__(self, connection_string: str):
        """Initialisiert den MAVSDK-Connector"""
        super().__init__()
        self.connection_string = connection_string
        self.mavsdk_server_process = None
        self.drone = None
        self._reconnect_task = None
        self._connection_check_interval = 5  # Sekunden zwischen Verbindungsprüfungen
        self._last_heartbeat = 0
        self._heartbeat_timeout = 3  # Sekunden bis Verbindung als tot gilt
        
    async def connect_to_drone(self) -> bool:
        """
        Implementiert die abstrakte connect_to_drone-Methode der Basisklasse.
        Returns:
            bool: True wenn die Verbindung erfolgreich war, False sonst
        """
        return await self.establish_connection()
        
    async def disconnect_from_drone(self) -> None:
        """
        Implementiert die abstrakte disconnect_from_drone-Methode der Basisklasse.
        """
        await self.close_connection()
        
    async def start_monitoring(self) -> None:
        """
        Implementiert die abstrakte start_monitoring-Methode der Basisklasse.
        """
        await self.begin_vehicle_monitoring()
        
    def stop(self) -> None:
        """
        Implementiert die abstrakte stop-Methode der Basisklasse.
        """
        self.stop_vehicle_monitoring()

    def stop_vehicle_monitoring(self) -> None:
        """Synchrone Methode zum Beenden der Verbindung"""
        self.running = False
        
        if self.debug:
            print("🔄 Beende MAVSDK-Verbindung...")
            
        if self.mavsdk_server_process:
            try:
                self.mavsdk_server_process.terminate()
                self.mavsdk_server_process.wait(timeout=5)
            except:
                pass
            finally:
                self.mavsdk_server_process = None
                
        self.connection_status.emit(False)
        
    async def establish_connection(self) -> bool:
        """Verbindung via MAVSDK herstellen"""
        if self._is_connecting:
            self._emit_log("⚠️ Verbindungsversuch läuft bereits")
            return False
            
        self._is_connecting = True
        try:
            if self.debug:
                self._emit_log("🔄 Importiere MAVSDK...")
                
            from mavsdk import System
            
            # Starte MAVSDK-Server wenn nötig
            if "udp" not in self.connection_string.lower():
                if self.debug:
                    self._emit_log("🔌 Serielle Verbindung erkannt, starte Server...")
                if not await self.start_mavsdk_server():
                    return False
            
            if self.debug:
                self._emit_log("🔄 Erstelle MAVSDK System...")
                
            self.drone = System()
            
            if self.debug:
                self._emit_log(f"🔌 Verbinde mit System: {self.connection_string}")
                
            # Verbinde mit dem System über die übergebene Verbindungs-URL
            await self.drone.connect(system_address=self.connection_string)
            
            self._emit_log("⏳ Warte auf Verbindung...")
            connection_timeout = time.time() + 10  # 10 Sekunden Timeout
            
            async for state in self.drone.core.connection_state():
                if state.is_connected:
                    self._emit_log("✅ Verbunden via MAVSDK!")
                    if self.debug:
                        try:
                            system_info = await self.drone.info.get_version()
                            self._emit_log(f"ℹ️ System Info: {system_info}")
                        except:
                            pass
                    self._emit_connection_status(True)
                    self.running = True
                    self._is_connecting = False
                    return True
                    
                if time.time() > connection_timeout:
                    self._emit_log("⚠️ Timeout beim Warten auf Verbindung")
                    break
                    
                await asyncio.sleep(0.1)
                
        except Exception as e:
            error_msg = f"❌ Fehler in MAVSDK-Verbindung: {str(e)}"
            self._emit_log(error_msg)
            self._is_connecting = False
            return False
            
        self._is_connecting = False
        return False

    async def close_connection(self) -> None:
        """Schließt die MAVSDK-Verbindung"""
        try:
            if self.drone:
                await self.drone.disconnect()
                self.drone = None
                
            if self.mavsdk_server_process:
                self.mavsdk_server_process.terminate()
                self.mavsdk_server_process = None
                
            self.running = False
            self._emit_connection_status(False)
            self._emit_log("🔌 MAVSDK-Verbindung geschlossen")
            
        except Exception as e:
            self._emit_log(f"❌ Fehler beim Schließen der Verbindung: {str(e)}")

    async def begin_vehicle_monitoring(self) -> None:
        """Startet das Monitoring der Fahrzeugdaten"""
        if not self.drone:
            self._emit_log("❌ Keine MAVSDK-Verbindung verfügbar")
            return
            
        try:
            self._emit_log("📡 Starte Telemetrie-Monitoring...")
            
            # GPS-Position
            async for position in self.drone.telemetry.position():
                if not self.running:
                    break
                lat, lon = position.latitude_deg, position.longitude_deg
                self.gps_msg.emit(lat, lon)
                self.sensor_data.emit("GPS Altitude", position.absolute_altitude_m)
                
            # Attitude
            async for attitude in self.drone.telemetry.attitude_euler():
                if not self.running:
                    break
                roll, pitch, yaw = attitude.roll_deg, attitude.pitch_deg, attitude.yaw_deg
                self.attitude_msg.emit(roll, pitch, yaw)
                self.sensor_data.emit("Roll", roll)
                self.sensor_data.emit("Pitch", pitch)
                self.sensor_data.emit("Yaw", yaw)
                
            # Battery
            async for battery in self.drone.telemetry.battery():
                if not self.running:
                    break
                self.sensor_data.emit("Battery %", battery.remaining_percent)
                
            # Flight Mode
            async for flight_mode in self.drone.telemetry.flight_mode():
                if not self.running:
                    break
                self.sensor_data.emit("Flight Mode", 0)  # Numerischer Wert für Kompatibilität
                self._emit_log(f"Flight Mode: {flight_mode}")
                
            # Armed Status
            async for armed in self.drone.telemetry.armed():
                if not self.running:
                    break
                self.sensor_data.emit("Armed", 1 if armed else 0)
                self._emit_log(f"Armed: {armed}")
                
            # Ground Speed
            async for ground_speed in self.drone.telemetry.ground_speed_ned():
                if not self.running:
                    break
                speed = math.sqrt(ground_speed.velocity_north_m_s**2 + ground_speed.velocity_east_m_s**2)
                self.sensor_data.emit("Groundspeed", speed)
                
        except Exception as e:
            self._emit_log(f"❌ Fehler im Telemetrie-Monitoring: {str(e)}")

    def __del__(self):
        """Destruktor für Aufräumarbeiten"""
        if self.mavsdk_server_process:
            try:
                self.mavsdk_server_process.terminate()
            except:
                pass

    async def start_mavsdk_server(self) -> bool:
        """Startet den MAVSDK-Server für serielle Verbindungen"""
        try:
            server_path = get_mavsdk_server_path()
            
            # Verbindungsstring für Server parsen
            if "serial://" in self.connection_string:
                # Format: serial:///COM3:115200
                parts = self.connection_string.replace("serial://", "").split(":")
                if len(parts) == 2:
                    port, baudrate = parts
                    server_args = [server_path, "-p", "50051", f"-d=serial://{port}:{baudrate}"]
                else:
                    self._emit_log("❌ Ungültiges serielles Verbindungsformat")
                    return False
            else:
                # Standard-UDP für andere Verbindungen
                server_args = [server_path, "-p", "50051", f"-d={self.connection_string}"]
            
            self._emit_log(f"🚀 Starte MAVSDK-Server: {' '.join(server_args)}")
            
            self.mavsdk_server_process = subprocess.Popen(
                server_args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Warten auf Server-Start
            await asyncio.sleep(2)
            
            if self.mavsdk_server_process.poll() is None:
                self._emit_log("✅ MAVSDK-Server gestartet")
                # Verbindungsstring für MAVSDK-Client anpassen
                self.connection_string = "tcp://localhost:50051"
                return True
            else:
                self._emit_log("❌ MAVSDK-Server konnte nicht gestartet werden")
                return False
                
        except Exception as e:
            self._emit_log(f"❌ Fehler beim Starten des MAVSDK-Servers: {str(e)}")
            return False

    async def _monitor_server_output(self):
        """Überwacht die Ausgabe des MAVSDK-Servers"""
        if not self.mavsdk_server_process:
            return
            
        try:
            while self.running and self.mavsdk_server_process.poll() is None:
                output = self.mavsdk_server_process.stdout.readline()
                if output:
                    self._emit_log(f"MAVSDK-Server: {output.strip()}")
                await asyncio.sleep(0.1)
        except:
            pass

    def _is_connection_alive(self) -> bool:
        """Prüft ob die Verbindung noch aktiv ist"""
        if not self.drone:
            return False
            
        current_time = time.time()
        if current_time - self._last_heartbeat > self._heartbeat_timeout:
            return False
            
        return True

    async def _restart_connection(self):
        """Versucht die Verbindung neu zu starten"""
        self._emit_log("🔄 Versuche Verbindung neu zu starten...")
        
        await self.close_connection()
        await asyncio.sleep(2)
        
        success = await self.establish_connection()
        if success:
            await self.begin_vehicle_monitoring()

class MAVLinkConnector(DroneConnectorBase):
    """Handles MAVLink connection to simulator"""
    
    # Signals
    log_received = Signal(str)
    error_occurred = Signal(str)
    
    def __init__(self, port="simulator://"):
        super().__init__()
        self._port = port
        self._connection = None
        self._running = False
        
    async def connect_to_drone(self):
        """Connect to the drone/simulator"""
        try:
            self._log_info(f"Connecting to {self._port}...")
            
            # Create connection
            self._connection = mavutil.mavlink_connection(self._port)
            
            # Wait for connection
            self._connection.wait_heartbeat(timeout=5)
            
            # Set target system and component
            self._connection.target_system = self._connection.target_system
            self._connection.target_component = self._connection.target_component
            
            # Send initial messages
            self._send_initial_messages()
            
            self._running = True
            self._log_info("Connected successfully!")
            return True
            
        except Exception as e:
            error_msg = f"Failed to connect: {str(e)}"
            self._log_error(error_msg)
            self.error_occurred.emit(error_msg)
            return False
            
    async def disconnect_from_drone(self):
        """Disconnect from the drone/simulator"""
        try:
            if self._connection:
                self._connection.close()
                self._connection = None
            self._running = False
            self._log_info("Disconnected")
        except Exception as e:
            self._log_error(f"Error during disconnect: {str(e)}")
    
    async def start_monitoring(self):
        """Start monitoring drone data"""
        # Implement monitoring logic here
        pass
    
    def stop(self):
        """Stop the connection"""
        self._running = False
        if self._connection:
            self._connection.close()
    
    def _send_initial_messages(self):
        """Send initial MAVLink messages"""
        try:
            # Send heartbeat
            self._connection.mav.heartbeat_send(
                mavutil.mavlink.MAV_TYPE_GCS,
                mavutil.mavlink.MAV_AUTOPILOT_INVALID,
                0, 0, 0
            )
            
            # Request data stream
            self._connection.mav.request_data_stream_send(
                self._connection.target_system,
                self._connection.target_component,
                mavutil.mavlink.MAV_DATA_STREAM_ALL,
                10, 1  # 10 Hz, 1 = start
            )
            
        except Exception as e:
            self._log_error(f"Error sending initial messages: {str(e)}")
    
    def _log_info(self, message: str) -> None:
        """Log info message"""
        self.log_received.emit(f"[INFO] {message}")
    
    def _log_error(self, message: str) -> None:
        """Log error message"""
        self.log_received.emit(f"[ERROR] {message}")

def create_connector(connector_type: ConnectorType, **kwargs) -> DroneConnectorBase:
    """Factory-Funktion für Connector-Erstellung"""
    if connector_type == ConnectorType.DRONEKIT:
        connection_string = kwargs.get('connection_string', 'udp://127.0.0.1:14550')
        return DroneKitConnector(connection_string)
    elif connector_type == ConnectorType.MAVSDK:
        connection_string = kwargs.get('connection_string', 'udp://127.0.0.1:14550')
        return MAVSDKConnector(connection_string)
    elif connector_type == ConnectorType.PYMAVLINK:
        port = kwargs.get('port', 'simulator://')
        return MAVLinkConnector(port)
    else:
        raise ValueError(f"Unknown connector type: {connector_type}")
