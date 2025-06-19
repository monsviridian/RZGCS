
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

ApplicationWindow {
    title: "MAVSDK Test"
    width: 1024
    height: 768
    visible: true
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 10
        
        // Connection Panel
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 60
            color: "#f0f0f0"
            border.color: "#c0c0c0"
            radius: 5
            
            RowLayout {
                anchors.fill: parent
                anchors.margins: 10
                spacing: 10
                
                TextField {
                    id: connectionField
                    Layout.fillWidth: true
                    placeholderText: "Verbindungsstring (z.B. udp://:14550)"
                    text: "udp://:14550"
                }
                
                Button {
                    text: droneController.is_connected ? "Trennen" : "Verbinden"
                    onClicked: {
                        if (droneController.is_connected) {
                            droneController.disconnect();
                        } else {
                            droneController.connect(connectionField.text);
                        }
                    }
                }
            }
        }
        
        // Main Content
        SplitView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            orientation: Qt.Horizontal
            
            // Sensor Panel
            Rectangle {
                SplitView.preferredWidth: 300
                SplitView.minimumWidth: 200
                color: "#f8f8f8"
                border.color: "#c0c0c0"
                
                ListView {
                    id: sensorListView
                    anchors.fill: parent
                    anchors.margins: 5
                    model: sensorViewModel.get_sensor_list()
                    
                    delegate: Rectangle {
                        width: sensorListView.width
                        height: 40
                        color: index % 2 === 0 ? "#ffffff" : "#f0f0f0"
                        
                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: 5
                            spacing: 5
                            
                            Text {
                                text: modelData.name
                                font.bold: true
                                Layout.preferredWidth: 140
                            }
                            
                            Text {
                                text: modelData.value
                                Layout.fillWidth: true
                            }
                            
                            Text {
                                text: modelData.unit
                                Layout.preferredWidth: 30
                            }
                        }
                    }
                    
                    // Update der Sensorliste, wenn sich Daten ändern
                    Connections {
                        target: sensorViewModel
                        function onSensorUpdated() {
                            sensorListView.model = sensorViewModel.get_sensor_list()
                        }
                    }
                }
            }
            
            // Log Panel
            Rectangle {
                SplitView.fillWidth: true
                SplitView.minimumWidth: 300
                color: "#f8f8f8"
                border.color: "#c0c0c0"
                
                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 5
                    spacing: 5
                    
                    Text {
                        text: "Logs"
                        font.bold: true
                        font.pixelSize: 16
                    }
                    
                    ListView {
                        id: logListView
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        model: logger.getLogs(100)
                        clip: true
                        
                        delegate: Text {
                            width: logListView.width
                            text: modelData
                            wrapMode: Text.Wrap
                            font.pixelSize: 12
                        }
                        
                        // Auto-Scroll nach unten
                        onCountChanged: {
                            currentIndex = count - 1
                        }
                    }
                    
                    // Update der Logs, wenn neue hinzukommen
                    Connections {
                        target: logger
                        function onLogAdded() {
                            logListView.model = logger.getLogs(100)
                        }
                    }
                }
            }
        }
    }
}
