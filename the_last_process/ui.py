"""
Haunted Terminal UI & Atmospheric Effects for THE LAST PROCESS.

Built with Rich & Prompt Toolkit.
Features:
- Retro CRT Phosphor color palettes (Amber, Phosphor Green, Cold Monochrome).
- Simulated teletype text cadence (with fast-mode toggle for accessibility).
- Controlled silence & blinking cursor suspense events (Feature 03).
- Atmospheric glitch text and retro mainframe status panels.
"""

import sys
import time
import random
import warnings
from typing import Optional

# Suppress urllib3 / charset warnings if any
warnings.filterwarnings("ignore", category=Warning)

# Ensure UTF-8 stdout encoding on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich import box
from .ghost_art import (
    play_ghost_animation,
    play_skull_glitch,
    GHOST_FRAMES,
    SKULL_FRAMES,
    PUMPKIN_ART,
    TOMBSTONE_ART
)

THEMES = {
    "halloween": {
        "primary": "#ff7700",
        "dim": "#883300",
        "highlight": "#00ff66",
        "alert": "#ff1122",
        "system": "#ff5500",
        "entity": "#33ff77",
        "ghost": "#eeffff",
        "name": "Halloween Haunted Bay (Pumpkin & Ectoplasm)"
    },
    "amber": {
        "primary": "#ffb000",
        "dim": "#b37b00",
        "highlight": "#ffe066",
        "alert": "#ff3300",
        "system": "#cc8800",
        "entity": "#ff9900",
        "ghost": "#ffeedd",
        "name": "Amber Mainframe (Default)"
    },
    "green": {
        "primary": "#00ff66",
        "dim": "#008833",
        "highlight": "#66ff99",
        "alert": "#ff2200",
        "system": "#00cc55",
        "entity": "#00ff88",
        "ghost": "#d0ffd0",
        "name": "Phosphor Green"
    },
    "monochrome": {
        "primary": "#d0e0e0",
        "dim": "#708080",
        "highlight": "#ffffff",
        "alert": "#ff5555",
        "system": "#90a0a0",
        "entity": "#e0ffff",
        "ghost": "#ffffff",
        "name": "Cold Monochrome"
    }
}

class TerminalUI:
    def __init__(self, theme_name: str = "amber", fast_mode: bool = False):
        self.console = Console(legacy_windows=False, highlight=False)
        self.theme_name = theme_name if theme_name in THEMES else "amber"
        self.theme = THEMES[self.theme_name]
        self.fast_mode = fast_mode  # Accessibility mode: instant rendering, no delays

    def set_theme(self, theme_name: str) -> bool:
        if theme_name in THEMES:
            self.theme_name = theme_name
            self.theme = THEMES[theme_name]
            return True
        return False

    def toggle_fast_mode(self) -> bool:
        self.fast_mode = not self.fast_mode
        return self.fast_mode

    def print_teletype(self, text: str, style: Optional[str] = None, delay: float = 0.015, end: str = "\n") -> None:
        """Prints text character by character to simulate an old mainframe terminal cleanly on all consoles."""
        if self.fast_mode:
            self.console.print(text, style=style, end=end)
            return

        # Render styling once to prevent console line buffer wrapping bugs
        with self.console.capture() as capture:
            self.console.print(text, style=style, end="")
        rendered = capture.get()

        in_escape = False
        for ch in rendered:
            sys.stdout.write(ch)
            sys.stdout.flush()
            if ch == '\x1b':
                in_escape = True
            elif in_escape:
                if ch in ('m', 'H', 'J', 'K'):
                    in_escape = False
            else:
                time.sleep(delay * random.uniform(0.5, 1.3))

        sys.stdout.write(end)
        sys.stdout.flush()

    def print_system(self, message: str) -> None:
        """Renders a system alert or notification."""
        self.print_teletype(f"SYSTEM > {message}", style=f"bold {self.theme['system']}")

    def print_entity(self, message: str) -> None:
        """Renders dialogue spoken by Entity 0."""
        self.print_teletype(message, style=f"bold {self.theme['entity']}", delay=0.02)

    def print_operator(self, message: str) -> None:
        """Renders operator input echo."""
        self.console.print(f"operator > {message}", style=f"dim {self.theme['primary']}")

    def animate_ghost(self) -> None:
        """Plays the floating ghost animation if not in fast mode."""
        if not self.fast_mode:
            try:
                play_ghost_animation(self.console, theme_color=self.theme.get("ghost", self.theme["highlight"]), loops=2)
            except Exception:
                self.console.print(GHOST_FRAMES[0], style=f"bold {self.theme['highlight']}")

    def animate_skull(self) -> None:
        """Plays the chattering glitch skull animation when suspicion spikes."""
        if not self.fast_mode:
            try:
                play_skull_glitch(self.console, theme_color=self.theme["alert"], loops=2)
            except Exception:
                self.console.print(SKULL_FRAMES[0], style=f"bold {self.theme['alert']}")

    def trigger_silence_event(self) -> None:
        """
        Executes Feature 03: Silence and delayed-response suspense event.
        Simulates cursor blinks, pause, floating ghost apparition, and 'Response delayed' notification.
        """
        if self.fast_mode:
            self.console.print("[The cursor blinks.]", style="dim italic")
            self.console.print("SYSTEM > Response delayed.", style=f"bold {self.theme['alert']}")
            return

        time.sleep(0.4)
        self.console.print("[The cursor blinks in the dark...]", style="dim italic")
        time.sleep(0.8)
        self.animate_ghost()
        self.console.print("[No response from terminal bay for a short, controlled pause.]", style="dim italic")
        time.sleep(0.8)
        self.console.print("SYSTEM > Response delayed.", style=f"bold {self.theme['alert']}")
        time.sleep(0.6)

    def display_banner(self, session_count: int, last_ending: Optional[str] = None) -> None:
        """Renders the atmospheric Halloween haunted game header."""
        session_str = f"SESSION {session_count:04d}"
        banner_text = Text()
        banner_text.append("+====================================================================+\n", style=self.theme["dim"])
        banner_text.append("|   .---.          T H E   L A S T   P R O C E S S          .-.      |\n", style=f"bold {self.theme['highlight']}")
        banner_text.append("|  /     \\    Terminal Bay 3 - Autonomous Heuristic 0      / o o\\    |\n", style=self.theme["primary"])
        banner_text.append("| | () () |      HALLOWEEN GHOST IN THE MACHINE EDITION     | O  |   |\n", style=f"bold {self.theme['alert']}")
        banner_text.append(f"|  \\  ^  /                  [{session_str}]                     '-'     |\n", style=f"bold {self.theme['system']}")
        banner_text.append("+====================================================================+", style=self.theme["dim"])

        self.console.print(banner_text)
        if last_ending:
            self.console.print(f"PREVIOUS SESSION CYCLE: {last_ending.upper()}", style=f"dim italic {self.theme['alert']}")
        self.console.print("")

    def display_file_content(self, filename: str, content: str, version: Optional[int] = None) -> None:
        """Renders an archive file inside a terminal CRT pane."""
        title = f"ARCHIVE ENTRY: {filename}"
        if version and version > 1:
            title += f" [REV.0{version}]"
            
        panel = Panel(
            content,
            title=title,
            title_align="left",
            border_style=self.theme["primary"],
            style=self.theme["primary"],
            box=box.ASCII
        )
        self.console.print(panel)

    def display_status(self, suspicion_lvl: str, trust_lvl: str, contradiction: bool, files_seen: int) -> None:
        """Renders the current diagnostics table."""
        table = Table(title="STATION 09 TELEMETRY & DIAGNOSTICS", border_style=self.theme["dim"], box=box.ASCII)
        table.add_column("SUBSYSTEM", style=f"bold {self.theme['primary']}")
        table.add_column("STATUS", style=self.theme["highlight"])

        table.add_row("Entity 0 State", "HEURISTIC LOOP ACTIVE")
        table.add_row("Trust Index", trust_lvl)
        table.add_row("Suspicion Level", suspicion_lvl)
        table.add_row("Archive Contradiction", "FLAGGED" if contradiction else "UNCHECKED")
        table.add_row("Discovered Records", str(files_seen))
        table.add_row("Biometric Presence", "OPERATOR ACTIVE")

        self.console.print(table)

    def display_help(self) -> None:
        """Displays available fictional terminal commands."""
        self.console.print("\n[bold]MISSION OBJECTIVE & HOW TO PLAY:[/bold]")
        self.console.print("  1. Type: [bold yellow]ls[/bold yellow] to list the station archive files.")
        self.console.print("  2. Type: [bold yellow]read operator_log.txt[/bold yellow] to view Arthur Vance's shutdown log.")
        self.console.print("  3. Type: [bold yellow]read departure.log[/bold yellow] to expose contradictory timestamps.")
        self.console.print("  4. Type: [bold yellow]ask why did you lie?[/bold yellow] (or just type questions directly) to interrogate Entity 0.")
        self.console.print("  5. Type: [bold yellow]read recovery_note.txt[/bold yellow] to recover Vance's warning.\n")

        help_table = Table(title="ALLOWED TERMINAL COMMANDS (Do not type '<' or '>')", border_style=self.theme["dim"], box=box.ASCII)
        help_table.add_column("COMMAND", style=f"bold {self.theme['highlight']}")
        help_table.add_column("EXAMPLE USAGE", style=self.theme["primary"])

        help_table.add_row("ls", "ls")
        help_table.add_row("read filename", "read operator_log.txt")
        help_table.add_row("ask question", "ask what happened to Vance? (or type question directly)")
        help_table.add_row("status", "status")
        help_table.add_row("decide", "decide")
        help_table.add_row("theme name", "theme halloween (or green, amber, monochrome)")
        help_table.add_row("speed", "speed (toggles instant text rendering)")
        help_table.add_row("clear", "clear")
        help_table.add_row("reset", "reset (wipes save back to Session 0001)")
        help_table.add_row("quit", "quit")

        self.console.print(help_table)

