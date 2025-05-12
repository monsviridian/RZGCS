

/*
This is a UI file (.ui.qml) that is intended to be edited in Qt Design Studio only.
It is supposed to be strictly declarative and only uses a subset of QML. If you edit
this file manually, you might introduce QML code that is not supported by Qt Design Studio.
Check out https://doc.qt.io/qtcreator/creator-quick-ui-forms.html for details on .ui.qml files.
*/
import QtQuick
import QtQuick.Controls

Rectangle {
    id: root
    width: 300
    height: 1080
    color: "#000000"

    ComboBox {
        id: seiral0
        x: 0
        y: 0
        width: 152
        height: 32

        contentItem: Text {
            color: "white"
            text: "Serial 0"
        }
    }

    ComboBox {
        id: seiral1
        x: 0
        y: 45
        width: 152
        height: 32

        contentItem: Text {
            color: "#ffffff"
            text: "Serial 1"
        }
    }

    ComboBox {
        id: seiral2
        x: 0
        y: 89
        width: 152
        height: 32

        contentItem: Text {
            color: "#ffffff"
            text: "Serial 2"
        }
    }

    ComboBox {
        id: seiral3
        x: 0
        y: 137
        width: 152
        height: 32

        contentItem: Text {
            color: "#ffffff"
            text: "Serial 3"
        }
    }

    ComboBox {
        id: seiral4
        x: 0
        y: 182
        width: 152
        height: 32

        contentItem: Text {
            color: "#ffffff"
            text: "Serial 4"
        }
    }

    ComboBox {
        id: seiral5
        x: 0
        y: 226
        width: 152
        height: 32

        contentItem: Text {
            color: "#ffffff"
            text: "Serial 5"
        }
    }

    ComboBox {
        id: seiral6
        x: 0
        y: 272
        width: 152
        height: 32
        contentItem: Text {
            color: "#ffffff"
            text: "Serial 6"
        }
    }

    TextArea {
        id: textArea
        x: 8
        y: 378
        width: 239
        height: 282
        placeholderText: qsTr("Tippe Commend")
    }
}
