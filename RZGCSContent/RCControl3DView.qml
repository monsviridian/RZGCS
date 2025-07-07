import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: root
    width: 400
    height: 300
    property var controller: null
    property var channelValues: [1500, 1500, 1500, 1500, 1500, 1500, 1500, 1500]
    ColumnLayout {
        anchors.fill: parent
        spacing: 10
        Text { text: "RC-Kalibrierung"; font.pixelSize: 18; font.bold: true; color: "white" }
        Text { text: "Bewegen Sie alle Steuerknüppel und Schalter auf Ihrer Fernsteuerung in ihre Endpositionen."; color: "#cccccc"; wrapMode: Text.WordWrap }
        Repeater {
            model: 8
            RowLayout {
                spacing: 8
                Text { text: "Kanal " + (index+1) + ":"; color: "white"; font.pixelSize: 12 }
                ProgressBar { value: (root.channelValues[index] - 1000) / 1000; Layout.fillWidth: true }
                Text { text: root.channelValues[index]; color: "#66ccff"; font.pixelSize: 12 }
            }
        }
        RowLayout {
            spacing: 10
            Button { text: "Starten"; onClicked: if (root.controller) root.controller.start_calibration("rc") }
            Button { text: "Abbrechen"; onClicked: if (root.controller) root.controller.cancelCalibration() }
            Button { text: "Speichern"; onClicked: if (root.controller) root.controller.saveCalibration("rc") }
        }
    }
    Connections {
        target: root.controller
        function onRCChannelsChanged(values) { 
            if (values && values.length > 0) {
                root.channelValues = values;
            }
        }
        function onCalibrationFinished(success, message) { 
            if (success) {
                // Reset channel values to center position
                for (var i = 0; i < root.channelValues.length; i++) {
                    root.channelValues[i] = 1500;
                }
            }
        }
    }
} 