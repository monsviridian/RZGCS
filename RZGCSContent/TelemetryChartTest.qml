import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import Components 1.0

ApplicationWindow {
    visible: true
    width: 900
    height: 600
    title: "Telemetry Chart Test"

    Component.onCompleted: {
        console.log("D: TelemetryChartTest.qml - ApplicationWindow completed")
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 20

        Label {
            text: "Demo: TelemetryChart mit Beispieldaten"
            font.pixelSize: 24
            Layout.alignment: Qt.AlignHCenter
        }

        // Echte TelemetryChart-Komponente
        TelemetryChart {
            id: telemetryChart
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.preferredHeight: 400
            chartTitle: "Altitude (Demo)"
            dataType: "altitude"
            showDemoData: true
            
            Component.onCompleted: {
                console.log("D: TelemetryChart Component.onCompleted")
                console.log("D: TelemetryChart width:", width)
                console.log("D: TelemetryChart height:", height)
                console.log("D: TelemetryChart visible:", visible)
                console.log("D: TelemetryChart showDemoData:", showDemoData)
            }
        }

        // Debug-Info
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 100
            color: "#2a2a2a"
            border.color: "#444"
            border.width: 1
            radius: 5

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 10
                spacing: 5

                Text {
                    text: "Debug Info:"
                    color: "#fff"
                    font.pixelSize: 14
                    font.bold: true
                }

                Text {
                    text: "TelemetryChart loaded: " + (telemetryChart ? "YES" : "NO")
                    color: telemetryChart ? "#4CAF50" : "#f44336"
                    font.pixelSize: 12
                }

                Text {
                    text: "Chart visible: " + telemetryChart.visible
                    color: telemetryChart.visible ? "#4CAF50" : "#f44336"
                    font.pixelSize: 12
                }

                Text {
                    text: "Chart size: " + telemetryChart.width + "x" + telemetryChart.height
                    color: "#fff"
                    font.pixelSize: 12
                }

                Text {
                    text: "Show demo data: " + telemetryChart.showDemoData
                    color: telemetryChart.showDemoData ? "#4CAF50" : "#f44336"
                    font.pixelSize: 12
                }
            }
        }
    }
} 