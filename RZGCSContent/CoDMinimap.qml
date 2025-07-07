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
                width: 10
                height: 10
                radius: 5
                color: "yellow"
                border.color: "white"
                border.width: 1
                x: mapBackground.width / 2 + (modelData.longitude - droneLongitude) * 50000 * zoomLevel
                y: mapBackground.height / 2 - (modelData.latitude - droneLatitude) * 50000 * zoomLevel
                
                // Pulse animation like in CoD
                Rectangle {
                    id: pulse
                    anchors.centerIn: parent
                    color: "transparent"
                    border.color: "yellow"
                    border.width: 2
                    opacity: 0.7
                    
                    SequentialAnimation {
                        running: true
                        loops: Animation.Infinite
                        
                        ParallelAnimation {
                            NumberAnimation { target: pulse; property: "width"; from: 10; to: 30; duration: 1000 }
                            NumberAnimation { target: pulse; property: "height"; from: 10; to: 30; duration: 1000 }
                            NumberAnimation { target: pulse; property: "opacity"; from: 0.7; to: 0; duration: 1000 }
                        }
                        
                        PropertyAction { target: pulse; property: "width"; value: 10 }
                        PropertyAction { target: pulse; property: "height"; value: 10 }
                        PropertyAction { target: pulse; property: "opacity"; value: 0.7 }
                    }
                }
            }
        }
        
        MouseArea {
            anchors.fill: parent
            onClicked: {
                // Beispiel-Umrechnung: Passe ggf. an deine Projektion an!
                var dx = mouse.x - mapBackground.width/2
                var dy = mapBackground.height/2 - mouse.y
                var lon = root.droneLongitude + dx / (50000 * root.zoomLevel)
                var lat = root.droneLatitude + dy / (50000 * root.zoomLevel)
                root.mapClicked(lat, lon)
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
}
