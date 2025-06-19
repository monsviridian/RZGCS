/*
This is a UI file (.ui.qml) that is intended to be edited in Qt Design Studio only.
It is supposed to be strictly declarative and only uses a subset of QML. If you edit
this file manually, you might introduce QML code that is not supported by Qt Design Studio.
Check out https://doc.qt.io/qtcreator/creator-quick-ui-forms.html for details on .ui.qml files.
*/
import QtQuick
import QtQuick.Controls 6.8

Item {
    id: delegate
    width: parent.width
    height: logText.height + 4

    Rectangle {
        anchors.fill: parent
        color: index % 2 === 0 ? "#2d2d2d" : "#252525"
    }

    Text {
        id: logText
        text: modelData
        color: "white"
        font.family: "Consolas, 'Courier New', monospace"
        font.pixelSize: 12
        wrapMode: Text.WordWrap
        width: parent.width - 10
        anchors {
            left: parent.left
            leftMargin: 5
            verticalCenter: parent.verticalCenter
        }
    }
}
