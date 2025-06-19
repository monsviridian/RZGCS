import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: warzoneFlightView
    color: "#161616"  // Dunkler Hintergrund wie in CoD
    clip: true
    width: parent ? parent.width : 800
    height: parent ? parent.height : 600
    
    // Eigenschaften
    property real droneLatitude: 51.505600
    property real droneLongitude: 7.452400
    property real droneAltitude: 100.0
    property real droneHeading: 0.0
    property real zoomLevel: 1.0
    property bool followDrone: true
    property bool showControlPanel: true  // New property to control panel visibility
    
    // Signale
    signal mapClicked(real lat, real lon)
    signal addWaypoint(real lat, real lon)
    
    // Gitternetzlinien für die Call of Duty-ähnliche Karte
    Canvas {
        id: mapGrid
        anchors.fill: parent
        property int gridSize: 40
        
        onPaint: {
            var ctx = getContext("2d");
            var width = warzoneFlightView.width;
            var height = warzoneFlightView.height;
            
            // Hintergrund (dunkel)
            ctx.fillStyle = "#161616";
            ctx.fillRect(0, 0, width, height);
            
            // Gitternetz
            ctx.strokeStyle = "rgba(255, 255, 255, 0.15)";
            ctx.lineWidth = 1;
            
            // Straßen und Hauptwege (hellere Linien)
            ctx.strokeStyle = "rgba(180, 180, 180, 0.3)";
            ctx.lineWidth = 2;
            
            // Haupt-Straßennetz zeichnen (simuliert die Stadt)
            // Horizontale Hauptstraßen
            for (var y = 0; y < height; y += gridSize * 3) {
                ctx.beginPath();
                ctx.moveTo(0, y);
                ctx.lineTo(width, y);
                ctx.stroke();
            }
            
            // Vertikale Hauptstraßen
            for (var x = 0; x < width; x += gridSize * 3) {
                ctx.beginPath();
                ctx.moveTo(x, 0);
                ctx.lineTo(x, height);
                ctx.stroke();
            }
            
            // Nebenstraßen (dünner)
            ctx.strokeStyle = "rgba(150, 150, 150, 0.15)";
            ctx.lineWidth = 1;
            
            // Horizontale Nebenstraßen
            for (var y = 0; y < height; y += gridSize) {
                ctx.beginPath();
                ctx.moveTo(0, y);
                ctx.lineTo(width, y);
                ctx.stroke();
            }
            
            // Vertikale Nebenstraßen
            for (var x = 0; x < width; x += gridSize) {
                ctx.beginPath();
                ctx.moveTo(x, 0);
                ctx.lineTo(x, height);
                ctx.stroke();
            }
            
            // Gebäude simulieren (Rechtecke in verschiedenen Größen)
            ctx.fillStyle = "rgba(180, 180, 180, 0.2)";
            var buildingCount = 80;
            
            for (var i = 0; i < buildingCount; i++) {
                var bx = Math.random() * width;
                var by = Math.random() * height;
                var bw = 10 + Math.random() * 40;
                var bh = 10 + Math.random() * 40;
                
                ctx.fillRect(bx, by, bw, bh);
            }
            
            // Wasser simulieren (blaue Bereiche)
            ctx.fillStyle = "rgba(30, 60, 100, 0.4)";
            var waterCount = 5;
            
            for (var i = 0; i < waterCount; i++) {
                var wx = Math.random() * width;
                var wy = Math.random() * height;
                var wr = 50 + Math.random() * 100;
                
                ctx.beginPath();
                ctx.arc(wx, wy, wr, 0, Math.PI * 2);
                ctx.fill();
            }
            
            // Geländedetails - Berge/Hügel (dunkle Bereiche)
            ctx.fillStyle = "rgba(40, 40, 40, 0.3)";
            var hillCount = 8;
            
            for (var i = 0; i < hillCount; i++) {
                var hx = Math.random() * width;
                var hy = Math.random() * height;
                var hr = 30 + Math.random() * 80;
                
                ctx.beginPath();
                ctx.arc(hx, hy, hr, 0, Math.PI * 2);
                ctx.fill();
            }
        }
    }
    
    // Kartenrand im CoD-Stil (rot)
    Rectangle {
        anchors.fill: parent
        color: "transparent"
        border.width: 2
        border.color: "#ff2222"
        z: 10
    }
    
    // Koordinaten-Beschriftungen im militärischen Stil
    Row {
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.topMargin: 10
        height: 20
        spacing: parent.width / 10
        z: 10
        
        Repeater {
            model: 10
            Text {
                text: String.fromCharCode(65 + index) // A, B, C, usw.
                color: "#ffffffaa"
                font.pixelSize: 14
                font.bold: true
                width: parent.width / 10
                horizontalAlignment: Text.AlignHCenter
            }
        }
    }
    
    // Zahlenkoordinaten an der Seite
    Column {
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.leftMargin: 10
        width: 20
        spacing: parent.height / 10
        z: 10
        
        Repeater {
            model: 10
            Text {
                text: (index + 1).toString() // 1, 2, 3, usw.
                color: "#ffffffaa"
                font.pixelSize: 14
                font.bold: true
                height: parent.height / 10
                verticalAlignment: Text.AlignVCenter
            }
        }
    }
    
    // POI-Marker (Points of Interest - wichtige Orte auf der Karte)
    Repeater {
        model: [
            {name: "Airport", x: parent.width * 0.2, y: parent.height * 0.3, color: "#ffffff"},
            {name: "Downtown", x: parent.width * 0.5, y: parent.height * 0.5, color: "#ffffff"},
            {name: "Stadium", x: parent.width * 0.7, y: parent.height * 0.3, color: "#ffffff"},
            {name: "Hospital", x: parent.width * 0.4, y: parent.height * 0.7, color: "#ffff00"},
            {name: "Military Base", x: parent.width * 0.8, y: parent.height * 0.6, color: "#ff4444"}
        ]
        
        Rectangle {
            id: poiMarker
            width: 8
            height: 8
            radius: 4
            x: modelData.x - width/2
            y: modelData.y - height/2
            color: modelData.color
            border.width: 1
            border.color: "white"
            z: 10
            
            // POI-Beschriftung
            Text {
                anchors.left: parent.right
                anchors.leftMargin: 5
                anchors.verticalCenter: parent.verticalCenter
                text: modelData.name
                color: "white"
                font.pixelSize: 10
                font.bold: true
            }
        }
    }
    
    // Drohnen-Position (als grüner Pfeil wie in CoD)
    Item {
        id: droneMarker
        width: 20
        height: 20
        x: parent.width / 2 - width / 2
        y: parent.height / 2 - height / 2
        rotation: droneHeading
        z: 15
        
        Canvas {
            anchors.fill: parent
            onPaint: {
                var ctx = getContext("2d");
                ctx.fillStyle = "#00ff00";  // Grün wie im CoD HUD
                ctx.strokeStyle = "white";
                ctx.lineWidth = 1.5;
                
                // Dreieckspfeil zeichnen
                ctx.beginPath();
                ctx.moveTo(width/2, 0);      // Spitze
                ctx.lineTo(0, height);      // Unten links
                ctx.lineTo(width, height);  // Unten rechts
                ctx.closePath();
                ctx.fill();
                ctx.stroke();
            }
        }
    }
    
    // Kreisförmiger Scanbereich um die Drohne (wie in CoD Radar)
    Rectangle {
        id: radarSweep
        width: 200
        height: 3
        color: "#00ff00"
        transformOrigin: Item.Left
        x: droneMarker.x + droneMarker.width/2
        y: droneMarker.y + droneMarker.height/2
        opacity: 0.5
        z: 14
        
        RotationAnimation on rotation {
            from: 0
            to: 360
            duration: 3000
            loops: Animation.Infinite
        }
    }
    
    // Kontrollpanel unten
    Rectangle {
        id: controlPanel
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        height: showControlPanel ? 80 : 0  // Use the property to control height
        visible: showControlPanel  // Also control visibility
        color: "#aa000000"
        z: 20
        
        RowLayout {
            anchors.fill: parent
            anchors.margins: 10
            spacing: 10
            
            // Steuerung
            ColumnLayout {
                Layout.preferredWidth: 160
                spacing: 8
                
                Button {
                    text: "Center"
                    Layout.preferredWidth: 160
                    Layout.preferredHeight: 25
                    background: Rectangle {
                        color: "#2980b9"
                        radius: 4
                    }
                    contentItem: Text {
                        text: parent.text
                        color: "white"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                    onClicked: followDrone = true
                }
                
                Button {
                    text: "Add Waypoint"
                    Layout.preferredWidth: 160
                    Layout.preferredHeight: 25
                    background: Rectangle {
                        color: "#c27ba0"
                        radius: 4
                    }
                    contentItem: Text {
                        text: parent.text
                        color: "white"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                    onClicked: {
                        addWaypoint(droneLatitude, droneLongitude)
                    }
                }
            }
            
            // Info-Anzeige (Koordinaten etc.)
            GridLayout {
                Layout.fillWidth: true
                columns: 4
                rowSpacing: 5
                columnSpacing: 10
                
                Text { text: "Position:"; color: "white"; font.pixelSize: 14 }
                Text { 
                    text: droneLatitude.toFixed(6) + ", " + droneLongitude.toFixed(6); 
                    color: "#80ff00"; 
                    font.pixelSize: 14 
                }
                
                Text { text: "Altitude:"; color: "white"; font.pixelSize: 14 }
                Text { 
                    text: droneAltitude.toFixed(1) + " m"; 
                    color: "#80ff00"; 
                    font.pixelSize: 14 
                }
                
                Text { text: "Heading:"; color: "white"; font.pixelSize: 14 }
                Text { 
                    text: droneHeading.toFixed(1) + "°"; 
                    color: "#80ff00"; 
                    font.pixelSize: 14 
                }
                
                Text { text: "Zone:"; color: "white"; font.pixelSize: 14 }
                Text { 
                    text: "C-4"; // CoD-ähnliche Zonenbezeichnung
                    color: "#80ff00"; 
                    font.pixelSize: 14 
                }
            }
            
            // Zoom-Steuerung
            ColumnLayout {
                spacing: 5
                
                Button {
                    text: "+"
                    Layout.preferredWidth: 30
                    Layout.preferredHeight: 25
                    background: Rectangle {
                        color: "#555555"
                        radius: 4
                    }
                    contentItem: Text {
                        text: parent.text
                        color: "white"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                    onClicked: {
                        if (zoomLevel < 2.0) zoomLevel += 0.1
                    }
                }
                
                Button {
                    text: "-"
                    Layout.preferredWidth: 30
                    Layout.preferredHeight: 25
                    background: Rectangle {
                        color: "#555555"
                        radius: 4
                    }
                    contentItem: Text {
                        text: parent.text
                        color: "white"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                    onClicked: {
                        if (zoomLevel > 0.5) zoomLevel -= 0.1
                    }
                }
            }
        }
    }
    
    // Aktualisiere die Kartenansicht, wenn sich die Daten ändern
    onDroneLatitudeChanged: mapGrid.requestPaint()
    onDroneLongitudeChanged: mapGrid.requestPaint()
    onZoomLevelChanged: mapGrid.requestPaint()
}
