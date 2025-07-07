import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Dialogs
import QtQuick.Window 2.15

Item {
    id: root
    anchors.fill: parent
    
    // Properties - ohne Binding-Loops
    property string searchText: ""
    property bool showModifiedOnly: false
    
    // Verwende Context Properties statt direkte Bindings
    // Diese werden automatisch über die Context Properties verfügbar gemacht
    
    // Advanced search properties
    property bool searchActive: searchText.trim() !== "" || showModifiedOnly
    
    Rectangle {
        anchors.fill: parent
        color: "#181c20"
        
        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 10
            spacing: 10
            
            // Header with advanced search
            Rectangle {
                Layout.fillWidth: true
                height: 80
                color: "#23272e"
                radius: 5
                
                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 10
                    spacing: 8
                    
                    // Title and search row
                    RowLayout {
                        Layout.fillWidth: true
                        
                        Text {
                            text: "Parameter Editor"
                            color: "#e0e0e0"
                            font.pixelSize: 16
                            font.bold: true
                        }
                        
                        Item { Layout.fillWidth: true }
                        
                        // Search field
                        TextField {
                            id: searchField
                            placeholderText: "Search parameters..."
                            text: searchText
                            onTextChanged: {
                                searchText = text
                                if (parameterViewModel) {
                                    parameterViewModel.setFilterText(text)
                                }
                            }
                            Layout.preferredWidth: 200
                            color: "#e0e0e0"
                            background: Rectangle {
                                color: "#181c20"
                                border.color: searchField.activeFocus ? "#3498db" : "#444"
                                radius: 3
                            }
                        }
                        
                        // Clear search button
                        Button {
                            text: "Clear"
                            onClicked: {
                                searchField.text = ""
                                searchText = ""
                                if (parameterViewModel) {
                                    parameterViewModel.setFilterText("")
                                }
                            }
                            background: Rectangle {
                                color: parent.pressed ? "#e74c3c" : "#c0392b"
                                radius: 3
                            }
                            contentItem: Text {
                                text: parent.text
                                color: "#ffffff"
                                horizontalAlignment: Text.AlignHCenter
                            }
                        }
                        
                        // Show modified only checkbox
                        CheckBox {
                            text: "Modified Only"
                            checked: showModifiedOnly
                            onCheckedChanged: {
                                showModifiedOnly = checked
                                if (parameterViewModel) {
                                    parameterViewModel.setShowModifiedOnly(checked)
                                }
                            }
                            indicator: Rectangle {
                                width: 16
                                height: 16
                                border.color: parent.checked ? "#3498db" : "#666"
                                color: parent.checked ? "#3498db" : "transparent"
                                radius: 3
                                Text {
                                    anchors.centerIn: parent
                                    text: "✓"
                                    color: "white"
                                    font.pixelSize: 10
                                    visible: parent.parent.checked
                                }
                            }
                            contentItem: Text {
                                text: parent.text
                                color: "#e0e0e0"
                                font.pixelSize: 12
                            }
                        }
                    }
                    
                    // Tools row
                    RowLayout {
                        Layout.fillWidth: true
                        
                        // Refresh button
                        Button {
                            text: "Refresh"
                            onClicked: {
                                if (parameterViewModel) {
                                    parameterViewModel.refreshParameters()
                                    if (messageManager) {
                                        messageManager.addMessage("Parameter refresh started", 1)
                                    }
                                }
                            }
                            background: Rectangle {
                                color: parent.pressed ? "#27ae60" : "#2ecc71"
                                radius: 3
                            }
                            contentItem: Text {
                                text: parent.text
                                color: "#ffffff"
                                horizontalAlignment: Text.AlignHCenter
                            }
                        }
                        
                        // Save button
                        Button {
                            text: "Save to File"
                            onClicked: {
                                if (parameterViewModel) {
                                    var success = parameterViewModel.saveToFile("parameters.txt")
                                    if (messageManager) {
                                        if (success) {
                                            messageManager.addMessage("Parameters saved to file", 4)
                                        } else {
                                            messageManager.addMessage("Failed to save parameters", 3)
                                        }
                                    }
                                }
                            }
                            background: Rectangle {
                                color: parent.pressed ? "#e67e22" : "#f39c12"
                                radius: 3
                            }
                            contentItem: Text {
                                text: parent.text
                                color: "#ffffff"
                                horizontalAlignment: Text.AlignHCenter
                            }
                        }
                        
                        // Load button
                        Button {
                            text: "Load from File"
                            onClicked: {
                                if (parameterViewModel) {
                                    var success = parameterViewModel.loadFromFile("parameters.txt")
                                    if (messageManager) {
                                        if (success) {
                                            messageManager.addMessage("Parameters loaded from file", 4)
                                        } else {
                                            messageManager.addMessage("Failed to load parameters", 3)
                                        }
                                    }
                                }
                            }
                            background: Rectangle {
                                color: parent.pressed ? "#8e44ad" : "#9b59b6"
                                radius: 3
                            }
                            contentItem: Text {
                                text: parent.text
                                color: "#ffffff"
                                horizontalAlignment: Text.AlignHCenter
                            }
                        }
                        
                        // Reset to defaults button
                        Button {
                            text: "Reset to Defaults"
                            onClicked: {
                                if (parameterViewModel) {
                                    parameterViewModel.resetAllToDefaults()
                                    if (messageManager) {
                                        messageManager.addMessage("Reset to defaults requested", 2)
                                    }
                                }
                            }
                            background: Rectangle {
                                color: parent.pressed ? "#c0392b" : "#e74c3c"
                                radius: 3
                            }
                            contentItem: Text {
                                text: parent.text
                                color: "#ffffff"
                                horizontalAlignment: Text.AlignHCenter
                            }
                        }
                        
                        Item { Layout.fillWidth: true }
                        
                        // Status text
                        Text {
                            text: parameterViewModel && parameterViewModel.parameterModel ? `${parameterViewModel.parameterModel.count} Parameters` : "0 Parameters"
                            color: "#b0b0b0"
                            font.pixelSize: 12
                        }
                    }
                }
            }
            
            // Main content area
            RowLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                spacing: 10
                
                // Category/Group navigation (only show when not searching)
                Rectangle {
                    visible: !searchActive
                    Layout.preferredWidth: 250
                    Layout.fillHeight: true
                    color: "#23272e"
                    radius: 5
                    
                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 10
                        spacing: 8
                        
                        Text {
                            text: "Categories"
                            color: "#e0e0e0"
                            font.pixelSize: 14
                            font.bold: true
                        }
                        
                        // Categories list
                        ListView {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            clip: true
                            model: parameterViewModel ? parameterViewModel.categories : []
                            
                            delegate: Rectangle {
                                width: parent.width
                                height: 30
                                color: "transparent"
                                
                                Text {
                                    anchors.left: parent.left
                                    anchors.verticalCenter: parent.verticalCenter
                                    text: modelData ? modelData.name : ""
                                    color: "#e0e0e0"
                                    font.pixelSize: 12
                                }
                                
                                MouseArea {
                                    anchors.fill: parent
                                    onClicked: {
                                        // TODO: Implement category selection
                                        if (messageManager) {
                                            messageManager.addMessage(`Selected category: ${modelData.name}`, 1)
                                        }
                                    }
                                }
                            }
                            
                            ScrollBar.vertical: ScrollBar {
                                active: true
                                policy: ScrollBar.AlwaysOn
                                background: Rectangle { color: "#181c20" }
                                contentItem: Rectangle { color: "#23272e"; radius: 3 }
                            }
                        }
                    }
                }
                
                // Parameter list
                Rectangle {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    color: "#23272e"
                    radius: 5
                    border.color: "#333"
                    border.width: 1
                    
                    ListView {
                        id: parameterListView
                        anchors.fill: parent
                        anchors.margins: 5
                        clip: true
                        
                        model: parameterViewModel ? parameterViewModel.parameterModel : null
                        
                        header: Rectangle {
                            width: parameterListView.width
                            height: 35
                            color: "#181c20"
                            
                            RowLayout {
                                anchors.fill: parent
                                anchors.margins: 8
                                
                                Text {
                                    text: "Parameter Name"
                                    color: "#e0e0e0"
                                    font.pixelSize: 12
                                    font.bold: true
                                    Layout.preferredWidth: 200
                                }
                                
                                Text {
                                    text: "Value"
                                    color: "#e0e0e0"
                                    font.pixelSize: 12
                                    font.bold: true
                                    Layout.preferredWidth: 100
                                }
                                
                                Text {
                                    text: "Type"
                                    color: "#e0e0e0"
                                    font.pixelSize: 12
                                    font.bold: true
                                    Layout.preferredWidth: 80
                                }
                                
                                Text {
                                    text: "Description"
                                    color: "#e0e0e0"
                                    font.pixelSize: 12
                                    font.bold: true
                                    Layout.fillWidth: true
                                }
                            }
                        }
                        
                        delegate: Rectangle {
                            width: parameterListView.width
                            height: 40
                            color: index % 2 === 0 ? "#2c3e50" : "#34495e"
                            
                            RowLayout {
                                anchors.fill: parent
                                anchors.margins: 8
                                
                                // Parameter Name
                                Text {
                                    text: model.NameRole || "N/A"
                                    font.pixelSize: 10
                                    font.family: "Courier"
                                    color: "#e0e0e0"
                                    Layout.preferredWidth: 200
                                    elide: Text.ElideRight
                                    Component.onCompleted: {
                                        console.log("Delegate created for", model.NameRole)
                                    }
                                }
                                
                                // Parameter Value (editable)
                                TextField {
                                    text: model.ValueRole || "N/A"
                                    font.pixelSize: 10
                                    font.family: "Courier"
                                    color: "#e0e0e0"
                                    Layout.preferredWidth: 100
                                    horizontalAlignment: TextInput.AlignRight
                                    background: Rectangle {
                                        color: activeFocus ? "#23272e" : "#181c20"
                                        border.color: activeFocus ? "#3498db" : "#444"
                                        radius: 3
                                    }
                                    selectionColor: "#3498db"
                                    onEditingFinished: {
                                        if (parameterViewModel) {
                                            var newValue = parseFloat(text)
                                            if (!isNaN(newValue)) {
                                                parameterViewModel.set_parameter_value(model.NameRole, newValue)
                                                if (messageManager) {
                                                    messageManager.addMessage(`Parameter ${model.NameRole} set to ${newValue}`, 4)
                                                }
                                            }
                                        }
                                    }
                                }
                                
                                // Parameter Type
                                Text {
                                    text: model.TypeRole || "N/A"
                                    font.pixelSize: 9
                                    color: "#7f8c8d"
                                    Layout.preferredWidth: 80
                                }
                                
                                // Parameter Description
                                Text {
                                    text: model.DescriptionRole || "N/A"
                                    font.pixelSize: 9
                                    color: "#b0b0b0"
                                    Layout.fillWidth: true
                                    elide: Text.ElideRight
                                }
                            }
                        }
                        
                        ScrollBar.vertical: ScrollBar {
                            active: true
                            policy: ScrollBar.AlwaysOn
                            background: Rectangle { color: "#181c20" }
                            contentItem: Rectangle { color: "#23272e"; radius: 3 }
                        }
                    }
                }
            }
            
            // Footer
            Rectangle {
                Layout.fillWidth: true
                height: 25
                color: "#23272e"
                radius: 5
                
                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 8
                    
                    Text {
                        text: parameterViewModel && parameterViewModel.parameterModel ? `${parameterViewModel.parameterModel.count} Parameters` : "0 Parameters"
                        font.pixelSize: 10
                        color: "#b0b0b0"
                    }
                    
                    Item { Layout.fillWidth: true }
                    
                    Text {
                        text: "RZGCS with QGroundControl-inspired features"
                        font.pixelSize: 9
                        color: "#7f8c8d"
                    }
                }
            }
        }
    }
    
    // Error handling - nur für existierende Signale
    Connections {
        target: parameterViewModel
        
        function onRefreshCompleted(success) {
            if (messageManager) {
                if (success) {
                    messageManager.addMessage("Parameter refresh completed", 4)
                } else {
                    messageManager.addMessage("Parameter refresh failed", 3)
                }
            }
        }
    }
    
    // Auto-load parameters when connected
    Component.onCompleted: {
        if (parameterViewModel) {
            // Try to load parameters if already connected
            parameterViewModel.refreshParameters()
        }
    }
} 