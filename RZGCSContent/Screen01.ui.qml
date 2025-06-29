/*
This is a UI file (.ui.qml) that is intended to be edited in Qt Design Studio only.
It is supposed to be strictly declarative and only uses a subset of QML. If you edit
this file manually, you might introduce QML code that is not supported by Qt Design Studio.
Check out https://doc.qt.io/qtcreator/creator-quick-ui-forms.html for details on .ui.qml files.
*/
import QtQuick 2.15
import QtQuick.Controls.Material 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Window 2.15

// Lokale Komponenten importieren
import "./" as RZGCS
import "./Connection/" as Connection

Item {
    id: root
    width: 800
    height: 600


    // Schwarzer Hintergrund
    Rectangle {
        anchors.fill: parent
        color: "black"
        z: -1  // Hinter allen Elementen
    }

    // Toast Notification Container
    Item {
        id: toastContainer
        anchors.top: parent.top
        anchors.right: parent.right
        anchors.margins: 20
        z: 1000
    }

    // Ensure serialConnector is available
    Component.onCompleted: {
        // WICHTIG: Context Property dem QML-Property zuweisen
        if (typeof messageManager !== 'undefined') {
            // Assign the context property to our local property
            root.messageManager = messageManager;
            console.log("D: QML messageManager successfully assigned from context property:", root.messageManager)
            
            // Test-Message senden zur Bestätigung
            root.messageManager.addMessage("QML MessageManager successfully initialized", 4)
        } else {
            console.log("W: messageManager context property is not available")
        }
        
        console.log("D: QML messageManager:", root.messageManager)
        console.log("D: QML serialConnector:", serialConnector)
        if (serialConnector)
            console.log("D: serialConnector.isConnected:", serialConnector.isConnected)
        if (root.messageManager && root.messageManager.messages)
            console.log("D: messageManager.messages.length:", root.messageManager.messages.length)
        else
            console.log("W: messageManager.messages ist nicht verfügbar")
        
        if (serialConnector) {
            serialConnector.load_ports()
            if (root.messageManager)
                root.messageManager.addMessage("Application started", 1)
            showToast("RZGCS started successfully", 1) // Success
        }
        
        // Connect serialConnector signals to message manager
        if (serialConnector) {
            serialConnector.connectedChanged.connect(function() {
                var status = serialConnector.isConnected ? "Connected" : "Disconnected"
                if (messageManager)
                    messageManager.updateConnectionStatus(serialConnector.isConnected, status)
                
                // Show toast for connection changes
                if (serialConnector.isConnected) {
                    showToast("Connected to vehicle", 1) // Success
                    
                    // Load parameters after successful connection if on parameter tab
                    if (parameterViewModel && tabBar.currentIndex === 2) {
                        parameterViewModel.refreshParameters()
                    }
                } else {
                    showToast("Disconnected from vehicle", 2) // Warning
                }
            })
        }
    }
    
    // Function to show toast notification
    function showToast(message, type) {
        var toast = Qt.createComponent("ToastNotification.qml").createObject(toastContainer, {
            message: message,
            type: type,
            duration: type === 3 ? 5000 : 3000 // Longer duration for errors
        })
        
        // Position the toast
        toast.x = toastContainer.width - toast.width
        
        // Show the toast
        toast.show()
        
        // Clean up after animation
        toast.hideAnimation.finished.connect(function() {
            toast.destroy()
        })
    }

    // Hauptlayout: Status Bar oben, Content unten
    ColumnLayout {
        anchors.fill: parent
        spacing: 5

        // Verbindungskontrolle oben
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
                    onCurrentIndexChanged: {
                        if (serialConnector && currentIndex >= 0 && currentText !== "") {
                            serialConnector.setPort(currentText)
                        }
                    }
                    
                    // Style the ComboBox
                    background: Rectangle {
                        color: "black"
                        border.color: "gray"
                        border.width: 1
                        radius: 2
                    }
                    
                    contentItem: Text {
                        text: portComboBox.displayText
                        color: "white"
                        verticalAlignment: Text.AlignVCenter
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
                            elide: Text.ElideRight
                            verticalAlignment: Text.AlignVCenter
                        }
                        background: Rectangle {
                            color: highlighted ? "gray" : "black"
                        }
                        highlighted: portComboBox.highlightedIndex === index
                    }
                }

                ComboBox {
                    id: baudComboBox
                    model: serialConnector ? serialConnector.availableBaudRates : []
                    currentIndex: 4  // 115200
                    Layout.preferredWidth: 100
                    
                    // Style the ComboBox
                    background: Rectangle {
                        color: "black"
                        border.color: "gray"
                        border.width: 1
                        radius: 2
                    }
                    
                    contentItem: Text {
                        text: baudComboBox.displayText
                        color: "white"
                        verticalAlignment: Text.AlignVCenter
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
                            elide: Text.ElideRight
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
                    text: serialConnector && serialConnector.isConnected ? "Disconnect" : "Connect"
                    Layout.preferredWidth: 80
                    background: Rectangle {
                        color: "black"
                        border.color: "gray"
                        border.width: 1
                        radius: 2
                    }
                    contentItem: Text {
                        text: parent.text
                        color: "white"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                    onClicked: {
                        if (serialConnector) {
                            if (serialConnector.isConnected) {
                                serialConnector.disconnect()
                            } else {
                                if (portComboBox.currentText !== "") {
                                    console.log("Connecting to: " + portComboBox.currentText)
                                    serialConnector.connect()
                                } else {
                                    showToast("Please select a port first", 2) // Warning
                                }
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
                        radius: 2
                    }
                    contentItem: Text {
                        text: parent.text
                        color: "white"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                    onClicked: {
                        if (serialConnector) {
                            serialConnector.load_ports()
                        }
                    }
                }
            }
        }

        // Tab-Leiste
        TabBar {
            id: tabBar
            Layout.fillWidth: true
            
            // Tab für den Connection View
            TabButton {
                text: "Connection"
                width: implicitWidth
                
                background: Rectangle {
                    color: tabBar.currentIndex === 0 ? "#303030" : "#202020"
                    Rectangle {
                        width: parent.width
                        height: 2
                        anchors.bottom: parent.bottom
                        color: tabBar.currentIndex === 0 ? "#0078d7" : "transparent"
                    }
                }
                
                contentItem: Text {
                    text: parent.text
                    color: "white"
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
            }
            
            // Tab für Preflight Check
            TabButton {
                text: "Preflight Check"
                width: implicitWidth
                
                background: Rectangle {
                    color: tabBar.currentIndex === 1 ? "#303030" : "#202020"
                    Rectangle {
                        width: parent.width
                        height: 2
                        anchors.bottom: parent.bottom
                        color: tabBar.currentIndex === 1 ? "#0078d7" : "transparent"
                    }
                }
                
                contentItem: Text {
                    text: parent.text
                    color: "white"
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
            }

            // Tab für Parameter
            TabButton {
                text: "Parameter"
                width: implicitWidth
                
                background: Rectangle {
                    color: tabBar.currentIndex === 2 ? "#303030" : "#202020"
                    Rectangle {
                        width: parent.width
                        height: 2
                        anchors.bottom: parent.bottom
                        color: tabBar.currentIndex === 2 ? "#0078d7" : "transparent"
                    }
                }
                
                contentItem: Text {
                    text: parent.text
                    color: "white"
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
                
                onClicked: {
                    // Lade Parameter beim Wechsel zum Parameter-Tab, wenn verbunden
                    if (serialConnector && serialConnector.connected && parameterViewModel) {
                        parameterViewModel.refreshParameters()
                    }
                }
            }
            
            // Tab für Kalibrierung
            TabButton {
                text: "Calibration"
                width: implicitWidth
                
                background: Rectangle {
                    color: tabBar.currentIndex === 3 ? "#303030" : "#202020"
                    Rectangle {
                        width: parent.width
                        height: 2
                        anchors.bottom: parent.bottom
                        color: tabBar.currentIndex === 3 ? "#0078d7" : "transparent"
                    }
                }
                
                contentItem: Text {
                    text: parent.text
                    color: "white"
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
            }
            
            // Tab für Motor Test
            TabButton {
                text: "Motor Test"
                width: implicitWidth
                
                background: Rectangle {
                    color: tabBar.currentIndex === 4 ? "#303030" : "#202020"
                    Rectangle {
                        width: parent.width
                        height: 2
                        anchors.bottom: parent.bottom
                        color: tabBar.currentIndex === 4 ? "#0078d7" : "transparent"
                    }
                }
                
                contentItem: Text {
                    text: parent.text
                    color: "white"
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
            }
            
            // Tab für Flight (Mission Planner)
            TabButton {
                text: "Flight"
                width: implicitWidth
                
                background: Rectangle {
                    color: tabBar.currentIndex === 5 ? "#303030" : "#202020"
                    Rectangle {
                        width: parent.width
                        height: 2
                        anchors.bottom: parent.bottom
                        color: tabBar.currentIndex === 5 ? "#0078d7" : "transparent"
                    }
                }
                
                contentItem: Text {
                    text: parent.text
                    color: "white"
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
            }
        }

        // Hauptbereich: Content links, Messages rechts
        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 10

            // Content-Bereich
            StackLayout {
                id: contentStack
                Layout.fillWidth: true
                Layout.fillHeight: true
                currentIndex: tabBar.currentIndex

                // ConnectionView (umbenannter PreflightView)
                RZGCS.PreflightView {
                    id: connectionView
                    
                    // Deaktiviere StatusBar in ConnectionView
                    Component.onCompleted: {
                        for (var i = 0; i < connectionView.children.length; i++) {
                            var child = connectionView.children[i]
                            if (child.objectName === "statusBar") {
                                child.visible = false
                                child.height = 0
                            }
                        }
                    }
                }

                // PreflightCheckView (neu)
                Rectangle {
                    id: preflightCheckView
                    color: "#1e1e1e"
                    
                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 15
                        spacing: 10
                        
                        Text {
                            text: "Preflight Check"
                            color: "white"
                            font.pixelSize: 20
                            font.bold: true
                        }
                        
                        // Preflight Check Checkliste
                        ListView {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            spacing: 5
                            model: ListModel {
                                ListElement { name: "Batterie-Status"; checked: false }
                                ListElement { name: "GPS-Signal"; checked: false }
                                ListElement { name: "Kompass kalibriert"; checked: false }
                                ListElement { name: "Gyro kalibriert"; checked: false }
                                ListElement { name: "RC-Verbindung"; checked: false }
                                ListElement { name: "Motoren getestet"; checked: false }
                                ListElement { name: "Flight Mode geprüft"; checked: false }
                                ListElement { name: "Notfall-Prozeduren überprüft"; checked: false }
                            }
                            delegate: RowLayout {
                                width: parent.width
                                height: 40
                                spacing: 10
                                
                                CheckBox {
                                    checked: model.checked
                                    onCheckedChanged: model.checked = checked
                                    indicator: Rectangle {
                                        width: 20
                                        height: 20
                                        border.color: "white"
                                        color: "transparent"
                                        Text {
                                            anchors.centerIn: parent
                                            text: "✓"
                                            color: "white"
                                            visible: parent.parent.checked
                                        }
                                    }
                                }
                                
                                Text {
                                    text: model.name
                                    color: "white"
                                    font.pixelSize: 16
                                }
                            }
                        }
                    }
                }
                
                // ParameterView
                RZGCS.ParameterView {
                    id: parameterView
                }
                
                // CalibrationView
                RZGCS.CalibrationView {
                    id: calibrationView
                }
                
                // MotorTestView
                RZGCS.MotorTestView {
                    id: motorTestView
                }
                
                // FlightView (Mission Planner)
                RZGCS.FlightView {
                    id: flightView
                    
                    // Verbinde mit dem flightViewController
                    Component.onCompleted: {
                        console.log("FlightView initialisiert")
                        if (typeof flightViewController !== 'undefined') {
                            console.log("FlightViewController gefunden!")
                        }
                    }
                }
            }
            
            // Rechter Message-Panel (immer sichtbar)
            MessageList {
                id: messageList
                Layout.preferredWidth: 300
                Layout.fillHeight: true
            }
        }
    }
}
