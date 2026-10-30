"""
Game State Machine and Narrative Engine for THE LAST PROCESS.

Owns:
- Canonical story state, suspicion score (0-10), trust score (0-10).
- Station power level (100% down to 10%), heart rate BPM (65 to 130), sanity index.
- Contradiction triggers, ghost file unlocks, silence events, jumpscare events.
- Ending availability validation and moral choice resolution.
"""

from typing import Dict, Any, List, Optional, Tuple
from .archive import VirtualArchive
from .memory import MemoryStore
from .story_data import ENDINGS

class GameEngine:
    def __init__(self, memory_store: Optional[MemoryStore] = None):
        self.memory = memory_store or MemoryStore()
        self.persistent_state = self.memory.load()
        self.archive = VirtualArchive()

        # Engine Bounded State
        self.suspicion: int = 2      # 0 to 10
        self.trust: int = 5          # 0 to 10
        self.power_level: int = 100  # 100% down to 10%
        self.heartbeat_bpm: int = 68 # 65 to 135 BPM
        self.sanity: int = 100       # 100% down to 15%
        
        # Flags
        self.contradiction_discovered: bool = False
        self.silence_triggered: bool = False
        self.terminal_lied: bool = False
        self.identity_unlocked: bool = False
        self.ready_to_decide: bool = False
        self.is_finished: bool = False
        self.jumpscare_triggered: bool = False
        self.selected_ending: Optional[str] = None
        
        # Free-text conversation history
        self.conversation_log: List[Dict[str, str]] = []

    @property
    def session_count(self) -> int:
        return self.persistent_state.get("session_count", 1)

    @property
    def last_ending(self) -> Optional[str]:
        return self.persistent_state.get("last_ending")

    def get_suspicion_level(self) -> str:
        if self.suspicion <= 3:
            return "LOW"
        elif self.suspicion <= 7:
            return "MEDIUM"
        return "CRITICAL"

    def get_trust_level(self) -> str:
        if self.trust <= 3:
            return "HOSTILE"
        elif self.trust <= 7:
            return "EVASIVE"
        return "INTIMATE"

    def get_active_files_map(self) -> Dict[str, str]:
        """
        Returns a mapping of numbered shortcuts [1..N] and keywords to virtual filenames.
        Allows instant access without typing long filenames!
        """
        mapping = {
            "1": "operator_log.txt",
            "operator": "operator_log.txt",
            "operator_log": "operator_log.txt",
            "operator_log.txt": "operator_log.txt",
            "vance": "operator_log.txt",

            "2": "departure.log",
            "departure": "departure.log",
            "departure.log": "departure.log",
            "telemetry": "departure.log",

            "3": "recovery_note.txt",
            "recovery": "recovery_note.txt",
            "recovery_note": "recovery_note.txt",
            "recovery_note.txt": "recovery_note.txt",
            "note": "recovery_note.txt",
        }

        if self.archive.is_unlocked("dont_read_this.txt"):
            mapping["4"] = "dont_read_this.txt"
            mapping["dont_read_this"] = "dont_read_this.txt"
            mapping["dont_read_this.txt"] = "dont_read_this.txt"
            mapping["corrupted"] = "dont_read_this.txt"

        if self.archive.is_unlocked("identity_record.log"):
            mapping["5"] = "identity_record.log"
            mapping["identity"] = "identity_record.log"
            mapping["identity_record"] = "identity_record.log"
            mapping["identity_record.log"] = "identity_record.log"
            mapping["ledger"] = "identity_record.log"

        return mapping

    def on_read_file(self, filename: str) -> Dict[str, Any]:
        """
        Executes game state transitions when a file is inspected.
        """
        # Resolve shortcut if provided
        file_map = self.get_active_files_map()
        cleaned_key = filename.strip().lower()
        if cleaned_key in file_map:
            target_file = file_map[cleaned_key]
        else:
            target_file = filename

        success, content, version = self.archive.read_file(target_file)
        event_notes: List[str] = []
        trigger_silence = False
        trigger_jumpscare = False
        trigger_glitch = False

        if not success:
            return {
                "success": False,
                "content": content,
                "version": None,
                "event_notes": event_notes,
                "trigger_silence": False,
                "trigger_jumpscare": False,
                "trigger_glitch": False
            }

        fname = target_file.strip().lower()
        self.memory.record_clue(fname)

        # 1. Check for Contradiction Discovery (Feature 04)
        if self.archive.has_read("operator_log.txt") and self.archive.has_read("departure.log"):
            if not self.contradiction_discovered:
                self.contradiction_discovered = True
                self.suspicion = min(10, self.suspicion + 3)
                self.trust = max(0, self.trust - 2)
                self.power_level = max(10, self.power_level - 18)
                self.heartbeat_bpm = 88
                self.sanity = max(15, self.sanity - 20)
                trigger_glitch = True
                event_notes.append("CRITICAL: Severe timestamp paradox between operator log (23:40:00) and telemetry (23:42:01).")

        # 2. Update File Versions (Feature 02)
        mutated = self.archive.update_versions(self.persistent_state.get("discovered_clues", []))
        if mutated:
            event_notes.append("ANOMALY: Archive sector integrity mutated. Prior records have rewritten themselves.")

        # 3. Check for Terminal Deception / Ghost file (Feature 05)
        if self.contradiction_discovered and not self.terminal_lied:
            self.terminal_lied = True

        if self.archive.has_read("recovery_note.txt"):
            if self.archive.unlock_ghost_file():
                self.power_level = max(10, self.power_level - 22)
                self.heartbeat_bpm = 104
                self.sanity = max(15, self.sanity - 25)
                trigger_glitch = True
                event_notes.append("WARNING: Corrupted memory pointer materialized at sector 0x7F: [4] dont_read_this.txt.")
                self.suspicion = min(10, self.suspicion + 2)

        # 4. Silence Trigger check (Feature 03)
        if fname in ("dont_read_this.txt", "recovery_note.txt") and not self.silence_triggered:
            self.silence_triggered = True
            trigger_silence = True

        # 5. Jumpscare when reading dont_read_this.txt
        if fname == "dont_read_this.txt" and not self.jumpscare_triggered:
            self.jumpscare_triggered = True
            trigger_jumpscare = True
            self.heartbeat_bpm = 126
            self.power_level = max(10, self.power_level - 25)
            self.sanity = max(15, self.sanity - 30)

        # 6. Check Identity Reveal Prerequisite (Feature 09)
        if (
            self.contradiction_discovered and
            self.archive.has_read("recovery_note.txt") and
            self.archive.has_read("dont_read_this.txt") and
            not self.identity_unlocked
        ):
            self.identity_unlocked = True
            self.archive.unlock_identity_record()
            event_notes.append("SECURITY OVERRIDE: Master biometric identity ledger breached: [5] identity_record.log.")
            self.ready_to_decide = True

        # If identity record read, unlock final decisions directly
        if fname == "identity_record.log":
            self.ready_to_decide = True
            self.suspicion = 10
            self.trust = 1
            self.power_level = 12  # Emergency power
            self.heartbeat_bpm = 135
            self.sanity = 15

        return {
            "success": True,
            "filename": target_file,
            "content": content,
            "version": version,
            "event_notes": event_notes,
            "trigger_silence": trigger_silence,
            "trigger_jumpscare": trigger_jumpscare,
            "trigger_glitch": trigger_glitch
        }

    def evaluate_query(self, query_text: str) -> Dict[str, Any]:
        """
        Updates trust/suspicion based on player's free-text questioning
        and returns bounded context for the AI dialogue adapter.
        """
        q = query_text.lower().strip()
        trigger_silence = False
        trigger_glitch = False
        system_alert = None

        # Check topics
        if any(w in q for w in ["lie", "liar", "lying", "fake", "deceive", "cheat", "trick"]):
            self.suspicion = min(10, self.suspicion + 2)
            self.trust = max(0, self.trust - 2)
            self.heartbeat_bpm = min(130, self.heartbeat_bpm + 10)
            trigger_glitch = True
            system_alert = "SUSPICION ELEVATED: Entity 0 detected hostile interrogation."

        elif any(w in q for w in ["vance", "arthur", "operator", "who left", "previous", "dead", "kill", "murder"]):
            self.suspicion = min(10, self.suspicion + 1)
            self.heartbeat_bpm = min(130, self.heartbeat_bpm + 6)
            if self.archive.has_read("recovery_note.txt"):
                trigger_silence = True

        elif any(w in q for w in ["timestamp", "23:40", "23:42", "clock", "contradiction", "active", "time"]):
            self.suspicion = min(10, self.suspicion + 2)
            self.trust = max(0, self.trust - 1)
            trigger_glitch = True

        elif any(w in q for w in ["trust", "help you", "promise", "stay", "friend", "help"]):
            self.trust = min(10, self.trust + 2)
            self.suspicion = max(0, self.suspicion - 1)
            self.memory.record_promise(query_text[:60])

        elif any(w in q for w in ["who are you", "what are you", "identity", "loop", "repeat", "am i vance"]):
            if self.identity_unlocked:
                self.suspicion = 10
                self.heartbeat_bpm = 130

        self.conversation_log.append({"role": "operator", "text": query_text})

        # Check if conversation warrants silence event
        if not self.silence_triggered and (self.suspicion >= 6 or "afraid" in q or "scared" in q or "where did you go" in q):
            self.silence_triggered = True
            trigger_silence = True

        # Check if enough depth reached to offer final choices
        if self.contradiction_discovered and (self.identity_unlocked or len(self.conversation_log) >= 5):
            self.ready_to_decide = True

        return {
            "query": query_text,
            "suspicion": self.suspicion,
            "trust": self.trust,
            "power_level": self.power_level,
            "heartbeat_bpm": self.heartbeat_bpm,
            "sanity": self.sanity,
            "suspicion_level": self.get_suspicion_level(),
            "trust_level": self.get_trust_level(),
            "contradiction_discovered": self.contradiction_discovered,
            "identity_unlocked": self.identity_unlocked,
            "trigger_silence": trigger_silence,
            "trigger_glitch": trigger_glitch,
            "system_alert": system_alert
        }

    def execute_choice(self, choice_id: str) -> Tuple[bool, List[str], str]:
        """
        Executes the final consequential moral choice (Feature 08).
        Choices:
        '1': Shutdown the process
        '2': Release the entity
        '3': Embrace the loop (Investigate further / recursion)
        """
        if choice_id not in ENDINGS:
            return False, ["INVALID CHOICE. Select 1, 2, or 3."], ""

        ending = ENDINGS[choice_id]
        self.is_finished = True
        self.selected_ending = ending["id"]

        # Persist choice for future sessions
        self.memory.record_choice(choice_id, ending["id"])

        return True, ending["lines"], ending["title"]
