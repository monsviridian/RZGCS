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

    // Define constants locally
    readonly property color textColor: "#ffffff"
    readonly property color labelColor: "#88a4bf"
    readonly property int textSize: Math.max(10, height * 0.3)
    readonly property int labelSize: Math.max(8, height * 0.25)

    // Safe model data access
    property string paramName: model && model.name ? model.name : ""
    property string paramValue: model && model.value ? model.value : "0"
    property string paramUnit: model && model.unit ? model.unit : ""

    RowLayout {
        anchors.fill: parent
        anchors.margins: Math.max(5, parent.height * 0.1)
        spacing: Math.max(5, parent.width * 0.01)

        // Parameter name
        Label {
            text: paramName
            color: labelColor
            font.pixelSize: labelSize
            Layout.preferredWidth: parent.width * 0.4
            elide: Text.ElideRight
        }

        // Parameter value
        Label {
            text: paramValue
            color: textColor
            font.pixelSize: textSize
            Layout.preferredWidth: parent.width * 0.3
            horizontalAlignment: Text.AlignRight
        }

        // Parameter unit
        Label {
            text: paramUnit
            color: labelColor
            font.pixelSize: labelSize
            Layout.preferredWidth: parent.width * 0.2
            visible: paramUnit !== ""
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
