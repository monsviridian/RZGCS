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
    property var validationData: ({})
    
    // Signals
    signal validateKeysClicked()
    signal verifyKeysClicked()
    
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
                    text: "Key Validator"
                    font.pixelSize: 20
                    color: "white"
                }
                
                Item { Layout.fillWidth: true }
                
                Button {
                    text: "Validate Keys"
                    enabled: isConnected && selectedUavId !== ""
                    onClicked: validateKeysClicked()
                }
                
                Button {
                    text: "Verify Keys"
                    enabled: isConnected && selectedUavId !== ""
                    onClicked: verifyKeysClicked()
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
                
                // Validation Settings
                GroupBox {
                    title: "Validation Settings"
                    Layout.fillWidth: true
                    
                    ColumnLayout {
                        anchors.fill: parent
                        spacing: 5
                        
                        // Validation Type
                        ComboBox {
                            id: validationTypeSelector
                            Layout.fillWidth: true
                            model: ["Format", "Structure", "Integrity", "Compliance"]
                            enabled: isConnected && selectedUavId !== ""
                        }
                        
                        // Validation Level
                        ComboBox {
                            id: validationLevelSelector
                            Layout.fillWidth: true
                            model: ["Basic", "Standard", "Strict", "Custom"]
                            enabled: isConnected && selectedUavId !== ""
                        }
                        
                        // Validation Rules
                        ListView {
                            id: validationRulesList
                            Layout.fillWidth: true
                            height: 100
                            model: ListModel {
                                ListElement { name: "Format Check"; enabled: true }
                                ListElement { name: "Structure Check"; enabled: true }
                                ListElement { name: "Integrity Check"; enabled: true }
                                ListElement { name: "Compliance Check"; enabled: true }
                            }
                            delegate: CheckDelegate {
                                text: name
                                checked: enabled
                                onCheckedChanged: enabled = checked
                            }
                        }
                    }
                }
                
                // Validation Status
                GroupBox {
                    title: "Validation Status"
                    Layout.fillWidth: true
                    
                    ColumnLayout {
                        anchors.fill: parent
                        spacing: 5
                        
                        Label {
                            text: "Validation Type: " + (validationData.type || "N/A")
                        }
                        
                        Label {
                            text: "Validation Level: " + (validationData.level || "N/A")
                        }
                        
                        Label {
                            text: "Validation Status: " + (validationData.status || "N/A")
                        }
                        
                        Label {
                            text: "Validation Time: " + (validationData.time || "N/A")
                        }
                        
                        Label {
                            text: "Validation Result: " + (validationData.result || "N/A")
                        }
                    }
                }
                
                // Validation Details
                GroupBox {
                    title: "Validation Details"
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    
                    ScrollView {
                        anchors.fill: parent
                        clip: true
                        
                        ListView {
                            id: validationDetailsList
                            model: validationData.details || []
                            delegate: ItemDelegate {
                                width: parent.width
                                contentItem: ColumnLayout {
                                    Label {
                                        text: modelData.name
                                        font.bold: true
                                    }
                                    Label {
                                        text: modelData.description
                                        wrapMode: Text.WordWrap
                                    }
                                    Label {
                                        text: "Status: " + modelData.status
                                        color: modelData.status === "Pass" ? "green" : "red"
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
        title: "Key Validator"
        buttons: MessageDialog.Ok
    }
    
    // Functions
    function showMessage(title, message) {
        messageDialog.title = title
        messageDialog.text = message
        messageDialog.open()
    }
    
    function updateValidationData(data) {
        validationData = data
    }
} 