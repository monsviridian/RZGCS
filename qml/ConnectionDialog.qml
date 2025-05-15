import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Dialog {
    id: connectionDialog
    title: "Connection Settings"
    width: 400
    height: 500
    modal: true
    standardButtons: Dialog.Ok | Dialog.Cancel

    signal connectRequested(var connectionData)

    ColumnLayout {
        anchors.fill: parent
        spacing: 20

        // Connection type selection
        GroupBox {
            title: "Connection Type"
            Layout.fillWidth: true

            ColumnLayout {
                anchors.fill: parent

                RadioButton {
                    id: mavsdkRadio
                    text: "MAVSDK"
                    checked: true
                    onCheckedChanged: {
                        if (checked) {
                            mavlinkSettings.visible = false
                            mavsdkSettings.visible = true
                        }
                    }
                }
                RadioButton {
                    id: mavlinkRadio
                    text: "MAVLink"
                    onCheckedChanged: {
                        if (checked) {
                            mavlinkSettings.visible = true
                            mavsdkSettings.visible = false
                        }
                    }
                }

                // MAVSDK connection type
                ComboBox {
                    id: mavsdkConnectionType
                    Layout.fillWidth: true
                    model: ["Serial", "UDP"]
                    visible: mavsdkRadio.checked
                }

                // Serial settings
                GridLayout {
                    columns: 2
                    Layout.fillWidth: true
                    visible: mavsdkConnectionType.currentIndex === 0

                    Label { text: "Port:" }
                    ComboBox {
                        id: mavsdkPortComboBox
                        Layout.fillWidth: true
                        model: ["COM1", "COM2", "COM3", "COM4", "COM5", "/dev/ttyACM0", "/dev/ttyUSB0"]
                        editable: true
                    }

                    Label { text: "Baudrate:" }
                    ComboBox {
                        id: mavsdkBaudrateComboBox
                        Layout.fillWidth: true
                        model: [9600, 57600, 115200]
                        currentIndex: 1  // 57600 as default
                    }
                }

                // UDP settings
                TextField {
                    id: udpConnectionString
                    Layout.fillWidth: true
                    visible: mavsdkConnectionType.currentIndex === 1
                    placeholderText: "udp://:14540"
                    text: "udp://:14540"
                    Label {
                        text: "UDP Connection URL"
                        color: "#666"
                        font.pointSize: 8
                        anchors.bottom: parent.top
                        anchors.left: parent.left
                    }
                }

                Label {
                    text: mavsdkConnectionType.currentIndex === 0 ?
                        "Serial connection for real hardware" :
                        "UDP connection for SITL simulation"
                    color: "#666"
                    font.pointSize: 8
                    Layout.fillWidth: true
                    wrapMode: Text.WordWrap
                }
            }
        }

        // MAVLink settings
        GroupBox {
            id: mavlinkSettings
            title: "MAVLink Settings"
            Layout.fillWidth: true
            visible: mavlinkRadio.checked

            GridLayout {
                columns: 2
                Layout.fillWidth: true

                Label { text: "Port:" }
                ComboBox {
                    id: portComboBox
                    Layout.fillWidth: true
                    model: ["COM1", "COM2", "COM3", "COM4", "COM5", "/dev/ttyACM0", "/dev/ttyUSB0"]
                    editable: true
                }

                Label { text: "Baudrate:" }
                ComboBox {
                    id: baudrateComboBox
                    Layout.fillWidth: true
                    model: [9600, 57600, 115200]
                    currentIndex: 1  // 57600 as default
                }
            }
        }

        // Status message
        Label {
            id: statusLabel
            Layout.fillWidth: true
            wrapMode: Text.WordWrap
            color: "#666"
            text: "Select the desired connection type and corresponding settings."
        }
    }

    onAccepted: {
        let connectionData = {
            connection_type: mavsdkRadio.checked ? "mavsdk" : "mavlink",
            autopilot: "ardupilot"
        }

        if (mavsdkRadio.checked) {
            if (mavsdkConnectionType.currentIndex === 0) {
                // Serial port for MAVSDK
                connectionData.connection_string = "serial://" + mavsdkPortComboBox.currentText + ":" + mavsdkBaudrateComboBox.currentText
            } else {
                // UDP for MAVSDK
                connectionData.connection_string = udpConnectionString.text
            }
        } else {
            // Classic MAVLink
            connectionData.port = portComboBox.currentText
            connectionData.baudrate = parseInt(baudrateComboBox.currentText)
        }

        connectRequested(connectionData)
    }
} 