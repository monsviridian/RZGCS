#!/usr/bin/env python3
"""
RZGCS Dependency Analyzer
Analysiert alle Imports und Dependencies im RZGCS-Projekt
"""

import os
import sys
import ast
import importlib
from pathlib import Path
from collections import defaultdict, deque
import json

class DependencyAnalyzer:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.imports = defaultdict(set)
        self.dependencies = defaultdict(set)
        self.external_packages = set()
        self.internal_modules = set()
        self.import_edges = []
        
    def analyze_file(self, file_path):
        """Analysiert eine einzelne Python-Datei"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        module_name = alias.name
                        self._add_import(file_path, module_name)
                        
                elif isinstance(node, ast.ImportFrom):
                    module_name = node.module
                    if module_name:
                        self._add_import(file_path, module_name)
                        
        except Exception as e:
            print(f"Fehler beim Analysieren von {file_path}: {e}")
    
    def _add_import(self, file_path, module_name):
        """Fügt einen Import zur Analyse hinzu"""
        relative_path = str(file_path.relative_to(self.project_root))
        
        # Bestimme ob es ein externes oder internes Modul ist
        if self._is_external_package(module_name):
            self.external_packages.add(module_name)
            self.dependencies[relative_path].add(module_name)
        else:
            self.internal_modules.add(module_name)
            self.imports[relative_path].add(module_name)
        
        # Füge zur Edge-Liste hinzu
        self.import_edges.append((relative_path, module_name))
    
    def _is_external_package(self, module_name):
        """Bestimmt ob ein Modul ein externes Paket ist"""
        # Bekannte interne Module
        internal_prefixes = [
            'backend', 'Python', 'RZGCSContent', 'RZGCS',
            'mavlink', 'dronekit', 'viewmodel', 'viewmodels',
            'dummy', 'mavlink_connector', 'dronekit_sensor_viewmodel',
            'dronekit_parameter_viewmodel', 'mission_planner_viewmodel'
        ]
        
        # Prüfe interne Präfixe
        for prefix in internal_prefixes:
            if module_name.startswith(prefix):
                return False
        
        # Standard Python-Module
        stdlib_modules = {
            'os', 'sys', 'ast', 'importlib', 'pathlib', 'collections', 
            'json', 'datetime', 'threading', 'time', 'enum', 'serial',
            'PySide6', 'PyQt5', 'QtCore', 'QtGui', 'QtQml', 'QtWidgets'
        }
        
        if module_name in stdlib_modules:
            return False
        
        # Prüfe ob es ein Standard-Python-Modul ist
        try:
            importlib.import_module(module_name)
            return True
        except ImportError:
            # Wenn es nicht importiert werden kann, ist es wahrscheinlich intern
            return False
    
    def scan_project(self):
        """Scannt das gesamte Projekt nach Python-Dateien"""
        python_files = []
        
        for root, dirs, files in os.walk(self.project_root):
            # Überspringe bestimmte Verzeichnisse
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'venv', 'build', 'dist']]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = Path(root) / file
                    python_files.append(file_path)
        
        print(f"Gefundene Python-Dateien: {len(python_files)}")
        
        for file_path in python_files:
            self.analyze_file(file_path)
    
    def get_requirements(self):
        """Ermittelt die benötigten externen Pakete"""
        requirements = set()
        
        for package in self.external_packages:
            requirements.add(package)
        
        return sorted(requirements)
    
    def create_import_graph(self):
        """Erstellt einen Import-Graphen"""
        return {
            'nodes': list(set([edge[0] for edge in self.import_edges] + [edge[1] for edge in self.import_edges])),
            'edges': self.import_edges,
            'external_packages': list(self.external_packages),
            'internal_modules': list(self.internal_modules)
        }
    
    def generate_report(self, output_file='dependency_report.json'):
        """Generiert einen detaillierten Bericht"""
        report = {
            'project_info': {
                'name': 'RZGCS',
                'root_path': str(self.project_root),
                'total_files_analyzed': len(self.imports)
            },
            'external_dependencies': self.get_requirements(),
            'internal_modules': list(self.internal_modules),
            'import_graph': self.create_import_graph(),
            'file_imports': {k: list(v) for k, v in self.imports.items()},
            'file_dependencies': {k: list(v) for k, v in self.dependencies.items()}
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"Dependency-Report gespeichert als: {output_file}")
        return report

def main():
    # Projekt-Root ermitteln
    project_root = Path(__file__).parent
    
    print("=== RZGCS Dependency Analyzer ===")
    print(f"Projekt-Root: {project_root}")
    
    # Analyzer erstellen und Projekt scannen
    analyzer = DependencyAnalyzer(project_root)
    analyzer.scan_project()
    
    # Bericht generieren
    report = analyzer.generate_report()
    
    # Zusammenfassung ausgeben
    print("\n=== ZUSAMMENFASSUNG ===")
    print(f"Externe Pakete: {len(analyzer.external_packages)}")
    print(f"Interne Module: {len(analyzer.internal_modules)}")
    print(f"Analysierte Dateien: {len(analyzer.imports)}")
    
    print("\n=== EXTERNE DEPENDENCIES ===")
    for req in analyzer.get_requirements():
        print(f"  {req}")
    
    print("\n=== INTERNE MODULE ===")
    for module in sorted(analyzer.internal_modules):
        print(f"  {module}")
    
    print("\n=== DATEIEN MIT DEN MEISTEN IMPORTS ===")
    sorted_files = sorted(analyzer.imports.items(), key=lambda x: len(x[1]), reverse=True)
    for file_path, imports in sorted_files[:10]:
        print(f"  {file_path}: {len(imports)} Imports")
        for imp in sorted(imports):
            print(f"    - {imp}")
    
    print("\n=== IMPORT GRAPH (ERSTE 20 EDGES) ===")
    for i, (source, target) in enumerate(analyzer.import_edges[:20]):
        print(f"  {source} -> {target}")

if __name__ == "__main__":
    main() 