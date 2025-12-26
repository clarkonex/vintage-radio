# Terminal Radio - Installation

## Voraussetzungen

### Linux (Debian/Ubuntu)
```bash
sudo apt install python3 python3-venv python3-pip mpv libmpv-dev
```

### Linux (Arch)
```bash
sudo pacman -S python python-pip mpv
```

### Linux (Fedora)
```bash
sudo dnf install python3 python3-pip mpv mpv-devel
```

### macOS
```bash
brew install python3 mpv
```

## Installation

### 1. Projekt herunterladen

```bash
# Falls per Git
git clone <repo-url> ~/terminal_radio

# Oder per scp von einem anderen Rechner
scp -r user@host:~/terminal_radio ~/terminal_radio
```

### 2. Installationsskript ausführen

```bash
cd ~/terminal_radio
./install.sh
```

### 3. PATH konfigurieren (falls nicht bereits vorhanden)

**Bash:**
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

**Zsh:**
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

## Benutzung

```bash
radio
```

## Tastenkürzel

| Taste | Funktion |
|-------|----------|
| `↑` `↓` | Sender wählen |
| `Enter` | Sender abspielen |
| `Space` | Play/Pause |
| `+` `-` | Lautstärke |
| `m` | Stumm |
| `t` | Theme wechseln |
| `q` | Beenden |

## Deinstallation

```bash
rm -rf ~/.local/share/terminal-radio
rm ~/.local/bin/radio
```
