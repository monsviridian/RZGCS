"""
MAVSDK-Server Controller
Verwaltet den Start und Stopp des MAVSDK-Servers im Hintergrund
"""

import os
import sys
import subprocess
import time
import signal
import socket
import psutil
import random
from pathlib import Path
from typing import Optional, Tuple

class MAVSDKServerController:
    """Verwaltet den MAVSDK-Server für serielle Verbindungen"""
    
    def __init__(self, logger=None):
        """Initialisiert den MAVSDK-Server Controller
        
        Args:
            logger: Optional, Logger-Instanz für die Protokollierung
        """
        self._logger = logger
        self._process = None
        self._port = None
        self._server_path = self._find_server_executable()
        
        # Port-Bereich für MAVSDK-Server
        self._port_range_start = 50051  # Standard-MAVSDK-Server-Port
        self._port_range_end = 50060    # 10 Ports im Bereich
        
        # Aktive Instanzen verfolgen
        self._all_server_processes = []
        
    def _find_server_executable(self) -> str:
        """Findet den Pfad zur MAVSDK-Server-Ausführungsdatei
        
        Returns:
            str: Pfad zur MAVSDK-Server-Ausführungsdatei
        """
        # Basisverzeichnis des Projekts ermitteln
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        project_dir = os.path.abspath(os.path.join(script_dir, ".."))
        
        # Prüfe verschiedene mögliche Pfade
        possible_paths = [
            os.path.join(project_dir, "mavsdk_server", "windows", "mavsdk-server.exe"),
            os.path.join(project_dir, "mavsdkserver", "windows", "mavsdk_server_bin.exe"),
            # Weitere mögliche Pfade
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                if self._logger:
                    self._logger.addLog(f"[INFO] MAVSDK-Server gefunden: {path}")
                return path
        
        error_msg = "MAVSDK-Server-Ausführungsdatei nicht gefunden!"
        if self._logger:
            self._logger.addLog(f"[FEHLER] {error_msg}")
        raise FileNotFoundError(error_msg)
        
    def _is_port_available(self, port: int) -> bool:
        """Prüft, ob ein bestimmter Port verfügbar ist
        
        Args:
            port: Zu prüfender Port
            
        Returns:
            bool: True, wenn der Port verfügbar ist, sonst False
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            # Versuche, den Socket an den Port zu binden
            sock.bind(("127.0.0.1", port))
            available = True
        except socket.error:
            available = False
        finally:
            sock.close()
        return available
    
    def _find_available_port(self) -> int:
        """Findet einen verfügbaren Port im konfigurierten Bereich
        
        Returns:
            int: Verfügbarer Port oder None, wenn kein Port verfügbar ist
        """
        # Zuerst versuchen wir den Standard-Port
        if self._is_port_available(self._port_range_start):
            return self._port_range_start
            
        # Dann durchsuchen wir den konfigurierten Bereich
        for port in range(self._port_range_start + 1, self._port_range_end + 1):
            if self._is_port_available(port):
                return port
                
        # Als letztes versuchen wir einen zufälligen Port außerhalb des Bereichs
        random_port = random.randint(50100, 50200)
        if self._is_port_available(random_port):
            return random_port
            
        # Kein Port verfügbar
        return None
    
    def _kill_existing_mavsdk_servers(self):
        """Findet und beendet alle laufenden MAVSDK-Server-Prozesse"""
        count = 0
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                # Suche nach Prozessen mit 'mavsdk' im Namen oder in den Kommandozeilenargumenten
                if proc.info['name'] and 'mavsdk' in proc.info['name'].lower():
                    proc.terminate()
                    count += 1
                elif proc.info['cmdline']:
                    cmd = ' '.join(proc.info['cmdline']).lower()
                    if 'mavsdk-server' in cmd:
                        proc.terminate()
                        count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        if count > 0 and self._logger:
            self._logger.addLog(f"[INFO] {count} bestehende MAVSDK-Server-Prozesse beendet")
            
        # Kurz warten, damit die Prozesse Zeit haben, sich zu beenden
        time.sleep(0.5)
    
    def start_server(self, port: str, baudrate: int = 115200) -> Tuple[bool, Optional[int]]:
        """Startet den MAVSDK-Server im Hintergrund
        
        Args:
            port: COM-Port (z.B. 'COM3')
            baudrate: Baudrate (z.B. 115200, Standard ist 115200)
            
        Returns:
            Tuple[bool, Optional[int]]: (Erfolg, verwendeter Port) oder (False, None) bei Fehler
        """
        # Bestehende Prozessinstanz stoppen, falls vorhanden
        if self._process and self._process.poll() is None:
            if self._logger:
                self._logger.addLog("[INFO] MAVSDK-Server läuft bereits, wird neu gestartet")
            self.stop_server()
        
        # Versuche, alte MAVSDK-Server-Prozesse zu beenden, die möglicherweise noch laufen
        self._kill_existing_mavsdk_servers()
        
        # Formatiere den seriellen Port für den MAVSDK-Server
        # Windows: COMx wird zu serial:///COMx:baudrate
        serial_url = f"serial:///{port}:{baudrate}"
        
        # Finde einen verfügbaren Port
        available_port = self._find_available_port()
        if not available_port:
            error_msg = "Kein verfügbarer Port für den MAVSDK-Server gefunden!"
            if self._logger:
                self._logger.addLog(f"[FEHLER] {error_msg}")
            return False, None
        
        # Speichere den Port für spätere Verwendung
        self._port = available_port
        
        # Starte den MAVSDK-Server mit dem korrekten seriellen Port, Baudrate und verfügbarem Port
        try:
            if self._logger:
                self._logger.addLog(f"[INFO] Starte MAVSDK-Server für {serial_url} auf Port {available_port}")
            
            # Verwende subprocess.PIPE für stdout/stderr, um den Prozess im Hintergrund laufen zu lassen
            self._process = subprocess.Popen(
                [self._server_path, "-p", str(available_port), serial_url],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW  # Kein Konsolenfenster anzeigen
            )
            
            # Füge diesen Prozess zu den bekannten Instanzen hinzu
            self._all_server_processes.append(self._process)
            
            # Kurz warten, um zu prüfen, ob der Prozess gestartet wurde
            time.sleep(1.0)
            if self._process.poll() is not None:
                # Prozess wurde bereits beendet
                stdout, stderr = self._process.communicate()
                error_msg = f"MAVSDK-Server konnte nicht gestartet werden: {stderr}"
                if self._logger:
                    self._logger.addLog(f"[FEHLER] {error_msg}")
                return False, None
            
            if self._logger:
                self._logger.addLog(f"[INFO] MAVSDK-Server erfolgreich gestartet auf Port {available_port}")
            return True, available_port
            
        except Exception as e:
            if self._logger:
                self._logger.addLog(f"[FEHLER] Fehler beim Starten des MAVSDK-Servers: {str(e)}")
            return False, None
    
    def stop_server(self) -> bool:
        """Stoppt den MAVSDK-Server
        
        Returns:
            bool: True, wenn der Server erfolgreich gestoppt wurde
        """
        if not self._process:
            return True
        
        try:
            if self._process.poll() is None:
                # Prozess läuft noch, beenden
                if self._logger:
                    self._logger.addLog("[INFO] Stoppe MAVSDK-Server")
                
                # Unter Windows
                self._process.terminate()
                
                # Warte bis zu 3 Sekunden auf Beendigung
                for _ in range(30):
                    if self._process.poll() is not None:
                        break
                    time.sleep(0.1)
                
                # Falls der Prozess noch läuft, mit Gewalt beenden
                if self._process.poll() is None:
                    if self._logger:
                        self._logger.addLog("[WARNUNG] MAVSDK-Server reagiert nicht, wird erzwungen beendet")
                    self._process.kill()
            
            self._process = None
            if self._logger:
                self._logger.addLog("[INFO] MAVSDK-Server erfolgreich gestoppt")
            return True
            
        except Exception as e:
            if self._logger:
                self._logger.addLog(f"[FEHLER] Fehler beim Stoppen des MAVSDK-Servers: {str(e)}")
            return False
    
    def is_running(self) -> bool:
        """Prüft, ob der MAVSDK-Server läuft
        
        Returns:
            bool: True, wenn der Server läuft
        """
        return self._process is not None and self._process.poll() is None
