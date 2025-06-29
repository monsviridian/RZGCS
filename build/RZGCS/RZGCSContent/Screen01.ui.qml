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

    // Instanziiere FirmwareViewModel direkt
    property var firmwareViewModel: FirmwareViewModel {}
    
    // Message Manager
    property var messageManager: MessageManager {}

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
        if (serialConnector) {
            serialConnector.load_ports()
            messageManager.addMessage("Application started", MessageManager.MessageType.Info)
            showToast("RZGCS started successfully", 1) // Success
        }
        
        // Connect serialConnector signals to message manager
        if (serialConnector) {
            serialConnector.connectedChanged.connect(function() {
                var status = serialConnector.connected ? "Connected" : "Disconnected"
                messageManager.updateConnectionStatus(serialConnector.connected, status)
                
                // Show toast for connection changes
                if (serialConnector.connected) {
                    showToast("Connected to vehicle", 1) // Success
                } else {
                    showToast("Disconnected from vehicle", 2) // Warning
                }
            })
        }
        
        // Connect message manager signals to show toasts for important messages
        messageManager.messageAdded.connect(function(message, type) {
            // Show toast for warnings and errors
            if (type === MessageManager.MessageType.Warning || type === MessageManager.MessageType.Error) {
                showToast(message, type)
            }
        })
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

    ColumnLayout {
        anchors.fill: parent
        spacing: 5

        // Status Bar
        StatusBar {
            Layout.fillWidth: true
            messageManager: root.messageManager
        }

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
                    onCurrentIndexChanged: {
                        if (serialConnector && currentIndex >= 0 && model.length > 0) {
                            var selectedPort = model[currentIndex]
                            console.log("Port selected: " + selectedPort)
                            serialConnector.setPort(selectedPort)
                            messageManager.addMessage("Port selected: " + selectedPort, MessageManager.MessageType.Info)
                        }
                    }
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
                    
                    // Add tooltip to show when no ports are available
                    ToolTip.visible: model.length <= 1
                    ToolTip.text: "No serial ports found. Please check your device connection and drivers."
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
                    }
                    onClicked: {
                        if (serialConnector) {
                            if (serialConnector.connected) {
                                serialConnector.disconnect()
                                messageManager.addMessage("Disconnecting...", MessageManager.MessageType.Info)
                            } else {
                                // Verwende establish_serial_connection mit dem ausgewählten Port
                                var port = portComboBox.currentText
                                if (port) {
                                    messageManager.addMessage("Connecting to " + port + "...", MessageManager.MessageType.Info)
                                    serialConnector.establish_serial_connection(port)
                                } else {
                                    messageManager.addMessage("No port selected", MessageManager.MessageType.Warning)
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
                            console.log("Refreshing ports...")
                            messageManager.addMessage("Refreshing available ports...", MessageManager.MessageType.Info)
                            serialConnector.load_ports()
                        }
                    }
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
                            messageManager.addMessage("Setting flight mode: " + currentText, MessageManager.MessageType.Info)
                            showToast("Flight mode: " + currentText, 0) // Info
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
                            messageManager.addMessage("Arming vehicle...", MessageManager.MessageType.Warning)
                            showToast("⚠ Arming vehicle - Remove all obstacles!", 2) // Warning
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
                            messageManager.addMessage("Disarming vehicle...", MessageManager.MessageType.Warning)
                            showToast("Disarming vehicle", 2) // Warning
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
                            messageManager.addMessage("Exited fullscreen mode", MessageManager.MessageType.Info)
                        } else {
                            window.showFullScreen()
                            messageManager.addMessage("Entered fullscreen mode", MessageManager.MessageType.Info)
                        }
                    }
                }
            }
        }

        // Main content area
        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 5

            // Tab content area
            ColumnLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                spacing: 5

                // Tab bar
                TabBar {
                    background: Rectangle {
                        color: "black"
                    }
                    id: tabBar
                    Layout.fillWidth: true
                    currentIndex: 0
                    position: TabBar.Footer
                    
                    // TabButtons mit Hover-Effekt
                    
                    TabButton {
                        id: tabButton_preflight
                        text: "Preflight"
                        Material.foreground: "white"
                        
                        // Hover-Status manuell verwalten
                        property bool isHovered: false
                        
                        HoverHandler {
                            onHoveredChanged: tabButton_preflight.isHovered = hovered
                        }
                        
                        background: Rectangle {
                            implicitWidth: 100
                            implicitHeight: 40
                            color: parent.checked ? "#303030" : (parent.isHovered ? "#404040" : "#2C2C2C")
                            border.color: "gray"
                            border.width: parent.checked ? 1 : 0
                            
                            // Sanfter Übergangseffekt für Farben
                            Behavior on color {
                                ColorAnimation { duration: 150 }
                            }
                        }
                    }
                    TabButton {
                        id: tabButton_parameters
                        text: "Parameters"
                        Material.foreground: "white"
                        
                        // Hover-Status manuell verwalten
                        property bool isHovered: false
                        
                        HoverHandler {
                            onHoveredChanged: tabButton_parameters.isHovered = hovered
                        }
                        
                        background: Rectangle {
                            implicitWidth: 100
                            implicitHeight: 40
                            color: parent.checked ? "#303030" : (parent.isHovered ? "#404040" : "#2C2C2C")
                            border.color: "gray"
                            border.width: parent.checked ? 1 : 0
                            
                            // Sanfter Übergangseffekt für Farben
                            Behavior on color {
                                ColorAnimation { duration: 150 }
                            }
                        }
                    }
                    TabButton {
                        id: tabButton_sensors
                        text: "Sensors"
                        Material.foreground: "white"
                        
                        // Hover-Status manuell verwalten
                        property bool isHovered: false
                        
                        HoverHandler {
                            onHoveredChanged: tabButton_sensors.isHovered = hovered
                        }
                        
                        background: Rectangle {
                            implicitWidth: 100
                            implicitHeight: 40
                            color: parent.checked ? "#303030" : (parent.isHovered ? "#404040" : "#2C2C2C")
                            border.color: "gray"
                            border.width: parent.checked ? 1 : 0
                            
                            // Sanfter Übergangseffekt für Farben
                            Behavior on color {
                                ColorAnimation { duration: 150 }
                            }
                        }
                    }
                    TabButton {
                        id: tabButton_sensorDashboard
                        text: "Sensor Dashboard"
                        Material.foreground: "white"
                    }
                    TabButton {
                        id: tabButton_calibration
                        text: "Calibration"
                        Material.foreground: "white"
                        
                        // Hover-Status manuell verwalten
                        property bool isHovered: false
                        
                        HoverHandler {
                            onHoveredChanged: tabButton_calibration.isHovered = hovered
                        }
                        
                        background: Rectangle {
                            implicitWidth: 100
                            implicitHeight: 40
                            color: parent.checked ? "#303030" : (parent.isHovered ? "#404040" : "#2C2C2C")
                            border.color: "gray"
                            border.width: parent.checked ? 1 : 0
                            
                            // Sanfter Übergangseffekt für Farben
                            Behavior on color {
                                ColorAnimation { duration: 150 }
                            }
                        }
                    }
                    TabButton {
                        id: tabButton_motorTest
                        text: "Motor Test"
                        Material.foreground: "white"
                        
                        // Hover-Status manuell verwalten
                        property bool isHovered: false
                        
                        HoverHandler {
                            onHoveredChanged: tabButton_motorTest.isHovered = hovered
                        }
                        
                        background: Rectangle {
                            implicitWidth: 100
                            implicitHeight: 40
                            color: parent.checked ? "#303030" : (parent.isHovered ? "#404040" : "#2C2C2C")
                            border.color: "gray"
                            border.width: parent.checked ? 1 : 0
                            
                            // Sanfter Übergangseffekt für Farben
                            Behavior on color {
                                ColorAnimation { duration: 150 }
                            }
                        }
                    }
                    TabButton {
                        id: tabButton_flight
                        text: "Flight"
                        Material.foreground: "white"
                        
                        // Hover-Status manuell verwalten
                        property bool isHovered: false
                        
                        HoverHandler {
                            onHoveredChanged: tabButton_flight.isHovered = hovered
                        }
                        
                        background: Rectangle {
                            implicitWidth: 100
                            implicitHeight: 40
                            color: parent.checked ? "#303030" : (parent.isHovered ? "#404040" : "#2C2C2C")
                            border.color: "gray"
                            border.width: parent.checked ? 1 : 0
                            
                            // Sanfter Übergangseffekt für Farben
                            Behavior on color {
                                ColorAnimation { duration: 150 }
                            }
                        }
                    }
                    TabButton {
                        id: tabButton_angelMode
                        text: "Angel Mode"
                        Material.foreground: "white"
                        
                        background: Rectangle {
                            implicitWidth: 100
                            implicitHeight: 40
                            color: parent.checked ? "#303030" : "#2C2C2C"
                            border.color: "gray"
                            border.width: parent.checked ? 1 : 0
                            
                            // HoverHandler für Hover-Effekte
                            HoverHandler {
                                onHoveredChanged: if (hovered) parent.color = "#404040"; else parent.color = parent.parent.checked ? "#303030" : "#2C2C2C"
                            }
                            
                            // Sanfter Übergangseffekt für Farben
                            Behavior on color {
                                ColorAnimation { duration: 150 }
                            }
                        }
                    }
                    TabButton {
                        id: tabButton_license
                        text: "License"
                        Material.foreground: "white"
                        
                        background: Rectangle {
                            implicitWidth: 100
                            implicitHeight: 40
                            color: parent.checked ? "#303030" : "#2C2C2C"
                            border.color: "gray"
                            border.width: parent.checked ? 1 : 0
                            
                            // HoverHandler für Hover-Effekte
                            HoverHandler {
                                onHoveredChanged: if (hovered) parent.color = "#404040"; else parent.color = parent.parent.checked ? "#303030" : "#2C2C2C"
                            }
                            
                            // Sanfter Übergangseffekt für Farben
                            Behavior on color {
                                ColorAnimation { duration: 150 }
                            }
                        }
                    }
                    TabButton {
                        id: tabButton_support
                        text: "Support"
                        Material.foreground: "white"
                        
                        background: Rectangle {
                            implicitWidth: 100
                            implicitHeight: 40
                            color: parent.checked ? "#303030" : "#2C2C2C"
                            border.color: "gray"
                            border.width: parent.checked ? 1 : 0
                            
                            // HoverHandler für Hover-Effekte
                            HoverHandler {
                                onHoveredChanged: if (hovered) parent.color = "#404040"; else parent.color = parent.parent.checked ? "#303030" : "#2C2C2C"
                            }
                            
                            // Sanfter Übergangseffekt für Farben
                            Behavior on color {
                                ColorAnimation { duration: 150 }
                            }
                        }
                    }

                    TabButton {
                        id: tabButton_rzstore
                        text: "RZ Store"
                        Material.foreground: "white"
                        
                        background: Rectangle {
                            implicitWidth: 100
                            implicitHeight: 40
                            color: parent.checked ? "#303030" : "#2C2C2C"
                            border.color: "gray"
                            border.width: parent.checked ? 1 : 0
                            
                            // HoverHandler für Hover-Effekte
                            HoverHandler {
                                onHoveredChanged: if (hovered) parent.color = "#404040"; else parent.color = parent.parent.checked ? "#303030" : "#2C2C2C"
                            }
                            
                            // Sanfter Übergangseffekt für Farben
                            Behavior on color {
                                ColorAnimation { duration: 150 }
                            }
                        }
                    }

                    TabButton {
                        id: tabButton_firmware
                        text: "Firmware"
                        Material.foreground: "white"
                        ToolTip.visible: hovered
                        ToolTip.text: "Firmware-Installation und Updates"
                        
                        background: Rectangle {
                            implicitWidth: 100
                            implicitHeight: 40
                            color: parent.checked ? "#303030" : "#2C2C2C"
                            border.color: "gray"
                            border.width: parent.checked ? 1 : 0
                            
                            // HoverHandler für Hover-Effekte
                            HoverHandler {
                                onHoveredChanged: if (hovered) parent.color = "#404040"; else parent.color = parent.parent.checked ? "#303030" : "#2C2C2C"
                            }
                            
                            // Sanfter Übergangseffekt für Farben
                            Behavior on color {
                                ColorAnimation { duration: 150 }
                            }
                        }
                    }

                    TabButton {
                        id: tabButton_rzdroneDashboard
                        text: "RZ Drone Dashboard"
                        Material.foreground: "white"
                    }
                }

                // Content
                StackLayout {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    currentIndex: tabBar.currentIndex

                    RZGCS.PreflightView {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                    }
                    RZGCS.ParameterView {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                    }
                    RZGCS.SensorView {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                    }
                    SensorDashboard {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                    }
                    RZGCS.CalibrationView {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        // Use conditional property binding to avoid errors when controller is not defined
                        controller: typeof calibrationViewController !== 'undefined' ? calibrationViewController : null
                    }
                    RZGCS.MotorTestView {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        // Use conditional property binding to avoid errors when controller is not defined
                        controller: typeof motorTestController !== 'undefined' ? motorTestController : null
                    }
                    RZGCS.FlightView {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                    }
                    // AnimationView removed
                    RZGCS.AngelView {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                    }
                    RZGCS.LicenseView {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                    }
                    // Support View
                    Item {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        
                        // Implement simple Support view
                        Rectangle {
                            anchors.fill: parent
                            color: "#1e1e1e"
                            
                            ColumnLayout {
                                anchors.centerIn: parent
                                width: parent.width * 0.8
                                spacing: 20
                                
                                Text {
                                    text: "Support Center"
                                    font.pixelSize: 24
                                    color: "white"
                                    Layout.alignment: Qt.AlignHCenter
                                }
                                
                                Text {
                                    text: "Need help? Contact our support team."
                                    font.pixelSize: 16
                                    color: "white"
                                    Layout.alignment: Qt.AlignHCenter
                                }
                                
                                Button {
                                    text: "Contact Support"
                                    Layout.alignment: Qt.AlignHCenter
                                }
                            }
                        }
                    }

                    RZGCS.StoreView {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                    }

                    // Firmware View
                    RZGCS.FirmwareView {
                        id: firmwareViewTab
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        isConnected: serialConnector ? serialConnector.connected : false
                        firmwareViewModel: screen01.firmwareViewModel
                    }

                    RZDroneDashboard {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                    }
                }
            }

            // Message List Panel
            MessageList {
                Layout.preferredWidth: 300
                Layout.fillHeight: true
                messageManager: root.messageManager
            }
        }
    }
}
