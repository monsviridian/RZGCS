import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: toast
    width: 300
    height: 60
    radius: 8
    opacity: 0
    z: 1000
    
    property string message: ""
    property int type: 0 // 0=Info, 1=Success, 2=Warning, 3=Error
    property int duration: 3000
    
    // Colors based on type
    property color backgroundColor: {
        switch (type) {
            case 0: return "#2196F3" // Info
            case 1: return "#4CAF50" // Success
            case 2: return "#FF9800" // Warning
            case 3: return "#F44336" // Error
            default: return "#2196F3"
        }
    }
    
    // Icon based on type
    property string icon: {
        switch (type) {
            case 0: return "ℹ"
            case 1: return "✓"
            case 2: return "⚠"
            case 3: return "✗"
            default: return "ℹ"
        }
    }
    
    color: backgroundColor
    border.color: Qt.darker(backgroundColor, 1.2)
    border.width: 1
    
    RowLayout {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 10
        
        // Icon
        Label {
            text: toast.icon
            color: "white"
            font.pixelSize: 20
            font.bold: true
            Layout.preferredWidth: 30
        }
        
        // Message
        Label {
            text: toast.message
            color: "white"
            font.pixelSize: 14
            wrapMode: Text.WordWrap
            Layout.fillWidth: true
        }
        
        // Close button
        Button {
            text: "×"
            Layout.preferredWidth: 20
            Layout.preferredHeight: 20
            
            background: Rectangle {
                color: parent.pressed ? Qt.darker(toast.backgroundColor, 1.3) : "transparent"
                radius: 10
            }
            
            contentItem: Text {
                text: parent.text
                color: "white"
                font.pixelSize: 16
                font.bold: true
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
            }
            
            onClicked: {
                toast.hide()
            }
        }
    }
    
    // Show animation
    function show() {
        opacity = 0
        y = -height
        visible = true
        
        showAnimation.start()
        
        // Auto-hide after duration
        if (duration > 0) {
            hideTimer.start()
        }
    }
    
    // Hide animation
    function hide() {
        hideAnimation.start()
    }
    
    // Show animation
    ParallelAnimation {
        id: showAnimation
        NumberAnimation {
            target: toast
            property: "opacity"
            to: 1.0
            duration: 300
            easing.type: Easing.OutCubic
        }
        NumberAnimation {
            target: toast
            property: "y"
            to: 20
            duration: 300
            easing.type: Easing.OutBack
        }
    }
    
    // Hide animation
    ParallelAnimation {
        id: hideAnimation
        NumberAnimation {
            target: toast
            property: "opacity"
            to: 0.0
            duration: 300
            easing.type: Easing.InCubic
        }
        NumberAnimation {
            target: toast
            property: "y"
            to: -toast.height
            duration: 300
            easing.type: Easing.InBack
        }
        onFinished: {
            toast.visible = false
        }
    }
    
    // Auto-hide timer
    Timer {
        id: hideTimer
        interval: toast.duration
        onTriggered: {
            toast.hide()
        }
    }
} 