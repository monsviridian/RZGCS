import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Window 2.15
import QtQuick.Shapes 1.15

Item {
    id: root
    width: 1000
    height: 650
    Rectangle {
        anchors.fill: parent
        color: "#10181c"
    }
    GridLayout {
        anchors.fill: parent
        anchors.margins: 32
        columns: 4
        rowSpacing: 24
        columnSpacing: 24

        // GPS Gauge
        Gauge {
            Layout.row: 0; Layout.column: 0
            title: "GPS"
            value: 2.3
            minValue: 0; maxValue: 7
        }
        // IMU Warning
        WarningBox {
            Layout.row: 0; Layout.column: 1
            text: "IMU"
        }
        // Luftdruck
        ValueBox {
            Layout.row: 0; Layout.column: 2
            value: "1012"
            unit: "hPa"
        }
        // Barometer Gauge
        Gauge {
            Layout.row: 0; Layout.column: 3
            title: "Barometer"
            value: 1042
            minValue: 900; maxValue: 1100
        }
        // Batterie
        BatteryBox {
            Layout.row: 1; Layout.column: 0
            percent: 32
            temp: 85
        }
        // ATTOP TEMP Warning
        WarningBox {
            Layout.row: 1; Layout.column: 1
            text: "ATTOP TEMP"
        }
        // Drohnen-Icon (Platzhalter)
        Rectangle {
            Layout.row: 1; Layout.column: 2
            Layout.rowSpan: 2
            Layout.columnSpan: 1
            color: "transparent"
            width: 180; height: 180
            anchors.centerIn: parent
            Shape {
                anchors.fill: parent
                ShapePath {
                    strokeColor: "#23343b"; strokeWidth: 8
                    fillColor: "#23343b"
                    startX: 150; startY: 90
                    PathArc {
                        x: 90; y: 90
                        radiusX: 60; radiusY: 60
                        useLargeArc: true
                        direction: PathArc.Clockwise
                    }
                    PathArc {
                        x: 150; y: 90
                        radiusX: 60; radiusY: 60
                        useLargeArc: true
                        direction: PathArc.Clockwise
                    }
                }
            }
        }
        // Signal
        ValueBox {
            Layout.row: 1; Layout.column: 3
            value: "-60"
            unit: "dBm"
            icon: "📶"
        }
        // Altitude Chart
        ChartBox {
            Layout.row: 2; Layout.column: 0
            title: "Altitude"
            values: [50,60,40,70,55,80,60,90,70,100,80,60,70,90,100]
            minY: 0; maxY: 100
        }
        // Temperatur Warning
        WarningBox {
            Layout.row: 2; Layout.column: 1
            text: "55 °C"
        }
        // Voltage Chart
        ChartBox {
            Layout.row: 2; Layout.column: 3
            title: "Voltage"
            values: [40,39,38,37,36,35,34,33,32,31,30,31,32,33,34,35,36,37,38,39,40]
            minY: 30; maxY: 40
        }
    }

    // --- Inline Components ---
    component Gauge : Item {
        property string title: ""
        property real value: 0
        property real minValue: 0
        property real maxValue: 100
        width: 200; height: 180
        Rectangle {
            anchors.fill: parent
            color: "#182328"
            radius: 16
            border.color: "#23343b"
            border.width: 2
        }
        Canvas {
            id: gaugeCanvas
            anchors.fill: parent
            onPaint: {
                var ctx = getContext("2d");
                ctx.reset();
                var w = width, h = height;
                var cx = w/2, cy = h*0.65, r = Math.min(w,h)*0.38;
                // Skala
                ctx.strokeStyle = "#3ee6ff";
                ctx.lineWidth = 4;
                ctx.beginPath();
                ctx.arc(cx, cy, r, Math.PI*0.75, Math.PI*0.25, false);
                ctx.stroke();
                // Zeiger
                var angle = Math.PI*0.75 + (Math.PI*1.5)*(value-minValue)/(maxValue-minValue);
                ctx.strokeStyle = "#ff4b4b";
                ctx.lineWidth = 5;
                ctx.beginPath();
                ctx.moveTo(cx, cy);
                ctx.lineTo(cx + r*Math.cos(angle), cy + r*Math.sin(angle));
                ctx.stroke();
            }
        }
        Text {
            text: title
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 16
            color: "#e6faff"
            font.pixelSize: 20
        }
        Text {
            text: value.toFixed(1)
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.verticalCenter: parent.verticalCenter
            color: "#e6faff"
            font.pixelSize: 32
            font.bold: true
        }
    }
    component WarningBox : Item {
        property string text: ""
        width: 160; height: 90
        Rectangle {
            anchors.fill: parent
            color: "#182328"
            radius: 16
            border.color: "#ff4b4b"
            border.width: 2
            Column {
                anchors.centerIn: parent
                spacing: 4
                Text { text: "\u26A0"; color: "#ff4b4b"; font.pixelSize: 32 }
                Text { text: parent.parent.text; color: "#ff4b4b"; font.pixelSize: 18; font.bold: true }
            }
        }
    }
    component ValueBox : Item {
        property string value: ""
        property string unit: ""
        property string icon: ""
        width: 160; height: 90
        Rectangle {
            anchors.fill: parent
            color: "#182328"
            radius: 16
            border.color: "#23343b"
            border.width: 2
            Row {
                anchors.centerIn: parent
                spacing: 8
                Text { text: icon; color: "#3ee6ff"; font.pixelSize: 28 }
                Text { text: value; color: "#e6faff"; font.pixelSize: 32; font.bold: true }
                Text { text: unit; color: "#3ee6ff"; font.pixelSize: 18; anchors.bottom: parent.bottom; anchors.bottomMargin: 8 }
            }
        }
    }
    component BatteryBox : Item {
        property int percent: 0
        property int temp: 0
        width: 160; height: 90
        Rectangle {
            anchors.fill: parent
            color: "#182328"
            radius: 16
            border.color: "#23343b"
            border.width: 2
            Row {
                anchors.centerIn: parent
                spacing: 8
                Text { text: "\uD83D\uDD0B"; color: "#ff4b4b"; font.pixelSize: 28 }
                Text { text: percent + "%"; color: "#e6faff"; font.pixelSize: 32; font.bold: true }
                Text { text: temp + "°C"; color: "#ff4b4b"; font.pixelSize: 18 }
            }
        }
    }
    component ChartBox : Item {
        property string title: ""
        property var values: []
        property real minY: 0
        property real maxY: 100
        width: 320; height: 120
        Rectangle {
            anchors.fill: parent
            color: "#182328"
            radius: 16
            border.color: "#23343b"
            border.width: 2
            Column {
                anchors.fill: parent
                anchors.margins: 8
                spacing: 2
                Text { text: title; color: "#e6faff"; font.pixelSize: 18 }
                Canvas {
                    id: chartCanvas
                    width: parent.width; height: 70
                    property var chartValues: values
                    property real chartMinY: minY
                    property real chartMaxY: maxY
                    onPaint: {
                        var ctx = getContext("2d");
                        ctx.reset();
                        var w = width, h = height;
                        var vals = chartValues || [0];
                        ctx.strokeStyle = "#3ee6ff";
                        ctx.lineWidth = 2;
                        ctx.beginPath();
                        for (var i=0; i<vals.length; ++i) {
                            var x = i/(vals.length-1)*w;
                            var y = h - (vals[i]-chartMinY)/(chartMaxY-chartMinY)*h;
                            if (i===0) ctx.moveTo(x,y);
                            else ctx.lineTo(x,y);
                        }
                        ctx.stroke();
                    }
                }
            }
        }
    }
} 