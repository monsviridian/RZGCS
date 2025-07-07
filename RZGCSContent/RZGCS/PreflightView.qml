import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: root
    anchors.fill: parent
    
    // Simple preflight view with connection controls
    Rectangle {
        anchors.fill: parent
        color: "#1e1e1e"
        
        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 20
            spacing: 15
            
            Text {
                text: "Preflight Check & Connection"
                color: "white"
                font.pixelSize: 24
                font.bold: true
                Layout.fillWidth: true
                horizontalAlignment: Text.AlignHCenter
            }
            
            Rectangle {
                Layout.fillWidth: true
                height: 1
                color: "#555555"
            }
            
            // Connection Status
            GroupBox {
                title: "Verbindungsstatus"
                Layout.fillWidth: true
                
                GridLayout {
                    anchors.fill: parent
                    columns: 2
                    
                    Label {
                        text: "Status:"
                        color: "white"
                    }
                    
                    Label {
                        text: serialConnector && serialConnector.isConnected ? "Verbunden" : "Getrennt"
                        color: serialConnector && serialConnector.isConnected ? "#44FF44" : "#FF4444"
                        Layout.fillWidth: true
                    }
                    
                    Label {
                        text: "Port:"
                        color: "white"
                    }
                    
                    Label {
                        text: serialConnector ? serialConnector.selectedPort : "Nicht ausgewählt"
                        color: "white"
                        Layout.fillWidth: true
                    }
                }
            }
            
            // Connection Controls
            GroupBox {
                title: "Verbindung"
                Layout.fillWidth: true
                
                ColumnLayout {
                    anchors.fill: parent
                    spacing: 10
                    
                    RowLayout {
                        Layout.fillWidth: true
                        
                        Label {
                            text: "Port:"
                            color: "white"
                        }
                        
                        ComboBox {
                            id: portComboBox
                            model: serialConnector ? serialConnector.availablePorts : []
                            Layout.fillWidth: true
                            onCurrentTextChanged: if (serialConnector) serialConnector.setPort(currentText)
                        }
                        
                        Label {
                            text: "Baudrate:"
                            color: "white"
                        }
                        
                        ComboBox {
                            id: baudrateComboBox
                            model: [9600, 19200, 38400, 57600, 115200]
                            currentIndex: 4
                            Layout.preferredWidth: 100
                            onCurrentTextChanged: if (serialConnector) serialConnector.setBaudRate(parseInt(currentText))
                        }
                    }
                    
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 10
                        
                        Button {
                            text: serialConnector && serialConnector.isConnected ? "Trennen" : "Verbinden"
                            Layout.fillWidth: true
                            onClicked: {
                                if (serialConnector) {
                                    if (serialConnector.isConnected) {
                                        serialConnector.disconnect()
                                    } else {
                                        serialConnector.connect()
                                    }
                                }
                            }
                        }
                        
                        Button {
                            text: "Ports laden"
                            Layout.preferredWidth: 100
                            onClicked: if (serialConnector) serialConnector.load_ports()
                        }
                    }
                }
            }
            
            // Preflight Checklist
            GroupBox {
                title: "Preflight Checklist"
                Layout.fillWidth: true
                Layout.fillHeight: true
                
                ListView {
                    anchors.fill: parent
                    spacing: 5
                    model: ListModel {
                        ListElement { name: "Batterie-Status"; checked: false }
                        ListElement { name: "GPS-Signal"; checked: false }
                        ListElement { name: "Kompass kalibriert"; checked: false }
                        ListElement { name: "Gyro kalibriert"; checked: false }
                        ListElement { name: "RC-Verbindung"; checked: false }
                        ListElement { name: "Motoren getestet"; checked: false }
                        ListElement { name: "Flight Mode geprüft"; checked: false }
                        ListElement { name: "Notfall-Prozeduren überprüft"; checked: false }
                    }
                    
                    delegate: RowLayout {
                        width: parent.width
                        height: 40
                        spacing: 10
                        
                        CheckBox {
                            checked: model.checked
                            onCheckedChanged: model.checked = checked
                        }
                        
                        Text {
                            text: model.name
                            color: "white"
                            font.pixelSize: 16
                            Layout.fillWidth: true
                        }
                    }
                }
            }
        }
    }
} 