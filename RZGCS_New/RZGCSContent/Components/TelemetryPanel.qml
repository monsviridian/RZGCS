import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

/**
 * TelemetryPanel - Emulates the telemetry display from Mission Planner
 * Shows flight data: altitude, speed, position, etc.
 */
Rectangle {
    id: telemetryPanel
    color: "#303030"
    border.color: "#404040"
    border.width: 1
    
    // Properties for telemetry data
    property real altitude: 0.0
    property real groundSpeed: 0.0
    property real airSpeed: 0.0
    property real verticalSpeed: 0.0
    property real distToWP: 0.0
    property real heading: 0.0
    property real waypointBearing: 0.0
    property real throttlePercent: 0
    property int batteryPercent: 100
    property real batteryVoltage: 12.6
    property real batteryCurrent: 0.0
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 5
        
        GridLayout {
            Layout.fillWidth: true
            columns: 2
            rowSpacing: 10
            columnSpacing: 15
            
            // Altitude display
            Label {
                text: "Altitude (m)"
                font.pixelSize: 12
                color: "white"
            }
            
            Label {
                text: altitude.toFixed(2)
                font.pixelSize: 24
                font.bold: true
                color: "#00aaff"
                horizontalAlignment: Text.AlignRight
                Layout.fillWidth: true
            }
            
            // Groundspeed display
            Label {
                text: "Groundspeed (m/s)"
                font.pixelSize: 12
                color: "white"
            }
            
            Label {
                text: groundSpeed.toFixed(2)
                font.pixelSize: 24
                font.bold: true
                color: "#ff9900"
                horizontalAlignment: Text.AlignRight
                Layout.fillWidth: true
            }
            
            // Distance to waypoint
            Label {
                text: "Dist to WP (m)"
                font.pixelSize: 12
                color: "white"
            }
            
            Label {
                text: distToWP.toFixed(2)
                font.pixelSize: 24
                font.bold: true
                color: "#ff00ff"
                horizontalAlignment: Text.AlignRight
                Layout.fillWidth: true
            }
            
            // Vertical speed
            Label {
                text: "Vertical Speed (m/s)"
                font.pixelSize: 12
                color: "white"
            }
            
            Label {
                text: verticalSpeed.toFixed(2)
                font.pixelSize: 24
                font.bold: true
                color: verticalSpeed >= 0 ? "#00ff00" : "#ff0000"
                horizontalAlignment: Text.AlignRight
                Layout.fillWidth: true
            }
            
            // Yaw/Heading
            Label {
                text: "Heading (deg)"
                font.pixelSize: 12
                color: "white"
            }
            
            Label {
                text: heading.toFixed(1)
                font.pixelSize: 24
                font.bold: true
                color: "#00ff00"
                horizontalAlignment: Text.AlignRight
                Layout.fillWidth: true
            }
            
            // Battery status
            Label {
                text: "Battery"
                font.pixelSize: 12
                color: "white"
            }
            
            RowLayout {
                Layout.fillWidth: true
                
                ProgressBar {
                    id: batteryBar
                    Layout.fillWidth: true
                    value: batteryPercent / 100
                    
                    // Custom styling
                    background: Rectangle {
                        implicitWidth: 200
                        implicitHeight: 10
                        color: "#333333"
                        border.color: "#666666"
                    }
                    
                    contentItem: Rectangle {
                        width: batteryBar.visualPosition * parent.width
                        height: parent.height
                        color: {
                            if (batteryPercent > 50) return "#00ff00";
                            if (batteryPercent > 25) return "#ffff00";
                            return "#ff0000";
                        }
                    }
                }
                
                Label {
                    text: batteryPercent + "%"
                    color: {
                        if (batteryPercent > 50) return "#00ff00";
                        if (batteryPercent > 25) return "#ffff00";
                        return "#ff0000";
                    }
                    font.bold: true
                    font.pixelSize: 14
                }
            }
            
            // Battery voltage
            Label {
                text: "Voltage (V)"
                font.pixelSize: 12
                color: "white"
            }
            
            Label {
                text: batteryVoltage.toFixed(1)
                font.pixelSize: 18
                font.bold: true
                color: batteryVoltage > 11.0 ? "#00ff00" : "#ff0000"
                horizontalAlignment: Text.AlignRight
                Layout.fillWidth: true
            }
            
            // Battery current
            Label {
                text: "Current (A)"
                font.pixelSize: 12
                color: "white"
            }
            
            Label {
                text: batteryCurrent.toFixed(2)
                font.pixelSize: 18
                font.bold: true
                color: batteryCurrent < 20 ? "#00ffff" : "#ff8800"
                horizontalAlignment: Text.AlignRight
                Layout.fillWidth: true
            }
            
            // Throttle percentage
            Label {
                text: "Throttle (%)"
                font.pixelSize: 12
                color: "white"
            }
            
            RowLayout {
                Layout.fillWidth: true
                
                ProgressBar {
                    id: throttleBar
                    Layout.fillWidth: true
                    value: throttlePercent / 100
                    
                    // Custom styling
                    background: Rectangle {
                        implicitWidth: 200
                        implicitHeight: 10
                        color: "#333333"
                        border.color: "#666666"
                    }
                    
                    contentItem: Rectangle {
                        width: throttleBar.visualPosition * parent.width
                        height: parent.height
                        color: "#00ff00"
                    }
                }
                
                Label {
                    text: throttlePercent + "%"
                    color: "#00ff00"
                    font.bold: true
                    font.pixelSize: 14
                }
            }
        }
    }
}
