# RZGCS Benutzerhandbuch

## Inhalt

1. [Einfu00fchrung](#einfu00fchrung)
2. [Installation](#installation)
   - [Systemanforderungen](#systemanforderungen)
   - [Windows-Installation](#windows-installation)
   - [macOS-Installation](#macos-installation)
3. [Erste Schritte](#erste-schritte)
   - [Programmstart](#programmstart)
   - [Benutzerinterface-u00dcbersicht](#benutzerinterface-%C3%BCbersicht)
4. [Verbindung herstellen](#verbindung-herstellen)
   - [Verbindung mit echtem Flugcontroller](#verbindung-mit-echtem-flugcontroller)
   - [Simulator-Modus](#simulator-modus)
5. [Hauptfunktionen](#hauptfunktionen)
   - [Preflight-View](#preflight-view)
   - [Sensordaten-Anzeige](#sensordaten-anzeige)
   - [Parametereinstellungen](#parametereinstellungen)
   - [Kalibrierung](#kalibrierung)
   - [Motortest](#motortest)
   - [Flugansicht](#flugansicht)
   - [Angel Mode](#angel-mode) (Enterprise-Lizenz erforderlich)
6. [Lizenzierung](#lizenzierung)
   - [Lizenztypen und Features](#lizenztypen-und-features)
   - [Lizenzaktivierung](#lizenzaktivierung)
   - [Lizenzverwaltung](#lizenzverwaltung)
7. [Fehlerbehebung](#fehlerbehebung)
8. [Support](#support)
9. [Hu00e4ufig gestellte Fragen](#h%C3%A4ufig-gestellte-fragen)

## Einfu00fchrung

RZGCS (Remotely-Operated Zone Ground Control Station) ist eine fortschrittliche Bodenstation zur Steuerung und u00dcberwachung von Drohnen. Die Software bietet umfangreiche Funktionen fu00fcr die Flugplanung, Sensordatenvisualisierung, Parametrierung und Kalibrierung von Flugcontrollern.

Diese Dokumentation bietet einen umfassenden u00dcberblick u00fcber alle Funktionen der RZGCS-Software und hilft Ihnen, das volle Potenzial Ihrer Drohne auszuschu00f6pfen.

## Installation

### Systemanforderungen

**Minimum:**
- Betriebssystem: Windows 10 (64-bit), macOS 10.15 oder neuer
- Prozessor: Intel Core i5 oder AMD Ryzen 5
- RAM: 8 GB
- Grafikkarte: DirectX 11 kompatible GPU mit 2 GB VRAM
- Speicherplatz: 500 MB freier Festplattenspeicher
- Bildschirmauflu00f6sung: 1280 x 720

**Empfohlen:**
- Betriebssystem: Windows 11 (64-bit), macOS 12 oder neuer
- Prozessor: Intel Core i7 oder AMD Ryzen 7
- RAM: 16 GB
- Grafikkarte: DirectX 12 kompatible GPU mit 4 GB VRAM
- Speicherplatz: 1 GB freier Festplattenspeicher
- Bildschirmauflu00f6sung: 1920 x 1080 oder hu00f6her

### Windows-Installation

1. Laden Sie das Installationsprogramm von der offiziellen Website herunter
2. Fu00fchren Sie die Datei `RZGCS_Setup.exe` aus
3. Folgen Sie den Anweisungen des Installationsassistenten
4. Nach Abschluss der Installation finden Sie das RZGCS-Symbol auf Ihrem Desktop

### macOS-Installation

1. Laden Sie die DMG-Datei von der offiziellen Website herunter
2. u00d6ffnen Sie die heruntergeladene Datei `RZGCS.dmg`
3. Ziehen Sie das RZGCS-Symbol in den Anwendungsordner
4. Beim ersten Start mu00fcssen Sie evtl. Sicherheitsberechtigungen erteilen:
   - Gehen Sie zu "Systemeinstellungen > Sicherheit & Datenschutz"
   - Erteilen Sie die Erlaubnis zum u00d6ffnen der App
   - Erteilen Sie ggf. Zugriff auf USB-Geru00e4te fu00fcr die Verbindung mit dem Flugcontroller

## Erste Schritte

### Programmstart

Nach erfolgreicher Installation ku00f6nnen Sie RZGCS u00fcber das Desktop-Symbol oder aus dem Anwendungsordner starten. Beim ersten Start erscheint ein Willkommensbildschirm mit Informationen zur aktuellen Lizenz und den verfu00fcgbaren Funktionen.

### Benutzerinterface-u00dcbersicht

Das RZGCS-Interface ist in verschiedene Bereiche unterteilt:

1. **Verbindungskontrollleiste** (oben): Hier ku00f6nnen Sie den Port und die Baudrate auswu00e4hlen sowie die Verbindung herstellen oder trennen.

2. **Haupt-Tabs** (Mitte): u00dcber diese Tabs ku00f6nnen Sie zwischen den verschiedenen Ansichten wechseln:
   - Preflight
   - Sensoren
   - Parameter
   - Kalibrierung
   - Motortest
   - Flug
   - Angel Mode (nur mit Enterprise-Lizenz)
   - Lizenz

3. **Statusleiste** (unten): Zeigt Verbindungsstatus, Protokollmeldungen und wichtige Systeminformationen an.

## Verbindung herstellen

### Verbindung mit echtem Flugcontroller

1. Schlieu00dfen Sie Ihren Flugcontroller per USB an den Computer an
2. Wu00e4hlen Sie in der Verbindungskontrollleiste den entsprechenden Port aus:
   - Windows: COMx (z.B. COM8)
   - macOS: /dev/cu.usbmodem... oder /dev/cu.SLAB_USBtoUART
3. Wu00e4hlen Sie die korrekte Baudrate (Standard: 57600 fu00fcr ArduPilot, 115200 fu00fcr PX4)
4. Klicken Sie auf "Connect"
5. Nach erfolgreicher Verbindung sollten Sie eine Heartbeat-Meldung sehen

**Hinweis fu00fcr macOS-Benutzer:** Bei Verbindungsproblemen pru00fcfen Sie, ob die erforderlichen Zugriffsrechte erteilt wurden. Gehen Sie zu "Systemeinstellungen > Sicherheit & Datenschutz > Datenschutz" und stellen Sie sicher, dass RZGCS Zugriff auf USB-Geru00e4te hat.

### Simulator-Modus

RZGCS bietet einen integrierten Simulator-Modus zum Testen und u00dcben:

1. Wu00e4hlen Sie "Simulator" aus der Port-Dropdown-Liste
2. Klicken Sie auf "Connect"
3. Der Simulator stellt automatisch simulierte Sensordaten und Parameter bereit

## Hauptfunktionen

### Preflight-View

Die Preflight-Ansicht bietet eine u00dcbersicht u00fcber die wichtigsten Systeminformationen vor dem Flug:

- **Drohnenanimation**: Zeigt eine 3D-Visualisierung der Drohne mit Animationen der Startsequenz
- **Systemstatus**: Zeigt den Status wichtiger Subsysteme wie GPS, Batterie, Sensoren
- **Preflight-Checkliste**: u00dcbersicht u00fcber wichtige Pru00fcfpunkte vor dem Start
- **Logbereich**: Hervorgehobene Darstellung wichtiger Systemmeldungen

### Sensordaten-Anzeige

Die Sensoransicht visualisiert alle verfu00fcgbaren Sensordaten in Echtzeit:

- **Attitude**: Lage der Drohne (Roll, Pitch, Yaw)
- **GPS**: Position, Geschwindigkeit, Satellitenstatus
- **Batterie**: Spannung, Strom, verbleibende Kapazitu00e4t
- **Barometer**: Hu00f6he, Druck, Temperatur
- **Magnetometer**: Magnetfeldwerte, Kompassrichtung

### Parametereinstellungen

Hier ku00f6nnen Sie alle Parameter des Flugcontrollers einsehen und konfigurieren:

- **Parametersuche**: Schnelles Finden spezifischer Parameter
- **Kategoriefilter**: Gruppierung der Parameter nach Funktion
- **Werteu00e4nderung**: u00c4ndern und Speichern von Parameterwerten
- **Parameter-Datei**: Speichern und Laden von Parameterkonfigurationen

**Hinweis**: Fu00fcr die Parameteru00e4nderung ist mindestens eine Professional-Lizenz erforderlich.

### Kalibrierung

Die Kalibrierungsansicht ermu00f6glicht die Kalibrierung verschiedener Sensoren:

- **Beschleunigungssensor**: 6-Positionen-Kalibrierung
- **Kompass**: Vollstu00e4ndige Rotation in allen Achsen
- **Level-Kalibrierung**: Horizontale Ausrichtung
- **Radio-Kalibrierung**: Einstellung der Fernbedienungskanu00e4le

### Motortest

Der Motortest ermu00f6glicht das sichere Testen einzelner Motoren am Boden:

- **Motorauswahl**: Auswahl des zu testenden Motors
- **Drehzahleinstellung**: Regelung der Testdrehzahl
- **Sicherheitsfunktionen**: Automatische Abschaltung bei Problemen

**Achtung**: Entfernen Sie vor dem Motortest immer die Propeller!

### Flugansicht

Die Flugansicht bietet eine umfassende u00dcbersicht wu00e4hrend des Flugs:

- **Kartendarstellung**: Position der Drohne in Echtzeit
- **Telemetriedaten**: Wichtige Flugdaten wie Hu00f6he, Geschwindigkeit, Entfernung
- **Flugregler**: Steuerung von Flugmodi und Missionen
- **Batterieu00fcberwachung**: Anzeige des Batteriestatus mit Warnungen

### Angel Mode

**Hinweis**: Diese Funktion ist nur mit einer Enterprise-Lizenz verfu00fcgbar.

Der Angel Mode bietet spezielle Flugpfade und Missionsprofile fu00fcr verschiedene geografische Regionen:

- **Ukraine** (rot)
- **Europa/Deutschland** (blau)
- **Tu00fcrkei** (orange)
- **Nordafrika** (gru00fcn)
- **Russland** (lila)
- **Baltikum** (bernstein)
- **Grou00dfbritannien** (tu00fcrkis)
- **Naher Osten** (rotbraun)

Jede Region bietet vordefinierte Flugpfade, die auf spezifische Einsatzszenarien optimiert sind.

## Lizenzierung

### Lizenztypen und Features

RZGCS ist in drei Lizenzstufen verfu00fcgbar:

**1. Basic (Kostenlos)**
- Verbindung mit Flugcontroller/Simulator
- Grundlegende Sensordatenanzeige
- Preflight-Checks
- Einfache Flugansicht

**2. Professional (Kostenpflichtig)**
- Alle Basic-Features
- Parameteru00e4nderung und -verwaltung
- Erweiterte Kalibrierungsfunktionen
- Motortest
- Missionsplanung
- Erweiterte Flugansicht mit Telemetrie

**3. Enterprise (Kostenpflichtig)**
- Alle Professional-Features
- Angel Mode mit regionalen Flugpfaden
- Erweiterte Datenanalyse
- Prioritu00e4ts-Support
- Multidrohnen-Unterstu00fctzung

### Lizenzaktivierung

Um eine hu00f6here Lizenzstufe zu aktivieren:

1. Erwerben Sie einen Lizenzschlu00fcssel von der offiziellen Website
2. u00d6ffnen Sie in RZGCS den Tab "Lizenz"
3. Geben Sie Ihren Lizenzschlu00fcssel in das Feld "Lizenzschlu00fcssel" ein
4. Klicken Sie auf "Aktivieren"
5. Nach erfolgreicher Aktivierung werden die neuen Features sofort freigeschaltet

### Lizenzverwaltung

Im Lizenz-Tab ku00f6nnen Sie:

- Ihren aktuellen Lizenzstatus einsehen
- Ihre Lizenz auf einen anderen Computer u00fcbertragen
- Ihre Lizenz deaktivieren
- Ein Upgrade auf eine hu00f6here Lizenzstufe durchfu00fchren

## Fehlerbehebung

### Verbindungsprobleme

**Problem: RZGCS erkennt den Flugcontroller nicht**

*Windows-Lu00f6sung:*
1. u00dcberpru00fcfen Sie im Geru00e4te-Manager, ob der Controller als COM-Port erkannt wird
2. Installieren Sie ggf. die erforderlichen Treiber (CH340, CP210x, FTDI)
3. Versuchen Sie einen anderen USB-Port

*macOS-Lu00f6sung:*
1. u00dcberpru00fcfen Sie in den Systemeinstellungen die Zugriffsrechte
2. Installieren Sie ggf. die erforderlichen Treiber fu00fcr Ihren USB-Adapter
3. u00d6ffnen Sie das Terminal und fu00fchren Sie `ls /dev/cu.*` aus, um verfu00fcgbare Ports zu sehen

**Problem: Verbindung bricht regelmu00e4u00dfig ab**

1. u00dcberpru00fcfen Sie das USB-Kabel und verwenden Sie ein hochwertiges Kabel
2. Reduzieren Sie die Baudrate (z.B. von 115200 auf 57600)
3. Deaktivieren Sie stromintensive USB-Geru00e4te, die den gleichen Hub nutzen

### Systemprobleme

**Problem: RZGCS startet nicht**

1. u00dcberpru00fcfen Sie, ob alle Abhu00e4ngigkeiten installiert sind
2. Starten Sie Ihren Computer neu
3. Installieren Sie RZGCS neu

**Problem: Hohe CPU-Auslastung**

1. Schlieu00dfen Sie andere anspruchsvolle Anwendungen
2. Deaktivieren Sie die 3D-Ansicht in den Einstellungen
3. Reduzieren Sie die Aktualisierungsrate der Sensordaten

## Support

Fu00fcr weitere Unterstu00fctzung nutzen Sie bitte unser Support-System:

- **Email-Support**: support@rzgcs.com
- **Live-Chat**: Verfu00fcgbar auf unserer Website wu00e4hrend der Geschu00e4ftszeiten
- **Support-Ticket**: u00dcber das integrierte Support-Tool in RZGCS
- **Wissensdatenbank**: Umfangreiche Sammlung von Lu00f6sungen und Anleitungen

## Hu00e4ufig gestellte Fragen

**F: Kann ich RZGCS auf mehreren Computern verwenden?**

A: Ja, Sie ku00f6nnen Ihre Lizenz auf bis zu zwei Computern gleichzeitig aktivieren. Fu00fcr weitere Installationen mu00fcssen Sie die Lizenz auf einem Computer deaktivieren.

**F: Funktioniert RZGCS mit allen Flugcontrollern?**

A: RZGCS unterstu00fctzt alle gu00e4ngigen Flugcontroller, die das MAVLink-Protokoll verwenden, darunter:
- ArduPilot (Pixhawk, Cube, etc.)
- PX4
- APM

**F: Wie oft werden Updates veru00f6ffentlicht?**

A: Wir veru00f6ffentlichen regelmu00e4u00dfig Updates:
- Bugfixes: Monatlich
- Neue Features: Quartalsweise
- Grou00dfe Versionen: Ju00e4hrlich

**F: Kann ich meine Lizenz upgraden?**

A: Ja, Sie ku00f6nnen jederzeit von Basic zu Professional oder von Professional zu Enterprise upgraden. Sie zahlen nur die Differenz zwischen den Lizenzstufen.
