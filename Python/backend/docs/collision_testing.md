# Testdokumentation: Kollisionsvermeidung

## Übersicht

Diese Dokumentation beschreibt die Teststrategie und -implementierung für das Kollisionsvermeidungsmodul. Die Tests sind in drei Kategorien unterteilt:
- Unit Tests
- Integrationstests
- Systemtests

## Teststruktur

### Unit Tests

#### Datenmodelle (`test_collision_data.py`)

##### Testumfang
- Objekttypen (STATIC, DYNAMIC, UNKNOWN)
- Erkennungsmethoden (LIDAR, RADAR, CAMERA, FUSION)
- Ausweichstrategien (STOP, HOVER, ALTITUDE, LATERAL, COMBINED)
- Datenklassen (DetectedObject, CollisionState, etc.)
- Fehlerklassen

##### Testfälle
1. **Objekttypen**
   ```python
   def test_object_types(self):
       self.assertEqual(ObjectType.STATIC.value, "static")
       self.assertEqual(ObjectType.DYNAMIC.value, "dynamic")
       self.assertEqual(ObjectType.UNKNOWN.value, "unknown")
   ```

2. **DetectedObject**
   ```python
   def test_detected_object(self):
       obj = DetectedObject(
           id="test1",
           type=ObjectType.STATIC,
           position={"lat": 48.123, "lon": 11.456, "alt": 100.0},
           velocity={"vx": 0.0, "vy": 0.0, "vz": 0.0},
           size={"length": 5.0, "width": 3.0, "height": 2.0},
           confidence=0.95,
           detection_method=DetectionMethod.LIDAR
       )
       self.assertEqual(obj.id, "test1")
       self.assertEqual(obj.type, ObjectType.STATIC)
       # ...
   ```

#### Service (`test_collision_service.py`)

##### Testumfang
- Aktivierung/Deaktivierung
- Objekterkennung
- Ausweichmanöver
- Fehlerbehandlung
- Statistik- und Logverwaltung

##### Testfälle
1. **Aktivierung**
   ```python
   def test_activation(self):
       self.service.activate()
       self.assertTrue(self.service._state.is_active)
       self.assertFalse(self.service._state.is_error)
       self.assertIsNone(self.service._state.error_message)
   ```

2. **Objekterkennung**
   ```python
   def test_object_detection(self):
       objects = [
           DetectedObject(
               id="test1",
               type=ObjectType.STATIC,
               # ...
           )
       ]
       self.service.update_detected_objects(objects)
       self.assertEqual(len(self.service._state.detected_objects), 1)
   ```

#### ViewModel (`test_collision_viewmodel.py`)

##### Testumfang
- Properties
- Slots
- Signal-Handler
- Fehlerbehandlung

##### Testfälle
1. **Properties**
   ```python
   def test_initial_state(self):
       self.assertFalse(self.viewmodel.is_active)
       self.assertFalse(self.viewmodel.is_error)
       self.assertEqual(self.viewmodel.error_message, "")
   ```

2. **Slots**
   ```python
   def test_activation(self):
       self.viewmodel.activate()
       self.assertTrue(self.viewmodel.is_active)
   ```

### Integrationstests (`test_collision_integration.py`)

#### Testumfang
- Service-ViewModel-Interaktion
- ViewModel-View-Bindung
- Signal-Slot-Verbindungen
- Datenfluss durch alle Schichten

#### Testfälle
1. **Aktivierungsfluss**
   ```python
   def test_activation_flow(self):
       self.view.activation_requested.emit()
       self.assertTrue(self.service._state.is_active)
       self.assertTrue(self.viewmodel.is_active)
       self.assertTrue(self.view._is_active)
   ```

2. **Objekterkennungsfluss**
   ```python
   def test_object_detection_flow(self):
       objects = [DetectedObject(...)]
       self.service.update_detected_objects(objects)
       self.assertEqual(len(self.viewmodel.detected_objects), 1)
       self.assertEqual(len(self.view._detected_objects), 1)
   ```

### Systemtests (`test_collision_system.py`)

#### Testumfang
- End-to-End-Szenarien
- Fehlerszenarien
- Performance-Tests
- Gleichzeitige Operationen
- Wiederherstellungsszenarien

#### Testfälle
1. **End-to-End-Szenario**
   ```python
   def test_end_to_end_scenario(self):
       # 1. Aktivierung
       self.service.activate()
       
       # 2. Objekterkennung
       objects = [DetectedObject(...)]
       self.service.update_detected_objects(objects)
       
       # 3. Ausweichmanöver
       self.service.execute_avoidance(AvoidanceStrategy.STOP)
       
       # 4. Deaktivierung
       self.service.deactivate()
   ```

2. **Performance-Test**
   ```python
   def test_performance(self):
       start_time = time.time()
       for _ in range(100):
           self.service.update_detected_objects(objects)
       end_time = time.time()
       self.assertLess(end_time - start_time, 1.0)
   ```

## Testausführung

### Voraussetzungen
- Python 3.8 oder höher
- PySide6
- pytest (optional)

### Ausführung
```bash
# Alle Tests ausführen
python -m unittest discover tests

# Spezifische Testdatei ausführen
python -m unittest tests/test_collision_data.py

# Mit pytest
pytest tests/
```

### Testabdeckung
```bash
# Mit Coverage
coverage run -m unittest discover tests
coverage report
```

## Best Practices

### Testorganisation
- Klare Testfallbenennung
- Isolierte Testumgebung
- Saubere Testdaten
- Dokumentierte Testfälle

### Wartung
- Regelmäßige Testaktualisierung
- Überprüfung der Testabdeckung
- Anpassung an neue Anforderungen
- Dokumentation von Änderungen

### Fehlerbehandlung
- Ausführliche Fehlermeldungen
- Reproduzierbare Testfälle
- Klare Fehlerursachen
- Lösungsvorschläge

## Metriken

### Testabdeckung
- Zeilenabdeckung: >90%
- Zweigabdeckung: >85%
- Funktionsabdeckung: 100%

### Performance-Kriterien
- Objekterkennung: <10ms pro Objekt
- Ausweichmanöver: <50ms
- Gesamtantwortzeit: <100ms

### Qualitätskriterien
- Keine bekannten Fehler
- Alle Tests erfolgreich
- Dokumentation aktuell
- Code-Review bestanden

## Erweiterungen

### Geplante Tests
- KI-basierte Objekterkennung
- Erweiterte Ausweichstrategien
- 3D-Visualisierung
- Echtzeit-Simulation

### Integration
- Autonome Flugmodi
- Geofencing
- Missionsplanung
- Telemetrie 