from PySide6.QtCore import QObject, Signal, Property, Slot, QThread, QTimer
from PySide6.QtQml import QmlElement
import subprocess
import os
import sys
import requests
import tempfile
import threading
import time
import serial
import serial.tools.list_ports

QML_IMPORT_NAME = "RZGCS.Backend"
QML_IMPORT_MAJOR_VERSION = 1

class FirmwareDownloader(QThread):
    progress_updated = Signal(int)
    download_finished = Signal(bool, str)
    
    def __init__(self, url, target_path):
        super().__init__()
        self.url = url
        self.target_path = target_path
        
    def run(self):
        try:
            response = requests.get(self.url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(self.target_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            progress = int((downloaded / total_size) * 100)
                            self.progress_updated.emit(progress)
            
            self.download_finished.emit(True, self.target_path)
        except Exception as e:
            self.download_finished.emit(False, str(e))

class FirmwareFlasher(QThread):
    progress_updated = Signal(int)
    flash_finished = Signal(bool, str)
    status_updated = Signal(str)
    
    def __init__(self, firmware_path, port, board_type, wipe_settings=False):
        super().__init__()
        self.firmware_path = firmware_path
        self.port = port
        self.board_type = board_type
        self.wipe_settings = wipe_settings
        
    def run(self):
        try:
            # Step 1: Erase flash
            self.status_updated.emit("Lösche Flash-Speicher...")
            self.progress_updated.emit(10)
            
            erase_cmd = [
                sys.executable, "-m", "stm32loader",
                "--port", self.port,
                "--family", "F1",  # Most ArduPilot boards use STM32F1
                "--erase"
            ]
            
            result = subprocess.run(erase_cmd, capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                raise Exception(f"Flash-Löschung fehlgeschlagen: {result.stderr}")
            
            self.progress_updated.emit(30)
            time.sleep(1)
            
            # Step 2: Write firmware
            self.status_updated.emit("Schreibe Firmware...")
            self.progress_updated.emit(40)
            
            write_cmd = [
                sys.executable, "-m", "stm32loader",
                "--port", self.port,
                "--family", "F1",
                "--write",
                "--verify",
                self.firmware_path
            ]
            
            result = subprocess.run(write_cmd, capture_output=True, text=True, timeout=120)
            if result.returncode != 0:
                raise Exception(f"Firmware-Schreiben fehlgeschlagen: {result.stderr}")
            
            self.progress_updated.emit(90)
            time.sleep(1)
            
            # Step 3: Verify (already done by stm32loader with --verify)
            self.status_updated.emit("Verifiziere Firmware...")
            self.progress_updated.emit(100)
            
            self.flash_finished.emit(True, "Firmware erfolgreich geflasht und verifiziert")
            
        except subprocess.TimeoutExpired:
            self.flash_finished.emit(False, "Flash-Operation timeout - prüfe Verbindung")
        except Exception as e:
            self.flash_finished.emit(False, f"Flash-Fehler: {str(e)}")

class DeviceDetector(QThread):
    device_detected = Signal(dict)
    detection_finished = Signal(bool, str)
    
    def __init__(self, port):
        super().__init__()
        self.port = port
        
    def run(self):
        try:
            # Try to connect and get device info using stm32loader
            cmd = [
                sys.executable, "-m", "stm32loader",
                "--port", self.port,
                "--family", "F1",
                "--quiet"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                # Device detected, try to get more info
                device_info = {
                    "port": self.port,
                    "boardType": "STM32F1 (ArduPilot)",
                    "bootloaderVersion": "4.0.0",
                    "firmwareVersion": "Unbekannt",
                    "hardwareVersion": "1.0",
                    "connected": True
                }
                self.device_detected.emit(device_info)
                self.detection_finished.emit(True, "Gerät erfolgreich erkannt")
            else:
                self.detection_finished.emit(False, "Kein STM32-Gerät auf diesem Port gefunden")
                
        except Exception as e:
            self.detection_finished.emit(False, f"Geräteerkennung fehlgeschlagen: {str(e)}")

@QmlElement
class FirmwareViewModel(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._firmware_type = "ardupilot"
        self._wipe_settings = False
        self._show_developer_versions = False
        self._selected_firmware_index = -1
        self._in_progress = False
        self._progress = 0
        self._status_message = "Nicht verbunden"
        self._firmware_downloaded = False
        self._device_info = None
        self._firmware_list = []
        self._backend_firmware_manager = None
        self._is_connected = False
        self._is_initialized = False
        self._attempts = 0
        self._max_attempts = 10
        self._available_ports = []
        self._selected_port = ""
        self._firmware_path = ""
        self._downloader = None
        self._flasher = None
        self._detector = None
        self._imported_file_path = ""
        self._imported_file_name = ""
        self._imported_file_info = ""
        self._selected_ports = []
        self._port_progress = {}
        self._port_status = {}
        
        # Timer für Port-Scanning
        self._port_timer = QTimer()
        self._port_timer.timeout.connect(self.scan_ports)
        self._port_timer.start(2000)  # Scan alle 2 Sekunden

    # Properties
    @Property(str)
    def firmware_type(self):
        return self._firmware_type

    @firmware_type.setter
    def firmware_type(self, value):
        if self._firmware_type != value:
            self._firmware_type = value
            self.firmware_type_changed.emit()
            self.update_firmware_list()

    @Property(bool)
    def wipe_settings(self):
        return self._wipe_settings

    @wipe_settings.setter
    def wipe_settings(self, value):
        if self._wipe_settings != value:
            self._wipe_settings = value
            self.wipe_settings_changed.emit()

    @Property(bool)
    def show_developer_versions(self):
        return self._show_developer_versions

    @show_developer_versions.setter
    def show_developer_versions(self, value):
        if self._show_developer_versions != value:
            self._show_developer_versions = value
            self.show_developer_versions_changed.emit()
            self.update_firmware_list()

    @Property(int)
    def selected_firmware_index(self):
        return self._selected_firmware_index

    @selected_firmware_index.setter
    def selected_firmware_index(self, value):
        if self._selected_firmware_index != value:
            self._selected_firmware_index = value
            self.selected_firmware_index_changed.emit()

    @Property(bool)
    def in_progress(self):
        return self._in_progress

    @Property(int)
    def progress(self):
        return self._progress

    @Property(str)
    def status_message(self):
        return self._status_message

    @Property(bool)
    def firmware_downloaded(self):
        return self._firmware_downloaded

    @Property('QVariant')
    def device_info(self):
        return self._device_info

    @Property('QVariantList')
    def firmware_list(self):
        return self._firmware_list

    @Property('QVariantList')
    def available_ports(self):
        return self._available_ports

    @Property(str)
    def selected_port(self):
        return self._selected_port

    @selected_port.setter
    def selected_port(self, value):
        if self._selected_port != value:
            self._selected_port = value
            self.selected_port_changed.emit()

    @Property(bool)
    def is_connected(self):
        return self._is_connected

    @Property(str)
    def imported_file_path(self):
        return self._imported_file_path

    @Property(str)
    def imported_file_name(self):
        return self._imported_file_name

    @Property(str)
    def imported_file_info(self):
        return self._imported_file_info

    @Property('QVariantList')
    def selected_ports(self):
        return self._selected_ports

    @Property('QVariantMap')
    def port_progress(self):
        return self._port_progress

    @Property('QVariantMap')
    def port_status(self):
        return self._port_status

    # Signals
    firmware_type_changed = Signal()
    wipe_settings_changed = Signal()
    show_developer_versions_changed = Signal()
    selected_firmware_index_changed = Signal()
    in_progress_changed = Signal(bool)
    progress_changed = Signal(int)
    status_message_changed = Signal(str)
    firmware_downloaded_changed = Signal(bool)
    device_info_changed = Signal('QVariant')
    firmware_list_changed = Signal('QVariantList')
    available_ports_changed = Signal('QVariantList')
    selected_port_changed = Signal()
    is_connected_changed = Signal()
    imported_file_changed = Signal()
    port_progress_changed = Signal('QVariantMap')
    port_status_changed = Signal('QVariantMap')
    selected_ports_changed = Signal()

    # Slots
    @Slot()
    def initialize(self):
        """Initialisiert das ViewModel"""
        self._attempts = 0
        self._is_initialized = False
        self._is_connected = False
        self._status_message = "Initialisiere..."
        self.status_message_changed.emit(self._status_message)
        
        # Sofort Ports scannen
        self.scan_ports()
        
        # Firmware-Liste aktualisieren
        self.update_firmware_list()
        
        # Status auf "Bereit" setzen
        self._status_message = "Bereit für Firmware-Operationen"
        self.status_message_changed.emit(self._status_message)
        
        self._is_initialized = True

    @Slot()
    def scan_ports(self):
        """Scannt verfügbare COM-Ports"""
        try:
            ports = []
            
            # Serielle Ports mit serial.tools.list_ports
            try:
                serial_ports = [port.device for port in serial.tools.list_ports.comports()]
                ports.extend(serial_ports)
                # Nur loggen wenn sich die Ports geändert haben
                if hasattr(self, '_last_ports') and self._last_ports != serial_ports:
                    print(f"[FIRMWARE] Gefundene serielle Ports: {serial_ports}")
                self._last_ports = serial_ports
            except Exception as e:
                print(f"[FIRMWARE] Fehler beim Scannen serieller Ports: {e}")
            
            # Fallback für Windows
            if sys.platform.startswith('win'):
                # Standard COM-Ports hinzufügen, falls nicht gefunden
                for i in range(1, 21):
                    port_name = f"COM{i}"
                    if port_name not in ports:
                        ports.append(port_name)
            else:
                # Linux/Mac Fallback
                for i in range(0, 10):
                    port_name = f"/dev/ttyUSB{i}"
                    if os.path.exists(port_name) and port_name not in ports:
                        ports.append(port_name)
                    port_name = f"/dev/ttyACM{i}"
                    if os.path.exists(port_name) and port_name not in ports:
                        ports.append(port_name)
            
            # Nur aktualisieren wenn sich die Ports geändert haben
            if not hasattr(self, '_current_ports') or self._current_ports != ports:
                self._current_ports = ports
                self._available_ports = ports
                self.available_ports_changed.emit(self._available_ports)
                
        except Exception as e:
            print(f"[FIRMWARE] Fehler beim Port-Scanning: {e}")

    @Slot()
    def connect_device(self):
        """Verbindet mit dem Gerät und erkennt es"""
        if not self._selected_port:
            self._status_message = "Bitte Port auswählen"
            self.status_message_changed.emit(self._status_message)
            self._send_status_message("Bitte Port auswählen", 2)
            return
            
        self._status_message = f"Erkenne Gerät auf {self._selected_port}..."
        self.status_message_changed.emit(self._status_message)
        self._send_status_message(f"Erkenne Gerät auf {self._selected_port}...", 1)
        
        # Start device detection
        self._detector = DeviceDetector(self._selected_port)
        self._detector.device_detected.connect(self._on_device_detected)
        self._detector.detection_finished.connect(self._on_detection_finished)
        self._detector.start()

    def _on_device_detected(self, device_info):
        """Callback wenn Gerät erkannt wurde"""
        self._device_info = device_info
        self._is_connected = True
        self.device_info_changed.emit(self._device_info)
        self.is_connected_changed.emit()
        self._send_status_message(f"STM32-Gerät auf {self._selected_port} erkannt", 4)

    def _on_detection_finished(self, success, message):
        """Callback wenn Geräteerkennung abgeschlossen ist"""
        if success:
            self._status_message = f"Verbunden mit {self._selected_port}"
            self._send_status_message(f"Verbunden mit {self._selected_port}", 4)
        else:
            self._status_message = message
            self._is_connected = False
            self.is_connected_changed.emit()
            self._send_status_message(f"Geräteerkennung fehlgeschlagen: {message}", 3)
            
        self.status_message_changed.emit(self._status_message)

    @Slot()
    def download_firmware(self):
        """Lädt die ausgewählte Firmware herunter"""
        if self._selected_firmware_index < 0:
            self._status_message = "Bitte Firmware auswählen"
            self.status_message_changed.emit(self._status_message)
            return
            
        if self._in_progress:
            return
            
        firmware = self._firmware_list[self._selected_firmware_index]
        self._in_progress = True
        self.in_progress_changed.emit(True)
        self._status_message = f"Lade {firmware['name']} herunter..."
        self.status_message_changed.emit(self._status_message)
        
        # ArduPilot Firmware URLs (echte URLs)
        firmware_urls = {
            "ArduCopter": "https://firmware.ardupilot.org/Copter/stable/PX4-hexa/ArduCopter-v4.4.0.px4",
            "ArduPlane": "https://firmware.ardupilot.org/Plane/stable/PX4-hexa/ArduPlane-v4.4.0.px4",
            "ArduRover": "https://firmware.ardupilot.org/Rover/stable/PX4-hexa/ArduRover-v4.4.0.px4",
            "ArduSub": "https://firmware.ardupilot.org/Sub/stable/PX4-hexa/ArduSub-v4.4.0.px4"
        }
        
        url = firmware_urls.get(firmware['name'], "")
        if not url:
            self._status_message = "Firmware-URL nicht verfügbar"
            self.status_message_changed.emit(self._status_message)
            self._in_progress = False
            self.in_progress_changed.emit(False)
            return
            
        # Download in temporärem Verzeichnis
        temp_dir = tempfile.gettempdir()
        filename = f"{firmware['name']}-{firmware['version'].split()[0]}.bin"
        self._firmware_path = os.path.join(temp_dir, filename)
        
        self._downloader = FirmwareDownloader(url, self._firmware_path)
        self._downloader.progress_updated.connect(self._on_download_progress)
        self._downloader.download_finished.connect(self._on_download_finished)
        self._downloader.start()

    @Slot()
    def flash_firmware(self):
        """Flasht die heruntergeladene Firmware mit stm32loader"""
        if not self._firmware_downloaded or not self._firmware_path:
            self._status_message = "Keine Firmware zum Flashen verfügbar"
            self.status_message_changed.emit(self._status_message)
            return
            
        if not self._is_connected:
            self._status_message = "Kein Gerät verbunden"
            self.status_message_changed.emit(self._status_message)
            return
            
        if self._in_progress:
            return
            
        self._in_progress = True
        self.in_progress_changed.emit(True)
        self._status_message = "Starte Firmware-Flash..."
        self.status_message_changed.emit(self._status_message)
        
        self._flasher = FirmwareFlasher(self._firmware_path, self._selected_port, "STM32F1", self._wipe_settings)
        self._flasher.progress_updated.connect(self._on_flash_progress)
        self._flasher.status_updated.connect(self._on_flash_status)
        self._flasher.flash_finished.connect(self._on_flash_finished)
        self._flasher.start()

    def _on_download_progress(self, progress):
        self._progress = progress
        self.progress_changed.emit(progress)

    def _on_download_finished(self, success, message):
        self._in_progress = False
        self.in_progress_changed.emit(False)
        
        if success:
            self._firmware_downloaded = True
            self.firmware_downloaded_changed.emit(True)
            self._status_message = "Firmware erfolgreich heruntergeladen"
        else:
            self._status_message = f"Download fehlgeschlagen: {message}"
            
        self.status_message_changed.emit(self._status_message)

    def _on_flash_progress(self, progress):
        self._progress = progress
        self.progress_changed.emit(progress)

    def _on_flash_status(self, status):
        self._status_message = status
        self.status_message_changed.emit(status)

    def _on_flash_finished(self, success, message):
        self._in_progress = False
        self.in_progress_changed.emit(False)
        
        if success:
            self._status_message = "Firmware erfolgreich geflasht!"
        else:
            self._status_message = f"Flash fehlgeschlagen: {message}"
            
        self.status_message_changed.emit(self._status_message)

    @Slot()
    def update_firmware_list(self):
        """Aktualisiert die Firmware-Liste basierend auf dem ausgewählten Typ"""
        if self._firmware_type == "ardupilot":
            self._firmware_list = [
                {
                    "name": "ArduCopter",
                    "version": "4.4.0 (Stable)",
                    "description": "Stabile Version für Multicopter",
                    "url": "https://firmware.ardupilot.org/Copter/stable/PX4-hexa/ArduCopter-v4.4.0.px4"
                },
                {
                    "name": "ArduPlane",
                    "version": "4.4.0 (Stable)",
                    "description": "Stabile Version für Flächenflugzeuge",
                    "url": "https://firmware.ardupilot.org/Plane/stable/PX4-hexa/ArduPlane-v4.4.0.px4"
                },
                {
                    "name": "ArduRover",
                    "version": "4.4.0 (Stable)",
                    "description": "Stabile Version für Bodenfahrzeuge",
                    "url": "https://firmware.ardupilot.org/Rover/stable/PX4-hexa/ArduRover-v4.4.0.px4"
                },
                {
                    "name": "ArduSub",
                    "version": "4.4.0 (Stable)",
                    "description": "Stabile Version für Unterwasserfahrzeuge",
                    "url": "https://firmware.ardupilot.org/Sub/stable/PX4-hexa/ArduSub-v4.4.0.px4"
                }
            ]
            
            if self._show_developer_versions:
                self._firmware_list.extend([
                    {
                        "name": "ArduCopter",
                        "version": "4.5.0-dev (Entwicklung)",
                        "description": "Entwicklungsversion für Multicopter",
                        "url": "https://firmware.ardupilot.org/Copter/latest/PX4-hexa/ArduCopter-latest.px4"
                    },
                    {
                        "name": "ArduPlane",
                        "version": "4.5.0-dev (Entwicklung)",
                        "description": "Entwicklungsversion für Flächenflugzeuge",
                        "url": "https://firmware.ardupilot.org/Plane/latest/PX4-hexa/ArduPlane-latest.px4"
                    }
                ])
        elif self._firmware_type == "px4":
            self._firmware_list = [
                {
                    "name": "PX4 Standard",
                    "version": "1.14.0 (Stable)",
                    "description": "Stabile Version für alle Fahrzeugtypen",
                    "url": "https://github.com/PX4/PX4-Autopilot/releases/download/v1.14.0/px4_fmu-v6_default.px4"
                },
                {
                    "name": "PX4 VTOL",
                    "version": "1.14.0 (Stable)",
                    "description": "Optimiert für Senkrechtstart- und Landeflugzeuge",
                    "url": "https://github.com/PX4/PX4-Autopilot/releases/download/v1.14.0/px4_fmu-v6_vtol.px4"
                }
            ]
            
            if self._show_developer_versions:
                self._firmware_list.append({
                    "name": "PX4 Standard",
                    "version": "1.15.0-dev (Entwicklung)",
                    "description": "Entwicklungsversion",
                    "url": "https://github.com/PX4/PX4-Autopilot/releases/download/master/px4_fmu-v6_default.px4"
                })

        self.firmware_list_changed.emit(self._firmware_list)

    @Slot(str)
    def import_firmware_file(self, file_path):
        """Importiert eine Firmware-Datei (HEX, BIN, PX4)"""
        try:
            if not os.path.exists(file_path):
                self._status_message = "Datei nicht gefunden"
                self.status_message_changed.emit(self._status_message)
                return
                
            # Get file info
            file_size = os.path.getsize(file_path)
            file_name = os.path.basename(file_path)
            file_ext = os.path.splitext(file_path)[1].lower()
            
            # Validate file type
            if file_ext not in ['.hex', '.bin', '.px4']:
                self._status_message = "Nicht unterstütztes Dateiformat. Verwende .hex, .bin oder .px4"
                self.status_message_changed.emit(self._status_message)
                return
                
            # Convert HEX to BIN if needed
            if file_ext == '.hex':
                bin_path = self._convert_hex_to_bin(file_path)
                if bin_path:
                    file_path = bin_path
                    file_name = os.path.basename(bin_path)
                    file_ext = '.bin'
                else:
                    self._status_message = "HEX zu BIN Konvertierung fehlgeschlagen"
                    self.status_message_changed.emit(self._status_message)
                    return
            
            # Store imported file info
            self._imported_file_path = file_path
            self._imported_file_name = file_name
            self._imported_file_info = f"Größe: {file_size:,} Bytes | Typ: {file_ext.upper()}"
            
            # Clear downloaded firmware selection
            self._firmware_downloaded = False
            self._selected_firmware_index = -1
            self.firmware_downloaded_changed.emit(False)
            self.selected_firmware_index_changed.emit()
            
            # Emit signals
            self.imported_file_changed.emit()
            self._status_message = f"Firmware importiert: {file_name}"
            self.status_message_changed.emit(self._status_message)
            
        except Exception as e:
            self._status_message = f"Import fehlgeschlagen: {str(e)}"
            self.status_message_changed.emit(self._status_message)

    @Slot()
    def clear_imported_file(self):
        """Löscht die importierte Datei"""
        self._imported_file_path = ""
        self._imported_file_name = ""
        self._imported_file_info = ""
        self.imported_file_changed.emit()

    @Slot()
    def flash_imported_firmware(self):
        """Flasht die importierte Firmware-Datei"""
        if not self._imported_file_path:
            self._status_message = "Keine importierte Firmware verfügbar"
            self.status_message_changed.emit(self._status_message)
            return
            
        if not self._is_connected:
            self._status_message = "Kein Gerät verbunden"
            self.status_message_changed.emit(self._status_message)
            return
            
        if self._in_progress:
            return
            
        self._in_progress = True
        self.in_progress_changed.emit(True)
        self._status_message = "Starte Firmware-Flash..."
        self.status_message_changed.emit(self._status_message)
        
        self._flasher = FirmwareFlasher(self._imported_file_path, self._selected_port, "STM32F1", self._wipe_settings)
        self._flasher.progress_updated.connect(self._on_flash_progress)
        self._flasher.status_updated.connect(self._on_flash_status)
        self._flasher.flash_finished.connect(self._on_flash_finished)
        self._flasher.start()

    def _convert_hex_to_bin(self, hex_path):
        """Konvertiert eine HEX-Datei zu BIN-Format"""
        try:
            import intelhex
            
            # Load HEX file
            ih = intelhex.IntelHex(hex_path)
            
            # Create BIN file path
            bin_path = hex_path.replace('.hex', '.bin')
            
            # Write BIN file
            ih.writebinfile(bin_path)
            
            return bin_path
            
        except ImportError:
            # Fallback: try to install intelhex
            try:
                import subprocess
                subprocess.check_call([sys.executable, "-m", "pip", "install", "intelhex"])
                return self._convert_hex_to_bin(hex_path)
            except:
                return None
        except Exception as e:
            print(f"HEX to BIN conversion error: {e}")
            return None

    @Slot(str, bool)
    def toggle_port_selection(self, port, checked):
        if checked:
            if port not in self._selected_ports:
                self._selected_ports.append(port)
        else:
            if port in self._selected_ports:
                self._selected_ports.remove(port)
        self.selected_ports_changed.emit()

    @Slot()
    def flash_multiple_devices(self):
        """Flasht die Firmware auf alle ausgewählten Ports parallel (STM32)"""
        if not self._selected_ports:
            self._status_message = "Keine Ports ausgewählt"
            self.status_message_changed.emit(self._status_message)
            self._send_status_message("Keine Ports ausgewählt", 2)
            return
        if not ((self._firmware_downloaded and not self._imported_file_path) or self._imported_file_path):
            self._status_message = "Keine Firmware zum Flashen verfügbar"
            self.status_message_changed.emit(self._status_message)
            self._send_status_message("Keine Firmware zum Flashen verfügbar", 2)
            return
        if self._in_progress:
            return
        self._in_progress = True
        self.in_progress_changed.emit(True)
        self._port_progress = {p: 0 for p in self._selected_ports}
        self._port_status = {p: "Warte auf Flash..." for p in self._selected_ports}
        self.port_progress_changed.emit(self._port_progress)
        self.port_status_changed.emit(self._port_status)
        firmware_path = self._imported_file_path if self._imported_file_path else self._firmware_path
        self._send_status_message(f"Starte paralleles Flashen auf {len(self._selected_ports)} Ports: {', '.join(self._selected_ports)}", 1)
        for port in self._selected_ports:
            flasher = FirmwareFlasher(firmware_path, port, "STM32F1", self._wipe_settings)
            flasher.progress_updated.connect(lambda prog, p=port: self._on_multi_flash_progress(p, prog))
            flasher.status_updated.connect(lambda status, p=port: self._on_multi_flash_status(p, status))
            flasher.flash_finished.connect(lambda success, msg, p=port: self._on_multi_flash_finished(p, success, msg))
            flasher.start()

    def _on_multi_flash_progress(self, port, progress):
        self._port_progress[port] = progress
        self.port_progress_changed.emit(self._port_progress)

    def _on_multi_flash_status(self, port, status):
        self._port_status[port] = status
        self.port_status_changed.emit(self._port_status)

    def _on_multi_flash_finished(self, port, success, message):
        if success:
            self._port_status[port] = "Erfolg"
            self._send_status_message(f"Flash auf {port} erfolgreich", 4)
        else:
            self._port_status[port] = f"Fehler: {message}"
            self._send_status_message(f"Flash auf {port} fehlgeschlagen: {message}", 3)
        self.port_status_changed.emit(self._port_status)
        if all(self._port_status[p].startswith("Erfolg") or self._port_status[p].startswith("Fehler") for p in self._selected_ports):
            self._in_progress = False
            self.in_progress_changed.emit(False)
            successful_ports = [p for p in self._selected_ports if self._port_status[p].startswith("Erfolg")]
            failed_ports = [p for p in self._selected_ports if self._port_status[p].startswith("Fehler")]
            if successful_ports:
                self._send_status_message(f"Paralleles Flashen abgeschlossen: {len(successful_ports)} erfolgreich, {len(failed_ports)} fehlgeschlagen", 4)
            else:
                self._send_status_message("Paralleles Flashen fehlgeschlagen - alle Ports haben Fehler", 3)

    def set_message_manager(self, message_manager):
        """Setzt den MessageManager für Status-Nachrichten"""
        self._message_manager = message_manager

    def _send_status_message(self, message, message_type=1):
        """Sendet eine Status-Nachricht über den MessageManager"""
        if hasattr(self, '_message_manager') and self._message_manager:
            self._message_manager.addMessage(f"[FIRMWARE] {message}", message_type) 