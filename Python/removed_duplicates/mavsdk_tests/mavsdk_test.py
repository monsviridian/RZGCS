#!/usr/bin/env python3
"""
Vereinfachter MAVSDK-Test mit minimaler QML-Oberfläche
"""

import os
import sys
import time
from pathlib import Path
from PySide6.QtCore import QUrl, QObject, Signal, Slot, Property, Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

# Einfacher Logger
class Logger(QObject):
    logAdded = Signal(str)
    
    def __init__(self):
        super().__init__()
        self._logs = []
    
    def addLog(self, message):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        self._logs.append(formatted_message)
        self.logAdded.emit(formatted_message)
        print(formatted_message)
    
    @Slot(int, result="QVariantList")
    def getLogs(self, count=50):
        return self._logs[-count:] if count else self._logs


# Einfaches SensorViewModel
class SensorViewModel(QObject):
    sensorUpdated = Signal(str, object, str)
    sensorListChanged = Signal()
    
    def __init__(self):
        super().__init__()
        self._sensors = {}
        self._list_elements = {}
    
    def initialize_default_sensors(self):
        """Initialisiert die Standard-Sensoren"""
        list_elements = [
            {"name": "System Servos", "unit": ""},
            {"name": "System RC", "unit": ""},
            {"name": "System CPU", "unit": ""},
            {"name": "Battery %", "unit": ""},
            {"name": "Roll", "unit": "°"},
            {"name": "Pitch", "unit": "°"},
            {"name": "Yaw", "unit": "°"},
            {"name": "Altitude", "unit": "m"},
            {"name": "GPS Pos", "unit": "°"}
        ]
        
        for element in list_elements:
            self._list_elements[element["name"]] = {
                "name": element["name"],
                "value": "Nicht verbunden",
                "unit": element["unit"]
            }
        
        self.sensorListChanged.emit()
    
    @Slot(str, object, str)
    def updateQmlSensor(self, name, value, unit):
        """Aktualisiert einen Sensor in der QML-Ansicht"""
        if name in self._list_elements:
            self._list_elements[name]["value"] = value
            self._list_elements[name]["unit"] = unit
        
        self.sensorUpdated.emit(name, value, unit)
    
    @Slot(result="QVariantList")
    def get_sensor_list(self):
        """Gibt eine Liste aller Sensoren für QML zurück"""
        result = []
        for name, data in self._list_elements.items():
            result.append({
                "name": name,
                "value": data["value"],
                "unit": data["unit"]
            })
        return result


# Einfacher Controller
class DroneController(QObject):
    connectionChanged = Signal(bool)
    
    def __init__(self, logger, sensor_viewmodel):
        super().__init__()
        self._logger = logger
        self._sensor_viewmodel = sensor_viewmodel
        self._is_connected = False
    
    @Slot(str)
    def connect(self, connection_string):
        self._logger.addLog(f"Verbindung zu {connection_string} wird hergestellt...")
        # Hier würde die echte MAVSDK-Verbindung stattfinden
        self._is_connected = True
        self.connectionChanged.emit(True)
        self._logger.addLog("Verbindung hergestellt (Simulation)")
        
        # Simulierte Sensordaten
        self._sensor_viewmodel.updateQmlSensor("Roll", "5.2", "°")
        self._sensor_viewmodel.updateQmlSensor("Pitch", "2.1", "°")
        self._sensor_viewmodel.updateQmlSensor("Yaw", "358.7", "°")
        self._sensor_viewmodel.updateQmlSensor("Altitude", "120.5", "m")
        self._sensor_viewmodel.updateQmlSensor("Battery %", "78%", "")
        self._sensor_viewmodel.updateQmlSensor("GPS Pos", "48.744101, 11.446327", "°")
        self._sensor_viewmodel.updateQmlSensor("System CPU", "23.5%", "")
        
        return True
    
    @Slot()
    def disconnect(self):
        self._logger.addLog("Verbindung wird getrennt...")
        # Hier würde die echte MAVSDK-Verbindung getrennt werden
        self._is_connected = False
        self.connectionChanged.emit(False)
        self._logger.addLog("Verbindung getrennt")
        return True
    
    @Property(bool, notify=connectionChanged)
    def is_connected(self):
        return self._is_connected


def main():
    # QT-Anwendung erstellen
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    
    # Komponenten erstellen
    logger = Logger()
    sensor_viewmodel = SensorViewModel()
    drone_controller = DroneController(logger, sensor_viewmodel)
    
    # QML-Kontext einrichten
    root_context = engine.rootContext()
    root_context.setContextProperty("droneController", drone_controller)
    root_context.setContextProperty("sensorViewModel", sensor_viewmodel)
    root_context.setContextProperty("logger", logger)
    
    # Initialisierung
    sensor_viewmodel.initialize_default_sensors()
    
    # Debug-Ausgabe für den aktuellen Arbeitsverzeichnis
    logger.addLog(f"Arbeitsverzeichnis: {os.getcwd()}")
    
    # Erstelle temporäre QML-Datei für Test
    test_qml = """
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

ApplicationWindow {
    title: "MAVSDK Test"
    width: 1024
    height: 768
    visible: true
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 10
        
        // Connection Panel
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 60
            color: "#f0f0f0"
            border.color: "#c0c0c0"
            radius: 5
            
            RowLayout {
                anchors.fill: parent
                anchors.margins: 10
                spacing: 10
                
                TextField {
                    id: connectionField
                    Layout.fillWidth: true
                    placeholderText: "Verbindungsstring (z.B. udp://:14550)"
                    text: "udp://:14550"
                }
                
                Button {
                    text: droneController.is_connected ? "Trennen" : "Verbinden"
                    onClicked: {
                        if (droneController.is_connected) {
                            droneController.disconnect();
                        } else {
                            droneController.connect(connectionField.text);
                        }
                    }
                }
            }
        }
        
        // Main Content
        SplitView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            orientation: Qt.Horizontal
            
            // Sensor Panel
            Rectangle {
                SplitView.preferredWidth: 300
                SplitView.minimumWidth: 200
                color: "#f8f8f8"
                border.color: "#c0c0c0"
                
                ListView {
                    id: sensorListView
                    anchors.fill: parent
                    anchors.margins: 5
                    model: sensorViewModel.get_sensor_list()
                    
                    delegate: Rectangle {
                        width: sensorListView.width
                        height: 40
                        color: index % 2 === 0 ? "#ffffff" : "#f0f0f0"
                        
                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: 5
                            spacing: 5
                            
                            Text {
                                text: modelData.name
                                font.bold: true
                                Layout.preferredWidth: 140
                            }
                            
                            Text {
                                text: modelData.value
                                Layout.fillWidth: true
                            }
                            
                            Text {
                                text: modelData.unit
                                Layout.preferredWidth: 30
                            }
                        }
                    }
                    
                    // Update der Sensorliste, wenn sich Daten ändern
                    Connections {
                        target: sensorViewModel
                        function onSensorUpdated() {
                            sensorListView.model = sensorViewModel.get_sensor_list()
                        }
                    }
                }
            }
            
            // Log Panel
            Rectangle {
                SplitView.fillWidth: true
                SplitView.minimumWidth: 300
                color: "#f8f8f8"
                border.color: "#c0c0c0"
                
                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 5
                    spacing: 5
                    
                    Text {
                        text: "Logs"
                        font.bold: true
                        font.pixelSize: 16
                    }
                    
                    ListView {
                        id: logListView
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        model: logger.getLogs(100)
                        clip: true
                        
                        delegate: Text {
                            width: logListView.width
                            text: modelData
                            wrapMode: Text.Wrap
                            font.pixelSize: 12
                        }
                        
                        // Auto-Scroll nach unten
                        onCountChanged: {
                            currentIndex = count - 1
                        }
                    }
                    
                    // Update der Logs, wenn neue hinzukommen
                    Connections {
                        target: logger
                        function onLogAdded() {
                            logListView.model = logger.getLogs(100)
                        }
                    }
                }
            }
        }
    }
}
"""
    
    # Temporäre QML-Datei schreiben
    temp_qml_path = os.path.join(os.path.dirname(__file__), "temp_mavsdk_test.qml")
    with open(temp_qml_path, "w") as f:
        f.write(test_qml)
    
    logger.addLog(f"Temporäre QML-Datei erstellt: {temp_qml_path}")
    
    # QML-Datei laden
    qml_url = QUrl.fromLocalFile(temp_qml_path)
    logger.addLog(f"Lade QML-Datei: {temp_qml_path}")
    engine.load(qml_url)
    
    # Prüfen, ob QML-Datei erfolgreich geladen wurde
    if not engine.rootObjects():
        logger.addLog("❌ Fehler beim Laden der QML-Datei")
        return -1
    
    logger.addLog("MAVSDK-Test gestartet")
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
