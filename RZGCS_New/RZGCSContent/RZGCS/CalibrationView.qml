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

        // Kalibrierungsoptionen
        GroupBox {
            title: "Calibration Options"
            Layout.fillWidth: true

            ColumnLayout {
                anchors.fill: parent
                spacing: 10

                // IMU Kalibrierung
                GroupBox {
                    title: "IMU Calibration"
                    Layout.fillWidth: true

                    ColumnLayout {
                        anchors.fill: parent
                        spacing: 5

                        Label {
                            text: "Calibrate the Inertial Measurement Unit (IMU)"
                            wrapMode: Text.WordWrap
                        }

                        Button {
                            text: "Start IMU Calibration"
                            Layout.fillWidth: true
                            onClicked: {
                                // TODO: Start IMU calibration
                            }
                        }
                    }
                }

                // Kompass Kalibrierung
                GroupBox {
                    title: "Compass Calibration"
                    Layout.fillWidth: true

                    ColumnLayout {
                        anchors.fill: parent
                        spacing: 5

                        Label {
                            text: "Calibrate the compass by rotating the vehicle in all directions"
                            wrapMode: Text.WordWrap
                        }

                        Button {
                            text: "Start Compass Calibration"
                            Layout.fillWidth: true
                            onClicked: {
                                // TODO: Start compass calibration
                            }
                        }
                    }
                }

                // RC Kalibrierung
                GroupBox {
                    title: "RC Calibration"
                    Layout.fillWidth: true

                    ColumnLayout {
                        anchors.fill: parent
                        spacing: 5

                        Label {
                            text: "Calibrate the radio control channels"
                            wrapMode: Text.WordWrap
                        }

                        Button {
                            text: "Start RC Calibration"
                            Layout.fillWidth: true
                            onClicked: {
                                // TODO: Start RC calibration
                            }
                        }
                    }
                }

                // ESC Kalibrierung
                GroupBox {
                    title: "ESC Calibration"
                    Layout.fillWidth: true

                    ColumnLayout {
                        anchors.fill: parent
                        spacing: 5

                        Label {
                            text: "Calibrate the Electronic Speed Controllers (ESC)"
                            wrapMode: Text.WordWrap
                        }

                        Button {
                            text: "Start ESC Calibration"
                            Layout.fillWidth: true
                            onClicked: {
                                // TODO: Start ESC calibration
                            }
                        }
                    }
                }

                // Level Kalibrierung
                GroupBox {
                    title: "Level Calibration"
                    Layout.fillWidth: true

                    ColumnLayout {
                        anchors.fill: parent
                        spacing: 5

                        Label {
                            text: "Calibrate the level of the vehicle"
                            wrapMode: Text.WordWrap
                        }

                        Button {
                            text: "Start Level Calibration"
                            Layout.fillWidth: true
                            onClicked: {
                                // TODO: Start level calibration
                            }
                        }
                    }
                }
            }
        }

        // Status
        GroupBox {
            title: "Calibration Status"
            Layout.fillWidth: true

            GridLayout {
                anchors.fill: parent
                columns: 2
                columnSpacing: 10
                rowSpacing: 5

                Label { text: "IMU:" }
                Label { text: "Not Calibrated" }

                Label { text: "Compass:" }
                Label { text: "Not Calibrated" }

                Label { text: "RC:" }
                Label { text: "Not Calibrated" }

                Label { text: "ESC:" }
                Label { text: "Not Calibrated" }

                Label { text: "Level:" }
                Label { text: "Not Calibrated" }
            }
        }

        // Fortschritt
        ProgressBar {
            id: calibrationProgress
            Layout.fillWidth: true
            from: 0
            to: 100
            value: 0
            visible: false
        }
    }
} 