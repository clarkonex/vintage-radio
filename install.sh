#!/bin/bash
# Terminal Radio - Linux/macOS Installation Script

set -e

echo "Terminal Radio - Installation"
echo "=============================="
echo ""

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
INSTALL_DIR="$HOME/.local/bin"
RADIO_DIR="$HOME/.local/share/terminal-radio"

# Detect OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
else
    echo "Unsupported OS: $OSTYPE"
    exit 1
fi

echo "Detected OS: $OS"
echo ""

# Check for Python 3
if command -v python3 &> /dev/null; then
    PYTHON="python3"
elif command -v python &> /dev/null; then
    PYTHON="python"
else
    echo "Error: Python 3 is required but not installed."
    if [[ "$OS" == "linux" ]]; then
        echo "Install with: sudo apt install python3 python3-venv python3-pip"
    else
        echo "Install with: brew install python3"
    fi
    exit 1
fi

echo "Using Python: $($PYTHON --version)"

# Check for mpv
if ! command -v mpv &> /dev/null; then
    echo ""
    echo "Warning: mpv is not installed."
    if [[ "$OS" == "linux" ]]; then
        echo "Install with: sudo apt install mpv libmpv-dev"
    else
        echo "Install with: brew install mpv"
    fi
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Create installation directory
echo ""
echo "Installing to: $RADIO_DIR"
mkdir -p "$RADIO_DIR"
mkdir -p "$INSTALL_DIR"

# Copy files
cp "$SCRIPT_DIR/radio.py" "$RADIO_DIR/"
cp "$SCRIPT_DIR/requirements.txt" "$RADIO_DIR/"
cp "$SCRIPT_DIR/stations.m3u" "$RADIO_DIR/" 2>/dev/null || true

# Create virtual environment
echo ""
echo "Creating virtual environment..."
$PYTHON -m venv "$RADIO_DIR/venv"

# Install dependencies
echo "Installing dependencies..."
"$RADIO_DIR/venv/bin/pip" install --upgrade pip -q
"$RADIO_DIR/venv/bin/pip" install -r "$RADIO_DIR/requirements.txt" -q

# Create the radio command
cat > "$INSTALL_DIR/radio" << 'SCRIPT'
#!/bin/bash
RADIO_DIR="$HOME/.local/share/terminal-radio"
cd "$RADIO_DIR"
source venv/bin/activate
python radio.py "$@"
SCRIPT

chmod +x "$INSTALL_DIR/radio"

echo ""
echo "Installation complete!"
echo ""

# Check if ~/.local/bin is in PATH
if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
    echo "Add this line to your shell config (~/.bashrc or ~/.zshrc):"
    echo ""
    echo '  export PATH="$HOME/.local/bin:$PATH"'
    echo ""
    echo "Then restart your terminal or run:"
    echo "  source ~/.bashrc  (or source ~/.zshrc)"
    echo ""
else
    echo "You can now start the radio by typing: radio"
fi
