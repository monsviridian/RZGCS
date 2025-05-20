/*
This is a UI file (.ui.qml) that is intended to be edited in Qt Design Studio only.
It is supposed to be strictly declarative and only uses a subset of QML. If you edit
this file manually, you might introduce QML code that is not supported by Qt Design Studio.
Check out https://doc.qt.io/qtcreator/creator-quick-ui-forms.html for details on .ui.qml files.
*/

import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtLocation
import QtPositioning
import QtQuick3D 6.8
import "./"

Rectangle {
    id: flightView
    color: "#1d1d1d"
    clip: true
    
    // Signal für Kartentyp-Änderung
    signal mapTypeChanged(int mapType)
    
    // Signal zum Öffnen der externen 3D-Karte
    signal openExternalMap()

    // Initialize map plugin
    Plugin {
        id: mapPlugin
        name: "osm"
        PluginParameter {
            name: "osm.mapping.custom.host"
            value: "https://tile.openstreetmap.org/"
        }
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 10

        // Header
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 40
            color: "#2a2a2a"
            radius: 5
            
            RowLayout {
                anchors.fill: parent
                anchors.margins: 8
                spacing: 10

                Label {
                    text: "Flugkarte"
                    font.pixelSize: 16
                    font.bold: true
                    color: "white"
                }
                
                // Kartentyp umschalten
                Button {
                    id: switchViewButton
                    text: mapStack.currentIndex === 0 ? "3D-Karte" : "2D-Karte"
                    font.pixelSize: 12
                    Layout.preferredHeight: 30
                    background: Rectangle {
                        color: "#2a82da"
                        radius: 4
                    }
                    contentItem: Text {
                        text: parent.text
                        font: parent.font
                        color: "white"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                    onClicked: {
                        mapStack.currentIndex = mapStack.currentIndex === 0 ? 1 : 0
                        
                        // Signal an Python-Backend senden
                        flightView.mapTypeChanged(mapStack.currentIndex)
                    }
                }
                
                // Separate 3D-Karte öffnen
                Button {
                    id: open3DMapButton
                    text: "3D-Karte extern öffnen"
                    font.pixelSize: 12
                    font.bold: true
                    Layout.preferredHeight: 30
                    background: Rectangle {
                        color: "#38b764"
                        radius: 4
                    }
                    contentItem: Text {
                        text: parent.text
                        font: parent.font
                        color: "white"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                    onClicked: {
                        // Signal zum Öffnen der externen 3D-Karte senden
                        flightView.openExternalMap()
                    }
                }

                Item { Layout.fillWidth: true }
                
                Label {
                    id: statusLabel
                    text: "Status: Nicht verbunden"
                    color: "#ff6666"
                    font.pixelSize: 14
                }
            }
        }

        // Map view mit Rahmen
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.preferredHeight: parent.height * 0.65
            color: "transparent"
            border.color: "#555555"
            border.width: 1
            radius: 5
            
            // Stack für 2D und 3D-Karten
            StackLayout {
                id: mapStack
                anchors.fill: parent
                anchors.margins: 2
                currentIndex: 1  // Standard: 3D-Karte
                
                // 2D-Karte
                Map {
                    id: map
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    plugin: mapPlugin
                    center: QtPositioning.coordinate(51.1657, 10.4515)
                    zoomLevel: 14

                    // Add drone position marker
                    MapQuickItem {
                        id: droneMarker
                        coordinate: QtPositioning.coordinate(51.1657, 10.4515)
                        anchorPoint.x: sourceItem.width / 2
                        anchorPoint.y: sourceItem.height / 2
                        sourceItem: Rectangle {
                            width: 40
                            height: 40
                            color: "transparent"
                            
                            Image {
                                id: droneImage
                                anchors.centerIn: parent
                                source: "images/drone_marker.svg"
                                width: 32
                                height: 32
                                smooth: true
                                mipmap: true
                            }
                            
                            // Pulsierender Kreis für bessere Sichtbarkeit
                            Rectangle {
                                id: pulseCircle
                                anchors.centerIn: parent
                                width: 32
                                height: 32
                                radius: width / 2
                                color: "#3300ff00"
                                border.width: 2
                                border.color: "#80ff00"
                                z: -1
                                
                                SequentialAnimation on scale {
                                    loops: Animation.Infinite
                                    NumberAnimation { from: 0.8; to: 1.5; duration: 1000; easing.type: Easing.OutQuad }
                                    NumberAnimation { from: 1.5; to: 0.8; duration: 1000; easing.type: Easing.InQuad }
                                }
                            }
                        }
                    }
                    
                    // Kartensteuerung
                    MapItemView {
                        model: waypointsModel
                        delegate: waypointDelegate
                    }
                    
                    // Wegpunkte-Modell
                    ListModel {
                        id: waypointsModel
                        // Beispielwegpunkte werden später durch echte Daten ersetzt
                    }
                    
                    // Template für Wegpunkte
                    Component {
                        id: waypointDelegate
                        MapQuickItem {
                            coordinate: QtPositioning.coordinate(model.lat, model.lon)
                            anchorPoint.x: 16
                            anchorPoint.y: 16
                            sourceItem: Column {
                                spacing: 2
                                
                                // Wegpunktmarkierung
                                Rectangle {
                                    width: 32
                                    height: 32
                                    radius: width / 2
                                    color: "#80ffffff"
                                    border.width: 2
                                    border.color: "#3c78d8"
                                    
                                    Text {
                                        anchors.centerIn: parent
                                        text: model.id
                                        font.pixelSize: 14
                                        font.bold: true
                                        color: "#3c78d8"
                                    }
                                }
                                
                                // Wegpunktbeschriftung
                                Rectangle {
                                    width: waypointLabel.width + 10
                                    height: waypointLabel.height + 6
                                    color: "#80ffffff"
                                    radius: 3
                                    
                                    Text {
                                        id: waypointLabel
                                        anchors.centerIn: parent
                                        text: "WP" + model.id
                                        font.pixelSize: 12
                                        color: "black"
                                        font.bold: true
                                    }
                                }
                                
                                // Höhenangabe
                                Rectangle {
                                    width: altLabel.width + 10
                                    height: altLabel.height + 6
                                    color: "#3c78d8"
                                    radius: 3
                                    
                                    Text {
                                        id: altLabel
                                        anchors.centerIn: parent
                                        text: model.alt + "m"
                                        font.pixelSize: 10
                                        color: "white"
                                        z: 1
                                    }
                                }
                            }
                        }
                    }
                }
                
                // 3D-Karte
                Item {
                    id: map3DContainer
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    
                    // Dieses Item wird zur Laufzeit durch ein QWidget ersetzt,
                    // das die 3D-Karte enthält
                    Rectangle {
                        id: mapContainer  // Diese ID wird vom FlightViewController verwendet
                        anchors.fill: parent
                        color: "#222222"
                        
                        Text {
                            anchors.centerIn: parent
                            text: "Cesium 3D-Karte wird geladen..."
                            color: "#aaaaaa"
                            font.pixelSize: 18
                        }
                    }
                }
            }
        }

        // Control Panel
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 130
            color: "#2d2d2d"
            radius: 5
            border.color: "#555555"
            border.width: 1

            RowLayout {
                anchors.fill: parent
                anchors.margins: 10
                spacing: 15
                
                // Linke Steuerelemente
                ColumnLayout {
                    Layout.preferredWidth: 120
                    spacing: 10
                    
                    Button {
                        id: prearmButton
                        text: "Prearm"
                        Layout.preferredWidth: 120
                        Layout.preferredHeight: 36
                        font.pixelSize: 14
                        background: Rectangle {
                            color: "#444444"
                            border.color: "#555555"
                            radius: 4
                        }
                        contentItem: Text {
                            text: prearmButton.text
                            font: prearmButton.font
                            color: "white"
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }
                    }
                    
                    Button {
                        id: resetButton
                        text: "Reset"
                        Layout.preferredWidth: 120
                        Layout.preferredHeight: 36
                        font.pixelSize: 14
                        background: Rectangle {
                            color: "#444444"
                            border.color: "#555555"
                            radius: 4
                        }
                        contentItem: Text {
                            text: resetButton.text
                            font: resetButton.font
                            color: "white"
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }
                    }
                }
                
                // Mittlere Steuerelemente
                ColumnLayout {
                    Layout.preferredWidth: 160
                    spacing: 10
                    
                    Button {
                        id: takeoffButton
                        text: "Start"
                        Layout.preferredWidth: 160
                        Layout.preferredHeight: 36
                        font.pixelSize: 14
                        background: Rectangle {
                            color: "#444444"
                            border.color: "#555555"
                            radius: 4
                        }
                        contentItem: Text {
                            text: takeoffButton.text
                            font: takeoffButton.font
                            color: "white"
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }
                    }
                    
                    Button {
                        id: landButton
                        text: "Landen"
                        Layout.preferredWidth: 160
                        Layout.preferredHeight: 36
                        font.pixelSize: 14
                        background: Rectangle {
                            color: "#444444"
                            border.color: "#555555"
                            radius: 4
                        }
                        contentItem: Text {
                            text: landButton.text
                            font: landButton.font
                            color: "white"
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }
                    }
                    
                    Button {
                        id: rtlButton
                        text: "Return to Launch"
                        Layout.preferredWidth: 160
                        Layout.preferredHeight: 36
                        font.pixelSize: 14
                        background: Rectangle {
                            color: "#444444"
                            border.color: "#555555"
                            radius: 4
                        }
                        contentItem: Text {
                            text: rtlButton.text
                            font: rtlButton.font
                            color: "white"
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }
                    }
                }
                
                // Rechte Steuerelemente
                ColumnLayout {
                    Layout.preferredWidth: 120
                    spacing: 10
                    
                    ComboBox {
                        id: modeComboBox
                        Layout.preferredWidth: 120
                        Layout.preferredHeight: 36
                        model: ["MANUAL", "STABILIZE", "RTL", "AUTO"]
                        font.pixelSize: 14
                        background: Rectangle {
                            color: "#444444"
                            border.color: "#555555"
                            radius: 4
                        }
                        contentItem: Text {
                            text: parent.displayText
                            font: parent.font
                            color: "white"
                            horizontalAlignment: Text.AlignLeft
                            verticalAlignment: Text.AlignVCenter
                            elide: Text.ElideRight
                            leftPadding: 10
                        }
                        popup: Popup {
                            y: modeComboBox.height
                            width: modeComboBox.width
                            implicitHeight: contentItem.implicitHeight
                            padding: 1
                            background: Rectangle {
                                color: "#444444"
                                border.color: "#555555"
                            }
                            contentItem: ListView {
                                clip: true
                                implicitHeight: contentHeight
                                model: modeComboBox.popup.visible ? modeComboBox.delegateModel : null
                                currentIndex: modeComboBox.highlightedIndex
                            }
                        }
                    }
                    
                    RowLayout {
                        Layout.preferredWidth: 120
                        Layout.preferredHeight: 36
                        spacing: 0
                        
                        Switch {
                            id: armSwitch
                            text: "Arm"
                            font.pixelSize: 14
                            Layout.fillWidth: true
                            checked: false
                            indicator: Rectangle {
                                implicitWidth: 40
                                implicitHeight: 20
                                x: armSwitch.leftPadding
                                y: parent.height / 2 - height / 2
                                radius: 10
                                color: armSwitch.checked ? "#80ff00" : "#555555"
                                border.color: armSwitch.checked ? "#80ff00" : "#999999"
                                Rectangle {
                                    x: armSwitch.checked ? parent.width - width - 2 : 2
                                    y: 2
                                    width: 16
                                    height: 16
                                    radius: 8
                                    color: "white"
                                }
                            }
                            contentItem: Text {
                                text: armSwitch.text
                                font: armSwitch.font
                                color: "white"
                                verticalAlignment: Text.AlignVCenter
                                leftPadding: armSwitch.indicator.width + armSwitch.spacing
                            }
                        }
                    }
                }
            }
        }
    }
    
    // Connections zur Steuerung der UI-Elemente
    Connections {
        target: serialConnector
        function onConnectedChanged(connected) {
            statusLabel.text = connected ? "Status: Verbunden" : "Status: Nicht verbunden"
            statusLabel.color = connected ? "#80ff00" : "#ff6666"
        }
    }
}
