# RZGCS - Drohnensteuerungssoftware

## Geschäftsmodell & Lizenzierung

### Marktübersicht

Die RZGCS (RZ Ground Control Station) ist eine fortschrittliche Drohnensteuerungssoftware mit modernem UI, umfassenden Sensordatenvisualisierungen und speziellen Funktionen wie dem Angel Mode für vorprogrammierte Flugpfade.

**Zielmarkt:**
- Hobby-Drohnenpiloten (20%)
- Professionelle Fotografen/Filmemacher (30%)
- Sicherheits- und Überwachungsunternehmen (25%)
- Landwirtschaftliche Anwendungen (15%)
- Forschung und Entwicklung (10%)

**Marktgröße:**
- Globaler Drohnenmarkt: ~€15 Milliarden (2025)
- Drohnensoftware-Segment: ~€1.8 Milliarden
- Angestrebter Marktanteil: 1-3% innerhalb von 3 Jahren

**Wettbewerb:**
- QGroundControl (Open Source)
- Mission Planner (Kostenlos)
- DJI Go/Fly (Herstellergebunden)
- Universal Ground Control (Kommerziell)

**Alleinstellungsmerkmale:**
- Intuitivere Benutzeroberfläche
- Angel Mode mit vordefinierten regionalen Flugpfaden
- Verbesserte Sensorfilterung und -visualisierung
- Plattformübergreifende Kompatibilität

### Lizenzmodell

RZGCS verwendet ein Freemium-Modell mit gestaffelten Lizenzen:

| Version | Preis | Merkmale |
|---------|-------|----------|
| Basic | Kostenlos | Grundlegende Steuerung, begrenzte Sensoren, keine fortgeschrittenen Modi |
| Professional | €99/Jahr | Alle Sensorfunktionen, Partikelanimation, erweiterte Protokollierung |
| Enterprise | €299/Jahr | Angel Mode, benutzerdefinierte Flugpfade, unbegrenzter Support, Branding-Optionen |
| OEM | Verhandlungsbasis | Individualisierbare Version für Drohnenhersteller |

### Funktionsumfang nach Lizenztyp

#### Basic (Kostenlos)
- Grundlegende Drohnensteuerung
- Basis-Sensordaten
- Einfache Vorflugchecks
- Standardvisualisierung

#### Professional (€99/Jahr)
- Alle Basic-Funktionen
- Voller Sensordatenzugriff
- Erweiterte Parametrierung
- Erweiterte Protokollierung
- Drohnenanimation
- Motortests

#### Enterprise (€299/Jahr)
- Alle Professional-Funktionen
- Angel Mode für vordefinierte Flugpfade
- Benutzerdefinierte Flugpfadprogrammierung
- Branding-Anpassungen
- Prioritätssupport

### Vertriebsstrategie

**Hauptvertriebskanäle:**
- Eigene Website (60% der Verkäufe)
- Partnerschaften mit Drohnenherstellern (25%)
- Software-Marktplätze (15%)

**Umsatzprognose:**
- Jahr 1: €104.300 (700 × €99 + 100 × €299)
- Jahr 2: €397.500 (2.500 × €99 + 500 × €299)
- Jahr 3: €1.390.000 (8.000 × €99 + 2.000 × €299)

## Lizenzierungssystem

### Technische Umsetzung

Das Lizenzierungssystem besteht aus folgenden Komponenten:

1. **LicenseManager**: Backend-Klasse zur Verwaltung von Lizenzen
   - Validierung von Lizenzschlüsseln
   - Speicherung von Lizenzinformationen
   - Feature-basierte Zugriffssteuerung

2. **LicenseController**: QML-Schnittstelle zum Lizenzmanager
   - Bereitstellung von Eigenschaften und Methoden für QML
   - Signale für Statusänderungen

3. **LicenseView**: QML-Benutzeroberfläche
   - Anzeige des aktuellen Lizenzstatus
   - Aktivierung und Deaktivierung von Lizenzen
   - Übersicht über verfügbare Lizenztypen

### Demo-Lizenzschlüssel

Für Testzwecke können folgende Schlüssel verwendet werden:

- Professional: `RZGCS-PRO-1234-5678-9ABC-DEF0`
- Enterprise: `RZGCS-ENT-ABCD-EF12-3456-789A`

### Integration in bestehende Anwendungen

Die Funktion `isFeatureEnabled("feature_name")` kann verwendet werden, um zu prüfen, ob ein bestimmtes Feature in der aktuellen Lizenz verfügbar ist. Beispiele für Feature-Namen:

- `basic_control`
- `basic_sensors`
- `all_sensors`
- `parameter_edit`
- `advanced_logging`
- `animation`
- `motor_test`
- `angel_mode`
- `custom_flight_paths`
- `branding`

## Installation und Verwendung

### Einrichtung des Lizenzierungssystems

1. Kopieren Sie die Dateien `license_manager.py` und `license_ui.py` in das Verzeichnis `backend`
2. Kopieren Sie `LicenseView.qml` in das Verzeichnis `RZGCSContent`
3. Aktualisieren Sie `main.py` und `Screen01.ui.qml` gemäß der Dokumentation

### Aktivierung einer Lizenz

1. Öffnen Sie die RZGCS-Anwendung
2. Navigieren Sie zum Tab "Lizenz"
3. Geben Sie Ihren Lizenzschlüssel ein und klicken Sie auf "Aktivieren"
4. Der Lizenzstatus wird aktualisiert und die entsprechenden Funktionen werden freigeschaltet

### Support und Kontakt

Bei Fragen zur Lizenzierung wenden Sie sich bitte an:

E-Mail: license@rzgcs.com
Telefon: +49 123 45678

---

© 2025 RZGCS GmbH. Alle Rechte vorbehalten.
