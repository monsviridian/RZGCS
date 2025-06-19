#!/usr/bin/env python
# Telemetrie-Logger-Integration für die PreflightView
from pymavlink import mavutil
from datetime import datetime
import threading
import time

class TelemetryLoggerIntegration:
    """
    Klasse zur Integration von Telemetriedaten in den bestehenden Logger.
    Diese Klasse empfängt MAVLink-Telemetrie und leitet sie an den Logger weiter,
    damit sie in der PreflightView angezeigt wird.
    """
    
    def __init__(self, connection=None, logger=None):
        """
        Initialisiert die Telemetrie-Logger-Integration.
        
        Args:
            connection: Eine bestehende MAVLink-Verbindung (optional)
            logger: Eine Instanz der Logger-Klasse
        """
        self.connection = connection
        self.logger = logger
        self.running = False
        self.thread = None
        
        # MAVLink-Nachrichtentypen, die als Telemetrie geloggt werden sollen
        self.telemetry_types = [
            "HEARTBEAT", 
            "ATTITUDE",
            "VFR_HUD", 
            "GLOBAL_POSITION_INT",
            "SYS_STATUS",
            "GPS_RAW_INT",
            "STATUSTEXT"
        ]
        
        if self.logger:
            self.logger.addLog("[INFO] TelemetryLoggerIntegration initialisiert")
    
    def set_connection(self, connection):
        """
        Setzt die MAVLink-Verbindung für die Telemetrie.
        
        Args:
            connection: Eine MAVLink-Verbindung
        """
        self.connection = connection
        if self.logger:
            self.logger.addLog(f"[INFO] Telemetrie-Verbindung aktualisiert")
    
    def set_logger(self, logger):
        """
        Setzt den Logger für die Telemetrie.
        
        Args:
            logger: Eine Instanz der Logger-Klasse
        """
        self.logger = logger
        if self.logger:
            self.logger.addLog("[INFO] Telemetrie-Logger aktualisiert")
    
    def log_telemetry(self, message):
        """
        Fügt eine Telemetrie-Nachricht als Systeminformation zum Logger hinzu.
        
        Args:
            message: Die zu loggende Nachricht
        """
        if self.logger:
            self.logger.addSystemInfoLog(message)
    
    def process_telemetry(self):
        """
        Verarbeitet eingehende MAVLink-Telemetrie und leitet sie an den Logger weiter.
        Wird in einem separaten Thread ausgeführt.
        """
        if not self.connection:
            if self.logger:
                self.logger.addLog("[WARN] Keine MAVLink-Verbindung für Telemetrie vorhanden")
            return
            
        if self.logger:
            self.logger.addLog("[INFO] Telemetrie-Monitoring gestartet")
            
        self.running = True
        
        try:
            # Telemetriedaten fortlaufend empfangen, solange der Thread läuft
            while self.running:
                # Auf nächste Nachricht warten, aber nicht blockieren
                msg = self.connection.recv_match(blocking=False)
                if not msg:
                    time.sleep(0.1)  # Kurze Pause um CPU-Last zu reduzieren
                    continue
                    
                msg_type = msg.get_type()
                
                # Nur gewünschte Telemetrietypen verarbeiten
                if msg_type in self.telemetry_types:
                    # Verschiedene Nachrichtentypen mit spezifischen Informationen formatieren
                    if msg_type == "HEARTBEAT":
                        status_text = "STANDBY"
                        if hasattr(msg, 'system_status'):
                            if msg.system_status == 3:
                                status_text = "AKTIV"
                            elif msg.system_status == 4:
                                status_text = "KRITISCH"
                            elif msg.system_status == 5:
                                status_text = "NOTFALL"
                        self.log_telemetry(f"[HEARTBEAT] Status: {status_text}, Mode: {msg.custom_mode}")
                    
                    elif msg_type == "ATTITUDE":
                        roll = round(msg.roll * 57.2958, 1)  # Konvertierung von rad zu grad
                        pitch = round(msg.pitch * 57.2958, 1)
                        yaw = round(msg.yaw * 57.2958, 1)
                        self.log_telemetry(f"[ATTITUDE] Roll: {roll}°, Pitch: {pitch}°, Yaw: {yaw}°")
                    
                    elif msg_type == "VFR_HUD":
                        self.log_telemetry(f"[FLIGHT] Speed: {msg.airspeed:.1f}m/s, Alt: {msg.alt:.1f}m, Climb: {msg.climb:.1f}m/s")
                    
                    elif msg_type == "GLOBAL_POSITION_INT":
                        lat = msg.lat / 1e7  # Konvertierung von 1E7 Format zu Grad
                        lon = msg.lon / 1e7
                        alt = msg.alt / 1000.0  # in Meter
                        rel_alt = msg.relative_alt / 1000.0  # relative Höhe in Meter
                        self.log_telemetry(f"[GPS] Lat: {lat:.6f}, Lon: {lon:.6f}, Alt: {alt:.1f}m, Rel: {rel_alt:.1f}m")
                    
                    elif msg_type == "SYS_STATUS":
                        voltage = msg.voltage_battery / 1000.0 if hasattr(msg, 'voltage_battery') else 0  # in Volt
                        current = msg.current_battery / 100.0 if hasattr(msg, 'current_battery') else 0   # in Ampere
                        remaining = msg.battery_remaining if hasattr(msg, 'battery_remaining') else 0     # in Prozent
                        self.log_telemetry(f"[BATTERY] {voltage:.2f}V, {current:.2f}A, Verbleibend: {remaining}%")
                    
                    elif msg_type == "GPS_RAW_INT":
                        fix_type = "KEIN FIX"
                        if hasattr(msg, 'fix_type'):
                            if msg.fix_type == 2:
                                fix_type = "2D FIX"
                            elif msg.fix_type == 3:
                                fix_type = "3D FIX"
                            elif msg.fix_type >= 4:
                                fix_type = "DGPS FIX"
                        satellites = msg.satellites_visible if hasattr(msg, 'satellites_visible') else 0
                        self.log_telemetry(f"[GPS] Status: {fix_type}, Satelliten: {satellites}")
                    
                    elif msg_type == "STATUSTEXT":
                        text = msg.text if hasattr(msg, 'text') else "Keine Nachricht"
                        severity = msg.severity if hasattr(msg, 'severity') else 0
                        if severity <= 3:  # Nur wichtige Meldungen (EMERGENCY, ALERT, CRITICAL, ERROR)
                            self.log_telemetry(f"[STATUS] {text}")
                    
        except Exception as e:
            if self.logger:
                self.logger.addLog(f"[ERR] Telemetrie-Fehler: {str(e)}")
        
        if self.logger:
            self.logger.addLog("[INFO] Telemetrie-Monitoring beendet")
    
    def start(self):
        """Startet das Telemetrie-Monitoring in einem separaten Thread."""
        if self.running:
            if self.logger:
                self.logger.addLog("[INFO] Telemetrie-Monitoring läuft bereits")
            return False
            
        if not self.connection:
            if self.logger:
                self.logger.addLog("[WARN] Keine Verbindung für Telemetrie vorhanden")
            return False
            
        # Thread starten
        self.thread = threading.Thread(target=self.process_telemetry)
        self.thread.daemon = True  # Als Daemon-Thread ausführen
        self.thread.start()
        
        return True
    
    def stop(self):
        """Stoppt das Telemetrie-Monitoring."""
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2.0)  # Auf Thread-Ende warten, max. 2 Sekunden
            
        if self.logger:
            self.logger.addLog("[INFO] Telemetrie-Monitoring gestoppt")
