# Vintage Radio

A retro-style internet radio player for the terminal.

```
╔══════════════════════════════════════════════════════════════════════════════════════╗
║                                    ~ R A D I O ~                                     ║
║  ╭────────────────────────────────────────────────────────────────╮  ╭────────────╮  ║
║  │  |      SomaFM Groove Salad                         PLAYING   │  │ │ │ │ │ │ │ │  ║
║  │  |      00:42              VOL: 60%                           │  │ │ │ │ │ │ │ │  ║
║  ╰────────────────────────────────────────────────────────────────╯  │ │ │ │ │ │ │ │  ║
║       [ |<< ]    [ > PLAY ]    [ [] STOP ]    [ >>| ]                │ │ │ │ │ │ │ │  ║
║  ╭────────────────────────────────────────────────────────────────╮  │ │ │ │ │ │ │ │  ║
║  │  ▶ 1. SomaFM Groove Salad                                     │  │ │ │ │ │ │ │ │  ║
║  │    2. SomaFM Drone Zone                                       │  ╰────────────╯  ║
║  │    3. KEXP Seattle                                            │                   ║
║  ╰────────────────────────────────────────────────────────────────╯                   ║
╚══════════════════════════════════════════════════════════════════════════════════════╝
```

## Features

- Retro radio UI with speaker grill and VU meters
- Real-time audio level visualization via ffmpeg
- 8 beautiful themes (Retro, Synthwave, Dracula, Nord, Gruvbox, and more)
- Add your own stations
- Keyboard-driven interface

## Installation

### From PyPI

```bash
pip install vintage-radio
```

### From source

```bash
git clone https://github.com/philjung/terminal-radio
cd terminal-radio
pip install .
```

### Requirements

- Python 3.9+
- [mpv](https://mpv.io/) - for audio playback
- ffmpeg (optional) - for VU meter visualization

On macOS:
```bash
brew install mpv ffmpeg
```

On Linux:
```bash
sudo apt install mpv ffmpeg  # Debian/Ubuntu
```

## Usage

```bash
radio
```

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Space` | Play / Pause |
| `S` | Stop |
| `N` | Next station |
| `P` | Previous station |
| `↑` / `↓` | Volume up / down |
| `A` | Add new station |
| `T` | Switch theme |
| `Q` | Quit |

## Themes

Switch themes with `T`:

- **Bakelite** - Dark brown with brass accents (default)
- **Retro Radio** - Warm wood tones
- **Mint Retro** - Silver with teal accents
- **Vintage Cream** - Light beige and brown
- **Synthwave** - Neon pink and cyan
- **Dracula** - Purple and green
- **Gruvbox** - Orange and earthy tones
- **Nord** - Cool arctic blues

## Configuration

Your stations are stored in `~/.config/terminal-radio/stations.m3u`. You can edit this file directly or add stations via the app with `A`.

Example format:
```m3u
#EXTM3U

#EXTINF:-1,SomaFM Groove Salad
http://ice1.somafm.com/groovesalad-128-mp3

#EXTINF:-1,KEXP Seattle
http://live-mp3-128.kexp.org/kexp128.mp3
```

## License

MIT

## Author

Phil Jung
