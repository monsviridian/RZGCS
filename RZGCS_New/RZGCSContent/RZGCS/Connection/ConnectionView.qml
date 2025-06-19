import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root
    color: "#2C2C2C"
    radius: 5
    border.color: "gray"
    border.width: 1

    property var backend: null
    property bool isConnected: false

    RowLayout {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 10

        // Verbindungsstatus
        Rectangle {
            Layout.preferredWidth: 20
            Layout.preferredHeight: 20
            radius: 10
            color: root.isConnected ? "#00FF00" : "#FF0000"
        }

        // Verbindungsbutton
        Button {
            text: root.isConnected ? "Disconnect" : "Connect"
            onClicked: {
                if (root.isConnected) {
                    backend.disconnect()
                } else {
                    backend.connect()
                }
            }
        }
    }

    Connections {
        target: backend
        function onStateChanged(state) {
            root.isConnected = state.connected
        }
    }
} 