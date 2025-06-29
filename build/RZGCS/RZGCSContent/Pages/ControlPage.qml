import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtPositioning
import QtLocation
import QtQuick.Controls.Material
import "../Components"
import "../Constants"

Page {
    id: controlPage
    title: "Control"

    property var serialConnector
    property var sensorModel

    // Signale
    signal modeChanged(string mode)
    signal controlModeChanged(string mode)
    signal emergencyTriggered(string procedure)

    ColumnLayout {
        anchors.fill: parent
        spacing: 20

        // Flugmodus
        GroupBox {
            title: "Flight Mode"
            Layout.fillWidth: true

            ColumnLayout {
                anchors.fill: parent
                spacing: 10

                ComboBox {
                    id: modeCombo
                    Layout.fillWidth: true
                    model: ["MANUAL", "STABILIZE", "ALTHOLD", "LOITER", "RTL", "AUTO"]
                    onCurrentTextChanged: {
                        modeChanged(currentText)
                    }
                }
            }
        }

        // Steuerungsmodus
        GroupBox {
            title: "Control Mode"
            Layout.fillWidth: true

            ColumnLayout {
                anchors.fill: parent
                spacing: 10

                ComboBox {
                    id: controlModeCombo
                    Layout.fillWidth: true
                    model: ["BASIC", "ADVANCED", "EXPERT"]
                    onCurrentTextChanged: {
                        controlModeChanged(currentText)
                    }
                }
            }
        }

        // Notfall-Prozeduren
        GroupBox {
            title: "Emergency Procedures"
            Layout.fillWidth: true

            GridLayout {
                anchors.fill: parent
                columns: 2
                columnSpacing: 10
                rowSpacing: 10

                Button {
                    text: "Return to Home"
                    Layout.fillWidth: true
                    onClicked: {
                        emergencyTriggered("RETURN_TO_HOME")
                    }
                }

                Button {
                    text: "Land"
                    Layout.fillWidth: true
                    onClicked: {
                        emergencyTriggered("LAND")
                    }
                }

                Button {
                    text: "Kill Motors"
                    Layout.fillWidth: true
                    onClicked: {
                        emergencyTriggered("KILL_MOTORS")
                    }
                }

                Button {
                    text: "Terminate"
                    Layout.fillWidth: true
                    onClicked: {
                        emergencyTriggered("TERMINATE")
                    }
                }
            }
        }

        // Steuerung
        GroupBox {
            title: "Control"
            Layout.fillWidth: true

            ColumnLayout {
                anchors.fill: parent
                spacing: 10

                // Pitch/Roll
                RowLayout {
                    Layout.fillWidth: true
                    spacing: 10

                    Label {
                        text: "Pitch"
                    }

                    Slider {
                        id: pitchSlider
                        Layout.fillWidth: true
                        from: -1.0
                        to: 1.0
                        value: 0.0
                    }

                    Label {
                        text: "Roll"
                    }

                    Slider {
                        id: rollSlider
                        Layout.fillWidth: true
                        from: -1.0
                        to: 1.0
                        value: 0.0
                    }
                }

                // Yaw/Thrust
                RowLayout {
                    Layout.fillWidth: true
                    spacing: 10

                    Label {
                        text: "Yaw"
                    }

                    Slider {
                        id: yawSlider
                        Layout.fillWidth: true
                        from: -1.0
                        to: 1.0
                        value: 0.0
                    }

                    Label {
                        text: "Thrust"
                    }

                    Slider {
                        id: thrustSlider
                        Layout.fillWidth: true
                        from: 0.0
                        to: 1.0
                        value: 0.0
                    }
                }
            }
        }

        // Safety
        GroupBox {
            title: "Safety"
            Layout.fillWidth: true

            RowLayout {
                anchors.fill: parent
                spacing: 10

                Button {
                    text: "Enable Safety"
                    Layout.fillWidth: true
                    onClicked: {
                        backend.enableSafety()
                    }
                }

                Button {
                    text: "Disable Safety"
                    Layout.fillWidth: true
                    onClicked: {
                        backend.disableSafety()
                    }
                }
            }
        }

        // Sensor Data Display
        GroupBox {
            title: "Sensor Data"
            Layout.fillWidth: true
            Layout.fillHeight: true

            GridLayout {
                anchors.fill: parent
                columns: 2
                columnSpacing: 20
                rowSpacing: 10

                Label { text: "GPS:" }
                Label { 
                    text: sensorModel ? 
                        `Lat: ${sensorModel.get_sensor_value("gps_lat").toFixed(6)}° Lon: ${sensorModel.get_sensor_value("gps_lon").toFixed(6)}°` : 
                        "No data"
                }

                Label { text: "Altitude:" }
                Label { 
                    text: sensorModel ? 
                        `${sensorModel.get_sensor_value("altitude").toFixed(1)} m` : 
                        "No data"
                }

                Label { text: "Attitude:" }
                Label { 
                    text: sensorModel ? 
                        `Roll: ${sensorModel.get_sensor_value("roll").toFixed(1)}° Pitch: ${sensorModel.get_sensor_value("pitch").toFixed(1)}° Yaw: ${sensorModel.get_sensor_value("yaw").toFixed(1)}°` : 
                        "No data"
                }

                Label { text: "Speed:" }
                Label { 
                    text: sensorModel ? 
                        `Air: ${sensorModel.get_sensor_value("airspeed").toFixed(1)} m/s Ground: ${sensorModel.get_sensor_value("groundspeed").toFixed(1)} m/s` : 
                        "No data"
                }

                Label { text: "Battery:" }
                Label { 
                    text: sensorModel ? 
                        `${sensorModel.get_sensor_value("battery_voltage").toFixed(1)}V ${sensorModel.get_sensor_value("battery_current").toFixed(1)}A (${sensorModel.get_sensor_value("battery_remaining").toFixed(0)}%)` : 
                        "No data"
                }
            }
        }
    }
} 