import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import RZGCS 1.0
import QtQuick3D 6.8

Item {
    width: Constants.width
    height: Constants.height

    StackLayout {
        anchors.fill: parent
        currentIndex: tabBar.currentIndex

        PreflightView {}
        ParameterView {}
        SerialView {}
        MotorTest {}
        SensorView {}
        FlightView {}

        TabBar {
            id: tabBar
            anchors.bottom: parent.bottom
            anchors.horizontalCenter: parent.horizontalCenter
            width: parent.width

            TabButton {
                text: "Preflight"
            }
            TabButton {
                text: "Parameter"
            }
            TabButton {
                text: "Sensoren"
            }
            TabButton {
                text: "Flug"
            }
        }
    }
}
