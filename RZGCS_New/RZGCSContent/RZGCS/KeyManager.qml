import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Window
import QtQuick.Dialogs

Item {
    id: root
    
    // Properties
    property bool isConnected: false
    property string selectedUavId: ""
    property var fleetData: ({})
    property var uavData: ({})
    
    // Signals
    signal uavSelected(string uavId)
    signal connectClicked()
    signal disconnectClicked()
    signal refreshClicked()
    
    // Layout
    ColumnLayout {
        anchors.fill: parent
        spacing: 10
        
        // Header
        Rectangle {
            Layout.fillWidth: true
            height: 50
            color: "#2c3e50"
            
            RowLayout {
                anchors.fill: parent
                anchors.margins: 10
                spacing: 10
                
                Label {
                    text: "Key Manager"
                    font.pixelSize: 20
                    color: "white"
                }
                
                Item { Layout.fillWidth: true }
                
                Button {
                    text: isConnected ? "Disconnect" : "Connect"
                    onClicked: isConnected ? disconnectClicked() : connectClicked()
                }
                
                Button {
                    text: "Refresh"
                    enabled: isConnected
                    onClicked: refreshClicked()
                }
            }
        }
        
        // Content
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: "#34495e"
            
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 10
                spacing: 10
                
                // UAV Selection
                ComboBox {
                    id: uavSelector
                    Layout.fillWidth: true
                    model: Object.keys(fleetData)
                    enabled: isConnected
                    onCurrentTextChanged: {
                        if (currentText !== "") {
                            selectedUavId = currentText
                            uavSelected(currentText)
                        }
                    }
                }
                
                // UAV Data
                ScrollView {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    clip: true
                    
                    ColumnLayout {
                        width: parent.width
                        spacing: 10
                        
                        // Key Status
                        GroupBox {
                            title: "Key Status"
                            Layout.fillWidth: true
                            
                            ColumnLayout {
                                anchors.fill: parent
                                spacing: 5
                                
                                Label {
                                    text: "Key Generation: " + (uavData.keyGeneration || "N/A")
                                }
                                
                                Label {
                                    text: "Key Validation: " + (uavData.keyValidation || "N/A")
                                }
                                
                                Label {
                                    text: "Key Verification: " + (uavData.keyVerification || "N/A")
                                }
                                
                                Label {
                                    text: "Key Signing: " + (uavData.keySigning || "N/A")
                                }
                                
                                Label {
                                    text: "Key Encryption: " + (uavData.keyEncryption || "N/A")
                                }
                                
                                Label {
                                    text: "Key Decryption: " + (uavData.keyDecryption || "N/A")
                                }
                            }
                        }
                        
                        // Key Management
                        GroupBox {
                            title: "Key Management"
                            Layout.fillWidth: true
                            
                            ColumnLayout {
                                anchors.fill: parent
                                spacing: 5
                                
                                Button {
                                    text: "Generate Keys"
                                    enabled: isConnected && selectedUavId !== ""
                                    onClicked: {
                                        // TODO: Implement key generation
                                    }
                                }
                                
                                Button {
                                    text: "Validate Keys"
                                    enabled: isConnected && selectedUavId !== ""
                                    onClicked: {
                                        // TODO: Implement key validation
                                    }
                                }
                                
                                Button {
                                    text: "Verify Keys"
                                    enabled: isConnected && selectedUavId !== ""
                                    onClicked: {
                                        // TODO: Implement key verification
                                    }
                                }
                                
                                Button {
                                    text: "Sign Keys"
                                    enabled: isConnected && selectedUavId !== ""
                                    onClicked: {
                                        // TODO: Implement key signing
                                    }
                                }
                                
                                Button {
                                    text: "Encrypt Keys"
                                    enabled: isConnected && selectedUavId !== ""
                                    onClicked: {
                                        // TODO: Implement key encryption
                                    }
                                }
                                
                                Button {
                                    text: "Decrypt Keys"
                                    enabled: isConnected && selectedUavId !== ""
                                    onClicked: {
                                        // TODO: Implement key decryption
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    
    // Message Dialog
    MessageDialog {
        id: messageDialog
        title: "Key Manager"
        buttons: MessageDialog.Ok
    }
    
    // Functions
    function showMessage(title, message) {
        messageDialog.title = title
        messageDialog.text = message
        messageDialog.open()
    }
    
    function updateFleetData(data) {
        fleetData = data
    }
    
    function updateUavData(data) {
        uavData = data
    }
} 