import os
import platform
import subprocess
import socket
import time
import threading
import datetime
import requests
import zipfile
import io
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Union

from PySide6.QtCore import QObject, Signal, Slot, Property

# Pfade für die SITL-Binaries
class SITLController(QObject):
    """Controller für Software-in-the-Loop Simulation von ArduPilot"""
    
    # Signale
    statusChanged = Signal(str)
    progressChanged = Signal(float)
    simStarted = Signal(str, str)  # Fahrzeugtyp, Verbindungsstring
    simStopped = Signal()
    errorOccurred = Signal(str)
    
    def __init__(self, logger=None, parent=None):
        """Initialisiert den SITL-Controller
        
        Args:
            logger: Logger-Instanz für Logging
            parent: Elternobjekt für Qt
        """
        super().__init__(parent)
        self._logger = logger
        
        # Pfade
        self._sitl_dir = os.path.join(os.path.expanduser("~"), "Documents", "RZGCS", "sitl")
        os.makedirs(self._sitl_dir, exist_ok=True)
        
        # Status-Variablen
        self._current_process = None
        self._is_simulation_running = False
        self._download_progress = 0.0
        self._simulator_processes = []
        self._udp_socket = None
        
        # URLs für offizielle ArduPilot SITL Binaries
        system = platform.system().lower()
        if system == "windows":
            self.binary_extension = ".exe"
            self.is_windows = True
        else:
            self.binary_extension = ".elf"
            self.is_windows = False
            
        # Basis-URLs für ArduPilot Firmware
        self.firmware_base_url = "https://firmware.ardupilot.org/"
        
        # ArduPilot SITL Binaries für verschiedene Fahrzeugtypen
        self.vehicle_types = {
            "copter": {
                "dir": "Copter",
                "bin_name": "arducopter",
                "variants": ["quad", "hexa", "octa", "tri", "y6", "heli"]
            },
            "plane": {
                "dir": "Plane",
                "bin_name": "arduplane",
                "variants": ["plane", "quadplane"]
            },
            "rover": {
                "dir": "Rover",
                "bin_name": "ardurover",
                "variants": ["rover"]
            },
            "sub": {
                "dir": "Sub",
                "bin_name": "ardusub",
                "variants": ["vectored"]
            },
            "tracker": {
                "dir": "AntennaTracker",
                "bin_name": "antennatracker",
                "variants": ["tracker"]
            }
        }
        
        # Build-Kategorien
        self.build_categories = {
            "Stable": "stable",
            "Beta": "beta",
            "Latest": "latest"
        }
        
        # Cleanup bei Programmende
        import atexit
        atexit.register(self.stop_all_simulators)
    
    def log(self, message, level="INFO"):
        """Loggt eine Nachricht"""
        if self._logger:
            if level == "INFO":
                self._logger.addLog(f"[SITL] {message}")
            elif level == "ERROR":
                self._logger.addLog(f"[SITL ERROR] {message}")
        else:
            print(f"[SITL {level}] {message}")
            
    def get_binary_path(self, vehicle_type: str, frame: str = "quad", version_type: str = "Stable") -> str:
        """Gibt den Pfad zum SITL-Binary zurück, lädt es herunter falls notwendig
        
        Args:
            vehicle_type: Typ des Fahrzeugs (z.B. "copter", "plane", "rover")
            frame: Frame-Typ (z.B. "quad", "hexa", "plane")
            version_type: Versionstyp (Stable, Beta, Latest)
            
        Returns:
            Pfad zum Binary oder None bei Fehler
        """
        # Fahrzeugtyp überprüfen
        vehicle_type = vehicle_type.lower()
        if vehicle_type not in self.vehicle_types:
            self.errorOccurred.emit(f"Unbekannter Fahrzeugtyp: {vehicle_type}")
            return None
            
        # Frame-Typ überprüfen
        frame = frame.lower()
        if frame not in self.vehicle_types[vehicle_type]["variants"]:
            self.log(f"Warnung: Frame-Typ {frame} nicht explizit unterstützt für {vehicle_type}, verwende Standard")
            frame = self.vehicle_types[vehicle_type]["variants"][0]
        
        # Build-Kategorie bestimmen
        category = self.build_categories.get(version_type, "stable")
        
        # Binary-Name bestimmen
        binary_name = f"{self.vehicle_types[vehicle_type]['bin_name']}-{frame}{self.binary_extension}"
        
        # Lokaler Pfad (in Unterordner pro Fahrzeugtyp/Version)
        vehicle_dir = os.path.join(self._sitl_dir, vehicle_type, category)
        os.makedirs(vehicle_dir, exist_ok=True)
        
        local_path = os.path.join(vehicle_dir, binary_name)
        
        # Überprüfen, ob Binary bereits vorhanden ist
        if os.path.exists(local_path):
            self.log(f"Verwende vorhandenes Binary: {local_path}")
            return local_path
            
        # Binary muss heruntergeladen werden
        self.log(f"Lade Binary '{binary_name}' für {vehicle_type}/{frame} ({category}) herunter...")
        
        # URL bestimmen - wir verwenden das SITL-Verzeichnis für die entsprechende Plattform
        # URL-Format: https://firmware.ardupilot.org/Copter/stable/SITL/arducopter-quad.exe
        
        url_path = f"{self.vehicle_types[vehicle_type]['dir']}/{category}/SITL/{binary_name}"
        url = f"{self.firmware_base_url}{url_path}"
            
        # Binary herunterladen
        try:
            self.statusChanged.emit(f"Lade {binary_name} herunter...")
            
            response = requests.get(url, stream=True)
            total_size = int(response.headers.get('content-length', 0))
            block_size = 8192
            downloaded = 0
            
            with open(local_path, "wb") as f:
                for data in response.iter_content(block_size):
                    downloaded += len(data)
                    f.write(data)
                    
                    if total_size:
                        progress = downloaded / total_size
                        self.progressChanged.emit(progress)
            
            # Ausführbar machen
            os.chmod(local_path, 0o755)
            
            self.statusChanged.emit(f"{binary_name} erfolgreich heruntergeladen")
            self.progressChanged.emit(1.0)
            
            return local_path
            
        except Exception as e:
            self.errorOccurred.emit(f"Fehler beim Herunterladen von {binary_name}: {str(e)}")
            return None
    
    def build_home_location(self, latitude: float, longitude: float, altitude: float = 40.0, heading: float = 0.0) -> str:
        """Erstellt den Home-Location-String für SITL
        
        Args:
            latitude: Breitengrad
            longitude: Längengrad
            altitude: Höhe in Metern
            heading: Ausrichtung in Grad
            
        Returns:
            Home-Location-String für SITL
        """
        return f"{latitude},{longitude},{altitude},{heading}"
    
    @Slot(str, str, str, str, int)
    def start_simulator(self, vehicle_type: str, frame: str, home_location: str, 
                      extra_params: str = "", sim_speed: int = 1) -> bool:
        """Startet eine SITL-Simulation
        
        Args:
            vehicle_type: Typ des Fahrzeugs (z.B. "copter", "plane", "rover")
            frame: Frame-Typ (z.B. "quad", "hexa", "plane")
            home_location: Home-Location-String (lat,lon,alt,yaw)
            extra_params: Zusätzliche Parameter
            sim_speed: Simulationsgeschwindigkeit
            
        Returns:
            True bei Erfolg, sonst False
        """
        if self._is_simulation_running:
            self.log("Es läuft bereits eine Simulation. Bitte zuerst beenden.")
            return False
        
        # Binary herunterladen oder lokales verwenden
        binary_path = self.get_binary_path(vehicle_type, frame, "Stable")
        if not binary_path:
            self.errorOccurred.emit(f"Konnte kein Binary für {vehicle_type}/{frame} finden oder herunterladen")
            return False
            
        # Parameter vorbereiten
        sim_options = []
        
        # Parameter je nach Fahrzeugtyp anpassen
        model_option = f"-{frame}"
        
        # Home Location
        sim_options.append(f"--home={home_location}")
        
        # Model Parameter
        sim_options.append(f"--model={frame}")
        
        # Simulation Speed
        if sim_speed != 1:
            sim_options.append(f"--speedup={sim_speed}")
        
        # Extra Params
        if extra_params:
            sim_options.append(extra_params)
        
        # UDP Port für SITL (5760 ist Standard)
        sitl_port = 5760
        sim_options.append(f"--uartA=tcp:127.0.0.1:{sitl_port}")
        
        # Kommando erstellen
        command = [binary_path] + sim_options
        
        try:
            # Prozess starten
            self.log(f"Starte SITL mit Kommando: {' '.join(command)}")
            
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                bufsize=1,
                universal_newlines=True
            )
            
            self._simulator_processes.append(process)
            self._is_simulation_running = True
            
            # Thread für Ausgabe-Weiterleitung
            def monitor_output():
                while process.poll() is None:
                    line = process.stdout.readline()
                    if line:
                        self.log(f"SITL: {line.strip()}")
            
            # Monitoring starten
            threading.Thread(target=monitor_output, daemon=True).start()
            
            # Signal senden
            connection_string = f"tcp:127.0.0.1:{sitl_port}"
            self.simStarted.emit(vehicle_type, connection_string)
            self.statusChanged.emit(f"SITL gestartet für {vehicle_type}")
            
            return True
            
        except Exception as e:
            self.errorOccurred.emit(f"Fehler beim Starten der Simulation: {str(e)}")
            return False
    
    @Slot()
    def stop_simulator(self):
        """Stoppt die laufende Simulation"""
        if not self._is_simulation_running:
            return
            
        for proc in self._simulator_processes:
            try:
                if proc.poll() is None:  # Prozess läuft noch
                    proc.terminate()
                    proc.wait(timeout=5)
            except Exception as e:
                self.log(f"Fehler beim Beenden des Simulators: {str(e)}", "ERROR")
                try:
                    proc.kill()
                except:
                    pass
        
        self._simulator_processes = []
        self._is_simulation_running = False
        self.simStopped.emit()
        self.statusChanged.emit("SITL beendet")
    
    def stop_all_simulators(self):
        """Stoppt alle laufenden Simulationen"""
        self.stop_simulator()
    
    @Property(bool)
    def is_simulation_running(self) -> bool:
        """Gibt an, ob eine Simulation läuft"""
        return self._is_simulation_running
