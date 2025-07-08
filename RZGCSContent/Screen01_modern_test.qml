/*
Test-Version von Screen01.ui.qml mit neuen modernen Komponenten
*/
import QtQuick 2.15
import QtQuick.Controls.Material 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Window 2.15

// Neue Komponenten importieren
import "./Utils" as Utils
import "./Components" as Components

Item {
    id: root
    width: 1200
    height: 800
    
    // Properties für ViewModels
    property var firmwareViewModel

    // Schwarzer Hintergrund
    Rectangle {
        anchors.fill: parent
        color: Utils.DroneTheme.backgroundColor
        z: -1
    }

    // Toast Notification Container
    Item {
        id: toastContainer
        anchors.top: parent.top
        anchors.right: parent.right
        anchors.margins: Utils.DroneTheme.marginLarge
        z: Utils.DroneTheme.zIndexToast
    }

    // Ensure serialConnector is available
    Component.onCompleted: {
        // WICHTIG: Context Properties sind direkt verfügbar, keine Zuweisung nötig
        console.log("D: QML messageManager:", messageManager)
        console.log("D: QML firmwareViewModel:", firmwareViewModel)
        console.log("D: QML serialConnector:", serialConnector)
        
        if (messageManager) {
            messageManager.addMessage("QML MessageManager successfully initialized", 4)
        } else {
            console.log("W: messageManager context property is not available")
        }
        
        if (serialConnector)
            console.log("D: serialConnector.isConnected:", serialConnector.isConnected)
        if (messageManager && messageManager.messages)
            console.log("D: messageManager.messages.length:", messageManager.messages.length)
        else
            console.log("W: messageManager.messages ist nicht verfügbar")
        
        if (serialConnector) {
            serialConnector.load_ports()
            if (root.messageManager)
                root.messageManager.addMessage("Application started", 1)
            showToast("RZGCS started successfully", 1)
        }
    }
    
    // Function to show toast notification
    function showToast(message, type) {
        var toast = Qt.createComponent("ToastNotification.qml").createObject(toastContainer, {
            message: message,
            type: type,
            duration: type === 3 ? 5000 : 3000
        })
        
        toast.x = toastContainer.width - toast.width
        toast.show()
        
        toast.hideAnimation.finished.connect(function() {
            toast.destroy()
        })
    }

    // Hauptlayout: Status Bar oben, Content unten
    ColumnLayout {
        anchors.fill: parent
        spacing: Utils.DroneTheme.spacingDefault

        // Verbindungskontrolle oben mit neuen Komponenten
        Rectangle {
            Layout.fillWidth: true
            color: Utils.DroneTheme.backgroundColor
            implicitHeight: connectionControlsRow.implicitHeight + Utils.DroneTheme.marginDefault
            
            RowLayout {
                id: connectionControlsRow
                anchors {
                    left: parent.left
                    right: parent.right
                    top: parent.top
                    margins: Utils.DroneTheme.marginDefault
                }
                spacing: Utils.DroneTheme.spacingDefault

                ComboBox {
                    id: portComboBox
                    model: serialConnector ? serialConnector.availablePorts : []
                    Layout.preferredWidth: 350
                    
                    ToolTip.visible: hovered
                    ToolTip.text: currentText || "Select a port"
                    ToolTip.delay: 500
                    
                    onCurrentIndexChanged: {
                        if (serialConnector && currentIndex >= 0 && currentText !== "") {
                            serialConnector.setPort(currentText)
                        }
                    }
                    
                    background: Rectangle {
                        color: Utils.DroneTheme.panelColor
                        border.color: Utils.DroneTheme.borderColor
                        border.width: 1
                        radius: Utils.DroneTheme.radiusSmall
                    }
                    
                    contentItem: Text {
                        text: portComboBox.displayText
                        color: Utils.DroneTheme.textColor
                        verticalAlignment: Text.AlignVCenter
                        leftPadding: 5
                        elide: Text.ElideRight
                    }
                    
                    popup.background: Rectangle {
                        color: Utils.DroneTheme.panelColor
                        border.color: Utils.DroneTheme.borderColor
                    }
                    
                    delegate: ItemDelegate {
                        width: portComboBox.width
                        contentItem: Text {
                            text: modelData
                            color: Utils.DroneTheme.textColor
                            elide: Text.ElideRight
                            verticalAlignment: Text.AlignVCenter
                            font.pointSize: 9
                        }
                        background: Rectangle {
                            color: highlighted ? Utils.DroneTheme.borderColor : Utils.DroneTheme.panelColor
                        }
                        highlighted: portComboBox.highlightedIndex === index
                    }
                }

                ComboBox {
                    id: baudComboBox
                    model: serialConnector ? serialConnector.availableBaudRates : []
                    currentIndex: 4
                    Layout.preferredWidth: 100
                    
                    background: Rectangle {
                        color: Utils.DroneTheme.panelColor
                        border.color: Utils.DroneTheme.borderColor
                        border.width: 1
                        radius: Utils.DroneTheme.radiusSmall
                    }
                    
                    contentItem: Text {
                        text: baudComboBox.displayText
                        color: Utils.DroneTheme.textColor
                        verticalAlignment: Text.AlignVCenter
                        leftPadding: 5
                    }
                    
                    popup.background: Rectangle {
                        color: Utils.DroneTheme.panelColor
                        border.color: Utils.DroneTheme.borderColor
                    }
                    
                    delegate: ItemDelegate {
                        width: baudComboBox.width
                        contentItem: Text {
                            text: modelData
                            color: Utils.DroneTheme.textColor
                            elide: Text.ElideRight
                            verticalAlignment: Text.AlignVCenter
                        }
                        background: Rectangle {
                            color: highlighted ? Utils.DroneTheme.borderColor : Utils.DroneTheme.panelColor
                        }
                        highlighted: baudComboBox.highlightedIndex === index
                    }
                    onCurrentTextChanged: if (serialConnector) serialConnector.setBaudRate(parseInt(currentText))
                }

                // NEUE: DroneButton verwenden
                Components.DroneButton {
                    text: serialConnector && serialConnector.isConnected ? "Disconnect" : "Connect"
                    buttonType: serialConnector && serialConnector.isConnected ? "danger" : "primary"
                    Layout.preferredWidth: 80
                    
                    onClicked: {
                        if (serialConnector) {
                            if (serialConnector.isConnected) {
                                serialConnector.disconnect()
                            } else {
                                if (portComboBox.currentText !== "") {
                                    console.log("Connecting to: " + portComboBox.currentText)
                                    serialConnector.setPort(portComboBox.currentText)
                                    var success = serialConnector.connect()
                                    
                                    if (!success) {
                                        showToast("Connection failed - check if device is connected and port is available", 3)
                                    }
                                } else {
                                    showToast("Please select a port first", 2)
                                }
                            }
                        } else {
                            showToast("Serial connector not available", 3)
                        }
                    }
                }

                Components.DroneButton {
                    text: "Refresh Ports"
                    buttonType: "secondary"
                    Layout.preferredWidth: 100
                    
                    onClicked: {
                        if (serialConnector) {
                            serialConnector.load_ports()
                        }
                    }
                }
                
                // NEUE: ConnectionAlert verwenden
                Components.ConnectionAlert {
                    id: connectionAlert
                    Layout.preferredWidth: 200
                    Layout.preferredHeight: 50
                    
                    // Verbinde mit SerialConnector
                    property bool isConnected: serialConnector ? serialConnector.isConnected : false
                    property real packetLossRate: 0.0
                    property real heartbeatFrequency: 1.0
                    
                    // Update Status basierend auf Verbindung
                    onIsConnectedChanged: {
                        if (isConnected) {
                            setStatus(true, packetLossRate, heartbeatFrequency)
                        } else {
                            setStatus(false, 0, 0)
                        }
                    }
                }
                
                // Status label showing selected port
                Label {
                    text: portComboBox.currentText ? "Selected: " + portComboBox.currentText : "No port selected"
                    color: Utils.DroneTheme.textColor
                    font.pointSize: 8
                    Layout.fillWidth: true
                    elide: Text.ElideRight
                }
            }
        }

        // Tab-Leiste mit Theme-Farben
        TabBar {
            id: tabBar
            Layout.fillWidth: true
            
            TabButton { text: "Connection" }
            TabButton { text: "MAVLink 2" }
            TabButton { text: "Preflight Check" }
            TabButton { text: "Parameter" }
            TabButton { text: "Calibration" }
            TabButton { text: "Motor Test" }
            TabButton { text: "Firmware" }
            TabButton { text: "Flight" }
            TabButton { text: "Sensor Dashboard" }
            TabButton { text: "Telemetry Chart" }
        }

        // Hauptbereich: Content links, Messages rechts
        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: Utils.DroneTheme.spacingDefault

            // Content-Bereich
            StackLayout {
                id: contentStack
                Layout.fillWidth: true
                Layout.fillHeight: true
                currentIndex: tabBar.currentIndex

                PreflightView { 
                    id: connectionView 
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
                
                Loader { 
                    id: mavlink2TabLoader
                    source: "MAVLink2Tab.qml"
                    onLoaded: {
                        if (mavlink2TabLoader.item) {
                            // MAVLink2Tab Context Properties zuweisen
                            if (typeof protocolConnectionManager !== "undefined") {
                                mavlink2TabLoader.item.protocolConnectionManager = protocolConnectionManager
                                console.log("D: protocolConnectionManager zugewiesen")
                            } else {
                                console.log("W: protocolConnectionManager nicht verfügbar")
                            }
                            
                            if (typeof mavlinkV2Backend !== "undefined") {
                                mavlink2TabLoader.item.mavlinkV2Backend = mavlinkV2Backend
                                console.log("D: mavlinkV2Backend zugewiesen")
                            } else {
                                console.log("W: mavlinkV2Backend nicht verfügbar")
                            }
                        }
                    }
                }
                
                Rectangle { 
                    id: preflightCheckView
                    color: Utils.DroneTheme.backgroundColor
                    
                    Components.StatusPanel {
                        id: preflightPanel
                        anchors.fill: parent
                        title: "Preflight Check"
                        
                        ColumnLayout {
                            anchors.fill: parent
                            spacing: Utils.DroneTheme.spacingMedium
                            
                            ListView {
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                spacing: Utils.DroneTheme.spacingSmall
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
                                    width: parent ? parent.width : 0
                                    height: 40
                                    spacing: Utils.DroneTheme.spacingDefault
                                    
                                    CheckBox {
                                        checked: model.checked
                                        onCheckedChanged: model.checked = checked
                                        indicator: Rectangle {
                                            width: 20
                                            height: 20
                                            border.color: Utils.DroneTheme.textColor
                                            color: "transparent"
                                            Text {
                                                anchors.centerIn: parent
                                                text: "✓"
                                                color: Utils.DroneTheme.accentColor
                                                visible: parent.parent.checked
                                            }
                                        }
                                    }
                                    
                                    Text {
                                        text: model.name
                                        color: Utils.DroneTheme.textColor
                                        font.pixelSize: Utils.DroneTheme.fontSizeMedium
                                    }
                                }
                            }
                        }
                    }
                }
                
                ParameterTab { 
                    id: parameterTab
                    Component.onCompleted: {
                        if (serialConnector && serialConnector.connected && parameterViewModel) {
                            parameterViewModel.refreshParameters()
                        }
                    }
                }
                
                CalibrationView { 
                    id: calibrationView
                    // CalibrationController ist als Context Property verfügbar
                    Component.onCompleted: {
                        console.log("D: CalibrationView initialisiert")
                        console.log("D: calibrationController verfügbar:", typeof calibrationController !== "undefined")
                    }
                }
                
                MotorTestView { 
                    id: motorTestView
                    // SerialConnector ist als Context Property verfügbar
                    Component.onCompleted: {
                        console.log("D: MotorTestView initialisiert")
                        console.log("D: serialConnector verfügbar:", typeof serialConnector !== "undefined")
                    }
                }
                
                Loader { 
                    id: firmwareTabLoader
                    source: "FirmwareView.ui.qml"
                    onLoaded: {
                        if (firmwareTabLoader.item) {
                            // Versuche verschiedene Context Property-Namen
                            if (typeof firmwareViewModel !== "undefined") {
                                firmwareTabLoader.item.firmwareViewModel = firmwareViewModel
                                console.log("D: FirmwareViewModel über Context Property zugewiesen")
                            } else if (typeof firmware_vm !== "undefined") {
                                firmwareTabLoader.item.firmwareViewModel = firmware_vm
                                console.log("D: FirmwareViewModel über firmware_vm zugewiesen")
                            } else if (root.firmwareViewModel) {
                                firmwareTabLoader.item.firmwareViewModel = root.firmwareViewModel
                                console.log("D: FirmwareViewModel über root zugewiesen")
                            } else {
                                console.log("W: FirmwareViewModel nicht verfügbar für FirmwareView")
                            }
                        }
                    }
                }
                
                FlightView { 
                    id: flightView
                    Component.onCompleted: {
                        console.log("FlightView initialisiert")
                        if (typeof flightViewController !== 'undefined') {
                            console.log("FlightViewController gefunden!")
                        }
                    }
                }
                
                SensorDashboardTab { 
                    id: sensorDashboardTab
                    // sensorViewModel ist als Context Property verfügbar
                    Component.onCompleted: {
                        console.log("D: SensorDashboardTab initialisiert")
                        console.log("D: sensorViewModel verfügbar:", typeof sensorViewModel !== "undefined")
                    }
                }
                
                // Telemetry Chart Tab
                Rectangle {
                    id: telemetryChartTab
                    color: Utils.DroneTheme.backgroundColor
                    
                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: Utils.DroneTheme.spacingDefault
                        spacing: Utils.DroneTheme.spacingMedium
                        
                        // Header
                        RowLayout {
                            Layout.fillWidth: true
                            spacing: Utils.DroneTheme.spacingDefault
                            
                            Text {
                                text: "Telemetry Charts"
                                color: Utils.DroneTheme.textColor
                                font.pixelSize: Utils.DroneTheme.fontSizeLarge
                                font.bold: true
                            }
                            
                            Item { Layout.fillWidth: true }
                            
                            // Chart-Type Selector
                            ComboBox {
                                id: chartTypeSelector
                                model: ["Altitude", "Speed", "Battery", "Roll", "Pitch", "Yaw"]
                                currentIndex: 0
                                onCurrentTextChanged: {
                                    if (telemetryChart.item) {
                                        telemetryChart.item.setDataType(currentText.toLowerCase())
                                    }
                                }
                                
                                background: Rectangle {
                                    color: Utils.DroneTheme.panelColor
                                    border.color: Utils.DroneTheme.borderColor
                                    border.width: 1
                                    radius: Utils.DroneTheme.radiusSmall
                                }
                                
                                contentItem: Text {
                                    text: chartTypeSelector.displayText
                                    color: Utils.DroneTheme.textColor
                                    font.pixelSize: Utils.DroneTheme.fontSizeMedium
                                    verticalAlignment: Text.AlignVCenter
                                    horizontalAlignment: Text.AlignHCenter
                                }
                            }
                        }
                        
                        // Chart Container
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            color: Utils.DroneTheme.panelColor
                            border.color: Utils.DroneTheme.borderColor
                            border.width: 1
                            radius: Utils.DroneTheme.radiusDefault
                            
                            // TelemetryChart Component
                            Loader {
                                id: telemetryChart
                                anchors.fill: parent
                                anchors.margins: Utils.DroneTheme.spacingDefault
                                source: "Components/TelemetryChart.qml"
                                
                                onLoaded: {
                                    if (item) {
                                        // Context Properties zuweisen
                                        item.sensorViewModel = sensorViewModel
                                        item.dataType = chartTypeSelector.currentText.toLowerCase()
                                        item.maxDataPoints = 200
                                        item.useOpenGL = true
                                        
                                        console.log("D: TelemetryChart geladen")
                                        console.log("D: sensorViewModel zugewiesen:", typeof sensorViewModel !== "undefined")
                                    }
                                }
                                
                                onStatusChanged: {
                                    if (status === Loader.Error) {
                                        console.log("E: TelemetryChart konnte nicht geladen werden")
                                    }
                                }
                            }
                        }
                        
                        // Control Panel
                        RowLayout {
                            Layout.fillWidth: true
                            spacing: Utils.DroneTheme.spacingDefault
                            
                            // Update Rate Slider
                            Text {
                                text: "Update Rate:"
                                color: Utils.DroneTheme.textColor
                                font.pixelSize: Utils.DroneTheme.fontSizeMedium
                            }
                            
                            Slider {
                                id: updateRateSlider
                                from: 1
                                to: 20
                                value: 10
                                stepSize: 1
                                
                                onValueChanged: {
                                    if (telemetryChart.item) {
                                        telemetryChart.item.updateTimer.interval = 1000 / value
                                    }
                                }
                            }
                            
                            Text {
                                text: updateRateSlider.value.toFixed(0) + " Hz"
                                color: Utils.DroneTheme.textColor
                                font.pixelSize: Utils.DroneTheme.fontSizeSmall
                            }
                            
                            Item { Layout.fillWidth: true }
                            
                            // Clear Chart Button
                            Components.DroneButton {
                                text: "Clear Chart"
                                buttonType: "secondary"
                                onClicked: {
                                    if (telemetryChart.item) {
                                        telemetryChart.item.clearChart()
                                    }
                                }
                            }
                            
                            // Export Button
                            Components.DroneButton {
                                text: "Export Data"
                                buttonType: "primary"
                                onClicked: {
                                    console.log("D: Export-Funktion noch nicht implementiert")
                                }
                            }
                        }
                    }
                }
            }
            
            // Rechter Message-Panel
            MessageList {
                id: messageList
                Layout.preferredWidth: 300
                Layout.minimumWidth: 200
                Layout.maximumWidth: 400
                Layout.fillHeight: true
            }
        }
    }
    
    // Event-getriebene Updates für bessere Performance
    Connections {
        target: sensorViewModel
        function onGpsChanged(lat, lon, alt) {
            // GPS-Daten wurden aktualisiert
            console.log("D: GPS-Daten aktualisiert:", lat, lon, alt)
        }
        
        function onAttitudeChanged(roll, pitch, yaw) {
            // Attitude-Daten wurden aktualisiert
            console.log("D: Attitude-Daten aktualisiert:", roll, pitch, yaw)
        }
        
        function onBatteryChanged(voltage, current, remaining) {
            // Batterie-Daten wurden aktualisiert
            console.log("D: Batterie-Daten aktualisiert:", voltage, current, remaining)
        }
    }
    
    // Event-getriebene Updates für MessageManager
    Connections {
        target: messageManager
        function onMessageAdded(message, type) {
            // Neue Nachricht wurde hinzugefügt
            console.log("D: Neue Nachricht:", message, type)
        }
        
        function onMessagesChanged() {
            // Nachrichtenliste wurde aktualisiert
            console.log("D: Nachrichtenliste aktualisiert")
        }
    }
    
    // Event-getriebene Updates für SerialConnector
    Connections {
        target: serialConnector
        function onConnectedChanged(connected) {
            // Verbindungsstatus wurde geändert
            console.log("D: Verbindungsstatus geändert:", connected)
        }
        
        function onConnectionStatusChanged(status) {
            // Verbindungsstatus wurde geändert
            console.log("D: Verbindungsstatus geändert:", status)
        }
    }
} 