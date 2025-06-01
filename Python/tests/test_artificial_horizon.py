#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test für den überarbeiteten ArtificialHorizon ohne Bilddatei
"""

import os
import sys
import unittest
import time
from pathlib import Path

# Pfad für die Importe hinzufügen
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from PySide6.QtCore import QUrl, Qt, QTimer
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuick import QQuickWindow


class TestArtificialHorizon(unittest.TestCase):
    """Tests für die überarbeitete ArtificialHorizon-Komponente ohne Bilddatei"""

    @classmethod
    def setUpClass(cls):
        """Setup für die Testklasse - nur einmal ausgeführt"""
        # QGuiApplication-Instanz erstellen
        cls.app = QGuiApplication.instance()
        if not cls.app:
            cls.app = QGuiApplication([])

    def setUp(self):
        """Setup für jeden Test"""
        self.engine = QQmlApplicationEngine()
        self.root_context = self.engine.rootContext()
        
        # Basispfad ermitteln
        content_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'RZGCSContent'))
        self.assertTrue(os.path.exists(content_dir), f"Konnte den Pfad nicht finden: {content_dir}")
        self.content_dir = content_dir
        
        # Überprüfen, ob die Komponente existiert
        horizon_path = os.path.join(content_dir, 'Components', 'ArtificialHorizon.qml')
        self.assertTrue(os.path.exists(horizon_path), f"ArtificialHorizon.qml nicht gefunden: {horizon_path}")
        
    def tearDown(self):
        """Cleanup nach jedem Test"""
        # Engine leeren
        self.engine.clearComponentCache()
        self.engine = None

    def test_horizon_loads_without_image(self):
        """Testen, ob der künstliche Horizont ohne Bilddatei korrekt geladen wird"""
        # Testkomponente erstellen, die den künstlichen Horizont verwendet
        test_qml = """
        import QtQuick 2.15
        import QtQuick.Controls 2.15
        
        Rectangle {
            width: 400
            height: 400
            color: "#333333"
            
            // Importiere die ArtificialHorizon-Komponente
            ArtificialHorizon {
                id: horizon
                anchors.centerIn: parent
                width: 300
                height: 300
                
                // Testbare Eigenschaften setzen
                roll: 10.0
                pitch: 5.0
                disarmed: true
            }
            
            // Text Anzeige für Test-Status
            Text {
                id: statusText
                anchors.top: parent.top
                anchors.horizontalCenter: parent.horizontalCenter
                text: "Horizon geladen: " + (horizon.visible ? "Ja" : "Nein")
                color: "white"
                font.pixelSize: 16
            }
        }
        """
        
        # Temporäre QML-Datei für den Test erstellen
        test_file = os.path.join(os.path.dirname(__file__), "temp_test_horizon.qml")
        with open(test_file, "w") as f:
            f.write(test_qml)
        
        try:
            # Importpfade setzen
            self.engine.addImportPath(self.content_dir)

            # QML laden und testen
            self.engine.load(QUrl.fromLocalFile(test_file))
            
            # Warten, bis QML geladen ist
            self.assertTrue(len(self.engine.rootObjects()) > 0, "QML konnte nicht geladen werden")
            root = self.engine.rootObjects()[0]
            
            # Sicherstellen, dass der Horizont sichtbar ist
            horizon = root.findChild(root, "horizon")
            self.assertIsNotNone(horizon, "Horizont wurde nicht gefunden")
            self.assertTrue(horizon.property("visible"), "Horizont ist nicht sichtbar")
            
            # Eigenschaften testen
            self.assertAlmostEqual(horizon.property("roll"), 10.0, places=1)
            self.assertAlmostEqual(horizon.property("pitch"), 5.0, places=1)
            self.assertTrue(horizon.property("disarmed"), "Disarmed-Eigenschaft nicht korrekt")
            
            # Test auf verwendete Farben (standardmäßig)
            self.assertEqual(horizon.property("skyColor"), "#3399ff")
            self.assertEqual(horizon.property("groundColor"), "#996600")
            
        finally:
            # Temporäre Datei aufräumen
            if os.path.exists(test_file):
                os.remove(test_file)

    def test_horizon_responds_to_property_changes(self):
        """Testen, ob der künstliche Horizont auf Eigenschaftsänderungen reagiert"""
        # Testkomponente wie oben, aber mit Zugriff auf interne Elemente
        test_qml = """
        import QtQuick 2.15
        import QtQuick.Controls 2.15
        
        Item {
            id: testRoot
            width: 400
            height: 400
            
            // Funktion, um die Rotation und Pitch programmatisch zu ändern
            function updateValues(newRoll, newPitch) {
                horizon.roll = newRoll;
                horizon.pitch = newPitch;
                return true;
            }
            
            ArtificialHorizon {
                id: horizon
                objectName: "horizon"
                anchors.centerIn: parent
                width: 300
                height: 300
            }
        }
        """
        
        # Temporäre QML-Datei für den Test erstellen
        test_file = os.path.join(os.path.dirname(__file__), "temp_test_horizon_props.qml")
        with open(test_file, "w") as f:
            f.write(test_qml)
        
        try:
            # Importpfade setzen
            self.engine.addImportPath(self.content_dir)
            
            # QML laden und testen
            self.engine.load(QUrl.fromLocalFile(test_file))
            self.assertTrue(len(self.engine.rootObjects()) > 0, "QML konnte nicht geladen werden")
            
            root = self.engine.rootObjects()[0]
            
            # Werte ändern und überprüfen
            success = root.metaObject().invokeMethod(root, 
                                                    "updateValues", 
                                                    Qt.ConnectionType.DirectConnection, 
                                                    Qt.Q_RETURN_ARG(bool), 
                                                    Qt.Q_ARG(float, 20.0), 
                                                    Qt.Q_ARG(float, 15.0))
            
            self.assertTrue(success, "Konnte Methode nicht aufrufen")
            
            # Finden des Horizon-Objekts und überprüfen der Werte
            horizon = root.findChild(QQuickWindow, "horizon")
            self.assertIsNotNone(horizon, "Konnte das Horizon-Objekt nicht finden")
            
            # Zeit geben, damit die Änderungen wirksam werden
            QTimer.singleShot(100, self.app.quit)
            self.app.exec()
            
            # Überprüfen der neuen Werte
            self.assertAlmostEqual(horizon.property("roll"), 20.0, places=1)
            self.assertAlmostEqual(horizon.property("pitch"), 15.0, places=1)
            
        finally:
            # Temporäre Datei aufräumen
            if os.path.exists(test_file):
                os.remove(test_file)


if __name__ == '__main__':
    unittest.main()
