/*
This is a UI file (.ui.qml) that is intended to be edited in Qt Design Studio only.
It is supposed to be strictly declarative and only uses a subset of QML. If you edit
this file manually, you might introduce QML code that is not supported by Qt Design Studio.
Check out https://doc.qt.io/qtcreator/creator-quick-ui-forms.html for details on .ui.qml files.
*/

import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import RZGCS 1.0
import "./" as Content

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
    
    // Hardcoded drone position data (Frankfurt coordinates)
    property real droneLatitude: 50.110924
    property real droneLongitude: 8.682127
    property real droneAltitude: 100.0
    property real droneHeading: 45.0
    
    // GPS position with default values
    // Values will be updated by the FlightViewController
    Component.onCompleted: {
        console.log("FlightView initialized with coordinates: " + droneLatitude + ", " + droneLongitude)
    }
    
    // No need for GPS update timer as we're using direct values
    // The FlightViewController handles position updates

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
            id: mapContainer
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.preferredHeight: parent.height * 0.65
            color: "transparent"
            border.color: "#555555"
            border.width: 1
            radius: 5
            
            // Call of Duty Warzone-ähnliche Karte
            Content.WarzoneFlightView {
                id: warzoneFlightView
                anchors.fill: parent
                
                // Binde die Drohnendaten an die Karte
                droneLatitude: flightView.droneLatitude
                droneLongitude: flightView.droneLongitude
                droneAltitude: flightView.droneAltitude
                droneHeading: flightView.droneHeading
                
                // Verbinde Signale
                onMapClicked: {
                    console.log("Karte angeklickt bei: " + lat + ", " + lon)
                }
                
                onAddWaypoint: {
                    console.log("Wegpunkt hinzugefügt bei: " + lat + ", " + lon)
                    flightViewController.add_waypoint()
                }
            }
            
            // Native 3D-Karte Container wird nicht mehr benötigt, da wir die Warzone-Karte verwenden
            Item {
                id: map3DContainer
                objectName: "map3DContainer"
                anchors.fill: parent
                visible: false // Unsichtbar machen, aber das Item belassen für Kompatibilität
                
                // Diese Funktion wird vom Python-Code aufgerufen, um das native Widget einzubetten
                // Wir behalten diese Funktion für Kompatibilität bei
                function setNativeWindowId(winId) {
                    console.log("Native Window ID nicht verwendet, da Warzone-Karte aktiv");
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
                    id: statusGrid
                    Layout.fillWidth: true
                    columns: 4
                    rowSpacing: 5
                    columnSpacing: 10
                    
                    // Position display - hardcoded Frankfurt coordinates
                    Text { text: "Position:"; color: "white"; font.pixelSize: 14 }
                    Text { 
                        id: positionText
                        text: "50.110924, 8.682127"
                        color: "#80ff00"
                        font.pixelSize: 14 
                    }
                    
                    // Altitude display - hardcoded value
                    Text { text: "Altitude:"; color: "white"; font.pixelSize: 14 }
                    Text { 
                        id: altitudeText
                        text: "100.0 m"
                        color: "#80ff00"
                        font.pixelSize: 14 
                    }
                    
                    // Heading display - hardcoded value
                    Text { text: "Heading:"; color: "white"; font.pixelSize: 14 }
                    Text { 
                        id: headingText
                        text: "45.0°"
                        color: "#80ff00"
                        font.pixelSize: 14 
                    }
                }
            }
        }
    }

    // Update connection status and GPS data
    Connections {
        target: serialConnector
        function onConnectedChanged(connected) {
            statusLabel.text = connected ? "Status: Connected" : "Status: Disconnected"
            statusLabel.color = connected ? "#80ff00" : "#ff6666"
        }
        
        // Listen for GPS position updates from the flight controller
        function onGpsChanged(lat, lon, alt) {
            console.log("Received GPS data from FC: " + lat + ", " + lon + ", " + alt)
            flightView.droneLatitude = lat
            flightView.droneLongitude = lon
            flightView.droneAltitude = alt
            
            // Update position display
            positionText.text = lat.toFixed(6) + ", " + lon.toFixed(6)
            altitudeText.text = alt.toFixed(1) + " m"
        }
    }
    
    // Connection to FlightViewController (if available)
    Connections {
        target: typeof flightViewController !== 'undefined' ? flightViewController : null
        enabled: target !== null
        
        // Handler for drone position updates
        function onDronePositionChanged(lat, lon, alt) {
            console.log("Position update received: " + lat + ", " + lon + ", " + alt)
            flightView.droneLatitude = lat
            flightView.droneLongitude = lon
            flightView.droneAltitude = alt
            
            // Force update of position display
            positionText.text = lat.toFixed(6) + ", " + lon.toFixed(6)
            altitudeText.text = alt.toFixed(1) + " m"
        }
        
        // Handler for drone heading updates
        function onDroneHeadingChanged(heading) {
            console.log("Heading update received: " + heading)
            flightView.droneHeading = heading
            
            // Force update of heading display
            headingText.text = heading.toFixed(1) + "°"
        }
    }
}