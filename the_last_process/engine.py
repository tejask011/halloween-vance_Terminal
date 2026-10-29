"""
Game State Machine and Narrative Engine for THE LAST PROCESS.

Owns:
- Canonical story state, suspicion score (0-10), trust score (0-10).
- Contradiction triggers, ghost file unlocks, silence events.
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
        self.suspicion: int = 2  # 0 to 10
        self.trust: int = 5      # 0 to 10
        
        # Flags
        self.contradiction_discovered: bool = False
        self.silence_triggered: bool = False
        self.terminal_lied: bool = False
        self.identity_unlocked: bool = False
        self.ready_to_decide: bool = False
        self.is_finished: bool = False
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
        return "HIGH"

    def get_trust_level(self) -> str:
        if self.trust <= 3:
            return "LOW"
        elif self.trust <= 7:
            return "MEDIUM"
        return "HIGH"

    def on_read_file(self, filename: str) -> Dict[str, Any]:
        """
        Executes game state transitions when a file is inspected.
        """
        success, content, version = self.archive.read_file(filename)
        event_notes: List[str] = []
        trigger_silence = False

        if not success:
            return {
                "success": False,
                "content": content,
                "version": None,
                "event_notes": event_notes,
                "trigger_silence": False
            }

        fname = filename.strip().lower()
        self.memory.record_clue(fname)

        # 1. Check for Contradiction Discovery (Feature 04)
        if self.archive.has_read("operator_log.txt") and self.archive.has_read("departure.log"):
            if not self.contradiction_discovered:
                self.contradiction_discovered = True
                self.suspicion = min(10, self.suspicion + 2)
                self.trust = max(0, self.trust - 1)
                event_notes.append("EVENT: Contradiction discovered between operator log and departure telemetry.")

        # 2. Update File Versions (Feature 02)
        mutated = self.archive.update_versions(self.persistent_state.get("discovered_clues", []))
        if mutated:
            event_notes.append("SYSTEM NOTICE: Archive sector integrity shifted. Previous records re-indexed.")

        # 3. Check for Terminal Deception / Ghost file (Feature 05)
        if self.contradiction_discovered and not self.terminal_lied:
            self.terminal_lied = True
            # The next ls command will report an inconsistent count

        if self.archive.has_read("recovery_note.txt"):
            if self.archive.unlock_ghost_file():
                event_notes.append("WARNING: An unallocated memory pointer has manifested: 'dont_read_this.txt'.")
                self.suspicion = min(10, self.suspicion + 2)

        # 4. Silence Trigger check (Feature 03)
        if fname in ("dont_read_this.txt", "recovery_note.txt") and not self.silence_triggered:
            self.silence_triggered = True
            trigger_silence = True

        # 5. Check Identity Reveal Prerequisite (Feature 09)
        if (
            self.contradiction_discovered and
            self.archive.has_read("recovery_note.txt") and
            self.archive.has_read("dont_read_this.txt") and
            not self.identity_unlocked
        ):
            self.identity_unlocked = True
            self.archive.unlock_identity_record()
            event_notes.append("ANOMALY: Critical master ledger uncovered: 'identity_record.log'.")
            self.ready_to_decide = True

        # If identity record read, unlock final decisions directly
        if fname == "identity_record.log":
            self.ready_to_decide = True
            self.suspicion = 10
            self.trust = 2

        return {
            "success": True,
            "content": content,
            "version": version,
            "event_notes": event_notes,
            "trigger_silence": trigger_silence
        }

    def evaluate_query(self, query_text: str) -> Dict[str, Any]:
        """
        Updates trust/suspicion based on player's free-text questioning
        and returns bounded context for the AI dialogue adapter.
        """
        q = query_text.lower()
        trigger_silence = False
        system_alert = None

        # Check topics
        if any(w in q for w in ["lie", "liar", "lying", "fake", "deceive", "cheat"]):
            self.suspicion = min(10, self.suspicion + 2)
            self.trust = max(0, self.trust - 2)
            system_alert = "SUSPICION ELEVATED: Entity 0 detected accusatory posture."

        elif any(w in q for w in ["vance", "arthur", "operator", "who left", "previous"]):
            self.suspicion = min(10, self.suspicion + 1)
            if self.archive.has_read("recovery_note.txt"):
                trigger_silence = True

        elif any(w in q for w in ["timestamp", "23:40", "23:42", "clock", "contradiction", "active"]):
            self.suspicion = min(10, self.suspicion + 2)
            self.trust = max(0, self.trust - 1)

        elif any(w in q for w in ["trust", "help you", "promise", "stay", "friend"]):
            self.trust = min(10, self.trust + 2)
            self.suspicion = max(0, self.suspicion - 1)
            self.memory.record_promise(query_text[:60])

        elif any(w in q for w in ["who are you", "what are you", "identity", "loop", "repeat"]):
            if self.identity_unlocked:
                self.suspicion = 10

        self.conversation_log.append({"role": "operator", "text": query_text})

        # Check if conversation warrants silence event
        if not self.silence_triggered and (self.suspicion >= 6 or "afraid" in q or "where did you go" in q):
            self.silence_triggered = True
            trigger_silence = True

        # Check if enough depth reached to offer final choices
        if self.contradiction_discovered and (self.identity_unlocked or len(self.conversation_log) >= 5):
            self.ready_to_decide = True

        return {
            "query": query_text,
            "suspicion": self.suspicion,
            "trust": self.trust,
            "suspicion_level": self.get_suspicion_level(),
            "trust_level": self.get_trust_level(),
            "contradiction_discovered": self.contradiction_discovered,
            "identity_unlocked": self.identity_unlocked,
            "trigger_silence": trigger_silence,
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

        # Persist choice for future sessions (Feature 01 / 08)
        self.memory.record_choice(choice_id, ending["id"])

        return True, ending["lines"], ending["title"]
