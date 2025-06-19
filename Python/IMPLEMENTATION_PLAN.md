# RZGCS MAVLink Integration: Implementierungsplan

## Übersicht
Dieser Implementierungsplan beschreibt die Integration der bestehenden Backend-Module `connection`, `flight_control` und `telemetry` in die Frontend-Komponenten der RZGCS-Anwendung. Das Ziel ist die vollständige Umstellung auf MAVLink-Kommunikation ohne MAVSDK-Abhängigkeiten unter Beibehaltung der MVVM-Architektur.

## Architektur
Die RZGCS-Anwendung folgt einer strikten MVVM-Architektur (Model-View-ViewModel):
- **Model**: Datenstruktur und Geschäftslogik in den Backend-Modulen
- **ViewModel**: Verbindungsschicht zwischen Model und View
- **View**: QML-basierte UI-Komponenten

## Aktuelle Fortschritte (Stand: 08.06.2025)

✅ **SensorManager Integration**
- ✅ SensorManager zu einem eigenständigen ViewModel umgebaut
- ✅ Interne Sensorwertspeicherung implementiert
- ✅ Filterung basierend auf Zeitintervallen und Wertschwellen
- ✅ QML-Integration und Signal-Emission verbessert
- ✅ Umfangreiches Debug-Logging hinzugefügt

✅ **SerialConnector Refaktorierung**
- ✅ MAVSDK-Abhängigkeiten vollständig entfernt
- ✅ Korrekte Nutzung der connect()-Methode ohne Parameter
- ✅ Richtige Porteinstellungen vor Verbindung
- ✅ Signal-Verbindungen zwischen MessageHandler und SensorManager

✅ **Verbesserte Connection-Komponente**
- ✅ Integration des erweiterten ConnectionManager
- ✅ ConnectionSecurity und BandwidthManager hinzugefügt
- ✅ Status-, Error- und Message-Handler implementiert
- ✅ Verschlüsselungs- und Bandbreiten-Management-Funktionalität

## Implementierungsphasen

### Phase 1: Connection-Modul Integration ✅
- ✅ Neue ConnectionView in RZGCSContent erstellt 
- ✅ ConnectionViewModel registriert
- ✅ Verbindungsparameter konfiguriert
- ✅ Universelle connect-Methode an UI angebunden
- ✅ Verbindungsstatusanzeige implementiert
- ✅ Tab für ConnectionView integriert
- ✅ Erweiterten ConnectionManager in SerialConnector integriert

### Phase 2: MAVLink-basierter Nachrichtenaustausch 🔄
- ✅ MessageHandler für MAVLink-Nachrichten optimiert
- ✅ Signalverbindungen für Sensordaten eingerichtet
- 🔄 MAVLink-Nachrichten-Parser vervollständigen
- Nachrichtenverarbeitung für verschiedene MAVLink-Typen implementieren
- Fehlerbehandlung bei unbekannten MAVLink-Nachrichtentypen

### Phase 3: Flight Control-Modul Integration
- Neue Views aus backend/flight_control/views integrieren:
  - AutonomousView.qml
  - GeofenceView.qml
  - CollisionView.qml
- FlightControlManager als ViewModel implementieren
- MAVLink-basierte Missionsplanung und -ausführung
- Geofence-Funktionalitäten anbinden

### Phase 4: Telemetrie-Modul Integration 🔄
- 🔄 TelemetryManager als eigenständiges ViewModel implementieren
- 🔄 Verbindung mit SensorManager optimieren
- Nachrichtenfilterungssystem für Telemetriedaten implementieren
- Datenvisualisierung in bestehende UI einbinden
- Preflight-Infoanzeige mit spezieller Filterung verbessern

### Phase 5: Menüstruktur und Navigation
- ✅ Tab für ConnectionView in die Menüstruktur integriert
- Navigation zwischen den Views optimieren
- Kontextsensitive Hilfe implementieren
- Einheitliches Fehlermanagement

## Technische Details

### MAVLink Integration
- Standard-Baudrate: 115200
- Verbindungsformate: COM-Ports, UDP, TCP
- Nachrichtenfilterung:
  - Wertänderungsbasiert: Nur bei signifikanten Änderungen (≥ 0.5%)
  - Zeitintervallbasiert: Minimale Update-Intervalle pro Sensortyp
  - Prioritätsbasiert: Kritische Sensoren (Battery, GPS) mit höherer Priorität

### ViewModel-Registrierung
- QML-Typ-Registrierung in main.py
- Kontextpropertybindung für die UI
- Signal-Slot-Verbindungen zwischen Backend und Frontend
- Eigenständige ViewModels ohne externe Modelabhängigkeiten

### Security und Bandbreite
- Verschlüsselungsoptionen für sichere Verbindungen
- Bandbreitenverwaltung mit konfigurierbaren Limits
- Adaptives Nachrichtenstreaming basierend auf verfügbarer Bandbreite

### UI-Integration
- Material Design-Richtlinien befolgen
- Konsistentes Farbschema und Layout
- Responsive Design für verschiedene Bildschirmgrößen

## Testverfahren
Nach jeder Implementierungsphase:
1. Unit-Tests für Backend-Komponenten
2. Integrationstests für UI-Backend-Verbindung
3. End-to-End-Tests mit simulierten MAVLink-Nachrichten
4. Verbindungstests mit realer Hardware
5. Lasttest für die Nachrichtenverarbeitung

## Nächste Schritte

1. **MessageHandler vervollständigen** - Erweitern der MAVLink-Nachrichtentypenverarbeitung
2. **TelemetryManager implementieren** - Als ViewModel mit eigener Datenhaltung
3. **FlightControlManager einbinden** - Vollständige Integration der Flugsteuerungskomponenten
4. **QML-Integration optimieren** - UI-Komponenten für alle ViewModels verbinden
