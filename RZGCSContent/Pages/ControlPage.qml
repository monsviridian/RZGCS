import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
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

    ColumnLayout {
        anchors.fill: parent
        spacing: 20

        // Flight Mode Selection
        GroupBox {
            title: "Flight Mode"
            Layout.fillWidth: true

            RowLayout {
                anchors.fill: parent
                spacing: 10

                ComboBox {
                    id: flightModeCombo
                    model: ["STABILIZE", "LOITER", "RTL"]
                    Layout.fillWidth: true
                    onCurrentTextChanged: {
                        if (serialConnector) {
                            serialConnector.set_flight_mode(currentText)
                        }
                    }
                }
            }
        }

        // Arm/Disarm Control
        GroupBox {
            title: "System Control"
            Layout.fillWidth: true

            RowLayout {
                anchors.fill: parent
                spacing: 10

                Button {
                    text: "ARM"
                    Layout.fillWidth: true
                    Material.background: Material.Green
                    onClicked: {
                        if (serialConnector) {
                            serialConnector.set_armed(true)
                        }
                    }
                }

                Button {
                    text: "DISARM"
                    Layout.fillWidth: true
                    Material.background: Material.Red
                    onClicked: {
                        if (serialConnector) {
                            serialConnector.set_armed(false)
                        }
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