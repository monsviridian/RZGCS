import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    id: mainWindow
    visible: true
    width: 1024
    height: 768
    title: "Drone Control"

    // Connection status
    property bool isConnected: false
    property string connectorType: ""

    // Main menu
    menuBar: MenuBar {
        Menu {
            title: "Connection"
            MenuItem {
                text: isConnected ? "Disconnect" : "Connect..."
                onTriggered: {
                    if (isConnected) {
                        backend.disconnect()
                    } else {
                        connectionDialog.open()
                    }
                }
            }
        }
    }

    // Main area with tabs
    TabBar {
        id: tabBar
        width: parent.width

        TabButton {
            text: "Status"
        }
        TabButton {
            text: "Logs"
        }
        TabButton {
            text: "Parameters"
        }
    }

    StackLayout {
        anchors.top: tabBar.bottom
        anchors.bottom: statusBar.top
        anchors.left: parent.left
        anchors.right: parent.right
        currentIndex: tabBar.currentIndex

        // Status tab
        Item {
            StatusView {
                anchors.fill: parent
            }
        }

        // Logs tab
        Item {
            LogsList {
                anchors.fill: parent
            }
        }

        // Parameters tab
        Item {
            ParameterView {
                anchors.fill: parent
            }
        }
    }

    // Status bar
    StatusBar {
        id: statusBar
        anchors.bottom: parent.bottom
        width: parent.width

        RowLayout {
            width: parent.width
            Label {
                text: isConnected ? 
                    "✅ Connected via " + connectorType : 
                    "❌ Not connected"
            }
        }
    }

    // Connection dialog
    ConnectionDialog {
        id: connectionDialog
        
        onConnectRequested: function(connectionData) {
            backend.connect(connectionData)
        }
    }

    // Connection feedback
    Connections {
        target: backend
        
        function onConnectionStatusChanged(connected, type) {
            isConnected = connected
            connectorType = type || ""
            
            if (connected) {
                showMessage("✅ Connection established", "success")
            } else {
                showMessage("❌ Connection terminated", "error")
            }
        }
        
        function onConnectionError(message) {
            showMessage("⚠️ " + message, "error")
        }
    }

    // Message popup
    function showMessage(message, type) {
        messagePopup.text = message
        messagePopup.type = type
        messagePopup.open()
    }

    Popup {
        id: messagePopup
        x: (parent.width - width) / 2
        y: parent.height - height - statusBar.height - 10
        width: message.width + 40
        height: message.height + 20
        
        property string text: ""
        property string type: "info"  // info, success, error
        
        background: Rectangle {
            color: {
                switch (messagePopup.type) {
                    case "success": return "#4CAF50"
                    case "error": return "#F44336"
                    default: return "#2196F3"
                }
            }
            radius: 5
        }
        
        Label {
            id: message
            anchors.centerIn: parent
            text: messagePopup.text
            color: "white"
        }
        
        Timer {
            running: messagePopup.visible
            interval: 3000
            onTriggered: messagePopup.close()
        }
    }
} 