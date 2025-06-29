import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: statusBar
    height: 30
    color: "#2C2C2C"
    border.color: "#404040"
    border.width: 1
    
    property var messageManager: null
    
    RowLayout {
        anchors.fill: parent
        anchors.margins: 5
        spacing: 10
        
        // Connection Status
        Rectangle {
            Layout.preferredWidth: 12
            Layout.preferredHeight: 12
            radius: 6
            color: messageManager && messageManager.isConnected ? "#4CAF50" : "#F44336"
            
            ToolTip {
                visible: parent.hovered
                text: messageManager ? messageManager.connectionStatus : "Unknown"
                delay: 500
            }
        }
        
        Label {
            text: messageManager ? messageManager.connectionStatus : "Disconnected"
            color: "white"
            font.pixelSize: 12
            Layout.preferredWidth: 100
        }
        
        // Separator
        Rectangle {
            Layout.preferredWidth: 1
            Layout.fillHeight: true
            color: "#404040"
        }
        
        // Current Status
        Label {
            text: "Status:"
            color: "#CCCCCC"
            font.pixelSize: 12
        }
        
        Label {
            text: messageManager ? messageManager.currentStatus : "Ready"
            color: "white"
            font.pixelSize: 12
            Layout.preferredWidth: 150
        }
        
        // Separator
        Rectangle {
            Layout.preferredWidth: 1
            Layout.fillHeight: true
            color: "#404040"
        }
        
        // Last Error (if any)
        Label {
            text: "Last Error:"
            color: "#CCCCCC"
            font.pixelSize: 12
            visible: messageManager && messageManager.lastError !== ""
        }
        
        Label {
            text: messageManager && messageManager.lastError !== "" ? messageManager.lastError : ""
            color: "#F44336"
            font.pixelSize: 12
            visible: messageManager && messageManager.lastError !== ""
            Layout.fillWidth: true
            elide: Text.ElideRight
        }
        
        // Spacer
        Item {
            Layout.fillWidth: true
        }
        
        // Message Count
        Label {
            text: "Messages: " + (messageManager ? messageManager.messages.length : 0)
            color: "#CCCCCC"
            font.pixelSize: 12
            Layout.preferredWidth: 80
        }
        
        // Clear Messages Button
        Button {
            text: "Clear"
            Layout.preferredWidth: 50
            Layout.preferredHeight: 20
            visible: messageManager && messageManager.messages.length > 0
            
            background: Rectangle {
                color: parent.pressed ? "#404040" : "#303030"
                border.color: "#505050"
                border.width: 1
                radius: 2
            }
            
            contentItem: Text {
                text: parent.text
                color: "white"
                font.pixelSize: 10
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
            }
            
            onClicked: {
                if (messageManager) {
                    messageManager.clearMessages()
                }
            }
        }
    }
} 