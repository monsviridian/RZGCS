import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Item {
    id: root
    
    // Controller-Referenz, die von außen gesetzt werden kann
    property var controller: null
    
    // Custom Dialog Component
    Rectangle {
        id: dialogOverlay
        anchors.fill: parent
        color: "#80000000"
        visible: false
        z: 1000
        
        MouseArea {
            anchors.fill: parent
            onClicked: { /* Prevent closing when clicking outside */ }
        }
        
        Rectangle {
            id: dialogBox
            width: 400
            height: 200
            radius: 5
            color: "#2e2e2e"
            anchors.centerIn: parent
            
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 20
                spacing: 15
                
                Text {
                    id: dialogTitle
                    text: "Information"
                    font.pixelSize: 18
                    font.bold: true
                    color: "white"
                }
                
                Text {
                    id: dialogMessage
                    text: ""
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    wrapMode: Text.WordWrap
                    color: "white"
                }
                
                Button {
                    text: "OK"
                    Layout.alignment: Qt.AlignRight
                    onClicked: {
                        dialogOverlay.visible = false;
                    }
                }
            }
        }
        
        // Function to show a message
        function showMessage(title, message) {
            dialogTitle.text = title;
            dialogMessage.text = message;
            dialogOverlay.visible = true;
        }
    }
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 20
        
        Text {
            text: "Support Center"
            font.pixelSize: 24
            color: "white"
            Layout.fillWidth: true
        }
        
        TabBar {
            id: tabBar
            Layout.fillWidth: true
            background: Rectangle {
                color: "#303030"
            }
            
            TabButton {
                text: "Support Ticket"
                contentItem: Text {
                    text: parent.text
                    color: "white"
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
                background: Rectangle {
                    color: parent.checked ? "#505050" : "#303030"
                }
            }
            
            TabButton {
                text: "System Diagnostics"
                contentItem: Text {
                    text: parent.text
                    color: "white"
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
                background: Rectangle {
                    color: parent.checked ? "#505050" : "#303030"
                }
            }
            
            TabButton {
                text: "Knowledge Base"
                contentItem: Text {
                    text: parent.text
                    color: "white"
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
                background: Rectangle {
                    color: parent.checked ? "#505050" : "#303030"
                }
            }
        }
        
        StackLayout {
            currentIndex: tabBar.currentIndex
            Layout.fillWidth: true
            Layout.fillHeight: true
            
            // Support Ticket Tab
            Rectangle {
                color: "#1e1e1e"
                Layout.fillWidth: true
                Layout.fillHeight: true
                
                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 15
                    spacing: 10
                    
                    Text {
                        text: "Create Support Ticket"
                        font.pixelSize: 18
                        color: "white"
                    }
                    
                    Text {
                        text: "Subject:"
                        color: "white"
                    }
                    
                    TextField {
                        id: subjectField
                        Layout.fillWidth: true
                        placeholderText: "Enter subject"
                    }
                    
                    Text {
                        text: "Description:"
                        color: "white"
                    }
                    
                    ScrollView {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        
                        TextArea {
                            id: descriptionArea
                            placeholderText: "Describe your issue"
                            wrapMode: TextEdit.Wrap
                        }
                    }
                    
                    RowLayout {
                        Layout.alignment: Qt.AlignRight
                        spacing: 10
                        
                        Button {
                            text: "Cancel"
                        }
                        
                        Button {
                            text: "Submit"
                            highlighted: true
                            onClicked: {
                                if (controller) {
                                    controller.submitSupportTicket(subjectField.text, descriptionArea.text);
                                }
                            }
                        }
                    }
                }
            }
            
            // System Diagnostics Tab
            Rectangle {
                color: "#1e1e1e"
                Layout.fillWidth: true
                Layout.fillHeight: true
                
                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 15
                    spacing: 10
                    
                    Text {
                        text: "System Diagnostics"
                        font.pixelSize: 18
                        color: "white"
                    }
                    
                    Button {
                        text: "Run Diagnostics"
                        Layout.alignment: Qt.AlignLeft
                        onClicked: {
                            if (controller) {
                                controller.runDiagnostics();
                                dialogOverlay.showMessage("Diagnostics", "Running system diagnostics. Please wait...");
                            }
                        }
                    }
                    
                    ScrollView {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        
                        TextArea {
                            id: diagnosticsArea
                            readOnly: true
                            wrapMode: TextEdit.Wrap
                            text: "Diagnostic results will appear here."
                        }
                    }
                }
            }
            
            // Knowledge Base Tab
            Rectangle {
                color: "#1e1e1e"
                Layout.fillWidth: true
                Layout.fillHeight: true
                
                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 15
                    spacing: 10
                    
                    Text {
                        text: "Knowledge Base"
                        font.pixelSize: 18
                        color: "white"
                    }
                    
                    ComboBox {
                        id: categoryComboBox
                        Layout.fillWidth: true
                        model: ListModel {
                            id: categoriesModel
                        }
                        textRole: "name"
                        onCurrentIndexChanged: {
                            if (controller && currentIndex >= 0) {
                                var categoryId = categoriesModel.get(currentIndex).id;
                                controller.loadKnowledgeBaseArticles(categoryId);
                            }
                        }
                    }
                    
                    ListView {
                        id: articlesView
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        clip: true
                        model: ListModel {
                            id: articlesModel
                        }
                        delegate: ItemDelegate {
                            text: model.title
                            width: articlesView.width
                            onClicked: {
                                if (controller) {
                                    controller.loadKnowledgeBaseArticle(model.id);
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    
    // Handle signals from the controller
    Connections {
        target: controller
        
        function onDiagnosisCompletedChanged(results) {
            dialogOverlay.visible = false;
            
            // Format diagnostic results for display
            var formattedResults = "=== SYSTEM DIAGNOSTICS RESULTS ===\n\n";
            
            if (results.system) {
                formattedResults += "== SYSTEM ==\n";
                formattedResults += "OS: " + (results.system.os || "N/A") + "\n";
                formattedResults += "Python: " + (results.system.python_version || "N/A") + "\n";
                formattedResults += "PySide6: " + (results.system.pyside_version || "N/A") + "\n\n";
            }
            
            if (results.hardware) {
                formattedResults += "== HARDWARE ==\n";
                formattedResults += "CPU: " + (results.hardware.cpu || "N/A") + "\n";
                formattedResults += "RAM: " + (results.hardware.ram || "N/A") + "\n";
                formattedResults += "Disk: " + (results.hardware.disk_space || "N/A") + "\n\n";
            }
            
            if (results.network) {
                formattedResults += "== NETWORK ==\n";
                formattedResults += "Connected: " + (results.network.connected ? "Yes" : "No") + "\n";
                if (results.network.interfaces) {
                    formattedResults += "Interfaces: " + results.network.interfaces.join(", ") + "\n";
                }
                formattedResults += "\n";
            }
            
            if (results.performance) {
                formattedResults += "== PERFORMANCE ==\n";
                
                if (results.performance.cpu_benchmark) {
                    formattedResults += "CPU Benchmark: " + results.performance.cpu_benchmark + "\n";
                }
                
                if (results.performance.memory_usage) {
                    formattedResults += "Memory Usage: " + results.performance.memory_usage + "\n";
                }
                
                if (results.performance.disk_speed) {
                    formattedResults += "Disk Speed: " + results.performance.disk_speed + "\n";
                }
                formattedResults += "\n";
            }
            
            if (results.recommendations) {
                formattedResults += "== RECOMMENDATIONS ==\n";
                for (var i = 0; i < results.recommendations.length; i++) {
                    formattedResults += "- " + results.recommendations[i] + "\n";
                }
            }
            
            diagnosticsArea.text = formattedResults;
        }
        
        function onSupportTicketSubmittedChanged(success, message) {
            if (success) {
                dialogOverlay.showMessage("Ticket Submitted", message);
                subjectField.text = "";
                descriptionArea.text = "";
            } else {
                dialogOverlay.showMessage("Error", message);
            }
        }
    }
    
    // Load initial data when the component is complete
    Component.onCompleted: {
        // Initialize knowledge base categories
        if (controller) {
            var categories = controller.getKnowledgeBaseCategories();
            categoriesModel.clear();
            for (var i = 0; i < categories.length; i++) {
                categoriesModel.append(categories[i]);
            }
            
            // Auto-select first category
            if (categories.length > 0) {
                categoryComboBox.currentIndex = 0;
            }
        }
    }
}
