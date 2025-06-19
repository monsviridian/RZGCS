import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root
    color: "#303030"
    border.color: "#404040"
    border.width: 1

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 10

        // IMU Status
        GroupBox {
            title: "IMU Status"
            Layout.fillWidth: true

            GridLayout {
                anchors.fill: parent
                columns: 2
                columnSpacing: 10
                rowSpacing: 5

                Label { text: "Accelerometer:" }
                Label { text: "Not Ready" }

                Label { text: "Gyroscope:" }
                Label { text: "Not Ready" }

                Label { text: "Magnetometer:" }
                Label { text: "Not Ready" }

                Label { text: "Barometer:" }
                Label { text: "Not Ready" }
            }
        }

        // GPS Status
        GroupBox {
            title: "GPS Status"
            Layout.fillWidth: true

            GridLayout {
                anchors.fill: parent
                columns: 2
                columnSpacing: 10
                rowSpacing: 5

                Label { text: "Fix Type:" }
                Label { text: "No Fix" }

                Label { text: "Satellites:" }
                Label { text: "0" }

                Label { text: "HDOP:" }
                Label { text: "0.0" }

                Label { text: "VDOP:" }
                Label { text: "0.0" }

                Label { text: "Latitude:" }
                Label { text: "0.0" }

                Label { text: "Longitude:" }
                Label { text: "0.0" }

                Label { text: "Altitude:" }
                Label { text: "0.0 m" }

                Label { text: "Ground Speed:" }
                Label { text: "0.0 m/s" }
            }
        }

        // RC Status
        GroupBox {
            title: "RC Status"
            Layout.fillWidth: true

            GridLayout {
                anchors.fill: parent
                columns: 2
                columnSpacing: 10
                rowSpacing: 5

                Label { text: "Connected:" }
                Label { text: "No" }

                Label { text: "RSSI:" }
                Label { text: "0%" }

                Label { text: "Channel 1:" }
                Label { text: "0" }

                Label { text: "Channel 2:" }
                Label { text: "0" }

                Label { text: "Channel 3:" }
                Label { text: "0" }

                Label { text: "Channel 4:" }
                Label { text: "0" }

                Label { text: "Channel 5:" }
                Label { text: "0" }

                Label { text: "Channel 6:" }
                Label { text: "0" }
            }
        }

        // Aktionen
        RowLayout {
            Layout.fillWidth: true
            spacing: 10

            Button {
                text: "Calibrate IMU"
                Layout.fillWidth: true
                onClicked: {
                    // TODO: Start IMU calibration
                }
            }

            Button {
                text: "Calibrate Compass"
                Layout.fillWidth: true
                onClicked: {
                    // TODO: Start compass calibration
                }
            }

            Button {
                text: "Calibrate RC"
                Layout.fillWidth: true
                onClicked: {
                    // TODO: Start RC calibration
                }
            }
        }
    }
} 