# Implementierungsplan: QML Frontend Modernisierung

## Analyse der bestehenden Struktur

### Aktuelle Architektur (Screen01.ui.qml)
- **Hauptcontainer**: ColumnLayout mit StatusBar oben und Content unten
- **Tab-System**: TabBar mit 9 Tabs (Connection, MAVLink 2, Preflight, Parameter, Calibration, Motor Test, Firmware, Flight, Sensor Dashboard)
- **Content-Bereich**: StackLayout mit Loader-Komponenten für dynamisches Laden
- **Message-Panel**: Immer sichtbar rechts (MessageList.qml)
- **Context Properties**: Werden über Python-Backend bereitgestellt

### Backend-Integration (dronekit_main.py)
- **Context Properties**: messageManager, serialConnector, firmwareViewModel, etc.
- **Signal-Verbindungen**: Zwischen Backend-Klassen und QML-Komponenten
- **Loader-Mechanismus**: Dynamisches Laden von QML-Komponenten mit Context Property-Übergabe

## Implementierungsplan

### Phase 1: Zentrale Theme-Konfiguration (Priorität: Hoch)

#### 1.1 Theme-System erstellen
**Datei**: `RZGCSContent/Utils/DroneTheme.qml`
```qml
pragma Singleton
import QtQuick 2.15

QtObject {
    // Farben
    readonly property color backgroundColor: "#181c1f"
    readonly property color panelColor: "#232b2e"
    readonly property color borderColor: "#2e3a3e"
    readonly property color accentColor: "#00e0c6"
    readonly property color textColor: "#cccccc"
    readonly property color errorColor: "#ff6666"
    readonly property color warningColor: "#ffb84b"
    readonly property color successColor: "#4caf50"
    
    // Schriftgrößen
    readonly property int fontSizeSmall: 10
    readonly property int fontSizeDefault: 12
    readonly property int fontSizeMedium: 14
    readonly property int fontSizeLarge: 16
    readonly property int fontSizeTitle: 18
    
    // Abstände
    readonly property int spacingSmall: 4
    readonly property int spacingDefault: 8
    readonly property int spacingMedium: 12
    readonly property int spacingLarge: 16
    
    // Ecken-Radien
    readonly property int radiusSmall: 4
    readonly property int radiusDefault: 8
    readonly property int radiusLarge: 12
}
```

#### 1.2 qmldir-Datei erstellen
**Datei**: `RZGCSContent/Utils/qmldir`
```
module Utils
singleton DroneTheme 1.0 DroneTheme.qml
```

#### 1.3 Theme in bestehende Komponenten integrieren
- **Screen01.ui.qml**: Farben durch Theme-Properties ersetzen
- **MessageList.qml**: Theme-Integration
- **ParameterTab.qml**: Theme-Integration

### Phase 2: Wiederverwendbare Basis-Komponenten (Priorität: Hoch)

#### 2.1 DroneButton-Komponente
**Datei**: `RZGCSContent/Components/DroneButton.qml`
```qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import "../Utils"

Button {
    id: root
    property string buttonType: "primary"
    property color primaryColor: DroneTheme.accentColor
    property color secondaryColor: "#c27ba0"
    property color textColor: "#ffffff"
    
    background: Rectangle {
        color: root.enabled ? 
               (root.buttonType === "primary" ? root.primaryColor : root.secondaryColor) : 
               "#555555"
        radius: DroneTheme.radiusSmall
        opacity: root.hovered ? 0.8 : 1.0
        
        Behavior on opacity {
            NumberAnimation { duration: 150 }
        }
    }
    
    contentItem: Text {
        text: root.text
        color: root.textColor
        font.pixelSize: DroneTheme.fontSizeDefault
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
    }
    
    scale: root.pressed ? 0.95 : 1.0
    Behavior on scale {
        NumberAnimation { duration: 100 }
    }
}
```

#### 2.2 StatusPanel-Komponente
**Datei**: `RZGCSContent/Components/StatusPanel.qml`
```qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../Utils"

Rectangle {
    id: root
    property alias title: titleText.text
    property alias content: contentArea.children
    property bool showBorder: true
    
    color: DroneTheme.panelColor
    radius: DroneTheme.radiusDefault
    border.color: showBorder ? DroneTheme.borderColor : "transparent"
    border.width: showBorder ? 1 : 0
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: DroneTheme.spacingLarge
        spacing: DroneTheme.spacingMedium
        
        Text {
            id: titleText
            color: DroneTheme.accentColor
            font.pixelSize: DroneTheme.fontSizeTitle
            font.bold: true
        }
        
        Item {
            id: contentArea
            Layout.fillWidth: true
            Layout.fillHeight: true
        }
    }
}
```

#### 2.3 ConnectionAlert-Komponente
**Datei**: `RZGCSContent/Components/ConnectionAlert.qml`
```qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../Utils"

Rectangle {
    id: root
    property bool isConnected: false
    property real packetLossRate: 0.0
    property real heartbeatFrequency: 0.0
    
    readonly property color okColor: DroneTheme.successColor
    readonly property color warnColor: DroneTheme.warningColor
    readonly property color errorColor: DroneTheme.errorColor
    
    property int statusLevel: 
        !isConnected ? 2 :
        packetLossRate > 10 ? 1 :
        heartbeatFrequency < 0.5 ? 1 : 0
    
    width: 200; height: 50
    radius: DroneTheme.radiusSmall
    border.width: 2
    border.color: statusLevel === 2 ? errorColor 
                 : statusLevel === 1 ? warnColor 
                 : okColor
    color: Qt.rgba(0, 0, 0, 0.5)
    
    // Pulsing-Animation bei kritischem Status
    SequentialAnimation on scale {
        running: statusLevel === 2
        loops: Animation.Infinite
        NumberAnimation { to: 1.1; duration: 500 }
        NumberAnimation { to: 1.0; duration: 500 }
    }
    
    RowLayout {
        anchors.fill: parent
        anchors.margins: DroneTheme.spacingDefault
        spacing: DroneTheme.spacingDefault
        
        Rectangle {
            id: led
            width: 16; height: 16; radius: 8
            color: statusLevel === 2 ? errorColor 
                   : statusLevel === 1 ? warnColor 
                   : okColor
            
            Timer {
                interval: statusLevel === 2 ? 600 : 0
                running: statusLevel === 2
                repeat: true
                onTriggered: led.opacity = led.opacity === 1 ? 0.3 : 1
            }
        }
        
        Text {
            text: {
                switch(root.statusLevel) {
                    case 2: return "KEINE VERBINDUNG"
                    case 1: return "SCHWACHE VERBINDUNG"
                    default: return "VERBUNDEN"
                }
            }
            color: statusLevel === 2 ? errorColor 
                   : statusLevel === 1 ? warnColor 
                   : okColor
            font.pixelSize: DroneTheme.fontSizeMedium
            font.bold: true
        }
    }
}
```

#### 2.4 qmldir für Components
**Datei**: `RZGCSContent/Components/qmldir`
```
module Components
DroneButton 1.0 DroneButton.qml
StatusPanel 1.0 StatusPanel.qml
ConnectionAlert 1.0 ConnectionAlert.qml
```

### Phase 3: Performance-Optimierung (Priorität: Mittel)

#### 3.1 TelemetryDataManager
**Datei**: `RZGCSContent/Utils/TelemetryDataManager.qml`
```qml
pragma Singleton
import QtQuick 2.15

QtObject {
    id: root
    property var currentData: ({})
    property var pendingUpdates: ({})
    property int maxUpdateRate: 30 // Hz
    
    Timer {
        id: batchTimer
        interval: 1000 / root.maxUpdateRate
        running: true
        repeat: true
        
        onTriggered: {
            if (Object.keys(root.pendingUpdates).length > 0) {
                root.processPendingUpdates()
            }
        }
    }
    
    function updateField(field, value) {
        root.pendingUpdates[field] = {
            value: value,
            timestamp: Date.now()
        }
    }
    
    function processPendingUpdates() {
        for (var field in root.pendingUpdates) {
            root.currentData[field] = root.pendingUpdates[field].value
        }
        root.pendingUpdates = {}
        root.batchDataUpdated()
    }
    
    signal batchDataUpdated()
}
```

### Phase 4: Interaktive Grafiken (Priorität: Niedrig)

#### 4.1 TelemetryChart-Komponente
**Datei**: `RZGCSContent/Components/TelemetryChart.qml`
- Implementierung der QtCharts-basierten Komponente
- Performance-Optimierung mit GPU-Beschleunigung
- Interaktive Features (Zoom, Pan, Tooltips)

#### 4.2 TelemetryDashboard
**Datei**: `RZGCSContent/Components/TelemetryDashboard.qml`
- Multi-Parameter-Dashboard
- Kombinierte und Grid-Ansicht
- Export-Funktionalität

### Phase 5: Integration in bestehende Architektur

#### 5.1 Screen01.ui.qml anpassen
- **Theme-Integration**: Alle Farben durch Theme-Properties ersetzen
- **Komponenten-Integration**: DroneButton und StatusPanel verwenden
- **ConnectionAlert**: In StatusBar integrieren
- **Performance**: TelemetryDataManager für Echtzeit-Daten

#### 5.2 Backend-Integration erweitern
- **Neue Context Properties**: DroneTheme, TelemetryDataManager
- **Signal-Verbindungen**: Für neue Komponenten
- **Loader-Mechanismus**: Für neue Komponenten erweitern

## Implementierungsreihenfolge

### Woche 1: Phase 1 (Theme-System)
1. **Tag 1-2**: DroneTheme.qml und qmldir erstellen
2. **Tag 3-4**: Theme in Screen01.ui.qml integrieren
3. **Tag 5**: Theme in MessageList.qml integrieren

### Woche 2: Phase 2 (Basis-Komponenten)
1. **Tag 1-2**: DroneButton.qml erstellen und testen
2. **Tag 3-4**: StatusPanel.qml erstellen und testen
3. **Tag 5**: ConnectionAlert.qml erstellen und testen

### Woche 3: Phase 3 (Performance)
1. **Tag 1-2**: TelemetryDataManager.qml erstellen
2. **Tag 3-4**: Performance-Optimierung in bestehenden Komponenten
3. **Tag 5**: Testing und Debugging

### Woche 4: Phase 4 (Interaktive Grafiken)
1. **Tag 1-3**: TelemetryChart.qml implementieren
2. **Tag 4-5**: TelemetryDashboard.qml implementieren

### Woche 5: Phase 5 (Integration)
1. **Tag 1-2**: Vollständige Integration in Screen01.ui.qml
2. **Tag 3-4**: Backend-Integration erweitern
3. **Tag 5**: Testing und Finalisierung

## Risiken und Mitigation

### Risiko 1: Backend-Kompatibilität
- **Risiko**: Neue Komponenten brechen bestehende Backend-Verbindungen
- **Mitigation**: Schrittweise Integration, umfassendes Testing nach jeder Phase

### Risiko 2: Performance-Probleme
- **Risiko**: Neue Komponenten verlangsamen die Anwendung
- **Mitigation**: Performance-Monitoring, Throttling-Mechanismen

### Risiko 3: QML-Loader-Probleme
- **Risiko**: Dynamisches Laden von neuen Komponenten funktioniert nicht
- **Mitigation**: Konsistente Loader-Struktur, Fehlerbehandlung

## Testing-Strategie

### Unit-Tests für jede Komponente
- **DroneButton**: Hover- und Klick-Events
- **StatusPanel**: Content-Rendering
- **ConnectionAlert**: Status-Übergänge
- **TelemetryChart**: Daten-Updates

### Integration-Tests
- **Backend-Integration**: Context Properties funktionieren
- **Signal-Verbindungen**: Datenfluss zwischen Backend und QML
- **Performance**: Echtzeit-Daten ohne Verzögerungen

### UI/UX-Tests
- **Responsive Design**: Verschiedene Bildschirmgrößen
- **Accessibility**: Tastatur-Navigation, Screen Reader
- **Cross-Platform**: Windows, macOS, Linux

## Erfolgskriterien

### Phase 1 (Theme)
- [ ] Alle Farben zentral konfigurierbar
- [ ] Konsistentes Design in allen Komponenten
- [ ] Einfache Anpassung des gesamten Looks

### Phase 2 (Komponenten)
- [ ] Wiederverwendbare DroneButton-Komponente
- [ ] StatusPanel für einheitliche Panel-Darstellung
- [ ] ConnectionAlert für auffällige Verbindungswarnungen

### Phase 3 (Performance)
- [ ] 30 Hz Update-Rate für Echtzeit-Daten
- [ ] GPU-Beschleunigung für Charts
- [ ] Batch-Updates für bessere Performance

### Phase 4 (Grafiken)
- [ ] Interaktive Telemetrie-Charts
- [ ] Multi-Parameter-Dashboard
- [ ] Export-Funktionalität

### Phase 5 (Integration)
- [ ] Vollständige Integration in bestehende Architektur
- [ ] Backend-Kompatibilität gewährleistet
- [ ] Keine Regressionen in bestehenden Features

## Nächste Schritte

1. **Sofort**: Phase 1 beginnen (Theme-System)
2. **Parallel**: Dokumentation der bestehenden Struktur vervollständigen
3. **Kontinuierlich**: Testing nach jeder Phase
4. **Feedback**: Regelmäßige Überprüfung der Implementierung

Dieser Plan gewährleistet eine schrittweise, sichere Modernisierung der QML-Oberfläche ohne Beeinträchtigung der bestehenden Funktionalität.
