import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: root
    property var controller: null
    
    Rectangle {
        anchors.fill: parent
        color: "#2c2c2c"
        
        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 20
            spacing: 15
            
            // Heading
            Text {
                Layout.fillWidth: true
                text: "Motor Test"
                font.pixelSize: 24
                font.bold: true
                color: "white"
            }
            
            // Description and warning
            Rectangle {
                Layout.fillWidth: true
                color: "#aa3030"
                radius: 5
                height: warningText.height + 20
                
                Text {
                    id: warningText
                    anchors.centerIn: parent
                    width: parent.width - 20
                    text: "WARNING: Remove all propellers before motor testing! Make sure that no people or objects are near the motors."
                    wrapMode: Text.WordWrap
                    color: "white"
                    font.bold: true
                    font.pixelSize: 14
                }
            }
            
            // Separator line
            Rectangle {
                Layout.fillWidth: true
                height: 1
                color: "#555555"
                Layout.topMargin: 10
                Layout.bottomMargin: 10
            }
            
            // Test mode buttons
            RowLayout {
                Layout.fillWidth: true
                spacing: 10
                
                Text {
                    text: "Test Mode:"
                    color: "white"
                    font.pixelSize: 16
                }
                
                Button {
                    text: "Single Test"
                    Layout.preferredWidth: 120
                    highlighted: true
                    onClicked: {
                        if (root.controller) {
                            root.controller.setTestMode("single");
                        }
                    }
                }
                
                Button {
                    text: "Sequence Test"
                    Layout.preferredWidth: 120
                    onClicked: {
                        if (root.controller) {
                            root.controller.setTestMode("sequence");
                        }
                    }
                }
                
                Button {
                    text: "All Motors"
                    Layout.preferredWidth: 120
                    onClicked: {
                        if (root.controller) {
                            root.controller.setTestMode("all");
                        }
                    }
                }
            }
            
            // Motors visualization
            Item {
                Layout.fillWidth: true
                Layout.preferredHeight: 300
                
                Rectangle {
                    id: motorSchematic
                    anchors.centerIn: parent
                    width: Math.min(parent.width * 0.8, 400)
                    height: width
                    color: "transparent"
                    border.color: "#555555"
                    border.width: 1
                    radius: 5
                    
                    // Drone frame
                    Rectangle {
                        anchors.centerIn: parent
                        width: parent.width * 0.7
                        height: width
                        rotation: 45
                        color: "#404040"
                        radius: 10
                    }
                    
                    // Center of the drone
                    Rectangle {
                        anchors.centerIn: parent
                        width: parent.width * 0.3
                        height: width
                        radius: width / 2
                        color: "#333333"
                        border.color: "#666666"
                        border.width: 2
                        
                        Text {
                            anchors.centerIn: parent
                            text: "RZGCS"
                            color: "#cccccc"
                            font.bold: true
                        }
                    }
                    
                    // Motor 1 (front left)
                    Rectangle {
                        id: motor1
                        width: parent.width * 0.2
                        height: width
                        x: parent.width * 0.1
                        y: parent.height * 0.1
                        radius: width / 2
                        color: "#3060ff"
                        border.color: "white"
                        border.width: 2
                        
                        Text {
                            anchors.centerIn: parent
                            text: "1"
                            color: "white"
                            font.bold: true
                            font.pixelSize: parent.width * 0.4
                        }
                        
                        MouseArea {
                            anchors.fill: parent
                            onClicked: {
                                if (root.controller) {
                                    root.controller.testMotor(1);
                                }
                            }
                        }
                    }
                    
                    // Motor 2 (vorne rechts)
                    Rectangle {
                        id: motor2
                        width: parent.width * 0.2
                        height: width
                        x: parent.width * 0.7
                        y: parent.height * 0.1
                        radius: width / 2
                        color: "#ff6030"
                        border.color: "white"
                        border.width: 2
                        
                        Text {
                            anchors.centerIn: parent
                            text: "2"
                            color: "white"
                            font.bold: true
                            font.pixelSize: parent.width * 0.4
                        }
                        
                        MouseArea {
                            anchors.fill: parent
                            onClicked: {
                                if (root.controller) {
                                    root.controller.testMotor(2);
                                }
                            }
                        }
                    }
                    
                    // Motor 3 (hinten rechts)
                    Rectangle {
                        id: motor3
                        width: parent.width * 0.2
                        height: width
                        x: parent.width * 0.7
                        y: parent.height * 0.7
                        radius: width / 2
                        color: "#60ff30"
                        border.color: "white"
                        border.width: 2
                        
                        Text {
                            anchors.centerIn: parent
                            text: "3"
                            color: "white"
                            font.bold: true
                            font.pixelSize: parent.width * 0.4
                        }
                        
                        MouseArea {
                            anchors.fill: parent
                            onClicked: {
                                if (root.controller) {
                                    root.controller.testMotor(3);
                                }
                            }
                        }
                    }
                    
                    // Motor 4 (hinten links)
                    Rectangle {
                        id: motor4
                        width: parent.width * 0.2
                        height: width
                        x: parent.width * 0.1
                        y: parent.height * 0.7
                        radius: width / 2
                        color: "#ff30a0"
                        border.color: "white"
                        border.width: 2
                        
                        Text {
                            anchors.centerIn: parent
                            text: "4"
                            color: "white"
                            font.bold: true
                            font.pixelSize: parent.width * 0.4
                        }
                        
                        MouseArea {
                            anchors.fill: parent
                            onClicked: {
                                if (root.controller) {
                                    root.controller.testMotor(4);
                                }
                            }
                        }
                    }
                    
                    // Richtungspfeil (Vorne)
                    Canvas {
                        anchors.horizontalCenter: parent.horizontalCenter
                        anchors.top: parent.top
                        anchors.topMargin: 5
                        width: 30
                        height: 40
                        
                        onPaint: {
                            var ctx = getContext("2d");
                            ctx.fillStyle = "#cccccc";
                            ctx.beginPath();
                            ctx.moveTo(width/2, 0);
                            ctx.lineTo(0, height);
                            ctx.lineTo(width, height);
                            ctx.closePath();
                            ctx.fill();
                        }
                    }
                    
                    Text {
                        anchors.horizontalCenter: parent.horizontalCenter
                        anchors.top: parent.top
                        anchors.topMargin: 45
                        color: "#cccccc"
                        text: "VORNE"
                        font.pixelSize: 12
                    }
                }
            }
            
            // Motor control sliders
            ColumnLayout {
                Layout.fillWidth: true
                Layout.preferredHeight: 120
                spacing: 5
                
                Text {
                    text: "Motorleistung: " + motorSlider.value.toFixed(0) + "%"
                    color: "white"
                    font.pixelSize: 14
                }
                
                Slider {
                    id: motorSlider
                    Layout.fillWidth: true
                    from: 0
                    to: 100
                    stepSize: 1
                    value: 30
                    
                    onValueChanged: {
                        if (root.controller) {
                            root.controller.setThrottle(value);
                        }
                    }
                }
                
                // Steuerschaltflu00e4chen
                RowLayout {
                    Layout.fillWidth: true
                    spacing: 10
                    
                    Button {
                        text: "Start Test"
                        Layout.preferredWidth: 120
                        onClicked: {
                            if (root.controller) {
                                root.controller.startTest();
                            }
                        }
                    }
                    
                    Button {
                        text: "Stop"
                        Layout.preferredWidth: 120
                        onClicked: {
                            if (root.controller) {
                                root.controller.stopTest();
                            }
                        }
                    }
                    
                    Button {
                        text: "Sicherheitscheck"
                        Layout.fillWidth: true
                        onClicked: {
                            if (root.controller) {
                                root.controller.runSafetyCheck();
                            }
                        }
                    }
                }
            }
            
            // Status und Log
            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                color: "#1a1a1a"
                border.color: "#555555"
                border.width: 1
                
                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 10
                    spacing: 5
                    
                    Text {
                        text: "Status & Log"
                        color: "white"
                        font.bold: true
                        font.pixelSize: 14
                    }
                    
                    ListView {
                        id: logView
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        clip: true
                        model: ListModel {
                            ListElement { message: "Bereit fu00fcr Motortest. Bitte stellen Sie sicher, dass alle Propeller entfernt sind." }
                            ListElement { message: "Sicherheitshinweis: Halten Sie wu00e4hrend des Tests einen Sicherheitsabstand zur Drohne ein." }
                        }
                        delegate: Rectangle {
                            width: ListView.view.width
                            height: logText.height + 10
                            color: index % 2 == 0 ? "#2a2a2a" : "#252525"
                            
                            Text {
                                id: logText
                                text: model.message
                                color: "#cccccc"
                                font.pixelSize: 12
                                width: parent.width - 10
                                wrapMode: Text.WordWrap
                                anchors.centerIn: parent
                            }
                        }
                    }
                }
            }
        }
    }
}
