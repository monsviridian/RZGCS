import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Controls.Material 2.15

Rectangle {
    id: root
    color: "#2C2C2C"
    radius: 5
    border.color: "gray"
    border.width: 1

    property string currentPhase: "DISARMED"
    property string currentMode: "MANUAL"
    property bool isMissionActive: false
    property bool hasSafetyViolation: false
    property bool hasSafetyWarning: false

    // Phasen-Farben
    readonly property var phaseColors: {
        "DISARMED": "#808080",  // Grau
        "ARMED": "#FFA500",     // Orange
        "TAKEOFF": "#FFD700",   // Gold
        "FLYING": "#00FF00",    // Grün
        "LANDING": "#FFD700",   // Gold
        "LANDED": "#808080",    // Grau
        "ERROR": "#FF0000",     // Rot
        "EMERGENCY": "#FF0000"  // Rot
    }

    // Phasen-Icons
    readonly property var phaseIcons: {
        "DISARMED": "🔒",
        "ARMED": "⚡",
        "TAKEOFF": "🛫",
        "FLYING": "✈",
        "LANDING": "🛬",
        "LANDED": "🛬",
        "ERROR": "⚠",
        "EMERGENCY": "🚨"
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 5

        // Phase-Anzeige
        Rectangle {
            Layout.fillWidth: true
            height: 30
            color: phaseColors[currentPhase]
            radius: 3

            RowLayout {
                anchors.fill: parent
                anchors.margins: 5
                spacing: 5

                Text {
                    text: phaseIcons[currentPhase]
                    font.pixelSize: 16
                }

                Text {
                    text: currentPhase
                    color: "white"
                    font.pixelSize: 14
                    font.bold: true
                    Layout.fillWidth: true
                }
            }
        }

        // Modus-Anzeige
        Rectangle {
            Layout.fillWidth: true
            height: 25
            color: "#404040"
            radius: 3

            Text {
                anchors.fill: parent
                anchors.margins: 5
                text: "Mode: " + currentMode
                color: "white"
                font.pixelSize: 12
                verticalAlignment: Text.AlignVCenter
            }
        }

        // Missions-Status
        Rectangle {
            Layout.fillWidth: true
            height: 25
            color: isMissionActive ? "#00FF00" : "#404040"
            radius: 3
            visible: isMissionActive

            Text {
                anchors.fill: parent
                anchors.margins: 5
                text: "Mission Active"
                color: "white"
                font.pixelSize: 12
                verticalAlignment: Text.AlignVCenter
            }
        }

        // Safety-Status
        Rectangle {
            Layout.fillWidth: true
            height: 25
            color: hasSafetyViolation ? "#FF0000" : (hasSafetyWarning ? "#FFA500" : "#404040")
            radius: 3
            visible: hasSafetyViolation || hasSafetyWarning

            Text {
                anchors.fill: parent
                anchors.margins: 5
                text: hasSafetyViolation ? "Safety Violation!" : "Safety Warning"
                color: "white"
                font.pixelSize: 12
                verticalAlignment: Text.AlignVCenter
            }
        }
    }

    // Funktionen
    function updatePhase(phase) {
        currentPhase = phase
    }

    function updateMode(mode) {
        currentMode = mode
    }

    function startMission() {
        isMissionActive = true
    }

    function completeMission() {
        isMissionActive = false
    }

    function abortMission() {
        isMissionActive = false
    }

    function handleSafetyViolation() {
        hasSafetyViolation = true
        hasSafetyWarning = false
    }

    function handleSafetyWarning() {
        hasSafetyWarning = true
        hasSafetyViolation = false
    }

    function handleSafetyCleared() {
        hasSafetyViolation = false
        hasSafetyWarning = false
    }
} 