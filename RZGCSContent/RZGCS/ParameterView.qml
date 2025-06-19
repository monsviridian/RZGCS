import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root
    color: "#303030"
    border.color: "#404040"
    border.width: 1

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 10

        // Suchleiste
        RowLayout {
            Layout.fillWidth: true
            spacing: 10

            TextField {
                id: searchField
                Layout.fillWidth: true
                placeholderText: "Search parameters..."
                background: Rectangle {
                    color: "black"
                    border.color: "gray"
                    border.width: 1
                    radius: 4
                }
                color: "white"
                onTextChanged: {
                    // TODO: Implement parameter search
                }
            }

            Button {
                text: "Refresh"
                onClicked: {
                    // TODO: Refresh parameters
                }
            }

            Button {
                text: "Save"
                onClicked: {
                    // TODO: Save parameters
                }
            }

            Button {
                text: "Load"
                onClicked: {
                    // TODO: Load parameters
                }
            }
        }

        // Parameter-Tabelle
        TableView {
            id: parameterTable
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            model: ListModel {
                // TODO: Add parameter data
            }

            TableViewColumn {
                title: "Name"
                role: "name"
                width: 200
            }

            TableViewColumn {
                title: "Value"
                role: "value"
                width: 100
            }

            TableViewColumn {
                title: "Type"
                role: "type"
                width: 100
            }

            TableViewColumn {
                title: "Description"
                role: "description"
                width: 300
            }

            background: Rectangle {
                color: "black"
            }

            headerDelegate: Rectangle {
                height: 30
                color: "#404040"
                border.color: "gray"
                border.width: 1

                Text {
                    anchors.fill: parent
                    anchors.margins: 5
                    text: styleData.value
                    color: "white"
                    verticalAlignment: Text.AlignVCenter
                }
            }

            rowDelegate: Rectangle {
                height: 30
                color: styleData.selected ? "#505050" : (styleData.alternate ? "#353535" : "#303030")
            }

            itemDelegate: Text {
                text: styleData.value
                color: "white"
                verticalAlignment: Text.AlignVCenter
                anchors.margins: 5
            }
        }

        // Status
        Label {
            text: "Parameters loaded: 0"
            color: "white"
        }
    }
} 