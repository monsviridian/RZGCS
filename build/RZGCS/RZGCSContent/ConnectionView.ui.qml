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
        spacing: 8

        RowLayout {
            spacing: 8
            ComboBox {
                id: connectionType
                model: ["Simulator", "Serial", "UDP", "TCP"]
                Layout.preferredWidth: 200
            }
            TextField {
                id: connectionString
                placeholderText: "Connection string (e.g. COM3, 127.0.0.1:14550)"
                Layout.preferredWidth: 400
                visible: connectionType.currentText !== "Simulator"
            }
            Button {
                text: "Connect"
                onClicked: {
                    let connString = connectionType.currentText === "Simulator" ? 
                        "simulator://" : 
                        connectionString.text
                    serialConnector.connect(connString)
                }
            }
            Button {
                text: "Disconnect"
                onClicked: serialConnector.disconnect()
            }
        }

        Text {
            text: "Connection Status: " + (serialConnector.connected ? "Connected" : "Disconnected")
            color: serialConnector.connected ? "green" : "red"
        }
    }
} 