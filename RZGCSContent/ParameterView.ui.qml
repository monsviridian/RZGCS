

/*
This is a UI file (.ui.qml) that is intended to be edited in Qt Design Studio only.
It is supposed to be strictly declarative and only uses a subset of QML. If you edit
this file manually, you might introduce QML code that is not supported by Qt Design Studio.
Check out https://doc.qt.io/qtcreator/creator-quick-ui-forms.html for details on .ui.qml files.
*/
import QtQuick
import QtQuick.Controls 6.8
import QtQuick3D 6.8
import QtQuick3D.Helpers 6.8

ListView {
    id: listview
    width: 420
    height: 420

    highlightMoveDuration: 0

    children: [
        Rectangle {
            color: "#1d1d1d"
            anchors.fill: parent
            z: -1
        }
    ]

    model: ParameterViewModel {}

    highlight: Rectangle {
        width: listview.width
        height: 120
        color: "#343434"
        radius: 4
        border.color: "#0d52a4"
        border.width: 8
    }

    delegate: ParameterViewDelegate {}

    Rectangle {
        id: rectangle
        x: 0
        y: -152
        width: 420
        height: 152
        color: "#0d52a4"
        anchors.bottom: listview.top

        TextInput {
            id: textInput
            x: 8
            y: 59
            width: 287
            height: 35
            text: qsTr("Search")
            font.pixelSize: 12

            color: "#1d1d1d"
        }
        Button {
            id: buttonsave
            x: 297
            y: 101
            width: 104
            height: 32
            text: qsTr("Save")
        }
        Button {
            id: buttonsearch
            x: 301
            y: 14
            width: 100
            height: 32
            text: qsTr("Search")
        }
    }

    Item {
        id: __materialLibrary__
    }
}
