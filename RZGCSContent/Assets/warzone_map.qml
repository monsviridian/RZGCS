import QtQuick
import QtQuick.Controls

Item {
    id: warzoneMapItem
    property real currentLatitude: 51.505600   // Standardposition
    property real currentLongitude: 7.452400
    property real currentAltitude: 100.0
    property real currentHeading: 0.0         // 0-360 Grad
    property bool showGrid: true              // Gitternetz anzeigen
    property bool showMarkers: true           // POI-Marker anzeigen
    property real zoomLevel: 1.0              // Zoom-Faktor
    property bool followDrone: true           // Automatisch Drohne verfolgen
    property var waypointList: []             // Liste der Wegpunkte

    // Karte mit Call of Duty Warzone-Stil
    Rectangle {
        id: mapBackground
        anchors.fill: parent
        color: "#161616"  // Dunkler Hintergrund

        // Hauptkartenbild
        Image {
            id: warzoneMapImage
            anchors.fill: parent
            source: "../assets/warzone_map_texture.jpg"  // Die Warzone-Kartenvorlage
            fillMode: Image.PreserveAspectCrop
            // Verschiebung der Karte basierend auf Drohnenposition und Zoom
            transform: Scale {
                xScale: warzoneMapItem.zoomLevel
                yScale: warzoneMapItem.zoomLevel
                origin.x: mapBackground.width / 2
                origin.y: mapBackground.height / 2
            }

            // Kartenverschiebung basierend auf der Drohnenposition
            x: followDrone ? (mapBackground.width / 2) - 
                             ((currentLongitude - 7.452400) * 100000 * zoomLevel) - 
                             width * (zoomLevel - 1) / 2 : 0
            y: followDrone ? (mapBackground.height / 2) - 
                             ((currentLatitude - 51.505600) * 100000 * zoomLevel) - 
                             height * (zoomLevel - 1) / 2 : 0

            // Kartenrand
            Rectangle {
                id: mapBorder
                anchors.fill: parent
                color: "transparent"
                border.width: 2
                border.color: "#ff2222"  // Rote Kante wie in CoD
                z: 10
            }
        }

        // Gitternetz-Overlay
        Grid {
            visible: showGrid
            anchors.fill: parent
            columns: 20
            rows: 20
            z: 5

            Repeater {
                model: 400 // 20x20 Grid
                Rectangle {
                    width: mapBackground.width / 20
                    height: mapBackground.height / 20
                    color: "transparent"
                    border.width: 1
                    border.color: "#ffffff22"  // Halbtransparente weiße Linien
                }
            }
        }

        // Koordinaten-Beschriftungen im militärischen Stil
        Row {
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.topMargin: 10
            height: 20
            spacing: mapBackground.width / 10

            Repeater {
                model: 10
                Text {
                    text: String.fromCharCode(65 + index) // A, B, C, usw.
                    color: "#ffffffaa"
                    font.pixelSize: 14
                    font.bold: true
                    width: mapBackground.width / 10
                    horizontalAlignment: Text.AlignHCenter
                }
            }
        }

        // Zahlenkoordinaten
        Column {
            anchors.left: parent.left
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            anchors.leftMargin: 10
            width: 20
            spacing: mapBackground.height / 10

            Repeater {
                model: 10
                Text {
                    text: (index + 1).toString() // 1, 2, 3, usw.
                    color: "#ffffffaa"
                    font.pixelSize: 14
                    font.bold: true
                    height: mapBackground.height / 10
                    verticalAlignment: Text.AlignVCenter
                }
            }
        }

        // POI-Marker für wichtige Orte
        Repeater {
            model: showMarkers ? [
                {name: "Airport", lat: 51.508, lon: 7.448, color: "#ffffff"},
                {name: "Downtown", lat: 51.505, lon: 7.452, color: "#ffffff"},
                {name: "Stadium", lat: 51.503, lon: 7.456, color: "#ffffff"},
                {name: "Hospital", lat: 51.507, lon: 7.454, color: "#ffff00"},
                {name: "Military Base", lat: 51.501, lon: 7.450, color: "#ff4444"}
            ] : []

            // POI-Marker im CoD-Stil
            Rectangle {
                id: poiMarker
                width: 8
                height: 8
                radius: 4
                color: modelData.color
                border.width: 1
                border.color: "white"
                // Position basierend auf Längen- und Breitengrad
                x: mapBackground.width / 2 + 
                   ((modelData.lon - currentLongitude) * 100000 * zoomLevel) - width/2
                y: mapBackground.height / 2 - 
                   ((modelData.lat - currentLatitude) * 100000 * zoomLevel) - height/2

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

        // Wegpunkte-Marker
        Repeater {
            model: waypointList
            Rectangle {
                id: waypointMarker
                width: 12
                height: 12
                radius: 6
                color: "#00000000"  // Transparent
                border.width: 2
                border.color: "#ffff00"  // Gelber Rand
                // Position basierend auf Längen- und Breitengrad
                x: mapBackground.width / 2 + 
                   ((modelData.longitude - currentLongitude) * 100000 * zoomLevel) - width/2
                y: mapBackground.height / 2 - 
                   ((modelData.latitude - currentLatitude) * 100000 * zoomLevel) - height/2

                // Pulseffekt wie in CoD
                Rectangle {
                    id: pulse
                    anchors.centerIn: parent
                    color: "transparent"
                    border.color: "#ffff00"
                    border.width: 2
                    width: parent.width
                    height: parent.height

                    SequentialAnimation {
                        running: true
                        loops: Animation.Infinite

                        ParallelAnimation {
                            NumberAnimation { target: pulse; property: "width"; from: waypointMarker.width; to: waypointMarker.width * 3; duration: 1500 }
                            NumberAnimation { target: pulse; property: "height"; from: waypointMarker.height; to: waypointMarker.height * 3; duration: 1500 }
                            NumberAnimation { target: pulse; property: "opacity"; from: 0.7; to: 0; duration: 1500 }
                        }

                        PropertyAction { target: pulse; property: "width"; value: waypointMarker.width }
                        PropertyAction { target: pulse; property: "height"; value: waypointMarker.height }
                        PropertyAction { target: pulse; property: "opacity"; value: 0.7 }
                    }
                }
            }
        }

        // Drohnen-Marker im CoD-Stil
        Item {
            id: droneMarker
            width: 16
            height: 16
            x: mapBackground.width / 2 - width / 2
            y: mapBackground.height / 2 - height / 2
            rotation: currentHeading

            // Drohnenindikator (Dreieck-Pfeil)
            Canvas {
                anchors.fill: parent
                onPaint: {
                    var ctx = getContext("2d");
                    ctx.fillStyle = "#00ff00";  // Grün wie im CoD HUD
                    ctx.strokeStyle = "white";
                    ctx.lineWidth = 1.5;

                    // Dreieckspfeil zeichnen
                    ctx.beginPath();
                    ctx.moveTo(width/2, 0);       // Spitze
                    ctx.lineTo(0, height);       // Unten links
                    ctx.lineTo(width, height);   // Unten rechts
                    ctx.closePath();
                    ctx.fill();
                    ctx.stroke();
                }
            }
        }
    }

    // Info-Panel für Koordinaten und Höhe
    Rectangle {
        id: infoPanel
        anchors.left: parent.left
        anchors.bottom: parent.bottom
        anchors.margins: 10
        width: 160
        height: 60
        color: Qt.rgba(0, 0, 0, 0.7)
        border.color: "#444444"
        border.width: 1

        Column {
            anchors.centerIn: parent
            spacing: 5
            width: parent.width - 10

            Text {
                text: "LAT: " + currentLatitude.toFixed(6)
                color: "#00ff00"
                font.pixelSize: 12
            }
            Text {
                text: "LON: " + currentLongitude.toFixed(6)
                color: "#00ff00"
                font.pixelSize: 12
            }
            Text {
                text: "ALT: " + currentAltitude.toFixed(1) + " m"
                color: "#00ff00"
                font.pixelSize: 12
            }
        }
    }

    // Zoom-Steuerung
    Row {
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.margins: 10
        spacing: 5

        Rectangle {
            width: 30
            height: 30
            color: Qt.rgba(0, 0, 0, 0.7)
            border.color: "#444444"
            border.width: 1

            Text {
                anchors.centerIn: parent
                text: "-"
                color: "white"
                font.pixelSize: 20
                font.bold: true
            }

            MouseArea {
                anchors.fill: parent
                onClicked: {
                    if (warzoneMapItem.zoomLevel > 0.5) {
                        warzoneMapItem.zoomLevel -= 0.1
                    }
                }
            }
        }

        Rectangle {
            width: 30
            height: 30
            color: Qt.rgba(0, 0, 0, 0.7)
            border.color: "#444444"
            border.width: 1

            Text {
                anchors.centerIn: parent
                text: "+"
                color: "white"
                font.pixelSize: 20
                font.bold: true
            }

            MouseArea {
                anchors.fill: parent
                onClicked: {
                    if (warzoneMapItem.zoomLevel < 2.0) {
                        warzoneMapItem.zoomLevel += 0.1
                    }
                }
            }
        }
    }
}
