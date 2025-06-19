import QtQuick 2.15
import QtQuick.Controls.Material 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Window 2.15

// Lokale Komponenten importieren
import "./" as RZGCS

Window {
    id: window
    visible: true
    title: "RZGCS"
    width: 800
    height: 600
    minimumWidth: 800
    minimumHeight: 600

    RZGCS.Screen01 {
        anchors.fill: parent
    }
}

