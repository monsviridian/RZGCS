import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root
    color: "#303030"
    border.color: "#404040"
    border.width: 1
    
    // Properties
    property var backend
    property var mavlinkV2Backend
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 10
        
        // Port-Auswahl
        ComboBox {
            id: portComboBox
            Layout.fillWidth: true
            model: backend ? backend.availablePorts : []
            onCurrentTextChanged: {
                if (backend) {
                    backend.setPort(currentText)
                }
            }
            background: Rectangle {
                color: "black"
                border.color: "gray"
                border.width: 1
                radius: 4
            }
            contentItem: Text {
                text: portComboBox.displayText
                color: "white"
                verticalAlignment: Text.AlignVCenter
                horizontalAlignment: Text.AlignLeft
                leftPadding: 5
            }
        }
        
        // Baudrate-Auswahl
        ComboBox {
            id: baudComboBox
            Layout.fillWidth: true
            model: backend ? backend.availableBaudRates : []
            currentIndex: 4  // 115200
            onCurrentTextChanged: {
                if (backend) {
                    backend.setBaudRate(parseInt(currentText))
                }
            }
            background: Rectangle {
                color: "black"
                border.color: "gray"
                border.width: 1
                radius: 4
            }
            contentItem: Text {
                text: baudComboBox.displayText
                color: "white"
                verticalAlignment: Text.AlignVCenter
                horizontalAlignment: Text.AlignLeft
                leftPadding: 5
            }
        }
        
        // Verbindungstyp-Auswahl
        RowLayout {
            spacing: 10
            Text { text: "Verbindungstyp:"; color: "white" }
            ComboBox {
                id: connectionTypeComboBox
                model: ["Serial", "UDP", "TCP", "Simulator", "MAVLink 2"]
                currentIndex: 0
                Layout.preferredWidth: 150
                onCurrentIndexChanged: {
                    // Optional: Logik für Umschalten des Verbindungstyps
                }
            }
        }
        
        // Verbindungs-Button
        Button {
            id: connectButton
            Layout.fillWidth: true
            text: backend && backend.isConnected ? "Disconnect" : "Connect"
            onClicked: {
                if (connectionTypeComboBox.currentText === "MAVLink 2") {
                    if (mavlinkV2Backend) {
                        if (mavlinkV2Backend.isConnected) mavlinkV2Backend.disconnect_mavlink()
                        else mavlinkV2Backend.connect_mavlink()
                    }
                } else {
                    if (backend) {
                        if (backend.isConnected) {
                            backend.disconnect_from_drone()
                        } else {
                            backend.connect()
                        }
                    }
                }
            }
            background: Rectangle {
                color: "black"
                border.color: "gray"
                border.width: 1
                radius: 4
            }
            contentItem: Text {
                text: connectButton.text
                color: "white"
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
            }
        }
        
        // Refresh-Button
        Button {
            Layout.fillWidth: true
            text: "Refresh Ports"
            onClicked: {
                if (backend) {
                    backend.loadPorts()
                }
            }
            background: Rectangle {
                color: "black"
                border.color: "gray"
                border.width: 1
                radius: 4
            }
            contentItem: Text {
                text: parent.text
                color: "white"
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
            }
        }
        
        // Status-Anzeige
        Label {
            Layout.fillWidth: true
            text: backend && backend.isConnected ? "Status: Connected" : "Status: Disconnected"
            color: backend && backend.isConnected ? "green" : "red"
            horizontalAlignment: Text.AlignHCenter
        }
    }
    
    // Backend-Signale
    Connections {
        target: backend
        
        function onConnectionStatusChanged(status) {
            connectButton.text = status === "CONNECTED" ? "Disconnect" : "Connect"
        }
        
        function onAvailablePortsChanged(ports) {
            portComboBox.model = ports
        }
        
        function onAvailableBaudRatesChanged(baudRates) {
            baudComboBox.model = baudRates
        }
    }
}
