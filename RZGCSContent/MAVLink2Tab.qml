import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    property var protocolConnectionManager
    property var mavlinkV2Backend
    property var waypointList: []

    function updateWaypointList() {
        if (mavlinkV2Backend && mavlinkV2Backend.mission_manager && mavlinkV2Backend.mission_manager.mission_items) {
            waypointList = mavlinkV2Backend.mission_manager.mission_items.map(function(item) {
                return { lat: item.x, lon: item.y, alt: item.z }
            })
        } else {
            waypointList = []
        }
        console.log("D: WaypointList updated:", JSON.stringify(waypointList))
        markerCanvas.requestPaint();
    }

    id: root
    color: "#181c1f"
    anchors.fill: parent

    // Debug-Ausgaben nur beim Start
    Component.onCompleted: {
        console.log("MAVLink2Tab: Component completed")
        console.log("MAVLink2Tab: protocolConnectionManager =", protocolConnectionManager)
        console.log("MAVLink2Tab: mavlinkV2Backend =", mavlinkV2Backend)
        
        // Send helpful message to user
        if (typeof messageManager !== 'undefined' && messageManager) {
            messageManager.addMessage("MAVLink 2 Tab loaded - Ready for advanced mission planning and telemetry", 1)
            messageManager.addMessage("To connect: Start SITL simulator or connect real flight controller to tcp:127.0.0.1:5760", 1)
        }
        updateWaypointList()
    }

    Connections {
        target: mavlinkV2Backend && mavlinkV2Backend.mission_manager ? mavlinkV2Backend.mission_manager : null
        onMissionItemsChanged: updateWaypointList()
        onMissionItemAdded: updateWaypointList()
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 8

        // Status Message Area
        Rectangle {
            Layout.fillWidth: true
            height: 60
            color: "#232b2e"
            radius: 8
            border.color: "#2e3a3e"
            
            RowLayout {
                anchors.fill: parent
                anchors.margins: 12
                spacing: 12
                
                // Status Icon
                Rectangle {
                    width: 16
                    height: 16
                    radius: 8
                    color: {
                        if ((protocolConnectionManager && protocolConnectionManager.isConnected) || (mavlinkV2Backend && mavlinkV2Backend.connected)) {
                            return "#00e0c6"  // Green when connected
                        }
                        return "#ff6666"  // Red when disconnected
                    }
                }
                
                // Status Text
                Text {
                    Layout.fillWidth: true
                    text: {
                        if (!protocolConnectionManager && !mavlinkV2Backend) {
                            return "MAVLink 2 Backend not available"
                        } else if ((protocolConnectionManager && protocolConnectionManager.isConnected) || (mavlinkV2Backend && mavlinkV2Backend.connected)) {
                            return "MAVLink 2 Connected (Serial or TCP) - Ready for mission planning and telemetry"
                        } else {
                            return "MAVLink 2 Disconnected - Click 'Connect' to connect to tcp:127.0.0.1:5760 (SITL simulator or real flight controller)"
                        }
                    }
                    color: "#cccccc"
                    font.pixelSize: 14
                    wrapMode: Text.WordWrap
                }
            }
        }

        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 16

            // Left: Mission Planning Panel
            Rectangle {
                color: "#232b2e"
                width: 340
                Layout.fillHeight: true
                radius: 8
                border.color: "#2e3a3e"
                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 16
                    spacing: 12
                    
                    // Connection controls
                    Text { text: "MAVLink 2 Connection"; color: "#00e0c6"; font.pixelSize: 18; font.bold: true }
                    Button {
                        Layout.fillWidth: true
                        text: protocolConnectionManager.isConnected ? "Disconnect" : "Connect"
                        onClicked: {
                            if (!protocolConnectionManager.isConnected) {
                                protocolConnectionManager.setConnectionString(portComboBox.currentText)
                            }
                            protocolConnectionManager.connect()
                        }
                    }
                    Label {
                        Layout.fillWidth: true
                        text: {
                            if (protocolConnectionManager) {
                                return protocolConnectionManager.isConnected ? "Status: Connected" : "Status: Disconnected"
                            }
                            return "Status: No Manager"
                        }
                        color: {
                            if (protocolConnectionManager && protocolConnectionManager.isConnected) {
                                return "#00e0c6"
                            }
                            return "#ff6666"
                        }
                    }
                    Rectangle { height: 2; color: "#2e3a3e"; Layout.fillWidth: true }
                    
                    // Mission Editor Section
                    Text { text: "Mission Editor"; color: "#cccccc"; font.pixelSize: 16; font.bold: true }
                    
                    // Add Waypoint Section
                    Rectangle {
                        Layout.fillWidth: true
                        height: 120
                        color: "#1a1e21"
                        radius: 4
                        border.color: "#2e3a3e"
                        
                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 8
                            spacing: 4
                            
                            Text { text: "Add Waypoint"; color: "#00e0c6"; font.pixelSize: 12; font.bold: true }
                            
                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 4
                                Text { text: "Lat:"; color: "#cccccc"; font.pixelSize: 10 }
                                TextField {
                                    id: latInput
                                    Layout.fillWidth: true
                                    placeholderText: "51.5074"
                                    text: "51.5074"
                                    color: "#cccccc"
                                    background: Rectangle { color: "#2e3a3e"; radius: 2 }
                                    font.pixelSize: 10
                                }
                            }
                            
                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 4
                                Text { text: "Lon:"; color: "#cccccc"; font.pixelSize: 10 }
                                TextField {
                                    id: lonInput
                                    Layout.fillWidth: true
                                    placeholderText: "-0.1278"
                                    text: "-0.1278"
                                    color: "#cccccc"
                                    background: Rectangle { color: "#2e3a3e"; radius: 2 }
                                    font.pixelSize: 10
                                }
                            }
                            
                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 4
                                Text { text: "Alt:"; color: "#cccccc"; font.pixelSize: 10 }
                                TextField {
                                    id: altInput
                                    Layout.fillWidth: true
                                    placeholderText: "100"
                                    text: "100"
                                    color: "#cccccc"
                                    background: Rectangle { color: "#2e3a3e"; radius: 2 }
                                    font.pixelSize: 10
                                }
                            }
                            
                            Button {
                                Layout.fillWidth: true
                                text: "Add Waypoint"
                                onClicked: {
                                    if (protocolConnectionManager && protocolConnectionManager.isConnected) {
                                        let backend = protocolConnectionManager.mavlinkV2Backend;
                                        if (backend && backend.mission_manager) {
                                            let waypoint = {
                                                x: parseFloat(latInput.text),
                                                y: parseFloat(lonInput.text),
                                                z: parseFloat(altInput.text),
                                                command: 16, // MAV_CMD_NAV_WAYPOINT
                                                frame: 0,    // MAV_FRAME_GLOBAL
                                                autocontinue: 1
                                            };
                                            backend.mission_manager.add_waypoint(waypoint);
                                            
                                            // Clear inputs
                                            latInput.text = "51.5074"
                                            lonInput.text = "-0.1278"
                                            altInput.text = "100"
                                        }
                                    }
                                }
                            }
                        }
                    }
                    
                    // Waypoint selector
                    Text { text: "Waypoints"; color: "#cccccc"; font.pixelSize: 16; font.bold: true }
                    Row {
                        spacing: 8
                        Repeater {
                            model: {
                                if (protocolConnectionManager && protocolConnectionManager.isConnected) {
                                    let backend = protocolConnectionManager.mavlinkV2Backend;
                                    return backend && backend.mission_manager ? backend.mission_manager.mission_items.length : 0
                                }
                                return 0
                            }
                            Rectangle {
                                width: 36; height: 36; radius: 18
                                color: {
                                    if (protocolConnectionManager && protocolConnectionManager.isConnected) {
                                        let backend = protocolConnectionManager.mavlinkV2Backend;
                                        return index === (backend.mission_manager.current_mission_index || 0) ? "#00e0c6" : "#2e3a3e"
                                    }
                                    return "#2e3a3e"
                                }
                                border.color: "#00e0c6"
                                Text { anchors.centerIn: parent; text: index+1; color: "white"; font.bold: true }
                                MouseArea {
                                    anchors.fill: parent
                                    onClicked: {
                                        if (protocolConnectionManager && protocolConnectionManager.isConnected) {
                                            let backend = protocolConnectionManager.mavlinkV2Backend;
                                            if (backend && backend.mission_manager)
                                                backend.mission_manager.current_mission_index = index
                                        }
                                    }
                                }
                            }
                        }
                    }
                    
                    // Mission details
                    Text {
                        text: {
                            if (protocolConnectionManager && protocolConnectionManager.isConnected) {
                                let backend = protocolConnectionManager.mavlinkV2Backend;
                                let mm = backend && backend.mission_manager;
                                if (mm && mm.mission_items.length > 0) {
                                    let wp = mm.mission_items[mm.current_mission_index || 0];
                                    return "Alt: " + wp.z + " | Lat: " + wp.x + " | Lon: " + wp.y;
                                }
                            }
                            return "No waypoint selected";
                        }
                        color: "#cccccc"
                    }
                    
                    // Mission control buttons
                    Row {
                        spacing: 8
                        Button { 
                            text: "Clear"; 
                            onClicked: { 
                                if (protocolConnectionManager && protocolConnectionManager.isConnected) {
                                    let backend = protocolConnectionManager.mavlinkV2Backend;
                                    if (backend && backend.mission_manager) 
                                        backend.mission_manager.clear_mission() 
                                }
                            } 
                        }
                        Button { 
                            text: "Restore"; 
                            onClicked: { 
                                if (protocolConnectionManager && protocolConnectionManager.isConnected) {
                                    let backend = protocolConnectionManager.mavlinkV2Backend;
                                    if (backend && backend.mission_manager) 
                                        backend.mission_manager.download_mission() 
                                }
                            } 
                        }
                        Button { 
                            text: "Save"; 
                            onClicked: { 
                                if (protocolConnectionManager && protocolConnectionManager.isConnected) {
                                    let backend = protocolConnectionManager.mavlinkV2Backend;
                                    if (backend && backend.mission_manager) 
                                        backend.mission_manager.upload_mission(backend.mission_manager.mission_items) 
                                }
                            } 
                        }
                    }
                }
            }
            
            // Center: Map View (CoDMinimap)
            Rectangle {
                color: "#222"
                Layout.fillWidth: true
                Layout.fillHeight: true
                radius: 8
                border.color: "#2e3a3e"
                
                CoDMinimap {
                    id: codMinimap
                    anchors.fill: parent
                    anchors.margins: 8
                    // Drohnenposition und Heading
                    droneLatitude: missionViewModel ? missionViewModel.droneLatitude : 51.505600
                    droneLongitude: missionViewModel ? missionViewModel.droneLongitude : 7.452400
                    droneAltitude: missionViewModel ? missionViewModel.droneAltitude : 100.0
                    droneHeading: missionViewModel ? missionViewModel.droneHeading : 0.0
                    // Waypoints direkt übergeben
                    waypointList: missionViewModel ? missionViewModel.waypointList : []
                    
                    // Map-Klick Handler für Waypoints
                    onMapClicked: {
                        console.log("D: Map clicked at:", latitude, longitude);
                        
                        // Debug: Prüfe verfügbare Backends
                        console.log("D: missionViewModel available:", typeof missionViewModel !== "undefined");
                        
                        var alt = 50.0; // Default altitude
                        
                        // Versuche Altitude aus Backend zu bekommen
                        if (missionViewModel && typeof missionViewModel.droneAltitude === "number") {
                            alt = missionViewModel.droneAltitude;
                        }
                        
                        console.log("D: Using altitude:", alt);
                        
                        // Waypoint über missionViewModel hinzufügen
                        if (typeof missionViewModel !== "undefined" && missionViewModel) {
                            console.log("D: Adding waypoint via missionViewModel.addWaypointToBackend");
                            missionViewModel.addWaypointToBackend(latitude, longitude, alt);
                            
                            if (typeof messageManager !== 'undefined' && messageManager) {
                                messageManager.addMessage(`Waypoint added: ${latitude.toFixed(6)}, ${longitude.toFixed(6)}`, 4);
                            }
                        } else {
                            console.log("D: No missionViewModel available for waypoint addition!");
                            if (typeof messageManager !== 'undefined' && messageManager) {
                                messageManager.addMessage("No mission manager available for waypoint addition", 3);
                            }
                        }
                    }
                    
                    // DEBUG: Zeige aktuelle Waypoint-Liste aus missionViewModel
                    Component.onCompleted: {
                        if (typeof missionViewModel !== 'undefined' && missionViewModel) {
                            console.log("[QML] missionViewModel.waypointList:", JSON.stringify(missionViewModel.waypointList));
                        } else {
                            console.log("[QML] missionViewModel nicht verfügbar");
                        }
                    }
                    
                    // Entferne den eigenen Marker-Repeater (Notfall-Variante)
                }
                
                // Mission Planning Controls
                Rectangle {
                    id: missionControls
                    anchors.bottom: parent.bottom
                    anchors.right: parent.right
                    anchors.margins: 10
                    width: 220
                    height: 130
                    color: Qt.rgba(0, 0, 0, 0.8)
                    radius: 8
                    border.color: "#444444"
                    border.width: 1
                    
                    property string setMode: "none" // "none", "home", "target"
                    property bool showPath: false
                    
                    Column {
                        anchors.fill: parent
                        anchors.margins: 8
                        spacing: 6
                        
                        Text {
                            text: "Mission Planning"
                            color: "white"
                            font.bold: true
                            font.pixelSize: 12
                        }
                        
                        Row {
                            spacing: 6
                            Button {
                                id: btnSetHome
                                text: "Set Home"
                                width: 60
                                height: 26
                                font.pixelSize: 10
                                checkable: true
                                checked: missionControls.setMode === "home"
                                onClicked: missionControls.setMode = checked ? "home" : "none"
                            }
                            Button {
                                id: btnSetTarget
                                text: "Set Target"
                                width: 70
                                height: 26
                                font.pixelSize: 10
                                checkable: true
                                checked: missionControls.setMode === "target"
                                onClicked: missionControls.setMode = checked ? "target" : "none"
                            }
                            Button {
                                id: btnDrawPath
                                text: missionControls.showPath ? "Hide Path" : "Draw Path"
                                width: 70
                                height: 26
                                font.pixelSize: 10
                                checkable: true
                                checked: missionControls.showPath
                                onClicked: missionControls.showPath = !missionControls.showPath
                            }
                        }
                        
                        Text {
                            text: missionControls.setMode === "home" ? "Klicke auf die Karte, um Home zu setzen" : (missionControls.setMode === "target" ? "Klicke auf die Karte, um Ziel zu setzen" : "")
                            color: "#cccccc"
                            font.pixelSize: 10
                        }
                        Text {
                            text: "Right-click waypoints for options"
                            color: "#cccccc"
                            font.pixelSize: 9
                        }
                    }
                }
                
                // Map controls overlay
                Rectangle {
                    anchors.top: parent.top
                    anchors.right: parent.right
                    anchors.margins: 8
                    width: 120
                    height: 80
                    color: Qt.rgba(0, 0, 0, 0.7)
                    radius: 4
                    
                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 4
                        spacing: 2
                        
                        Text {
                            text: "Map Controls"
                            color: "white"
                            font.pixelSize: 10
                            font.bold: true
                        }
                        
                        Row {
                            spacing: 4
                            Button {
                                text: "Sat"
                                width: 30
                                height: 20
                                background: Rectangle {
                                    color: codMinimap.mapStyle === "satellite" ? "#00e0c6" : "#2e3a3e"
                                    radius: 2
                                }
                                contentItem: Text {
                                    text: parent.text
                                    color: "white"
                                    font.pixelSize: 8
                                    horizontalAlignment: Text.AlignHCenter
                                    verticalAlignment: Text.AlignVCenter
                                }
                                onClicked: codMinimap.mapStyle = "satellite"
                            }
                            
                            Button {
                                text: "Ter"
                                width: 30
                                height: 20
                                background: Rectangle {
                                    color: codMinimap.mapStyle === "terrain" ? "#00e0c6" : "#2e3a3e"
                                    radius: 2
                                }
                                contentItem: Text {
                                    text: parent.text
                                    color: "white"
                                    font.pixelSize: 8
                                    horizontalAlignment: Text.AlignHCenter
                                    verticalAlignment: Text.AlignVCenter
                                }
                                onClicked: codMinimap.mapStyle = "terrain"
                            }
                            
                            Button {
                                text: "Night"
                                width: 30
                                height: 20
                                background: Rectangle {
                                    color: codMinimap.mapStyle === "night" ? "#00e0c6" : "#2e3a3e"
                                    radius: 2
                                }
                                contentItem: Text {
                                    text: parent.text
                                    color: "white"
                                    font.pixelSize: 8
                                    horizontalAlignment: Text.AlignHCenter
                                    verticalAlignment: Text.AlignVCenter
                                }
                                onClicked: codMinimap.mapStyle = "night"
                            }
                        }
                        
                        Row {
                            spacing: 4
                            Button {
                                text: "+"
                                width: 20
                                height: 20
                                background: Rectangle { color: "#2e3a3e"; radius: 2 }
                                contentItem: Text {
                                    text: parent.text
                                    color: "white"
                                    font.pixelSize: 10
                                    horizontalAlignment: Text.AlignHCenter
                                    verticalAlignment: Text.AlignVCenter
                                }
                                onClicked: codMinimap.zoomLevel = Math.min(codMinimap.zoomLevel + 0.2, 3.0)
                            }
                            
                            Button {
                                text: "-"
                                width: 20
                                height: 20
                                background: Rectangle { color: "#2e3a3e"; radius: 2 }
                                contentItem: Text {
                                    text: parent.text
                                    color: "white"
                                    font.pixelSize: 10
                                    horizontalAlignment: Text.AlignHCenter
                                    verticalAlignment: Text.AlignVCenter
                                }
                                onClicked: codMinimap.zoomLevel = Math.max(codMinimap.zoomLevel - 0.2, 0.5)
                            }
                            
                            Button {
                                text: codMinimap.showCompass ? "Hide" : "Show"
                                width: 40
                                height: 20
                                background: Rectangle { color: "#2e3a3e"; radius: 2 }
                                contentItem: Text {
                                    text: parent.text
                                    color: "white"
                                    font.pixelSize: 8
                                    horizontalAlignment: Text.AlignHCenter
                                    verticalAlignment: Text.AlignVCenter
                                }
                                onClicked: codMinimap.showCompass = !codMinimap.showCompass
                            }
                        }
                    }
                }
                
                // Hinweistext
                Text {
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.bottom: parent.bottom
                    anchors.bottomMargin: 8
                    text: "Klicke auf die Karte, um einen Waypoint hinzuzufügen."
                    color: "#cccccc"
                    font.pixelSize: 12
                }
            }
            
            // Right: Telemetry/Status Panel
            Rectangle {
                color: "#232b2e"
                width: 340
                Layout.fillHeight: true
                radius: 8
                border.color: "#2e3a3e"
                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 16
                    spacing: 12
                    Text { text: "Telemetry & Status"; color: "#00e0c6"; font.pixelSize: 18; font.bold: true }
                    // --- SENSORWERTE ANZEIGE (direkt aus mavlinkV2Backend) ---
                    Text { text: "GPS Latitude: " + (mavlinkV2Backend && typeof mavlinkV2Backend.gps_latitude === "number" ? mavlinkV2Backend.gps_latitude.toFixed(7) : "-"); color: "#cccccc" }
                    Text { text: "GPS Longitude: " + (mavlinkV2Backend && typeof mavlinkV2Backend.gps_longitude === "number" ? mavlinkV2Backend.gps_longitude.toFixed(7) : "-"); color: "#cccccc" }
                    Text { text: "GPS Altitude: " + (mavlinkV2Backend && typeof mavlinkV2Backend.gps_altitude === "number" ? mavlinkV2Backend.gps_altitude.toFixed(2) : "-") + " m"; color: "#cccccc" }
                    Text { text: "Satellites: " + (mavlinkV2Backend && typeof mavlinkV2Backend.gps_satellites === "number" ? mavlinkV2Backend.gps_satellites : "-"); color: "#cccccc" }
                    Text { text: "GPS Fix: " + (mavlinkV2Backend && typeof mavlinkV2Backend.gps_fix === "number" ? mavlinkV2Backend.gps_fix : "-"); color: "#cccccc" }
                    Text { text: "HDOP: " + (mavlinkV2Backend && typeof mavlinkV2Backend.gps_hdop === "number" ? mavlinkV2Backend.gps_hdop.toFixed(2) : "-"); color: "#cccccc" }
                    Text { text: "VDOP: " + (mavlinkV2Backend && typeof mavlinkV2Backend.gps_vdop === "number" ? mavlinkV2Backend.gps_vdop.toFixed(2) : "-"); color: "#cccccc" }
                    Text { text: "Battery Voltage: " + (mavlinkV2Backend && typeof mavlinkV2Backend.battery_voltage === "number" ? mavlinkV2Backend.battery_voltage.toFixed(2) : "-") + " V"; color: "#cccccc" }
                    Text { text: "Battery Current: " + (mavlinkV2Backend && typeof mavlinkV2Backend.battery_current === "number" ? mavlinkV2Backend.battery_current.toFixed(2) : "-") + " A"; color: "#cccccc" }
                    Text { text: "Battery Remaining: " + (mavlinkV2Backend && typeof mavlinkV2Backend.battery_remaining === "number" ? mavlinkV2Backend.battery_remaining.toFixed(1) : "-") + " %"; color: "#cccccc" }
                    Text { text: "Roll: " + (mavlinkV2Backend && typeof mavlinkV2Backend.roll === "number" ? mavlinkV2Backend.roll.toFixed(2) : "-") + "°"; color: "#cccccc" }
                    Text { text: "Pitch: " + (mavlinkV2Backend && typeof mavlinkV2Backend.pitch === "number" ? mavlinkV2Backend.pitch.toFixed(2) : "-") + "°"; color: "#cccccc" }
                    Text { text: "Yaw: " + (mavlinkV2Backend && typeof mavlinkV2Backend.yaw === "number" ? mavlinkV2Backend.yaw.toFixed(2) : "-") + "°"; color: "#cccccc" }
                    Text { text: "Heading: " + (mavlinkV2Backend && typeof mavlinkV2Backend.heading === "number" ? mavlinkV2Backend.heading.toFixed(2) : "-") + "°"; color: "#cccccc" }
                    Text { text: "Airspeed: " + (mavlinkV2Backend && typeof mavlinkV2Backend.airspeed === "number" ? mavlinkV2Backend.airspeed.toFixed(2) : "-") + " m/s"; color: "#cccccc" }
                    Text { text: "Groundspeed: " + (mavlinkV2Backend && typeof mavlinkV2Backend.groundspeed === "number" ? mavlinkV2Backend.groundspeed.toFixed(2) : "-") + " m/s"; color: "#cccccc" }
                    Text { text: "Climb Rate: " + (mavlinkV2Backend && typeof mavlinkV2Backend.climb_rate === "number" ? mavlinkV2Backend.climb_rate.toFixed(2) : "-") + " m/s"; color: "#cccccc" }
                    Text { text: "Armed: " + (mavlinkV2Backend && typeof mavlinkV2Backend.armed === "boolean" ? (mavlinkV2Backend.armed ? "Yes" : "No") : "-"); color: "#cccccc" }
                    Text { text: "Mode: " + (mavlinkV2Backend && typeof mavlinkV2Backend.mode === "string" ? mavlinkV2Backend.mode : "-"); color: "#cccccc" }
                    Text { text: "System Status: " + (mavlinkV2Backend && typeof mavlinkV2Backend.system_status === "string" ? mavlinkV2Backend.system_status : "-"); color: "#cccccc" }
                    // Optional: Luftdruck, falls vorhanden
                    Text { text: "Pressure (abs): " + (mavlinkV2Backend && typeof mavlinkV2Backend.pressure_abs === "number" ? mavlinkV2Backend.pressure_abs.toFixed(2) : "-") + " hPa"; color: "#cccccc" }
                    Text { text: "Pressure (diff): " + (mavlinkV2Backend && typeof mavlinkV2Backend.pressure_diff === "number" ? mavlinkV2Backend.pressure_diff.toFixed(2) : "-") + " hPa"; color: "#cccccc" }
                    Text { text: "Pressure Temp: " + (mavlinkV2Backend && typeof mavlinkV2Backend.pressure_temp === "number" ? mavlinkV2Backend.pressure_temp.toFixed(2) : "-") + " °C"; color: "#cccccc" }
                    // Artificial Horizon
                    Loader {
                        width: 300; height: 120
                        source: "Components/ArtificialHorizon.qml"
                        onLoaded: {
                            if (item && mavlinkV2Backend && mavlinkV2Backend.isConnected) {
                                item.roll = mavlinkV2Backend.roll || 0
                                item.pitch = mavlinkV2Backend.pitch || 0
                                item.disarmed = !mavlinkV2Backend.armed
                            }
                        }
                    }
                    // Compass 3D
                    Loader {
                        width: 300; height: 120
                        source: "Compass3DView.qml"
                        onLoaded: {
                            if (item && mavlinkV2Backend && mavlinkV2Backend.isConnected) {
                                item.angleZ = mavlinkV2Backend.heading || 0
                            }
                        }
                    }
                }
            }
        }
    }
} 