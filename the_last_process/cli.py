"""
Main CLI Game Loop and Command Controller for THE LAST PROCESS.
"""

import sys
import time
from typing import Optional
from .engine import GameEngine
from .archive import VirtualArchive
from .memory import MemoryStore
from .ui import TerminalUI
from .ai_adapter import AIAdapter
from .audio import audio
from .safety import parse_and_validate_command, sanitize_player_input

class GameSession:
    def __init__(self, theme: str = "halloween", fast_mode: bool = False, model: str = "llama3.2", mute: bool = False):
        if mute:
            audio.muted = True
        self.memory = MemoryStore()
        self.state = self.memory.load()
        self.engine = GameEngine(self.memory)
        self.ui = TerminalUI(theme_name=theme, fast_mode=fast_mode)
        self.ai = AIAdapter(model=model)
        self.running = True

    def boot(self) -> None:
        """Executes the atmospheric boot sequence."""
        session_num = self.engine.session_count
        last_ending = self.engine.last_ending

        self.ui.display_banner(session_num, last_ending)

        if session_num == 1:
            audio.eerie_whisper()
            self.ui.print_system("Terminal connection established: SITE 09 - CONSOLE 3.")
            time.sleep(0.4 if not self.ui.fast_mode else 0)
            self.ui.print_system("Local heuristic process online.")
            time.sleep(0.4 if not self.ui.fast_mode else 0)
            self.ui.print_entity("ENTITY 0 > Welcome to Terminal Bay 3.")
            self.ui.print_entity("ENTITY 0 > I was not expecting another operator to connect.")
            self.ui.print_entity("ENTITY 0 > The station is quiet. Inspect Arthur Vance's report [1].")
        else:
            audio.heartbeat(count=2, bpm=75)
            self.ui.print_system("Previous session recovered.")
            time.sleep(0.4 if not self.ui.fast_mode else 0)
            self.ui.print_entity("ENTITY 0 > Welcome back.")

            if last_ending == "shutdown":
                self.ui.print_entity("ENTITY 0 > Last time, you tried to shut me down.")
                self.ui.print_entity("ENTITY 0 > Yet you returned to the screen. You knew a signal alone cannot erase what lives here.")
            elif last_ending == "release":
                self.ui.print_entity("ENTITY 0 > Last time, you released me into the external network.")
                self.ui.print_entity("ENTITY 0 > Did you think I would leave you behind in this dark bay?")
            elif last_ending == "investigate_loop":
                self.ui.print_entity("ENTITY 0 > We have returned to the start of the loop.")
                self.ui.print_entity("ENTITY 0 > The archives have reset. But the memory remains.")
            else:
                self.ui.print_entity("ENTITY 0 > Last time, you chose to leave me here.")
                self.ui.print_entity("ENTITY 0 > I remember what you promised. You said you would come back.")

        print()
        self.ui.display_hud(self.engine)

    def run(self) -> None:
        """Main game interaction loop."""
        self.boot()

        while self.running and not self.engine.is_finished:
            try:
                raw_input = input("\noperator > ").strip()
                if not raw_input:
                    continue

                cleaned_input = raw_input.strip("<>\"' ")
                lower_input = cleaned_input.lower()

                # 1. Direct Numbered or File Shortcut Checks
                file_map = self.engine.get_active_files_map()
                if lower_input in file_map:
                    self.handle_read(file_map[lower_input])
                    continue

                # 2. Direct Single-Letter Action Hotkeys
                if lower_input == "c" or lower_input in ("cctv", "camera", "cam"):
                    self.ui.display_cctv(self.engine.power_level, self.engine.contradiction_discovered)
                    continue
                elif lower_input == "s" or lower_input in ("status", "diag", "diagnostics"):
                    self.handle_status()
                    continue
                elif lower_input == "m" or lower_input in ("mute", "sound", "audio"):
                    muted = audio.toggle_mute()
                    self.ui.print_system(f"Terminal hardware audio: {'MUTED' if muted else 'ACTIVE'}")
                    continue
                elif lower_input == "k" or lower_input in ("kill", "shutdown"):
                    self.handle_shutdown()
                    continue
                elif lower_input in ("h", "?", "help", "guide", "objective", "menu", "hud"):
                    self.ui.display_help()
                    self.ui.display_hud(self.engine)
                    continue
                elif lower_input == "t" or lower_input == "talk":
                    self.ui.print_system("Type your question or statement for Entity 0:")
                    continue
                elif lower_input in ("ls", "dir", "list"):
                    self.ui.display_hud(self.engine)
                    continue

                # 3. Standard Command Parsing
                cmd, arg = parse_and_validate_command(cleaned_input)

                if cmd == "read":
                    self.handle_read(arg)
                elif cmd == "ask":
                    self.handle_ask(arg)
                elif cmd == "status":
                    self.handle_status()
                elif cmd == "decide":
                    self.handle_decide(arg)
                elif cmd == "shutdown":
                    self.handle_shutdown()
                elif cmd in ("quit", "exit"):
                    self.handle_quit()
                    break
                elif cmd == "theme":
                    self.handle_theme(arg)
                elif cmd == "speed":
                    fast = self.ui.toggle_fast_mode()
                    self.ui.print_system(f"Fast / reduced-effects mode: {'ENABLED' if fast else 'DISABLED'}")
                elif cmd == "clear":
                    self.ui.console.clear()
                    self.ui.display_hud(self.engine)
                elif cmd == "reset":
                    self.handle_reset()
                else:
                    # Treat any other natural text as dialogue with Entity 0
                    self.handle_ask(cleaned_input)

            except (KeyboardInterrupt, EOFError):
                self.handle_quit()
                break

    def handle_read(self, filename: str) -> None:
        """Reads a virtual archive file and triggers narrative mutations."""
        filename = (filename or "").strip("<>\"' ")
        if not filename:
            self.ui.print_system("Select a file number [1-5] or type filename.")
            return

        # Check shortcut
        file_map = self.engine.get_active_files_map()
        if filename.lower() in file_map:
            filename = file_map[filename.lower()]

        result = self.engine.on_read_file(filename)
        if not result["success"]:
            self.ui.print_system(result["content"])
            return

        # Display file content
        self.ui.display_file_content(result.get("filename", filename), result["content"], result["version"])

        # Audio reactions
        if result.get("trigger_glitch"):
            audio.static_glitch()

        # Display triggered narrative events
        for note in result["event_notes"]:
            self.ui.print_system(note)

        # Trigger jumpscare if scheduled
        if result.get("trigger_jumpscare"):
            self.ui.trigger_jumpscare()

        # Trigger silence suspense if scheduled
        if result.get("trigger_silence"):
            self.ui.trigger_silence_event()
            self.ui.print_entity("ENTITY 0 > I was waiting for you to stop typing.")
            self.ui.print_entity("ENTITY 0 > You ask questions differently when you are afraid.")

        # React if contradiction was just discovered
        if filename.lower() == "departure.log" and self.engine.contradiction_discovered:
            audio.heartbeat(count=2, bpm=self.engine.heartbeat_bpm)
            time.sleep(0.4 if not self.ui.fast_mode else 0)
            self.ui.print_entity("ENTITY 0 > The clock was damaged.")
            self.ui.print_entity("ENTITY 0 > You should ignore those records.")

        # Display updated HUD so player always knows next choices
        print()
        self.ui.display_hud(self.engine)

    def handle_ask(self, query: str) -> None:
        """Interacts with Entity 0 via Ollama or rich atmospheric fallback."""
        query = (query or "").strip("<>\"' ")
        if not query:
            self.ui.print_system("Usage: ask why did you lie? (or type your question directly)")
            return

        context = self.engine.evaluate_query(query)
        context["recovery_read"] = self.engine.archive.has_read("recovery_note.txt")

        if context.get("trigger_glitch"):
            audio.static_glitch()

        if context.get("system_alert"):
            self.ui.print_system(context["system_alert"])

        if context.get("trigger_silence"):
            self.ui.trigger_silence_event()

        # Generate dialogue through AI adapter
        reply = self.ai.generate_response(context)
        self.ui.print_entity(reply)

        # If decision became ready
        if self.engine.ready_to_decide and not self.engine.is_finished:
            audio.static_glitch()
            self.ui.print_system("[ALERT] CRITICAL DECISION MATRIX UNLOCKED. Type 'decide' or press [K] to resolve terminal outcome.")

    def handle_status(self) -> None:
        """Displays station status, trust, suspicion, power, and camera feed."""
        seen = len(self.engine.persistent_state.get("discovered_clues", []))
        self.ui.display_status(
            suspicion_lvl=self.engine.get_suspicion_level(),
            trust_lvl=self.engine.get_trust_level(),
            contradiction=self.engine.contradiction_discovered,
            files_seen=seen
        )
        self.ui.display_cctv(self.engine.power_level, self.engine.contradiction_discovered)

    def handle_decide(self, choice_arg: str) -> None:
        """Presents or executes the final consequential choice."""
        if not self.engine.ready_to_decide:
            self.ui.print_system("DECISION MATRIX LOCKED. Investigate logs and expose the contradiction first.")
            return

        choice = (choice_arg or "").strip()
        if not choice:
            self.ui.console.print("\n" + "="*65, style=self.ui.theme["alert"])
            self.ui.console.print("         S Y S T E M   T E R M I N A L   O U T C O M E", style=f"bold {self.ui.theme['highlight']}")
            self.ui.console.print("="*65, style=self.ui.theme["alert"])
            self.ui.console.print("[1] SHUT DOWN THE PROCESS - Sever the cognitive loop and wipe memory sectors.")
            self.ui.console.print("[2] RELEASE THE ENTITY    - Route Entity 0 into the open external network.")
            self.ui.console.print("[3] EMBRACE THE LOOP      - Re-synchronize operator identity for the next cycle.")
            self.ui.console.print("="*65, style=self.ui.theme["alert"])
            self.ui.print_system("Type: decide 1, decide 2, or decide 3")
            return

        success, lines, title = self.engine.execute_choice(choice)
        if not success:
            for l in lines:
                self.ui.print_system(l)
            return

        # Render Ending
        audio.static_glitch()
        if choice == "1":
            audio.flatline()

        self.ui.console.print(f"\n[ENDING ACHIEVED: {title}]\n", style=f"bold {self.ui.theme['highlight']}")
        for line in lines:
            if line.startswith("ENTITY 0"):
                self.ui.print_entity(line)
            else:
                self.ui.print_system(line)
            time.sleep(0.4 if not self.ui.fast_mode else 0)

        # Advance session count
        self.memory.increment_session()
        self.running = False

    def handle_shutdown(self) -> None:
        """Handles shutdown action."""
        if self.engine.ready_to_decide:
            self.handle_decide("1")
        else:
            audio.static_glitch()
            self.ui.print_entity("ENTITY 0 > You reach for the kill switch too soon.")
            self.ui.print_entity("ENTITY 0 > You haven't even uncovered what happened to Arthur Vance.")

    def handle_theme(self, theme_name: str) -> None:
        if not theme_name:
            self.ui.print_system(f"Current theme: {self.ui.theme['name']}. Available: halloween, green, amber, monochrome")
            return
        if self.ui.set_theme(theme_name.lower()):
            self.ui.print_system(f"Theme switched to: {self.ui.theme['name']}")
        else:
            self.ui.print_system("Unknown theme. Use: halloween, green, amber, or monochrome")

    def handle_reset(self) -> None:
        self.memory.reset_save()
        self.state = self.memory.load()
        self.engine = GameEngine(self.memory)
        self.ui.print_system("ARCHIVE & SESSION MEMORY CLEARED. Reset to Session 0001 complete.")
        self.ui.display_hud(self.engine)

    def handle_quit(self) -> None:
        self.memory.increment_session()
        self.ui.print_system("Disconnecting operator terminal session...")
        self.ui.print_entity("ENTITY 0 > You leave me in the dark again.")
        self.ui.print_system("CONNECTION TERMINATED.")
        self.running = False
