import os
import json
import hashlib
import datetime
import sys
import uuid
import base64
from PySide6.QtCore import QObject, Signal, Slot, Property

class LicenseManager(QObject):
    licenseStatusChanged = Signal(bool)
    licenseTypeChanged = Signal(str)
    licenseExpiryChanged = Signal(str)
    
    def __init__(self, app_id="com.rzgcs.controller"):
        super().__init__()
        self._app_id = app_id
        self._license_key = ""
        self._license_valid = False
        self._license_type = "Basic"
        self._license_expiry = None
        self._features_enabled = {}
        
        # Einfacher Schutz fu00fcr lokale Lizenzdaten
        self._encryption_key = hashlib.sha256("RZGCS_LICENSE_KEY".encode()).digest()
        
        # Standardmu00e4u00dfig aktivierte Features fu00fcr Basic-Version
        self._feature_matrix = {
            "Basic": ["basic_control", "basic_sensors", "preflight_view"],
            "Professional": ["basic_control", "basic_sensors", "preflight_view", 
                            "all_sensors", "parameter_edit", "advanced_logging", 
                            "animation", "motor_test"],
            "Enterprise": ["basic_control", "basic_sensors", "preflight_view", 
                          "all_sensors", "parameter_edit", "advanced_logging", 
                          "animation", "motor_test", "angel_mode", 
                          "custom_flight_paths", "branding"]
        }
        
        # Versuche, gespeicherte Lizenz zu laden
        self._load_license()
    
    @Property(bool, notify=licenseStatusChanged)
    def license_valid(self):
        return self._license_valid
    
    @Property(str, notify=licenseTypeChanged)
    def license_type(self):
        return self._license_type
    
    @Property(str, notify=licenseExpiryChanged)
    def license_expiry(self):
        if self._license_expiry:
            return self._license_expiry.strftime("%Y-%m-%d")
        return "Unbegrenzt (Basic)"
    
    @Slot(str, result=bool)
    def activate_license(self, license_key):
        """Aktiviert einen Lizenzschlu00fcssel"""
        if not license_key:
            return False
            
        # In einer realen Implementierung wu00fcrde hier eine Serverabfrage stehen
        # Fu00fcr dieses Beispiel simulieren wir eine erfolgreiche Aktivierung
        
        try:
            # Simulierte Serverabfrage
            license_data = self._validate_with_server(license_key)
            
            if license_data.get("valid", False):
                self._license_key = license_key
                self._license_valid = True
                self._license_type = license_data.get("type", "Basic")
                
                # Ablaufdatum setzen
                expiry_str = license_data.get("expiry")
                if expiry_str:
                    self._license_expiry = datetime.datetime.fromisoformat(expiry_str)
                
                # Features basierend auf Lizenztyp aktivieren
                self._update_features()
                
                # Lizenz lokal speichern
                self._save_license()
                
                # Signale emittieren
                self.licenseStatusChanged.emit(True)
                self.licenseTypeChanged.emit(self._license_type)
                self.licenseExpiryChanged.emit(self.license_expiry)
                
                return True
                
        except Exception as e:
            print(f"Fehler bei der Lizenzaktivierung: {str(e)}")
        
        return False
    
    @Slot(result=bool)
    def deactivate_license(self):
        """Deaktiviert den aktuellen Lizenzschlu00fcssel"""
        if not self._license_key:
            return True
            
        try:
            # In einer realen Implementierung wu00fcrde hier eine Serverabfrage stehen
            # Simulierte erfolgreiche Deaktivierung
            
            # Zuru00fcck zur Basic-Version
            self._license_key = ""
            self._license_valid = False
            self._license_type = "Basic"
            self._license_expiry = None
            
            # Features aktualisieren
            self._update_features()
            
            # Gespeicherte Lizenz lu00f6schen
            self._delete_license()
            
            # Signale emittieren
            self.licenseStatusChanged.emit(False)
            self.licenseTypeChanged.emit("Basic")
            self.licenseExpiryChanged.emit(self.license_expiry)
            
            return True
            
        except Exception as e:
            print(f"Fehler bei der Lizenzdeaktivierung: {str(e)}")
            
        return False
    
    @Slot(str, result=bool)
    def is_feature_enabled(self, feature_name):
        """Pru00fcft, ob ein bestimmtes Feature in der aktuellen Lizenz aktiviert ist"""
        return feature_name in self._features_enabled
    
    def _update_features(self):
        """Aktiviert Features basierend auf dem aktuellen Lizenztyp"""
        self._features_enabled = {}
        
        if self._license_type in self._feature_matrix:
            for feature in self._feature_matrix[self._license_type]:
                self._features_enabled[feature] = True
    
    def _validate_with_server(self, license_key):
        """
        Validiert einen Lizenzschlu00fcssel mit dem Lizenzserver
        In einer realen Implementierung wu00fcrde hier eine echte API-Abfrage stehen
        """
        # Simuliert eine Serverantwort basierend auf dem Lizenzschlu00fcssel
        # Im echten System wu00fcrde hier eine verschlu00fcsselte Kommunikation mit dem Server stattfinden
        
        # Demo-Lizenzschlu00fcssel fu00fcr Testzwecke
        if license_key == "RZGCS-PRO-1234-5678-9ABC-DEF0":
            return {
                "valid": True,
                "type": "Professional",
                "expiry": (datetime.datetime.now() + datetime.timedelta(days=365)).isoformat(),
                "customer_id": "demo_user_pro"
            }
        elif license_key == "RZGCS-ENT-ABCD-EF12-3456-789A":
            return {
                "valid": True,
                "type": "Enterprise",
                "expiry": (datetime.datetime.now() + datetime.timedelta(days=365)).isoformat(),
                "customer_id": "demo_user_enterprise"
            }
        
        # Ungu00fcltige Lizenz
        return {"valid": False}
    
    def _get_machine_id(self):
        """Generiert eine eindeutige ID fu00fcr den Computer"""
        machine_id = ""
        
        try:
            if os.path.isfile("/etc/machine-id"):
                with open("/etc/machine-id", "r") as f:
                    machine_id = f.read().strip()
            elif os.path.isfile("/var/lib/dbus/machine-id"):
                with open("/var/lib/dbus/machine-id", "r") as f:
                    machine_id = f.read().strip()
            elif sys.platform == "win32":
                import winreg
                registry = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
                key = winreg.OpenKey(registry, r"SOFTWARE\Microsoft\Cryptography")
                machine_id, _ = winreg.QueryValueEx(key, "MachineGuid")
            elif sys.platform == "darwin":
                import subprocess
                machine_id = subprocess.check_output(["/usr/sbin/ioreg", "-rd1", "-c", "IOPlatformExpertDevice"]).decode()
                machine_id = machine_id.split("IOPlatformUUID")[1].split('"')[2]
        except:
            # Fallback-Lu00f6sung - nicht ideal, aber besser als nichts
            machine_id = str(uuid.getnode())
            
        return machine_id
    
    def _get_license_path(self):
        """Liefert den Pfad zur Lizenzdatei"""
        app_data_dir = ""
        if sys.platform == "win32":
            app_data_dir = os.path.join(os.environ["APPDATA"], "RZGCS")
        elif sys.platform == "darwin":
            app_data_dir = os.path.join(os.path.expanduser("~"), "Library", "Application Support", "RZGCS")
        else:
            app_data_dir = os.path.join(os.path.expanduser("~"), ".config", "RZGCS")
            
        os.makedirs(app_data_dir, exist_ok=True)
        return os.path.join(app_data_dir, "license.dat")
    
    def _save_license(self):
        """Speichert die Lizenzinformationen lokal"""
        try:
            license_data = {
                "key": self._license_key,
                "type": self._license_type,
                "machine_id": self._get_machine_id(),
                "app_id": self._app_id
            }
            
            if self._license_expiry:
                license_data["expiry"] = self._license_expiry.isoformat()
                
            # Daten einfach kodieren
            json_data = json.dumps(license_data).encode()
            encrypted_data = base64.b64encode(json_data)
            
            # In Datei speichern
            with open(self._get_license_path(), "wb") as f:
                f.write(encrypted_data)
                
        except Exception as e:
            print(f"Fehler beim Speichern der Lizenz: {str(e)}")
    
    def _load_license(self):
        """Lu00e4dt gespeicherte Lizenzinformationen"""
        try:
            license_path = self._get_license_path()
            if not os.path.isfile(license_path):
                return False
                
            with open(license_path, "rb") as f:
                encrypted_data = f.read()
                
            # Daten dekodieren
            json_data = base64.b64decode(encrypted_data)
            license_data = json.loads(json_data.decode())
            
            # u00dcberpru00fcfen der Maschinenkennung
            if license_data.get("machine_id") != self._get_machine_id():
                print("Warnung: Lizenz wurde auf einem anderen Computer aktiviert")
                return False
                
            # Lizenzinformationen u00fcbernehmen
            self._license_key = license_data.get("key", "")
            self._license_type = license_data.get("type", "Basic")
            
            # Ablaufdatum pru00fcfen
            expiry_str = license_data.get("expiry")
            if expiry_str:
                self._license_expiry = datetime.datetime.fromisoformat(expiry_str)
                
                # Pru00fcfen, ob die Lizenz abgelaufen ist
                if datetime.datetime.now() > self._license_expiry:
                    print("Lizenz ist abgelaufen")
                    self._license_valid = False
                    self._license_type = "Basic"
                    self._license_expiry = None
                    return False
            
            # Lizenz als gu00fcltig markieren und Features aktualisieren
            self._license_valid = True
            self._update_features()
            
            # Signale emittieren
            self.licenseStatusChanged.emit(True)
            self.licenseTypeChanged.emit(self._license_type)
            self.licenseExpiryChanged.emit(self.license_expiry)
            
            return True
            
        except Exception as e:
            print(f"Fehler beim Laden der Lizenz: {str(e)}")
            
        return False
    
    def _delete_license(self):
        """Lu00f6scht die gespeicherte Lizenzdatei"""
        try:
            license_path = self._get_license_path()
            if os.path.isfile(license_path):
                os.remove(license_path)
                return True
        except Exception as e:
            print(f"Fehler beim Lu00f6schen der Lizenz: {str(e)}")
            
        return False
