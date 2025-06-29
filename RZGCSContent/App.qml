import QtQuick 2.15
import QtQuick.Controls.Material 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Window 2.15

// Kein Import nötig, der Screen01 wird über die QML-Engine direkt registriert

Window {
    id: window
    visible: true
    title: "RZGCS"
    width: 800
    height: 600
    minimumWidth: 800
    minimumHeight: 600

    // Direktes Laden der QML-Datei mit einem Loader
    Loader {
        id: mainLoader
        anchors.fill: parent
        source: "Screen01.ui.qml"
    }
}
