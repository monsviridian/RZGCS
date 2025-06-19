import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import RZGCS.FlightControl 1.0

Item {
    id: root
    
    // Properties
    property var viewModel: ConnectionViewModel {}
    
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
                    text: "Status: " + viewModel.status
                    Layout.fillWidth: true
                }
                
                Label {
                    text: "Typ: " + viewModel.type
                    Layout.fillWidth: true
                }
                
                Label {
                    text: "Verbunden: " + (viewModel.state.is_connected ? "Ja" : "Nein")
                    Layout.fillWidth: true
                }
                
                Label {
                    text: "Fehler: " + (viewModel.state.is_error ? "Ja" : "Nein")
                    Layout.fillWidth: true
                }
                
                Label {
                    text: "Fehlermeldung: " + (viewModel.state.error_message || "Keine")
                    Layout.fillWidth: true
                }
            }
        }
        
        // Parameter
        GroupBox {
            title: "Verbindungsparameter"
            Layout.fillWidth: true
            
            ColumnLayout {
                anchors.fill: parent
                
                ComboBox {
                    id: typeComboBox
                    model: ["Serial", "UDP", "TCP", "MAVLink"]
                    currentIndex: viewModel.type === ConnectionType.MAVLINK ? 3 :
                                viewModel.type === ConnectionType.TCP ? 2 :
                                viewModel.type === ConnectionType.UDP ? 1 : 0
                    Layout.fillWidth: true
                    
                    onCurrentIndexChanged: {
                        var type = ConnectionType.MAVLINK
                        if (currentIndex === 0) type = ConnectionType.SERIAL
                        else if (currentIndex === 1) type = ConnectionType.UDP
                        else if (currentIndex === 2) type = ConnectionType.TCP
                        
                        var params = viewModel.parameters
                        params.type = type
                        viewModel.set_parameters(params)
                    }
                }
                
                TextField {
                    id: portTextField
                    placeholderText: "Port"
                    text: viewModel.parameters.port || ""
                    Layout.fillWidth: true
                    
                    onTextChanged: {
                        var params = viewModel.parameters
                        params.port = text
                        viewModel.set_parameters(params)
                    }
                }
                
                TextField {
                    id: baudrateTextField
                    placeholderText: "Baudrate"
                    text: viewModel.parameters.baudrate || ""
                    Layout.fillWidth: true
                    
                    onTextChanged: {
                        var params = viewModel.parameters
                        params.baudrate = parseInt(text) || 0
                        viewModel.set_parameters(params)
                    }
                }
                
                TextField {
                    id: hostTextField
                    placeholderText: "Host"
                    text: viewModel.parameters.host || ""
                    Layout.fillWidth: true
                    
                    onTextChanged: {
                        var params = viewModel.parameters
                        params.host = text
                        viewModel.set_parameters(params)
                    }
                }
                
                TextField {
                    id: portNumberTextField
                    placeholderText: "Port-Nummer"
                    text: viewModel.parameters.port_number || ""
                    Layout.fillWidth: true
                    
                    onTextChanged: {
                        var params = viewModel.parameters
                        params.port_number = parseInt(text) || 0
                        viewModel.set_parameters(params)
                    }
                }
                
                SpinBox {
                    id: timeoutSpinBox
                    from: 1
                    to: 60
                    value: viewModel.parameters.timeout
                    Layout.fillWidth: true
                    
                    onValueChanged: {
                        var params = viewModel.parameters
                        params.timeout = value
                        viewModel.set_parameters(params)
                    }
                }
                
                SpinBox {
                    id: retryCountSpinBox
                    from: 0
                    to: 10
                    value: viewModel.parameters.retry_count
                    Layout.fillWidth: true
                    
                    onValueChanged: {
                        var params = viewModel.parameters
                        params.retry_count = value
                        viewModel.set_parameters(params)
                    }
                }
                
                CheckBox {
                    id: autoReconnectCheckBox
                    text: "Auto-Reconnect"
                    checked: viewModel.parameters.auto_reconnect
                    Layout.fillWidth: true
                    
                    onCheckedChanged: {
                        var params = viewModel.parameters
                        params.auto_reconnect = checked
                        viewModel.set_parameters(params)
                    }
                }
            }
        }
        
        // Statistiken
        GroupBox {
            title: "Verbindungsstatistiken"
            Layout.fillWidth: true
            
            ColumnLayout {
                anchors.fill: parent
                
                Label {
                    text: "Bytes gesendet: " + viewModel.statistics.bytes_sent
                    Layout.fillWidth: true
                }
                
                Label {
                    text: "Bytes empfangen: " + viewModel.statistics.bytes_received
                    Layout.fillWidth: true
                }
                
                Label {
                    text: "Pakete gesendet: " + viewModel.statistics.packets_sent
                    Layout.fillWidth: true
                }
                
                Label {
                    text: "Pakete empfangen: " + viewModel.statistics.packets_received
                    Layout.fillWidth: true
                }
                
                Label {
                    text: "Fehler: " + viewModel.statistics.errors
                    Layout.fillWidth: true
                }
                
                Label {
                    text: "Verbindungszeit: " + viewModel.statistics.connection_time.toFixed(1) + "s"
                    Layout.fillWidth: true
                }
                
                Label {
                    text: "Letzter Fehler: " + (viewModel.statistics.last_error_message || "Keine")
                    Layout.fillWidth: true
                }
            }
        }
        
        // Aktionen
        RowLayout {
            Layout.fillWidth: true
            spacing: 10
            
            Button {
                text: viewModel.state.is_connected ? "Trennen" : "Verbinden"
                Layout.fillWidth: true
                
                onClicked: {
                    if (viewModel.state.is_connected) {
                        viewModel.disconnect()
                    } else {
                        viewModel.connect()
                    }
                }
            }
            
            Button {
                text: "Exportieren"
                Layout.fillWidth: true
                
                onClicked: {
                    // TODO: Dateidialog implementieren
                    viewModel.export_connection_data("connection.json")
                }
            }
            
            Button {
                text: "Importieren"
                Layout.fillWidth: true
                
                onClicked: {
                    // TODO: Dateidialog implementieren
                    viewModel.import_connection_data("connection.json")
                }
            }
        }
    }
    
    // Error-Handler
    Connections {
        target: viewModel
        function onError_occurred(message) {
            // TODO: Fehlermeldung anzeigen
            console.error("Verbindungsfehler:", message)
        }
    }
} 