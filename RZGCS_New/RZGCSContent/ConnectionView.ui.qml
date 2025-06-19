import QtQuick
import QtQuick.Controls 6.8
import QtQuick.Layouts

Item {
    id: root
    anchors.fill: parent

    Rectangle {
        anchors.fill: parent
        color: "black"
        z: -1
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 15

        // Connection Type and Port Selection
        GridLayout {
            columns: 2
            columnSpacing: 10
            rowSpacing: 10
            Layout.fillWidth: true

            Label { 
                text: "Connection Type:" 
                color: "white"
            }
            ComboBox {
                id: connectionType
                model: ["Serial", "UDP", "TCP", "Simulator"]
                Layout.preferredWidth: 200
                onCurrentTextChanged: {
                    connectionString.visible = currentText !== "Simulator"
                    portCombo.visible = currentText === "Serial"
                    if (currentText === "Serial") {
                        serialConnector.refreshPorts()
                    }
                }
            }

            Label { 
                text: "Port:" 
                color: "white"
                visible: connectionType.currentText === "Serial"
            }
            ComboBox {
                id: portCombo
                model: serialConnector.availablePorts || []
                Layout.preferredWidth: 200
                visible: connectionType.currentText === "Serial"
            }

            Label { 
                text: connectionType.currentText === "Serial" ? "Baudrate:" : "Host:Port:" 
                color: "white"
                visible: connectionType.currentText !== "Simulator"
            }
            TextField {
                id: connectionString
                placeholderText: connectionType.currentText === "Serial" ? "115200" : "127.0.0.1:14550"
                Layout.preferredWidth: 200
                visible: connectionType.currentText !== "Simulator"
            }
        }


        // Connection Buttons
        RowLayout {
            spacing: 10
            Layout.alignment: Qt.AlignHCenter

            Button {
                id: refreshButton
                text: "Refresh Ports"
                onClicked: {
                    if (connectionType.currentText === "Serial") {
                        serialConnector.refreshPorts()
                    }
                }
                visible: connectionType.currentText === "Serial"
            }

            Button {
                text: "Connect"
                Layout.preferredWidth: 100
                enabled: connectionType.currentText === "Serial" ? portCombo.currentText !== "" : connectionString.text !== ""
                onClicked: {
                    if (connectionType.currentText === "Serial") {
                        var port = portCombo.currentText
                        if (port) {
                            serialConnector.establish_serial_connection(port)
                        }
                    } else {
                        var connString = connectionString.text
                        if (connString) {
                            serialConnector.establish_serial_connection(connString)
                        }
                    }
                }
            }

            Button {
                text: "Disconnect"
                onClicked: serialConnector.disconnect()
                enabled: serialConnector.connected
            }
        }

        // Connection Status
        Text {
            text: serialConnector.connectionStatus
            color: serialConnector.connected ? "#00ff00" : "#ff0000"
            font.bold: true
            Layout.alignment: Qt.AlignHCenter
        }

        // Status Messages
        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            TextArea {
                id: statusText
                readOnly: true
                wrapMode: Text.Wrap
                text: serialConnector.statusMessage
                color: "white"
                background: Rectangle {
                    color: "#1a1a1a"
                    radius: 5
                }
                padding: 5
            }
        }
    }

    
    // Initial port refresh
    Component.onCompleted: {
        if (connectionType.currentText === "Serial") {
            serialConnector.refreshPorts()
        }
    }
}