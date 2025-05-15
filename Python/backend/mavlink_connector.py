# backend/mavlink_connector.py

import threading, time, subprocess, sys, os
from PySide6.QtCore import QObject, Signal, QTimer
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
import asyncio
from enum import Enum
import pathlib
from pymavlink import mavutil
from pymavlink.dialects.v20 import ardupilotmega as mavlink
import serial
import math

from .mavlink_protocol import MAVLinkProtocol
from .drone_connector_base import DroneConnectorBase

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

class MAVLinkConnector(QObject):
    """
    Implementiert die MAVLink-Verbindung zur Drohne.
    Basierend auf QGroundControl's MAVLink-Implementierung.
    """
    
    # Signals
    log_received = Signal(str)
    gps_msg = Signal(float, float)  # lat, lon
    attitude_msg = Signal(float, float, float)  # roll, pitch, yaw
    sensor_data = Signal(str, float)  # sensor name, value
    connection_status = Signal(bool)  # connected status
    
    def __init__(self, port: str, baudrate: int):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.mavlink_connection = None
        self.connected = False
        self.message_timer = QTimer()
        self.message_timer.setInterval(100)  # 100ms interval for message processing
        self.message_timer.timeout.connect(self._process_messages)
        
        # Log throttling
        self._last_log_time = {}
        self._log_throttle_interval = 1.0  # Reduced to 1 second for more frequent updates
        
        # Message filtering - reduced list of ignored messages
        self._ignored_messages = {
            "TIMESYNC", "SERVO_OUTPUT_RAW", "RC_CHANNELS",
            "RAW_IMU", "SCALED_IMU2", "MEMINFO"
        }
        
    def _log_info(self, message: str) -> None:
        """Loggt eine Informationsnachricht."""
        print(f"[MAVLinkConnector] {message}")
        self.log_received.emit(message)
        
    def _log_error(self, message: str) -> None:
        """Loggt eine Fehlernachricht."""
        print(f"[MAVLinkConnector] ❌ {message}")
        self.log_received.emit(f"❌ {message}")
        
    def connect_to_drone(self) -> bool:
        """Stellt die Verbindung zur Drohne her."""
        try:
            self._log_info(f"🔄 Verbinde mit {self.port} @ {self.baudrate}")
            self.mavlink_connection = mavutil.mavlink_connection(
                self.port,
                baud=self.baudrate,
                source_system=255,
                source_component=0,
                dialect='ardupilotmega'
            )
            
            # Warte auf Heartbeat
            self._log_info("⏳ Warte auf Heartbeat...")
            msg = self.mavlink_connection.wait_heartbeat(timeout=10.0)
            if msg:
                self._log_info(f"✅ Verbunden mit System {msg.get_srcSystem()}")
                self.connected = True
                self.connection_status.emit(True)
                self.message_timer.start()
                self._request_data_streams()
                return True
            else:
                self._log_error("❌ Kein Heartbeat empfangen")
                return False
                
        except Exception as e:
            self._log_error(f"❌ Verbindungsfehler: {str(e)}")
            self.connected = False
            self.connection_status.emit(False)
            return False
            
    def _request_data_streams(self) -> None:
        """Fordert die benötigten Datenströme an."""
        try:
            # Request all data streams
            self.mavlink_connection.mav.request_data_stream_send(
                self.mavlink_connection.target_system,
                self.mavlink_connection.target_component,
                mavlink.MAV_DATA_STREAM_ALL,
                10,  # 10 Hz
                1    # Start
            )
            self._log_info("📡 Data streams requested")
        except Exception as e:
            self._log_error(f"❌ Error requesting data streams: {str(e)}")
            
    def _should_throttle(self, message_type: str) -> bool:
        """Check if a message type should be throttled."""
        current_time = time.time()
        if message_type in self._last_log_time:
            time_diff = current_time - self._last_log_time[message_type]
            if time_diff < self._log_throttle_interval:
                return True
        self._last_log_time[message_type] = current_time
        return False
        
    def _process_messages(self) -> None:
        """Verarbeitet eingehende MAVLink-Nachrichten."""
        if not self.connected or not self.mavlink_connection:
            return
            
        try:
            while True:
                msg = self.mavlink_connection.recv_match(blocking=False)
                if not msg:
                    break
                    
                msg_type = msg.get_type()
                
                # Ignore certain message types completely
                if msg_type in self._ignored_messages:
                    continue
                    
                # Process important messages
                if msg_type == "GLOBAL_POSITION_INT":
                    self._handle_global_position_int(msg)
                elif msg_type == "ATTITUDE":
                    self._handle_attitude(msg)
                elif msg_type == "SYS_STATUS":
                    self._handle_sys_status(msg)
                elif msg_type == "VFR_HUD":
                    self._handle_vfr_hud(msg)
                elif msg_type == "HEARTBEAT":
                    self._handle_heartbeat(msg)
                elif msg_type == "STATUSTEXT":
                    self._handle_statustext(msg)
                    
        except Exception as e:
            self._log_error(f"Error processing messages: {str(e)}")
            
    def _handle_global_position_int(self, message) -> None:
        """Handles global position updates."""
        try:
            # Convert to degrees
            lat = message.lat / 1e7
            lon = message.lon / 1e7
            alt = message.alt / 1000.0  # Convert to meters
            relative_alt = message.relative_alt / 1000.0  # Convert to meters
            
            # Check if GPS is valid (using altitude as indicator)
            has_fix = alt != 0.0
            
            # Log GPS status changes
            if not hasattr(self, '_last_gps_status') or self._last_gps_status != has_fix:
                self._last_gps_status = has_fix
                status = "GPS Fix" if has_fix else "No GPS Fix"
                self._log_info(f"GPS Status: {status}")
            
            # Log position changes more frequently
            if not hasattr(self, '_last_position') or \
               abs(self._last_position[2] - relative_alt) > 5:  # Reduced threshold to 5m
                self._last_position = (lat, lon, relative_alt)
                self._log_info(f"Position: {lat:.6f}, {lon:.6f}, Alt: {relative_alt:.1f}m")
            
            # Always emit GPS data for sensor updates
            self.gps_msg.emit(lat, lon)
            self.sensor_data.emit("altitude", relative_alt)
            
        except Exception as e:
            self._log_error(f"Error processing GPS data: {str(e)}")
            
    def _handle_attitude(self, message) -> None:
        """Handles attitude updates."""
        try:
            # Convert to degrees
            roll = math.degrees(message.roll)
            pitch = math.degrees(message.pitch)
            yaw = math.degrees(message.yaw)
            
            # Only log significant attitude changes (>5 degrees)
            if not hasattr(self, '_last_attitude') or \
               abs(self._last_attitude[0] - roll) > 5 or \
               abs(self._last_attitude[1] - pitch) > 5 or \
               abs(self._last_attitude[2] - yaw) > 5:
                self._last_attitude = (roll, pitch, yaw)
                if not self._should_throttle("ATTITUDE"):
                    self._log_info(f"Attitude: Roll={roll:.1f}°, Pitch={pitch:.1f}°, Yaw={yaw:.1f}°")
            
            # Always emit attitude for sensor updates
            self.attitude_msg.emit(roll, pitch, yaw)
            
        except Exception as e:
            self._log_error(f"Error processing attitude: {str(e)}")
            
    def _handle_sys_status(self, message) -> None:
        """Handles system status updates."""
        try:
            voltage = message.voltage_battery / 1000.0
            current = message.current_battery / 100.0
            remaining = message.battery_remaining
            
            # Log battery changes more frequently
            if not hasattr(self, '_last_battery') or abs(self._last_battery - remaining) > 2:  # Reduced threshold to 2%
                self._last_battery = remaining
                self._log_info(f"Battery: {voltage:.1f}V, {current:.1f}A, {remaining}%")
            
            # Always emit battery for sensor updates
            self.sensor_data.emit("battery_voltage", voltage)
            self.sensor_data.emit("battery_current", current)
            self.sensor_data.emit("battery_remaining", remaining)
            
        except Exception as e:
            self._log_error(f"Error processing system status: {str(e)}")
            
    def _handle_vfr_hud(self, message) -> None:
        """Handles VFR HUD updates."""
        try:
            # Log changes more frequently
            if not hasattr(self, '_last_vfr') or \
               abs(self._last_vfr[0] - message.alt) > 2 or \
               abs(self._last_vfr[1] - message.groundspeed) > 0.5:  # Reduced threshold to 0.5m/s
                self._last_vfr = (message.alt, message.groundspeed)
                self._log_info(f"VFR: Alt={message.alt:.1f}m, Speed={message.groundspeed:.1f}m/s")
            
            # Always emit VFR data for sensor updates
            self.sensor_data.emit("airspeed", message.airspeed)
            self.sensor_data.emit("groundspeed", message.groundspeed)
            self.sensor_data.emit("heading", message.heading)
            self.sensor_data.emit("throttle", message.throttle)
            self.sensor_data.emit("altitude", message.alt)
            self.sensor_data.emit("climb", message.climb)
            
        except Exception as e:
            self._log_error(f"Error processing VFR HUD: {str(e)}")
            
    def _handle_heartbeat(self, message) -> None:
        """Handles heartbeat messages."""
        try:
            # Log mode changes
            if not hasattr(self, '_last_mode') or self._last_mode != message.custom_mode:
                self._last_mode = message.custom_mode
                mode = mavutil.mode_string_v10(message)
                self._log_info(f"Flight Mode: {mode}")
            
            # Always emit mode for sensor updates
            self.sensor_data.emit("flight_mode", message.custom_mode)
            
        except Exception as e:
            self._log_error(f"Error processing heartbeat: {str(e)}")
            
    def _handle_statustext(self, message) -> None:
        """Handles status text messages."""
        try:
            # Log more status messages
            if message.severity <= 5:  # Now includes WARNING level
                severity = ["EMERGENCY", "ALERT", "CRITICAL", "ERROR", "WARNING", "NOTICE"][message.severity]
                self._log_info(f"[{severity}] {message.text}")
            
        except Exception as e:
            self._log_error(f"Error processing status text: {str(e)}")
            
    def stop(self) -> None:
        """Beendet die Verbindung."""
        if self.message_timer.isActive():
            self.message_timer.stop()
            
        if self.mavlink_connection:
            try:
                self.mavlink_connection.close()
            except:
                pass
            self.mavlink_connection = None
            
        self.connected = False
        self.connection_status.emit(False)
        self._log_info("🛑 Connection terminated")

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
