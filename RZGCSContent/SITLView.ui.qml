import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtLocation 5.15
import QtPositioning 5.15
import QtQuick.Controls.Material 2.15

import RZGCS 1.0

Item {
    id: sitlView
    width: parent.width
    height: parent.height
    
    property var sitlViewModel: null // Wird im Backend gesetzt
    
    // Status-Properties
    property bool isSimulationRunning: sitlViewModel ? sitlViewModel.isSimulationRunning : false
    property string statusMessage: sitlViewModel ? sitlViewModel.statusMessage : "Inaktiv"
    property real downloadProgress: sitlViewModel ? sitlViewModel.downloadProgress : 0.0
    
    // Home-Position
    property var homeMarker: null
    
    // Zeigt eine Nachricht an
    function showMessage(text) {
        messagePopup.text = text;
        messagePopup.open();
    }
    
    // Verbindet mit der SITL-Simulation
    function connectToSITL(connectionString) {
        console.log("Connecting to SITL: " + connectionString);
        // Prüfe, ob serialConnector existiert und definiert ist
        if (typeof serialConnector !== "undefined" && serialConnector) {
            console.log("serialConnector ist verfügbar");
            try {
                serialConnector.disconnect();
                // Kurze Verzögerung, um sicherzustellen, dass die vorherige Verbindung getrennt wurde
                connectTimer.connectionString = connectionString;
                connectTimer.start();
            } catch (e) {
                console.error("Fehler beim Verbinden mit SITL:", e);
                showMessage("Fehler beim Verbinden mit SITL: " + e);
            }
        } else {
            console.error("serialConnector ist nicht verfügbar");
            showMessage("serialConnector ist nicht verfügbar. Bitte Anwendung neu starten.");
        }
    }
    
    // Timer für verzögerte Verbindung
    Timer {
        id: connectTimer
        interval: 1000
        repeat: false
        property string connectionString: ""
        onTriggered: {
            if (serialConnector && connectionString !== "") {
                console.log("Connecting with delay to: " + connectionString);
                serialConnector.connect(connectionString);
            }
        }
    }
    
    // Aktualisiert die Home-Position
    function updateHomePosition(coordinate) {
        if (sitlViewModel) {
            sitlViewModel.setHomePosition(coordinate.latitude, coordinate.longitude);
        }
    }
    
    GridLayout {
        anchors.fill: parent
        anchors.margins: 10
        columns: 2
        rows: 2
        
        // Karte für die Auswahl des Start-Orts
        Item {
            Layout.column: 0
            Layout.row: 0
            Layout.rowSpan: 2
            Layout.fillHeight: true
            Layout.fillWidth: true
            Layout.preferredWidth: parent.width * 0.7
            
            Plugin {
                id: mapPlugin
                name: "osm" // OpenStreetMap
            }
            
            Map {
                id: map
                anchors.fill: parent
                plugin: mapPlugin
                center: QtPositioning.coordinate(49.445232, 7.769488) // Kaiserslautern, Deutschland
                zoomLevel: 14
                
                // Map-Komponenten
                MapItemView {
                    id: markerView
                    model: ListModel { id: markerModel }
                    delegate: MapQuickItem {
                        id: marker
                        coordinate: QtPositioning.coordinate(model.latitude, model.longitude)
                        anchorPoint.x: image.width * 0.5
                        anchorPoint.y: image.height
                        sourceItem: Column {
                            Image {
                                id: image
                                width: 32
                                height: 32
                                source: "Assets/markers/home_marker.svg"
                                sourceSize.width: 32
                                sourceSize.height: 32
                            }
                            Text {
                                anchors.horizontalCenter: parent.horizontalCenter
                                text: "H"
                                color: "white"
                                style: Text.Outline
                                styleColor: "black"
                                font.pointSize: 10
                                font.bold: true
                            }
                        }
                    }
                }
                
                // Klick-Handler für Marker-Platzierung
                MouseArea {
                    anchors.fill: parent
                    onClicked: {
                        // Konvertiere Mausposition zu Geo-Koordinaten
                        var coordinate = map.toCoordinate(Qt.point(mouseX, mouseY))
                        
                        // Markermodel aktualisieren
                        markerModel.clear()
                        markerModel.append({
                            "latitude": coordinate.latitude,
                            "longitude": coordinate.longitude
                        })
                        
                        // ViewModel aktualisieren
                        updateHomePosition(coordinate)
                    }
                }
                
                Component.onCompleted: {
                    // Initial einen Marker setzen
                    markerModel.append({
                        "latitude": center.latitude,
                        "longitude": center.longitude
                    })
                    
                    // ViewModel aktualisieren
                    updateHomePosition(center)
                }
            }
        }
        
        // Steuerungselemente (rechts oben)
        Item {
            Layout.column: 1
            Layout.row: 0
            Layout.fillWidth: true
            Layout.preferredWidth: parent.width * 0.3
            Layout.preferredHeight: parent.height * 0.5
            
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 10
                spacing: 15
                
                Label {
                    text: "SITL Simulation"
                    font.bold: true
                    font.pointSize: 14
                }
                
                // Version auswählen
                RowLayout {
                    Layout.fillWidth: true
                    Label {
                        text: "Version:"
                        Layout.preferredWidth: 70
                    }
                    ComboBox {
                        id: versionComboBox
                        Layout.fillWidth: true
                        model: ["Stable", "Beta", "Latest"]
                        currentIndex: 0
                        onCurrentTextChanged: {
                            if (sitlViewModel) {
                                sitlViewModel.versionType = currentText
                            }
                        }
                    }
                }
                
                // Heading einstellen
                RowLayout {
                    Layout.fillWidth: true
                    Label {
                        text: "Heading:"
                        Layout.preferredWidth: 70
                    }
                    Slider {
                        id: headingSlider
                        Layout.fillWidth: true
                        from: 0
                        to: 359
                        stepSize: 1
                        value: 0
                        onValueChanged: {
                            if (sitlViewModel) {
                                sitlViewModel.heading = value
                            }
                            headingValueLabel.text = Math.round(value) + "°"
                        }
                    }
                    Label {
                        id: headingValueLabel
                        text: "0°"
                        Layout.preferredWidth: 40
                    }
                }
                
                // Simulationsgeschwindigkeit
                RowLayout {
                    Layout.fillWidth: true
                    Label {
                        text: "Sim-Speed:"
                        Layout.preferredWidth: 70
                    }
                    Slider {
                        id: speedSlider
                        Layout.fillWidth: true
                        from: 1
                        to: 10
                        stepSize: 1
                        value: 1
                        onValueChanged: {
                            if (sitlViewModel) {
                                sitlViewModel.simSpeed = value
                            }
                            speedValueLabel.text = Math.round(value) + "x"
                        }
                    }
                    Label {
                        id: speedValueLabel
                        text: "1x"
                        Layout.preferredWidth: 30
                    }
                }
                
                // Fortschrittsanzeige für Downloads
                ProgressBar {
                    id: downloadProgressBar
                    Layout.fillWidth: true
                    value: downloadProgress
                    visible: downloadProgress > 0 && downloadProgress < 1
                }
                
                // Statusanzeige
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 30
                    color: "#f0f0f0"
                    border.color: "#cccccc"
                    radius: 5
                    
                    Label {
                        anchors.fill: parent
                        anchors.margins: 5
                        text: statusMessage
                        horizontalAlignment: Text.AlignLeft
                        verticalAlignment: Text.AlignVCenter
                        elide: Text.ElideRight
                        font.italic: true
                    }
                }
            }
        }
        
        // Fahrzeug-Buttons (rechts unten)
        Item {
            Layout.column: 1
            Layout.row: 1
            Layout.fillHeight: true
            Layout.fillWidth: true
            Layout.preferredWidth: parent.width * 0.3
            Layout.preferredHeight: parent.height * 0.5
            
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 10
                spacing: 10
                
                Label {
                    text: "Fahrzeugtyp wählen:"
                    font.bold: true
                }
                
                Button {
                    id: quadcopterButton
                    Layout.fillWidth: true
                    Layout.preferredHeight: 60
                    text: "Quadcopter"
                    enabled: !isSimulationRunning
                    Material.background: Material.Green
                    
                    onClicked: {
                        console.log("Starting Quadcopter Simulation")
                        if (sitlViewModel) {
                            sitlViewModel.startCopterSimulation()
                        }
                    }
                }
                
                Button {
                    id: planeButton
                    Layout.fillWidth: true
                    Layout.preferredHeight: 60
                    text: "Flugzeug"
                    enabled: !isSimulationRunning
                    Material.background: Material.Blue
                    
                    onClicked: {
                        console.log("Starting Plane Simulation")
                        if (sitlViewModel) {
                            sitlViewModel.startPlaneSimulation()
                        }
                    }
                }
                
                Button {
                    id: roverButton
                    Layout.fillWidth: true
                    Layout.preferredHeight: 60
                    text: "Rover"
                    enabled: !isSimulationRunning
                    Material.background: Material.Amber
                    
                    onClicked: {
                        console.log("Starting Rover Simulation")
                        if (sitlViewModel) {
                            sitlViewModel.startRoverSimulation()
                        }
                    }
                }
                
                Button {
                    id: heliButton
                    Layout.fillWidth: true
                    Layout.preferredHeight: 60
                    text: "Helikopter"
                    enabled: !isSimulationRunning
                    Material.background: Material.Purple
                    
                    onClicked: {
                        console.log("Starting Helicopter Simulation")
                        if (sitlViewModel) {
                            sitlViewModel.startHeliSimulation()
                        }
                    }
                }
                
                Button {
                    id: stopButton
                    Layout.fillWidth: true
                    Layout.preferredHeight: 60
                    text: "Simulation stoppen"
                    enabled: isSimulationRunning
                    Material.background: Material.Red
                    
                    onClicked: {
                        console.log("Stopping Simulation")
                        if (sitlViewModel) {
                            sitlViewModel.stopSimulation()
                        }
                    }
                }
            }
        }
    }
    
    // Popup für Nachrichten
    Popup {
        id: messagePopup
        x: (parent.width - width) / 2
        y: (parent.height - height) / 2
        width: 400
        height: 150
        modal: true
        focus: true
        closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside
        
        property alias text: messageLabel.text
        
        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 20
            
            Label {
                id: messageLabel
                Layout.fillWidth: true
                Layout.fillHeight: true
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                wrapMode: Text.WordWrap
            }
            
            Button {
                text: "OK"
                Layout.alignment: Qt.AlignHCenter
                onClicked: messagePopup.close()
            }
        }
    }
    
    // Verwende einfache Connections statt komplizierter Timer und direkter Verbindung
    // Da das sitlViewModel vom Backend bereitgestellt wird, ist ein einfacher Ansatz besser
    Connections {
        // target als null setzen und später im onCompleted aktualisieren
        target: null
        id: sitlConnections
        
        // Signal-Handler für die SITL-Signale
        function onErrorOccurred(errorMessage) {
            showMessage(errorMessage)
        }
        
        function onSimulationStarted(vehicleType, connectionString) {
            console.log("SITL: Simulation gestartet für " + vehicleType)
            showMessage("Simulation gestartet für " + vehicleType + "\nVerbindung wird hergestellt...")
        }
        
        function onAutoConnectRequested(connectionString) {
            console.log("Auto-connect requested to: " + connectionString)
            connectToSITL(connectionString)
        }
        
        function onSimulationStopped() {
            showMessage("Simulation beendet")
            if (typeof serialConnector !== "undefined" && serialConnector && serialConnector.connected) {
                serialConnector.disconnect()
            }
        }
    }
    
    // Target nach Komponenten-Initialisierung setzen
    Component.onCompleted: {
        console.log("SITLView: Component.onCompleted")
        // Direkter Zugriff auf das sitlViewModel, das in der QML-Engine registriert ist
        sitlConnections.target = sitlViewModel
        console.log("SITL-Connections initialisiert mit sitlViewModel")
    }
    
    // Verbindungsstatus überwachen
    Connections {
        // Prüfe, ob serialConnector existiert, ansonsten verwende null als Target
        target: typeof serialConnector !== "undefined" && serialConnector ? serialConnector : null
        
        function onConnectedChanged() {
            // Erneut prüfen, ob serialConnector existiert und connected ist
            if (typeof serialConnector !== "undefined" && serialConnector && serialConnector.connected) {
                showMessage("Verbunden mit SITL-Simulation!\nSensordaten werden jetzt angezeigt.")
            }
        }
    }
}
