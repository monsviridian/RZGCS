#!/usr/bin/env python3
"""
Minimal MAVSDK MVVM Implementation
Simplified integration focusing only on essential components
"""

import os
import sys
import types
import re
import asyncio
import mavsdk
from pathlib import Path

# Set QML style BEFORE importing PySide6
os.environ["QT_QUICK_CONTROLS_STYLE"] = "Material"

# Import PySide6 components
import PySide6
from PySide6.QtCore import QUrl, Property, Signal, Slot
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine, qmlRegisterType
from PySide6.QtQuickControls2 import QQuickStyle

# Import MVVM components
from backend.logger import Logger
from backend.sensorviewmodel import SensorViewModel
from backend.parameter_model import ParameterTableModel
from backend.parameter_manager import ParameterManager
from rzgcs.mvvm.viewmodel.mavsdk_drone_viewmodel import MAVSDKDroneViewModel
from rzgcs.mvvm.qml_compatibility_adapter import QMLCompatibilityAdapter


def main():
    """Main application function"""
    print(f"Python version: {sys.version}")
    print(f"PySide6 version: {PySide6.__version__}")
    
    # Set working directory to project root (essential for finding QML files)
    project_root = Path(__file__).resolve().parent.parent
    os.chdir(str(project_root))
    print(f"Working directory: {os.getcwd()}")
    
    # Set Material style for QML
    QQuickStyle.setStyle("Material")
    
    # Create QApplication
    app = QGuiApplication(sys.argv)
    
    # Create logger
    logger = Logger()
    logger.addLog("[INFO] Starting minimal MAVSDK MVVM integration")
    
    # Create drone view model
    drone_view_model = MAVSDKDroneViewModel(logger)
    
    # Add compatibility methods based on memory about UI connection improvements
    # 1. Store selected port
    drone_view_model._selected_port = ""
    
    # 2. Add 'load_ports' method
    def load_ports():
        drone_view_model.refreshPorts()
    drone_view_model.load_ports = load_ports
    
    # 3. Add 'setPort' and 'setSelectedPort' methods
    def setPort(port_name):
        drone_view_model._selected_port = port_name
        logger.addLog(f"[INFO] Port selected: {port_name}")
    drone_view_model.setPort = setPort
    
    # Add the setSelectedPort method that is called by QMLCompatibilityAdapter
    def setSelectedPort(self, port_name):
        """Speichert den ausgewählten Port vom UI"""
        self._selected_port = port_name
        print(f"[DEBUG] Port selected: {port_name}")
        self._logger.addLog(f"[INFO] Port im ViewModel gesetzt: {port_name}")
    drone_view_model.setSelectedPort = types.MethodType(setSelectedPort, drone_view_model)
    
    # 4. Add universal connection method (renamed to avoid conflict with Signal.connect)
    async def _check_connection(self):
        """Überprüft, ob die Verbindung zum Fahrzeug hergestellt wurde"""
        try:
            # Versuche zuerst mit get_version, was bei den meisten Drohnen funktioniert
            try:
                await self._drone.info.get_version()
                return True
            except Exception:
                pass
                
            # Alternativ versuche mit get_identification
            try:
                await self._drone.info.get_identification()
                return True
            except Exception:
                pass
                
            # Als letztes versuche es mit connection_state, falls verfügbar
            try:
                connection_task = asyncio.ensure_future(self._drone.core.connection_state().__anext__())
                state = await asyncio.wait_for(connection_task, timeout=1.0)
                return state.is_connected
            except Exception:
                pass
                
            return False
        except Exception:
            return False
        
    def _clean_up_server(self):
        """Beendet den MAVSDK-Server-Prozess"""
        if hasattr(self, '_server_process') and self._server_process:
            try:
                self._logger.addLog("[INFO] Beende MAVSDK-Server-Prozess...")
                self._server_process.terminate()
                self._server_process.wait(timeout=3)
                self._logger.addLog("[INFO] MAVSDK-Server erfolgreich beendet")
            except Exception as e:
                self._logger.addLog(f"[WARNUNG] Fehler beim Beenden des MAVSDK-Servers: {str(e)}")
                try:
                    self._logger.addLog("[INFO] Erzwinge Beendigung des MAVSDK-Servers")
                    self._server_process.kill()
                except:
                    pass
            finally:
                self._server_process = None
                
    def _connect_implementation(self, connection_string=""):
        """
        Verbindet mit einem Fahrzeug über die angegebene Verbindung
        
        Args:
            connection_string: Der Verbindungsstring (z.B. "COM3:115200" oder "udp://:14550")
            
        Returns:
            bool: True, wenn die Verbindung erfolgreich initiiert wurde
        """
        if not connection_string and hasattr(self, '_selected_port'):
            connection_string = self._selected_port
        
        if not connection_string:
            self._logger.addLog("[WARNUNG] Kein Verbindungsstring angegeben")
            return False

        # MAVSDK-Server-Konfiguration
        import os
        import subprocess
        import sys
        import signal
        
        server_port = 50051
        self._mavsdk_server_process = None
        
        # Prüfen, ob wir unter Windows sind
        is_windows = sys.platform.startswith('win')
        
        # Pfad zum MAVSDK-Server ermitteln
        mavsdk_server_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mavsdk_server")
        if is_windows:
            mavsdk_server_path = os.path.join(mavsdk_server_dir, "windows", "mavsdk-server.exe")
        else:
            mavsdk_server_path = os.path.join(mavsdk_server_dir, "linux", "mavsdk-server")
            
        # Prüfe, ob der MAVSDK-Server existiert
        if not os.path.exists(mavsdk_server_path):
            self._logger.addLog(f"[FEHLER] MAVSDK-Server nicht gefunden: {mavsdk_server_path}")
            return False

        # Prüfe auf serielle Verbindung (z.B. COM3:57600)
        serial_match = re.match(r"([A-Za-z0-9]+)(?::([0-9]+))?$", connection_string)
        if serial_match:
            port = serial_match.group(1)
            baud = serial_match.group(2) or "115200"  # Default-Baudrate
            
            self._logger.addLog(f"[INFO] Verbinde seriell mit {port} bei {baud} Baud")
            
            # Formatiere die URL korrekt für den MAVSDK-Server
            # WICHTIG: Das korrekte Format ist serial://COM8:115200 (ohne dritten Slash)
            mavsdk_url = f"serial://{port}:{baud}"
            
            self._logger.addLog(f"[DEBUG] Starte MAVSDK-Server mit URL: {mavsdk_url}")
            
            # MAVSDK-Server starten
            server_args = [
                mavsdk_server_path,
                "-p", str(server_port),
                mavsdk_url
            ]
            
            try:
                # Server im Hintergrund starten
                self._mavsdk_server_process = subprocess.Popen(server_args)
                self._logger.addLog(f"[INFO] MAVSDK-Server gestartet (PID: {self._mavsdk_server_process.pid})")
                
                # Kurz warten, bis der Server initiiert ist
                import time
                time.sleep(2)
                
                import threading
                # Thread starten
                # Speichere Server-Prozess im korrekten Attribut
                self._server_process = self._mavsdk_server_process
                
                # Thread starten
                import threading
                self._connect_thread = threading.Thread(target=self.connect_thread, args=(server_port,), daemon=True)
                self._connect_thread.start()
                
                return True  # Server erfolgreich gestartet
                
            except Exception as e:
                self._logger.addLog(f"[FEHLER] Fehler beim Starten des MAVSDK-Servers: {str(e)}")
                return False
                        
                        # Wenn verbunden
                        if connected:
                            self._logger.addLog(f"[INFO] Verbunden mit {port} bei {baud} Baud")
                            self._is_connected = True
                            
                            # Stelle sicher, dass alle relevanten Signale emittiert werden
                            self.connectionStateChanged.emit(True)
                            
                            # Wichtig: Rufe _handle_connection auf, um UI-Status zu aktualisieren
                            self._handle_connection(True)
                            
                            # Starte Telemetrie-Abruf als Beispiel
                            try:
                                # Rufe Initial-Telemetrie ab
                                loop.run_until_complete(self.telemetry_position_task())
                                loop.run_until_complete(self.telemetry_battery_task())
                                loop.run_until_complete(self.telemetry_gps_task())
                                loop.run_until_complete(self.telemetry_health_task())
                                
                                # Starte Status-Text-Überwachung in separatem Thread
                                status_text_task = asyncio.ensure_future(self._start_status_text_monitoring())
                                loop.run_until_complete(asyncio.gather(status_text_task))
                            except Exception as e:
                                self._logger.addLog(f"[WARNUNG] Initialer Telemetrie-Abruf fehlgeschlagen: {str(e)}")
                        else:
                            self._logger.addLog(f"[FEHLER] Konnte keine Verbindung herstellen")
                            self._clean_up_server()
                            self._is_connected = False
                            self.connectionStateChanged.emit(False)
                            self._handle_connection(False)
                            
                    except Exception as e:
                        self._logger.addLog(f"[FEHLER] Verbindungsfehler: {str(e)}")
                        self._clean_up_server()
                        self._is_connected = False
                        self.connectionStateChanged.emit(False)
                        self._handle_connection(False)
                
                # Thread wird direkt über die Methode gestartet
                
            except Exception as e:
                self._logger.addLog(f"[FEHLER] Fehler beim Starten des MAVSDK-Servers: {str(e)}")
                self._clean_up_server()
                return False
        
        return True

    # Alte connect-Methode entfernen, falls vorhanden
    if hasattr(drone_view_model.__class__, 'connect'):
        delattr(drone_view_model.__class__, 'connect')
    
    # Erstelle die connectToDrone-Methode und hänge sie an das ViewModel an
    @Slot(str)
    def connectToDrone(self, connection_string=""):
        print(f"[DEBUG] Connecting to drone: {connection_string}")
        return self._original_connect(connection_string)
    
    # Telemetrie-Task-Methoden
    async def telemetry_position_task(self):
        """Task zum Abrufen der Positionsdaten"""
        try:
            # Position als asynchroner Generator abrufen
            async for position in self._drone.telemetry.position():
                self._position = position
                self.positionChanged.emit(position)
                return True
        except Exception as e:
            self._logger.addLog(f"[FEHLER] Position konnte nicht abgerufen werden: {str(e)}")
            return False
            
    async def telemetry_battery_task(self):
        """Task zum Abrufen der Batteriedaten"""
        try:
            # Batterie als asynchroner Generator abrufen
            async for battery in self._drone.telemetry.battery():
                self._battery = battery
                self.batteryChanged.emit(battery)
                return True
        except Exception as e:
            self._logger.addLog(f"[FEHLER] Batteriedaten konnten nicht abgerufen werden: {str(e)}")
            return False
            
    async def telemetry_gps_task(self):
        """Task zum Abrufen der GPS-Daten"""
        try:
            # GPS-Info als asynchroner Generator abrufen
            async for gps_info in self._drone.telemetry.gps_info():
                self._gps_info = gps_info
                self.gpsInfoChanged.emit(gps_info)
                return True
        except Exception as e:
            self._logger.addLog(f"[FEHLER] GPS-Daten konnten nicht abgerufen werden: {str(e)}")
            return False
            
    async def telemetry_health_task(self):
        """Task zum Abrufen der Gesundheitsdaten"""
        try:
            # Gesundheitsstatus als asynchroner Generator abrufen
            async for health in self._drone.telemetry.health():
                self._health = health
                self.healthChanged.emit(health)
                return True
        except Exception as e:
            self._logger.addLog(f"[FEHLER] Gesundheitsdaten konnten nicht abgerufen werden: {str(e)}")
            return False
            
    async def _start_status_text_monitoring(self):
        """Überwacht die Status-Text-Meldungen der Drohne und leitet sie an den Logger weiter"""
        try:
            # Status-Text-Stream abonnieren
            self._logger.addLog("[INFO] Starte Status-Text-Überwachung")
            async for status_text in self._drone.telemetry.status_text():
                # Prefix für die Art der Meldung bestimmen (INFO, WARNING, CRITICAL usw.)
                prefix = "[INFO]"
                if status_text.type.name == "WARNING":
                    prefix = "[WARNUNG]"
                elif status_text.type.name == "CRITICAL":
                    prefix = "[KRITISCH]"
                elif status_text.type.name == "ERROR":
                    prefix = "[FEHLER]"
                    
                # An Logger weiterleiten (mit FC-Prefix für wichtige Meldungen)
                message = f"[FC] {prefix} {status_text.text}"
                self._logger.addLog(message)
                
                # Wichtige FC-Nachrichten auch an die PreflightView-UI weiterleiten
                self.fcImportantMessageReceived.emit(status_text.text)
                
        except asyncio.CancelledError:
            self._logger.addLog("[INFO] Status-Text-Überwachung beendet")
            return
        except Exception as e:
            self._logger.addLog(f"[FEHLER] Fehler bei Status-Text-Überwachung: {str(e)}")
            return
            
    def connect_thread(self, server_port):
        """Thread-Methode für die Drohnen-Verbindung"""
        import time
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            # Verbindung zum MAVSDK-Server herstellen
            self._drone = mavsdk.System(mavsdk_server_address="localhost", port=server_port)
            self._logger.addLog(f"[DEBUG] Verbinde mit MAVSDK-Server auf localhost:{server_port}")
            loop.run_until_complete(self._drone.connect())
            
            # Signalisiere Verbindungsversuch an die UI
            self.connectionStateChanged.emit(True)  # Emittiert Signal für QML-UI
            
            # Auf Verbindung warten
            connected = False
            try:
                timeout_sec = 15
                start_time = time.time()
                
                while time.time() - start_time < timeout_sec:
                    # Prüfen, ob Verbindung besteht
                    try:
                        if self._check_connection(loop):
                            connected = True
                            break
                    except:
                        pass
                    time.sleep(1)
                    
                # Wenn verbunden
                if connected:
                    self._logger.addLog(f"[INFO] Verbunden mit Drohne")
                    self._is_connected = True
                    
                    # Stelle sicher, dass alle relevanten Signale emittiert werden
                    self.connectionStateChanged.emit(True)
                    
                    # Wichtig: Rufe _handle_connection auf, um UI-Status zu aktualisieren
                    self._handle_connection(True)
                    
                    # Starte Telemetrie-Abruf als Beispiel
                    try:
                        # Rufe Initial-Telemetrie ab
                        loop.run_until_complete(self.telemetry_position_task())
                        loop.run_until_complete(self.telemetry_battery_task())
                        loop.run_until_complete(self.telemetry_gps_task())
                        loop.run_until_complete(self.telemetry_health_task())
                        
                        # Starte Status-Text-Überwachung in separatem Thread
                        status_text_task = asyncio.ensure_future(self._start_status_text_monitoring())
                        loop.run_until_complete(asyncio.gather(status_text_task))
                    except Exception as e:
                        self._logger.addLog(f"[WARNUNG] Initialer Telemetrie-Abruf fehlgeschlagen: {str(e)}")
                else:
                    self._logger.addLog(f"[FEHLER] Konnte keine Verbindung herstellen")
                    self._clean_up_server()
                    self._is_connected = False
                    self.connectionStateChanged.emit(False)
                    self._handle_connection(False)
                    
            except Exception as e:
                self._logger.addLog(f"[FEHLER] Verbindungsfehler: {str(e)}")
                self._clean_up_server()
                self._is_connected = False
                self.connectionStateChanged.emit(False)
                self._handle_connection(False)
        except Exception as e:
            self._logger.addLog(f"[FEHLER] Fehler beim Verbinden mit MAVSDK-Server: {str(e)}")
            self._clean_up_server()
            self._is_connected = False
            self.connectionStateChanged.emit(False)
            self._handle_connection(False)
    
    # Methode anhängen
    drone_view_model._original_connect = types.MethodType(_connect_implementation, drone_view_model)
    drone_view_model.connectToDrone = types.MethodType(connectToDrone, drone_view_model)
    
    print("[INFO] Successfully renamed connect method to connectToDrone to fix signal conflicts")
    
    # Add disconnect method
    @Slot()
    def disconnectDrone(self):
        """Trennt die Verbindung zur Drohne und beendet den MAVSDK-Server"""
        if not self._is_connected:
            return True
            
        self._logger.addLog("[INFO] Trenne Verbindung zur Drohne")
        
        # MAVSDK-Server beenden
        self._clean_up_server()
        
        # Verbindungsstatus aktualisieren
        self._is_connected = False
        self.connectionStateChanged.emit(False)
        self._handle_connection(False)
        
        return True
    
    # Methode anhängen
    drone_view_model.disconnectDrone = types.MethodType(disconnectDrone, drone_view_model)
    
    # 5. Add 'update_connection_status' method
    def update_connection_status(is_connected):
        drone_view_model.connectionStateChanged.emit(is_connected)
    drone_view_model.update_connection_status = update_connection_status
    
    # 6. Add 'connected' property as alias for connectionState
    def get_connected(self):
        return getattr(self._model, 'is_connected', False)
    setattr(drone_view_model.__class__, 'connected', 
            Property(bool, get_connected, notify=drone_view_model.connectionStateChanged))
    
    # Create additional models required by the QML UI
    # IMPORTANT: These models must be properly registered for QML
    sensor_model = SensorViewModel()
    parameter_model = ParameterTableModel()
    parameter_manager = ParameterManager(parameter_model, logger)
    
    # Register the SensorViewModel as a QML type (needed for proper QML interaction)
    qmlRegisterType(SensorViewModel, "RZGCS", 1, 0, "SensorViewModel")
    
    # Ensure MAVSDK server is found
    mavsdk_server_path = os.path.join(os.getcwd(), "mavsdk_server", "windows", "mavsdk-server.exe")
    if os.path.exists(mavsdk_server_path):
        logger.addLog(f"[INFO] MAVSDK-Server gefunden: {mavsdk_server_path}")
    else:
        logger.addLog(f"[WARNUNG] MAVSDK-Server nicht gefunden an: {mavsdk_server_path}")
    
    # Define explicit update methods for signal connections to avoid naming conflicts
    def update_battery(battery):
        sensor_model.setBatteryLevel(battery['remaining_percent'])
        sensor_model.setBatteryVoltage(battery['voltage_v'])
    
    def update_gps(gps_info):
        sensor_model.setGpsSatelliteCount(gps_info['num_satellites'])
        sensor_model.setGpsFixType(gps_info['fix_type'])
        
    # Verwende stattdessen eine separate Funktion, um die Signale manuell zu verbinden
    def connect_signals():
        # Benutze interne Signal-Connect-Methode direkt, um Konflikte zu vermeiden
        battery_signal = getattr(drone_view_model, 'batteryChanged')
        battery_signal.connect(lambda battery: update_battery(battery))
        
        #class MAVSDKDroneViewModel(QObject):
    # QML-kompatible Signale für Aktualisierungen
    connectionStateChanged = Signal(bool)
    positionChanged = Signal(object)
    batteryChanged = Signal(object)
    gpsInfoChanged = Signal(object)
    healthChanged = Signal(object)
    fcImportantMessageReceived = Signal(str)  # Neues Signal für FC-wichtige Meldungen(lambda gps_info: update_gps(gps_info))
        
        # Andere Signale verbinden
        pos_signal = getattr(drone_view_model, 'positionChanged')
        pos_signal.connect(lambda position: (
            sensor_model.setLatitude(position['latitude_deg']),
            sensor_model.setLongitude(position['longitude_deg']),
            sensor_model.setAltitude(position['absolute_altitude_m']) if 'absolute_altitude_m' in position else None
        ))
    drone_view_model.headingChanged.connect(lambda heading: sensor_model.setHeading(heading))
    
    # Create QML engine and set Material style
    engine = QQmlApplicationEngine()
    
    # Set import paths
    qml_content_dir = os.path.join(os.getcwd(), "RZGCSContent")
    engine.addImportPath(qml_content_dir)
    engine.addImportPath(os.getcwd())
    
    # Set environment variables for QML import paths (essential for proper QML loading)
    os.environ["QML_IMPORT_PATH"] = qml_content_dir
    os.environ["QML2_IMPORT_PATH"] = qml_content_dir
    
    # Ensure Material style configuration file exists
    config_file = os.path.join(os.getcwd(), "RZGCSContent", "qtquickcontrols2.conf")
    if not os.path.exists(config_file):
        config_content = """[Controls]\nStyle=Material\n\n[Material]\nTheme=Dark\nAccent=Teal\nPrimary=BlueGrey\nVariant=Dense\n"""
        with open(config_file, "w") as f:
            f.write(config_content)
        logger.addLog(f"[INFO] Material style Konfigurationsdatei erstellt: {config_file}")
    
    # Create QML compatibility adapter for proper signal mapping
    qml_adapter = QMLCompatibilityAdapter(drone_view_model)
    
    # Register objects in QML context (IMPORTANT: register ALL required models)
    context = engine.rootContext()
    context.setContextProperty("serialConnector", qml_adapter)  # Important: Use adapter for compatibility
    context.setContextProperty("droneViewModel", drone_view_model) # Original ViewModel still available
    context.setContextProperty("sensorModel", sensor_model)  # Required by PreflightView.ui.qml
    context.setContextProperty("parameterModel", parameter_model)  # Required by ParameterView.ui.qml
    context.setContextProperty("parameterManager", parameter_manager)  # May be needed by parameter functionality
    context.setContextProperty("logger", logger)
    
    # Load existing main module that has working QML loading logic
    # This is the key difference: we're borrowing the QML loading code that we know works
    import mavsdk_rzgcs_main
    
    # Replace the QML loading part while keeping our objects
    original_main = mavsdk_rzgcs_main.main
    
    def custom_main():
        # Our QML setup is already done, so we'll execute a minimal version of the original main
        # that just handles QML file loading, which seems to be working in the original
        
        # Create the original backend to access its objects
        backend = mavsdk_rzgcs_main.RZGCSBackend()
        
        # Load the QML file using the original code's approach
        qml_file = os.path.join(os.getcwd(), "RZGCSContent", "App.qml")
        print(f"Loading QML file: {qml_file}")
        
        # Load QML file
        url = QUrl.fromLocalFile(qml_file)
        engine.load(url)
        
        # Check if application loaded successfully
        if not engine.rootObjects():
            logger.addLog("[ERROR] Failed to load QML file!")
            print(f"[ERROR] Failed to load QML file: {url.toString()}")
            return 1
        
        # Start application
        logger.addLog("[INFO] RZGCS with MAVSDK MVVM integration started")
        logger.addLog("[INFO] Alle erforderlichen Modelle wurden registriert (serialConnector, sensorModel, parameterModel)")
        logger.addLog("[INFO] Material Style wurde für QML konfiguriert")
        return app.exec()
    
    # Run our custom main function
    return custom_main()


if __name__ == "__main__":
    sys.exit(main())
