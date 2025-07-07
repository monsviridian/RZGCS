#!/bin/bash

# RZGCS macOS Deployment Script
# This script creates a macOS app bundle for RZGCS

set -e  # Exit on any error

echo "=== RZGCS macOS Deployment ==="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    print_error "This script is designed for macOS only"
    exit 1
fi

# Check for required tools
check_requirements() {
    print_status "Checking requirements..."
    
    # Check for Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.10 or newer."
        exit 1
    fi
    
    # Check for pip
    if ! command -v pip3 &> /dev/null; then
        print_error "pip3 is not installed. Please install pip."
        exit 1
    fi
    
    # Check for git
    if ! command -v git &> /dev/null; then
        print_error "git is not installed. Please install git."
        exit 1
    fi
    
    print_status "All requirements satisfied"
}

# Setup Python virtual environment
setup_python_env() {
    print_status "Setting up Python virtual environment..."
    
    cd Python
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_status "Created virtual environment"
    else
        print_status "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install dependencies
    print_status "Installing Python dependencies..."
    pip install -r requirements.txt
    
    cd ..
    print_status "Python environment setup complete"
}

# Create macOS app bundle
create_app_bundle() {
    print_status "Creating macOS app bundle..."
    
    # Create app bundle structure
    APP_NAME="RZGCS.app"
    APP_CONTENTS="$APP_NAME/Contents"
    APP_MACOS="$APP_CONTENTS/MacOS"
    APP_RESOURCES="$APP_CONTENTS/Resources"
    
    # Remove existing app bundle
    if [ -d "$APP_NAME" ]; then
        rm -rf "$APP_NAME"
    fi
    
    # Create directory structure
    mkdir -p "$APP_MACOS"
    mkdir -p "$APP_RESOURCES"
    
    # Create Info.plist
    cat > "$APP_CONTENTS/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>RZGCS</string>
    <key>CFBundleIdentifier</key>
    <string>com.rzgcs.app</string>
    <key>CFBundleName</key>
    <string>RZGCS</string>
    <key>CFBundleDisplayName</key>
    <string>RZGCS Ground Control Station</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleSignature</key>
    <string>????</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.15</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>LSApplicationCategoryType</key>
    <string>public.app-category.utilities</string>
</dict>
</plist>
EOF
    
    # Create launcher script
    cat > "$APP_MACOS/RZGCS" << 'EOF'
#!/bin/bash

# RZGCS macOS Launcher Script

# Get the directory where the app bundle is located
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
RESOURCES_DIR="$APP_DIR/Contents/Resources"

# Change to the app directory
cd "$RESOURCES_DIR"

# Activate Python virtual environment
source Python/venv/bin/activate

# Set environment variables
export PYTHONPATH="$RESOURCES_DIR/Python:$PYTHONPATH"
export QT_MAC_WANTS_LAYER=1

# Launch the application
python3 main.py
EOF
    
    # Make launcher executable
    chmod +x "$APP_MACOS/RZGCS"
    
    # Copy project files to Resources
    print_status "Copying project files to app bundle..."
    cp -r Python "$APP_RESOURCES/"
    cp -r RZGCSContent "$APP_RESOURCES/"
    cp main.py "$APP_RESOURCES/"
    cp HOW_TO_START.md "$APP_RESOURCES/"
    cp .gitignore "$APP_RESOURCES/"
    
    # Create app icon (placeholder)
    print_status "Creating app icon..."
    # You can replace this with a proper .icns file
    touch "$APP_RESOURCES/AppIcon.icns"
    
    print_status "App bundle created: $APP_NAME"
}

# Create DMG installer
create_dmg() {
    print_status "Creating DMG installer..."
    
    DMG_NAME="RZGCS-macOS.dmg"
    
    # Remove existing DMG
    if [ -f "$DMG_NAME" ]; then
        rm "$DMG_NAME"
    fi
    
    # Create DMG
    hdiutil create -volname "RZGCS" -srcfolder "RZGCS.app" -ov -format UDZO "$DMG_NAME"
    
    print_status "DMG created: $DMG_NAME"
}

# Create installation script
create_install_script() {
    print_status "Creating installation script..."
    
    cat > "install_RZGCS_macOS.sh" << 'EOF'
#!/bin/bash

# RZGCS macOS Installation Script

set -e

echo "=== RZGCS macOS Installation ==="

# Check if we're on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "Error: This script is designed for macOS only"
    exit 1
fi

# Install to Applications folder
APP_NAME="RZGCS.app"
INSTALL_DIR="/Applications"

echo "Installing RZGCS to $INSTALL_DIR..."

# Remove existing installation
if [ -d "$INSTALL_DIR/$APP_NAME" ]; then
    echo "Removing existing installation..."
    sudo rm -rf "$INSTALL_DIR/$APP_NAME"
fi

# Copy app bundle
echo "Copying app bundle..."
sudo cp -R "$APP_NAME" "$INSTALL_DIR/"

# Set permissions
echo "Setting permissions..."
sudo chown -R root:wheel "$INSTALL_DIR/$APP_NAME"
sudo chmod -R 755 "$INSTALL_DIR/$APP_NAME"

echo "Installation complete!"
echo "You can now launch RZGCS from Applications folder"
EOF
    
    chmod +x "install_RZGCS_macOS.sh"
    print_status "Installation script created: install_RZGCS_macOS.sh"
}

# Main deployment process
main() {
    print_status "Starting RZGCS macOS deployment..."
    
    check_requirements
    setup_python_env
    create_app_bundle
    create_dmg
    create_install_script
    
    print_status "=== Deployment Complete ==="
    print_status "Files created:"
    print_status "  - RZGCS.app (macOS app bundle)"
    print_status "  - RZGCS-macOS.dmg (DMG installer)"
    print_status "  - install_RZGCS_macOS.sh (Installation script)"
    print_status ""
    print_status "To install:"
    print_status "  ./install_RZGCS_macOS.sh"
    print_status ""
    print_status "To run directly:"
    print_status "  open RZGCS.app"
}

# Run main function
main "$@" 