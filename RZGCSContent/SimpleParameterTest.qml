import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Window 2.15

Window {
    id: window
    width: 800
    height: 600
    visible: true
    title: "Parameter Test"
    
    Rectangle {
        anchors.fill: parent
        color: "#1e1e1e"
        
        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 10
            spacing: 10
            
            // Header
            Text {
                text: "Parameter Test"
                color: "white"
                font.pixelSize: 20
                font.bold: true
            }
            
            // Status
            Text {
                text: "ParameterViewModel verfügbar: " + (parameterViewModel ? "Ja" : "Nein")
                color: "white"
                font.pixelSize: 14
            }
            
            Text {
                text: "ParameterModel verfügbar: " + (parameterViewModel && parameterViewModel.parameterModel ? "Ja" : "Nein")
                color: "white"
                font.pixelSize: 14
            }
            
            Text {
                text: "Parameter-Anzahl: " + (parameterViewModel && parameterViewModel.parameterModel ? parameterViewModel.parameterModel.count : "0")
                color: "white"
                font.pixelSize: 14
            }
            
            // Refresh Button
            Button {
                text: "Refresh Parameters"
                onClicked: {
                    if (parameterViewModel) {
                        parameterViewModel.refreshParameters()
                        console.log("Refresh requested")
                    }
                }
                background: Rectangle {
                    color: parent.pressed ? "#27ae60" : "#2ecc71"
                    radius: 3
                }
                contentItem: Text {
                    text: parent.text
                    color: "#ffffff"
                    horizontalAlignment: Text.AlignHCenter
                }
            }
            
            // Parameter List
            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                color: "#23272e"
                radius: 5
                border.color: "#333"
                border.width: 1
                
                ListView {
                    id: parameterListView
                    anchors.fill: parent
                    anchors.margins: 5
                    clip: true
                    
                    model: parameterViewModel ? parameterViewModel.parameterModel : null
                    
                    header: Rectangle {
                        width: parameterListView.width
                        height: 35
                        color: "#181c20"
                        
                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: 8
                            
                            Text {
                                text: "Name"
                                color: "#e0e0e0"
                                font.pixelSize: 12
                                font.bold: true
                                Layout.preferredWidth: 200
                            }
                            
                            Text {
                                text: "Value"
                                color: "#e0e0e0"
                                font.pixelSize: 12
                                font.bold: true
                                Layout.preferredWidth: 100
                            }
                            
                            Text {
                                text: "Type"
                                color: "#e0e0e0"
                                font.pixelSize: 12
                                font.bold: true
                                Layout.preferredWidth: 80
                            }
                            
                            Text {
                                text: "Description"
                                color: "#e0e0e0"
                                font.pixelSize: 12
                                font.bold: true
                                Layout.fillWidth: true
                            }
                        }
                    }
                    
                    delegate: Rectangle {
                        width: parameterListView.width
                        height: 40
                        color: index % 2 === 0 ? "#2c3e50" : "#34495e"
                        
                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: 8
                            
                            Text {
                                text: model.NameRole || "N/A"
                                font.pixelSize: 10
                                font.family: "Courier"
                                color: "#e0e0e0"
                                Layout.preferredWidth: 200
                                elide: Text.ElideRight
                            }
                            
                            Text {
                                text: model.ValueRole || "N/A"
                                font.pixelSize: 10
                                font.family: "Courier"
                                color: "#e0e0e0"
                                Layout.preferredWidth: 100
                                horizontalAlignment: Text.AlignRight
                            }
                            
                            Text {
                                text: model.TypeRole || "N/A"
                                font.pixelSize: 9
                                color: "#7f8c8d"
                                Layout.preferredWidth: 80
                            }
                            
                            Text {
                                text: model.DescriptionRole || "N/A"
                                font.pixelSize: 9
                                color: "#b0b0b0"
                                Layout.fillWidth: true
                                elide: Text.ElideRight
                            }
                        }
                        
                        Component.onCompleted: {
                            console.log("Delegate created for index", index, "NameRole:", model.NameRole)
                        }
                    }
                    
                    ScrollBar.vertical: ScrollBar {
                        active: true
                        policy: ScrollBar.AlwaysOn
                        background: Rectangle { color: "#181c20" }
                        contentItem: Rectangle { color: "#23272e"; radius: 3 }
                    }
                }
            }
        }
    }
    
    Component.onCompleted: {
        console.log("SimpleParameterTest.qml loaded")
        console.log("parameterViewModel:", parameterViewModel)
        if (parameterViewModel) {
            console.log("parameterViewModel.parameterModel:", parameterViewModel.parameterModel)
            if (parameterViewModel.parameterModel) {
                console.log("parameterModel.count:", parameterViewModel.parameterModel.count)
            }
        }
    }
} 