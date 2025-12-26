#!/usr/bin/env python3
"""
Terminal Radio - A retro-style internet radio player for the terminal by phil jung
"""

import re
import shutil
import subprocess
import threading
from pathlib import Path
from dataclasses import dataclass


def get_config_dir() -> Path:
    """Get the user config directory, creating it if needed."""
    config_dir = Path.home() / ".config" / "terminal-radio"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_stations_path() -> Path:
    """Get the path to stations.m3u, copying default if needed."""
    config_dir = get_config_dir()
    user_stations = config_dir / "stations.m3u"

    if not user_stations.exists():
        # Copy default stations from package
        default_stations = Path(__file__).parent / "stations.m3u"
        if default_stations.exists():
            shutil.copy(default_stations, user_stations)
        else:
            # Create empty file with header
            user_stations.write_text("#EXTM3U\n")

    return user_stations

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, Center
from textual.widgets import Static, Button, ListView, ListItem, Label, Input
from textual.screen import ModalScreen

try:
    import mpv
    MPV_AVAILABLE = True
except (ImportError, OSError):
    MPV_AVAILABLE = False


@dataclass
class Station:
    name: str
    url: str


@dataclass
class Theme:
    """Theme definition for the radio UI."""
    name: str
    background: str
    container_bg: str
    border: str
    header_bg: str
    display_bg: str
    title_color: str
    time_color: str
    highlight_bg: str
    footer_color: str


# Available themes
THEMES = {
    "retro": Theme(
        name="Retro Radio",
        background="#8B4513",           # Warm brown background (wood)
        container_bg="#D2691E",         # Chocolate brown (radio body)
        border="#DAA520",               # Goldenrod (brass accents)
        header_bg="#B8860B",            # Dark goldenrod (dial area)
        display_bg="#2F4F4F",           # Dark slate (display window)
        title_color="#FFD700",          # Gold (station name)
        time_color="#98FB98",           # Pale green (frequency display)
        highlight_bg="#CD853F",         # Peru (selected station)
        footer_color="#DEB887",         # Burlywood (footer text)
    ),
    "mint_retro": Theme(
        name="Mint Retro",
        background="#E8B89D",           # Terracotta/coral background
        container_bg="#A8A8A8",         # Silver gray (radio body)
        border="#5F9EA0",               # Cadet blue (teal accents)
        header_bg="#708090",            # Slate gray (header)
        display_bg="#2F4F4F",           # Dark slate (display)
        title_color="#FFD700",          # Gold text
        time_color="#40E0D0",           # Turquoise
        highlight_bg="#5F9EA0",         # Teal highlight
        footer_color="#708090",         # Slate gray
    ),
    "synthwave": Theme(
        name="Synthwave",
        background="#1a1a2e",
        container_bg="#16213e",
        border="#e94560",
        header_bg="#e94560",
        display_bg="#0f0f23",
        title_color="#00ff00",
        time_color="#00ffff",
        highlight_bg="#e94560",
        footer_color="#666666",
    ),
    "dracula": Theme(
        name="Dracula",
        background="#282a36",
        container_bg="#44475a",
        border="#bd93f9",
        header_bg="#bd93f9",
        display_bg="#21222c",
        title_color="#50fa7b",
        time_color="#8be9fd",
        highlight_bg="#bd93f9",
        footer_color="#6272a4",
    ),
    "gruvbox": Theme(
        name="Gruvbox",
        background="#282828",
        container_bg="#3c3836",
        border="#fe8019",
        header_bg="#fe8019",
        display_bg="#1d2021",
        title_color="#b8bb26",
        time_color="#83a598",
        highlight_bg="#fe8019",
        footer_color="#928374",
    ),
    "nord": Theme(
        name="Nord",
        background="#2e3440",
        container_bg="#3b4252",
        border="#88c0d0",
        header_bg="#88c0d0",
        display_bg="#242933",
        title_color="#a3be8c",
        time_color="#81a1c1",
        highlight_bg="#88c0d0",
        footer_color="#4c566a",
    ),
    "vintage": Theme(
        name="Vintage Cream",
        background="#F5F5DC",           # Beige
        container_bg="#DEB887",         # Burlywood
        border="#8B4513",               # Saddle brown
        header_bg="#A0522D",            # Sienna
        display_bg="#3D2914",           # Dark brown
        title_color="#FFE4B5",          # Moccasin
        time_color="#FFDAB9",           # Peach puff
        highlight_bg="#CD853F",         # Peru
        footer_color="#8B4513",         # Saddle brown
    ),
    "bakelite": Theme(
        name="Bakelite",
        background="#2D2D2D",           # Dark gray
        container_bg="#4A3728",         # Dark brown (bakelite)
        border="#C9A86C",               # Brass/gold
        header_bg="#3D2914",            # Darker brown
        display_bg="#1A1A1A",           # Almost black
        title_color="#C9A86C",          # Brass
        time_color="#90EE90",           # Light green (old dial)
        highlight_bg="#5D4E37",         # Medium brown
        footer_color="#8B7355",         # Tan
    ),
}


def save_station(path: Path, name: str, url: str):
    """Append a new station to the M3U file."""
    with open(path, 'a') as f:
        f.write(f"\n#EXTINF:-1,{name}\n{url}\n")


def parse_m3u(path: Path) -> list[Station]:
    """Parse M3U playlist file."""
    stations = []
    lines = path.read_text().strip().split('\n')

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('#EXTINF:'):
            match = re.search(r'#EXTINF:[^,]*,(.+)', line)
            name = match.group(1).strip() if match else "Unknown Station"
            i += 1
            while i < len(lines) and (not lines[i].strip() or lines[i].startswith('#')):
                i += 1
            if i < len(lines):
                url = lines[i].strip()
                stations.append(Station(name=name, url=url))
        i += 1

    return stations


class ThemeScreen(ModalScreen):
    """Modal screen to select a theme."""

    CSS = """
    ThemeScreen {
        align: center middle;
    }

    #theme-dialog {
        width: 40;
        height: 14;
        background: #16213e;
        border: heavy #e94560;
        padding: 1 2;
    }

    #theme-dialog Static {
        margin-bottom: 1;
    }

    #theme-list {
        height: 8;
        background: #0f0f23;
        border: round #e94560;
    }

    #theme-buttons {
        height: 3;
        align: center middle;
    }
    """

    def compose(self) -> ComposeResult:
        with Container(id="theme-dialog"):
            yield Static("[bold]Select Theme[/]")
            yield ListView(id="theme-list")
            with Horizontal(id="theme-buttons"):
                yield Button("Back", id="btn-back", variant="default")

    def on_mount(self):
        theme_list = self.query_one("#theme-list", ListView)
        for key, theme in THEMES.items():
            item = ListItem(Label(theme.name), id=f"theme-{key}")
            theme_list.append(item)

    def on_list_view_selected(self, event: ListView.Selected):
        if event.item and event.item.id:
            theme_key = event.item.id.replace("theme-", "")
            self.dismiss(theme_key)

    def on_button_pressed(self, event: Button.Pressed):
        self.dismiss(None)


class AddStationScreen(ModalScreen):
    """Modal screen to add a new station."""

    CSS = """
    AddStationScreen {
        align: center middle;
    }

    #add-dialog {
        width: 50;
        height: 18;
        background: #16213e;
        border: heavy #e94560;
        padding: 1 2;
    }

    #add-dialog Static {
        margin-bottom: 1;
    }

    #add-dialog Input {
        margin-bottom: 1;
    }

    #add-buttons {
        height: 3;
        align: center middle;
    }

    #add-buttons Button {
        margin: 0 1;
    }
    """

    def compose(self) -> ComposeResult:
        with Container(id="add-dialog"):
            yield Static("[bold]Add New Station[/]")
            yield Input(placeholder="Station name", id="station-name")
            yield Input(placeholder="Stream URL", id="station-url")
            with Horizontal(id="add-buttons"):
                yield Button("Add", id="btn-add", variant="success")
                yield Button("Back", id="btn-cancel", variant="default")

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "btn-add":
            name = self.query_one("#station-name", Input).value.strip()
            url = self.query_one("#station-url", Input).value.strip()
            if name and url:
                self.dismiss((name, url))
            else:
                self.dismiss(None)
        else:
            self.dismiss(None)


def generate_css(theme: Theme) -> str:
    """Generate CSS for the given theme."""
    return f"""
    Screen {{
        background: {theme.background};
        align: center middle;
    }}

    #outer-container {{
        width: 90;
        height: 25;
        background: {theme.container_bg};
        border: double {theme.border};
    }}

    #radio-body {{
        height: 1fr;
        width: 100%;
    }}

    #left-panel {{
        width: 1fr;
        height: 100%;
        padding: 0 1;
    }}

    #speaker-panel {{
        width: 20;
        height: 100%;
        background: {theme.display_bg};
        border-left: heavy {theme.border};
        padding: 1;
    }}

    #speaker-frame {{
        width: 100%;
        height: 100%;
        border: round {theme.border};
        background: {theme.container_bg};
    }}

    #speaker-grill {{
        width: 100%;
        height: 100%;
        text-align: center;
        content-align: center middle;
        color: {theme.border};
    }}

    #header {{
        height: 3;
        background: {theme.header_bg};
        text-align: center;
        color: white;
        border-bottom: solid {theme.border};
        padding: 1;
    }}

    #display-area {{
        height: 7;
        background: {theme.display_bg};
        border: round {theme.border};
        margin: 1;
        padding: 0 1;
    }}

    #vu-left, #vu-right {{
        width: 4;
        height: 100%;
        text-align: center;
        padding: 0 1;
    }}

    #display-center {{
        width: 1fr;
        height: 100%;
        align: center middle;
    }}

    #title-display {{
        height: 1;
        width: 100%;
        text-align: center;
        color: {theme.title_color};
        text-style: bold;
    }}

    #info-row {{
        height: 1;
    }}

    #time-display {{
        width: 1fr;
        text-align: left;
        color: {theme.time_color};
    }}

    #volume-display {{
        width: 1fr;
        text-align: center;
        color: {theme.time_color};
    }}

    #status-display {{
        width: 1fr;
        text-align: right;
    }}

    #controls {{
        height: 3;
        margin: 0 1;
        align: center middle;
    }}

    #controls Button {{
        width: 1fr;
        min-width: 10;
        margin: 0 1;
        border: tall {theme.border};
    }}

    #playlist-container {{
        height: 1fr;
        margin: 0 1 1 1;
        border: round {theme.border};
        background: {theme.display_bg};
    }}

    #playlist {{
        height: 100%;
        background: transparent;
    }}

    #playlist > ListItem {{
        background: transparent;
        padding: 0 1;
    }}

    #playlist > ListItem.--highlight {{
        background: {theme.highlight_bg};
    }}

    #footer {{
        height: 2;
        text-align: center;
        color: {theme.footer_color};
        border-top: solid {theme.border};
        padding: 0 1;
    }}
    """


class TerminalRadio(App):
    """Main application."""

    CSS = generate_css(THEMES["bakelite"])

    BINDINGS = [
        ("space", "toggle_play", "Play/Pause"),
        ("s", "stop", "Stop"),
        ("n", "next_station", "Next"),
        ("p", "prev_station", "Previous"),
        ("q", "quit", "Quit"),
        ("a", "add_station", "Add Station"),
        ("t", "select_theme", "Theme"),
        ("up", "volume_up", "Volume Up"),
        ("down", "volume_down", "Volume Down"),
    ]

    def __init__(self):
        super().__init__()
        self.stations: list[Station] = []
        self.current_index = 0
        self.player = None
        self.volume = 60
        self.active_theme = "bakelite"
        self._init_player()
        self._load_stations()

    def _init_player(self):
        if MPV_AVAILABLE:
            try:
                self.player = mpv.MPV(
                    video=False,
                    terminal=False,
                    input_default_bindings=False,
                    input_vo_keyboard=False,
                )
                self.player.volume = self.volume
            except Exception:
                self.player = None
        # Audio level analysis
        self._analyzer_process = None
        self._analyzer_thread = None
        self._audio_levels = {"left": 0.0, "right": 0.0}
        self._analyzer_lock = threading.Lock()

    def _load_stations(self):
        m3u_path = get_stations_path()
        if m3u_path.exists():
            self.stations = parse_m3u(m3u_path)

    def _generate_speaker_grill(self, theme: Theme) -> str:
        """Generate vertical bar speaker grill pattern."""
        border_color = theme.border
        bg_color = theme.display_bg
        rows = 15
        cols = 14
        lines = []
        for r in range(rows):
            line = ""
            for c in range(cols):
                line += f"[{border_color}]│[/][{bg_color}] [/]"
            lines.append(line)
        return "\n".join(lines)

    def compose(self) -> ComposeResult:
        with Container(id="outer-container"):
            with Horizontal(id="radio-body"):
                with Vertical(id="left-panel"):
                    yield Static("[bold]~ R A D I O ~[/]", id="header")

                    with Horizontal(id="display-area"):
                        yield Static("", id="vu-left")
                        with Vertical(id="display-center"):
                            yield Static("Ready to play", id="title-display")
                            with Horizontal(id="info-row"):
                                yield Static("00:00", id="time-display")
                                yield Static("VOL: 60%", id="volume-display")
                                yield Static("[red]STOPPED[/]", id="status-display")
                        yield Static("", id="vu-right")

                    with Horizontal(id="controls"):
                        yield Button(" |<< ", id="btn-prev", variant="default")
                        yield Button(" > PLAY ", id="btn-play", variant="success")
                        yield Button(" [] STOP ", id="btn-stop", variant="error")
                        yield Button(" >>| ", id="btn-next", variant="default")

                    with Container(id="playlist-container"):
                        yield ListView(id="playlist")

                    yield Static("[Space] Play/Pause  [S] Stop  [N/P] Next/Prev  [Up/Down] Volume  [A] Add  [T] Theme  [Q] Quit", id="footer")

                with Container(id="speaker-panel"):
                    with Container(id="speaker-frame"):
                        yield Static(self._generate_speaker_grill(THEMES[self.active_theme]), id="speaker-grill")

    def on_mount(self):
        self._refresh_playlist()
        if not MPV_AVAILABLE:
            self.query_one("#title-display", Static).update("MPV not found! brew install mpv")
        self.set_interval(1.0, self._update_time)
        self.set_interval(0.1, self._update_visualizer)
        self.vu_left = 0
        self.vu_right = 0
        self.is_playing = False

    def _refresh_playlist(self):
        playlist = self.query_one("#playlist", ListView)
        playlist.clear()
        for idx, station in enumerate(self.stations):
            marker = "▶" if idx == self.current_index else " "
            item = ListItem(Label(f"{marker} {idx + 1}. {station.name}"))
            playlist.append(item)

    def _update_time(self):
        if self.player and MPV_AVAILABLE:
            try:
                pos = self.player.time_pos
                if pos is not None:
                    mins = int(pos) // 60
                    secs = int(pos) % 60
                    self.query_one("#time-display", Static).update(f"{mins:02d}:{secs:02d}")
            except Exception:
                pass

    def _start_audio_analyzer(self, url: str):
        """Start ffmpeg process to analyze audio levels."""
        self._stop_audio_analyzer()

        cmd = [
            "ffmpeg", "-i", url,
            "-af", "ebur128=peak=true",
            "-f", "null", "-"
        ]

        try:
            self._analyzer_process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            self._analyzer_thread = threading.Thread(
                target=self._read_audio_levels,
                daemon=True
            )
            self._analyzer_thread.start()
        except Exception:
            self._analyzer_process = None

    def _stop_audio_analyzer(self):
        """Stop the ffmpeg analyzer process."""
        if self._analyzer_process:
            try:
                self._analyzer_process.terminate()
                self._analyzer_process.wait(timeout=1)
            except Exception:
                try:
                    self._analyzer_process.kill()
                except Exception:
                    pass
            self._analyzer_process = None
        with self._analyzer_lock:
            self._audio_levels = {"left": 0.0, "right": 0.0}

    def _read_audio_levels(self):
        """Read audio levels from ffmpeg stderr in background thread."""
        if not self._analyzer_process:
            return

        ftpk_pattern = re.compile(r"FTPK:\s*([-\d.]+)\s*([-\d.]+)\s*dBFS")

        try:
            for line in self._analyzer_process.stderr:
                if self._analyzer_process is None:
                    break
                match = ftpk_pattern.search(line)
                if match:
                    left_db = float(match.group(1))
                    right_db = float(match.group(2))
                    # Convert dB to 0-1 range (-40dB to 0dB)
                    left = max(0.0, min(1.0, (left_db + 40) / 40))
                    right = max(0.0, min(1.0, (right_db + 40) / 40))
                    with self._analyzer_lock:
                        self._audio_levels["left"] = left
                        self._audio_levels["right"] = right
        except Exception:
            pass

    def _get_audio_level(self, channel: str) -> float:
        """Get current audio level (0-1 range)."""
        if not self.is_playing:
            return 0.0
        with self._analyzer_lock:
            return self._audio_levels.get(channel, 0.0)

    def _update_visualizer(self):
        max_level = 5
        if self.is_playing:
            # Echte Audio-Level von ffmpeg holen
            level_left = self._get_audio_level("left")
            level_right = self._get_audio_level("right")

            # In Anzeigebereich umrechnen (0-1 -> 0-max_level)
            target_left = int(level_left * max_level)
            target_right = int(level_right * max_level)

            # Sanftes Abklingen für bessere Visualisierung
            if target_left > self.vu_left:
                self.vu_left = target_left
            else:
                self.vu_left = max(self.vu_left - 1, target_left)

            if target_right > self.vu_right:
                self.vu_right = target_right
            else:
                self.vu_right = max(self.vu_right - 1, target_right)
        else:
            self.vu_left = max(0, self.vu_left - 1)
            self.vu_right = max(0, self.vu_right - 1)

        self.query_one("#vu-left", Static).update(self._render_vu(self.vu_left, max_level))
        self.query_one("#vu-right", Static).update(self._render_vu(self.vu_right, max_level))

    def _render_vu(self, level: int, max_level: int) -> str:
        lines = []
        for i in range(max_level, 0, -1):
            if i <= level:
                if i >= max_level:
                    lines.append("[red bold]|[/]")
                elif i >= max_level - 1:
                    lines.append("[#FFD700 bold]|[/]")
                else:
                    lines.append("[#90EE90 bold]|[/]")
            else:
                lines.append("[#4A4A4A]-[/]")
        return "\n".join(lines)

    def _play_station(self, index: int):
        if not self.player or not self.stations:
            return

        self.current_index = index
        station = self.stations[index]

        self.query_one("#title-display", Static).update(station.name)
        self.query_one("#status-display", Static).update("[yellow]CONNECTING[/]")

        try:
            self.player.play(station.url)
            self._start_audio_analyzer(station.url)
            self.query_one("#status-display", Static).update("[green]PLAYING[/]")
            self.is_playing = True
        except Exception as e:
            self.query_one("#title-display", Static).update(f"Error: {e}")
            self.query_one("#status-display", Static).update("[red]STOPPED[/]")
            self.is_playing = False

        self._refresh_playlist()

    def _stop(self):
        if self.player:
            try:
                self.player.stop()
            except Exception:
                pass
        self._stop_audio_analyzer()
        self.is_playing = False
        self.query_one("#status-display", Static).update("[red]STOPPED[/]")
        self.query_one("#time-display", Static).update("00:00")
        self.query_one("#title-display", Static).update("Ready to play")

    def on_button_pressed(self, event: Button.Pressed):
        button_id = event.button.id
        if button_id == "btn-play":
            self.action_toggle_play()
        elif button_id == "btn-stop":
            self.action_stop()
        elif button_id == "btn-next":
            self.action_next_station()
        elif button_id == "btn-prev":
            self.action_prev_station()

    def on_list_view_selected(self, event: ListView.Selected):
        if event.list_view.index is not None:
            self._play_station(event.list_view.index)

    def action_toggle_play(self):
        if not self.player:
            return
        status = self.query_one("#status-display", Static).render()
        if "STOPPED" in str(status):
            self._play_station(self.current_index)
        else:
            try:
                self.player.pause = not self.player.pause
            except Exception:
                pass

    def action_stop(self):
        self._stop()

    def action_next_station(self):
        if self.stations:
            next_idx = (self.current_index + 1) % len(self.stations)
            self._play_station(next_idx)

    def action_prev_station(self):
        if self.stations:
            prev_idx = (self.current_index - 1) % len(self.stations)
            self._play_station(prev_idx)

    def action_volume_up(self):
        self.volume = min(100, self.volume + 5)
        self._update_volume()

    def action_volume_down(self):
        self.volume = max(0, self.volume - 5)
        self._update_volume()

    def _update_volume(self):
        if self.player:
            try:
                self.player.volume = self.volume
            except Exception:
                pass
        vol_display = self.query_one("#volume-display", Static)
        vol_display.update(f"VOL: {self.volume}%")

    def action_add_station(self):
        self.push_screen(AddStationScreen(), self._on_station_added)

    def _on_station_added(self, result):
        if result:
            name, url = result
            m3u_path = get_stations_path()
            save_station(m3u_path, name, url)
            station = Station(name=name, url=url)
            self.stations.append(station)
            self._refresh_playlist()

    def action_select_theme(self):
        theme_keys = list(THEMES.keys())
        current_idx = theme_keys.index(self.active_theme)
        next_idx = (current_idx + 1) % len(theme_keys)
        self.active_theme = theme_keys[next_idx]
        self._apply_theme(THEMES[self.active_theme])

    def _apply_theme(self, theme: Theme):
        """Apply theme colors to UI elements."""
        self.screen.styles.background = theme.background

        outer = self.query_one("#outer-container")
        outer.styles.background = theme.container_bg
        outer.styles.border = ("double", theme.border)

        header = self.query_one("#header")
        header.styles.background = theme.header_bg

        display = self.query_one("#display-area")
        display.styles.background = theme.display_bg
        display.styles.border = ("round", theme.border)

        title = self.query_one("#title-display")
        title.styles.color = theme.title_color

        time_display = self.query_one("#time-display")
        time_display.styles.color = theme.time_color

        volume_display = self.query_one("#volume-display")
        volume_display.styles.color = theme.time_color

        playlist_container = self.query_one("#playlist-container")
        playlist_container.styles.background = theme.display_bg
        playlist_container.styles.border = ("round", theme.border)

        footer = self.query_one("#footer")
        footer.styles.color = theme.footer_color

        # Speaker panel styling
        speaker_panel = self.query_one("#speaker-panel")
        speaker_panel.styles.background = theme.display_bg
        speaker_panel.styles.border_left = ("heavy", theme.border)

        speaker_frame = self.query_one("#speaker-frame")
        speaker_frame.styles.background = theme.container_bg
        speaker_frame.styles.border = ("round", theme.border)

        speaker_grill = self.query_one("#speaker-grill", Static)
        speaker_grill.update(self._generate_speaker_grill(theme))


def main():
    app = TerminalRadio()
    app.run()


if __name__ == "__main__":
    main()
