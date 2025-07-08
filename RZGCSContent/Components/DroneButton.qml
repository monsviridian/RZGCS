import QtQuick 2.15
import QtQuick.Controls 2.15
import "../Utils"

Button {
    id: root
    
    // Properties
    property string buttonType: "primary" // "primary", "secondary", "danger", "success"
    property color primaryColor: DroneTheme.accentColor
    property color secondaryColor: "#c27ba0"
    property color dangerColor: DroneTheme.errorColor
    property color successColor: DroneTheme.successColor
    property color textColor: "#ffffff"
    property bool showIcon: false
    property string iconSource: ""
    
    // Styling basierend auf buttonType
    property color buttonColor: {
        switch(buttonType) {
            case "primary": return primaryColor
            case "secondary": return secondaryColor
            case "danger": return dangerColor
            case "success": return successColor
            default: return primaryColor
        }
    }
    
    background: Rectangle {
        color: root.enabled ? 
               (root.pressed ? Qt.darker(root.buttonColor, 1.2) : root.buttonColor) : 
               "#555555"
        radius: DroneTheme.radiusSmall
        opacity: root.hovered ? 0.8 : 1.0
        
        Behavior on opacity {
            NumberAnimation { duration: DroneTheme.animationDurationFast }
        }
        
        Behavior on color {
            ColorAnimation { duration: DroneTheme.animationDurationFast }
        }
    }
    
    contentItem: Row {
        spacing: DroneTheme.spacingSmall
        anchors.centerIn: parent
        
        Image {
            source: root.iconSource
            width: 16
            height: 16
            visible: root.showIcon && root.iconSource !== ""
            anchors.verticalCenter: parent.verticalCenter
        }
        
        Text {
            text: root.text
            color: root.textColor
            font.pixelSize: DroneTheme.fontSizeDefault
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            anchors.verticalCenter: parent.verticalCenter
        }
    }
    
    // Klick-Animation
    scale: root.pressed ? 0.95 : 1.0
    
    Behavior on scale {
        NumberAnimation { duration: DroneTheme.animationDurationFast }
    }
    
    // Hover-Effekt
    states: [
        State {
            name: "hovered"
            when: root.hovered
            PropertyChanges {
                target: root
                scale: 1.02
            }
        }
    ]
    
    transitions: [
        Transition {
            from: ""
            to: "hovered"
            reversible: true
            NumberAnimation {
                properties: "scale"
                duration: DroneTheme.animationDurationFast
            }
        }
    ]
} 