import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import Utils 1.0

Item {
    id: root
    property var messageManager
    anchors.fill: parent

    Rectangle {
        anchors.fill: parent
        color: DroneTheme.backgroundColor
        border.color: DroneTheme.borderColor
        radius: 8
        
        ListView {
            id: messageList
            anchors.fill: parent
            anchors.margins: 8
            model: messageManager ? messageManager.messages : []
            delegate: Rectangle {
                width: parent.width
                height: 40
                color: {
                    switch (model.type) {
                        case 2: return DroneTheme.warningColor;
                        case 3: return DroneTheme.errorColor;
                        case 4: return DroneTheme.successColor;
                        default: return DroneTheme.panelColor;
                    }
                }
                radius: 6
                border.color: DroneTheme.borderColor
                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 8
                    spacing: 8
                    Text {
                        text: {
                            switch (model.type) {
                                case 2: return "⚠️";
                                case 3: return "⛔";
                                case 4: return "✔️";
                                default: return "ℹ️";
                            }
                        }
                        font.pixelSize: DroneTheme.fontSizeDefault
                    }
                    Text {
                        text: model.message
                        color: DroneTheme.textColor
                        font.pixelSize: DroneTheme.fontSizeDefault
                        wrapMode: Text.Wrap
                        Layout.fillWidth: true
                    }
                }
            }
        }
    }
} 