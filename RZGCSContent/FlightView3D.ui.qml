import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtWebEngine

// Hauptansicht für den Flight-Tab mit 3D-Karte
Item {
    id: flightView3D
    anchors.fill: parent
    
    property var flightMapBridge: null
    
    // Haupt-Layout
    ColumnLayout {
        anchors.fill: parent
        spacing: 0
        
        // Obere Werkzeugleiste
        Rectangle {
            Layout.fillWidth: true
            height: 40
            color: "#2c3e50"
            
            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 10
                anchors.rightMargin: 10
                spacing: 10
                
                Button {
                    text: "Flugplan"
                    onClicked: {
                        // TODO: Flugplan-Funktionalität einbinden
                    }
                }
                
                Button {
                    text: "Start"
                    onClicked: {
                        // TODO: Start-Befehl implementieren
                    }
                }
                
                Button {
                    text: "Landung"
                    onClicked: {
                        // TODO: Landungs-Befehl implementieren
                    }
                }
                
                Button {
                    text: "Notfall-Stopp"
                    background: Rectangle {
                        color: "#e74c3c"
                        radius: 4
                    }
                    onClicked: {
                        // TODO: Notfall-Stopp implementieren
                    }
                }
                
                Item { Layout.fillWidth: true } // Spacer
                
                ComboBox {
                    id: mapTypeCombo
                    model: ["3D Terrain", "Satellit", "Straßenkarte"]
                    onActivated: {
                        // TODO: Kartentyp-Wechsel implementieren
                    }
                }
            }
        }
        
        // Hauptbereich mit Karte und Steuerungen
        Item {
            Layout.fillWidth: true
            Layout.fillHeight: true
            
            // Dieser Bereich wird vom WebEngineView gefüllt (in FlightViewController.py)
            Rectangle {
                id: mapContainer
                anchors.fill: parent
                color: "#f0f0f0"
                
                // Platzhalter-Text (wird durch den echten WebEngineView ersetzt)
                Text {
                    anchors.centerIn: parent
                    text: "Hier wird die 3D-Karte angezeigt"
                    font.pixelSize: 20
                    color: "#999999"
                }
            }
            
            // Überlagerungen für die Karte
            Item {
                anchors.fill: parent
                
                // Drohnen-Statusanzeige (rechts oben)
                Rectangle {
                    anchors.top: parent.top
                    anchors.right: parent.right
                    anchors.margins: 20
                    width: 240
                    height: 160
                    color: Qt.rgba(0, 0, 0, 0.7)
                    radius: 8
                    
                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 10
                        spacing: 6
                        
                        Text {
                            text: "DROHNEN-STATUS"
                            color: "white"
                            font.bold: true
                            font.pixelSize: 14
                            Layout.alignment: Qt.AlignHCenter
                        }
                        
                        Rectangle {
                            Layout.fillWidth: true
                            height: 1
                            color: "gray"
                        }
                        
                        // Status-Anzeigen
                        GridLayout {
                            Layout.fillWidth: true
                            columns: 2
                            columnSpacing: 10
                            rowSpacing: 5
                            
                            Text { 
                                text: "Akku:" 
                                color: "white" 
                                font.pixelSize: 12
                            }
                            ProgressBar {
                                id: batteryProgress
                                value: flightMapBridge ? flightMapBridge.currentBattery / 100 : 0.75
                                Layout.fillWidth: true
                                background: Rectangle {
                                    implicitWidth: 200
                                    implicitHeight: 6
                                    color: "#616161"
                                    radius: 3
                                }
                                contentItem: Rectangle {
                                    width: batteryProgress.visualPosition * parent.width
                                    height: parent.height
                                    radius: 2
                                    color: {
                                        if (batteryProgress.value > 0.5) return "#4caf50"
                                        else if (batteryProgress.value > 0.2) return "#ff9800"
                                        else return "#f44336"
                                    }
                                }
                            }
                            
                            Text { 
                                text: "Höhe:" 
                                color: "white" 
                                font.pixelSize: 12
                            }
                            Text { 
                                text: flightMapBridge ? flightMapBridge.currentAlt.toFixed(1) + " m" : "100.0 m"
                                color: "white" 
                                font.pixelSize: 12
                            }
                            
                            Text { 
                                text: "Geschw.:" 
                                color: "white" 
                                font.pixelSize: 12
                            }
                            Text { 
                                text: flightMapBridge ? flightMapBridge.currentSpeed.toFixed(1) + " m/s" : "0.0 m/s"
                                color: "white" 
                                font.pixelSize: 12
                            }
                            
                            Text { 
                                text: "GPS:" 
                                color: "white" 
                                font.pixelSize: 12
                            }
                            RowLayout {
                                spacing: 2
                                Repeater {
                                    model: 5
                                    Rectangle {
                                        width: 6
                                        height: 12
                                        radius: 1
                                        color: index < 4 ? "#4caf50" : "#e0e0e0"
                                    }
                                }
                            }
                        }
                    }
                }
                
                // Steuerungsleiste (unten)
                Rectangle {
                    anchors.bottom: parent.bottom
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.margins: 20
                    height: 60
                    color: Qt.rgba(0, 0, 0, 0.7)
                    radius: 8
                    
                    RowLayout {
                        anchors.fill: parent
                        anchors.margins: 10
                        spacing: 10
                        
                        Button {
                            text: "Drohne zentrieren"
                            onClicked: {
                                if (flightMapBridge) {
                                    flightMapBridge.followDrone();
                                }
                            }
                        }
                        
                        Button {
                            text: "Pfad anzeigen"
                            checkable: true
                            checked: true
                            onClicked: {
                                if (flightMapBridge) {
                                    flightMapBridge.setPathVisible(checked);
                                }
                            }
                        }
                        
                        Button {
                            text: "Pfad löschen"
                            onClicked: {
                                if (flightMapBridge) {
                                    flightMapBridge.clearPath();
                                }
                            }
                        }
                        
                        Item { Layout.fillWidth: true } // Spacer
                        
                        Text {
                            text: "Position:"
                            color: "white"
                            font.pixelSize: 12
                        }
                        
                        Text {
                            text: {
                                if (flightMapBridge) {
                                    return flightMapBridge.currentLat.toFixed(6) + ", " +
                                           flightMapBridge.currentLon.toFixed(6);
                                }
                                return "52.520000, 13.405000";
                            }
                            color: "white"
                            font.pixelSize: 12
                            font.family: "Courier"
                        }
                    }
                }
            }
        }
    }
}
