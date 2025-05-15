/*
This is a UI file (.ui.qml) that is intended to be edited in Qt Design Studio only.
It is supposed to be strictly declarative and only uses a subset of QML. If you edit
this file manually, you might introduce QML code that is not supported by Qt Design Studio.
Check out https://doc.qt.io/qtcreator/creator-quick-ui-forms.html for details on .ui.qml files.
*/
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: delegate
    color: "#2d2d2d"
    radius: 4

    // Extract log level from the message
    property string logLevel: {
        if (modelData.includes("[ERROR]")) return "error"
        if (modelData.includes("[WARNING]")) return "warning"
        if (modelData.includes("[DEBUG]")) return "debug"
        return "info"
    }

    // Set color based on log level
    property color textColor: {
        switch(logLevel) {
            case "error": return "#ff6b6b"
            case "warning": return "#ffd93d"
            case "debug": return "#6b8aff"
            default: return "#ffffff"
        }
    }

    RowLayout {
        anchors.fill: parent
        anchors.margins: Math.max(5, parent.height * 0.1)
        spacing: Math.max(5, parent.width * 0.01)

        Label {
            text: modelData
            color: textColor
            font.pixelSize: Math.max(12, parent.height * 0.4)
            font.family: "Consolas, Monaco, monospace"
            elide: Text.ElideRight
            Layout.fillWidth: true
        }
    }

    // Hover effect
    MouseArea {
        anchors.fill: parent
        hoverEnabled: true
        onEntered: parent.color = "#3d3d3d"
        onExited: parent.color = "#2d2d2d"
    }
}
