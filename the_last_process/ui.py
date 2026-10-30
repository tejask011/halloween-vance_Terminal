"""
Haunted Terminal UI, Atmospheric HUD, and Horror Effects for THE LAST PROCESS.
"""

import sys
import time
import random
import warnings
from typing import Optional, List, Dict

warnings.filterwarnings("ignore", category=Warning)

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
    GHOST_ART,
    SKULL_ART,
    JUMPSCARE_FACE,
    get_camera_feed,
    corrupt_text
)
from .audio import audio

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
    def __init__(self, theme_name: str = "halloween", fast_mode: bool = False):
        self.console = Console(legacy_windows=False, highlight=False)
        self.theme_name = theme_name if theme_name in THEMES else "halloween"
        self.theme = THEMES[self.theme_name]
        self.fast_mode = fast_mode

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
        """Prints text character by character to simulate an old mainframe terminal cleanly."""
        if self.fast_mode:
            self.console.print(text, style=style, end=end)
            return

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
        self.print_teletype(f"SYSTEM > {message}", style=f"bold {self.theme['system']}")

    def print_entity(self, message: str) -> None:
        self.print_teletype(message, style=f"bold {self.theme['entity']}", delay=0.018)

    def print_operator(self, message: str) -> None:
        self.console.print(f"operator > {message}", style=f"dim {self.theme['primary']}")

    def display_hud(self, engine) -> None:
        """
        Renders the active station HUD, telemetry, and quick-action menu.
        Uses pure ASCII symbols to guarantee 100% stable rendering on all Windows consoles.
        """
        power = engine.power_level
        bpm = engine.heartbeat_bpm
        sanity = engine.sanity
        
        # Audio pulse when HUD renders
        audio.heartbeat(count=1, bpm=bpm)

        # Header status bar
        header_text = Text()
        header_text.append("[SITE 09 - BAY 3]  ", style="bold white")
        power_color = "green" if power > 50 else ("yellow" if power > 25 else "bold red")
        header_text.append(f"POWER: {power}%  ", style=power_color)
        header_text.append(f"SANITY: {sanity}%  ", style="cyan")
        header_text.append(f"PULSE: {bpm} BPM  ", style="bold red")
        header_text.append(f"ENTITY 0: {engine.get_trust_level()}", style=f"bold {self.theme['highlight']}")

        table = Table(title=header_text, box=box.ASCII, border_style=self.theme["primary"], show_header=True)
        table.add_column("KEY", style="bold yellow", width=6)
        table.add_column("ARCHIVE & ACTION MENU", style="bold white", width=50)
        table.add_column("STATUS", style="italic", width=22)

        # File options
        op_rev = engine.archive.files.get("operator_log.txt", {}).get("version", 1)
        table.add_row("[1]", "operator_log.txt (Arthur Vance's Report)", f"REV.0{op_rev}")
        
        dep_status = "[PARADOX FLAGGED]" if engine.contradiction_discovered else "Telemetry Log"
        dep_style = "bold red" if engine.contradiction_discovered else "dim"
        table.add_row("[2]", "departure.log (Facility Telemetry Sensors)", f"[{dep_style}]{dep_status}[/{dep_style}]")

        rec_seen = engine.archive.has_read("recovery_note.txt")
        table.add_row("[3]", "recovery_note.txt (Vance's Warning)", "RECOVERED" if rec_seen else "UNOPENED")

        if engine.archive.is_unlocked("dont_read_this.txt"):
            table.add_row("[4]", "[bold red]dont_read_this.txt (Unallocated Pointer)[/bold red]", "[bold red][!] CORRUPTED[/bold red]")

        if engine.archive.is_unlocked("identity_record.log"):
            table.add_row("[5]", "[bold magenta]identity_record.log (Biometric Ledger)[/bold magenta]", "[bold magenta][MASTER REVEAL][/bold magenta]")

        table.add_section()
        table.add_row("[T]", "Talk / Question Entity 0 in free text", "DIRECT CONVERSATION")
        table.add_row("[C]", "Surveillance CCTV Camera Feed (Bay 3)", "VIDEO TELEMETRY")
        table.add_row("[S]", "Station Diagnostics & Integrity Report", "TELEMETRY MATRIX")
        table.add_row("[K]", "Emergency Shutdown Process (Kill Switch)", "CONSEQUENTIAL CHOICE")
        table.add_row("[M]", f"Toggle Sound Effects [{'MUTED' if audio.muted else 'ACTIVE'}]", "HARDWARE AUDIO")
        table.add_row("[H]", "Mission Objectives & Story Guide", "OPERATOR MANUAL")

        self.console.print(table)
        self.console.print("[dim]Select a number [1-5], press an action key [T,C,S,K,M,H], or type any question freely:[/dim]")

    def trigger_jumpscare(self) -> None:
        """Horrifying CRT glitch and screaming demonic reflection."""
        audio.dissonance_screech()
        audio.static_glitch()

        self.console.clear()
        self.console.print(JUMPSCARE_FACE, style="bold red")
        time.sleep(0.6)
        self.console.clear()
        self.console.print("[bold red]SYSTEM > CRITICAL COGNITIVE BREACH IN SECTOR 09[/bold red]")
        self.console.print("[bold red]ENTITY 0 > I TOLD YOU NOT TO LOOK AT THAT.[/bold red]\n")
        time.sleep(0.4)

    def trigger_silence_event(self) -> None:
        """Controlled psychological silence event."""
        audio.eerie_whisper()
        time.sleep(0.5)
        self.console.print("[dim italic][The cursor blinks in the darkness...][/dim italic]")
        time.sleep(1.2)
        self.console.print(GHOST_ART, style=f"bold {self.theme.get('ghost', self.theme['highlight'])}")
        time.sleep(1.0)
        audio.heartbeat(count=2, bpm=92)
        self.console.print("[dim italic][No response from terminal bay for a short, controlled pause.][/dim italic]")
        time.sleep(1.0)
        self.console.print("SYSTEM > Response delayed.", style=f"bold {self.theme['alert']}")
        time.sleep(0.6)

    def display_cctv(self, power_level: int, contradiction_found: bool) -> None:
        """Renders CCTV surveillance feed."""
        audio.static_glitch()
        feed_text = get_camera_feed(power_level, contradiction_found)
        panel = Panel(
            feed_text,
            title="SURVEILLANCE CAM 03: TERMINAL BAY",
            border_style=self.theme["primary"],
            style=self.theme["primary"],
            box=box.ASCII
        )
        self.console.print(panel)

    def display_banner(self, session_count: int, last_ending: Optional[str] = None) -> None:
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

    def display_help(self) -> None:
        self.console.print("\n[bold yellow]MISSION OBJECTIVE & INVESTIGATION GUIDE:[/bold yellow]")
        self.console.print("  • You are an operator logged into Terminal Bay 3.")
        self.console.print("  • Vance's report claimed Entity 0 was killed at 23:40:00.")
        self.console.print("  • But the departure sensor recorded Entity 0 heartbeat at 23:42:01!")
        self.console.print("  • Your goal is to investigate the paradox, uncover who is watching you, and decide.")
        self.console.print("\n[bold yellow]HOW TO PLAY:[/bold yellow]")
        self.console.print("  • [bold white]Press 1, 2, 3, 4, 5[/bold white] to open files instantly.")
        self.console.print("  • [bold white]Press C[/bold white] to check Bay 3 surveillance cameras.")
        self.console.print("  • [bold white]Press S[/bold white] to view diagnostics and power level.")
        self.console.print("  • [bold white]Press M[/bold white] to toggle hardware sound effects.")
        self.console.print("  • [bold white]Type any question[/bold white] (e.g. 'why did you lie?', 'where is vance?') to interrogate Entity 0.\n")
