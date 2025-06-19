import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Window 2.15

// Füge Timer hinzu, um Canvas neu zu zeichnen, wenn Sensordaten aktualisiert werden

Item {
    id: root
    width: 1000
    height: 650
    
    // Timer zum Neu-Zeichnen von Komponenten bei Sensoränderungen
    Timer {
        interval: 500  // Intervall für Updates
        running: true
        repeat: true
        onTriggered: {
            // Neu-Zeichnen der Canvas-Elemente
            if (telemetryCanvas) telemetryCanvas.requestPaint();
            if (batteryCanvas) batteryCanvas.requestPaint();
        }
    }
    
    Rectangle {
        anchors.fill: parent
        color: "#10181c"
    }
    // Oberer Statusbereich
    RowLayout {
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.margins: 24
        spacing: 32
        height: 40
        // Icons und dynamische Werte
        Text { text: "\uF1EB"; font.family: "FontAwesome"; color: "#7ee6ff"; font.pixelSize: 22 } // WiFi
        Text { text: "\uF185"; font.family: "FontAwesome"; color: "#7ee6ff"; font.pixelSize: 22 } // Sun
        Text { 
            text: {
                var battery = sensorModel.findSensorByName("Battery");
                return battery ? battery.value + " %" : "-- %";
            }
            color: "#e6faff"; font.pixelSize: 20 
        }
        Text { text: "\u26A0"; color: "#ffb84b"; font.pixelSize: 22 } // Warnung
        Text { text: "\uF1EB"; font.family: "FontAwesome"; color: "#7ee6ff"; font.pixelSize: 22 } // WiFi
        Text { 
            text: { 
                var altitude = sensorModel.findSensorByName("Altitude");
                return altitude ? altitude.value + " m" : "-- m";
            }
            color: "#e6faff"; font.pixelSize: 20 
        }
        Text { text: "S\u223C\u223C"; color: "#e6faff"; font.pixelSize: 20 }
        Text { 
            text: { 
                var speed = sensorModel.findSensorByName("Ground Speed");
                return speed ? speed.value + " km/h" : "-- km/h";
            }
            color: "#e6faff"; font.pixelSize: 20 
        }
    }
    // Hauptbereich
    GridLayout {
        anchors.top: parent.top
        anchors.topMargin: 64
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.margins: 24
        columns: 2
        rowSpacing: 24
        columnSpacing: 24
        // Logo und Bild
        Rectangle {
            Layout.row: 0; Layout.column: 0
            Layout.preferredWidth: 420
            Layout.preferredHeight: 180
            color: "#181f23"
            radius: 12
            border.color: "#23343b"
            border.width: 2
            RowLayout {
                anchors.fill: parent
                anchors.margins: 20
                spacing: 20
                // Logo (SVG/PNG oder Text)
                ColumnLayout {
                    spacing: 0
                    Text {
                        text: "RZ"
                        color: "#3ee6ff"
                        font.pixelSize: 44
                        font.bold: true
                    }
                    Text {
                        text: "DRONE"
                        color: "#e6faff"
                        font.pixelSize: 36
                        font.bold: true
                    }
                    Text {
                        text: "SOLUTIONS"
                        color: "#e6faff"
                        font.pixelSize: 18
                        font.letterSpacing: 2
                    }
                }
                Rectangle {
                    width: 120; height: 80
                    color: "transparent"
                    border.color: "#3ee6ff"
                    border.width: 2
                    radius: 8
                    Text {
                        anchors.centerIn: parent
                        text: "\uD83D\uDE81"
                        color: "#3ee6ff"
                        font.pixelSize: 60
                    }
                }
            }
        }
        Rectangle {
            Layout.row: 0; Layout.column: 1
            Layout.preferredWidth: 420
            Layout.preferredHeight: 180
            color: "#181f23"
            radius: 12
            border.color: "#23343b"
            border.width: 2
            // Bild/Video-Feed (Platzhalter)
            Image {
                anchors.fill: parent
                anchors.margins: 16
                source: "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=600&q=80"
                fillMode: Image.PreserveAspectCrop
                smooth: true
            }
        }
        // Map View
        Rectangle {
            Layout.row: 1; Layout.column: 0
            Layout.preferredWidth: 420
            Layout.preferredHeight: 220
            color: "#181f23"
            radius: 12
            border.color: "#23343b"
            border.width: 2
            Text {
                text: "MAP VIEW"
                color: "#7ee6ff"
                font.pixelSize: 16
                anchors.left: parent.left
                anchors.leftMargin: 16
                anchors.top: parent.top
                anchors.topMargin: 8
            }
            // Dummy Map
            Canvas {
                anchors.fill: parent
                anchors.margins: 32
                onPaint: {
                    var ctx = getContext("2d");
                    ctx.reset();
                    ctx.strokeStyle = "#3ee6ff";
                    ctx.lineWidth = 2;
                    ctx.beginPath();
                    ctx.moveTo(20, 80); ctx.lineTo(120, 40); ctx.lineTo(200, 120); ctx.lineTo(300, 60);
                    ctx.stroke();
                    ctx.beginPath();
                    ctx.arc(120, 80, 10, 0, 2*Math.PI);
                    ctx.fillStyle = "#3ee6ff";
                    ctx.fill();
                }
            }
        }
        // Telemetry Graph
        Rectangle {
            Layout.row: 1; Layout.column: 1
            Layout.preferredWidth: 420
            Layout.preferredHeight: 220
            color: "#181f23"
            radius: 12
            border.color: "#23343b"
            border.width: 2
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 16
                spacing: 8
                Text {
                    text: "TELEMETRY"
                    color: "#e6faff"
                    font.pixelSize: 18
                }
                RowLayout {
                    spacing: 16
                    Text { text: "Altitude"; color: "#3ee6ff"; font.pixelSize: 14 }
                    Text { text: "Distance"; color: "#7ee6ff"; font.pixelSize: 14 }
                    Text { text: "Speed"; color: "#e6faff"; font.pixelSize: 14 }
                }
                Canvas {
                    id: telemetryCanvas
                    width: parent.width; height: 100
                    property var values1: {
                        var altitude = sensorModel.findSensorByName("Altitude");
                        return altitude ? altitude.values : [50,60,40,70,55,80,60,90,70,100,80,60,70,90,100];
                    }
                    property var values2: {
                        var distance = sensorModel.findSensorByName("Distance") || sensorModel.findSensorByName("Home Distance");
                        return distance ? distance.values : [30,40,35,50,45,60,50,70,60,80,70,60,70,80,90];
                    }
                    property var values3: {
                        var speed = sensorModel.findSensorByName("Ground Speed");
                        return speed ? speed.values : [20,30,25,40,35,50,40,60,50,70,60,50,60,70,80];
                    }
                    onPaint: {
                        var ctx = getContext("2d");
                        ctx.reset();
                        var w = width, h = height;
                        // Altitude
                        ctx.strokeStyle = "#3ee6ff";
                        ctx.lineWidth = 2;
                        ctx.beginPath();
                        for (var i=0; i<values1.length; ++i) {
                            var x = i/(values1.length-1)*w;
                            var y = h - (values1[i]/100)*h;
                            if (i===0) ctx.moveTo(x,y);
                            else ctx.lineTo(x,y);
                        }
                        ctx.stroke();
                        // Distance
                        ctx.strokeStyle = "#7ee6ff";
                        ctx.lineWidth = 2;
                        ctx.beginPath();
                        for (var i=0; i<values2.length; ++i) {
                            var x = i/(values2.length-1)*w;
                            var y = h - (values2[i]/100)*h;
                            if (i===0) ctx.moveTo(x,y);
                            else ctx.lineTo(x,y);
                        }
                        ctx.stroke();
                        // Speed
                        ctx.strokeStyle = "#e6faff";
                        ctx.lineWidth = 2;
                        ctx.beginPath();
                        for (var i=0; i<values3.length; ++i) {
                            var x = i/(values3.length-1)*w;
                            var y = h - (values3[i]/100)*h;
                            if (i===0) ctx.moveTo(x,y);
                            else ctx.lineTo(x,y);
                        }
                        ctx.stroke();
                    }
                }
            }
        }
        // Untere Wertefelder
        Rectangle {
            Layout.row: 2; Layout.column: 0
            Layout.columnSpan: 1
            Layout.preferredHeight: 100
            color: "#181f23"
            radius: 12
            border.color: "#23343b"
            border.width: 2
            RowLayout {
                anchors.fill: parent
                anchors.margins: 16
                spacing: 32
                ColumnLayout {
                    spacing: 0
                    Text { text: "ALTITUDE"; color: "#7ee6ff"; font.pixelSize: 14 }
                    Text { 
                        text: { 
                            var altitude = sensorModel.findSensorByName("Altitude");
                            return altitude ? altitude.value + " m" : "-- m";
                        }
                        color: "#e6faff"; font.pixelSize: 32; font.bold: true 
                    }
                }
                ColumnLayout {
                    spacing: 0
                    Text { text: "DISTANCE"; color: "#7ee6ff"; font.pixelSize: 14 }
                    Text { 
                        text: { 
                            var distance = sensorModel.findSensorByName("Distance") || sensorModel.findSensorByName("Home Distance");
                            return distance ? distance.value + " m" : "-- m";
                        }
                        color: "#e6faff"; font.pixelSize: 32; font.bold: true 
                    }
                }
            }
        }
        // Battery-Ring und Speed
        Rectangle {
            Layout.row: 2; Layout.column: 1
            Layout.columnSpan: 1
            Layout.preferredHeight: 100
            color: "#181f23"
            radius: 12
            border.color: "#23343b"
            border.width: 2
            RowLayout {
                anchors.fill: parent
                anchors.margins: 16
                spacing: 32
                // Battery-Ring
                Item {
                    width: 70; height: 70
                    Canvas {
                        id: batteryCanvas
                        anchors.fill: parent
                        property real percent: {
                            var battery = sensorModel.findSensorByName("Battery");
                            return battery ? battery.value / 100.0 : 0.0;
                        }
                        onPaint: {
                            var ctx = getContext("2d");
                            ctx.reset();
                            var w = width, h = height, r = Math.min(w,h)/2-6;
                            var cx = w/2, cy = h/2;
                            // Hintergrund-Kreis
                            ctx.beginPath();
                            ctx.arc(cx, cy, r, 0, 2*Math.PI);
                            ctx.strokeStyle = "#23343b";
                            ctx.lineWidth = 8;
                            ctx.stroke();
                            // Fortschritt
                            ctx.beginPath();
                            ctx.arc(cx, cy, r, -Math.PI/2, -Math.PI/2 + 2*Math.PI*percent);
                            ctx.strokeStyle = "#3ee6ff";
                            ctx.lineWidth = 8;
                            ctx.stroke();
                        }
                    }
                    Text {
                        anchors.centerIn: parent
                        text: {
                            var battery = sensorModel.findSensorByName("Battery");
                            return battery ? battery.value + "%" : "--%";
                        }
                        color: "#e6faff"
                        font.pixelSize: 22
                        font.bold: true
                    }
                }
                // Speed
                ColumnLayout {
                    spacing: 0
                    Text { text: "SPEED"; color: "#7ee6ff"; font.pixelSize: 14 }
                    Text { 
                        text: { 
                            var speed = sensorModel.findSensorByName("Ground Speed");
                            return speed ? speed.value + " km/h" : "-- km/h";
                        }
                        color: "#e6faff"; font.pixelSize: 32; font.bold: true 
                    }
                }
            }
        }
    }
}