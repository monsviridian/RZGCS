/*
This is a UI file (.ui.qml) that is intended to be edited in Qt Design Studio only.
It is supposed to be strictly declarative and only uses a subset of QML. If you edit
this file manually, you might introduce QML code that is not supported by Qt Design Studio.
Check out https://doc.qt.io/qtcreator/creator-quick-ui-forms.html for details on .ui.qml files.
*/
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root
    color: "#2C2C2C"
    radius: 5
    border.color: "gray"
    border.width: 1

    property string currentMode: "MANUAL"
    property bool isConnected: false
    property bool isArmed: false

    RowLayout {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 10

        // Verbindungsstatus
        Rectangle {
            Layout.preferredWidth: 20
            Layout.preferredHeight: 20
            radius: 10
            color: root.isConnected ? "#00FF00" : "#FF0000"
        }

        // Modus
        Label {
            text: "Mode: " + root.currentMode
            color: "white"
            font.pixelSize: 14
        }

        // Armed-Status
        Rectangle {
            Layout.preferredWidth: 20
            Layout.preferredHeight: 20
            radius: 10
            color: root.isArmed ? "#FF0000" : "#808080"
        }
    }

    function updateMode(mode) {
        currentMode = mode
    }

    function updateConnection(status) {
        isConnected = status
    }

    function updateArmed(status) {
        isArmed = status
    }
}
