/*
This is a UI file (.ui.qml) that is intended to be edited in Qt Design Studio only.
It is supposed to be strictly declarative and only uses a subset of QML. If you edit
this file manually, you might introduce QML code that is not supported by Qt Design Studio.
Check out https://doc.qt.io/qtcreator/creator-quick-ui-forms.html for details on .ui.qml files.
*/

import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: flightView
    objectName: "flightView"
    color: "#1d1d1d"
    clip: true
    width: parent ? parent.width : 800
    height: parent ? parent.height : 600
    
    // Signal für Kartentyp-Änderung
    signal mapTypeChanged(int mapType)
    
    // Signal zum Öffnen der externen 3D-Karte
    signal openExternalMap()
    
    // Aktueller Kartentyp (0=2D-Ansicht, 1=3D-Ansicht)
    property int currentMapType: 1

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
                    text: "Flight Map"
                    font.pixelSize: 16
                    font.bold: true
                    color: "white"
                }
                
                // Switch map view (2D/3D)
                Button {
                    id: switchViewButton
                    text: "Switch View"
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
                        var newType = flightView.currentMapType === 0 ? 1 : 0;
                        flightView.currentMapType = newType;
                        flightView.mapTypeChanged(newType);
                    }
                }
                
                // Open separate 3D map
                Button {
                    id: open3DMapButton
                    text: "Open External 3D Map"
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
                        flightView.openExternalMap()
                    }
                }

                Item { Layout.fillWidth: true }
                
                Label {
                    id: statusLabel
                    text: "Status: Not connected"
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
            
            // Native 3D-Karte Container
            Item {
                id: map3DContainer
                objectName: "map3DContainer"
                anchors.fill: parent
                
                // Placeholder text, will be replaced by the native 3D map
                Text {
                    id: loadingText
                    anchors.centerIn: parent
                    text: "Loading 3D map..."
                    font.pixelSize: 20
                    color: "white"
                    visible: true
                }
                
                // Diese Funktion wird vom Python-Code aufgerufen, um das native Widget einzubetten
                function setNativeWindowId(winId) {
                    console.log("Native Window ID gesetzt: " + winId);
                    loadingText.visible = false;
                }
            }
        }

        // Control Panel
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 90
            color: "#2a2a2a"
            radius: 5
            
            RowLayout {
                anchors.fill: parent
                anchors.margins: 10
                spacing: 15
                
                // Steuerung
                ColumnLayout {
                    Layout.preferredWidth: 160
                    spacing: 8
                    
                    Button {
                        id: centerButton
                        text: "Center"
                        Layout.preferredWidth: 160
                        Layout.preferredHeight: 30
                        font.pixelSize: 12
                        background: Rectangle {
                            color: "#2980b9"
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
                            console.log("Zentrieren Button geklickt")
                            flightViewController.center_on_drone()
                        }
                    }
                    
                    Button {
                        id: setWaypointButton
                        text: "Set Waypoint"
                        Layout.preferredWidth: 160
                        Layout.preferredHeight: 30
                        font.pixelSize: 12
                        background: Rectangle {
                            color: "#c27ba0"
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
                            console.log("Wegpunkt setzen geklickt")
                            flightViewController.add_waypoint()
                        }
                    }
                    
                    Row {
                        spacing: 8
                        Layout.preferredWidth: 160
                        
                        Button {
                            id: startButton
                            text: "Start"
                            width: 76
                            height: 30
                            font.pixelSize: 12
                            background: Rectangle {
                                color: "#6aa84f"
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
                                console.log("Start Button geklickt")
                                flightViewController.start_mission()
                            }
                        }
                        
                        Button {
                            id: landButton
                            text: "Land"
                            width: 76
                            height: 30
                            font.pixelSize: 12
                            background: Rectangle {
                                color: "#e69138"
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
                                console.log("Landen Button geklickt")
                                flightViewController.land()
                            }
                        }
                    }
                    
                    Row {
                        spacing: 8
                        Layout.preferredWidth: 160
                        
                        Button {
                            id: rthButton
                            text: "RTH"
                            width: 76
                            height: 30
                            font.pixelSize: 12
                            background: Rectangle {
                                color: "#cc0000"
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
                                console.log("RTH Button geklickt")
                                flightViewController.return_to_home()
                            }
                        }
                        
                        Button {
                            id: haltButton
                            text: "HALT"
                            width: 76
                            height: 30
                            font.pixelSize: 12
                            background: Rectangle {
                                color: "#990000"
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
                                console.log("HALT Button geklickt")
                                flightViewController.emergency_stop()
                            }
                        }
                    }
                }

                // Status
                GridLayout {
                    Layout.fillWidth: true
                    columns: 4
                    rowSpacing: 5
                    columnSpacing: 10
                    
                    Text { text: "Position:"; color: "white"; font.pixelSize: 14 }
                    Text { text: "--"; color: "#80ff00"; font.pixelSize: 14 }
                    
                    Text { text: "Altitude:"; color: "white"; font.pixelSize: 14 }
                    Text { text: "--"; color: "#80ff00"; font.pixelSize: 14 }
                }
            }
        }
    }

    // Verbindungsstatus aktualisieren
    Connections {
        target: serialConnector
        function onConnectedChanged(connected) {
            statusLabel.text = connected ? "Status: Verbunden" : "Status: Nicht verbunden"
            statusLabel.color = connected ? "#80ff00" : "#ff6666"
        }
    }
    
    // Verbindung zum FlightViewController
    Connections {
        target: flightViewController
    }
}