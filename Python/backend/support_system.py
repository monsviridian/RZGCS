# Python/backend/support_system.py

import os
import sys
import json
import time
import platform
import logging
import uuid
import requests
import datetime
import subprocess
import shutil
import tempfile
import threading
import zipfile
import io
from PySide6.QtCore import QObject, Signal, Slot, Property, QUrl, QTimer
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply

from .logger import Logger

class SupportSystem(QObject):
    """RZGCS Support-System-Manager
    
    Bietet Funktionen für technischen Support, Fehlerbericht-Erstellung,
    Systemdiagnose und Zugriff auf die Support-Wissensdatenbank.
    """
    
    # Signale
    supportTicketSubmitted = Signal(bool, str)  # Erfolg, Ticket-ID oder Fehlermeldung
    diagnosisCompleted = Signal(dict)          # Diagnoseergebnisse
    knowledgeBaseArticleLoaded = Signal(str, str)  # Artikel-ID, Inhalt
    errorOccurred = Signal(str)                # Fehlermeldung
    
    def __init__(self, logger: Logger = None):
        super().__init__()
        self._logger = logger
        self._network_manager = QNetworkAccessManager()
        self._support_api_url = "https://api.rzgcs.com/support"
        self._knowledge_base_url = "https://api.rzgcs.com/kb"
        self._active_diagnosis = False
        self._diagnostic_results = {}
        self._local_kb_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                      "docs", "knowledge_base")
        
        # Stelle sicher, dass das lokale KB-Verzeichnis existiert
        os.makedirs(self._local_kb_path, exist_ok=True)
        
        # Setup-Logging
        if self._logger:
            self._logger.addLog("[INFO] Support-System initialisiert")
        
    @Slot(str, str, str, str, str, result=bool)
    def submit_support_ticket(self, subject, description, email, category, priority):
        """Reicht ein Support-Ticket beim Support-Team ein
        
        Args:
            subject: Betreff des Tickets
            description: Ausführliche Beschreibung des Problems
            email: Kontakt-E-Mail des Benutzers
            category: Kategorie des Problems (Hardware, Software, Lizenz, usw.)
            priority: Priorität (Low, Medium, High, Critical)
            
        Returns:
            bool: True, wenn das Ticket erfolgreich eingereicht wurde
        """
        try:
            # Erzeuge eine eindeutige Ticket-ID
            ticket_id = f"RZGCS-{int(time.time())}-{uuid.uuid4().hex[:6]}"
            
            # Sammle Systemdiagnosedaten
            diagnostic_data = self._collect_system_info()
            
            # Sammle Log-Dateien
            logs = self._collect_logs()
            
            # Bereite Ticket-Daten vor
            ticket_data = {
                "ticket_id": ticket_id,
                "subject": subject,
                "description": description,
                "email": email,
                "category": category,
                "priority": priority,
                "timestamp": datetime.datetime.now().isoformat(),
                "system_info": diagnostic_data,
                "logs": logs,
                "status": "open"
            }
            
            # Speichere Ticket lokal
            self._save_ticket_locally(ticket_id, ticket_data)
            
            # Sende Ticket an den Server, wenn eine Internetverbindung besteht
            try:
                # Im Echtbetrieb würde hier die API-Anfrage stehen
                # self._send_ticket_to_server(ticket_id, ticket_data)
                
                # Simuliere einen erfolgreichen API-Aufruf
                if self._logger:
                    self._logger.addLog(f"[OK] Support-Ticket {ticket_id} erstellt")
                
                self.supportTicketSubmitted.emit(True, ticket_id)
                return True
            except Exception as e:
                # Bei Verbindungsproblemen nur lokal speichern
                if self._logger:
                    self._logger.addLog(f"[WARN] Ticket konnte nicht gesendet werden, wurde aber lokal gespeichert: {str(e)}")
                
                self.supportTicketSubmitted.emit(True, f"{ticket_id} (Offline gespeichert)")
                return True
                
        except Exception as e:
            error_msg = f"Fehler beim Erstellen des Support-Tickets: {str(e)}"
            if self._logger:
                self._logger.addLog(f"[ERR] {error_msg}")
            
            self.supportTicketSubmitted.emit(False, error_msg)
            return False
    
    def _collect_system_info(self):
        """Sammelt Systemdiagnoseinformationen"""
        system_info = {
            "os": platform.system(),
            "os_version": platform.version(),
            "architecture": platform.machine(),
            "python_version": sys.version,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        # Sammle Qt-Versionsinformationen
        try:
            from PySide6 import __version__ as pyside_version
            system_info["pyside_version"] = pyside_version
        except:
            system_info["pyside_version"] = "unknown"
        
        # Sammle Hardware-Informationen
        try:
            if platform.system() == "Windows":
                # Windows-spezifische Hardware-Informationen
                system_info["cpu_info"] = platform.processor()
                system_info["ram"] = self._get_windows_ram()
                system_info["gpu"] = self._get_windows_gpu()
            elif platform.system() == "Darwin":  # macOS
                # macOS-spezifische Hardware-Informationen
                system_info["cpu_info"] = self._get_macos_cpu()
                system_info["ram"] = self._get_macos_ram()
                system_info["gpu"] = self._get_macos_gpu()
            elif platform.system() == "Linux":
                # Linux-spezifische Hardware-Informationen
                system_info["cpu_info"] = self._get_linux_cpu()
                system_info["ram"] = self._get_linux_ram()
                system_info["gpu"] = self._get_linux_gpu()
        except Exception as e:
            system_info["hardware_error"] = str(e)
        
        # Sammle installierte Pakete
        try:
            import pkg_resources
            packages = []
            for pkg in pkg_resources.working_set:
                packages.append(f"{pkg.project_name}=={pkg.version}")
            system_info["installed_packages"] = packages
        except:
            system_info["installed_packages"] = ["Error collecting package information"]
        
        return system_info
    
    def _collect_logs(self):
        """Sammelt relevante Log-Dateien"""
        logs = {}
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
        
        if os.path.exists(log_dir):
            for file in os.listdir(log_dir):
                if file.endswith(".log"):
                    try:
                        with open(os.path.join(log_dir, file), 'r') as f:
                            # Lese nur die letzten 500 Zeilen, um die Größe zu begrenzen
                            lines = f.readlines()
                            logs[file] = "".join(lines[-500:]) if len(lines) > 500 else "".join(lines)
                    except:
                        logs[file] = "Error reading log file"
        
        # Aktuelle Laufzeitlogs hinzufügen, falls verfügbar
        if self._logger and hasattr(self._logger, 'get_logs'):
            logs["current_session.log"] = "\n".join(self._logger.get_logs())
        
        return logs
    
    def _save_ticket_locally(self, ticket_id, ticket_data):
        """Speichert ein Support-Ticket lokal"""
        tickets_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                               "support_tickets")
        os.makedirs(tickets_dir, exist_ok=True)
        
        ticket_file = os.path.join(tickets_dir, f"{ticket_id}.json")
        
        with open(ticket_file, 'w') as f:
            json.dump(ticket_data, f, indent=2)
    
    # Plattformspezifische Hardware-Informationsmethoden
    def _get_windows_ram(self):
        """Ermittelt den RAM unter Windows"""
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            c_ulong = ctypes.c_ulong
            class MEMORYSTATUS(ctypes.Structure):
                _fields_ = [
                    ('dwLength', c_ulong),
                    ('dwMemoryLoad', c_ulong),
                    ('dwTotalPhys', c_ulong),
                    ('dwAvailPhys', c_ulong),
                    ('dwTotalPageFile', c_ulong),
                    ('dwAvailPageFile', c_ulong),
                    ('dwTotalVirtual', c_ulong),
                    ('dwAvailVirtual', c_ulong)
                ]
                
            memory_status = MEMORYSTATUS()
            memory_status.dwLength = ctypes.sizeof(MEMORYSTATUS)
            kernel32.GlobalMemoryStatus(ctypes.byref(memory_status))
            
            return {
                "total": memory_status.dwTotalPhys,
                "available": memory_status.dwAvailPhys,
                "used_percent": memory_status.dwMemoryLoad
            }
        except:
            return "Unknown"
    
    def _get_windows_gpu(self):
        """Ermittelt die GPU unter Windows"""
        try:
            output = subprocess.check_output(["wmic", "path", "win32_VideoController", "get", "name"], 
                                           universal_newlines=True)
            lines = output.strip().split('\n')
            return lines[1] if len(lines) > 1 else "Unknown"
        except:
            return "Unknown"
    
    def _get_macos_cpu(self):
        """Ermittelt die CPU unter macOS"""
        try:
            output = subprocess.check_output(["sysctl", "-n", "machdep.cpu.brand_string"], 
                                           universal_newlines=True)
            return output.strip()
        except:
            return "Unknown"
    
    def _get_macos_ram(self):
        """Ermittelt den RAM unter macOS"""
        try:
            # Gesamter physischer Speicher
            mem_output = subprocess.check_output(["sysctl", "-n", "hw.memsize"], 
                                              universal_newlines=True)
            total_ram = int(mem_output.strip())
            
            # Freier Speicher ist schwieriger zu ermitteln und erfordert vm_stat
            vm_stat_output = subprocess.check_output(["vm_stat"], universal_newlines=True)
            lines = vm_stat_output.strip().split('\n')
            
            # Vereinfachte Berechnung - nicht 100% genau, aber ausreichend für Diagnosezwecke
            return {
                "total": total_ram,
                "total_gb": round(total_ram / (1024**3), 2),
                "vm_stat": "\n".join(lines[:5])  # Erste paar Zeilen von vm_stat
            }
        except:
            return "Unknown"
    
    def _get_macos_gpu(self):
        """Ermittelt die GPU unter macOS"""
        try:
            output = subprocess.check_output(["system_profiler", "SPDisplaysDataType"], 
                                           universal_newlines=True)
            lines = output.strip().split('\n')
            gpu_info = [line.strip() for line in lines if "Chipset Model:" in line]
            return gpu_info[0].replace("Chipset Model:", "").strip() if gpu_info else "Unknown"
        except:
            return "Unknown"
    
    def _get_linux_cpu(self):
        """Ermittelt die CPU unter Linux"""
        try:
            with open("/proc/cpuinfo", "r") as f:
                for line in f:
                    if "model name" in line:
                        return line.split(":")[1].strip()
            return "Unknown"
        except:
            return "Unknown"
    
    def _get_linux_ram(self):
        """Ermittelt den RAM unter Linux"""
        try:
            with open("/proc/meminfo", "r") as f:
                meminfo = {}
                for line in f:
                    if ":" in line:
                        key, value = line.split(":")
                        meminfo[key.strip()] = value.strip()
                return {
                    "total": meminfo.get("MemTotal", "Unknown"),
                    "free": meminfo.get("MemFree", "Unknown"),
                    "available": meminfo.get("MemAvailable", "Unknown")
                }
        except:
            return "Unknown"
    
    def _get_linux_gpu(self):
        """Ermittelt die GPU unter Linux"""
        try:
            output = subprocess.check_output(["lspci"], universal_newlines=True)
            lines = output.strip().split('\n')
            gpu_lines = [line for line in lines if "VGA" in line or "3D" in line]
            return gpu_lines[0] if gpu_lines else "Unknown"
        except:
            return "Unknown"
            
    @Slot()
    def run_system_diagnosis(self):
        """Führt eine umfassende Systemdiagnose durch"""
        if self._active_diagnosis:
            return  # Verhindere mehrere gleichzeitige Diagnosen
            
        self._active_diagnosis = True
        
        # Starte die Diagnose in einem separaten Thread
        threading.Thread(target=self._run_diagnosis_thread, daemon=True).start()
        
        if self._logger:
            self._logger.addLog("[INFO] Systemdiagnose gestartet")
    
    def _run_diagnosis_thread(self):
        """Führt die Diagnose im Hintergrund aus"""
        try:
            diagnostic_results = {}
            
            # 1. Systeminfo
            diagnostic_results['system_info'] = self._collect_system_info()
            
            # 2. Verbindungstest
            diagnostic_results['connectivity'] = self._test_connectivity()
            
            # 3. Software-Prüfung
            diagnostic_results['software_check'] = self._check_software()
            
            # 4. Lizenzprüfung
            diagnostic_results['license_check'] = self._check_license()
            
            # 5. Portzugriffstests
            diagnostic_results['port_access'] = self._test_port_access()
            
            # 6. Performance-Tests
            diagnostic_results['performance'] = self._test_performance()
            
            # Ergebnisse speichern
            self._diagnostic_results = diagnostic_results
            
            # Signal mit den Ergebnissen senden
            self.diagnosisCompleted.emit(diagnostic_results)
            
            if self._logger:
                self._logger.addLog("[OK] Systemdiagnose abgeschlossen")
        except Exception as e:
            error_msg = f"Fehler bei der Systemdiagnose: {str(e)}"
            if self._logger:
                self._logger.addLog(f"[ERR] {error_msg}")
            self.errorOccurred.emit(error_msg)
        finally:
            self._active_diagnosis = False
    
    def _test_connectivity(self):
        """Testet die Internetverbindung und API-Erreichbarkeit"""
        results = {}
        
        # Internet-Konnektivität testen
        try:
            # Verwende requests mit einem Timeout von 5 Sekunden
            response = requests.get("https://www.google.com", timeout=5)
            results['internet'] = {
                'status': 'ok' if response.status_code == 200 else 'error',
                'latency': response.elapsed.total_seconds() * 1000  # ms
            }
        except Exception as e:
            results['internet'] = {
                'status': 'error',
                'error': str(e)
            }
        
        # RZGCS API-Server testen (simuliert)
        results['api_server'] = {
            'status': 'simulated',
            'message': 'API-Verbindungstest simuliert'
        }
        
        return results
    
    def _check_software(self):
        """Prüft die Softwarekomponenten auf Probleme"""
        results = {}
        
        # Prüfen, ob alle erforderlichen Python-Pakete installiert sind
        try:
            import pkg_resources
            required_packages = [
                'PySide6', 'pymavlink', 'requests', 'numpy', 'pyserial'
            ]
            missing_packages = []
            version_info = {}
            
            for package in required_packages:
                try:
                    version = pkg_resources.get_distribution(package).version
                    version_info[package] = version
                except pkg_resources.DistributionNotFound:
                    missing_packages.append(package)
            
            results['packages'] = {
                'status': 'ok' if not missing_packages else 'warning',
                'versions': version_info,
                'missing': missing_packages
            }
        except Exception as e:
            results['packages'] = {
                'status': 'error',
                'error': str(e)
            }
        
        # Prüfen, ob die RZGCS-Dateien vollständig sind
        try:
            rzgcs_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            required_dirs = ['Python', 'RZGCSContent', 'RZGCS', 'docs', 'Assets']
            missing_dirs = [d for d in required_dirs if not os.path.isdir(os.path.join(rzgcs_dir, d))]
            
            results['files'] = {
                'status': 'ok' if not missing_dirs else 'error',
                'missing_dirs': missing_dirs
            }
        except Exception as e:
            results['files'] = {
                'status': 'error',
                'error': str(e)
            }
        
        return results
    
    def _check_license(self):
        """Prüft den Lizenzstatus"""
        # In einer realen Implementierung würde dies mit dem Lizenzsystem interagieren
        # Hier geben wir simulierte Ergebnisse zurück
        return {
            'status': 'simulated',
            'message': 'Lizenzprüfung simuliert'
        }
    
    def _test_port_access(self):
        """Testet den Zugriff auf serielle Ports"""
        results = {}
        
        try:
            import serial.tools.list_ports
            ports = list(serial.tools.list_ports.comports())
            
            port_info = []
            for port in ports:
                port_data = {
                    'device': port.device,
                    'description': port.description,
                    'hwid': port.hwid
                }
                
                # Test, ob Port geöffnet werden kann
                try:
                    test_connection = serial.Serial(port.device, timeout=1)
                    test_connection.close()
                    port_data['accessible'] = True
                except Exception as e:
                    port_data['accessible'] = False
                    port_data['error'] = str(e)
                
                port_info.append(port_data)
            
            results['available_ports'] = port_info
            results['status'] = 'ok' if ports else 'warning'
        except Exception as e:
            results['status'] = 'error'
            results['error'] = str(e)
        
        return results
    
    def _test_performance(self):
        """Führt einfache Performance-Tests durch"""
        results = {}
        
        # CPU-Benchmark (einfache Berechnung)
        try:
            start_time = time.time()
            # Einfacher CPU-Test: Berechne die ersten 1000 Primzahlen
            primes = []
            num = 2
            while len(primes) < 1000:
                is_prime = True
                for i in range(2, int(num ** 0.5) + 1):
                    if num % i == 0:
                        is_prime = False
                        break
                if is_prime:
                    primes.append(num)
                num += 1
            
            cpu_time = time.time() - start_time
            results['cpu_benchmark'] = {
                'time': cpu_time,
                'score': 10.0 / cpu_time if cpu_time > 0 else 0  # Höherer Wert = besser
            }
        except Exception as e:
            results['cpu_benchmark'] = {
                'error': str(e)
            }
        
        # Festplatten-I/O-Test
        try:
            # Temporäre Datei erstellen und lesen/schreiben testen
            with tempfile.TemporaryFile(mode='w+b') as f:
                # Schreibtest
                start_time = time.time()
                data = b'0' * (1024 * 1024)  # 1 MB Daten
                for _ in range(10):  # 10 MB schreiben
                    f.write(data)
                f.flush()
                write_time = time.time() - start_time
                
                # Lesetest
                start_time = time.time()
                f.seek(0)
                while f.read(1024 * 1024):
                    pass
                read_time = time.time() - start_time
                
                results['disk_benchmark'] = {
                    'write_time': write_time,
                    'write_speed_mbps': 10 / write_time if write_time > 0 else 0,
                    'read_time': read_time,
                    'read_speed_mbps': 10 / read_time if read_time > 0 else 0
                }
        except Exception as e:
            results['disk_benchmark'] = {
                'error': str(e)
            }
        
        return results
