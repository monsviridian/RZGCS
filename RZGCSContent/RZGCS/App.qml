import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Controls.Material 2.15
import com.rzgcs.licensing 1.0
import Components 1.0
import Connection 1.0

ApplicationWindow {
    id: window
    visible: true
    width: 1280
    height: 720
    title: "RZGCS - Ground Control Station"

    // Backend-Signale
    Connections {
        target: backend

        // Status-Updates
        function onStateChanged(state) {
            telemetryPanel.updateState(state)
            artificialHorizon.updateAttitude(state.attitude)
            missionInfoDisplay.updatePosition(state.position)
            flightPhaseIndicator.updatePhase(state.flight_phase)
        }

        // Modus-Updates
        function onModeChanged(mode) {
            statusOverview.updateMode(mode)
            flightPhaseIndicator.updateMode(mode)
        }

        // Fehler-Updates
        function onErrorOccurred(message) {
            errorDialog.show(message)
        }

        // Missions-Updates
        function onMissionStarted(mission) {
            missionInfoDisplay.startMission(mission)
            missionPlannerView.updateMission(mission)
            flightPhaseIndicator.startMission()
        }

        function onMissionCompleted(mission) {
            missionInfoDisplay.completeMission()
            missionPlannerView.clearMission()
            flightPhaseIndicator.completeMission()
        }

        function onMissionAborted(mission) {
            missionInfoDisplay.abortMission()
            missionPlannerView.clearMission()
            flightPhaseIndicator.abortMission()
        }

        function onWaypointReached(waypoint) {
            missionInfoDisplay.reachWaypoint(waypoint)
            missionPlannerView.updateCurrentWaypoint(waypoint)
        }

        function onMissionProgress(progress) {
            missionInfoDisplay.updateProgress(progress)
        }

        // Safety-Updates
        function onSafetyViolation(message) {
            safetyDialog.showViolation(message)
            flightPhaseIndicator.handleSafetyViolation()
        }

        function onSafetyWarning(message) {
            safetyDialog.showWarning(message)
            flightPhaseIndicator.handleSafetyWarning()
        }

        function onSafetyCleared(message) {
            safetyDialog.showCleared(message)
            flightPhaseIndicator.handleSafetyCleared()
        }
    }

    // Haupt-Layout
    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        // Toolbar
        RowLayout {
            Layout.fillWidth: true
            height: 50
            spacing: 10

            // Logo
            Image {
                source: "qrc:/Assets/ardupilot_logo.png"
                width: 40
                height: 40
            }

            // Titel
            Label {
                text: "RZGCS"
                font.pixelSize: 20
                font.bold: true
            }

            // Status
            StatusOverview {
                id: statusOverview
                Layout.fillWidth: true
            }

            // Flugphasen-Indikator
            FlightPhaseIndicator {
                id: flightPhaseIndicator
                Layout.preferredWidth: 200
            }

            // Verbindung
            ConnectionView {
                id: connectionView
                backend: backend
                Layout.preferredWidth: 300
            }
        }

        // Hauptbereich
        StackLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            currentIndex: tabBar.currentIndex

            // Preflight Tab
            PreflightView {
                id: preflightView
                backend: backend
            }

            // Parameters Tab
            ParameterView {
                id: parameterView
                backend: backend
            }

            // Sensors Tab entfernt

            // Calibration Tab
            CalibrationView {
                id: calibrationView
                backend: backend
            }

            // Motor Test Tab
            MotorTestView {
                id: motorTestView
                backend: backend
            }

            // Angel Mode Tab
            AngelModeView {
                id: angelView
                backend: backend
            }

            // License Tab
            LicenseView {
                id: licenseView
                backend: backend
            }

            // KeyGenerator Tab
            KeyGenerator {
                id: keyGenerator
            }
            KeyVerifier {
                id: keyVerifier
            }
            KeySigner {
                id: keySigner
            }
            KeyEncryptor {
                id: keyEncryptor
            }
            KeyDecryptor {
                id: keyDecryptor
            }
            // KeyManager entfernt
        }

        // Tab Bar
        TabBar {
            id: tabBar
            Layout.fillWidth: true
            currentIndex: 0
            position: TabBar.Footer
            background: Rectangle {
                color: "black"
            }

            TabButton {
                text: "Preflight"
                Material.foreground: "white"
                background: Rectangle {
                    implicitWidth: 100
                    implicitHeight: 40
                    color: parent.checked ? "#303030" : (parent.hovered ? "#404040" : "#2C2C2C")
                    border.color: "gray"
                    border.width: parent.checked ? 1 : 0
                    Behavior on color {
                        ColorAnimation { duration: 150 }
                    }
                }
            }

            TabButton {
                text: "Parameters"
                Material.foreground: "white"
                background: Rectangle {
                    implicitWidth: 100
                    implicitHeight: 40
                    color: parent.checked ? "#303030" : (parent.hovered ? "#404040" : "#2C2C2C")
                    border.color: "gray"
                    border.width: parent.checked ? 1 : 0
                    Behavior on color {
                        ColorAnimation { duration: 150 }
                    }
                }
            }

            // Sensors Tab Button entfernt

            TabButton {
                text: "Calibration"
                Material.foreground: "white"
                background: Rectangle {
                    implicitWidth: 100
                    implicitHeight: 40
                    color: parent.checked ? "#303030" : (parent.hovered ? "#404040" : "#2C2C2C")
                    border.color: "gray"
                    border.width: parent.checked ? 1 : 0
                    Behavior on color {
                        ColorAnimation { duration: 150 }
                    }
                }
            }

            TabButton {
                text: "Motor Test"
                Material.foreground: "white"
                background: Rectangle {
                    implicitWidth: 100
                    implicitHeight: 40
                    color: parent.checked ? "#303030" : (parent.hovered ? "#404040" : "#2C2C2C")
                    border.color: "gray"
                    border.width: parent.checked ? 1 : 0
                    Behavior on color {
                        ColorAnimation { duration: 150 }
                    }
                }
            }

            TabButton {
                text: "Angel Mode"
                Material.foreground: "white"
                background: Rectangle {
                    implicitWidth: 100
                    implicitHeight: 40
                    color: parent.checked ? "#303030" : (parent.hovered ? "#404040" : "#2C2C2C")
                    border.color: "gray"
                    border.width: parent.checked ? 1 : 0
                    Behavior on color {
                        ColorAnimation { duration: 150 }
                    }
                }
            }

            TabButton {
                text: "License"
                Material.foreground: "white"
                background: Rectangle {
                    implicitWidth: 100
                    implicitHeight: 40
                    color: parent.checked ? "#303030" : (parent.hovered ? "#404040" : "#2C2C2C")
                    border.color: "gray"
                    border.width: parent.checked ? 1 : 0
                    Behavior on color {
                        ColorAnimation { duration: 150 }
                    }
                }
            }

            TabButton {
                text: "Key Generator"
                Material.foreground: "white"
                background: Rectangle {
                    implicitWidth: 100
                    implicitHeight: 40
                    color: parent.checked ? "#303030" : (parent.hovered ? "#404040" : "#2C2C2C")
                    border.color: "gray"
                    border.width: parent.checked ? 1 : 0
                    Behavior on color {
                        ColorAnimation { duration: 150 }
                    }
                }
            }

            TabButton {
                text: "Key Verifier"
                Material.foreground: "white"
                background: Rectangle {
                    implicitWidth: 100
                    implicitHeight: 40
                    color: parent.checked ? "#303030" : (parent.hovered ? "#404040" : "#2C2C2C")
                    border.color: "gray"
                    border.width: parent.checked ? 1 : 0
                    Behavior on color {
                        ColorAnimation { duration: 150 }
                    }
                }
            }

            TabButton {
                text: "Key Signer"
                Material.foreground: "white"
                background: Rectangle {
                    implicitWidth: 100
                    implicitHeight: 40
                    color: parent.checked ? "#303030" : (parent.hovered ? "#404040" : "#2C2C2C")
                    border.color: "gray"
                    border.width: parent.checked ? 1 : 0
                    Behavior on color {
                        ColorAnimation { duration: 150 }
                    }
                }
            }

            TabButton {
                text: "Key Encryptor"
                Material.foreground: "white"
                background: Rectangle {
                    implicitWidth: 100
                    implicitHeight: 40
                    color: parent.checked ? "#303030" : (parent.hovered ? "#404040" : "#2C2C2C")
                    border.color: "gray"
                    border.width: parent.checked ? 1 : 0
                    Behavior on color {
                        ColorAnimation { duration: 150 }
                    }
                }
            }

            TabButton {
                text: "Key Decryptor"
                Material.foreground: "white"
                background: Rectangle {
                    implicitWidth: 100
                    implicitHeight: 40
                    color: parent.checked ? "#303030" : (parent.hovered ? "#404040" : "#2C2C2C")
                    border.color: "gray"
                    border.width: parent.checked ? 1 : 0
                    Behavior on color {
                        ColorAnimation { duration: 150 }
                    }
                }
            }

            // Key Manager Tab Button entfernt
        }
    }

    // Dialoge
    ErrorDialog {
        id: errorDialog
    }

    SafetyDialog {
        id: safetyDialog
    }
} 