#!/bin/bash

# RZGCS macOS Build Script
# Simplified build script for development and testing

set -e

echo "=== RZGCS macOS Build ==="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

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

# Check for Python
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed"
    exit 1
fi

# Setup Python environment
setup_python() {
    print_status "Setting up Python environment..."
    
    cd Python
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_status "Created virtual environment"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    print_status "Installing dependencies..."
    pip install --upgrade pip
    pip install -r requirements_macos.txt
    
    cd ..
    print_status "Python environment ready"
}

# Create minimal app bundle
create_app_bundle() {
    print_status "Creating app bundle..."
    
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
</dict>
</plist>
EOF
    
    # Create launcher script
    cat > "$APP_MACOS/RZGCS" << 'EOF'
#!/bin/bash

# RZGCS macOS Launcher

# Get app directory
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
RESOURCES_DIR="$APP_DIR/Contents/Resources"

# Change to resources directory
cd "$RESOURCES_DIR"

# Activate Python virtual environment
source Python/venv/bin/activate

# Set environment variables
export PYTHONPATH="$RESOURCES_DIR/Python:$PYTHONPATH"
export QT_MAC_WANTS_LAYER=1

# Launch application
python3 main.py
EOF
    
    # Make launcher executable
    chmod +x "$APP_MACOS/RZGCS"
    
    # Copy project files
    print_status "Copying project files..."
    cp -r Python "$APP_RESOURCES/"
    cp -r RZGCSContent "$APP_RESOURCES/"
    cp main.py "$APP_RESOURCES/"
    
    print_status "App bundle created: $APP_NAME"
}

# Test the build
test_build() {
    print_status "Testing the build..."
    
    if [ -d "RZGCS.app" ]; then
        print_status "App bundle exists"
        
        # Test launcher script
        if [ -x "RZGCS.app/Contents/MacOS/RZGCS" ]; then
            print_status "Launcher script is executable"
        else
            print_warning "Launcher script is not executable"
        fi
        
        # Test Python environment
        if [ -d "RZGCS.app/Contents/Resources/Python/venv" ]; then
            print_status "Python virtual environment exists"
        else
            print_warning "Python virtual environment missing"
        fi
        
        # Test main.py
        if [ -f "RZGCS.app/Contents/Resources/main.py" ]; then
            print_status "Main script exists"
        else
            print_warning "Main script missing"
        fi
        
    else
        print_error "App bundle not found"
        exit 1
    fi
}

# Main build process
main() {
    print_status "Starting RZGCS macOS build..."
    
    setup_python
    create_app_bundle
    test_build
    
    print_status "=== Build Complete ==="
    print_status "App bundle: RZGCS.app"
    print_status ""
    print_status "To run:"
    print_status "  open RZGCS.app"
    print_status ""
    print_status "To test from command line:"
    print_status "  ./RZGCS.app/Contents/MacOS/RZGCS"
}

# Run main function
main "$@" 