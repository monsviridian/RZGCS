import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

QtObject {
    id: messageManager
    
    // Message types
    enum MessageType {
        Info,
        Success,
        Warning,
        Error
    }
    
    // Message structure
    property var messages: []
    property int maxMessages: 10
    
    // Status properties
    property string currentStatus: "Ready"
    property bool isConnected: false
    property string connectionStatus: "Disconnected"
    property string lastError: ""
    
    // Signals
    signal messageAdded(string message, int type)
    signal messageRemoved(int index)
    signal statusChanged(string status)
    signal connectionStatusChanged(bool connected, string status)
    
    // Add a new message
    function addMessage(message, type = MessageManager.MessageType.Info) {
        var timestamp = new Date().toLocaleTimeString()
        var messageObj = {
            text: message,
            type: type,
            timestamp: timestamp,
            id: Date.now() + Math.random()
        }
        
        messages.push(messageObj)
        
        // Keep only maxMessages
        if (messages.length > maxMessages) {
            messages.shift()
        }
        
        messageAdded(message, type)
        
        // Auto-remove info messages after 5 seconds
        if (type === MessageManager.MessageType.Info) {
            removeMessageTimer.start()
        }
        
        console.log("[" + timestamp + "] " + getTypeString(type) + ": " + message)
        console.log("Message array length: " + messages.length)
        console.log("First message (should be oldest): " + (messages[0] ? messages[0].text : "none"))
        console.log("Last message (should be newest): " + (messages[messages.length-1] ? messages[messages.length-1].text : "none"))
    }
    
    // Remove message by index
    function removeMessage(index) {
        if (index >= 0 && index < messages.length) {
            messages.splice(index, 1)
            messageRemoved(index)
        }
    }
    
    // Clear all messages
    function clearMessages() {
        messages = []
    }
    
    // Update status
    function updateStatus(status) {
        if (currentStatus !== status) {
            currentStatus = status
            statusChanged(status)
            addMessage("Status: " + status, MessageManager.MessageType.Info)
        }
    }
    
    // Update connection status
    function updateConnectionStatus(connected, status) {
        isConnected = connected
        connectionStatus = status
        
        if (connected) {
            addMessage("Connected: " + status, MessageManager.MessageType.Success)
        } else {
            addMessage("Disconnected: " + status, MessageManager.MessageType.Warning)
        }
        
        connectionStatusChanged(connected, status)
    }
    
    // Log error
    function logError(error) {
        lastError = error
        addMessage(error, MessageManager.MessageType.Error)
    }
    
    // Get type string
    function getTypeString(type) {
        switch (type) {
            case MessageManager.MessageType.Info:
                return "INFO"
            case MessageManager.MessageType.Success:
                return "SUCCESS"
            case MessageManager.MessageType.Warning:
                return "WARNING"
            case MessageManager.MessageType.Error:
                return "ERROR"
            default:
                return "INFO"
        }
    }
    
    // Get type color
    function getTypeColor(type) {
        switch (type) {
            case MessageManager.MessageType.Info:
                return "#2196F3"
            case MessageManager.MessageType.Success:
                return "#4CAF50"
            case MessageManager.MessageType.Warning:
                return "#FF9800"
            case MessageManager.MessageType.Error:
                return "#F44336"
            default:
                return "#2196F3"
        }
    }
    
    // Timer for auto-removing info messages
    Timer {
        id: removeMessageTimer
        interval: 5000
        repeat: false
        onTriggered: {
            // Remove oldest info message
            for (var i = messages.length - 1; i >= 0; i--) {
                if (messages[i].type === MessageManager.MessageType.Info) {
                    messageManager.removeMessage(i)
                    break
                }
            }
        }
    }
    
    // Test function to verify message order
    function testMessageOrder() {
        console.log("=== Testing Message Order ===")
        addMessage("Test Message 1 (oldest)", MessageManager.MessageType.Info)
        addMessage("Test Message 2 (newer)", MessageManager.MessageType.Success)
        addMessage("Test Message 3 (newest)", MessageManager.MessageType.Warning)
        
        console.log("Final message order:")
        for (var i = 0; i < messages.length; i++) {
            console.log("[" + i + "] " + messages[i].text + " - " + messages[i].timestamp)
        }
    }
} 