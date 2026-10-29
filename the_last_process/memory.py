"""
Persistent Game Memory for THE LAST PROCESS.

Implements Feature 01:
- Saves explicit in-game choices, discovered clues, session count, and endings.
- Dedicated user app-data or isolated game data path.
- Reset feature to wipe memory cleanly.
- Strict isolation: NEVER accesses or records real-world files, conversations, or system activity.
"""

import json
import os
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

DEFAULT_SAVE_DIR = Path.home() / ".the_last_process"
SAVE_FILE_NAME = "save_state.json"

DEFAULT_STATE: Dict[str, Any] = {
    "session_count": 0,
    "last_session_time": 0.0,
    "discovered_clues": [],
    "last_choice": None,
    "last_ending": None,
    "promises_made": [],
    "total_queries": 0,
    "identity_discovered": False,
    "operator_name_entered": None
}

class MemoryStore:
    def __init__(self, custom_dir: Optional[Path] = None):
        self.save_dir = custom_dir or DEFAULT_SAVE_DIR
        self.save_file = self.save_dir / SAVE_FILE_NAME
        self._ensure_storage()

    def _ensure_storage(self) -> None:
        try:
            self.save_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            # Fallback to local workspace if home directory is restricted
            self.save_dir = Path("./.game_data")
            self.save_dir.mkdir(parents=True, exist_ok=True)
            self.save_file = self.save_dir / SAVE_FILE_NAME

    def load(self) -> Dict[str, Any]:
        """Loads persistent session state or initializes default state if not found."""
        if not self.save_file.exists():
            state = dict(DEFAULT_STATE)
            state["session_count"] = 1
            state["last_session_time"] = time.time()
            return state

        try:
            with open(self.save_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Merge with defaults in case of missing keys
                state = dict(DEFAULT_STATE)
                state.update(data)
                return state
        except Exception:
            # Corrupted or unreadable save; fallback safely to defaults
            state = dict(DEFAULT_STATE)
            state["session_count"] = 1
            return state

    def save(self, state: Dict[str, Any]) -> bool:
        """Saves session state safely to JSON."""
        try:
            state["last_session_time"] = time.time()
            temp_file = self.save_file.with_suffix(".tmp")
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2)
            temp_file.replace(self.save_file)
            return True
        except Exception:
            return False

    def increment_session(self) -> Dict[str, Any]:
        """Advances the session counter and updates last session timestamp."""
        state = self.load()
        state["session_count"] = state.get("session_count", 0) + 1
        self.save(state)
        return state

    def record_clue(self, clue_id: str) -> None:
        state = self.load()
        clues = set(state.get("discovered_clues", []))
        clues.add(clue_id)
        state["discovered_clues"] = list(clues)
        self.save(state)

    def record_choice(self, choice_id: str, ending_name: Optional[str] = None) -> None:
        state = self.load()
        state["last_choice"] = choice_id
        if ending_name:
            state["last_ending"] = ending_name
        self.save(state)

    def record_promise(self, promise_text: str) -> None:
        state = self.load()
        promises = state.get("promises_made", [])
        if promise_text not in promises:
            promises.append(promise_text)
        state["promises_made"] = promises
        self.save(state)

    def reset_save(self) -> bool:
        """Wipes the save file completely for a fresh game experience."""
        try:
            if self.save_file.exists():
                self.save_file.unlink()
            return True
        except Exception:
            return False
