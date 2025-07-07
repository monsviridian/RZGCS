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
    width: 1200
    height: 800
    
    // Properties für ViewModels
    property var firmwareViewModel


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
        
        // FirmwareViewModel zuweisen
        if (typeof firmwareViewModel !== 'undefined') {
            root.firmwareViewModel = firmwareViewModel;
            console.log("D: QML firmwareViewModel successfully assigned from context property:", root.firmwareViewModel)
        } else {
            console.log("W: firmwareViewModel context property is not available")
        }
        
        // Zusätzliche Prüfung für firmwareViewModel
        if (typeof firmwareViewModel !== 'undefined') {
            console.log("D: firmwareViewModel context property gefunden:", firmwareViewModel)
            console.log("D: firmwareViewModel.available_ports:", firmwareViewModel.available_ports)
        } else {
            console.log("W: firmwareViewModel context property nicht gefunden")
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
            
            // Connect error signals
            serialConnector.errorOccurred.connect(function(errorMessage) {
                console.log("D: SerialConnector error:", errorMessage)
                showToast("Connection error: " + errorMessage, 3) // Error
                if (messageManager) {
                    messageManager.addMessage("Connection error: " + errorMessage, 3)
                }
            })
            
            // Connect status change signals
            serialConnector.connectionStatusChanged.connect(function(status) {
                console.log("D: Connection status changed:", status)
                var statusText = ""
                switch(status) {
                    case 0: statusText = "Disconnected"; break
                    case 1: statusText = "Connecting..."; break
                    case 2: statusText = "Connected"; break
                    case 3: statusText = "Error"; break
                    default: statusText = "Unknown"; break
                }
                if (messageManager) {
                    messageManager.addMessage("Connection status: " + statusText, 1)
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
                    Layout.preferredWidth: 350  // Increased width to show descriptions
                    
                    // Add tooltip to show full description
                    ToolTip.visible: hovered
                    ToolTip.text: currentText || "Select a port"
                    ToolTip.delay: 500
                    
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
                        elide: Text.ElideRight  // Show ellipsis if text is too long
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
                            font.pointSize: 9  // Slightly smaller font to fit more text
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
                                    
                                    // Set the port before connecting
                                    serialConnector.setPort(portComboBox.currentText)
                                    
                                    // Try to connect
                                    var success = serialConnector.connect()
                                    
                                    if (!success) {
                                        showToast("Connection failed - check if device is connected and port is available", 3) // Error
                                    }
                                } else {
                                    showToast("Please select a port first", 2) // Warning
                                }
                            }
                        } else {
                            showToast("Serial connector not available", 3) // Error
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
                
                // Status label showing selected port
                Label {
                    text: portComboBox.currentText ? "Selected: " + portComboBox.currentText : "No port selected"
                    color: "white"
                    font.pointSize: 8
                    Layout.fillWidth: true
                    elide: Text.ElideRight
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
            
            // NEW: MAVLink 2 Tab (second tab)
            TabButton {
                text: "MAVLink 2"
                width: implicitWidth
                background: Rectangle {
                    color: tabBar.currentIndex === 1 ? "#303030" : "#202020"
                    Rectangle {
                        width: parent.width
                        height: 2
                        anchors.bottom: parent.bottom
                        color: tabBar.currentIndex === 1 ? "#00e0c6" : "transparent"
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
            }

            // Tab für Parameter
            TabButton {
                text: "Parameter"
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
            
            // Tab für Motor Test
            TabButton {
                text: "Motor Test"
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
            
            // Tab für Firmware
            TabButton {
                text: "Firmware"
                width: implicitWidth
                background: Rectangle {
                    color: tabBar.currentIndex === 6 ? "#303030" : "#202020"
                    Rectangle {
                        width: parent.width
                        height: 2
                        anchors.bottom: parent.bottom
                        color: tabBar.currentIndex === 6 ? "#0078d7" : "transparent"
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
                    color: tabBar.currentIndex === 7 ? "#303030" : "#202020"
                    Rectangle {
                        width: parent.width
                        height: 2
                        anchors.bottom: parent.bottom
                        color: tabBar.currentIndex === 7 ? "#0078d7" : "transparent"
                    }
                }
                
                contentItem: Text {
                    text: parent.text
                    color: "white"
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
            }
            
            // Tab für Sensor Dashboard
            TabButton {
                text: "Sensor Dashboard"
                width: implicitWidth
                
                background: Rectangle {
                    color: tabBar.currentIndex === 8 ? "#303030" : "#202020"
                    Rectangle {
                        width: parent.width
                        height: 2
                        anchors.bottom: parent.bottom
                        color: tabBar.currentIndex === 8 ? "#0078d7" : "transparent"
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
                PreflightView {
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

                // NEW: MAVLink2Tab (index 1)
                Loader {
                    id: mavlink2TabLoader
                    source: "MAVLink2Tab.qml"
                    visible: tabBar.currentIndex === 1
                    onLoaded: {
                        if (mavlink2TabLoader.item) {
                            if (typeof protocolConnectionManager !== "undefined")
                                mavlink2TabLoader.item.protocolConnectionManager = protocolConnectionManager
                            if (typeof mavlinkV2Backend !== "undefined")
                                mavlink2TabLoader.item.mavlinkV2Backend = mavlinkV2Backend
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
                
                // ParameterTab (neue UI)
                ParameterTab {
                    id: parameterTab
                }
                
                // CalibrationView
                CalibrationView {
                    id: calibrationView
                }
                
                // MotorTestView
                MotorTestView {
                    id: motorTestView
                }
                
                // FirmwareView
                Loader {
                    id: firmwareTabLoader
                    source: "FirmwareView.ui.qml"
                    visible: tabBar.currentIndex === 6
                    width: 900
                    height: 700
                    
                    // Übergebe das firmwareViewModel an die geladene Komponente
                    onLoaded: {
                        if (firmwareTabLoader.item && root.firmwareViewModel) {
                            firmwareTabLoader.item.firmwareViewModel = root.firmwareViewModel
                            console.log("D: FirmwareViewModel an FirmwareView übergeben:", root.firmwareViewModel)
                        } else {
                            console.log("W: FirmwareViewModel nicht verfügbar für FirmwareView")
                        }
                    }
                }
                
                // FlightView (Mission Planner)
                FlightView {
                    id: flightView
                    
                    // Verbinde mit dem flightViewController
                    Component.onCompleted: {
                        console.log("FlightView initialisiert")
                        if (typeof flightViewController !== 'undefined') {
                            console.log("FlightViewController gefunden!")
                        }
                    }
                }
                
                // SensorDashboardTab
                SensorDashboardTab {
                    id: sensorDashboardTab
                }
            }
            
            // Rechter Message-Panel (immer sichtbar)
            MessageList {
                id: messageList
                Layout.preferredWidth: 300
                Layout.minimumWidth: 200
                Layout.maximumWidth: 400
                Layout.fillHeight: true
            }
        }
    }
}
