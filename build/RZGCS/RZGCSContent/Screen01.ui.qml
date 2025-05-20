/*
This is a UI file (.ui.qml) that is intended to be edited in Qt Design Studio only.
It is supposed to be strictly declarative and only uses a subset of QML. If you edit
this file manually, you might introduce QML code that is not supported by Qt Design Studio.
Check out https://doc.qt.io/qtcreator/creator-quick-ui-forms.html for details on .ui.qml files.
*/
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Window

Item {
    id: root
    width: 800
    height: 600

    // Ensure serialConnector is available
    Component.onCompleted: {
        if (serialConnector) {
            serialConnector.load_ports()
        }
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 10

        // Connection controls
        Rectangle {
            Layout.fillWidth: true
            color: "black"
            implicitHeight: connectionControlsRow.implicitHeight + 16  // Add some padding
            
            RowLayout {
                id: connectionControlsRow
                anchors {
                    left: parent.left
                    right: parent.right
                    top: parent.top
                    margins: 8
                }
                spacing: 10

                ComboBox {
                    id: portComboBox
                    model: serialConnector ? serialConnector.availablePorts : []
                    Layout.preferredWidth: 200
                    background: Rectangle {
                        color: "black"
                        border.color: "gray"
                        border.width: 1
                        radius: 4
                    }
                    contentItem: Text {
                        text: portComboBox.displayText
                        color: "white"
                        verticalAlignment: Text.AlignVCenter
                        horizontalAlignment: Text.AlignLeft
                        leftPadding: 5
                    }
                    popup.background: Rectangle {
                        color: "black"
                        border.color: "gray"
                    }
                    delegate: ItemDelegate {
                        width: portComboBox.width
                        contentItem: Text {
                            text: modelData
                            color: "white"
                            verticalAlignment: Text.AlignVCenter
                        }
                        background: Rectangle {
                            color: highlighted ? "gray" : "black"
                        }
                        highlighted: portComboBox.highlightedIndex === index
                    }
                    onCurrentTextChanged: if (serialConnector) serialConnector.setPort(currentText)
                }

                ComboBox {
                    id: baudComboBox
                    model: serialConnector ? serialConnector.availableBaudRates : []
                    currentIndex: 4  // 115200
                    Layout.preferredWidth: 100
                    background: Rectangle {
                        color: "black"
                        border.color: "gray"
                        border.width: 1
                        radius: 4
                    }
                    contentItem: Text {
                        text: baudComboBox.displayText
                        color: "white"
                        verticalAlignment: Text.AlignVCenter
                        horizontalAlignment: Text.AlignLeft
                        leftPadding: 5
                    }
                    popup.background: Rectangle {
                        color: "black"
                        border.color: "gray"
                    }
                    delegate: ItemDelegate {
                        width: baudComboBox.width
                        contentItem: Text {
                            text: modelData
                            color: "white"
                            verticalAlignment: Text.AlignVCenter
                        }
                        background: Rectangle {
                            color: highlighted ? "gray" : "black"
                        }
                        highlighted: baudComboBox.highlightedIndex === index
                    }
                    onCurrentTextChanged: if (serialConnector) serialConnector.setBaudRate(parseInt(currentText))
                }

                Button {
                    text: serialConnector && serialConnector.connected ? "Disconnect" : "Connect"
                    Layout.preferredWidth: 100
                    background: Rectangle {
                        color: "black"
                        border.color: "gray"
                        border.width: 1
                        radius: 4
                    }
                    contentItem: Text {
                        text: parent.text
                        color: "white"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                    onClicked: {
                        if (serialConnector) {
                            if (serialConnector.connected) {
                                serialConnector.disconnect()
                            } else {
                                serialConnector.connect()
                            }
                        }
                    }
                }

                Button {
                    text: "Refresh Ports"
                    Layout.preferredWidth: 100
                    background: Rectangle {
                        color: "black"
                        border.color: "gray"
                        border.width: 1
                        radius: 4
                    }
                    contentItem: Text {
                        text: parent.text
                        color: "white"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                    onClicked: if (serialConnector) serialConnector.load_ports()
                }
                
                // Flugmodus-Auswahl
                ComboBox {
                    id: flightModeCombo
                    model: ["STABILIZE", "ALT_HOLD", "LOITER", "RTL", "AUTO", "GUIDED"]
                    Layout.preferredWidth: 120
                    background: Rectangle {
                        color: "black"
                        border.color: "gray"
                        border.width: 1
                        radius: 4
                        opacity: flightModeCombo.enabled ? 1.0 : 0.3
                    }
                    contentItem: Text {
                        text: flightModeCombo.displayText
                        color: "white"
                        verticalAlignment: Text.AlignVCenter
                        horizontalAlignment: Text.AlignLeft
                        leftPadding: 5
                        opacity: flightModeCombo.enabled ? 1.0 : 0.3
                    }
                    popup.background: Rectangle {
                        color: "black"
                        border.color: "gray"
                    }
                    delegate: ItemDelegate {
                        width: flightModeCombo.width
                        contentItem: Text {
                            text: modelData
                            color: "white"
                            verticalAlignment: Text.AlignVCenter
                        }
                        background: Rectangle {
                            color: highlighted ? "gray" : "black"
                        }
                        highlighted: flightModeCombo.highlightedIndex === index
                    }
                    enabled: serialConnector && serialConnector.connected
                    onActivated: {
                        if (serialConnector) {
                            serialConnector.setFlightMode(currentText)
                        }
                    }
                }
                
                // Arm/Disarm Buttons
                Button {
                    text: "ARM"
                    Layout.preferredWidth: 80
                    background: Rectangle {
                        color: "black"
                        border.color: "gray"
                        border.width: 1
                        radius: 4
                    }
                    contentItem: Text {
                        text: parent.text
                        color: "white"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        opacity: parent.enabled ? 1.0 : 0.3
                    }
                    enabled: serialConnector && serialConnector.connected
                    onClicked: {
                        if (serialConnector) {
                            serialConnector.armDisarm(true)
                        }
                    }
                }
                
                Button {
                    text: "DISARM"
                    Layout.preferredWidth: 80
                    background: Rectangle {
                        color: "black"
                        border.color: "gray"
                        border.width: 1
                        radius: 4
                    }
                    contentItem: Text {
                        text: parent.text
                        color: "white"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        opacity: parent.enabled ? 1.0 : 0.3
                    }
                    enabled: serialConnector && serialConnector.connected
                    onClicked: {
                        if (serialConnector) {
                            serialConnector.armDisarm(false)
                        }
                    }
                }
                
                Button {
                    text: window.visibility === Window.FullScreen ? "Exit Fullscreen" : "Fullscreen"
                    Layout.preferredWidth: 120
                    background: Rectangle {
                        color: "black"
                        border.color: "gray"
                        border.width: 1
                        radius: 4
                    }
                    contentItem: Text {
                        text: parent.text
                        color: "white"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                    onClicked: {
                        if (window.visibility === Window.FullScreen) {
                            window.showNormal()
                        } else {
                            window.showFullScreen()
                        }
                    }
                }
            }
        }

        // Tab bar
        TabBar {
            background: Rectangle {
                color: "black"
            }
            id: tabBar
            Layout.fillWidth: true
            currentIndex: 0

            TabButton {
                text: "Preflight"
                contentItem: Text {
                    text: parent.text
                    color: "white"
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
                background: Rectangle {
                    color: parent.checked ? "#303030" : "black"
                    border.color: "gray"
                    border.width: parent.checked ? 1 : 0
                }
            }
            TabButton {
                text: "Parameters"
                contentItem: Text {
                    text: parent.text
                    color: "white"
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
                background: Rectangle {
                    color: parent.checked ? "#303030" : "black"
                    border.color: "gray"
                    border.width: parent.checked ? 1 : 0
                }
            }
            TabButton {
                text: "Sensors"
                contentItem: Text {
                    text: parent.text
                    color: "white"
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
                background: Rectangle {
                    color: parent.checked ? "#303030" : "black"
                    border.color: "gray"
                    border.width: parent.checked ? 1 : 0
                }
            }
            TabButton {
                text: "Flight"
                contentItem: Text {
                    text: parent.text
                    color: "white"
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
                background: Rectangle {
                    color: parent.checked ? "#303030" : "black"
                    border.color: "gray"
                    border.width: parent.checked ? 1 : 0
                }
            }
            TabButton {
                text: "RZ Store"
                contentItem: Text {
                    text: parent.text
                    color: "white"
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
                background: Rectangle {
                    color: parent.checked ? "#303030" : "black"
                    border.color: "gray"
                    border.width: parent.checked ? 1 : 0
                }
            }
        }

        // Content
        StackLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            currentIndex: tabBar.currentIndex

            PreflightView {
                Layout.fillWidth: true
                Layout.fillHeight: true
            }
            ParameterView {
                Layout.fillWidth: true
                Layout.fillHeight: true
            }
            SensorView {
                Layout.fillWidth: true
                Layout.fillHeight: true
            }
            FlightView {
                Layout.fillWidth: true
                Layout.fillHeight: true
            }
            StoreView {
                Layout.fillWidth: true
                Layout.fillHeight: true
            }
        }
    }
}
