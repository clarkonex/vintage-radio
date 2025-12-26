#!/bin/bash
# Setup script for Terminal Radio

INSTALL_DIR="$HOME/.local/bin"
RADIO_DIR="$(cd "$(dirname "$0")" && pwd)"

# Create bin directory if needed
mkdir -p "$INSTALL_DIR"

# Create the radio command
cat > "$INSTALL_DIR/radio" << EOF
#!/bin/bash
cd "$RADIO_DIR"
source venv/bin/activate
python radio.py "\$@"
EOF

chmod +x "$INSTALL_DIR/radio"

# Check if ~/.local/bin is in PATH
if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
    echo ""
    echo "Add this line to your ~/.zshrc:"
    echo ""
    echo '  export PATH="$HOME/.local/bin:$PATH"'
    echo ""
    echo "Then run: source ~/.zshrc"
else
    echo "Done! You can now type 'radio' to start."
fi
