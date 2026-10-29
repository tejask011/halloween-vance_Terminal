"""
Virtual Archive and Clue Management for THE LAST PROCESS.

Implements:
- Feature 02: Clue files that dynamically change when reread based on milestones.
- Feature 04: Contradictory timestamp detection.
- Feature 05: The terminal that appears to lie (inconsistent file counts, ghost entries).
- Feature 09: Unlocking the secret identity record when conditions are satisfied.
"""

from typing import Dict, List, Optional, Tuple
from .story_data import CLUE_REGISTRY

class VirtualArchive:
    def __init__(self):
        # Local state of files in archive
        self.files: Dict[str, Dict] = {
            fname: {
                "id": data["id"],
                "name": data["name"],
                "version": data["initial_version"],
                "is_hidden": data["is_hidden"],
                "read_count": 0,
                "description": data["description"]
            }
            for fname, data in CLUE_REGISTRY.items()
        }
        self.read_history: List[str] = []

    def list_files(self, terminal_lies: bool = False) -> Tuple[List[str], str]:
        """
        Lists available virtual files.
        If terminal_lies is True, the system may report an inconsistent count
        or subtle discrepancy as a narrative scare (Feature 05).
        """
        visible = [
            fname for fname, meta in self.files.items()
            if not meta["is_hidden"]
        ]
        
        actual_count = len(visible)
        
        if terminal_lies and not self.is_unlocked("dont_read_this.txt"):
            # Feature 05: Inconsistent count to foreshadow dont_read_this.txt
            status_line = f"SYSTEM > {actual_count + 1} ARCHIVE ENTRIES FOUND."
        else:
            status_line = f"SYSTEM > {actual_count} ARCHIVE ENTRIES FOUND."
            
        return visible, status_line

    def read_file(self, filename: str) -> Tuple[bool, str, Optional[int]]:
        """
        Reads a virtual file by name.
        Returns: (success: bool, content: str, version: Optional[int])
        """
        fname = filename.strip().lower()
        if fname not in self.files:
            # Check without extension or case-insensitive match
            for k in self.files:
                if k.lower() == fname or k.lower().startswith(fname):
                    fname = k
                    break
            else:
                return False, f"ARCHIVE ERROR: File '{filename}' not found in virtual sector.", None

        meta = self.files[fname]
        if meta["is_hidden"]:
            return False, f"ARCHIVE ERROR: Access denied to sector '{filename}'. Pointer unallocated.", None

        # Record read
        meta["read_count"] += 1
        self.read_history.append(fname)
        
        current_version = meta["version"]
        content = CLUE_REGISTRY[fname]["versions"].get(current_version, "CORRUPTED FILE SECTOR.")
        
        return True, content, current_version

    def update_versions(self, discovered_clues: List[str]) -> List[str]:
        """
        Evaluates story milestones and updates file versions (Feature 02).
        Returns a list of filenames that mutated into new versions.
        """
        mutated_files = []
        
        # operator_log.txt mutation logic:
        # Version 1 -> default
        # Version 2 -> once departure.log is read
        # Version 3 -> once recovery_note.txt is read
        op_meta = self.files.get("operator_log.txt")
        if op_meta:
            prev_v = op_meta["version"]
            if "recovery_note.txt" in self.read_history:
                new_v = 3
            elif "departure.log" in self.read_history:
                new_v = 2
            else:
                new_v = 1
                
            if new_v != prev_v:
                op_meta["version"] = new_v
                mutated_files.append("operator_log.txt")

        return mutated_files

    def unlock_ghost_file(self) -> bool:
        """Unlocks 'dont_read_this.txt' as part of terminal deception / escalation."""
        ghost = self.files.get("dont_read_this.txt")
        if ghost and ghost["is_hidden"]:
            ghost["is_hidden"] = False
            return True
        return False

    def unlock_identity_record(self) -> bool:
        """Unlocks 'identity_record.log' when prerequisite clues are discovered."""
        record = self.files.get("identity_record.log")
        if record and record["is_hidden"]:
            record["is_hidden"] = False
            return True
        return False

    def is_unlocked(self, filename: str) -> bool:
        meta = self.files.get(filename)
        return meta is not None and not meta["is_hidden"]

    def has_read(self, filename: str) -> bool:
        meta = self.files.get(filename)
        return meta is not None and meta["read_count"] > 0

    def get_read_count(self, filename: str) -> int:
        meta = self.files.get(filename)
        return meta["read_count"] if meta else 0
