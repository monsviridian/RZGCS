import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: messageList
    color: "#1E1E1E"
    border.color: "#404040"
    border.width: 1
    
    // Debug-Ausgabe beim Laden
    Component.onCompleted: {
        console.log("D: MessageList: Component.onCompleted")
        console.log("D: MessageList: messageManager:", messageManager)
        if (messageManager) {
            console.log("D: MessageList: messageManager.messages:", messageManager.messages)
            console.log("D: MessageList: messageManager.messages.length:", messageManager.messages ? messageManager.messages.length : 0)
        } else {
            console.log("W: MessageList: messageManager ist null")
        }
    }
    
    // Connections für MessageManager-Signale
    Connections {
        target: messageManager
        function onMessagesChanged() {
            console.log("D: MessageList: messagesChanged signal received")
            console.log("D: messageManager.messages.length:", messageManager ? messageManager.messages.length : 0)
            // Auto-scroll to top when messages change
            scrollToLatestMessage()
        }
        
        function onMessageAdded(message, type) {
            console.log("D: MessageList: messageAdded signal received:", message, type)
            // Auto-scroll to top when new message is added
            scrollToLatestMessage()
        }
    }
    
    // Function to scroll to the latest message (bottom)
    function scrollToLatestMessage() {
        if (listView.count > 0) {
            // Use a small delay to ensure the model is updated
            scrollTimer.start()
        }
    }
    
    // Timer for delayed scrolling to ensure model is updated
    Timer {
        id: scrollTimer
        interval: 50  // 50ms delay
        repeat: false
        onTriggered: {
            if (listView.count > 0) {
                listView.positionViewAtEnd()  // Scroll to bottom (newest message)
                console.log("D: Scrolled to latest message (bottom)")
            }
        }
    }
    
    // Header
    Rectangle {
        id: header
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        height: 30
        color: "#2C2C2C"
        border.color: "#404040"
        border.width: 0
        
        RowLayout {
            anchors.fill: parent
            anchors.margins: 5
            
            Label {
                text: "Recent Messages"
                color: "white"
                font.pixelSize: 14
                font.bold: true
            }
            
            Item {
                Layout.fillWidth: true
            }
            
            Label {
                text: messageManager && messageManager.messages ? messageManager.messages.length + " messages" : "0 messages"
                color: "#CCCCCC"
                font.pixelSize: 12
            }
        }
    }
    
    // Message List
    ListView {
        id: listView
        anchors.top: header.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.margins: 5
        
        model: messageManager && messageManager.messages ? messageManager.messages : []
        
        // Ensure latest messages are always visible at the top
        verticalLayoutDirection: ListView.TopToBottom
        
        delegate: Rectangle {
            width: listView.width
            height: messageText.height + 20
            color: index % 2 === 0 ? "#252525" : "#2A2A2A"
            
            RowLayout {
                anchors.fill: parent
                anchors.margins: 5
                spacing: 8
                
                // Type indicator
                Rectangle {
                    Layout.preferredWidth: 4
                    Layout.fillHeight: true
                    color: getTypeColor(modelData.type)
                }
                
                // Message text with timestamp
                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 2
                    
                    Label {
                        id: messageText
                        text: modelData.text || modelData.message
                        color: "white"
                        font.pixelSize: 12
                        wrapMode: Text.WordWrap
                        Layout.fillWidth: true
                    }
                    
                    Label {
                        text: modelData.timestamp || ""
                        color: "#888888"
                        font.pixelSize: 10
                        Layout.fillWidth: true
                    }
                }
            }
        }
        
        // Scroll indicator
        ScrollBar.vertical: ScrollBar {
            active: true
            policy: ScrollBar.AsNeeded
        }
        
        // Auto-scroll to bottom when model changes
        onModelChanged: {
            if (count > 0) {
                positionViewAtEnd()  // Scroll to bottom (newest message)
            }
        }
    }
    
    // Empty state
    Rectangle {
        anchors.fill: listView
        color: "#1E1E1E"
        visible: !messageManager || !messageManager.messages || messageManager.messages.length === 0
        
        ColumnLayout {
            anchors.centerIn: parent
            spacing: 10
            
            Label {
                text: "No messages yet"
                color: "#888888"
                font.pixelSize: 16
                Layout.alignment: Qt.AlignHCenter
            }
            
            Label {
                text: "Messages will appear here when events occur"
                color: "#666666"
                font.pixelSize: 12
                Layout.alignment: Qt.AlignHCenter
            }
        }
    }
    
    // Hilfsfunktionen für Message-Typen
    function getTypeColor(type) {
        switch (type) {
            case 1: return "#2196F3"  // Info - Blau
            case 2: return "#FF9800"  // Warning - Orange
            case 3: return "#F44336"  // Error - Rot
            case 4: return "#4CAF50"  // Success - Grün
            default: return "#2196F3"
        }
    }
} 