# Verbindungsmanagement in RZGCS
## Analyse und Implementierung basierend auf QGroundControl und MissionPlanner

### 1. Verbindungstypen

#### 1.1 Serielle Verbindung
```python
# Python/backend/mavlink_connector.py
class SerialConnection:
    def __init__(self):
        self.supported_baudrates = [
            9600, 14400, 19200, 38400, 57600, 115200, 230400, 460800, 921600
        ]
        self.connection_string_format = "serial://{port}:{baudrate}"
    
    def connect(self, port, baudrate):
        if baudrate not in self.supported_baudrates:
            raise ValueError(f"Unsupported baudrate: {baudrate}")
        
        connection_string = self.connection_string_format.format(
            port=port,
            baudrate=baudrate
        )
        return self._establish_connection(connection_string)
```

#### 1.2 UDP Verbindung
```python
# Python/backend/mavlink_connector.py
class UDPConnection:
    def __init__(self):
        self.connection_string_format = "udp://{host}:{port}"
        self.default_ports = {
            'local': 14550,  # Standard MAVLink UDP Port
            'remote': 14540  # Standard GCS UDP Port
        }
    
    def connect(self, host, port=None):
        if port is None:
            port = self.default_ports['remote']
        
        connection_string = self.connection_string_format.format(
            host=host,
            port=port
        )
        return self._establish_connection(connection_string)
```

#### 1.3 TCP Verbindung
```python
# Python/backend/mavlink_connector.py
class TCPConnection:
    def __init__(self):
        self.connection_string_format = "tcp://{host}:{port}"
        self.default_port = 5760  # Standard MAVLink TCP Port
    
    def connect(self, host, port=None):
        if port is None:
            port = self.default_port
        
        connection_string = self.connection_string_format.format(
            host=host,
            port=port
        )
        return self._establish_connection(connection_string)
```

### 2. Verbindungsmanagement UI

#### 2.1 Hauptverbindungsansicht
```qml
// RZGCSContent/ConnectionView.ui.qml
Item {
    id: connectionView
    
    // Connection Type Selection
    ComboBox {
        id: connectionType
        model: ["Serial", "UDP", "TCP", "Simulator"]
        onCurrentTextChanged: {
            connectionSettings.visible = true
            switch(currentText) {
                case "Serial":
                    serialSettings.visible = true
                    udpSettings.visible = false
                    tcpSettings.visible = false
                    break
                case "UDP":
                    serialSettings.visible = false
                    udpSettings.visible = true
                    tcpSettings.visible = false
                    break
                case "TCP":
                    serialSettings.visible = false
                    udpSettings.visible = false
                    tcpSettings.visible = true
                    break
                case "Simulator":
                    connectionSettings.visible = false
                    break
            }
        }
    }
    
    // Connection Settings
    Item {
        id: connectionSettings
        
        // Serial Settings
        Item {
            id: serialSettings
            visible: false
            
            ComboBox {
                id: portCombo
                model: connectionManager.availablePorts
            }
            
            ComboBox {
                id: baudRateCombo
                model: [9600, 14400, 19200, 38400, 57600, 115200, 230400, 460800, 921600]
                currentIndex: 5  // Default to 115200
            }
        }
        
        // UDP Settings
        Item {
            id: udpSettings
            visible: false
            
            TextField {
                id: udpHost
                placeholderText: "Enter host IP"
            }
            
            SpinBox {
                id: udpPort
                from: 1024
                to: 65535
                value: 14550
            }
        }
        
        // TCP Settings
        Item {
            id: tcpSettings
            visible: false
            
            TextField {
                id: tcpHost
                placeholderText: "Enter host IP"
            }
            
            SpinBox {
                id: tcpPort
                from: 1024
                to: 65535
                value: 5760
            }
        }
    }
    
    // Connect Button
    Button {
        text: connectionManager.connected ? "Disconnect" : "Connect"
        onClicked: {
            if (connectionManager.connected) {
                connectionManager.disconnect()
            } else {
                var settings = {
                    type: connectionType.currentText,
                    port: portCombo.currentText,
                    baudRate: baudRateCombo.currentText,
                    host: udpHost.text || tcpHost.text,
                    port: udpPort.value || tcpPort.value
                }
                connectionManager.connect(settings)
            }
        }
    }
}
```

### 3. Verbindungsstatus und Fehlerbehandlung

#### 3.1 Status Management
```python
# Python/backend/connection_manager.py
class ConnectionStatus:
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"

class ConnectionManager:
    def __init__(self):
        self.status = ConnectionStatus.DISCONNECTED
        self.error_message = ""
        self.connection = None
        self.heartbeat_timer = None
    
    def connect(self, settings):
        try:
            self.status = ConnectionStatus.CONNECTING
            self.error_message = ""
            
            if settings['type'] == 'Serial':
                self.connection = SerialConnection()
                self.connection.connect(settings['port'], settings['baudRate'])
            elif settings['type'] == 'UDP':
                self.connection = UDPConnection()
                self.connection.connect(settings['host'], settings['port'])
            elif settings['type'] == 'TCP':
                self.connection = TCPConnection()
                self.connection.connect(settings['host'], settings['port'])
            
            self.status = ConnectionStatus.CONNECTED
            self._start_heartbeat()
            
        except Exception as e:
            self.status = ConnectionStatus.ERROR
            self.error_message = str(e)
            self.connection = None
```

#### 3.2 Heartbeat System
```python
# Python/backend/connection_manager.py
    def _start_heartbeat(self):
        self.heartbeat_timer = QTimer()
        self.heartbeat_timer.timeout.connect(self._check_heartbeat)
        self.heartbeat_timer.start(1000)  # Check every second
    
    def _check_heartbeat(self):
        if not self.connection or not self.connection.is_alive():
            self.status = ConnectionStatus.ERROR
            self.error_message = "Connection lost"
            self._stop_heartbeat()
```

### 4. Verbindungsprotokollierung

#### 4.1 Logging System
```python
# Python/backend/connection_logger.py
class ConnectionLogger:
    def __init__(self):
        self.log_file = None
        self.log_level = logging.INFO
    
    def start_logging(self, connection_id):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"connection_{connection_id}_{timestamp}.log"
        self.log_file = open(filename, 'w')
    
    def log_connection_event(self, event_type, details):
        timestamp = datetime.now().isoformat()
        log_entry = f"{timestamp} - {event_type}: {details}\n"
        if self.log_file:
            self.log_file.write(log_entry)
            self.log_file.flush()
```

### 5. Verbindungssicherheit

#### 5.1 Verschlüsselung
```python
# Python/backend/connection_security.py
class ConnectionSecurity:
    def __init__(self):
        self.encryption_enabled = False
        self.encryption_key = None
    
    def enable_encryption(self, key):
        self.encryption_enabled = True
        self.encryption_key = key
    
    def encrypt_message(self, message):
        if not self.encryption_enabled:
            return message
        # Implement encryption logic here
        return encrypted_message
    
    def decrypt_message(self, encrypted_message):
        if not self.encryption_enabled:
            return encrypted_message
        # Implement decryption logic here
        return decrypted_message
```

### 6. Verbindungsoptimierung

#### 6.1 Bandbreitenmanagement
```python
# Python/backend/bandwidth_manager.py
class BandwidthManager:
    def __init__(self):
        self.max_bandwidth = 1000000  # 1 Mbps
        self.current_usage = 0
        self.message_priorities = {
            'HEARTBEAT': 1,
            'COMMAND': 2,
            'TELEMETRY': 3,
            'LOG': 4
        }
    
    def can_send_message(self, message_type):
        message_size = self._get_message_size(message_type)
        if self.current_usage + message_size > self.max_bandwidth:
            return False
        self.current_usage += message_size
        return True
```

### 7. Implementierungsreihenfolge

1. **Phase 1: Grundlegende Verbindung (1 Woche)**
   - [x] Serielle Verbindung
   - [x] UDP Verbindung
   - [x] TCP Verbindung
   - [ ] Simulator Verbindung

2. **Phase 2: Verbindungsmanagement (1 Woche)**
   - [ ] Status Management
   - [ ] Fehlerbehandlung
   - [ ] Heartbeat System
   - [ ] Verbindungsprotokollierung

3. **Phase 3: Sicherheit & Optimierung (1 Woche)**
   - [ ] Verschlüsselung
   - [ ] Bandbreitenmanagement
   - [ ] Verbindungsoptimierung

### 8. Best Practices

1. **Verbindungsaufbau**
   - Immer Timeout für Verbindungsversuche setzen
   - Automatische Wiederverbindung implementieren
   - Verbindungsstatus regelmäßig überprüfen

2. **Fehlerbehandlung**
   - Alle Verbindungsfehler protokollieren
   - Benutzerfreundliche Fehlermeldungen anzeigen
   - Automatische Fehlerbehebung wo möglich

3. **Sicherheit**
   - Verschlüsselung für sensible Daten
   - Authentifizierung implementieren
   - Regelmäßige Sicherheitsüberprüfungen

4. **Performance**
   - Bandbreite effizient nutzen
   - Nachrichten priorisieren
   - Verbindungsqualität überwachen

### 9. Nächste Schritte

1. **Sofort**
   - Grundlegende Verbindungstypen implementieren
   - Verbindungsmanagement UI erstellen
   - Status Management einrichten

2. **Kurzfristig**
   - Fehlerbehandlung implementieren
   - Logging System einrichten
   - Heartbeat System entwickeln

3. **Mittelfristig**
   - Verschlüsselung implementieren
   - Bandbreitenmanagement entwickeln
   - Verbindungsoptimierung durchführen 