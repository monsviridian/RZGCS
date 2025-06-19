import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import RZGCS 1.0
import QtQuick3D 6.8

Item {
    width: Constants.width
    height: Constants.height

    StackLayout {
        id: stackLayout
        anchors.fill: parent
        anchors.bottomMargin: tabBar.height
        currentIndex: tabBar.currentIndex

        PreflightView {}
        ParameterView {}
        SerialView {}
        MotorTest {}
        SensorView {
            isConnected: serialConnector ? serialConnector.connected : false
        }
        FlightView {}
        SITLView {
            id: sitlView
            sitlViewModel: backend ? backend.sitlViewModel : null
        }
        FirmwareView {
            id: firmwareView
            visible: tabBar.currentIndex === 7
            firmwareViewModel: FirmwareViewModel {
                id: firmwareViewModel
                backendFirmwareManager: backend ? backend.firmwareManager : null
                Component.onCompleted: {
                    initialize()
                }
            }
        }
    }
    
    TabBar {
        id: tabBar
        anchors.bottom: parent.bottom
        anchors.horizontalCenter: parent.horizontalCenter
        width: parent.width

        TabButton {
            text: "Preflight"
            ToolTip.visible: hovered
            ToolTip.text: "Check Preflight Conditions"
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
            text: "Parameter"
            ToolTip.visible: hovered
            ToolTip.text: "Parameter Management"
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
            text: "Serial"
            ToolTip.visible: hovered
            ToolTip.text: "Serial Connection"
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
            ToolTip.visible: hovered
            ToolTip.text: "Motor Test"
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
            text: "Sensoren"
            ToolTip.visible: hovered
            ToolTip.text: "Sensor Management"
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
            text: "Flug"
            ToolTip.visible: hovered
            ToolTip.text: "Flight Management"
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
            text: "SITL"
            ToolTip.visible: hovered
            ToolTip.text: "Software in the Loop Simulation"
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
            text: "Firmware"
            ToolTip.visible: hovered
            ToolTip.text: "Firmware-Installation und Updates"
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
    }
}
