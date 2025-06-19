#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Einfacher visueller Test für den überarbeiteten künstlichen Horizont
"""

import os
import sys
import time
import math

# Pfad für die Importe hinzufügen
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from PySide6.QtCore import Qt, QTimer, QObject, Signal, Property, Slot
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine, QQmlContext


class HorizonTester(QObject):
    """Einfacher Tester für den künstlichen Horizont"""
    
    # Signale für die Aktualisierung der Werte
    rollChanged = Signal()
    pitchChanged = Signal()
    disarmedChanged = Signal()
    
    def __init__(self):
        super().__init__()
        self._roll = 0.0
        self._pitch = 0.0
        self._disarmed = True
        self._animation_timer = None
        
    # Roll Property
    def get_roll(self):
        return self._roll
        
    def set_roll(self, value):
        if self._roll != value:
            self._roll = value
            self.rollChanged.emit()
            
    roll = Property(float, get_roll, set_roll, notify=rollChanged)
    
    # Pitch Property
    def get_pitch(self):
        return self._pitch
        
    def set_pitch(self, value):
        if self._pitch != value:
            self._pitch = value
            self.pitchChanged.emit()
            
    pitch = Property(float, get_pitch, set_pitch, notify=pitchChanged)
    
    # Disarmed Property
    def get_disarmed(self):
        return self._disarmed
        
    def set_disarmed(self, value):
        if self._disarmed != value:
            self._disarmed = value
            self.disarmedChanged.emit()
            
    disarmed = Property(bool, get_disarmed, set_disarmed, notify=disarmedChanged)
    
    @Slot()
    def startAnimations(self):
        """Starte Animation der Roll- und Pitch-Werte"""
        if not self._animation_timer:
            self._animation_timer = QTimer(self)
            self._animation_timer.timeout.connect(self._update_values)
            self._animation_timer.start(50)  # 50ms Aktualisierungsintervall
            print("Animation gestartet")
    
    @Slot()
    def stopAnimations(self):
        """Stoppe die Animation"""
        if self._animation_timer:
            self._animation_timer.stop()
            self._animation_timer = None
            print("Animation gestoppt")
    
    @Slot(bool)
    def toggleArmed(self, armed):
        """Umschalten des Armed-Status"""
        self.set_disarmed(not armed)
        print(f"Status: {'Armed' if armed else 'Disarmed'}")
    
    def _update_values(self):
        """Aktualisiere Roll und Pitch mit animierten Werten"""
        # Berechne Roll und Pitch basierend auf der Zeit für eine sanfte Animation
        current_time = time.time()
        self.set_roll(30 * math.sin(current_time * 0.5))  # -30° bis +30° Roll
        self.set_pitch(15 * math.cos(current_time * 0.7)) # -15° bis +15° Pitch


def main():
    """Hauptfunktion zum Starten des Tests"""
    app = QGuiApplication(sys.argv)
    
    # Engine erstellen
    engine = QQmlApplicationEngine()
    
    # HorizonTester erstellen und im QML-Kontext registrieren
    tester = HorizonTester()
    engine.rootContext().setContextProperty("horizonTester", tester)
    
    # Importpfade für QML-Komponenten festlegen
    rzgcs_content_dir = os.path.abspath(os.path.join(parent_dir, "..", "RZGCSContent"))
    engine.addImportPath(rzgcs_content_dir)
    
    # QML-Datei laden
    qml_file = os.path.join(current_dir, "horizon_test.qml")
    
    # QML-Datei erstellen, wenn sie nicht existiert
    if not os.path.exists(qml_file):
        with open(qml_file, "w") as f:
            f.write("""
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Window {
    id: testWindow
    width: 800
    height: 600
    visible: true
    title: "Künstlicher Horizont Test"
    color: "#222222"
    
    // Layout für alle Komponenten
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 20
        
        // Überschrift
        Text {
            Layout.alignment: Qt.AlignHCenter
            text: "Test des künstlichen Horizonts ohne Bild"
            color: "white"
            font.pixelSize: 24
            font.bold: true
        }
        
        // Horizont-Komponente
        ArtificialHorizon {
            id: horizon
            Layout.alignment: Qt.AlignHCenter
            width: 300
            height: 300
            roll: horizonTester.roll
            pitch: horizonTester.pitch
            disarmed: horizonTester.disarmed
        }
        
        // Anzeige der aktuellen Werte
        Rectangle {
            Layout.alignment: Qt.AlignHCenter
            width: 300
            height: 80
            color: "#333333"
            radius: 5
            
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 10
                
                Text {
                    text: "Roll: " + horizonTester.roll.toFixed(1) + "°"
                    color: "white"
                    font.pixelSize: 16
                }
                
                Text {
                    text: "Pitch: " + horizonTester.pitch.toFixed(1) + "°"
                    color: "white"
                    font.pixelSize: 16
                }
                
                Text {
                    text: "Status: " + (horizonTester.disarmed ? "Disarmed" : "Armed")
                    color: horizonTester.disarmed ? "red" : "lime"
                    font.pixelSize: 16
                    font.bold: true
                }
            }
        }
        
        // Steuerelemente
        RowLayout {
            Layout.alignment: Qt.AlignHCenter
            spacing: 20
            
            Button {
                text: "Animation starten"
                onClicked: horizonTester.startAnimations()
            }
            
            Button {
                text: "Animation stoppen"
                onClicked: horizonTester.stopAnimations()
            }
            
            Button {
                text: horizonTester.disarmed ? "Arming" : "Disarming"
                onClicked: horizonTester.toggleArmed(!horizonTester.disarmed)
            }
        }
        
        // Hinweis
        Text {
            Layout.alignment: Qt.AlignHCenter
            text: "Dieser Test zeigt den künstlichen Horizont mit Rechtecken statt Bilddatei."
            color: "lightgray"
            font.pixelSize: 14
        }
    }
}
""")
    
    # QML-Datei laden
    engine.load(qml_file)
    
    # Prüfen, ob QML geladen wurde
    if not engine.rootObjects():
        print("FEHLER: QML-Datei konnte nicht geladen werden!")
        sys.exit(-1)
    
    # Starte die Animation automatisch
    QTimer.singleShot(1000, tester.startAnimations)
    
    # Event-Loop starten
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
