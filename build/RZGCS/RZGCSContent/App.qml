import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Window
import "./"

Window {
    id: window
    visible: true
    title: "RZGCS"
    width: 800
    height: 600
    minimumWidth: 800
    minimumHeight: 600

    Screen01 {
        anchors.fill: parent
    }
}

