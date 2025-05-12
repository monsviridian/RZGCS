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
        width: 100
        anchors.top: tabBar.bottom
        anchors.right: parent.right
        anchors.left: parent.left
        anchors.bottom: parent.bottom
        currentIndex: tabBar.currentIndex

        Item {
            Rectangle {

                anchors.fill: parent


                color: "black"
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                z: -1 // sorgt dafür, dass es hinter allen anderen Komponenten liegt
            }

            PreflightView {
                id: preflightview
                anchors.fill:parent
            }
        }

        Item {
            Rectangle {

                anchors.fill: parent


                color: "black"
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                z: -1 // sorgt dafür, dass es hinter allen anderen Komponenten liegt
            }

            ParameterView {
                id: parameterview
                anchors.left: parent.left
                anchors.bottom: parent.bottom
                anchors.top: parent.top
                anchors.topMargin: 180
            }
            SerialView {
                id: serialview

                anchors.left: parameterview.right
            }

            MotorTest {
                id: motortest
                anchors.left: serialview.right
                anchors.bottom: parent.bottom
                anchors.top: parent.top
            }
        }

        Item {

            Text {
                id: titel
                text: qsTr("Calibration")
                anchors.bottom: sensorview.top
                anchors.centerIn: parent
            }

            SensorView {
                id: sensorview
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.bottom: parent.bottom
            }
        }
        Item {
            FlightView {
                id: flightview
                anchors.centerIn: parent
            }
        }
    }

    TabBar {
        id: tabBar
        currentIndex: 0
        anchors.top: parent.top
        anchors.right: stackLayout.right
        anchors.left: stackLayout.left

        TabButton {
            text: qsTr("Preflight")
        }

        TabButton {
            text: qsTr("Parameter")
        }

        TabButton {
            text: qsTr("Sensors")
        }
        TabButton {
            text: qsTr("Flight")
        }
    }

    Item {
        id: __materialLibrary__
    }
}
