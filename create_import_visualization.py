#!/usr/bin/env python3
"""
RZGCS Import Graph Visualizer für dronekit_main.py
Erstellt eine vollständige Visualisierung aller Imports mit Frontend und Backend
"""

import json
import networkx as nx
import matplotlib.pyplot as plt
from pathlib import Path
import matplotlib.patches as mpatches

def load_dependency_report():
    """Lädt den Dependency-Report"""
    with open('dependency_report.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def get_dronekit_main_imports(report):
    """Ermittelt alle direkten Imports von dronekit_main.py"""
    dronekit_imports = []
    for edge in report['import_graph']['edges']:
        if edge[0] == 'Python\\dronekit_main.py':
            dronekit_imports.append(edge[1])
    return dronekit_imports

def get_recursive_imports(report, start_modules, max_depth=3):
    """Ermittelt rekursive Imports bis zu einer bestimmten Tiefe"""
    graph = nx.DiGraph()
    visited = set()
    
    def add_imports(module, depth=0):
        if depth > max_depth or module in visited:
            return
        
        visited.add(module)
        
        # Finde alle Imports für dieses Modul
        for edge in report['import_graph']['edges']:
            if edge[0] == module:
                target = edge[1]
                graph.add_edge(module, target)
                
                # Rekursiv für interne Module
                if not is_external_package(target):
                    add_imports(target, depth + 1)
    
    for module in start_modules:
        add_imports(module)
    
    return graph

def is_external_package(module_name):
    """Bestimmt ob ein Modul ein externes Paket ist"""
    external_prefixes = [
        'PySide6', 'pymavlink', 'mavsdk', 'dronekit', 'numpy', 'matplotlib',
        'serial', 'requests', 'cryptography', 'psutil', 'qasync'
    ]
    
    for prefix in external_prefixes:
        if module_name.startswith(prefix):
            return True
    
    return False

def categorize_module(module_name):
    """Kategorisiert ein Modul als Frontend, Backend oder External"""
    if is_external_package(module_name):
        return 'external'
    elif module_name.startswith('backend'):
        return 'backend'
    elif any(module_name.startswith(prefix) for prefix in ['viewmodel', 'viewmodels', 'dummy', 'RZGCSContent']):
        return 'frontend'
    else:
        return 'other'

def create_visualization():
    """Erstellt die vollständige Visualisierung"""
    print("Lade Dependency-Report...")
    report = load_dependency_report()
    
    print("Ermittle dronekit_main.py Imports...")
    dronekit_imports = get_dronekit_main_imports(report)
    
    print(f"Direkte Imports gefunden: {len(dronekit_imports)}")
    for imp in dronekit_imports:
        print(f"  - {imp}")
    
    print("Erstelle rekursiven Import-Graphen...")
    graph = get_recursive_imports(report, ['Python\\dronekit_main.py'] + dronekit_imports)
    
    print(f"Graphen erstellt mit {len(graph.nodes())} Knoten und {len(graph.edges())} Kanten")
    
    # Erstelle die Visualisierung
    plt.figure(figsize=(20, 16))
    
    # Position der Knoten
    pos = nx.spring_layout(graph, k=2, iterations=50, seed=42)
    
    # Kategorisiere Knoten
    node_colors = []
    node_sizes = []
    
    for node in graph.nodes():
        category = categorize_module(node)
        if category == 'backend':
            node_colors.append('#ff9999')  # Rot für Backend
            node_sizes.append(800)
        elif category == 'frontend':
            node_colors.append('#99ff99')  # Grün für Frontend
            node_sizes.append(600)
        elif category == 'external':
            node_colors.append('#9999ff')  # Blau für External
            node_sizes.append(400)
        else:
            node_colors.append('#ffff99')  # Gelb für Other
            node_sizes.append(500)
    
    # Zeichne Knoten
    nx.draw_networkx_nodes(graph, pos, 
                          node_color=node_colors,
                          node_size=node_sizes,
                          alpha=0.8)
    
    # Zeichne Kanten
    nx.draw_networkx_edges(graph, pos,
                          edge_color='gray',
                          arrows=True,
                          arrowsize=15,
                          alpha=0.6)
    
    # Beschriftungen (nur für wichtige Knoten)
    labels = {}
    for node in graph.nodes():
        if (node == 'Python\\dronekit_main.py' or 
            node.startswith('backend.') or
            node.startswith('viewmodel.') or
            node.startswith('dummy_') or
            len(node) < 30):
            labels[node] = node.replace('Python\\', '').replace('backend.', '')
    
    nx.draw_networkx_labels(graph, pos, labels,
                           font_size=8,
                           font_family='monospace',
                           font_weight='bold')
    
    # Legende
    legend_elements = [
        mpatches.Patch(color='#ff9999', label='Backend'),
        mpatches.Patch(color='#99ff99', label='Frontend'),
        mpatches.Patch(color='#9999ff', label='External'),
        mpatches.Patch(color='#ffff99', label='Other')
    ]
    plt.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(0, 1))
    
    plt.title("RZGCS Import Graph - dronekit_main.py\n(Frontend: Grün, Backend: Rot, External: Blau)", 
              fontsize=16, fontweight='bold')
    plt.axis('off')
    
    # Speichere das Bild
    output_file = 'dronekit_main_import_graph.png'
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Visualisierung gespeichert als: {output_file}")
    
    # Erstelle auch eine vereinfachte Version
    create_simplified_visualization(graph, dronekit_imports)

def create_simplified_visualization(graph, dronekit_imports):
    """Erstellt eine vereinfachte Visualisierung nur der direkten Abhängigkeiten"""
    plt.figure(figsize=(16, 12))
    
    # Erstelle Subgraph nur mit direkten Imports und deren direkten Abhängigkeiten
    important_nodes = {'Python\\dronekit_main.py'} | set(dronekit_imports)
    
    # Füge direkte Abhängigkeiten der Imports hinzu
    for node in dronekit_imports:
        for edge in graph.edges():
            if edge[0] == node:
                important_nodes.add(edge[1])
    
    subgraph = graph.subgraph(important_nodes)
    
    # Position
    pos = nx.spring_layout(subgraph, k=3, iterations=50, seed=42)
    
    # Kategorisiere Knoten
    node_colors = []
    node_sizes = []
    
    for node in subgraph.nodes():
        category = categorize_module(node)
        if node == 'Python\\dronekit_main.py':
            node_colors.append('#ff0000')  # Rot für Hauptdatei
            node_sizes.append(1200)
        elif category == 'backend':
            node_colors.append('#ff9999')
            node_sizes.append(800)
        elif category == 'frontend':
            node_colors.append('#99ff99')
            node_sizes.append(600)
        elif category == 'external':
            node_colors.append('#9999ff')
            node_sizes.append(400)
        else:
            node_colors.append('#ffff99')
            node_sizes.append(500)
    
    # Zeichne Knoten
    nx.draw_networkx_nodes(subgraph, pos, 
                          node_color=node_colors,
                          node_size=node_sizes,
                          alpha=0.8)
    
    # Zeichne Kanten
    nx.draw_networkx_edges(subgraph, pos,
                          edge_color='gray',
                          arrows=True,
                          arrowsize=20,
                          alpha=0.7)
    
    # Beschriftungen
    labels = {}
    for node in subgraph.nodes():
        if node == 'Python\\dronekit_main.py':
            labels[node] = 'dronekit_main.py'
        else:
            # Vereinfachte Namen
            name = node.replace('Python\\', '').replace('backend.', '')
            if len(name) > 25:
                name = name[:22] + '...'
            labels[node] = name
    
    nx.draw_networkx_labels(subgraph, pos, labels,
                           font_size=9,
                           font_family='monospace',
                           font_weight='bold')
    
    # Legende
    legend_elements = [
        mpatches.Patch(color='#ff0000', label='dronekit_main.py'),
        mpatches.Patch(color='#ff9999', label='Backend'),
        mpatches.Patch(color='#99ff99', label='Frontend'),
        mpatches.Patch(color='#9999ff', label='External'),
        mpatches.Patch(color='#ffff99', label='Other')
    ]
    plt.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(0, 1))
    
    plt.title("RZGCS Import Graph - Vereinfacht\n(dronekit_main.py und direkte Abhängigkeiten)", 
              fontsize=16, fontweight='bold')
    plt.axis('off')
    
    # Speichere das Bild
    output_file = 'dronekit_main_import_graph_simplified.png'
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Vereinfachte Visualisierung gespeichert als: {output_file}")

def create_dot_file():
    """Erstellt eine DOT-Datei für Graphviz"""
    report = load_dependency_report()
    dronekit_imports = get_dronekit_main_imports(report)
    graph = get_recursive_imports(report, ['Python\\dronekit_main.py'] + dronekit_imports)
    
    dot_content = """digraph dronekit_main_imports {
    rankdir=TB;
    node [shape=box, style=filled, fontname="Arial", fontsize=10];
    edge [fontname="Arial", fontsize=8];
    
    // Hauptdatei
    "dronekit_main.py" [fillcolor="#ff0000", fontcolor=white, fontsize=12, fontweight=bold];
    
"""
    
    # Füge Knoten hinzu
    for node in graph.nodes():
        if node == 'Python\\dronekit_main.py':
            continue
        
        category = categorize_module(node)
        if category == 'backend':
            color = '#ff9999'
        elif category == 'frontend':
            color = '#99ff99'
        elif category == 'external':
            color = '#9999ff'
        else:
            color = '#ffff99'
        
        node_name = node.replace('Python\\', '').replace('backend.', '')
        dot_content += f'    "{node_name}" [fillcolor="{color}"];\n'
    
    # Füge Kanten hinzu
    for edge in graph.edges():
        source = edge[0].replace('Python\\', '').replace('backend.', '')
        target = edge[1].replace('Python\\', '').replace('backend.', '')
        dot_content += f'    "{source}" -> "{target}";\n'
    
    dot_content += "}\n"
    
    with open('dronekit_main_imports.dot', 'w', encoding='utf-8') as f:
        f.write(dot_content)
    
    print("DOT-Datei gespeichert als: dronekit_main_imports.dot")

def create_frontend_graph():
    """Erstellt und speichert einen reinen Frontend-Import-Graphen"""
    print("Erstelle reinen Frontend-Graphen...")
    report = load_dependency_report()
    all_edges = report['import_graph']['edges']
    all_nodes = set()
    for edge in all_edges:
        all_nodes.add(edge[0])
        all_nodes.add(edge[1])
    
    # Filtere nur Frontend-Knoten
    frontend_nodes = set(n for n in all_nodes if categorize_module(n) == 'frontend')
    # Füge dronekit_main.py hinzu, falls es Frontend-Imports hat
    if categorize_module('Python\\dronekit_main.py') == 'frontend':
        frontend_nodes.add('Python\\dronekit_main.py')
    
    # Füge Kanten hinzu, bei denen beide Enden Frontend sind
    frontend_edges = [e for e in all_edges if e[0] in frontend_nodes and e[1] in frontend_nodes]
    
    # Erstelle Graph
    graph = nx.DiGraph()
    graph.add_edges_from(frontend_edges)
    
    print(f"Frontend-Knoten: {len(frontend_nodes)} | Frontend-Kanten: {len(frontend_edges)}")
    
    # Visualisierung
    plt.figure(figsize=(16, 12))
    pos = nx.spring_layout(graph, k=2, iterations=50, seed=42)
    nx.draw_networkx_nodes(graph, pos, node_color='#99ff99', node_size=700, alpha=0.9)
    nx.draw_networkx_edges(graph, pos, edge_color='gray', arrows=True, arrowsize=20, alpha=0.7)
    labels = {n: n.replace('Python\\', '').replace('viewmodel.', '').replace('viewmodels.', '').replace('dummy_', '') for n in graph.nodes()}
    nx.draw_networkx_labels(graph, pos, labels, font_size=9, font_family='monospace', font_weight='bold')
    plt.title("RZGCS Frontend Import Graph", fontsize=16, fontweight='bold')
    plt.axis('off')
    plt.tight_layout()
    plt.savefig('frontend_import_graph.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Frontend-Graph gespeichert als: frontend_import_graph.png")
    # DOT-Datei
    dot_content = "digraph frontend_imports {\n    rankdir=TB;\n    node [shape=box, style=filled, fillcolor=\"#99ff99\", fontname=Arial, fontsize=10];\n    edge [fontname=Arial, fontsize=8];\n"
    for n in graph.nodes():
        name = n.replace('Python\\', '').replace('viewmodel.', '').replace('viewmodels.', '').replace('dummy_', '')
        dot_content += f'    "{name}";\n'
    for e in graph.edges():
        src = e[0].replace('Python\\', '').replace('viewmodel.', '').replace('viewmodels.', '').replace('dummy_', '')
        tgt = e[1].replace('Python\\', '').replace('viewmodel.', '').replace('viewmodels.', '').replace('dummy_', '')
        dot_content += f'    "{src}" -> "{tgt}";\n'
    dot_content += '}\n'
    with open('frontend_import_graph.dot', 'w', encoding='utf-8') as f:
        f.write(dot_content)
    print("Frontend-DOT-Datei gespeichert als: frontend_import_graph.dot")

if __name__ == "__main__":
    try:
        print("=== RZGCS Import Graph Visualizer ===")
        create_visualization()
        create_dot_file()
        create_frontend_graph()
        print("\n=== Fertig ===")
        print("Erstellte Dateien:")
        print("- dronekit_main_import_graph.png (vollständiger Graph)")
        print("- dronekit_main_import_graph_simplified.png (vereinfachter Graph)")
        print("- dronekit_main_imports.dot (Graphviz-Datei)")
        print("- frontend_import_graph.png (nur Frontend)")
        print("- frontend_import_graph.dot (nur Frontend, Graphviz)")
    except Exception as e:
        print(f"Fehler: {e}")
        import traceback
        traceback.print_exc() 