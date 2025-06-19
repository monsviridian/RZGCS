# Diese Funktionen sollten in support_system.py hinzugefügt werden
# Fügen Sie sie am Ende der SupportSystem-Klasse ein, vor dem Ende der Klassendefinition

@Slot(str, result=str)
def get_knowledge_base_article(self, article_id):
    """Holt einen Artikel aus der Wissensdatenbank
    
    Args:
        article_id: ID des Artikels
        
    Returns:
        str: Inhalt des Artikels als Markdown-Text
    """
    try:
        # Versuche zuerst, den Artikel lokal zu finden
        local_article_path = os.path.join(self._local_kb_path, f"{article_id}.md")
        
        if os.path.exists(local_article_path):
            with open(local_article_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.knowledgeBaseArticleLoaded.emit(article_id, content)
                return content
        
        # Wenn nicht lokal gefunden, lade einen Standardartikel
        if article_id == "connection_issues":
            content = self._get_default_connection_article()
        elif article_id == "performance_optimization":
            content = self._get_default_performance_article()
        elif article_id == "license_activation":
            content = self._get_default_license_article()
        else:
            content = f"# Artikel nicht gefunden\n\nDer angeforderte Artikel mit der ID '{article_id}' wurde nicht gefunden.\n\nBitte kontaktieren Sie den Support unter support@rzgcs.com für weitere Hilfe."
        
        # Cache den Artikel lokal für späteren Zugriff
        with open(local_article_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.knowledgeBaseArticleLoaded.emit(article_id, content)
        return content
        
    except Exception as e:
        error_msg = f"Fehler beim Laden des Artikels: {str(e)}"
        if self._logger:
            self._logger.addLog(f"[ERR] {error_msg}")
        self.errorOccurred.emit(error_msg)
        return f"# Fehler\n\nEs ist ein Fehler beim Laden des Artikels aufgetreten: {str(e)}"

@Slot(result='QVariantList')
def get_knowledge_base_categories(self):
    """Gibt die verfügbaren Kategorien der Wissensdatenbank zurück
    
    Returns:
        list: Liste der Kategorien mit IDs und Namen
    """
    # Simulierte Kategorien
    categories = [
        {"id": "getting_started", "name": "Erste Schritte"},
        {"id": "connection", "name": "Verbindung und Kommunikation"},
        {"id": "calibration", "name": "Kalibrierung"},
        {"id": "flight", "name": "Flugbetrieb"},
        {"id": "licensing", "name": "Lizenzierung"},
        {"id": "troubleshooting", "name": "Fehlerbehebung"},
    ]
    return categories

@Slot(str, result='QVariantList')
def get_articles_by_category(self, category_id):
    """Gibt Artikel einer bestimmten Kategorie zurück
    
    Args:
        category_id: ID der Kategorie
        
    Returns:
        list: Liste der Artikel in dieser Kategorie
    """
    # Simulierte Artikel pro Kategorie
    articles_by_category = {
        "getting_started": [
            {"id": "installation", "title": "Installation der Software"},
            {"id": "first_connection", "title": "Erste Verbindung mit der Drohne"},
            {"id": "ui_overview", "title": "Übersicht der Benutzeroberfläche"}
        ],
        "connection": [
            {"id": "connection_issues", "title": "Probleme mit der Verbindung lösen"},
            {"id": "mavlink_settings", "title": "MAVLink-Einstellungen"},
            {"id": "serial_ports", "title": "Serielle Ports verstehen"}
        ],
        "calibration": [
            {"id": "accel_calibration", "title": "Beschleunigungssensor kalibrieren"},
            {"id": "compass_calibration", "title": "Kompass kalibrieren"},
            {"id": "radio_calibration", "title": "Fernbedienung kalibrieren"}
        ],
        "flight": [
            {"id": "flight_modes", "title": "Flugmodi verstehen"},
            {"id": "mission_planning", "title": "Missionsplanung"},
            {"id": "angel_mode", "title": "Angel Mode nutzen"}
        ],
        "licensing": [
            {"id": "license_activation", "title": "Lizenz aktivieren"},
            {"id": "license_types", "title": "Lizenztypen und Features"},
            {"id": "license_transfer", "title": "Lizenz auf neuen Computer übertragen"}
        ],
        "troubleshooting": [
            {"id": "common_errors", "title": "Häufige Fehlermeldungen"},
            {"id": "performance_optimization", "title": "Performance-Optimierung"},
            {"id": "diagnostics", "title": "Systemdiagnose durchführen"}
        ]
    }
    
    return articles_by_category.get(category_id, [])

@Slot(result=str)
def create_support_package(self):
    """Erstellt ein Support-Paket mit Diagnosedaten und Logs
    
    Returns:
        str: Pfad zur erstellten Support-Paket-Datei
    """
    try:
        # Basisverzeichnis für Support-Pakete
        support_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                "support_packages")
        os.makedirs(support_dir, exist_ok=True)
        
        # Eindeutigen Dateinamen erstellen
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        package_filename = f"RZGCS_Support_{timestamp}.zip"
        package_path = os.path.join(support_dir, package_filename)
        
        # ZIP-Datei erstellen
        with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Systeminfo hinzufügen
            system_info = self._collect_system_info()
            zipf.writestr("system_info.json", json.dumps(system_info, indent=2))
            
            # Logs hinzufügen
            logs = self._collect_logs()
            for log_name, log_content in logs.items():
                zipf.writestr(f"logs/{log_name}", log_content)
            
            # Diagnose-Ergebnisse hinzufügen, falls vorhanden
            if self._diagnostic_results:
                zipf.writestr("diagnostics.json", json.dumps(self._diagnostic_results, indent=2))
            
            # Konfigurations- und Lizenzinformationen hinzufügen
            # (In einer realen Implementierung würde dies aus der tatsächlichen Konfiguration kommen)
            config_info = {
                "app_version": "1.0.0",
                "build_date": "2025-05-26",
                "license_info": {
                    "type": "simulated",
                    "status": "active",
                    "expiry": "2026-05-26"
                }
            }
            zipf.writestr("config_info.json", json.dumps(config_info, indent=2))
        
        if self._logger:
            self._logger.addLog(f"[OK] Support-Paket erstellt: {package_path}")
            
        return package_path
        
    except Exception as e:
        error_msg = f"Fehler beim Erstellen des Support-Pakets: {str(e)}"
        if self._logger:
            self._logger.addLog(f"[ERR] {error_msg}")
        self.errorOccurred.emit(error_msg)
        return ""

# Standardartikel für die Wissensdatenbank
def _get_default_connection_article(self):
    return """# Probleme mit der Verbindung lösen

## Häufige Verbindungsprobleme

Verbindungsprobleme zwischen RZGCS und dem Flugcontroller sind eine der häufigsten Schwierigkeiten. Hier sind Lösungen für die gängigsten Probleme:

### Flugcontroller wird nicht erkannt

#### Windows-Lösung:
1. Überprüfen Sie im Geräte-Manager, ob der Controller als COM-Port erkannt wird
2. Installieren Sie ggf. die erforderlichen Treiber (CH340, CP210x, FTDI)
3. Versuchen Sie einen anderen USB-Port

#### macOS-Lösung:
1. Überprüfen Sie in den Systemeinstellungen die Zugriffsrechte
2. Installieren Sie ggf. die erforderlichen Treiber für Ihren USB-Adapter
3. Öffnen Sie das Terminal und führen Sie `ls /dev/cu.*` aus, um verfügbare Ports zu sehen

### Verbindung bricht regelmäßig ab

1. Überprüfen Sie das USB-Kabel und verwenden Sie ein hochwertiges Kabel
2. Reduzieren Sie die Baudrate (z.B. von 115200 auf 57600)
3. Deaktivieren Sie stromintensive USB-Geräte, die den gleichen Hub nutzen

## Richtige Baudrate wählen

Die richtige Baudrate hängt vom verwendeten Flugcontroller ab:

- ArduPilot: 57600 (Standard)
- PX4: 115200 (Standard)
- APM: 115200

## Heartbeat-Fehlermeldungen verstehen

Wenn Sie eine Meldung "Waiting for heartbeat..." erhalten, prüfen Sie:

1. Stromversorgung des Flugcontrollers
2. Korrekten COM-Port und Baudrate
3. USB-Kabelverbindung

## Fortgeschrittene Fehlersuche

Wenn die grundlegenden Schritte nicht helfen:

1. Führen Sie eine Systemdiagnose durch
2. Prüfen Sie die Logdateien auf spezifische Fehlermeldungen
3. Starten Sie RZGCS mit erhöhter Protokollierung

## Unterstützung erhalten

Wenn Sie weiterhin Probleme haben, erstellen Sie ein Support-Paket und kontaktieren Sie unseren Support unter support@rzgcs.com.
"""

def _get_default_performance_article(self):
    return """# Performance-Optimierung

## Optimierung der RZGCS-Performance

Wenn RZGCS langsam läuft oder die CPU-Auslastung hoch ist, können folgende Maßnahmen helfen:

### Systemanforderungen prüfen

Stellen Sie sicher, dass Ihr System die Mindestanforderungen erfüllt:
- Windows 10/11 oder macOS 10.15+
- 8 GB RAM
- 2 GB freier Festplattenspeicher
- DirectX 11 kompatible Grafikkarte

### Software-Optimierungen

1. **3D-Visualisierung reduzieren**
   - Deaktivieren Sie 3D-Modelle in den Einstellungen
   - Reduzieren Sie die Qualität der 3D-Darstellung

2. **Datenaktualisierungsrate anpassen**
   - Verringern Sie die Aktualisierungsrate von Sensordaten
   - Reduzieren Sie die MAVLink-Datenrate (Standard ist 4 Hz)

3. **Hintergrundprozesse schließen**
   - Beenden Sie andere ressourcenintensive Anwendungen
   - Prüfen Sie den Task-Manager auf CPU-intensive Prozesse

### Hardware-Optimierungen

1. **Grafikeinstellungen**
   - Aktivieren Sie die Hardware-Beschleunigung
   - Stellen Sie sicher, dass die neuesten Grafiktreiber installiert sind

2. **Temperaturmanagement**
   - Überprüfen Sie die CPU-Temperatur während der Ausführung
   - Stellen Sie sicher, dass Lüfter und Kühlkörper staubfrei sind

3. **Festplattenleistung**
   - Stellen Sie sicher, dass ausreichend freier Speicherplatz vorhanden ist
   - Verwenden Sie nach Möglichkeit eine SSD statt einer HDD

## Optimierte Einstellungen für verschiedene Systeme

### Low-End-Systeme

- Deaktivieren Sie 3D-Visualisierungen
- Reduzieren Sie die Datenaktualisierungsrate auf 1 Hz
- Deaktivieren Sie nicht benötigte Tabs und Funktionen

### Standard-Systeme

- Verwenden Sie mittlere Grafikqualität
- Aktualisierungsrate von 2-4 Hz
- Standard-Visualisierungen

### High-End-Systeme

- Aktivieren Sie alle Visualisierungen
- Verwenden Sie hohe Grafikqualität
- Aktualisierungsrate von 10 Hz oder höher

## Diagnose durchführen

Verwenden Sie die integrierte Systemdiagnose, um Leistungsprobleme zu identifizieren:

1. Gehen Sie zum Support-Tab
2. Klicken Sie auf "Systemdiagnose durchführen"
3. Analysieren Sie die Ergebnisse der Performance-Tests

## Nach Updates suchen

Stellen Sie sicher, dass Sie die neueste Version von RZGCS verwenden, da Updates oft Leistungsverbesserungen enthalten.
"""

def _get_default_license_article(self):
    return """# Lizenz aktivieren

## Lizenzaktivierung in RZGCS

Um alle Funktionen von RZGCS nutzen zu können, müssen Sie eine Professional- oder Enterprise-Lizenz aktivieren.

### Lizenzschlüssel erhalten

1. Besuchen Sie den [RZGCS Online-Shop](https://shop.rzgcs.com)
2. Wählen Sie den gewünschten Lizenztyp (Professional oder Enterprise)
3. Schließen Sie den Kauf ab
4. Sie erhalten Ihren Lizenzschlüssel per E-Mail

### Lizenz in RZGCS aktivieren

1. Starten Sie RZGCS
2. Wechseln Sie zum Tab "Lizenz"
3. Geben Sie Ihren Lizenzschlüssel in das Feld "Lizenzschlüssel" ein
4. Klicken Sie auf "Aktivieren"
5. Nach erfolgreicher Aktivierung werden die neuen Features sofort freigeschaltet

### Aktivierungsprobleme lösen

#### Fehlermeldung: "Ungültiger Lizenzschlüssel"

- Überprüfen Sie die korrekte Eingabe des Schlüssels (einschließlich Bindestriche)
- Stellen Sie sicher, dass keine Leerzeichen am Anfang oder Ende vorhanden sind
- Überprüfen Sie Groß-/Kleinschreibung

#### Fehlermeldung: "Lizenzaktivierung fehlgeschlagen"

- Stellen Sie sicher, dass Ihr Computer mit dem Internet verbunden ist
- Überprüfen Sie, ob der Lizenzschlüssel bereits auf einem anderen Computer aktiviert wurde
- Kontaktieren Sie den Support unter support@rzgcs.com

#### Fehlermeldung: "Maschinenbindung fehlgeschlagen"

- Dies kann auftreten, wenn die Hardware-ID Ihres Computers nicht ordnungsgemäß gelesen werden kann
- Starten Sie RZGCS mit Administratorrechten
- Deaktivieren Sie temporär Antivirensoftware, die den Zugriff blockieren könnte

## Lizenztypen und Features

### Basic (Kostenlos)
- Verbindung mit Flugcontroller/Simulator
- Grundlegende Sensordatenanzeige
- Preflight-Checks
- Einfache Flugansicht

### Professional (Kostenpflichtig)
- Alle Basic-Features
- Parameteränderung und -verwaltung
- Erweiterte Kalibrierungsfunktionen
- Motortest
- Missionsplanung
- Erweiterte Flugansicht mit Telemetrie

### Enterprise (Kostenpflichtig)
- Alle Professional-Features
- Angel Mode mit regionalen Flugpfaden
- Erweiterte Datenanalyse
- Prioritäts-Support
- Multidrohnen-Unterstützung

## Lizenzübertragung

Um Ihre Lizenz auf einen anderen Computer zu übertragen:

1. Deaktivieren Sie die Lizenz auf dem alten Computer:
   - Gehen Sie zum Tab "Lizenz"
   - Klicken Sie auf "Lizenz deaktivieren"
   - Bestätigen Sie den Vorgang

2. Aktivieren Sie die Lizenz auf dem neuen Computer:
   - Installieren Sie RZGCS
   - Geben Sie denselben Lizenzschlüssel ein
   - Klicken Sie auf "Aktivieren"

**Hinweis:** Eine Lizenz kann auf bis zu zwei Computern gleichzeitig aktiviert sein. Für weitere Installationen müssen Sie die Lizenz auf einem Computer deaktivieren.
"""
