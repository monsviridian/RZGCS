/*
This is a UI file (.ui.qml) that is intended to be edited in Qt Design Studio only.
It is supposed to be strictly declarative and only uses a subset of QML. If you edit
this file manually, you might introduce QML code that is not supported by Qt Design Studio.
Check out https://doc.qt.io/qtcreator/creator-quick-ui-forms.html for details on .ui.qml files.
*/
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Window 2.15

Window {
    id: parameterWindow
    width: 800
    height: 600
    title: "Parameter Manager"
    visible: true
    
    // Context Properties
    property var parameterViewModel: parameterViewModel
    property var messageManager: messageManager

    Rectangle {
        anchors.fill: parent
        color: "#f0f0f0"
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 10
            
            // Header
            Rectangle {
                Layout.fillWidth: true
                height: 60
                color: "#2c3e50"
                radius: 5

        RowLayout {
                    anchors.fill: parent
                    anchors.margins: 10
                    
                    Text {
                        text: "Parameter Manager"
                color: "white"
                        font.pixelSize: 18
                        font.bold: true
                    }
                    
                    Item { Layout.fillWidth: true }
                    
                    // Status
                    Text {
                        text: parameterViewModel ? parameterViewModel.status : "Nicht verbunden"
                    color: "white"
                        font.pixelSize: 12
        }

                    // Loading Indicator
                    BusyIndicator {
                        running: parameterViewModel ? parameterViewModel.isLoading : false
                        visible: parameterViewModel ? parameterViewModel.isLoading : false
                }
                }
            }
            
            // Toolbar
            Rectangle {
            Layout.fillWidth: true
                height: 50
                color: "#ecf0f1"
                radius: 5

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 10

                    // Filter
                    Text {
                        text: "Filter:"
                        font.pixelSize: 12
                    }
                    
                    TextField {
                        id: filterField
                        Layout.preferredWidth: 200
                        placeholderText: "Parameter-Name eingeben..."
                        text: parameterViewModel ? parameterViewModel.filterText : ""
                        onTextChanged: {
                            if (parameterViewModel) {
                                parameterViewModel.filterParameters(text)
                            }
                        }
                    }
                    
                    Item { Layout.fillWidth: true }
                    
                    // Buttons
                    Button {
                        text: "Laden"
                        enabled: parameterViewModel && !parameterViewModel.isLoading
                        onClicked: {
                            if (parameterViewModel) {
                                parameterViewModel.loadParameters()
                                if (messageManager) {
                                    messageManager.addMessage("Parameter werden geladen...", 1)
                                }
                            }
                        }
                    }
                    
                    Button {
                        text: "Speichern"
                        enabled: parameterViewModel && parameterViewModel.parameterModel.count > 0
                        onClicked: {
                            if (parameterViewModel) {
                                parameterViewModel.saveToFile("parameters.txt")
                                if (messageManager) {
                                    messageManager.addMessage("Parameter gespeichert", 4)
                                }
                            }
                        }
                    }
                    
                    Button {
                        text: "Löschen"
                        enabled: parameterViewModel && parameterViewModel.parameterModel.count > 0
                        onClicked: {
                            if (parameterViewModel) {
                                parameterViewModel.clearParameters()
                                if (messageManager) {
                                    messageManager.addMessage("Parameter gelöscht", 2)
                                }
                            }
                        }
                    }
                }
            }
            
            // Parameter Table
            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                color: "white"
                radius: 5
                border.color: "#bdc3c7"
                border.width: 1
                
                ListView {
                    id: parameterListView
                    anchors.fill: parent
                    anchors.margins: 5
                    clip: true
                    
                    model: parameterViewModel ? parameterViewModel.parameterModel : null
                    
                    header: Rectangle {
                        width: parameterListView.width
                height: 40
                        color: "#34495e"

                RowLayout {
                    anchors.fill: parent
                            anchors.margins: 10
                            
                            Text {
                                text: "Name"
                                color: "white"
                                font.pixelSize: 12
                                font.bold: true
                                Layout.preferredWidth: 200
                            }
                            
                            Text {
                                text: "Wert"
                                color: "white"
                                font.pixelSize: 12
                                font.bold: true
                                Layout.preferredWidth: 100
                            }

                    Text {
                                text: "Typ"
                                color: "white"
                                font.pixelSize: 12
                                font.bold: true
                                Layout.preferredWidth: 80
                    }
                    
                    Text {
                                text: "Index"
                                color: "white"
                                font.pixelSize: 12
                                font.bold: true
                                Layout.preferredWidth: 60
                            }
                            
                            Item { Layout.fillWidth: true }
                        }
                    }
                    
                    delegate: Rectangle {
                        width: parameterListView.width
                        height: 40
                        color: index % 2 === 0 ? "#f8f9fa" : "white"
                        
                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: 10
                            
                            // Parameter Name
                            Text {
                                text: model.name
                                font.pixelSize: 11
                                font.family: "Courier"
                                Layout.preferredWidth: 200
                                elide: Text.ElideRight
                            }
                            
                            // Parameter Value (editable)
                            TextField {
                                text: model.value
                                font.pixelSize: 11
                                font.family: "Courier"
                                Layout.preferredWidth: 100
                                horizontalAlignment: TextInput.AlignRight
                                
                                onEditingFinished: {
                                    if (parameterViewModel) {
                                        var newValue = parseFloat(text)
                                        if (!isNaN(newValue)) {
                                            parameterViewModel.setParameter(model.name, newValue)
                                            if (messageManager) {
                                                messageManager.addMessage(`Parameter ${model.name} auf ${newValue} gesetzt`, 4)
                                            }
                                        }
                                    }
                                }
                            }
                            
                            // Parameter Type
                            Text {
                                text: model.type
                                font.pixelSize: 10
                                color: "#7f8c8d"
                                Layout.preferredWidth: 80
                            }
                            
                            // Parameter Index
                            Text {
                                text: model.index
                                font.pixelSize: 10
                                color: "#7f8c8d"
                                Layout.preferredWidth: 60
                                horizontalAlignment: Text.AlignRight
                            }
                            
                            Item { Layout.fillWidth: true }
                        }
                        
                        // Hover effect
                        Rectangle {
                            anchors.fill: parent
                            color: "transparent"
                            border.color: "#3498db"
                            border.width: 1
                            visible: mouseArea.containsMouse
                        }
                        
                        MouseArea {
                            id: mouseArea
                            anchors.fill: parent
                            hoverEnabled: true
                            onClicked: {
                                // Focus on the value field for editing
                                parent.children[1].forceActiveFocus()
                            }
                }
            }
            
                    ScrollBar.vertical: ScrollBar {
                        active: true
                    }
            }
        }

            // Footer
            Rectangle {
                Layout.fillWidth: true
                height: 30
                color: "#ecf0f1"
                radius: 5
                
                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 10
                    
                    Text {
                        text: parameterViewModel ? `${parameterViewModel.parameterModel.count} Parameter` : "0 Parameter"
                        font.pixelSize: 11
                        color: "#7f8c8d"
                    }
                    
                    Item { Layout.fillWidth: true }
                    
                    Text {
                        text: "DroneKit/PyMAVLink Parameter Manager"
                        font.pixelSize: 10
                        color: "#7f8c8d"
                    }
                }
            }
        }
    }
    
    // Error handling
    Connections {
        target: parameterViewModel
        
        function onErrorOccurred(error) {
            if (messageManager) {
                messageManager.addMessage(`Parameter-Fehler: ${error}`, 3)
            }
        }
    }
    
    // Auto-load parameters when connected
    Component.onCompleted: {
        if (parameterViewModel) {
            // Try to load parameters if already connected
            parameterViewModel.loadParameters()
        }
    }
}
