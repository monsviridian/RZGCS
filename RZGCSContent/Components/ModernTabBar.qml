import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import Utils 1.0

TabBar {
    id: tabBar
    background: Rectangle {
        color: DroneTheme.panelColor
        radius: 8
        border.color: DroneTheme.borderColor
    }
    contentItem: RowLayout {
        spacing: 4
        Repeater {
            model: tabBar.contentModel
            TabButton {
                text: modelData.title
                checked: tabBar.currentIndex === index
                onClicked: tabBar.currentIndex = index
                background: Rectangle {
                    color: checked ? DroneTheme.accentColor : DroneTheme.panelColor
                    radius: 6
                    border.color: DroneTheme.borderColor
                }
                contentItem: Text {
                    text: modelData.title
                    color: checked ? DroneTheme.textColor : DroneTheme.textSecondaryColor
                    font.pixelSize: DroneTheme.fontSizeDefault
                }
            }
        }
    }
} 