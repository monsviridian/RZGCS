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
                height: warningText.height + 30
                border.color: "#ff5555"
                border.width: 2
                
                Text {
                    id: warningText
                    anchors.centerIn: parent
                    width: parent.width - 20
                    text: "⚠️ WARNUNG: Entfernen Sie alle Propeller vor dem Motortest! Stellen Sie sicher, dass keine Personen oder Gegenstände in der Nähe der Motoren sind."
                    wrapMode: Text.WordWrap
                    color: "white"
                    font.bold: true
                    font.pixelSize: 16
                    horizontalAlignment: Text.AlignHCenter
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
                        property bool isActive: false
                        
                        // Propeller visualization
                        Rectangle {
                            id: propeller1
                            anchors.centerIn: parent
                            width: parent.width * 0.6
                            height: width * 0.1
                            color: "#dddddd"
                            antialiasing: true
                            transformOrigin: Item.Center
                            rotation: 0
                        }
                        
                        Rectangle {
                            anchors.centerIn: parent
                            width: propeller1.height
                            height: propeller1.width
                            color: propeller1.color
                            antialiasing: true
                            transformOrigin: Item.Center
                            rotation: 90
                        }
                        
                        // Rotation animation
                        RotationAnimation {
                            id: rotationAnim1
                            target: propeller1
                            property: "rotation"
                            from: propeller1.rotation
                            to: propeller1.rotation + 360
                            duration: 1000 / (motorSlider.value / 10 + 0.1) // Faster rotation with higher throttle
                            loops: Animation.Infinite
                            running: motor1.isActive
                        }
                        
                        Text {
                            anchors.centerIn: parent
                            text: "1"
                            color: "white"
                            font.bold: true
                            font.pixelSize: parent.width * 0.4
                            z: 2 // Make sure text is above propeller
                        }
                        
                        MouseArea {
                            anchors.fill: parent
                            onClicked: {
                                if (root.controller) {
                                    motor1.isActive = !motor1.isActive;
                                    if (motor1.isActive) {
                                        root.controller.testMotor(1);
                                    } else {
                                        root.controller.stopTest();
                                    }
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
                        property bool isActive: false
                        
                        // Propeller visualization
                        Rectangle {
                            id: propeller2
                            anchors.centerIn: parent
                            width: parent.width * 0.6
                            height: width * 0.1
                            color: "#dddddd"
                            antialiasing: true
                            transformOrigin: Item.Center
                            rotation: 0
                        }
                        
                        Rectangle {
                            anchors.centerIn: parent
                            width: propeller2.height
                            height: propeller2.width
                            color: propeller2.color
                            antialiasing: true
                            transformOrigin: Item.Center
                            rotation: 90
                        }
                        
                        // Rotation animation
                        RotationAnimation {
                            id: rotationAnim2
                            target: propeller2
                            property: "rotation"
                            from: propeller2.rotation
                            to: propeller2.rotation + 360
                            duration: 1000 / (motorSlider.value / 10 + 0.1) // Faster rotation with higher throttle
                            loops: Animation.Infinite
                            running: motor2.isActive
                        }
                        
                        Text {
                            anchors.centerIn: parent
                            text: "2"
                            color: "white"
                            font.bold: true
                            font.pixelSize: parent.width * 0.4
                            z: 2 // Make sure text is above propeller
                        }
                        
                        MouseArea {
                            anchors.fill: parent
                            onClicked: {
                                if (root.controller) {
                                    motor2.isActive = !motor2.isActive;
                                    if (motor2.isActive) {
                                        root.controller.testMotor(2);
                                    } else {
                                        root.controller.stopTest();
                                    }
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
                        property bool isActive: false
                        
                        // Propeller visualization
                        Rectangle {
                            id: propeller3
                            anchors.centerIn: parent
                            width: parent.width * 0.6
                            height: width * 0.1
                            color: "#dddddd"
                            antialiasing: true
                            transformOrigin: Item.Center
                            rotation: 0
                        }
                        
                        Rectangle {
                            anchors.centerIn: parent
                            width: propeller3.height
                            height: propeller3.width
                            color: propeller3.color
                            antialiasing: true
                            transformOrigin: Item.Center
                            rotation: 90
                        }
                        
                        // Rotation animation
                        RotationAnimation {
                            id: rotationAnim3
                            target: propeller3
                            property: "rotation"
                            from: propeller3.rotation
                            to: propeller3.rotation + 360
                            duration: 1000 / (motorSlider.value / 10 + 0.1) // Faster rotation with higher throttle
                            loops: Animation.Infinite
                            running: motor3.isActive
                        }
                        
                        Text {
                            anchors.centerIn: parent
                            text: "3"
                            color: "white"
                            font.bold: true
                            font.pixelSize: parent.width * 0.4
                            z: 2 // Make sure text is above propeller
                        }
                        
                        MouseArea {
                            anchors.fill: parent
                            onClicked: {
                                if (root.controller) {
                                    motor3.isActive = !motor3.isActive;
                                    if (motor3.isActive) {
                                        root.controller.testMotor(3);
                                    } else {
                                        root.controller.stopTest();
                                    }
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
                        property bool isActive: false
                        
                        // Propeller visualization
                        Rectangle {
                            id: propeller4
                            anchors.centerIn: parent
                            width: parent.width * 0.6
                            height: width * 0.1
                            color: "#dddddd"
                            antialiasing: true
                            transformOrigin: Item.Center
                            rotation: 0
                        }
                        
                        Rectangle {
                            anchors.centerIn: parent
                            width: propeller4.height
                            height: propeller4.width
                            color: propeller4.color
                            antialiasing: true
                            transformOrigin: Item.Center
                            rotation: 90
                        }
                        
                        // Rotation animation
                        RotationAnimation {
                            id: rotationAnim4
                            target: propeller4
                            property: "rotation"
                            from: propeller4.rotation
                            to: propeller4.rotation + 360
                            duration: 1000 / (motorSlider.value / 10 + 0.1) // Faster rotation with higher throttle
                            loops: Animation.Infinite
                            running: motor4.isActive
                        }
                        
                        Text {
                            anchors.centerIn: parent
                            text: "4"
                            color: "white"
                            font.bold: true
                            font.pixelSize: parent.width * 0.4
                            z: 2 // Make sure text is above propeller
                        }
                        
                        MouseArea {
                            anchors.fill: parent
                            onClicked: {
                                if (root.controller) {
                                    motor4.isActive = !motor4.isActive;
                                    if (motor4.isActive) {
                                        root.controller.testMotor(4);
                                    } else {
                                        root.controller.stopTest();
                                    }
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
                        
                        onPaint: function() {
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
                    font.bold: true
                }
                
                Slider {
                    id: motorSlider
                    Layout.fillWidth: true
                    from: 0
                    to: 100
                    stepSize: 1
                    value: 30
                    
                    onValueChanged: function() {
                        if (root.controller) {
                            root.controller.setThrottle(value);
                            
                            // Update animation speed for all active motors
                            if (rotationAnim1) rotationAnim1.duration = 1000 / (value / 10 + 0.1);
                            if (rotationAnim2) rotationAnim2.duration = 1000 / (value / 10 + 0.1);
                            if (rotationAnim3) rotationAnim3.duration = 1000 / (value / 10 + 0.1);
                            if (rotationAnim4) rotationAnim4.duration = 1000 / (value / 10 + 0.1);
                        }
                    }
                }
                
                // Control buttons
                RowLayout {
                    Layout.fillWidth: true
                    spacing: 20
                    
                    Button {
                        text: "Start Test"
                        Layout.preferredWidth: 120
                        
                        onClicked: function() {
                            if (root.controller) {
                                root.controller.startTest();
                                // Reset motor active states
                                motor1.isActive = false;
                                motor2.isActive = false;
                                motor3.isActive = false;
                                motor4.isActive = false;
                            }
                        }
                    }
                    
                    Button {
                        text: "Stop Test"
                        Layout.preferredWidth: 120
                        
                        onClicked: function() {
                            if (root.controller) {
                                root.controller.stopTest();
                                // Reset motor active states
                                motor1.isActive = false;
                                motor2.isActive = false;
                                motor3.isActive = false;
                                motor4.isActive = false;
                            }
                        }
                    }
                    
                    Button {
                        text: "Sicherheitscheck"
                        Layout.preferredWidth: 140
                        
                        onClicked: function() {
                            if (root.controller) {
                                root.controller.runSafetyCheck();
                            }
                        }
                    }
                }
            }
            
            // Status and Log
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
                    
                    Rectangle {
                        Layout.fillWidth: true
                        height: 24
                        color: "#333333"
                        radius: 3
                        
                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: 4
                            
                            Text {
                                id: statusLabel
                                text: "Bereit"
                                color: "#cccccc"
                                Layout.fillWidth: true
                            }
                            
                            ProgressBar {
                                id: testProgressBar
                                value: 0.0
                                Layout.preferredWidth: 100
                            }
                        }
                    }
                    
                    ListView {
                        id: logView
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        clip: true
                        model: ListModel {
                            ListElement { message: "Bereit für Motortest. Bitte stellen Sie sicher, dass alle Propeller entfernt sind." }
                            ListElement { message: "Sicherheitshinweis: Halten Sie während des Tests einen Sicherheitsabstand zur Drohne ein." }
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
    
    Connections {
        target: root.controller
        function onMotorStatusChanged(motorNumber, isRunning, statusText) {
            // Update UI based on motor status
            console.log("Motor " + motorNumber + " status: " + statusText);
            
            // Update the motor active state
            if (motorNumber === 1) motor1.isActive = isRunning;
            if (motorNumber === 2) motor2.isActive = isRunning;
            if (motorNumber === 3) motor3.isActive = isRunning;
            if (motorNumber === 4) motor4.isActive = isRunning;
        }
        
        function onLogMessageAdded(message) {
            // Add message to log model
            logView.model.append({message: message});
        }
        
        function onTestProgressChanged(progress, status) {
            testProgressBar.value = progress / 100;
            statusLabel.text = status;
        }
        
        function onTestFinished(success, message) {
            testProgressBar.value = 0;
            statusLabel.text = message;
            
            // Reset all motor active states
            motor1.isActive = false;
            motor2.isActive = false;
            motor3.isActive = false;
            motor4.isActive = false;
        }
    }
}
