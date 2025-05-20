"""
Sicherheitstests für die RZ Ground Control Station.
Diese Tests überprüfen potenzielle Sicherheitslücken und Schwachstellen.
"""
import pytest
import sys
import os
import re
import glob
from unittest.mock import MagicMock, patch
from backend.logger import Logger

# Korrekte Pfadangaben für Import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestSecurity:
    """Sicherheitstests für die RZ Ground Control Station."""
    
    def test_no_hardcoded_credentials(self):
        """Testet, dass keine Anmeldedaten im Code hart codiert sind."""
        # Pfad zum Projektverzeichnis
        project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        
        # Regex-Muster für potenzielle Anmeldedaten
        patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'passwd\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'api[_\s]?key\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']'
        ]
        
        # Liste der Dateien, die gescannt werden sollen
        python_files = glob.glob(os.path.join(project_dir, 'Python', '**', '*.py'), recursive=True)
        qml_files = glob.glob(os.path.join(project_dir, 'RZGCSContent', '**', '*.qml'), recursive=True)
        ui_files = glob.glob(os.path.join(project_dir, 'RZGCSContent', '**', '*.ui.qml'), recursive=True)
        
        all_files = python_files + qml_files + ui_files
        
        # Zulässige Test-Anmeldedaten (können ignoriert werden)
        whitelist = [
            'password = "test_password"',  # Nur für Tests
            'api_key = "TEST_KEY"',        # Nur für Tests
            'secret = "DEBUG_SECRET"'      # Nur für Debugging
        ]
        
        # Problematische Zeilen sammeln
        issues = []
        
        for file_path in all_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    for pattern in patterns:
                        matches = re.finditer(pattern, content, re.IGNORECASE)
                        for match in matches:
                            line = match.group(0)
                            
                            # Whitelisted Einträge ignorieren
                            if any(white in line for white in whitelist):
                                continue
                                
                            # Relative Dateipfad für bessere Lesbarkeit
                            rel_path = os.path.relpath(file_path, project_dir)
                            issues.append(f"{rel_path}: {line}")
            except Exception as e:
                print(f"Fehler beim Lesen von {file_path}: {e}")
        
        # Assert - Keine Probleme gefunden
        assert len(issues) == 0, f"Potenziell unsichere Anmeldedaten gefunden:\n" + "\n".join(issues)
    
    def test_input_validation(self):
        """Testet die Eingabevalidierung für kritische Funktionen."""
        # Import der zu testenden Module
        from backend.mavlink_connector import MAVLinkConnector, create_connector, ConnectorType
        
        # Mock Logger erstellen
        mock_logger = MagicMock(spec=Logger)
        
        # Test 1: MAVLinkConnector mit ungültigen Eingaben
        connector = MAVLinkConnector(mock_logger)
        
        with pytest.raises(ValueError):
            connector.set_connection_params("", 0)  # Leerer Port und ungültige Baudrate
            
        with pytest.raises(ValueError):
            connector.set_connection_params("COM1", -1)  # Negative Baudrate
        
        # Test 2: Factory-Methode mit ungültigen Parametern
        with pytest.raises(ValueError):
            create_connector(ConnectorType.PYMAVLINK, port="")  # Fehlende baudrate
            
        with pytest.raises(ValueError):
            create_connector(ConnectorType.PYMAVLINK, baudrate=115200)  # Fehlender port
    
    def test_no_command_injection(self):
        """Testet die Robustheit gegen Command-Injection-Angriffe."""
        # Import der zu testenden Module
        from backend.mavlink_connector import MAVLinkConnector
        
        # Mock Logger erstellen
        mock_logger = MagicMock(spec=Logger)
        
        # Methode mocken, um direkte Aufrufe zu verhindern
        with patch('serial.Serial') as mock_serial:
            # Mock-Instanz konfigurieren
            mock_instance = MagicMock()
            mock_serial.return_value = mock_instance
            mock_instance.is_open = True
            
            # Test mit potenziell gefährlichen Port-Namen
            malicious_ports = [
                "COM1; rm -rf /",
                "COM1 && del /f /s /q *",
                "COM1` echo pwned`",
                "COM1$(cat /etc/passwd)",
                "COM1|whoami"
            ]
            
            for port in malicious_ports:
                # Sicherstellen, dass keine Ausnahme auftritt, aber auch kein System-Befehl ausgeführt wird
                connector = MAVLinkConnector(mock_logger)
                connector.set_connection_params(port, 115200)
                connector.connect()
                
                # Überprüfen, ob der Port-Name unverändert an Serial übergeben wurde
                # (Kein Versuch, Befehle zu interpretieren)
                mock_serial.assert_called_with(port, 115200, timeout=1.0)
