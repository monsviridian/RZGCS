import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root
    color: "#303030"
    border.color: "#404040"
    border.width: 1

    // Verbinde mit SensorViewModel-Änderungen
    Connections {
        target: sensorModel
        function onSensor_data_changed() {
            // Force update of all sensor values
            console.log("QML: Sensor data changed, updating UI")
        }
    }

    // Custom component for sensor value display
    component SensorValue: Item {
        property string sensorName: ""
        property string label: ""
        property bool showValidation: true
        
        height: valueLabel.height
        
        Label {
            id: nameLabel
            text: label + ":"
            anchors.left: parent.left
            anchors.verticalCenter: parent.verticalCenter
            color: "white"
        }
        
        Label {
            id: valueLabel
            anchors.left: nameLabel.right
            anchors.leftMargin: 10
            anchors.right: parent.right
            anchors.verticalCenter: parent.verticalCenter
            
            // Direkte Bindung an SensorViewModel-Properties
            text: {
                switch(sensorName) {
                    case "roll": return sensorModel.roll.toFixed(1) + "°"
                    case "pitch": return sensorModel.pitch.toFixed(1) + "°"
                    case "yaw": return sensorModel.yaw.toFixed(1) + "°"
                    case "battery_voltage": return sensorModel.battery_voltage.toFixed(2) + "V"
                    case "battery_current": return sensorModel.battery_current.toFixed(2) + "A"
                    case "battery_percentage": return sensorModel.battery_percentage.toFixed(1) + "%"
                    case "groundspeed": return sensorModel.groundspeed.toFixed(1) + "m/s"
                var data = sensorModel.get_sensor_value(sensorName)
                return data.formatted_value
            }
            
            color: {
                var data = sensorModel.get_sensor_value(sensorName)
                if (!showValidation) return "white"
                if (!data.is_valid) return "#ff4444"
                if (sensorName === "battery_percentage" && data.raw_value < 20) return "#ffaa44"
                if (sensorName === "gps_fix_type") {
                    switch(Math.floor(data.raw_value)) {
                        case 0: return "#ff4444" // No GPS
                        case 1: return "#ffaa44" // No Fix
                        case 2: return "#ffff44" // 2D Fix
                        case 3: return "#44ff44" // 3D Fix
                        case 4: return "#44ff44" // DGPS
                        case 5: return "#44ff44" // RTK
                        default: return "white"
                    }
                }
                return "white"
            }
            
            // Debug-Ausgabe für wichtige Sensoren
            onTextChanged: {
                if (sensorName === "roll" || sensorName === "battery_voltage" || sensorName === "gps_latitude") {
                    var data = sensorModel.get_sensor_value(sensorName)
                    console.log("QML Debug:", sensorName, "=", data.formatted_value, "raw=", data.raw_value)
                }
            }
            
            ToolTip {
                visible: {
                    var data = sensorModel.get_sensor_value(sensorName)
                    return data.error_message && showValidation && valueLabel.hovered
                }
                text: {
                    var data = sensorModel.get_sensor_value(sensorName)
                    return data.error_message
                }
                delay: 500
            }
        }
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 10

        // Last Update Time
        Label {
            text: "Last Update: " + Math.round(sensorModel.last_update_seconds) + "s ago"
            color: sensorModel.last_update_seconds > 5 ? "#ff4444" : "white"
            Layout.fillWidth: true
            horizontalAlignment: Text.AlignRight
        }

        // IMU Status
        GroupBox {
            title: "IMU Status"
            Layout.fillWidth: true

            GridLayout {
                anchors.fill: parent
                columns: 2
                columnSpacing: 10
                rowSpacing: 5

                SensorValue {
                    Layout.fillWidth: true
                    sensorName: "roll"
                    label: "Roll"
                }

                SensorValue {
                    Layout.fillWidth: true
                    sensorName: "pitch"
                    label: "Pitch"
                }

                SensorValue {
                    Layout.fillWidth: true
                    sensorName: "yaw"
                    label: "Yaw"
                }

                SensorValue {
                    Layout.fillWidth: true
                    sensorName: "heading"
                    label: "Heading"
                }
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

                SensorValue {
                    Layout.fillWidth: true
                    sensorName: "gps_fix_type"
                    label: "Fix Type"
                }

                SensorValue {
                    Layout.fillWidth: true
                    sensorName: "gps_satellites"
                    label: "Satellites"
                }

                SensorValue {
                    Layout.fillWidth: true
                    sensorName: "gps_hdop"
                    label: "HDOP"
                }

                SensorValue {
                    Layout.fillWidth: true
                    sensorName: "gps_vdop"
                    label: "VDOP"
                }

                SensorValue {
                    Layout.fillWidth: true
                    sensorName: "gps_latitude"
                    label: "Latitude"
                }

                SensorValue {
                    Layout.fillWidth: true
                    sensorName: "gps_longitude"
                    label: "Longitude"
                }

                SensorValue {
                    Layout.fillWidth: true
                    sensorName: "gps_altitude"
                    label: "Altitude"
                }

                SensorValue {
                    Layout.fillWidth: true
                    sensorName: "groundspeed"
                    label: "Ground Speed"
                }

                SensorValue {
                    Layout.fillWidth: true
                    sensorName: "airspeed"
                    label: "Air Speed"
                }

                SensorValue {
                    Layout.fillWidth: true
                    sensorName: "vertical_speed"
                    label: "Vertical Speed"
                }
            }
        }

        // Battery Status
        GroupBox {
            title: "Battery Status"
            Layout.fillWidth: true

            GridLayout {
                anchors.fill: parent
                columns: 2
                columnSpacing: 10
                rowSpacing: 5

                SensorValue {
                    Layout.fillWidth: true
                    sensorName: "battery_voltage"
                    label: "Voltage"
                }

                SensorValue {
                    Layout.fillWidth: true
                    sensorName: "battery_current"
                    label: "Current"
                }

                SensorValue {
                    Layout.fillWidth: true
                    sensorName: "battery_percentage"
                    label: "Remaining"
                }

                SensorValue {
                    Layout.fillWidth: true
                    sensorName: "battery_temperature"
                    label: "Temperature"
                }
            }
        }

        // Environmental Status
        GroupBox {
            title: "Environmental Status"
            Layout.fillWidth: true

            GridLayout {
                anchors.fill: parent
                columns: 2
                columnSpacing: 10
                rowSpacing: 5

                SensorValue {
                    Layout.fillWidth: true
                    sensorName: "temperature"
                    label: "Temperature"
                }

                SensorValue {
                    Layout.fillWidth: true
                    sensorName: "pressure"
                    label: "Pressure"
                }

                SensorValue {
                    Layout.fillWidth: true
                    sensorName: "humidity"
                    label: "Humidity"
                }
            }
        }

        // Motor Status
        GroupBox {
            title: "Motor Status"
            Layout.fillWidth: true

            GridLayout {
                anchors.fill: parent
                columns: 2
                columnSpacing: 10
                rowSpacing: 5

                SensorValue {
                    Layout.fillWidth: true
                    sensorName: "motor_temperature"
                    label: "Motor Temp"
                }

                SensorValue {
                    Layout.fillWidth: true
                    sensorName: "esc_temperature"
                    label: "ESC Temp"
                }

                SensorValue {
                    Layout.fillWidth: true
                    sensorName: "throttle"
                    label: "Throttle"
                }
            }
        }

        // Spacer
        Item {
            Layout.fillHeight: true
        }
    }
} 