#!/bin/bash

echo "RZGCS Installation für Mac"
echo "========================="

# Prüfe Python-Installation
if ! command -v python3 &> /dev/null; then
    echo "Python 3 ist nicht installiert. Bitte installieren Sie Python 3 von python.org"
    exit 1
fi

# Erstelle virtuelle Umgebung
echo "Erstelle virtuelle Python-Umgebung..."
python3 -m venv venv

# Aktiviere virtuelle Umgebung
echo "Aktiviere virtuelle Umgebung..."
source venv/bin/activate

# Upgrade pip
echo "Aktualisiere pip..."
pip install --upgrade pip

# Installiere Abhängigkeiten
echo "Installiere benötigte Pakete..."
pip install -r requirements.txt

# Erstelle Start-Skript
echo "Erstelle Start-Skript..."
cat > start_mac.command << 'EOL'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
python main.py
EOL

# Mache Start-Skript ausführbar
chmod +x start_mac.command

echo "Installation abgeschlossen!"
echo "Sie können die Software jetzt durch Doppelklick auf 'start_mac.command' starten." 