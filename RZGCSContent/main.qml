import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Window

ApplicationWindow {
    id: window
    visible: true
    title: "RZGCS"
    width: Screen.width * 0.8
    height: Screen.height * 0.8
    minimumWidth: 1024
    minimumHeight: 768

    // Enable fullscreen mode and proper scaling
    flags: Qt.Window | Qt.WindowFullscreenButtonHint

    // Set proper scaling for high DPI displays
    Screen.orientationUpdateMask: Qt.LandscapeOrientation | Qt.PortraitOrientation

    // Main layout with proper scaling
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Math.max(5, parent.width * 0.005)
        spacing: Math.max(5, parent.height * 0.005)

        // Top bar with connection controls
        RowLayout {
            Layout.fillWidth: true
            Layout.preferredHeight: Math.max(30, parent.height * 0.04)
            spacing: Math.max(5, parent.width * 0.005)

            ComboBox {
                id: portComboBox
                Layout.preferredWidth: Math.max(150, parent.width * 0.12)
                Layout.preferredHeight: Math.max(25, parent.height * 0.03)
                font.pixelSize: Math.max(10, parent.height * 0.015)
                model: serialConnector ? serialConnector.availablePorts : []
            }

            ComboBox {
                id: baudComboBox
                Layout.preferredWidth: Math.max(80, parent.width * 0.06)
                Layout.preferredHeight: Math.max(25, parent.height * 0.03)
                font.pixelSize: Math.max(10, parent.height * 0.015)
                model: ["9600", "19200", "38400", "57600", "115200"]
                currentIndex: 3
            }

            Button {
                Layout.preferredHeight: Math.max(25, parent.height * 0.03)
                font.pixelSize: Math.max(10, parent.height * 0.015)
                text: serialConnector && serialConnector.isConnected ? "Trennen" : "Verbinden"
                onClicked: {
                    if (serialConnector && serialConnector.isConnected) {
                        serialConnector.disconnect()
                    } else {
                        serialConnector.connect(portComboBox.currentText, parseInt(baudComboBox.currentText))
                    }
                }
            }

            Item { Layout.fillWidth: true }

            Button {
                Layout.preferredHeight: Math.max(25, parent.height * 0.03)
                font.pixelSize: Math.max(10, parent.height * 0.015)
                text: window.visibility === Window.FullScreen ? "Vollbild beenden" : "Vollbild"
                onClicked: {
                    if (window.visibility === Window.FullScreen) {
                        window.showNormal()
                    } else {
                        window.showFullScreen()
                    }
                }
            }
        }

        // Main content area with proper scaling
        TabBar {
            id: tabBar
            Layout.fillWidth: true
            Layout.preferredHeight: Math.max(25, parent.height * 0.03)
            currentIndex: 0

            TabButton {
                text: "Sensoren"
                font.pixelSize: Math.max(10, parent.height * 0.015)
            }
            TabButton {
                text: "Motoren"
                font.pixelSize: Math.max(10, parent.height * 0.015)
            }
            TabButton {
                text: "Logs"
                font.pixelSize: Math.max(10, parent.height * 0.015)
            }
        }

        StackLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.topMargin: Math.max(2, parent.height * 0.002)
            currentIndex: tabBar.currentIndex

            // Sensors tab
            SensorsView {
                Layout.fillWidth: true
                Layout.fillHeight: true
            }

            // Motors tab
            MotorsView {
                Layout.fillWidth: true
                Layout.fillHeight: true
            }

            // Logs tab
            LogsView {
                Layout.fillWidth: true
                Layout.fillHeight: true
            }
        }
    }

    // Handle window state changes with proper scaling
    onVisibilityChanged: {
        if (visibility === Window.FullScreen) {
            anchors.margins = 0
        } else {
            anchors.margins = Math.max(5, width * 0.005)
        }
    }

    // Handle screen changes
    onScreenChanged: {
        // Adjust window size based on screen
        width = Screen.width * 0.8
        height = Screen.height * 0.8
    }
} 