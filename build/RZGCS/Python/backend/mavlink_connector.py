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

def get_mavsdk_server_path() -> str:
    """Ermittelt den Pfad zum MAVSDK-Server basierend auf dem Betriebssystem"""
    # Basis-Pfad zum Projekt-Ordner
    base_path = pathlib.Path(__file__).parent.parent.parent
    mavsdk_path = base_path / "mavsdk_server"
    
    if sys.platform == "win32":
        server_path = mavsdk_path / "windows" / "mavsdk-server.exe"
    elif sys.platform == "darwin":  # macOS
        server_path = mavsdk_path / "mac" / "mavsdk-server"
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
            
            return False
            
        except Exception as e:
            self._emit_log(f"❌ MAVSDK Verbindungsfehler: {str(e)}")
            if self.debug:
                import traceback
                self._emit_log(f"🔍 Stacktrace: {traceback.format_exc()}")
            return False
        finally:
            self._is_connecting = False
            
    async def close_connection(self) -> None:
        """Trennt die MAVSDK-Verbindung"""
        self.running = False
        
        if self.debug:
            self._emit_log("🔄 Beende MAVSDK-Verbindung...")
            
        if self.mavsdk_server_process:
            try:
                self.mavsdk_server_process.terminate()
                self.mavsdk_server_process.wait(timeout=5)
                if self.debug:
                    self._emit_log("✅ MAVSDK-Server beendet")
            except Exception as e:
                self._emit_log(f"⚠️ Fehler beim Beenden des Servers: {str(e)}")
            finally:
                self.mavsdk_server_process = None
                
        if self.drone:
            try:
                await self.drone.close()
                if self.debug:
                    self._emit_log("✅ MAVSDK System geschlossen")
            except Exception as e:
                self._emit_log(f"⚠️ Fehler beim Schließen des Systems: {str(e)}")
            finally:
                self.drone = None
                
        self._emit_connection_status(False)
        self._emit_log("🛑 MAVSDK-Verbindung getrennt")
        
    async def begin_vehicle_monitoring(self) -> None:
        """Überwacht Drohnendaten via MAVSDK"""
        if not self.drone:
            self._emit_log("⚠️ Keine Verbindung zum System")
            return
            
        try:
            if self.debug:
                self._emit_log("🔄 Aktiviere Telemetrie-Streams...")
                
            # Telemetrie-Streams aktivieren
            await self.drone.telemetry.set_rate_position(10)
            await self.drone.telemetry.set_rate_attitude(10)
            await self.drone.telemetry.set_rate_battery(1)
            
            if self.debug:
                self._emit_log("✅ Telemetrie-Streams aktiviert")
            
            last_connection_check = time.time()
            
            while self.running:
                try:
                    current_time = time.time()
                    
                    # Regelmäßige Verbindungsprüfung
                    if current_time - last_connection_check > self._connection_check_interval:
                        if not self._is_connection_alive():
                            raise ConnectionError("Verbindung verloren - kein Heartbeat")
                        last_connection_check = current_time
                    
                    # Position
                    async for position in self.drone.telemetry.position():
                        self.gps_msg.emit(position.latitude_deg, position.longitude_deg)
                        if self.debug:
                            self._emit_log(f"📍 Position: {position.latitude_deg:.6f}, {position.longitude_deg:.6f}")
                        break
                    
                    # Attitude    
                    async for attitude in self.drone.telemetry.attitude_euler():
                        self.attitude_msg.emit(attitude.roll_deg, attitude.pitch_deg, attitude.yaw_deg)
                        if self.debug:
                            self._emit_log(f"🧭 Lage: Roll={attitude.roll_deg:.1f}°, Pitch={attitude.pitch_deg:.1f}°, Yaw={attitude.yaw_deg:.1f}°")
                        break
                    
                    # Battery
                    async for battery in self.drone.telemetry.battery():
                        self.sensor_data.emit("battery_voltage", battery.voltage_v)
                        if self.debug:
                            self._emit_log(f"🔋 Batterie: {battery.voltage_v:.1f}V ({battery.remaining_percent:.0f}%)")
                        break
                    
                    # Flight Mode & Connection State
                    async for flight_mode in self.drone.telemetry.flight_mode():
                        if self.debug:
                            self._emit_log(f"✈️ Flugmodus: {flight_mode}")
                        break
                        
                    # Aktualisiere Heartbeat-Zeitstempel
                    self._last_heartbeat = current_time
                    
                    await asyncio.sleep(0.1)
                    
                except ConnectionError as e:
                    self._emit_log(f"⚠️ Verbindungsfehler: {str(e)}")
                    
                    # Starte Reconnect wenn nicht schon einer läuft
                    if not self._reconnect_task:
                        self._reconnect_task = asyncio.create_task(self._restart_connection())
                    return
                    
                except Exception as e:
                    self._emit_log(f"⚠️ Fehler beim Lesen der Telemetrie: {str(e)}")
                    await asyncio.sleep(1)
                
        except Exception as e:
            self._emit_log(f"❌ MAVSDK Monitoring Fehler: {str(e)}")
            if self.debug:
                import traceback
                self._emit_log(f"🔍 Stacktrace: {traceback.format_exc()}")
            self.running = False
            
    def __del__(self):
        """Cleanup beim Zerstören der Instanz"""
        if hasattr(self, 'mavsdk_server_process') and self.mavsdk_server_process:
            try:
                self.mavsdk_server_process.terminate()
                self.mavsdk_server_process.wait(timeout=5)
            except:
                if self.debug:
                    self._emit_log("⚠️ Konnte MAVSDK-Server nicht sauber beenden")

    async def start_mavsdk_server(self) -> bool:
        """Startet den MAVSDK-Server als Subprocess"""
        try:
            # Hole den Pfad zum MAVSDK-Server
            server_path = get_mavsdk_server_path()
            if self.debug:
                self._emit_log(f"📂 MAVSDK-Server Pfad: {server_path}")
            
            # Starte Server mit UDP Port
            cmd = [server_path, "-p", "50051"]
            
            # Füge die Verbindungs-URL hinzu, wenn es sich um eine serielle Verbindung handelt
            if self.connection_string.startswith("serial://"):
                cmd.append(self.connection_string)
                if self.debug:
                    self._emit_log(f"🔌 Verbindungs-URL: {self.connection_string}")
            
            self._emit_log("🚀 Starte MAVSDK-Server...")
            if self.debug:
                self._emit_log(f"📋 Befehl: {' '.join(cmd)}")
            
            # Starte den Server
            self.mavsdk_server_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,  # Line-buffered
                universal_newlines=True
            )
            
            # Warte kurz damit der Server starten kann
            await asyncio.sleep(2)
            
            # Prüfe ob der Server läuft
            if self.mavsdk_server_process.poll() is None:
                self._emit_log("✅ MAVSDK-Server gestartet")
                
                # Debug-Ausgabe der Server-Ausgabe
                if self.debug:
                    asyncio.create_task(self._monitor_server_output())
                    
                return True
            else:
                # Hole Fehlerausgabe
                stdout, stderr = self.mavsdk_server_process.communicate()
                error_msg = stderr.strip() if stderr else "Unbekannter Fehler"
                self._emit_log(f"❌ MAVSDK-Server konnte nicht gestartet werden: {error_msg}")
                if stdout and self.debug:
                    self._emit_log(f"📤 Server stdout: {stdout.strip()}")
                if stderr and self.debug:
                    self._emit_log(f"⚠️ Server stderr: {stderr.strip()}")
                return False
                
        except Exception as e:
            self._emit_log(f"❌ MAVSDK-Server Fehler: {str(e)}")
            if self.debug:
                import traceback
                self._emit_log(f"🔍 Stacktrace: {traceback.format_exc()}")
            return False
            
    async def _monitor_server_output(self):
        """Überwacht die Ausgabe des MAVSDK-Servers"""
        try:
            while self.mavsdk_server_process and self.mavsdk_server_process.poll() is None:
                # Lese stdout
                line = self.mavsdk_server_process.stdout.readline()
                if line:
                    self._emit_log(f"🔧 Server: {line.strip()}")
                
                # Lese stderr
                error = self.mavsdk_server_process.stderr.readline()
                if error:
                    self._emit_log(f"⚠️ Server Error: {error.strip()}")
                
                await asyncio.sleep(0.1)
                
            # Wenn der Server beendet wurde
            if self.mavsdk_server_process:
                return_code = self.mavsdk_server_process.poll()
                if return_code is not None:
                    self._emit_log(f"⚠️ MAVSDK-Server beendet mit Code: {return_code}")
                    
        except Exception as e:
            self._emit_log(f"❌ Fehler beim Überwachen der Server-Ausgabe: {str(e)}")
            if self.debug:
                import traceback
                self._emit_log(f"🔍 Stacktrace: {traceback.format_exc()}")
                
    def _is_connection_alive(self) -> bool:
        """
        Prüft ob die Verbindung noch aktiv ist.
        Returns:
            bool: True wenn die Verbindung aktiv ist, False sonst
        """
        if not self.drone:
            return False
            
        try:
            # Prüfe Zeitstempel des letzten Heartbeats
            if time.time() - self._last_heartbeat > self._heartbeat_timeout:
                return False
            return True
        except Exception:
            return False
            
    async def _restart_connection(self):
        """Versucht die Verbindung wiederherzustellen"""
        self._emit_log("🔄 Versuche Verbindung wiederherzustellen...")
        
        try:
            # Stoppe altes Monitoring
            self.running = False
            await self.disconnect_from_drone()
            
            # Warte kurz
            await asyncio.sleep(1)
            
            # Versuche neue Verbindung
            if await self.connect_to_drone():
                self._emit_log("✅ Verbindung wiederhergestellt")
                await self.begin_vehicle_monitoring()
            else:
                self._emit_log("❌ Wiederverbindung fehlgeschlagen")
                
        except Exception as e:
            self._emit_log(f"❌ Fehler beim Wiederverbinden: {str(e)}")
        finally:
            self._reconnect_task = None

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
            
    def _send_initial_messages(self):
        """Send initial messages to simulator"""
        try:
            # Send heartbeat
            self._connection.mav.heartbeat_send(
                mavutil.mavlink.MAV_TYPE_GCS,
                mavutil.mavlink.MAV_AUTOPILOT_INVALID,
                0,  # base mode
                0,  # custom mode
                mavutil.mavlink.MAV_STATE_ACTIVE
            )
            
            # Send initial parameters
            self._connection.mav.param_value_send(
                "SIM_ENABLE", 1.0, mavutil.mavlink.MAV_PARAM_TYPE_REAL32, 1, 0
            )
            
            # Request data streams
            self._connection.mav.request_data_stream_send(
                self._connection.target_system,
                self._connection.target_component,
                mavutil.mavlink.MAV_DATA_STREAM_ALL,
                10,  # 10 Hz
                1    # Enable
            )
            
            self._log_info("Initial messages sent")
        except Exception as e:
            self._log_error(f"Error sending initial messages: {str(e)}")
            
    def _log_info(self, message: str) -> None:
        """Log an info message"""
        print(f"[MAVLinkConnector] {message}")
        self.log_received.emit(message)
        
    def _log_error(self, message: str) -> None:
        """Log an error message"""
        print(f"[MAVLinkConnector] ❌ {message}")
        self.log_received.emit(f"❌ {message}")
        
    def stop(self):
        """Stop the connection"""
        self._running = False
        if self._connection:
            try:
                self._connection.close()
            except:
                pass
            self._connection = None

def create_connector(connector_type: ConnectorType, **kwargs) -> DroneConnectorBase:
    """Factory-Methode für Connector-Erstellung"""
    try:
        if connector_type == ConnectorType.MAVSDK:
            if 'connection_string' not in kwargs:
                raise ValueError("connection_string ist erforderlich für MAVSDK")
            return MAVSDKConnector(kwargs['connection_string'])
        else:  # PYMAVLINK
            if 'port' not in kwargs or 'baudrate' not in kwargs:
                raise ValueError("port und baudrate sind erforderlich für MAVLink")
            return MAVLinkConnector(kwargs['port'], kwargs['baudrate'])
    except Exception as e:
        print(f"Fehler beim Erstellen des Connectors: {str(e)}")
        raise
