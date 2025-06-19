import os
import platform
import sys
import logging
import serial.tools.list_ports
from typing import List, Dict, Optional, Tuple, Union

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Plattformunabhu00e4ngiger Manager fu00fcr MAVLink-Verbindungen.
    
    Diese Klasse behandelt plattformspezifische Unterschiede bei seriellen Ports,
    Verbindungsparametern und Netzwerkverbindungen fu00fcr MAVLink.
    """
    
    def __init__(self):
        self.system_platform = platform.system().lower()
        self.is_executable = getattr(sys, 'frozen', False)
        logger.info(f"Initialisiere ConnectionManager fu00fcr Plattform: {self.system_platform}")
        logger.info(f"Wird als ausfu00fchrbare Datei ausgefuhrt: {self.is_executable}")
    
    def get_available_ports(self) -> List[Dict[str, str]]:
        """Gibt eine Liste von verfu00fcgbaren seriellen Ports zuru00fcck, plattformunabhu00e4ngig formatiert.
        
        Returns:
            List[Dict[str, str]]: Liste mit Dictionarys, die Informationen u00fcber die verfu00fcgbaren Ports enthalten.
                                   Jedes Dictionary enthu00e4lt 'port', 'description' und 'hwid'.
        """
        ports = []
        try:
            available_ports = list(serial.tools.list_ports.comports())
            
            for port in available_ports:
                port_info = {
                    'port': port.device,
                    'description': port.description,
                    'hwid': port.hwid
                }
                
                # Spezielle Behandlung fu00fcr verschiedene Plattformen
                if self.system_platform == 'windows':
                    # Windows kann bestimmte Ports blockieren, wenn sie bereits geu00f6ffnet sind
                    try:
                        test_connection = serial.Serial(port.device)
                        test_connection.close()
                        port_info['status'] = 'available'
                    except Exception:
                        port_info['status'] = 'possibly_in_use'
                
                elif self.system_platform == 'darwin':  # macOS
                    # macOS hat besondere Regeln fu00fcr Bluetooth-Verbindungen und USB-Geru00e4te
                    if 'bluetooth' in port.description.lower():
                        port_info['type'] = 'bluetooth'
                    elif 'usb' in port.description.lower():
                        port_info['type'] = 'usb'
                        
                    # Typische macOS-Ports fu00fcr Flight Controller erkennen
                    if 'cu.usbmodem' in port.device:
                        port_info['probable_fc'] = True  # Wahrscheinlich ein Flight Controller
                    elif 'cu.SLAB_USBtoUART' in port.device:
                        port_info['probable_fc'] = True  # Silabs CP210x Adapter (ha00fcufig)
                
                elif self.system_platform == 'linux':
                    # Linux, einschließlich Raspberry Pi
                    if os.path.exists('/etc/rpi-issue'):  # Raspberry Pi-Erkennung
                        # Auf dem Pi brauchen wir mu00f6glicherweise spezielle Zugriffsrechte
                        port_info['requires_sudo'] = not os.access(port.device, os.W_OK)
                    
                    # Unterscheiden zwischen verschiedenen Arten von Verbindungen
                    if 'ttyACM' in port.device:
                        port_info['type'] = 'arduino_compatible'
                    elif 'ttyUSB' in port.device:
                        port_info['type'] = 'usb_serial'
                    elif 'ttyS' in port.device:
                        port_info['type'] = 'hardware_serial'
                
                ports.append(port_info)
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der verfu00fcgbaren Ports: {str(e)}")
        
        return ports
    
    def get_default_connection_params(self) -> Dict[str, Union[str, int]]:
        """Liefert plattformspezifische Standardverbindungsparameter.
        
        Returns:
            Dict[str, Union[str, int]]: Dictionary mit Standardverbindungsparametern.
        """
        params = {
            'baudrate': 57600,  # Standardwert fu00fcr die meisten MAVLink-Verbindungen
            'timeout': 3.0
        }
        
        # Plattformspezifische Standardports
        if self.system_platform == 'windows':
            params['port'] = 'COM8'  # Hu00e4ufiger Standard auf Windows
        elif self.system_platform == 'darwin':
            # macOS verwendet verschiedene Port-Muster, versuche sie zu erkennen
            available_ports = self.get_available_ports()
            for port_info in available_ports:
                if port_info.get('probable_fc', False):
                    params['port'] = port_info['port']  # Verwende den ersten erkannten FC-Port
                    break
            else:  # Wenn keine wahrscheinlichen FC-Ports gefunden wurden
                if any('cu.usbmodem' in p['port'] for p in available_ports):
                    for p in available_ports:
                        if 'cu.usbmodem' in p['port']:
                            params['port'] = p['port']
                            break
                else:
                    params['port'] = '/dev/cu.usbmodem1'  # Typisch fu00fcr macOS
        elif self.system_platform == 'linux':
            if os.path.exists('/etc/rpi-issue'):  # Raspberry Pi
                params['port'] = '/dev/ttyAMA0'  # Typisch fu00fcr Raspberry Pi
            else:
                params['port'] = '/dev/ttyUSB0'  # Typisch fu00fcr Linux
        
        # Spezielle Behandlung fu00fcr ausfu00fchrbare Dateien
        if self.is_executable:
            # Wenn als ausfu00fchrbare Datei ausgefu00fchrt, mu00fcssen wir mu00f6glicherweise
            # Pfade anpassen oder andere spezielle Einstellungen vornehmen
            logger.info(f"Verwende ausfu00fchrbare-spezifische Einstellungen fu00fcr {self.system_platform}")
            
            # Beispiel: Bei Windows-Installationen mu00fcssen wir eventuell Berechtigungen u00fcberpru00fcfen
            if self.system_platform == 'windows':
                # Zusätzliche Windows-spezifische Logik für ausführbare Dateien
                pass
        
        return params
    
    def create_connection_string(self, 
                               connection_type: str, 
                               **kwargs) -> str:
        """Erstellt einen plattformspezifisch formatierten Verbindungsstring.
        
        Args:
            connection_type: Art der Verbindung ('serial', 'udp', 'tcp')
            **kwargs: Zusätzliche Parameter für die Verbindung
        
        Returns:
            str: Formatierter Verbindungsstring für die MAVLink-Verbindung
        """
        if connection_type == 'serial':
            port = kwargs.get('port')
            baud = kwargs.get('baudrate', 57600)
            
            # Sicherstellen, dass wir einen gültigen Port haben
            if not port:
                port = self.get_default_connection_params()['port']
            
            # Auf Windows müssen wir sicherstellen, dass der Port korrekt formatiert ist
            if self.system_platform == 'windows' and not port.startswith('COM'):
                # Versuche, den Port zu korrigieren
                if port.isdigit():
                    port = f"COM{port}"
            
            # Für Windows-Verbindungen: nur den Portnamen zurückgeben (die Baudrate wird separat übergeben)
            # Pymavlink erwartet auf Windows keine Baudrate im String
            return port
        
        elif connection_type == 'udp':
            host = kwargs.get('host', '127.0.0.1')
            port = kwargs.get('port', 14550)
            return f"udp:{host}:{port}"
        
        elif connection_type == 'tcp':
            host = kwargs.get('host', '127.0.0.1')
            port = kwargs.get('port', 5760)
            return f"tcp:{host}:{port}"
        
        else:
            logger.error(f"Unbekannter Verbindungstyp: {connection_type}")
            return ""
    
    def get_connection_config_for_deployment(self) -> Dict[str, any]:
        """Liefert Konfigurationsinformationen für das Deployment auf der aktuellen Plattform.
        
        Diese Methode wird verwendet, um plattformspezifische Informationen für das
        Deployment-Skript bereitzustellen.
        
        Returns:
            Dict[str, any]: Konfigurationsinformationen für das Deployment
        """
        config = {
            'platform': self.system_platform,
            'is_executable': self.is_executable,
            'connection_params': self.get_default_connection_params(),
            'special_instructions': []
        }
        
        # Plattformspezifische Anweisungen hinzufügen
        if self.system_platform == 'windows':
            config['special_instructions'].append(
                "Windows-Benutzer mu00fcssen mu00f6glicherweise den korrekten COM-Port in den Einstellungen ausw00e4hlen."
            )
        elif self.system_platform == 'darwin':
            config['special_instructions'].extend([
                "macOS-Benutzer mu00fcssen Sicherheitsberechtigungen fu00fcr USB-Geru00e4te erteilen:",
                "1. Gehen Sie zu 'Systemeinstellungen > Sicherheit & Datenschutz'",
                "2. Wechseln Sie zur Registerkarte 'Datenschutz'",
                "3. Stellen Sie sicher, dass RZGCS Zugriff auf USB-Geru00e4te hat",
                "4. Port-Benennungskonvention: /dev/cu.usbmodem* oder /dev/cu.SLAB_USBtoUART fu00fcr CP210x-Adapter"
            ])
        elif self.system_platform == 'linux':
            if os.path.exists('/etc/rpi-issue'):  # Raspberry Pi
                config['special_instructions'].append(
                    "Raspberry Pi-Benutzer mu00fcssen sicherstellen, dass der Benutzer in der 'dialout'-Gruppe ist."
                )
            else:
                config['special_instructions'].append(
                    "Linux-Benutzer mu00fcssen mu00f6glicherweise Zugriffsrechte fu00fcr serielle Ports mit 'sudo chmod 666 /dev/ttyX' erteilen."
                )
        
        return config


# Beispiel für die Verwendung
def main():
    """Beispiel für die Verwendung des ConnectionManagers."""
    connection_manager = ConnectionManager()
    print(f"Verfügbare Ports: {connection_manager.get_available_ports()}")
    print(f"Standardverbindungsparameter: {connection_manager.get_default_connection_params()}")
    print(f"Beispiel-Verbindungsstring (seriell): {connection_manager.create_connection_string('serial')}")
    print(f"Deployment-Konfiguration: {connection_manager.get_connection_config_for_deployment()}")


if __name__ == "__main__":
    main()
