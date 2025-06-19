#!/usr/bin/env python3
"""
MAVSDK Connection Helper - Hilfsmethoden für die Verbindung mit der Drohne
"""

import asyncio
import threading
import time
from typing import Callable, Dict, List, Any, Optional

from mavsdk import System
from mavsdk.telemetry import FlightMode, LandedState

from backend.logger import Logger
from backend.exceptions import ConnectionError, ConnectionTimeoutError


class MAVSDKConnectionHelper:
    """Helper-Klasse für die MAVSDK-Verbindung und Telemetrie-Abonnements"""
    
    @staticmethod
    async def connect_to_drone(drone: System, connection_string: str, timeout_seconds: int = 30) -> bool:
        """
        Stellt eine Verbindung zur Drohne her
        Unterstützt verschiedene Verbindungsformate:
        - COM-Port mit Baudrate: "COM3:115200"
        - COM-Port ohne Baudrate: "COM3" (nutzt Standard-Baudrate 115200)
        - UDP: "udp://:14540"
        - TCP: "tcp://192.168.1.1:5760"
        """
        # Baudrate extrahieren, falls im Format "COM3:115200"
        connection_url = connection_string
        baudrate = 115200  # Standardwert
        
        # COM-Port mit Baudrate (z.B. "COM3:115200")
        if ":" in connection_string and not connection_string.startswith(("udp:", "tcp:")):
            try:
                port, baudrate_str = connection_string.split(":", 1)
                baudrate = int(baudrate_str)
                # Format für MAVSDK: serial://COM3:115200
                connection_url = f"serial://{port}:{baudrate}"
            except (ValueError, TypeError):
                # Bei ungültigem Format Original-String verwenden
                connection_url = f"serial://{connection_string}"
        
        # COM-Port ohne Baudrate (einfach nur "COM3")
        elif connection_string.startswith("COM"):
            connection_url = f"serial://{connection_string}:{baudrate}"
        
        # Verbindung herstellen
        print(f"[DEBUG] Verbinde mit: {connection_url}")
        await drone.connect(connection_url)
        
        # Auf Verbindung warten
        start_time = time.time()
        while not drone.is_connected:
            if time.time() - start_time > timeout_seconds:
                raise ConnectionTimeoutError(f"Timeout bei Verbindungsaufbau zu {connection_string}")
            await asyncio.sleep(0.1)
        
        return True
    
    @staticmethod
    async def subscribe_to_telemetry(drone: System, logger: Logger) -> None:
        """Abonniert alle Telemetrie-Streams der Drohne"""
        try:
            # System-Status abonnieren
            await drone.telemetry.armed_subscribe(lambda armed: None)
            await drone.telemetry.flight_mode_subscribe(lambda flight_mode: None)
            
            # Position abonnieren
            await drone.telemetry.position_subscribe(lambda position: None)
            await drone.telemetry.home_subscribe(lambda home: None)
            
            # Attitude abonnieren
            await drone.telemetry.attitude_euler_subscribe(lambda attitude: None)
            
            # Batterie abonnieren
            await drone.telemetry.battery_subscribe(lambda battery: None)
            
            # GPS-Informationen abonnieren
            await drone.telemetry.gps_info_subscribe(lambda gps_info: None)
            
            # Länder-Status abonnieren
            await drone.telemetry.landed_state_subscribe(lambda landed_state: None)
            
            # Status-Texte abonnieren
            await drone.telemetry.status_text_subscribe(lambda status_text: None)
            
        except Exception as e:
            logger.addLog(f"[ERROR] Fehler beim Abonnieren der Telemetrie: {str(e)}")
            raise
    
    @staticmethod
    async def update_telemetry_loop(drone: System, 
                                    logger: Logger, 
                                    is_connected: bool, 
                                    stop_event: threading.Event,
                                    signal_handlers: Dict[str, Callable],
                                    telemetry_callbacks: Dict[str, List[Callable]],
                                    statustext_callbacks: List[Callable],
                                    message_filter: Dict[str, float],
                                    message_interval: Dict[str, float]) -> None:
        """
        Haupt-Telemetrie-Loop, der regelmäßig Telemetrie-Updates abruft und verarbeitet
        """
        # Letzte Werte und Zeitstempel für die Nachrichtenfilterung
        last_values = {}
        last_times = {}
        
        # Solange keine Stoppanforderung vorliegt
        while not stop_event.is_set() and is_connected:
            try:
                # System-Status abfragen
                armed = await drone.telemetry.armed()
                flight_mode = await drone.telemetry.flight_mode()
                
                # Prüfen, ob sich der Armed-Status geändert hat oder ob das Mindestintervall vergangen ist
                if MAVSDKConnectionHelper._should_emit_update('armed', armed, last_values, last_times, 
                                                            message_filter, message_interval):
                    # Signal emittieren
                    signal_handlers.get('armed_changed', lambda x: None)(armed)
                    
                    # Callbacks aufrufen
                    for callback in telemetry_callbacks.get('armed', []):
                        try:
                            callback(armed)
                        except Exception as e:
                            logger.addLog(f"[ERROR] Fehler im Armed-Callback: {str(e)}")
                    
                    # Wert und Zeit aktualisieren
                    last_values['armed'] = armed
                    last_times['armed'] = time.time()
                
                # Prüfen, ob sich der Flugmodus geändert hat oder ob das Mindestintervall vergangen ist
                if MAVSDKConnectionHelper._should_emit_update('flight_mode', str(flight_mode), last_values, last_times, 
                                                            message_filter, message_interval):
                    # Signal emittieren
                    signal_handlers.get('flight_mode_changed', lambda x: None)(str(flight_mode))
                    
                    # Callbacks aufrufen
                    for callback in telemetry_callbacks.get('flight_mode', []):
                        try:
                            callback(str(flight_mode))
                        except Exception as e:
                            logger.addLog(f"[ERROR] Fehler im Flight-Mode-Callback: {str(e)}")
                    
                    # Wert und Zeit aktualisieren
                    last_values['flight_mode'] = str(flight_mode)
                    last_times['flight_mode'] = time.time()
                
                # Position abfragen
                position = await drone.telemetry.position()
                home = await drone.telemetry.home()
                
                # Position-Update verarbeiten
                position_dict = {
                    'latitude_deg': position.latitude_deg,
                    'longitude_deg': position.longitude_deg,
                    'absolute_altitude_m': position.absolute_altitude_m,
                    'relative_altitude_m': position.relative_altitude_m
                }
                
                # Prüfen, ob sich die Höhe signifikant geändert hat oder ob das Mindestintervall vergangen ist
                if MAVSDKConnectionHelper._should_emit_update('altitude', position.relative_altitude_m, last_values, last_times, 
                                                            message_filter, message_interval):
                    # Signal emittieren
                    signal_handlers.get('position_changed', lambda x: None)(position_dict)
                    
                    # Callbacks aufrufen
                    for callback in telemetry_callbacks.get('position', []):
                        try:
                            callback(position_dict)
                        except Exception as e:
                            logger.addLog(f"[ERROR] Fehler im Position-Callback: {str(e)}")
                    
                    # Wert und Zeit aktualisieren
                    last_values['altitude'] = position.relative_altitude_m
                    last_times['altitude'] = time.time()
                
                # Home-Position verarbeiten
                home_dict = {
                    'latitude_deg': home.latitude_deg,
                    'longitude_deg': home.longitude_deg,
                    'absolute_altitude_m': home.absolute_altitude_m,
                    'relative_altitude_m': 0.0  # Home hat keine relative Höhe
                }
                
                # Home-Position-Update immer senden, da selten
                signal_handlers.get('home_position_changed', lambda x: None)(home_dict)
                
                # Callbacks aufrufen
                for callback in telemetry_callbacks.get('home_position', []):
                    try:
                        callback(home_dict)
                    except Exception as e:
                        logger.addLog(f"[ERROR] Fehler im Home-Position-Callback: {str(e)}")
                
                # Attitude abfragen
                attitude = await drone.telemetry.attitude_euler()
                
                # Attitude-Update verarbeiten
                attitude_dict = {
                    'roll_deg': attitude.roll_deg,
                    'pitch_deg': attitude.pitch_deg,
                    'yaw_deg': attitude.yaw_deg
                }
                
                # Prüfen, ob sich der Heading signifikant geändert hat oder ob das Mindestintervall vergangen ist
                if MAVSDKConnectionHelper._should_emit_update('heading', attitude.yaw_deg, last_values, last_times, 
                                                            message_filter, message_interval):
                    # Signal emittieren
                    signal_handlers.get('attitude_changed', lambda x: None)(attitude_dict)
                    signal_handlers.get('heading_changed', lambda x: None)(attitude.yaw_deg)
                    
                    # Callbacks aufrufen
                    for callback in telemetry_callbacks.get('attitude', []):
                        try:
                            callback(attitude_dict)
                        except Exception as e:
                            logger.addLog(f"[ERROR] Fehler im Attitude-Callback: {str(e)}")
                    
                    for callback in telemetry_callbacks.get('heading', []):
                        try:
                            callback(attitude.yaw_deg)
                        except Exception as e:
                            logger.addLog(f"[ERROR] Fehler im Heading-Callback: {str(e)}")
                    
                    # Wert und Zeit aktualisieren
                    last_values['heading'] = attitude.yaw_deg
                    last_times['heading'] = time.time()
                
                # Batterie abfragen
                battery = await drone.telemetry.battery()
                
                # Batterie-Update verarbeiten
                battery_dict = {
                    'remaining_percent': battery.remaining_percent,
                    'voltage_v': battery.voltage_v,
                    'current_a': battery.current_a if hasattr(battery, 'current_a') else 0.0
                }
                
                # Prüfen, ob sich der Batteriestand signifikant geändert hat oder ob das Mindestintervall vergangen ist
                if MAVSDKConnectionHelper._should_emit_update('battery', battery.remaining_percent, last_values, last_times, 
                                                            message_filter, message_interval):
                    # Signal emittieren
                    signal_handlers.get('battery_changed', lambda x: None)(battery_dict)
                    
                    # Callbacks aufrufen
                    for callback in telemetry_callbacks.get('battery', []):
                        try:
                            callback(battery_dict)
                        except Exception as e:
                            logger.addLog(f"[ERROR] Fehler im Battery-Callback: {str(e)}")
                    
                    # Wert und Zeit aktualisieren
                    last_values['battery'] = battery.remaining_percent
                    last_times['battery'] = time.time()
                
                # GPS-Informationen abfragen
                gps_info = await drone.telemetry.gps_info()
                
                # GPS-Update verarbeiten
                gps_dict = {
                    'num_satellites': gps_info.num_satellites,
                    'fix_type': gps_info.fix_type
                }
                
                # Prüfen, ob sich der GPS-Status geändert hat oder ob das Mindestintervall vergangen ist
                if MAVSDKConnectionHelper._should_emit_update('gps', gps_info.fix_type, last_values, last_times, 
                                                            message_filter, message_interval):
                    # Signal emittieren
                    signal_handlers.get('gps_info_changed', lambda x: None)(gps_dict)
                    
                    # Callbacks aufrufen
                    for callback in telemetry_callbacks.get('gps_info', []):
                        try:
                            callback(gps_dict)
                        except Exception as e:
                            logger.addLog(f"[ERROR] Fehler im GPS-Info-Callback: {str(e)}")
                    
                    # Wert und Zeit aktualisieren
                    last_values['gps'] = gps_info.fix_type
                    last_times['gps'] = time.time()
                
                # Status-Texte abfragen (falls implementiert)
                try:
                    status_text = await drone.telemetry.status_text()
                    
                    # Status-Text-Update verarbeiten
                    if status_text and status_text.text:
                        # Status-Texte werden immer gesendet, unabhängig vom Filter
                        # Signal emittieren
                        signal_handlers.get('statustext_received', lambda x: None)(status_text.text)
                        
                        # Callbacks aufrufen
                        for callback in statustext_callbacks:
                            try:
                                callback(status_text.text)
                            except Exception as e:
                                logger.addLog(f"[ERROR] Fehler im Status-Text-Callback: {str(e)}")
                except:
                    # Status-Text-API könnte nicht verfügbar sein, ignorieren
                    pass
                
                # Kurz warten, um CPU-Last zu reduzieren
                await asyncio.sleep(0.1)
            
            except Exception as e:
                logger.addLog(f"[ERROR] Fehler im Telemetrie-Loop: {str(e)}")
                await asyncio.sleep(1.0)  # Bei Fehler länger warten
    
    @staticmethod
    def _should_emit_update(key: str, 
                           value: Any, 
                           last_values: Dict[str, Any], 
                           last_times: Dict[str, float], 
                           thresholds: Dict[str, float],
                           min_intervals: Dict[str, float]) -> bool:
        """
        Prüft, ob ein Update emittiert werden soll, basierend auf:
        1. Ob sich der Wert signifikant geändert hat (Schwellenwert)
        2. Ob genügend Zeit seit dem letzten Update vergangen ist (Mindestintervall)
        """
        # Wenn der Wert noch nie gesendet wurde, immer senden
        if key not in last_values or key not in last_times:
            return True
        
        # Aktueller Zeitstempel
        now = time.time()
        
        # Prüfen, ob das Mindestintervall vergangen ist
        time_passed = now - last_times.get(key, 0)
        min_interval = min_intervals.get(key, 0.0)
        
        if time_passed < min_interval:
            return False  # Mindestintervall noch nicht vergangen
        
        # Prüfen, ob der Wert sich signifikant geändert hat
        old_value = last_values.get(key)
        threshold = thresholds.get(key, 0.0)
        
        # Bei numerischen Werten den absoluten Unterschied vergleichen
        if isinstance(value, (int, float)) and isinstance(old_value, (int, float)):
            if abs(value - old_value) >= threshold:
                return True  # Schwellenwert überschritten
        # Bei nicht-numerischen Werten jede Änderung als signifikant betrachten
        elif value != old_value:
            return True
        
        # Bei sehr langem Intervall ohne Update trotzdem ein Update senden (z.B. alle 10 Sekunden)
        if time_passed > 10.0:
            return True
        
        # Sonst kein Update senden
        return False
