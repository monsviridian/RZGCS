import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: root
    width: 200
    height: 200
    property real droneLatitude: 51.505600  // Default position
    property real droneLongitude: 7.452400
    property real droneAltitude: 100.0
    property real droneHeading: 0.0        // 0-360 degrees
    property var waypointList: []          // List of waypoints to show
    property bool showCompass: true        // Show compass directions
    property string mapStyle: "satellite"  // Options: "satellite", "terrain", "night"
    property real zoomLevel: 1.0           // Zoom level 1.0 = normal
    property bool showPath: false // Wird von außen gesetzt
    
    signal mapClicked(real latitude, real longitude)
    
    // Map background image
    Rectangle {
        id: mapBackground
        anchors.fill: parent
        radius: width / 2  // Circular map like in CoD
        color: mapStyle === "night" ? "#001524" : 
               mapStyle === "terrain" ? "#487c29" : "#1a3542"
        border.width: 3
        border.color: "#90a0a0"
        clip: true
        
        // Grid lines
        Canvas {
            anchors.fill: parent
            opacity: 0.4
            onPaint: {
                var ctx = getContext("2d");
                ctx.lineWidth = 1;
                ctx.strokeStyle = Qt.rgba(1, 1, 1, 0.3);
                
                // Draw grid lines
                var spacing = 20;
                for (var i = 0; i < parent.width; i += spacing) {
                    ctx.beginPath();
                    ctx.moveTo(i, 0);
                    ctx.lineTo(i, parent.height);
                    ctx.stroke();
                    
                    ctx.beginPath();
                    ctx.moveTo(0, i);
                    ctx.lineTo(parent.width, i);
                    ctx.stroke();
                }
            }
        }
        
        // Radar sweep effect (like in CoD)
        Rectangle {
            id: radarSweep
            width: parent.width * 2
            height: 3
            color: Qt.rgba(0.7, 1, 0.7, 0.7)
            transformOrigin: Item.Left
            antialiasing: true
            x: parent.width / 2
            y: parent.height / 2
            
            RotationAnimation on rotation {
                from: 0
                to: 360
                duration: 4000
                loops: Animation.Infinite
            }
        }
        
        // Waypoints display (e.g., mission objectives in CoD)
        Repeater {
            model: waypointList
            delegate: Rectangle {
                id: waypoint
                width: modelData.type === 'home' ? 16 : (modelData.type === 'target' ? 20 : 12)
                height: modelData.type === 'home' ? 16 : (modelData.type === 'target' ? 20 : 12)
                radius: width / 2
                
                // Farben basierend auf Typ
                color: {
                    if (modelData.type === 'home') return "#00ff00"      // Grün für Home
                    else if (modelData.type === 'target') return "#ff0000" // Rot für Ziel
                    else return "#ffff00"                                // Gelb für Waypoints
                }
                
                border.color: "white"
                border.width: 2
                x: mapBackground.width / 2 + (modelData.longitude - droneLongitude) * 50000 * zoomLevel
                y: mapBackground.height / 2 - (modelData.latitude - droneLatitude) * 50000 * zoomLevel
                
                // Label für Nummerierung
                Text {
                    anchors.centerIn: parent
                    text: modelData.label || (modelData.index >= 0 ? (modelData.index + 1).toString() : "")
                    color: "black"
                    font.bold: true
                    font.pixelSize: modelData.type === 'home' ? 8 : (modelData.type === 'target' ? 10 : 6)
                    visible: modelData.type !== 'waypoint' || modelData.index >= 0
                }
                
                // Tooltip
                ToolTip.visible: codMinimap.containsMouse
                ToolTip.text: {
                    var typeText = modelData.type === 'home' ? 'HOME' : 
                                  modelData.type === 'target' ? 'ZIEL' : 'WEGPUNKT'
                    return typeText + ": " + modelData.latitude.toFixed(5) + ", " + modelData.longitude.toFixed(5) + 
                           "\nHöhe: " + modelData.altitude.toFixed(0) + "m"
                }
                
                // Pulse animation für Home und Ziel
                Rectangle {
                    id: pulse
                    anchors.centerIn: parent
                    color: "transparent"
                    border.color: parent.color
                    border.width: 2
                    opacity: 0.7
                    visible: modelData.type === 'home' || modelData.type === 'target'
                    
                    SequentialAnimation {
                        running: visible
                        loops: Animation.Infinite
                        
                        ParallelAnimation {
                            NumberAnimation { target: pulse; property: "width"; from: parent.width; to: parent.width * 3; duration: 2000 }
                            NumberAnimation { target: pulse; property: "height"; from: parent.height; to: parent.height * 3; duration: 2000 }
                            NumberAnimation { target: pulse; property: "opacity"; from: 0.7; to: 0; duration: 2000 }
                        }
                        
                        PropertyAction { target: pulse; property: "width"; value: parent.width }
                        PropertyAction { target: pulse; property: "height"; value: parent.height }
                        PropertyAction { target: pulse; property: "opacity"; value: 0.7 }
                    }
                }
                
                // Kontext-Menü für Waypoints
                MouseArea {
                    anchors.fill: parent
                    acceptedButtons: Qt.LeftButton | Qt.RightButton
                    
                    onClicked: function(mouse) {
                        if (mouse.button === Qt.RightButton && modelData.type === 'waypoint') {
                            // Kontext-Menü für Waypoint-Aktionen
                            waypointContextMenu.x = mouse.x
                            waypointContextMenu.y = mouse.y
                            waypointContextMenu.index = modelData.index
                            waypointContextMenu.type = 'waypoint'
                            waypointContextMenu.open()
                        }
                    }
                }
            }
        }
        
        // Marker-Logik: Home/Ziel nur anzeigen, wenn gesetzt
        Repeater {
            model: waypointList.filter(function(wp) {
                if (wp.type === 'home') return wp.latitude !== 0 || wp.longitude !== 0
                if (wp.type === 'target') return wp.latitude !== 0 || wp.longitude !== 0
                return true
            })
            delegate: Rectangle {
                id: homeMarker
                width: 16
                height: 16
                radius: width / 2
                color: "#00ff00" // Grün für Home
                border.color: "white"
                border.width: 2
                x: mapBackground.width / 2 + (modelData.longitude - droneLongitude) * 50000 * zoomLevel
                y: mapBackground.height / 2 - (modelData.latitude - droneLatitude) * 50000 * zoomLevel
                
                // Label für Nummerierung
                Text {
                    anchors.centerIn: parent
                    text: modelData.label || (modelData.index >= 0 ? (modelData.index + 1).toString() : "")
                    color: "black"
                    font.bold: true
                    font.pixelSize: 8
                    visible: modelData.type !== 'waypoint' || modelData.index >= 0
                }
                
                // Tooltip
                ToolTip.visible: codMinimap.containsMouse
                ToolTip.text: {
                    var typeText = modelData.type === 'home' ? 'HOME' : 'ZIEL'
                    return typeText + ": " + modelData.latitude.toFixed(5) + ", " + modelData.longitude.toFixed(5) + 
                           "\nHöhe: " + modelData.altitude.toFixed(0) + "m"
                }
                
                // Pulse animation für Home und Ziel
                Rectangle {
                    id: pulse
                    anchors.centerIn: parent
                    color: "transparent"
                    border.color: parent.color
                    border.width: 2
                    opacity: 0.7
                    visible: modelData.type === 'home' || modelData.type === 'target'
                    
                    SequentialAnimation {
                        running: visible
                        loops: Animation.Infinite
                        
                        ParallelAnimation {
                            NumberAnimation { target: pulse; property: "width"; from: parent.width; to: parent.width * 3; duration: 2000 }
                            NumberAnimation { target: pulse; property: "height"; from: parent.height; to: parent.height * 3; duration: 2000 }
                            NumberAnimation { target: pulse; property: "opacity"; from: 0.7; to: 0; duration: 2000 }
                        }
                        
                        PropertyAction { target: pulse; property: "width"; value: parent.width }
                        PropertyAction { target: pulse; property: "height"; value: parent.height }
                        PropertyAction { target: pulse; property: "opacity"; value: 0.7 }
                    }
                }
                
                // Kontext-Menü für Home/Ziel entfernen
                MouseArea {
                    anchors.fill: parent
                    acceptedButtons: Qt.RightButton
                    
                    onClicked: function(mouse) {
                        if (mouse.button === Qt.RightButton) {
                            waypointContextMenu.x = mouse.x
                            waypointContextMenu.y = mouse.y
                            waypointContextMenu.index = modelData.index
                            waypointContextMenu.type = modelData.type
                            waypointContextMenu.open()
                        }
                    }
                }
            }
        }
        
        // Kontext-Menü für Home/Ziel entfernen
        Menu {
            id: waypointContextMenu
            property int index: -1
            property string type: ""
            
            MenuItem {
                text: "Wegpunkt entfernen"
                visible: waypointContextMenu.type === 'waypoint'
                onTriggered: {
                    if (typeof missionViewModel !== 'undefined' && missionViewModel) {
                        missionViewModel.removeWaypoint(waypointContextMenu.index)
                    }
                }
            }
            MenuItem {
                text: "Home entfernen"
                visible: waypointContextMenu.type === 'home'
                onTriggered: {
                    if (typeof missionViewModel !== 'undefined' && missionViewModel) {
                        missionViewModel.setHomePosition(0, 0, 0)
                    }
                }
            }
            MenuItem {
                text: "Ziel entfernen"
                visible: waypointContextMenu.type === 'target'
                onTriggered: {
                    if (typeof missionViewModel !== 'undefined' && missionViewModel) {
                        missionViewModel.setTargetPosition(0, 0, 0)
                    }
                }
            }
        }
        
        MouseArea {
            anchors.fill: parent
            onClicked: function(mouse) {
                // Einfachklick: Waypoint hinzufügen
                var dx = mouse.x - mapBackground.width/2
                var dy = mapBackground.height/2 - mouse.y
                var lon = root.droneLongitude + dx / (50000 * root.zoomLevel)
                var lat = root.droneLatitude + dy / (50000 * root.zoomLevel)
                root.mapClicked(lat, lon)
            }
            onDoubleClicked: function(mouse) {
                var dx = mouse.x - mapBackground.width/2
                var dy = mapBackground.height/2 - mouse.y
                var lon = root.droneLongitude + dx / (50000 * root.zoomLevel)
                var lat = root.droneLatitude + dy / (50000 * root.zoomLevel)
                // Home/Ziel setzen je nach Status
                if (typeof missionViewModel !== 'undefined' && missionViewModel) {
                    var homeSet = missionViewModel.homeLatitude !== 0 || missionViewModel.homeLongitude !== 0
                    var targetSet = missionViewModel.targetLatitude !== 0 || missionViewModel.targetLongitude !== 0
                    if (!homeSet) {
                        missionViewModel.setHomePosition(lat, lon, 0)
                    } else if (!targetSet) {
                        missionViewModel.setTargetPosition(lat, lon, 0)
                    }
                }
            }
        }
    }
    
    // Compass directions (N, S, E, W)
    Text {
        visible: showCompass
        text: "N"
        color: "white"
        font.pixelSize: 12
        font.bold: true
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: parent.top
        anchors.topMargin: 5
    }
    
    Text {
        visible: showCompass
        text: "S"
        color: "white"
        font.pixelSize: 12
        font.bold: true
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 5
    }
    
    Text {
        visible: showCompass
        text: "E"
        color: "white"
        font.pixelSize: 12
        font.bold: true
        anchors.verticalCenter: parent.verticalCenter
        anchors.right: parent.right
        anchors.rightMargin: 5
    }
    
    Text {
        visible: showCompass
        text: "W"
        color: "white"
        font.pixelSize: 12
        font.bold: true
        anchors.verticalCenter: parent.verticalCenter
        anchors.left: parent.left
        anchors.leftMargin: 5
    }
    
    // Drone position indicator (triangle showing direction)
    Item {
        id: droneIndicator
        width: 16
        height: 16
        x: mapBackground.width / 2 - width / 2
        y: mapBackground.height / 2 - height / 2
        rotation: droneHeading
        
        Canvas {
            anchors.fill: parent
            onPaint: {
                var ctx = getContext("2d");
                ctx.fillStyle = "#00ff00";
                ctx.strokeStyle = "white";
                ctx.lineWidth = 1.5;
                
                // Draw triangle pointing upward
                ctx.beginPath();
                ctx.moveTo(width/2, 0);  // Top point
                ctx.lineTo(0, height);   // Bottom left
                ctx.lineTo(width, height); // Bottom right
                ctx.closePath();
                ctx.fill();
                ctx.stroke();
            }
        }
    }
    
    // Altitude and heading display
    Rectangle {
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.margins: 5
        width: 80
        height: 30
        color: Qt.rgba(0, 0, 0, 0.7)
        radius: 5
        
        Column {
            anchors.centerIn: parent
            Text {
                text: "ALT: " + Math.round(droneAltitude) + "m"
                color: "white"
                font.pixelSize: 10
            }
            Text {
                text: "HDG: " + Math.round(droneHeading) + "°"
                color: "white"
                font.pixelSize: 10
            }
        }
    }
    
    // Flugweg zeichnen
    // Entferne den alten Path-Canvas außerhalb von mapBackground
}
