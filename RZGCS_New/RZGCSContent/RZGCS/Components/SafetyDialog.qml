import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Dialog {
    id: root
    title: "Safety Warning"
    modal: true
    standardButtons: Dialog.Ok

    property string safetyMessage: ""
    property string warningType: ""

    Label {
        text: warningType + ": " + root.safetyMessage
        color: warningType === "Violation" ? "red" : (warningType === "Warning" ? "orange" : "green")
        wrapMode: Text.WordWrap
    }

    function showViolation(message) {
        warningType = "Violation"
        safetyMessage = message
        root.open()
    }
    function showWarning(message) {
        warningType = "Warning"
        safetyMessage = message
        root.open()
    }
    function showCleared(message) {
        warningType = "Cleared"
        safetyMessage = message
        root.open()
    }
} 