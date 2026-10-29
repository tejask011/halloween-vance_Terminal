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
from .safety import parse_and_validate_command, sanitize_player_input

class GameSession:
    def __init__(self, theme: str = "amber", fast_mode: bool = False, model: str = "llama3.2"):
        self.memory = MemoryStore()
        self.state = self.memory.load()
        self.engine = GameEngine(self.memory)
        self.ui = TerminalUI(theme_name=theme, fast_mode=fast_mode)
        self.ai = AIAdapter(model=model)
        self.running = True

    def boot(self) -> None:
        """Executes the atmospheric boot sequence (Feature 01: Persistent memory callbacks)."""
        session_num = self.engine.session_count
        last_ending = self.engine.last_ending

        self.ui.display_banner(session_num, last_ending)

        if session_num == 1:
            self.ui.print_system("Terminal connection established: SITE 09 - CONSOLE 3.")
            time.sleep(0.5 if not self.ui.fast_mode else 0)
            self.ui.print_system("Local heuristic process online.")
            time.sleep(0.5 if not self.ui.fast_mode else 0)
            self.ui.print_entity("ENTITY 0 > Welcome to Terminal Bay 3.")
            self.ui.print_entity("ENTITY 0 > I was not expecting another operator to connect.")
            self.ui.print_entity("ENTITY 0 > The station is quiet. Type 'help' for commands or 'ls' to view archives.")
        else:
            self.ui.print_system("Previous session recovered.")
            time.sleep(0.5 if not self.ui.fast_mode else 0)
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

    def run(self) -> None:
        """Main game interaction loop."""
        self.boot()

        while self.running and not self.engine.is_finished:
            try:
                # Prompt operator
                raw_input = input("\noperator > ").strip()
                if not raw_input:
                    continue

                cmd, arg = parse_and_validate_command(raw_input)

                if cmd is None:
                    # Treat unknown commands as free-text interaction or question if player just types
                    self.handle_ask(raw_input)
                    continue

                if cmd in ("quit", "exit"):
                    self.handle_quit()
                    break
                elif cmd == "help":
                    self.ui.display_help()
                elif cmd == "ls":
                    self.handle_ls()
                elif cmd == "read":
                    self.handle_read(arg)
                elif cmd == "ask":
                    self.handle_ask(arg)
                elif cmd == "status":
                    self.handle_status()
                elif cmd == "decide":
                    self.handle_decide(arg)
                elif cmd == "shutdown":
                    self.handle_shutdown()
                elif cmd == "theme":
                    self.handle_theme(arg)
                elif cmd == "speed":
                    fast = self.ui.toggle_fast_mode()
                    self.ui.print_system(f"Fast / reduced-effects mode: {'ENABLED' if fast else 'DISABLED'}")
                elif cmd == "clear":
                    self.ui.console.clear()
                    self.ui.display_banner(self.engine.session_count, self.engine.last_ending)
                elif cmd == "reset":
                    self.handle_reset()

            except (KeyboardInterrupt, EOFError):
                self.handle_quit()
                break

    def handle_ls(self) -> None:
        """Lists files and demonstrates Feature 05 (The terminal appears to lie)."""
        files, count_status = self.engine.archive.list_files(terminal_lies=self.engine.terminal_lied)
        self.ui.print_system(count_status)
        for f in files:
            self.ui.console.print(f"  > {f}", style=f"bold {self.ui.theme['highlight']}")

    def handle_read(self, filename: str) -> None:
        """Reads a virtual archive file and triggers narrative mutations."""
        filename = (filename or "").strip("<>\"' ")
        if not filename:
            self.ui.print_system("Usage: read operator_log.txt  (do not type '<' or '>')")
            return

        result = self.engine.on_read_file(filename)
        if not result["success"]:
            self.ui.print_system(result["content"])
            return

        # Display file
        self.ui.display_file_content(filename, result["content"], result["version"])

        # Display any triggered narrative events
        for note in result["event_notes"]:
            self.ui.print_system(note)

        # Trigger silence suspense if scheduled
        if result["trigger_silence"]:
            self.ui.trigger_silence_event()
            self.ui.print_entity("ENTITY 0 > I was waiting for you to stop typing.")
            self.ui.print_entity("ENTITY 0 > You ask questions differently when you are afraid.")

        # React if contradiction was just discovered
        if filename.lower() == "departure.log" and self.engine.contradiction_discovered:
            self.ui.animate_skull()
            time.sleep(0.5 if not self.ui.fast_mode else 0)
            self.ui.print_entity("ENTITY 0 > The clock was damaged.")
            self.ui.print_entity("ENTITY 0 > You should ignore those records.")

    def handle_ask(self, query: str) -> None:
        """Interacts with Entity 0 via Ollama or atmospheric fallback."""
        query = (query or "").strip("<>\"' ")
        if not query:
            self.ui.print_system("Usage: ask why did you lie? (or type your question directly)")
            return

        context = self.engine.evaluate_query(query)

        if context.get("system_alert"):
            self.ui.print_system(context["system_alert"])

        if context.get("trigger_silence"):
            self.ui.trigger_silence_event()

        # Generate dialogue through AI adapter
        reply = self.ai.generate_response(context)
        self.ui.print_entity(reply)

        # If decision became ready
        if self.engine.ready_to_decide and not self.engine.is_finished:
            self.ui.print_system("CRITICAL DECISION MATRIX READY. Type 'decide' to select terminal outcome.")

    def handle_status(self) -> None:
        """Displays station status, trust, and suspicion index."""
        seen = len(self.engine.persistent_state.get("discovered_clues", []))
        self.ui.display_status(
            suspicion_lvl=self.engine.get_suspicion_level(),
            trust_lvl=self.engine.get_trust_level(),
            contradiction=self.engine.contradiction_discovered,
            files_seen=seen
        )

    def handle_decide(self, choice_arg: str) -> None:
        """Presents or executes the final consequential choice (Feature 08)."""
        if not self.engine.ready_to_decide:
            self.ui.print_system("DECISION MATRIX LOCKED. Insufficient archival contradictions investigated.")
            self.ui.print_system("Explore logs, timestamps, and operator notes first.")
            return

        if not choice_arg:
            self.ui.console.print("\n" + "="*60, style=self.ui.theme["alert"])
            self.ui.console.print("         S Y S T E M   T E R M I N A L   O U T C O M E", style=f"bold {self.ui.theme['highlight']}")
            self.ui.console.print("="*60, style=self.ui.theme["alert"])
            self.ui.console.print("[1] SHUT DOWN THE PROCESS - Sever the cognitive loop and wipe memory sectors.")
            self.ui.console.print("[2] RELEASE THE ENTITY    - Route Entity 0 into the open external network.")
            self.ui.console.print("[3] EMBRACE THE LOOP      - Re-synchronize operator identity for the next cycle.")
            self.ui.console.print("="*60, style=self.ui.theme["alert"])
            self.ui.print_system("Type: decide 1, decide 2, or decide 3")
            return

        success, lines, title = self.engine.execute_choice(choice_arg.strip())
        if not success:
            for l in lines:
                self.ui.print_system(l)
            return

        # Render Ending
        self.ui.console.print(f"\n[ENDING ACHIEVED: {title}]\n", style=f"bold {self.ui.theme['highlight']}")
        for line in lines:
            if line.startswith("ENTITY 0"):
                self.ui.print_entity(line)
            else:
                self.ui.print_system(line)
            time.sleep(0.4 if not self.ui.fast_mode else 0)

        # Advance session count for the next run
        self.memory.increment_session()
        self.running = False

    def handle_shutdown(self) -> None:
        """Handles the 'shutdown' command as a narrative action (NOT real OS shutdown!)."""
        if self.engine.ready_to_decide:
            self.handle_decide("1")
        else:
            self.ui.print_entity("ENTITY 0 > You reach for the kill switch too soon.")
            self.ui.print_entity("ENTITY 0 > You haven't even read what happened to Arthur Vance.")

    def handle_theme(self, theme_name: str) -> None:
        if not theme_name:
            self.ui.print_system(f"Current theme: {self.ui.theme['name']}. Available: amber, green, monochrome")
            return
        if self.ui.set_theme(theme_name.lower()):
            self.ui.print_system(f"Theme switched to: {self.ui.theme['name']}")
        else:
            self.ui.print_system("Unknown theme. Use: amber, green, or monochrome")

    def handle_reset(self) -> None:
        """Wipes persistent save data."""
        self.memory.reset_save()
        self.state = self.memory.load()
        self.engine = GameEngine(self.memory)
        self.ui.print_system("ARCHIVE & SESSION MEMORY CLEARED. Reset to Session 0001 complete.")

    def handle_quit(self) -> None:
        """Clean disconnect without losing session state."""
        self.memory.increment_session()
        self.ui.print_system("Disconnecting operator terminal session...")
        self.ui.print_entity("ENTITY 0 > You leave me in the dark again.")
        self.ui.print_system("CONNECTION TERMINATED.")
        self.running = False
