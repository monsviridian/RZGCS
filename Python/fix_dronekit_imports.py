#!/usr/bin/env python3
"""
Fix-DroneKit-Imports Script
----------------------------
Dieses Skript korrigiert alle DroneKit-Imports in den Python-Dateien im RZGCS-Projekt.
Es ersetzt 'from dronekit import X' mit 'import dronekit; X = dronekit.X'
Das hilft, zirkuläre Imports zu vermeiden und stellt sicher, dass DroneKit-Symbole
aus der externen Bibliothek importiert werden.
"""

import os
import re
import sys

def find_python_files(directory):
    """Findet alle .py Dateien in einem Verzeichnis und seinen Unterverzeichnissen"""
    python_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))
    return python_files

def fix_dronekit_imports(file_path):
    """Korrigiert DroneKit-Imports in einer Datei"""
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Suche nach 'from dronekit import X, Y, Z'
    pattern = r'from\s+dronekit\s+import\s+([^;\n]+)'
    matches = re.findall(pattern, content)

    if not matches:
        return False  # Keine Änderungen

    print(f"Fixing imports in {file_path}")
    
    for match in matches:
        symbols = [s.strip() for s in match.split(',')]
        import_line = f"from dronekit import {match}"
        
        # Ersetze den Import mit individuellen Zuweisungen
        replacement = "# External DroneKit import - fixed to avoid circular imports\n"
        replacement += "import dronekit as dronekit_external  # Externe DroneKit-Bibliothek\n"
        for symbol in symbols:
            replacement += f"{symbol} = dronekit_external.{symbol}  # Aus externer DroneKit-Bibliothek\n"
        
        content = content.replace(import_line, replacement)
    
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)
    
    return True  # Änderungen vorgenommen

def main():
    """Hauptfunktion"""
    if len(sys.argv) != 2:
        print("Usage: python fix_dronekit_imports.py <directory>")
        sys.exit(1)
    
    directory = sys.argv[1]
    if not os.path.isdir(directory):
        print(f"Error: {directory} is not a directory")
        sys.exit(1)
    
    python_files = find_python_files(directory)
    fixed_count = 0
    
    for file_path in python_files:
        if fix_dronekit_imports(file_path):
            fixed_count += 1
    
    print(f"Fixed DroneKit imports in {fixed_count} files")

if __name__ == "__main__":
    main()
