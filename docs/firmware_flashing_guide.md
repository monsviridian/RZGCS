# ArduPilot Firmware Flashing Guide

## Übersicht

Das RZGCS Firmware-Tab ermöglicht es dir, ArduPilot-Firmware auf STM32-basierten Flugcontrollern zu flashen. Es verwendet `stm32loader` für echte Hardware-Kommunikation.

## Installation

### 1. Python-Abhängigkeiten installieren

```bash
cd Python
pip install -r requirements_firmware.txt
```

Oder manuell:
```bash
pip install stm32loader pyserial requests
```

### 2. Hardware-Verbindung

Für STM32F1-basierte Flugcontroller (Pixhawk, etc.):

- **GND** → GND
- **TX** → RX (PA10)
- **RX** → TX (PA9)
- **DTR** → RESET
- **RTS** → BOOT0
- **BOOT1** → GND

## Verwendung

### 1. Flugcontroller vorbereiten

1. **Bootloader-Modus aktivieren:**
   - BOOT0 auf HIGH setzen (3.3V)
   - BOOT1 auf LOW setzen (GND)
   - RESET drücken oder DTR toggeln

2. **Verbindung herstellen:**
   - Flugcontroller über USB verbinden
   - COM-Port wird automatisch erkannt

### 2. Firmware flashen

#### Option A: Firmware aus der Liste herunterladen

1. **RZGCS starten** und zum "Firmware"-Tab wechseln
2. **COM-Port auswählen** (wird automatisch gescannt)
3. **"Gerät verbinden"** klicken
4. **Firmware auswählen:**
   - ArduCopter (Multicopter)
   - ArduPlane (Flächenflugzeuge)
   - ArduRover (Bodenfahrzeuge)
   - ArduSub (Unterwasserfahrzeuge)
5. **"Firmware herunterladen"** klicken
6. **"Firmware flashen"** klicken

#### Option B: Eigene Firmware-Datei importieren

1. **RZGCS starten** und zum "Firmware"-Tab wechseln
2. **COM-Port auswählen** und "Gerät verbinden"
3. **"Datei auswählen"** klicken
4. **Firmware-Datei auswählen** (HEX, BIN oder PX4)
5. **"Firmware flashen"** klicken

### 3. Unterstützte Dateiformate

- **HEX-Dateien** (.hex) - Intel HEX Format
- **BIN-Dateien** (.bin) - Binary Format
- **PX4-Dateien** (.px4) - PX4 Firmware Format

**Hinweis:** HEX-Dateien werden automatisch zu BIN konvertiert.

### 4. Flash-Prozess

Der Flash-Prozess läuft automatisch ab:

1. **Flash löschen** (10%)
2. **Firmware schreiben** (40-90%)
3. **Verifizieren** (90-100%)

## Unterstützte Hardware

### STM32F1 Boards (Standard)
- Pixhawk 1
- Pixhawk 2
- Pixhawk 4
- F4V3
- F4V5
- F4V5S

### Andere STM32-Familien
- STM32F4 (Pixhawk 4, F4V3)
- STM32F7 (Pixhawk 2)
- STM32H7 (Pixhawk 6)

## Fehlerbehebung

### "Kein STM32-Gerät gefunden"
- **Bootloader-Modus prüfen:** BOOT0=HIGH, BOOT1=LOW
- **Verbindung prüfen:** TX/RX korrekt verbunden
- **Port prüfen:** Richtiger COM-Port ausgewählt
- **Treiber prüfen:** USB-Treiber installiert

### "Flash-Operation timeout"
- **Verbindung stabilisieren:** Kabel prüfen
- **Bootloader-Modus:** Gerät neu starten
- **Port-Geschwindigkeit:** 115200 Baud verwenden

### "Firmware-Schreiben fehlgeschlagen"
- **Datei prüfen:** Firmware-Download vollständig
- **Speicher prüfen:** Genügend Flash-Speicher verfügbar
- **Schutz prüfen:** Flash-Schutz deaktiviert

## Erweiterte Optionen

### Wipe Settings
- **Aktivieren:** Alle Parameter löschen
- **Deaktivieren:** Parameter beibehalten
- **Empfehlung:** Bei neuen Boards aktivieren

### Entwicklungsversionen
- **Stable:** Getestete, stabile Versionen
- **Development:** Neueste Entwicklungsversionen
- **Empfehlung:** Nur für Entwickler

## Kommandozeile

Du kannst auch direkt `stm32loader` verwenden:

```bash
# Firmware flashen
stm32loader --port COM7 --family F1 --erase --write --verify firmware.bin

# Flash lesen
stm32loader --port COM7 --family F1 --read --length 0x10000 dump.bin

# Flash löschen
stm32loader --port COM7 --family F1 --erase
```

## Sicherheitshinweise

⚠️ **Wichtig:**
- **Backup erstellen:** Vor dem Flash alle Parameter sichern
- **Stromversorgung:** Stabile Stromversorgung während des Flash
- **Nicht unterbrechen:** Flash-Prozess nicht unterbrechen
- **Richtige Firmware:** Passende Firmware für dein Board verwenden

## Support

Bei Problemen:
1. **Logs prüfen:** RZGCS-Logs für Fehlermeldungen
2. **Hardware testen:** Mit Mission Planner testen
3. **Community:** ArduPilot-Forum für Hilfe

## Technische Details

### Verwendete Tools
- **stm32loader:** Hauptwerkzeug für STM32-Kommunikation
- **pyserial:** Serielle Kommunikation
- **requests:** Firmware-Download

### Protokolle
- **USART:** STM32 Bootloader-Protokoll
- **HTTP:** Firmware-Download von ArduPilot-Servern
- **Binary:** Firmware-Format (.bin)

### Timeouts
- **Geräteerkennung:** 10 Sekunden
- **Flash-Löschung:** 30 Sekunden
- **Firmware-Schreiben:** 120 Sekunden 