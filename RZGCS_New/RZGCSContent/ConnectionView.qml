import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import RZGCS.Connection 1.0

Item {
    id: root
    
    // Properties
    property var viewModel: connectionViewModel

    // Layout
    ColumnLayout {
        anchors.fill: parent
        spacing: 10
        
        // Status
        GroupBox {
            title: "Verbindungsstatus"
            Layout.fillWidth: true
            
            ColumnLayout {
                anchors.fill: parent
                
                Label {
                    text: "Status: " + (viewModel ? viewModel.status : "Unbekannt")
                    Layout.fillWidth: true
                    color: "white"
                }
                
                Label {
                    text: "Typ: " + (viewModel ? viewModel.type : "Unbekannt")
                    Layout.fillWidth: true
                    color: "white"
                }
                
                Label {
                    text: "Verbunden: " + (viewModel && viewModel.state && viewModel.state.is_connected ? "Ja" : "Nein")
                    Layout.fillWidth: true
                    color: "white"
                }
                
                Label {
                    text: "Fehler: " + (viewModel && viewModel.state && viewModel.state.is_error ? "Ja" : "Nein")
                    Layout.fillWidth: true
                    color: "white"
                }
                
                Label {
                    text: "Fehlermeldung: " + (viewModel && viewModel.state && viewModel.state.error_message ? viewModel.state.error_message : "Keine")
                    Layout.fillWidth: true
                    color: "white"
                }
            }
        }
        
        // Parameter
        GroupBox {
            title: "Verbindungsparameter"
            Layout.fillWidth: true
            
            GridLayout {
                anchors.fill: parent
                columns: 2
                
                Label {
                    text: "Port:"
                    color: "white"
                }
                
                ComboBox {
                    id: portComboBox
                    model: serialConnector ? serialConnector.availablePorts : []
                    Layout.fillWidth: true
                    onCurrentTextChanged: if (serialConnector) serialConnector.setPort(currentText)
                    
                    background: Rectangle {
                        color: "#222222"
                        border.color: "gray"
                        border.width: 1
                        radius: 4
                    }
                    
                    contentItem: Text {
                        text: portComboBox.displayText
                        color: "white"
                        verticalAlignment: Text.AlignVCenter
                    }
                    
                    // Für bessere Darstellung des Dropdown-Menüs
                    popup.background: Rectangle {
                        color: "#222222"
                        border.color: "gray"
                    }
                    
                    // Delegat für jedes Element im Dropdown
                    delegate: ItemDelegate {
                        width: portComboBox.width
                        contentItem: Text {
                            text: modelData
                            color: "white"
                        }
                        background: Rectangle {
                            color: highlighted ? "#444444" : "#222222"
                        }
                        highlighted: portComboBox.highlightedIndex === index
                    }
                }
                
                Label {
                    text: "Baudrate:"
                    color: "white"
                }
                
                ComboBox {
                    id: baudrateComboBox
                    model: [9600, 19200, 38400, 57600, 115200]
                    currentIndex: 4  // 115200 vorausgewählt
                    Layout.fillWidth: true
                    onCurrentTextChanged: if (serialConnector) serialConnector.setBaudRate(parseInt(currentText))
                    
                    background: Rectangle {
                        color: "#222222"
                        border.color: "gray"
                        border.width: 1
                        radius: 4
                    }
                    
                    contentItem: Text {
                        text: baudrateComboBox.displayText
                        color: "white"
                        verticalAlignment: Text.AlignVCenter
                    }
                    
                    popup.background: Rectangle {
                        color: "#222222"
                        border.color: "gray"
                    }
                    
                    delegate: ItemDelegate {
                        width: baudrateComboBox.width
                        contentItem: Text {
                            text: modelData
                            color: "white"
                        }
                        background: Rectangle {
                            color: highlighted ? "#444444" : "#222222"
                        }
                        highlighted: baudrateComboBox.highlightedIndex === index
                    }
                }
                
                Label {
                    text: "Verbindungstyp:"
                    color: "white"
                }
                
                ComboBox {
                    id: connectionTypeComboBox
                    model: ["Serial", "UDP", "TCP", "Simulator"]
                    currentIndex: 3  // Simulator vorausgewählt
                    Layout.fillWidth: true
                    onCurrentTextChanged: {
                        if (currentText === "Simulator" && serialConnector) {
                            serialConnector.setPort("Simulator")
                        }
                    }
                    
                    background: Rectangle {
                        color: "#222222"
                        border.color: "gray"
                        border.width: 1
                        radius: 4
                    }
                    
                    contentItem: Text {
                        text: connectionTypeComboBox.displayText
                        color: "white"
                        verticalAlignment: Text.AlignVCenter
                    }
                    
                    popup.background: Rectangle {
                        color: "#222222"
                        border.color: "gray"
                    }
                    
                    delegate: ItemDelegate {
                        width: connectionTypeComboBox.width
                        contentItem: Text {
                            text: modelData
                            color: "white"
                        }
                        background: Rectangle {
                            color: highlighted ? "#444444" : "#222222"
                        }
                        highlighted: connectionTypeComboBox.highlightedIndex === index
                    }
                }
            }
        }
        
        // Connection actions
        RowLayout {
            Layout.fillWidth: true
            spacing: 10
            
            Button {
                id: connectButton
                text: serialConnector && serialConnector.connected ? "Trennen" : "Verbinden"
                Layout.fillWidth: true
                
                onClicked: {
                    if (serialConnector) {
                        if (serialConnector.connected) {
                            serialConnector.disconnect();
                        } else {
                            serialConnector.connect(portComboBox.currentText);
                        }
                    }
                }
                
                background: Rectangle {
                    color: connectButton.pressed ? "#005500" : (serialConnector && serialConnector.connected ? "#FF4444" : "#44FF44")
                    radius: 4
                }
                
                contentItem: Text {
                    text: connectButton.text
                    color: "white"
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
            }
            
            Button {
                text: "Ports neu laden"
                Layout.fillWidth: true
                
                onClicked: {
                    if (serialConnector) {
                        serialConnector.load_ports();
                    }
                }
                
                background: Rectangle {
                    color: parent.pressed ? "#003366" : "#0066CC"
                    radius: 4
                }
                
                contentItem: Text {
                    text: parent.text
                    color: "white"
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
            }
        }
        
        // Statistics
        GroupBox {
            title: "Verbindungsstatistik"
            Layout.fillWidth: true
            
            GridLayout {
                anchors.fill: parent
                columns: 2
                
                Label {
                    text: "Gesendete Pakete:"
                    color: "white"
                }
                
                Label {
                    text: viewModel && viewModel.statistics ? viewModel.statistics.packets_sent : "0"
                    Layout.fillWidth: true
                    color: "white"
                }
                
                Label {
                    text: "Empfangene Pakete:"
                    color: "white"
                }
                
                Label {
                    text: viewModel && viewModel.statistics ? viewModel.statistics.packets_received : "0"
                    Layout.fillWidth: true
                    color: "white"
                }
                
                Label {
                    text: "Fehlgeschlagene Pakete:"
                    color: "white"
                }
                
                Label {
                    text: viewModel && viewModel.statistics ? viewModel.statistics.packets_failed : "0"
                    Layout.fillWidth: true
                    color: "white"
                }
                
                Label {
                    text: "Verbindungszeit:"
                    color: "white"
                }
                
                Label {
                    text: viewModel && viewModel.statistics ? viewModel.statistics.connection_time + " s" : "0 s"
                    Layout.fillWidth: true
                    color: "white"
                }
            }
        }
    }
}
