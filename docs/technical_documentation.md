# RZGCS Technische Dokumentation

## Inhaltsverzeichnis

1. [Architekturu00fcbersicht](#architektur%C3%BCbersicht)
2. [Backend-Komponenten](#backend-komponenten)
   - [Verbindungssystem](#verbindungssystem)
   - [MAVLink-Integration](#mavlink-integration)
   - [Nachrichtenfilterung](#nachrichtenfilterung)
   - [Sensordatenverarbeitung](#sensordatenverarbeitung)
   - [Parameterverwaltung](#parameterverwaltung)
   - [Lizenzsystem](#lizenzsystem)
3. [Frontend-Komponenten](#frontend-komponenten)
   - [UI-Architektur](#ui-architektur)
   - [QML-Module](#qml-module)
   - [3D-Visualisierung](#3d-visualisierung)
   - [Datenanbindung](#datenanbindung)
4. [Plattformu00fcbergreifende Kompatibilitu00e4t](#plattform%C3%BCbergreifende-kompatibilit%C3%A4t)
5. [Build-System](#build-system)
6. [Testframework](#testframework)
7. [API-Dokumentation](#api-dokumentation)
8. [Erweiterungsleitfaden](#erweiterungsleitfaden)

## Architekturu00fcbersicht

RZGCS ist eine Python/Qt-basierte Anwendung, die eine moderne, modulare Architektur verwendet. Die Kernkomponenten sind:

1. **Backend** (Python)
   - Verbindungsmanagement (MAVLink, serielle Verbindungen)
   - Datenverarbeitung und -analyse
   - Geschu00e4ftslogik und Feature-Management

2. **Frontend** (QML/Qt)
   - Benutzerinterfacekomponenten
   - 3D-Visualisierungen
   - Datenvisualisierung

3. **Verbindungsschicht** (PySide6)
   - Signale und Slots fu00fcr die Kommunikation zwischen Frontend und Backend
   - Datenbindung fu00fcr reaktive UI-Updates

### Architekturdiagramm

```
+-------------------------+     +-------------------------+
|       FRONTEND          |     |        BACKEND          |
| (QML, Qt Quick, Qt3D)  |     |      (Python, PySide6)  |
+-------------------------+     +-------------------------+
| - Screen01.ui.qml       |     | - main.py              |
| - PreflightView.ui.qml  |<--->| - serial_connector.py  |
| - SensorView.ui.qml     |     | - message_handler.py   |
| - ParameterView.ui.qml  |     | - license_manager.py   |
| - CalibrationView.ui.qml|     | - parameter_manager.py |
| - MotorTestView.ui.qml  |     | - sensor_manager.py    |
| - FlightView.ui.qml     |     | - connection_manager.py|
| - AngelView.ui.qml      |     | - mavlink_connector.py |
| - LicenseView.qml       |     +-------------------------+
+-------------------------+
```

## Backend-Komponenten

### Verbindungssystem

Das Verbindungssystem besteht aus mehreren Komponenten:

#### ConnectionManager

`connection_manager.py` ist eine plattformunabhu00e4ngige Abstraktionsschicht, die die Unterschiede zwischen verschiedenen Betriebssystemen (Windows, macOS, Linux) verwaltet. Hauptfunktionen:

- Erkennung verfu00fcgbarer serieller Ports basierend auf dem Betriebssystem
- Erstellung plattformspezifischer Verbindungsstrings
- Bereitstellung von Standardverbindungsparametern
- Behandlung von Plattformunterschieden bei der Gerhautekennung

**Beispiel:**
```python
class ConnectionManager:
    def __init__(self):
        self.system_platform = platform.system().lower()
        
    def get_available_ports(self):
        # Plattformspezifische Porterkennungslogik
        if self.system_platform == 'windows':
            # Windows-spezifischer Code
        elif self.system_platform == 'darwin':  # macOS
            # macOS-spezifischer Code
        elif self.system_platform == 'linux':
            # Linux-spezifischer Code
```

#### SerialConnector

`serial_connector.py` verwaltet die tatsu00e4chliche Verbindung zum Flugcontroller oder Simulator. Hauptfunktionen:

- Verbindungsaufbau und -verwaltung
- Koordination zwischen MAVLink-Verbindung und Datenverarbeitung
- Bereitstellung von Verbindungsstatus und verfu00fcgbaren Ports an die UI

### MAVLink-Integration

Die MAVLink-Integration erfolgt u00fcber verschiedene Klassen:

#### MAVLinkConnector

`mavlink_connector.py` stellt eine abstrakte Schnittstelle fu00fcr MAVLink-Verbindungen bereit, mit Implementierungen sowohl fu00fcr direkte PyMAVLink-Verbindungen als auch MAVSDK-basierte Verbindungen.

#### MessageHandler

`message_handler.py` verarbeitet eingehende MAVLink-Nachrichten, extrahiert relevante Daten und leitet sie an die entsprechenden Subsysteme weiter. Besonders wichtig ist das implementierte Nachrichtenfiltersystem:

- Caching der neuesten Werte jedes Nachrichtentyps
- Filterung von Nachrichten basierend auf Wertu00e4nderungen
- Erzwingen von Mindestzeit-Intervallen zwischen Nachrichten
- Sicherstellung, dass kritische Nachrichten immer protokolliert werden

**Beispiel des Nachrichtenfiltersystems:**
```python
def process_messages(self):
    # Verarbeite maximal 100 Nachrichten pro Aufruf
    for i in range(100):
        msg = self._mavlink_connection.recv_match(blocking=False)
        if not msg:
            break
            
        # Nachrichtentyp extrahieren
        msg_type = msg.get_type()
        
        # Pru00fcfen, ob sich der Wert signifikant geu00e4ndert hat
        if self._should_process_message(msg_type, msg):
            # Nachricht verarbeiten
            self._process_message(msg_type, msg)
            # Nachrichtencache aktualisieren
            self._update_message_cache(msg_type, msg)
```

### Nachrichtenfilterung

Eine besondere Eigenschaft von RZGCS ist das zweistufige Nachrichtenfiltersystem:

1. **Allgemeine Nachrichtenfilterung** in `message_handler.py`:
   - Reduziert die Protokollierung wiederholter Nachrichten
   - Verwendet konfigurierbare Schwellenwerte fu00fcr Wertu00e4nderungen
   - Stellt sicher, dass kritische Nachrichten immer angezeigt werden

2. **Spezieller Preflight-Filter** fu00fcr die Preflight-View:
   - Filtert gezielt Systeminformationen aus Logs
   - Extrahiert Frame-Typ, RCOut, MicoAir743, ChibiOS, ArduCopter-Version und PreArm-Warnungen
   - Zeigt diese in einem vergru00f6u00dferten Log-Bereich (30% statt 10% der Hu00f6he) an
   - Verwendet gru00f6u00dfere Schrift (16px) und Hervorhebung fu00fcr bessere Lesbarkeit

### Sensordatenverarbeitung

Die Sensordatenverarbeitung wird vom `sensor_manager.py` und `sensorviewmodel.py` u00fcbernommen:

- Extraktion und Normalisierung von Sensordaten aus MAVLink-Nachrichten
- Bereitstellung reaktiver Datenmodelle fu00fcr die UI
- Aufbereitung von Sensordaten fu00fcr Visualisierungen

### Parameterverwaltung

Die Parameterverwaltung in `parameter_manager.py` und `parameter_model.py` ermu00f6glicht:

- Laden und Speichern von Flugcontroller-Parametern
- Filtern und Kategorisieren von Parametern
- u00c4ndern von Parameterwerten mit Validierung
- Reaktive Aktualisierung der UI bei Parameteru00e4nderungen

### Lizenzsystem

Das Lizenzsystem in `license_manager.py` und `license_ui.py` implementiert:

- Verschiedene Lizenztypen (Basic, Professional, Enterprise)
- Feature-basierte Zugangskontrolle
- Sichere Lizenzaktivierung und -validierung
- Maschinenbindung von Lizenzen

**Beispiel der Feature-Zugangskontrolle:**
```python
def is_feature_enabled(self, feature_name):
    # Basic-Features sind immer verfu00fcgbar
    if feature_name in self._feature_matrix['basic']:
        return True
        
    # Pru00fcfe, ob eine gu00fcltige Lizenz vorhanden ist
    if not self.license_valid:
        return False
        
    # Pru00fcfe, ob das Feature in der aktuellen Lizenzstufe enthalten ist
    return feature_name in self._feature_matrix.get(self.license_type, [])
```

## Frontend-Komponenten

### UI-Architektur

Die Benutzeroberflu00e4che ist in modulare QML-Komponenten aufgeteilt:

- `Screen01.ui.qml`: Hauptfenster mit Tab-Leiste und Rahmen
- Verschiedene View-Komponenten fu00fcr spezifische Funktionen
- Wiederverwendbare UI-Elemente wie Listen, Delegaten und Dialoge

### QML-Module

Die Anwendung verwendet mehrere QML-Module:

- `RZGCS`: Hauptmodul mit den meisten UI-Komponenten
- `QtQuick`: Basis-UI-Elemente
- `QtQuick.Controls`: Erweiterte UI-Steuerelemente
- `QtQuick.Layouts`: Layout-Management
- `QtQuick3D`: 3D-Visualisierungen

### 3D-Visualisierung

Die 3D-Visualisierungen werden mit QtQuick3D implementiert:

- `AnimView.qml`: Drohnenanimation in der Preflight-View
- `Accel3DView.qml`: 3D-Visualisierung fu00fcr die Beschleunigungssensor-Kalibrierung

### Datenanbindung

Die Datenanbindung zwischen Frontend und Backend erfolgt u00fcber:

- Qt Properties und Signale/Slots
- QML-Context-Properties fu00fcr Controller-Instanzen
- Listen- und Tabellenmodelle fu00fcr strukturierte Daten

## Plattformu00fcbergreifende Kompatibilitu00e4t

RZGCS ist fu00fcr plattformu00fcbergreifende Kompatibilitu00e4t konzipiert:

### Windows-Kompatibilitu00e4t

- COM-Port-Erkennung und -Verwaltung
- Windows-spezifische Pfade und Berechtigungen
- DirectX-Unterstu00fctzung fu00fcr 3D-Visualisierungen

### macOS-Kompatibilitu00e4t

- Erkennung und Behandlung von macOS-spezifischen Geru00e4tepfaden (`/dev/cu.*`)
- Berechtigungsmanagement fu00fcr USB-Zugriff
- Metal-Unterstu00fctzung fu00fcr 3D-Visualisierungen

### Linux-Kompatibilitu00e4t

- Unterstu00fctzung fu00fcr verschiedene Linux-Distributionen
- Berechtigungsverwaltung fu00fcr serielle Ports
- OpenGL-Unterstu00fctzung fu00fcr 3D-Visualisierungen

## Build-System

RZGCS verwendet ein flexibles Build-System:

- Python-basierter Build-Prozess
- CMake-Integration fu00fcr C++-Komponenten
- QML-Bundling mit Qt-Ressourcensystem
- Plattformspezifische Packaging-Skripte

## Testframework

Das Testframework umfasst:

- Unit-Tests fu00fcr Backend-Komponenten
- Integration-Tests fu00fcr Systeme und Subsysteme
- UI-Tests fu00fcr Frontend-Komponenten
- Plattformspezifische Tests fu00fcr OS-Kompatibilitu00e4t
- Lizenzsystem-Tests

**Beispiel eines Testbefehls:**
```bash
python tests/run_tests.py --all --verbose
```

## API-Dokumentation

### Backend-API

#### SerialConnector

```python
class SerialConnector(QObject):
    """Verwaltet die serielle Verbindung zur Drohne und koordiniert die Sensordatenu00fcbertragung."""
    
    # Signale
    availablePortsChanged = Signal(list)   # Liste verfu00fcgbarer Ports
    connectedChanged = Signal(bool)        # Verbindungsstatus
    portChanged = Signal(str)              # Aktueller Port
    baudRateChanged = Signal(int)          # Aktuelle Baudrate
    
    # Methoden
    def connect(self)                      # Verbindet zum ausgewu00e4hlten Port
    def disconnect(self)                   # Trennt die Verbindung
    def load_ports(self)                   # Lu00e4dt verfu00fcgbare Ports
    def setPort(self, port)                # Setzt den Port
    def setBaudRate(self, baud_rate)       # Setzt die Baudrate
    
    # Properties
    @Property(bool, notify=connectedChanged)
    def connected(self)                    # Gibt den Verbindungsstatus zuru00fcck
    
    @Property(str, notify=portChanged)
    def port(self)                         # Gibt den aktuellen Port zuru00fcck
    
    @Property('QVariantList', notify=availablePortsChanged)
    def availablePorts(self)              # Gibt verfu00fcgbare Ports zuru00fcck
```

#### LicenseManager

```python
class LicenseManager(QObject):
    """Verwaltet Lizenzen und Feature-Zugriffskontrollen."""
    
    # Signale
    license_changed = Signal()             # Lizenzu00e4nderung
    
    # Methoden
    def activate_license(self, license_key)  # Aktiviert eine Lizenz
    def deactivate_license(self)           # Deaktiviert die Lizenz
    def is_feature_enabled(self, feature)   # Pru00fcft, ob ein Feature aktiviert ist
    
    # Properties
    @property
    def license_valid(self)                # Gibt an, ob eine gu00fcltige Lizenz vorhanden ist
    
    @property
    def license_type(self)                 # Gibt den Lizenztyp zuru00fcck
```

### Frontend-API

#### LicenseView

```qml
Item {
    // Controller-Referenz
    property var controller: null
    
    // UI-Elemente fu00fcr Lizenzaktivierung und -anzeige
    TextField {
        id: licenseKeyInput
        placeholderText: "Lizenzschlu00fcssel eingeben"
    }
    
    Button {
        text: "Aktivieren"
        onClicked: {
            var result = controller.activateLicense(licenseKeyInput.text);
            // Ergebnis verarbeiten
        }
    }
    
    // Anzeige des Lizenzstatus
    Text {
        text: "Lizenzstatus: " + (controller.isLicensed ? "Aktiv" : "Inaktiv")
    }
    
    Text {
        text: "Lizenztyp: " + controller.licenseType
    }
}
```

#### AngelView

```qml
Item {
    id: root
    
    // Controller-Referenz
    property var controller: null
    
    // Feature-Status basierend auf Lizenz pru00fcfen
    property bool isFeatureEnabled: licenseController ? 
                                   licenseController.isFeatureEnabled("angel_mode") : 
                                   false
    
    // Inhalt nur anzeigen, wenn Feature aktiviert ist
    Rectangle {
        visible: root.isFeatureEnabled
        // Kartendarstellung und Flugpfade
    }
    
    // Upgrade-Hinweis anzeigen, wenn Feature nicht aktiviert ist
    Rectangle {
        visible: !root.isFeatureEnabled
        // Upgrade-Dialog
    }
}
```

## Erweiterungsleitfaden

### Hinzufu00fcgen neuer Features

1. **Backend-Komponente erstellen**
   - Neue Python-Klasse im `backend`-Verzeichnis erstellen
   - QObject-Basisklasse verwenden fu00fcr Signal/Slot-Integration
   - Features in der Lizenzverwaltung registrieren

2. **UI-Komponente erstellen**
   - Neue QML-Datei im `RZGCSContent`-Verzeichnis erstellen
   - Controller-Property fu00fcr Backend-Anbindung definieren
   - Feature-Pru00fcfung implementieren

3. **Integration in die Hauptanwendung**
   - Backend-Controller in `main.py` registrieren
   - UI-Komponente in `qmldir` registrieren
   - Tab in `Screen01.ui.qml` hinzufu00fcgen

### Integration eigener Hardware

1. **Hardware-Connector erstellen**
   - Von `DroneConnectorBase` ableiten
   - Hardware-spezifische Kommunikationsprotokolle implementieren
   - Daten in MAVLink-Nachrichten konvertieren

2. **UI-Anpassungen vornehmen**
   - Hardware-spezifische Steuerelemente hinzufu00fcgen
   - Spezielle Visualisierungen implementieren
