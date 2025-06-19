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
    property var keyData: ({})
    
    // Signals
    signal generateKeysClicked()
    signal validateKeysClicked()
    
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
                    text: "Key Generator"
                    font.pixelSize: 20
                    color: "white"
                }
                
                Item { Layout.fillWidth: true }
                
                Button {
                    text: "Generate Keys"
                    enabled: isConnected && selectedUavId !== ""
                    onClicked: generateKeysClicked()
                }
                
                Button {
                    text: "Validate Keys"
                    enabled: isConnected && selectedUavId !== ""
                    onClicked: validateKeysClicked()
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
                
                // Key Generation Settings
                GroupBox {
                    title: "Key Generation Settings"
                    Layout.fillWidth: true
                    
                    ColumnLayout {
                        anchors.fill: parent
                        spacing: 5
                        
                        // Key Type
                        ComboBox {
                            id: keyTypeSelector
                            Layout.fillWidth: true
                            model: ["RSA", "ECC", "AES", "ChaCha20"]
                            enabled: isConnected && selectedUavId !== ""
                        }
                        
                        // Key Size
                        ComboBox {
                            id: keySizeSelector
                            Layout.fillWidth: true
                            model: {
                                switch(keyTypeSelector.currentText) {
                                    case "RSA": return ["2048", "4096", "8192"]
                                    case "ECC": return ["256", "384", "521"]
                                    case "AES": return ["128", "192", "256"]
                                    case "ChaCha20": return ["256"]
                                    default: return []
                                }
                            }
                            enabled: isConnected && selectedUavId !== ""
                        }
                        
                        // Key Format
                        ComboBox {
                            id: keyFormatSelector
                            Layout.fillWidth: true
                            model: ["PEM", "DER", "JWK", "Raw"]
                            enabled: isConnected && selectedUavId !== ""
                        }
                    }
                }
                
                // Key Status
                GroupBox {
                    title: "Key Status"
                    Layout.fillWidth: true
                    
                    ColumnLayout {
                        anchors.fill: parent
                        spacing: 5
                        
                        Label {
                            text: "Key Type: " + (keyData.type || "N/A")
                        }
                        
                        Label {
                            text: "Key Size: " + (keyData.size || "N/A")
                        }
                        
                        Label {
                            text: "Key Format: " + (keyData.format || "N/A")
                        }
                        
                        Label {
                            text: "Key Status: " + (keyData.status || "N/A")
                        }
                        
                        Label {
                            text: "Key Created: " + (keyData.created || "N/A")
                        }
                        
                        Label {
                            text: "Key Expires: " + (keyData.expires || "N/A")
                        }
                    }
                }
                
                // Key Preview
                GroupBox {
                    title: "Key Preview"
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    
                    ScrollView {
                        anchors.fill: parent
                        clip: true
                        
                        TextArea {
                            id: keyPreview
                            readOnly: true
                            text: keyData.preview || ""
                            font.family: "Courier"
                            font.pixelSize: 12
                        }
                    }
                }
            }
        }
    }
    
    // Message Dialog
    MessageDialog {
        id: messageDialog
        title: "Key Generator"
        buttons: MessageDialog.Ok
    }
    
    // Functions
    function showMessage(title, message) {
        messageDialog.title = title
        messageDialog.text = message
        messageDialog.open()
    }
    
    function updateKeyData(data) {
        keyData = data
    }
} 