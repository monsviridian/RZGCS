import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: root
    width: 400
    height: 300
    property var controller: null
    property int step: 0
    property var axisNames: ["Left X", "Left Y", "Right X", "Right Y", "LT", "RT"]
    property var axisValues: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]  // Simulated values
    ColumnLayout {
        anchors.fill: parent
        spacing: 10
        Text { text: "Joystick-Kalibrierung"; font.pixelSize: 18; font.bold: true; color: "white" }
        Text { text: "Schritt " + (step+1) + ": Bewegen Sie " + axisNames[step] + " zur maximalen Position."; color: "#cccccc" }
        ProgressBar { value: Math.abs(axisValues[step]); Layout.fillWidth: true }
        RowLayout {
            spacing: 10
            Button { text: "Weiter"; enabled: Math.abs(axisValues[step]) > 0.9; onClicked: { if (step < axisNames.length-1) step++; else step = 0 } }
            Button { text: "Abbrechen"; onClicked: step = 0 }
            Button { text: "Starten"; onClicked: if (root.controller) root.controller.start_calibration("joystick") }
        }
        // Live axis/button feedback
        GroupBox {
            title: "Live Feedback"
            Layout.fillWidth: true
            ColumnLayout {
                spacing: 4
                Repeater {
                    model: axisNames.length
                    RowLayout {
                        Text { text: axisNames[index] + ":"; color: "#cccccc"; font.pixelSize: 12 }
                        ProgressBar { value: (axisValues[index]+1)/2; Layout.fillWidth: true }
                        Text { text: axisValues[index].toFixed(2); color: "#66ccff"; font.pixelSize: 12 }
                    }
                }
                Text { text: "Buttons pressed: A, B, X, Y"; color: "#cccccc"; font.pixelSize: 12 }
            }
        }
    }
    Connections {
        target: root.controller
        function onCalibrationFinished(success, message) { 
            if (success) {
                step = 0;
                // Reset axis values
                for (var i = 0; i < axisValues.length; i++) {
                    axisValues[i] = 0.0;
                }
            }
        }
        function onJoystickDataChanged(x, y, throttle, yaw) {
            axisValues[0] = x;
            axisValues[1] = y;
            axisValues[2] = throttle;
            axisValues[3] = yaw;
            axisValues[4] = 0.0; // LT Dummy
            axisValues[5] = 0.0; // RT Dummy
        }
    }
} 