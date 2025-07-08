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
    
    // ViewModel binding
    property var flightViewModel: flightNavigationViewModel // must be set as context property
    
    // Signal für Kartentyp-Änderung
    signal mapTypeChanged(int mapType)
    
    // Signal zum Öffnen der externen 3D-Karte
    signal openExternalMap()
    
    // Aktueller Kartentyp (0=2D-Ansicht, 1=3D-Ansicht)
    property int currentMapType: 1
    
    // GPS position with default values
    // Values will be updated by the FlightViewController
    Component.onCompleted: {
        console.log("FlightView initialized with coordinates: " + flightViewModel._current_latitude + ", " + flightViewModel._current_longitude)
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
                    text: flightViewModel && flightViewModel.is_connected ? "Status: Connected" : "Status: Disconnected"
                    color: flightViewModel && flightViewModel.is_connected ? "#80ff00" : "#ff6666"
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
                droneLatitude: flightViewModel && flightViewModel._current_latitude ? flightViewModel._current_latitude : 0
                droneLongitude: flightViewModel && flightViewModel._current_longitude ? flightViewModel._current_longitude : 0
                droneAltitude: flightViewModel && flightViewModel._current_altitude ? flightViewModel._current_altitude : 0
                droneHeading: flightViewModel && flightViewModel._current_heading ? flightViewModel._current_heading : 0
                
                // Verbinde Signale
                onMapClicked: function(lat, lon) {
                    if (flightViewModel) flightViewModel.add_waypoint(lat, lon, flightViewModel._current_altitude)
                }
                
                onAddWaypoint: {
                    console.log("Wegpunkt hinzugefügt bei: " + lat + ", " + lon)
                    flightViewModel.add_waypoint(lat, lon, flightViewModel._current_altitude)
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

        // Mission & Flight Controls
        RowLayout {
            Layout.fillWidth: true
            Layout.preferredHeight: 120
            spacing: 20
            // Mission Controls
            ColumnLayout {
                spacing: 8
                Label { text: "Mission"; color: "#80ff00"; font.pixelSize: 14; font.bold: true }
            RowLayout {
                    spacing: 8
                    Button { text: "Add Waypoint"; onClicked: { if (flightViewModel) flightViewModel.add_waypoint(flightViewModel._current_latitude, flightViewModel._current_longitude, flightViewModel._current_altitude) } }
                    Button { text: "Clear Mission"; onClicked: { if (flightViewModel) flightViewModel.abort_mission() } }
                    }
                RowLayout {
                        spacing: 8
                    Button { text: "Upload Mission"; onClicked: { if (flightViewModel) flightViewModel.upload_mission(flightViewModel.current_mission) } }
                    Button { text: "Start Mission"; onClicked: { if (flightViewModel) flightViewModel.start_mission(flightViewModel.current_mission ? flightViewModel.current_mission.id : "") } }
                    Button { text: "Pause"; onClicked: { if (flightViewModel) flightViewModel.pause_mission() } }
                    Button { text: "Stop"; onClicked: { if (flightViewModel) flightViewModel.abort_mission() } }
                        }
                    }
            // Flight Controls
            ColumnLayout {
                        spacing: 8
                Label { text: "Flight Control"; color: "#4CAF50"; font.pixelSize: 14; font.bold: true }
                RowLayout {
                    spacing: 8
                    Button { text: "Arm"; onClicked: { if (flightViewModel) flightViewModel.arm() } }
                    Button { text: "Disarm"; onClicked: { if (flightViewModel) flightViewModel.disarm() } }
                    Button { text: "Takeoff"; onClicked: { if (flightViewModel) flightViewModel.takeoff() } }
                    Button { text: "Land"; onClicked: { if (flightViewModel) flightViewModel.land() } }
                    Button { text: "RTH"; onClicked: { if (flightViewModel) flightViewModel.return_to_launch() } }
                    Button { text: "HALT"; onClicked: { if (flightViewModel) flightViewModel.hold_position() } }
                }
            }
        }
        // Mission Tab Bereich (direkt eingefügt)
        Rectangle {
            Layout.fillWidth: true
            color: "#232323"
            radius: 5
            border.color: "#34495e"
            border.width: 1
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 10
                spacing: 8
                // Header
                RowLayout {
                    Layout.fillWidth: true
                    spacing: 10
                    Label {
                        text: "Mission Control"
                        font.pixelSize: 16
                        font.bold: true
                        color: "#80ff00"
                    }
                    Item { Layout.fillWidth: true }
                    Label {
                        text: missionViewModel && missionViewModel.is_connected ? "Status: Connected" : "Status: Disconnected"
                        color: missionViewModel && missionViewModel.is_connected ? "#80ff00" : "#ff6666"
                        font.pixelSize: 14
                    }
                }
                // Mission Controls
                RowLayout {
                    Layout.fillWidth: true
                    spacing: 8
                    Button { text: "Upload"; onClicked: { if (missionViewModel) missionViewModel.upload_mission() } }
                    Button { text: "Download"; onClicked: { if (missionViewModel) missionViewModel.download_mission() } }
                    Button { text: "Clear"; onClicked: { if (missionViewModel) missionViewModel.clear_mission() } }
                    Button { text: "Start"; onClicked: { if (missionViewModel) missionViewModel.start_mission() } }
                    Button { text: "Pause"; onClicked: { if (missionViewModel) missionViewModel.pause_mission() } }
                    Button { text: "Stop"; onClicked: { if (missionViewModel) missionViewModel.stop_mission() } }
                }
                // Missionspunkte-Liste
                ListView {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 100
                    model: missionViewModel ? missionViewModel.mission_items : []
                    delegate: Rectangle {
                        width: parent.width
                        height: 30
                        color: ListView.isCurrentItem ? "#555555" : "transparent"
                        RowLayout {
                            anchors.fill: parent
                            spacing: 8
                            Text { text: "Seq: " + modelData.seq; color: "white" }
                            Text { text: "Cmd: " + modelData.command; color: "#cccccc" }
                            Text { text: "Lat: " + modelData.lat; color: "#cccccc" }
                            Text { text: "Lon: " + modelData.lon; color: "#cccccc" }
                            Text { text: "Alt: " + modelData.alt; color: "#cccccc" }
                        }
                    }
                }
                // Statuslabels
                RowLayout {
                    Layout.fillWidth: true
                    spacing: 20
                    Label { text: "Current WP: " + (missionViewModel ? missionViewModel.current_seq : "-"); color: "white" }
                    Label { text: "ACK: " + (missionViewModel ? missionViewModel.last_ack : "-"); color: "white" }
                }
            }
        }
    }

    // Update connection status and GPS data
    Connections {
        target: serialConnector
        function onConnectedChanged(connected) {
            console.log("Received connection status from FC: " + connected)
            flightViewModel.is_connected = connected
        }
        
        // Listen for GPS position updates from the flight controller
        function onGpsChanged(lat, lon, alt) {
            console.log("Received GPS data from FC: " + lat + ", " + lon + ", " + alt)
            flightViewModel._current_latitude = lat
            flightViewModel._current_longitude = lon
            flightViewModel._current_altitude = alt
            
            // Update position display
            console.log("Position updated: " + lat + ", " + lon + ", " + alt)
        }
    }
    
    // Connection to FlightViewController (if available)
    Connections {
        target: typeof flightViewController !== 'undefined' ? flightViewController : null
        enabled: target !== null
        
        // Handler for drone position updates
        function onDronePositionChanged(lat, lon, alt) {
            console.log("Position update received: " + lat + ", " + lon + ", " + alt)
            flightViewModel._current_latitude = lat
            flightViewModel._current_longitude = lon
            flightViewModel._current_altitude = alt
            
            // Force update of position display
            console.log("Position updated: " + lat + ", " + lon + ", " + alt)
        }
        
        // Handler for drone heading updates
        function onDroneHeadingChanged(heading) {
            console.log("Heading update received: " + heading)
            flightViewModel._current_heading = heading
            
            // Force update of heading display
            console.log("Heading updated: " + heading)
        }
    }
}