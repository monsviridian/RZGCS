import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Window 2.15

Rectangle {
    id: root
    color: "#1e1e1e"
    border.color: "#404040"
    border.width: 1

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 16
        spacing: 16

        // Header mit Titel und Status
        RowLayout {
            Layout.fillWidth: true
            spacing: 20

            Text {
                text: "Sensor Dashboard"
                color: "#e0e0e0"
                font.pixelSize: 24
                font.bold: true
            }

            Item { Layout.fillWidth: true }

            // Status-Anzeigen
            Rectangle {
                width: 120
                height: 30
                radius: 15
                color: serialConnector && serialConnector.isConnected ? "#4CAF50" : "#f44336"
                
                Text {
                    anchors.centerIn: parent
                    text: serialConnector && serialConnector.isConnected ? "Connected" : "Disconnected"
                    color: "white"
                    font.pixelSize: 12
                    font.bold: true
                }
            }

            Text {
                text: "GPS: " + (sensorViewModel ? sensorViewModel.satellites : "0") + " Sat"
                color: "#aaa"
                font.pixelSize: 14
            }

            Text {
                text: "Last Update: " + (sensorViewModel && sensorViewModel.last_update_seconds ? sensorViewModel.last_update_seconds.toFixed(1) : "0.0") + "s ago"
                color: "#aaa"
                font.pixelSize: 14
            }
        }

        // Hauptbereich mit Gauges und Sensor-Daten
        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 20

            // Linke Seite: Gauges
            ColumnLayout {
                spacing: 16
                Layout.preferredWidth: 300

                // Höhe Gauge
                Rectangle {
                    Layout.fillWidth: true
                    height: 120
                    radius: 8
                    color: "#2c3e50"
                    border.color: "#34495e"
                    border.width: 1

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 12

                        Text {
                            text: "Höhe"
                            color: "#bdc3c7"
                            font.pixelSize: 14
                            Layout.alignment: Qt.AlignHCenter
                        }

                        Text {
                            text: (typeof sensorViewModel.alt === "number" && sensorViewModel.alt !== null)
                                ? sensorViewModel.alt.toFixed(1)
                                : "—" + " m"
                            color: "#3498db"
                            font.pixelSize: 28
                            font.bold: true
                            Layout.alignment: Qt.AlignHCenter
                        }

                        ProgressBar {
                            Layout.fillWidth: true
                            from: 0
                            to: 1000
                            value: sensorViewModel ? sensorViewModel.alt : 0
                            background: Rectangle {
                                color: "#34495e"
                                radius: 2
                            }
                            contentItem: Rectangle {
                                color: "#3498db"
                                radius: 2
                            }
                        }
                    }
                }

                // Geschwindigkeit Gauge
                Rectangle {
                    Layout.fillWidth: true
                    height: 120
                    radius: 8
                    color: "#2c3e50"
                    border.color: "#34495e"
                    border.width: 1

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 12

                        Text {
                            text: "Geschwindigkeit"
                            color: "#bdc3c7"
                            font.pixelSize: 14
                            Layout.alignment: Qt.AlignHCenter
                        }

                        Text {
                            text: (typeof sensorViewModel.groundspeed === "number" && sensorViewModel.groundspeed !== null)
                                ? sensorViewModel.groundspeed.toFixed(1)
                                : "—" + " m/s"
                            color: "#e74c3c"
                            font.pixelSize: 28
                            font.bold: true
                            Layout.alignment: Qt.AlignHCenter
                        }

                        ProgressBar {
                            Layout.fillWidth: true
                            from: 0
                            to: 50
                            value: sensorViewModel ? sensorViewModel.groundspeed : 0
                            background: Rectangle {
                                color: "#34495e"
                                radius: 2
                            }
                            contentItem: Rectangle {
                                color: "#e74c3c"
                                radius: 2
                            }
                        }
                    }
                }

                // Batterie Gauge
                Rectangle {
                    Layout.fillWidth: true
                    height: 120
                    radius: 8
                    color: "#2c3e50"
                    border.color: "#34495e"
                    border.width: 1

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 12

                        Text {
                            text: "Batterie"
                            color: "#bdc3c7"
                            font.pixelSize: 14
                            Layout.alignment: Qt.AlignHCenter
                        }

                        Text {
                            text: (typeof sensorViewModel.voltage === "number" && sensorViewModel.voltage !== null)
                                ? sensorViewModel.voltage.toFixed(2)
                                : "—" + " V"
                            color: "#f39c12"
                            font.pixelSize: 28
                            font.bold: true
                            Layout.alignment: Qt.AlignHCenter
                        }

                        ProgressBar {
                            Layout.fillWidth: true
                            from: 10
                            to: 16.8
                            value: sensorViewModel ? sensorViewModel.voltage : 0
                            background: Rectangle {
                                color: "#34495e"
                                radius: 2
                            }
                            contentItem: Rectangle {
                                color: "#f39c12"
                                radius: 2
                            }
                        }
                    }
                }
            }

            // Rechte Seite: Sensor-Details
            GridLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                columns: 2
                rowSpacing: 12
                columnSpacing: 16

                // GPS Gruppe
                GroupBox {
                    title: "GPS"
                    Layout.fillWidth: true
                    Layout.preferredHeight: 150

                    background: Rectangle {
                        color: "#2c3e50"
                        border.color: "#34495e"
                        border.width: 1
                        radius: 4
                    }

                    label: Text {
                        text: parent.title
                        color: "#3498db"
                        font.pixelSize: 14
                        font.bold: true
                    }

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 8
                        spacing: 4

                        RowLayout {
                            Text { text: "Latitude:"; color: "#bdc3c7"; font.pixelSize: 12 }
                            Text { 
                                text: typeof sensorViewModel.lat === "number"
                                    ? sensorViewModel.lat.toFixed(7)
                                    : "—"
                                color: "#ecf0f1"
                                font.pixelSize: 12
                                font.family: "Courier"
                            }
                        }

                        RowLayout {
                            Text { text: "Longitude:"; color: "#bdc3c7"; font.pixelSize: 12 }
                            Text { 
                                text: typeof sensorViewModel.lon === "number"
                                    ? sensorViewModel.lon.toFixed(7)
                                    : "—"
                                color: "#ecf0f1"
                                font.pixelSize: 12
                                font.family: "Courier"
                            }
                        }

                        RowLayout {
                            Text { text: "Altitude:"; color: "#bdc3c7"; font.pixelSize: 12 }
                            Text { 
                                text: typeof sensorViewModel.alt === "number"
                                    ? sensorViewModel.alt.toFixed(1)
                                    : "—" + " m"
                                color: "#ecf0f1"
                                font.pixelSize: 12
                            }
                        }

                        RowLayout {
                            Text { text: "Satellites:"; color: "#bdc3c7"; font.pixelSize: 12 }
                            Text { 
                                text: typeof sensorViewModel.satellites === "number"
                                    ? sensorViewModel.satellites.toFixed(0)
                                    : "—"
                                color: "#ecf0f1"
                                font.pixelSize: 12
                            }
                        }

                        RowLayout {
                            Text { text: "HDOP:"; color: "#bdc3c7"; font.pixelSize: 12 }
                            Text { 
                                text: typeof sensorViewModel.hdop === "number"
                                    ? sensorViewModel.hdop.toFixed(2)
                                    : "—"
                                color: "#ecf0f1"
                                font.pixelSize: 12
                            }
                        }

                        RowLayout {
                            Text { text: "VDOP:"; color: "#bdc3c7"; font.pixelSize: 12 }
                            Text { 
                                text: typeof sensorViewModel.vdop === "number"
                                    ? sensorViewModel.vdop.toFixed(2)
                                    : "—"
                                color: "#ecf0f1"
                                font.pixelSize: 12
                            }
                        }
                    }
                }

                // Attitude Gruppe
                GroupBox {
                    title: "Attitude"
                    Layout.fillWidth: true
                    Layout.preferredHeight: 150

                    background: Rectangle {
                        color: "#2c3e50"
                        border.color: "#34495e"
                        border.width: 1
                        radius: 4
                    }

                    label: Text {
                        text: parent.title
                        color: "#e74c3c"
                        font.pixelSize: 14
                        font.bold: true
                    }

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 8
                        spacing: 4

                        RowLayout {
                            Text { text: "Roll:"; color: "#bdc3c7"; font.pixelSize: 12 }
                            Text { 
                                text: typeof sensorViewModel.roll === "number"
                                    ? sensorViewModel.roll.toFixed(1)
                                    : "—" + "°"
                                color: "#ecf0f1"
                                font.pixelSize: 12
                            }
                        }

                        RowLayout {
                            Text { text: "Pitch:"; color: "#bdc3c7"; font.pixelSize: 12 }
                            Text { 
                                text: typeof sensorViewModel.pitch === "number"
                                    ? sensorViewModel.pitch.toFixed(1)
                                    : "—" + "°"
                                color: "#ecf0f1"
                                font.pixelSize: 12
                            }
                        }

                        RowLayout {
                            Text { text: "Yaw:"; color: "#bdc3c7"; font.pixelSize: 12 }
                            Text { 
                                text: typeof sensorViewModel.yaw === "number"
                                    ? sensorViewModel.yaw.toFixed(1)
                                    : "—" + "°"
                                color: "#ecf0f1"
                                font.pixelSize: 12
                            }
                        }

                        RowLayout {
                            Text { text: "Heading:"; color: "#bdc3c7"; font.pixelSize: 12 }
                            Text { 
                                text: typeof sensorViewModel.heading === "number"
                                    ? sensorViewModel.heading.toFixed(1)
                                    : "—" + "°"
                                color: "#ecf0f1"
                                font.pixelSize: 12
                            }
                        }
                    }
                }

                // Barometer Gruppe
                GroupBox {
                    title: "Barometer"
                    Layout.fillWidth: true
                    Layout.preferredHeight: 120

                    background: Rectangle {
                        color: "#2c3e50"
                        border.color: "#34495e"
                        border.width: 1
                        radius: 4
                    }

                    label: Text {
                        text: parent.title
                        color: "#9b59b6"
                        font.pixelSize: 14
                        font.bold: true
                    }

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 8
                        spacing: 4

                        RowLayout {
                            Text { text: "Pressure:"; color: "#bdc3c7"; font.pixelSize: 12 }
                            Text { 
                                text: typeof sensorViewModel.pressure === "number"
                                    ? sensorViewModel.pressure.toFixed(2)
                                    : "—" + " hPa"
                                color: "#ecf0f1"
                                font.pixelSize: 12
                            }
                        }

                        RowLayout {
                            Text { text: "Temperature:"; color: "#bdc3c7"; font.pixelSize: 12 }
                            Text { 
                                text: typeof sensorViewModel.temperature === "number"
                                    ? sensorViewModel.temperature.toFixed(1)
                                    : "—" + " °C"
                                color: "#ecf0f1"
                                font.pixelSize: 12
                            }
                        }

                        RowLayout {
                            Text { text: "Humidity:"; color: "#bdc3c7"; font.pixelSize: 12 }
                            Text { 
                                text: typeof sensorViewModel.humidity === "number"
                                    ? sensorViewModel.humidity.toFixed(1)
                                    : "—" + " %"
                                color: "#ecf0f1"
                                font.pixelSize: 12
                            }
                        }
                    }
                }

                // Batterie Gruppe
                GroupBox {
                    title: "Batterie"
                    Layout.fillWidth: true
                    Layout.preferredHeight: 120

                    background: Rectangle {
                        color: "#2c3e50"
                        border.color: "#34495e"
                        border.width: 1
                        radius: 4
                    }

                    label: Text {
                        text: parent.title
                        color: "#f39c12"
                        font.pixelSize: 14
                        font.bold: true
                    }

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 8
                        spacing: 4

                        RowLayout {
                            Text { text: "Voltage:"; color: "#bdc3c7"; font.pixelSize: 12 }
                            Text { 
                                text: typeof sensorViewModel.voltage === "number"
                                    ? sensorViewModel.voltage.toFixed(2)
                                    : "—" + " V"
                                color: "#ecf0f1"
                                font.pixelSize: 12
                            }
                        }

                        RowLayout {
                            Text { text: "Current:"; color: "#bdc3c7"; font.pixelSize: 12 }
                            Text { 
                                text: typeof sensorViewModel.current === "number"
                                    ? sensorViewModel.current.toFixed(2)
                                    : "—" + " A"
                                color: "#ecf0f1"
                                font.pixelSize: 12
                            }
                        }

                        RowLayout {
                            Text { text: "Percentage:"; color: "#bdc3c7"; font.pixelSize: 12 }
                            Text { 
                                text: typeof sensorViewModel.battery_percent === "number"
                                    ? sensorViewModel.battery_percent.toFixed(1)
                                    : "—" + "%"
                                color: "#ecf0f1"
                                font.pixelSize: 12
                            }
                        }

                        RowLayout {
                            Text { text: "Remaining:"; color: "#bdc3c7"; font.pixelSize: 12 }
                            Text { 
                                text: typeof sensorViewModel.battery_remaining === "number"
                                    ? sensorViewModel.battery_remaining.toFixed(1)
                                    : "—" + "%"
                                color: "#ecf0f1"
                                font.pixelSize: 12
                            }
                        }
                    }
                }

                // Speed Gruppe
                GroupBox {
                    title: "Speed"
                    Layout.fillWidth: true
                    Layout.preferredHeight: 120

                    background: Rectangle {
                        color: "#2c3e50"
                        border.color: "#34495e"
                        border.width: 1
                        radius: 4
                    }

                    label: Text {
                        text: parent.title
                        color: "#1abc9c"
                        font.pixelSize: 14
                        font.bold: true
                    }

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 8
                        spacing: 4

                        RowLayout {
                            Text { text: "Ground Speed:"; color: "#bdc3c7"; font.pixelSize: 12 }
                            Text { 
                                text: typeof sensorViewModel.groundspeed === "number"
                                    ? sensorViewModel.groundspeed.toFixed(1)
                                    : "—" + " m/s"
                                color: "#ecf0f1"
                                font.pixelSize: 12
                            }
                        }

                        RowLayout {
                            Text { text: "Air Speed:"; color: "#bdc3c7"; font.pixelSize: 12 }
                            Text { 
                                text: typeof sensorViewModel.airspeed === "number"
                                    ? sensorViewModel.airspeed.toFixed(1)
                                    : "—" + " m/s"
                                color: "#ecf0f1"
                                font.pixelSize: 12
                            }
                        }

                        RowLayout {
                            Text { text: "Vertical Speed:"; color: "#bdc3c7"; font.pixelSize: 12 }
                            Text { 
                                text: typeof sensorViewModel.vertical_speed === "number"
                                    ? sensorViewModel.vertical_speed.toFixed(1)
                                    : "—" + " m/s"
                                color: "#ecf0f1"
                                font.pixelSize: 12
                            }
                        }

                        RowLayout {
                            Text { text: "Throttle:"; color: "#bdc3c7"; font.pixelSize: 12 }
                            Text { 
                                text: typeof sensorViewModel.throttle === "number"
                                    ? sensorViewModel.throttle.toFixed(1)
                                    : "—" + "%"
                                color: "#ecf0f1"
                                font.pixelSize: 12
                            }
                        }
                    }
                }

                // System Status Gruppe
                GroupBox {
                    title: "System Status"
                    Layout.fillWidth: true
                    Layout.preferredHeight: 120

                    background: Rectangle {
                        color: "#2c3e50"
                        border.color: "#34495e"
                        border.width: 1
                        radius: 4
                    }

                    label: Text {
                        text: parent.title
                        color: "#95a5a6"
                        font.pixelSize: 14
                        font.bold: true
                    }

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 8
                        spacing: 4

                        RowLayout {
                            Text { text: "Connection:"; color: "#bdc3c7"; font.pixelSize: 12 }
                            Text { 
                                text: serialConnector && serialConnector.isConnected ? "Connected" : "Disconnected"
                                color: serialConnector && serialConnector.isConnected ? "#27ae60" : "#e74c3c"
                                font.pixelSize: 12
                                font.bold: true
                            }
                        }

                        RowLayout {
                            Text { text: "GPS Fix:"; color: "#bdc3c7"; font.pixelSize: 12 }
                            Text { 
                                text: typeof sensorViewModel.gps_fix_type === "number"
                                    ? sensorViewModel.gps_fix_type > 0 ? "Yes" : "No"
                                    : "Unknown"
                                color: typeof sensorViewModel.gps_fix_type === "number" && sensorViewModel.gps_fix_type > 0 ? "#27ae60" : "#e74c3c"
                                font.pixelSize: 12
                                font.bold: true
                            }
                        }

                        RowLayout {
                            Text { text: "Last Update:"; color: "#bdc3c7"; font.pixelSize: 12 }
                            Text { 
                                text: typeof sensorViewModel.last_update_seconds === "number"
                                    ? sensorViewModel.last_update_seconds.toFixed(1)
                                    : "—" + "s ago"
                                color: "#ecf0f1"
                                font.pixelSize: 12
                            }
                        }
                    }
                }
            }
        }

        // Footer mit Update-Info
        RowLayout {
            Layout.fillWidth: true
            spacing: 20

            Text {
                text: "Data Source: " + (serialConnector && serialConnector.isConnected ? "Vehicle" : "Simulation")
                color: "#7f8c8d"
                font.pixelSize: 12
            }

            Item { Layout.fillWidth: true }

            Text {
                text: "Update Rate: " + (sensorViewModel ? (1.0 / Math.max(sensorViewModel.last_update_seconds, 0.1)).toFixed(1) : "0.0") + " Hz"
                color: "#7f8c8d"
                font.pixelSize: 12
            }
        }
    }
} 