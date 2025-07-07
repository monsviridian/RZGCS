import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: root
    width: 400
    height: 200
    property var controller: null
    property bool inProgress: false
    ColumnLayout {
        anchors.fill: parent
        spacing: 10
        Text { text: "ESC-Kalibrierung"; font.pixelSize: 18; font.bold: true; color: "white" }
        Text { text: "Folgen Sie den Anweisungen, um die ESCs zu kalibrieren. Entfernen Sie die Propeller!"; color: "#ffcc00"; wrapMode: Text.WordWrap }
        Text { text: inProgress ? "Kalibrierung läuft..." : "Bereit"; color: inProgress ? "#ffff99" : "#aaffaa" }
        RowLayout {
            spacing: 10
            Button { text: "Starten"; enabled: !inProgress; onClicked: { inProgress = true; if (root.controller) root.controller.start_calibration("esc") } }
            Button { text: "Abbrechen"; enabled: inProgress; onClicked: { inProgress = false; if (root.controller) root.controller.cancelCalibration() } }
        }
    }
    Connections {
        target: root.controller
        function onCalibrationFinished(success, message) { inProgress = false }
    }
} 