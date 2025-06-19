import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root
    color: "#303030"
    border.color: "#404040"
    border.width: 1

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 10

        // Warnung
        Rectangle {
            Layout.fillWidth: true
            color: "#FF0000"
            radius: 4
            visible: true

            Label {
                anchors.fill: parent
                anchors.margins: 10
                text: "WARNING: Remove propellers before testing motors!"
                color: "white"
                font.bold: true
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
            }
        }

        // Motor-Test-Steuerung
        GroupBox {
            title: "Motor Test Controls"
            Layout.fillWidth: true

            ColumnLayout {
                anchors.fill: parent
                spacing: 10

                // Alle Motoren
                GroupBox {
                    title: "All Motors"
                    Layout.fillWidth: true

                    RowLayout {
                        anchors.fill: parent
                        spacing: 10

                        Slider {
                            id: allMotorsSlider
                            Layout.fillWidth: true
                            from: 0
                            to: 100
                            value: 0
                            enabled: false
                        }

                        Label {
                            text: allMotorsSlider.value.toFixed(0) + "%"
                            Layout.preferredWidth: 50
                        }

                        Button {
                            text: "Test All"
                            Layout.preferredWidth: 100
                            enabled: false
                            onClicked: {
                                // TODO: Test all motors
                            }
                        }
                    }
                }

                // Einzelne Motoren
                GridLayout {
                    Layout.fillWidth: true
                    columns: 2
                    columnSpacing: 10
                    rowSpacing: 10

                    // Motor 1
                    GroupBox {
                        title: "Motor 1"
                        Layout.fillWidth: true

                        ColumnLayout {
                            anchors.fill: parent
                            spacing: 5

                            Slider {
                                id: motor1Slider
                                Layout.fillWidth: true
                                from: 0
                                to: 100
                                value: 0
                                enabled: false
                            }

                            Label {
                                text: motor1Slider.value.toFixed(0) + "%"
                                horizontalAlignment: Text.AlignHCenter
                            }

                            Button {
                                text: "Test"
                                Layout.fillWidth: true
                                enabled: false
                                onClicked: {
                                    // TODO: Test motor 1
                                }
                            }
                        }
                    }

                    // Motor 2
                    GroupBox {
                        title: "Motor 2"
                        Layout.fillWidth: true

                        ColumnLayout {
                            anchors.fill: parent
                            spacing: 5

                            Slider {
                                id: motor2Slider
                                Layout.fillWidth: true
                                from: 0
                                to: 100
                                value: 0
                                enabled: false
                            }

                            Label {
                                text: motor2Slider.value.toFixed(0) + "%"
                                horizontalAlignment: Text.AlignHCenter
                            }

                            Button {
                                text: "Test"
                                Layout.fillWidth: true
                                enabled: false
                                onClicked: {
                                    // TODO: Test motor 2
                                }
                            }
                        }
                    }

                    // Motor 3
                    GroupBox {
                        title: "Motor 3"
                        Layout.fillWidth: true

                        ColumnLayout {
                            anchors.fill: parent
                            spacing: 5

                            Slider {
                                id: motor3Slider
                                Layout.fillWidth: true
                                from: 0
                                to: 100
                                value: 0
                                enabled: false
                            }

                            Label {
                                text: motor3Slider.value.toFixed(0) + "%"
                                horizontalAlignment: Text.AlignHCenter
                            }

                            Button {
                                text: "Test"
                                Layout.fillWidth: true
                                enabled: false
                                onClicked: {
                                    // TODO: Test motor 3
                                }
                            }
                        }
                    }

                    // Motor 4
                    GroupBox {
                        title: "Motor 4"
                        Layout.fillWidth: true

                        ColumnLayout {
                            anchors.fill: parent
                            spacing: 5

                            Slider {
                                id: motor4Slider
                                Layout.fillWidth: true
                                from: 0
                                to: 100
                                value: 0
                                enabled: false
                            }

                            Label {
                                text: motor4Slider.value.toFixed(0) + "%"
                                horizontalAlignment: Text.AlignHCenter
                            }

                            Button {
                                text: "Test"
                                Layout.fillWidth: true
                                enabled: false
                                onClicked: {
                                    // TODO: Test motor 4
                                }
                            }
                        }
                    }
                }
            }
        }

        // Status
        GroupBox {
            title: "Motor Status"
            Layout.fillWidth: true

            GridLayout {
                anchors.fill: parent
                columns: 2
                columnSpacing: 10
                rowSpacing: 5

                Label { text: "Motor 1:" }
                Label { text: "Not Ready" }

                Label { text: "Motor 2:" }
                Label { text: "Not Ready" }

                Label { text: "Motor 3:" }
                Label { text: "Not Ready" }

                Label { text: "Motor 4:" }
                Label { text: "Not Ready" }
            }
        }

        // Sicherheits-Checkbox
        CheckBox {
            id: safetyCheckbox
            text: "I confirm that all propellers have been removed"
            checked: false
            onCheckedChanged: {
                allMotorsSlider.enabled = checked
                motor1Slider.enabled = checked
                motor2Slider.enabled = checked
                motor3Slider.enabled = checked
                motor4Slider.enabled = checked
            }
        }
    }
} 