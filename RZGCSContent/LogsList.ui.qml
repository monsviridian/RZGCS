/*
This is a UI file (.ui.qml) that is intended to be edited in Qt Design Studio only.
It is supposed to be strictly declarative and only uses a subset of QML. If you edit
this file manually, you might introduce QML code that is not supported by Qt Design Studio.
Check out https://doc.qt.io/qtcreator/creator-quick-ui-forms.html for details on .ui.qml files.
*/
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ListView {
    id: logsList
    width: 420
    height: 200
    clip: true
    spacing: 2

    // Connect to the logger from Python backend
    model: logger ? logger.logs : []

    // Background
    Rectangle {
        color: "#1d1d1d"
        anchors.fill: parent
        z: -1
    }

    delegate: LogsListDelegate {
        width: logsList.width
    }

    ScrollBar.vertical: ScrollBar {
        active: true
        policy: ScrollBar.AsNeeded
    }

    // Listen for log changes from Python
    Connections {
        target: logger
        function onLogsChanged() {
            // Scroll to bottom (newest logs)
            positionViewAtEnd()
        }
    }
}
