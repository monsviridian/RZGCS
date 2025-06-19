import QtQuick
import QtQuick.Controls 6.8

Item {
    id: delegate
    width: 140
    height: 140

    Rectangle {
        id: rectangle
        color: "#2d2d2d"
        anchors.fill: parent
        anchors.margins: 12
        visible: true
        radius: 4
        border.color: delegate.GridView.isCurrentItem ? "#0d52a4" : "#3d3d3d"
        border.width: delegate.GridView.isCurrentItem ? 2 : 1
    }

    Column {
        anchors.fill: parent
        anchors.margins: 12
        spacing: 8

        Text {
            id: label
            color: "#ffffff"
            text: model ? (model.name || "Unknown") : "Unknown"
            font.pixelSize: 14
            font.bold: true
            anchors.horizontalCenter: parent.horizontalCenter
        }

        Text {
            id: valueLabel
            color: "#ffffff"
            text: model ? (model.formattedValue || "N/A") : "N/A"
            font.pixelSize: 12
            anchors.horizontalCenter: parent.horizontalCenter
            horizontalAlignment: Text.AlignHCenter
            wrapMode: Text.WordWrap
        }
    }

    MouseArea {
        anchors.fill: parent
        onClicked: delegate.GridView.view.currentIndex = index
    }
}
