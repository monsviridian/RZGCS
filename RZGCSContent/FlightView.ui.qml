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

Rectangle {
    id: flightView
    color: "#1d1d1d"
    clip: true

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
            
            Map {
                id: map
                anchors.fill: parent
                anchors.margins: 2
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
                        sourceItem: Rectangle {
                            width: 32
                            height: 32
                            color: "transparent"
                            
                            Text {
                                anchors.centerIn: parent
                                text: model.index + 1
                                color: "white"
                                font.bold: true
                                font.pixelSize: 12
                                z: 2
                            }
                            
                            Rectangle {
                                anchors.centerIn: parent
                                width: 24
                                height: 24
                                radius: width / 2
                                color: "#e67e22"
                                border.color: "white"
                                border.width: 2
                                z: 1
                            }
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
                            color: parent.pressed ? "#333333" : "#444444"
                            border.color: "#555555"
                            radius: 4
                        }
                        contentItem: Text {
                            text: parent.text
                            font: parent.font
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
                            color: parent.pressed ? "#333333" : "#444444"
                            border.color: "#555555"
                            radius: 4
                        }
                        contentItem: Text {
                            text: parent.text
                            font: parent.font
                            color: "white"
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }
                    }
                }
                
                // Mittlere Steuerelemente
                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 10
                    
                    Button {
                        id: positionButton
                        text: "Set Position"
                        Layout.fillWidth: true
                        Layout.preferredHeight: 36
                        font.pixelSize: 14
                        background: Rectangle {
                            color: parent.pressed ? "#333333" : "#444444"
                            border.color: "#555555"
                            radius: 4
                        }
                        contentItem: Text {
                            text: parent.text
                            font: parent.font
                            color: "white"
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }
                    }
                    
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 10
                        
                        TextField {
                            id: missionField
                            Layout.fillWidth: true
                            placeholderText: "Send Mission Plan"
                            font.pixelSize: 14
                            height: 36
                            color: "white"
                            background: Rectangle {
                                color: "#1a1a1a"
                                border.color: "#555555"
                                radius: 4
                            }
                        }
                        
                        Slider {
                            id: speedSlider
                            Layout.fillWidth: true
                            Layout.preferredHeight: 36
                            from: 0
                            to: 100
                            value: 50
                            stepSize: 5
                            background: Rectangle {
                                x: speedSlider.leftPadding
                                y: speedSlider.topPadding + speedSlider.availableHeight / 2 - height / 2
                                width: speedSlider.availableWidth
                                height: 4
                                radius: 2
                                color: "#1a1a1a"
                                Rectangle {
                                    width: speedSlider.visualPosition * parent.width
                                    height: parent.height
                                    color: "#80ff00"
                                    radius: 2
                                }
                            }
                            handle: Rectangle {
                                x: speedSlider.leftPadding + speedSlider.visualPosition * (speedSlider.availableWidth - width)
                                y: speedSlider.topPadding + speedSlider.availableHeight / 2 - height / 2
                                width: 16
                                height: 16
                                radius: 8
                                color: speedSlider.pressed ? "#f0f0f0" : "#f6f6f6"
                                border.color: "#555555"
                            }
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
