/*
This is a UI file (.ui.qml) that is intended to be edited in Qt Design Studio only.
It is supposed to be strictly declarative and only uses a subset of QML. If you edit
this file manually, you might introduce QML code that is not supported by Qt Design Studio.
Check out https://doc.qt.io/qtcreator/creator-quick-ui-forms.html for details on .ui.qml files.
*/

import QtQuick
import QtQuick.Controls

Rectangle {
    id: root
    width: 600
    height: 800
    color: "#3b3a3a"

    Slider {
        id: slider
        x: 107
        y: 507
        width: 86
        height: 293
        value: 0.5
        orientation: Qt.Vertical
    }

    Slider {
        id: slider1
        x: 182
        y: 507
        width: 86
        height: 293
        value: 0.5
        orientation: Qt.Vertical
    }

    Slider {
        id: slider2
        x: 286
        y: 507
        width: 86
        height: 293
        value: 0.5
        orientation: Qt.Vertical
    }

    Slider {
        id: slider3
        x: 412
        y: 507
        width: 86
        height: 293
        value: 0.5
        orientation: Qt.Vertical
    }

    Slider {
        id: slider4
        x: 22
        y: 507
        width: 86
        height: 293
        value: 0.5
        orientation: Qt.Vertical
    }

    CheckBox {
        id: checkBox
        x: 191
        y: 384
        width: 218
        height: 69
        text: qsTr("Propeller are remove")

        Connections {
            target: checkBox
            function onClicked() { animatedImage.playing = true }
        }





    }

    AnimatedImage {
        id: animatedImage
        x: 126
        y: 50
        width: 349
        height: 306
        source: "../../RZGroundControlV0001/Python/RZ/assets/Animation.gif"
        paused: false
        playing: false
    }
}
