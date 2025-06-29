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
                        var baudrate = connectionString.text || "115200"
                        
                        // Port und Baudrate setzen
                        serialConnector.setPort(port)
                        serialConnector.setBaudRate(parseInt(baudrate))
                        
                        // Verbindung herstellen
                        serialConnector.connect()
                        
                        // Log-Eintrag
                        messageManager.addMessage("Verbinde mit " + port + " bei " + baudrate + " Baud", 1)
                    } else if (connectionType.currentText === "Simulator") {
                        // Direkt mit Simulator verbinden
                        serialConnector.setPort("tcp:127.0.0.1:5760")
                        serialConnector.connect()
                        messageManager.addMessage("Verbinde mit Simulator", 1)
                    } else {
                        // TCP/UDP Verbindung
                        var connString = connectionString.text
                        if (connString) {
                            if (connectionType.currentText === "UDP" && !connString.startsWith("udp:")) {
                                connString = "udp:" + connString
                            } else if (connectionType.currentText === "TCP" && !connString.startsWith("tcp:")) {
                                connString = "tcp:" + connString
                            }
                            serialConnector.setPort(connString)
                            serialConnector.connect()
                            messageManager.addMessage("Verbinde mit " + connString, 1)
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