import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: serialView
    color: "#1d1d1d"

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 20

        // Connection settings
        GroupBox {
            title: "Connection Settings"
            Layout.fillWidth: true

            GridLayout {
                columns: 2
                anchors.fill: parent

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

        // Connection status
        GroupBox {
            title: "Connection Status"
            Layout.fillWidth: true

            ColumnLayout {
                anchors.fill: parent
                spacing: 10

                Label {
                    text: "Status: " + (serialConnector.connected ? "Connected" : "Disconnected")
                    color: serialConnector.connected ? "#4CAF50" : "#F44336"
                }

                Label {
                    text: "Port: " + (serialConnector.port || "None")
                    color: "#BDBDBD"
                }

                Label {
                    text: "Baudrate: " + (serialConnector.baudrate || "None")
                    color: "#BDBDBD"
                }
            }
        }

        // Connection buttons
        RowLayout {
            Layout.fillWidth: true
            spacing: 10

            Button {
                text: "Connect"
                enabled: !serialConnector.connected
                onClicked: {
                    serialConnector.connect_to_serial(portComboBox.currentText, parseInt(baudrateComboBox.currentText))
                }
            }

            Button {
                text: "Disconnect"
                enabled: serialConnector.connected
                onClicked: {
                    serialConnector.disconnect()
                }
            }

            Button {
                text: "Refresh Ports"
                onClicked: {
                    serialConnector.load_ports()
                }
            }
        }

        // Log messages
        GroupBox {
            title: "Log Messages"
            Layout.fillWidth: true
            Layout.fillHeight: true

            ListView {
                id: logListView
                anchors.fill: parent
                model: serialConnector.logs
                delegate: Text {
                    text: modelData
                    color: "#BDBDBD"
                    wrapMode: Text.WordWrap
                }
                ScrollBar.vertical: ScrollBar {}
            }
        }
    }
} 