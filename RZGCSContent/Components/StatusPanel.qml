import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../Utils"

Rectangle {
    id: root
    
    // Properties
    property alias title: titleText.text
    property alias content: contentArea.children
    property bool showBorder: true
    property bool showHeader: true
    property color headerColor: DroneTheme.accentColor
    property int headerHeight: 40
    
    // Styling
    color: DroneTheme.panelColor
    radius: DroneTheme.radiusDefault
    border.color: showBorder ? DroneTheme.borderColor : "transparent"
    border.width: showBorder ? 1 : 0
    
    // Layout
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: DroneTheme.marginDefault
        spacing: DroneTheme.spacingMedium
        
        // Header
        Rectangle {
            id: headerRect
            Layout.fillWidth: true
            Layout.preferredHeight: showHeader ? headerHeight : 0
            color: "transparent"
            visible: showHeader
            
            Text {
                id: titleText
                anchors.left: parent.left
                anchors.verticalCenter: parent.verticalCenter
                color: headerColor
                font.pixelSize: DroneTheme.fontSizeTitle
                font.bold: true
            }
            
            // Optional: Subtitle oder Status
            Text {
                id: subtitleText
                anchors.right: parent.right
                anchors.verticalCenter: parent.verticalCenter
                color: DroneTheme.textSecondaryColor
                font.pixelSize: DroneTheme.fontSizeSmall
                visible: false
                
                property string subtitle: ""
                text: subtitle
            }
        }
        
        // Content Area
        Item {
            id: contentArea
            Layout.fillWidth: true
            Layout.fillHeight: true
        }
    }
    
    // Öffentliche API
    function setSubtitle(text) {
        subtitleText.subtitle = text
        subtitleText.visible = text !== ""
    }
    
    function setHeaderColor(color) {
        headerColor = color
    }
    
    function setHeaderHeight(height) {
        headerHeight = height
    }
} 