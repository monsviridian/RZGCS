"""
Spezialisierter Konnektor für die Simulatorverbindung mit verbesserter Fehlerbehandlung.
Dieses Modul stellt eine robuste UDP-basierte Verbindung zum MAVLink-Simulator bereit.
"""

import asyncio
import time
from PySide6.QtCore import QObject, Signal, Slot, QTimer
from pymavlink import mavutil

from backend.simple_mavlink_simulator import SimpleMAVLinkSimulator
from backend.logger import Logger

class SimulatorConnector(QObject):
    """
    Verwaltet die Verbindung zum MAVLink-Simulator.
    
    Diese Klasse kümmert sich speziell um den Simulator und stellt sicher,
    dass die Verbindung robust ist und Fehlerfälle ordnungsgemäß behandelt werden.
    """
    
    # Signale für UI-Updates
    connectionStatusChanged = Signal(bool)    # Verbindungsstatus (verbunden/getrennt)
    heartbeatReceived = Signal()             # Heartbeat empfangen
    messageReceived = Signal(object)         # MAVLink-Nachricht empfangen
    errorOccurred = Signal(str)              # Fehler aufgetreten
    
    def __init__(self, logger: Logger):
        """
        Initialisiert den SimulatorConnector.
        
        Args:
            logger: Logger für Statusmeldungen
        """
        super().__init__()
        self._logger = logger
        self._connected = False
        self._mavlink_connection = None
        self._simulator = None
        self._receive_timer = None
        self._simulator_started = False
        
    @property
    def connected(self):
        """Gibt an, ob eine Verbindung besteht."""
        return self._connected
        
    @Slot()
    def start_connection(self):
        """Stellt eine Verbindung zum Simulator her."""
        if self._connected:
            self._logger.addLog("✅ Bereits mit dem Simulator verbunden")
            return True
            
        try:
            self._logger.addLog("🔄 Verbinde mit Simulator...")
            
            # Start simulator process
            self._simulator = SimpleMAVLinkSimulator()
            if not self._simulator.start():
                self._logger.addLog("❌ Fehler beim Starten des Simulators")
                return False
                
            self._simulator_started = True
            self._logger.addLog("✅ Simulator gestartet")
            
            # Wait a moment for the simulator to initialize
            time.sleep(0.5)
            
            # Create MAVLink connection to receive simulator data
            try:
                self._mavlink_connection = mavutil.mavlink_connection(
                    'udpin:localhost:14551',
                    source_system=1,
                    source_component=1,
                    dialect='ardupilotmega'
                )
                self._logger.addLog("✅ MAVLink-Verbindung hergestellt")
            except Exception as e:
                self._logger.addLog(f"❌ Fehler bei MAVLink-Verbindung: {str(e)}")
                return False
                
            # Wait for heartbeat with timeout
            self._logger.addLog("⌛ Warte auf Heartbeat...")
            try:
                self._mavlink_connection.wait_heartbeat(timeout=2)
                self._logger.addLog("💓 Heartbeat empfangen!")
                self.heartbeatReceived.emit()
            except Exception as e:
                # Heartbeat might not come in simulator mode immediately
                self._logger.addLog("⚠️ Kein Heartbeat empfangen, fahre trotzdem fort")
            
            # Start message receive timer
            self._receive_timer = QTimer(self)
            self._receive_timer.timeout.connect(self._receive_messages)
            self._receive_timer.start(100)  # 100ms
            
            # Set connected state
            self._connected = True
            self.connectionStatusChanged.emit(True)
            self._logger.addLog("✅ Mit Simulator verbunden")
            
            return True
            
        except Exception as e:
            self._logger.addLog(f"❌ Verbindungsfehler: {str(e)}")
            self.errorOccurred.emit(f"Verbindungsfehler: {str(e)}")
            self._cleanup_connection()
            return False
            
    @Slot()
    def disconnect(self):
        """Trennt die Verbindung zum Simulator."""
        if not self._connected:
            return True
            
        self._logger.addLog("🔄 Trenne Verbindung zum Simulator...")
        self._cleanup_connection()
        self._logger.addLog("✅ Verbindung zum Simulator getrennt")
        return True
        
    def _cleanup_connection(self):
        """Räumt alle Verbindungsressourcen auf."""
        # Stop the message receive timer
        if self._receive_timer is not None:
            self._receive_timer.stop()
            self._receive_timer = None
            
        # Stop the simulator
        if self._simulator is not None and self._simulator_started:
            try:
                self._simulator.stop()
                self._simulator = None
                self._simulator_started = False
            except Exception as e:
                self._logger.addLog(f"⚠️ Fehler beim Stoppen des Simulators: {str(e)}")
                
        # Close the MAVLink connection
        if self._mavlink_connection is not None:
            try:
                self._mavlink_connection.close()
            except:
                pass
            self._mavlink_connection = None
            
        # Update connection state
        if self._connected:
            self._connected = False
            self.connectionStatusChanged.emit(False)
            
    def _receive_messages(self):
        """Empfängt und verarbeitet MAVLink-Nachrichten."""
        if not self._connected or self._mavlink_connection is None:
            return
            
        try:
            # Check for new messages
            msg = self._mavlink_connection.recv_match(blocking=False)
            if msg:
                # Process message
                msgtype = msg.get_type()
                
                # Emit message for handlers
                self.messageReceived.emit(msg)
                
                # Special handling for heartbeat
                if msgtype == "HEARTBEAT":
                    self.heartbeatReceived.emit()
                    
        except Exception as e:
            self._logger.addLog(f"⚠️ Fehler beim Empfangen von Nachrichten: {str(e)}")
            # Don't disconnect on receive errors
