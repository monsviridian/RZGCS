import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Dialog {
    id: root
    title: "Error"
    modal: true
    standardButtons: Dialog.Ok

    property string errorMessage: ""

    Label {
        text: root.errorMessage
        color: "red"
        wrapMode: Text.WordWrap
    }

    function show(message) {
        root.errorMessage = message
        root.open()
    }
} 