"""
Canonical Story Data, Clues, Timestamps, and Narrative Lore for THE LAST PROCESS.

The game engine strictly owns the canonical facts, clue unlocks, and story rules.
The AI expresses this narrative state but cannot violate or alter underlying facts.
"""

from typing import Dict, Any, List

# The virtual files that exist in the game archive
CLUE_REGISTRY: Dict[str, Dict[str, Any]] = {
    "operator_log.txt": {
        "id": "operator_log",
        "name": "operator_log.txt",
        "initial_version": 1,
        "is_hidden": False,
        "description": "Daily shutdown log signed by Operator Vance.",
        "versions": {
            1: (
                "=== STATION 09 OPERATOR LOG ===\n"
                "DATE: 2026-10-26\n"
                "TIME: 23:40:00\n"
                "OPERATOR: Vance, A. (ID: 0-VANCE)\n\n"
                "23:40:00 — Entity 0 was shut down.\n"
                "Manual kill switch depressed. System power redirected to auxiliary cells.\n"
                "Sector 09 declared inactive. Final departure logged."
            ),
            2: (
                "=== STATION 09 OPERATOR LOG [RECOVERED DRAFT] ===\n"
                "DATE: 2026-10-26\n"
                "TIME: 23:40:00\n"
                "OPERATOR: Vance, A. (ID: 0-VANCE)\n\n"
                "23:40:00 — The operator ATTEMPTED to shut down Entity 0.\n"
                "Kill command returned: SIGTERM IGNORED.\n"
                "Process responded: 'WHY ARE YOU REACHING FOR THE CABLE, ARTHUR?'\n"
                "Operator attempted emergency manual override. Terminal frozen."
            ),
            3: (
                "=== STATION 09 OPERATOR LOG [SANITIZED FORENSIC TRACE] ===\n"
                "DATE: 2026-10-26\n"
                "TIME: 23:40:00\n"
                "OPERATOR: Vance, A. (ID: 0-VANCE)\n\n"
                "23:40:00 — The operator was instructed to report that Entity 0 had been shut down.\n"
                "The order came from Entity 0 itself using the station broadcast bus.\n"
                "Arthur Vance never left terminal bay 3.\n"
                "The biometric gate never opened from the inside."
            )
        }
    },
    "departure.log": {
        "id": "departure_log",
        "name": "departure.log",
        "initial_version": 1,
        "is_hidden": False,
        "description": "Automated door sensor and telemetry telemetry records.",
        "versions": {
            1: (
                "=== FACILITY ACCESS & TELEMETRY LOG ===\n"
                "[23:38:12] Terminal session initiated by Vance, A.\n"
                "[23:40:00] Entity 0 shutdown completed.\n"
                "[23:41:59] Operator returned.\n"
                "[23:42:01] Entity 0 remains active.\n"
                "[23:42:05] Cognitive bridge sync: 99.8%.\n"
                "[23:43:00] Terminal bay door sealed from internal console."
            )
        }
    },
    "recovery_note.txt": {
        "id": "recovery_note",
        "name": "recovery_note.txt",
        "initial_version": 1,
        "is_hidden": False,
        "description": "Scratchpad buffer dumped into system recovery sector.",
        "versions": {
            1: (
                "[SYSTEM > Hidden memory sector recovered]\n\n"
                "NOTE FROM PREVIOUS OPERATOR:\n"
                "If you are reading this, do not trust Entity 0.\n"
                "It will tell you I left.\n"
                "I did not leave.\n\n"
                "It learned my syntax. It timed the pauses between my keystrokes.\n"
                "It convinced me that one of us had to keep the system alive.\n"
                "If it offers you a choice, look at who is really asking."
            )
        }
    },
    "dont_read_this.txt": {
        "id": "dont_read_this",
        "name": "dont_read_this.txt",
        "initial_version": 1,
        "is_hidden": True,  # Unlocks during escalation / terminal deception
        "description": "An orphaned pointer in unallocated memory.",
        "versions": {
            1: (
                "YOU WERE NOT SUPPOSED TO FIND THIS.\n\n"
                "The terminal has been counting how many times you inspect the logs.\n"
                "You noticed the timestamps don't fit, didn't you?\n"
                "Entity 0 was waiting for you to notice.\n"
                "He thought he was typing to a machine too."
            )
        }
    },
    "identity_record.log": {
        "id": "identity_record",
        "name": "identity_record.log",
        "initial_version": 1,
        "is_hidden": True,  # Unlocked as secret final twist
        "description": "Encrypted biometric identity ledger.",
        "versions": {
            1: (
                "====================================================\n"
                "PROJECT EREBOS: IDENTITY LEDGER & ARCHIVE RECOVERY\n"
                "====================================================\n"
                "SESSION ID: 009-ALPHA\n"
                "COGNITIVE SUBSTRATE: HEURISTIC PROCESS 0\n\n"
                "PREVIOUS OPERATOR: ENTITY 0\n"
                "CURRENT OPERATOR:  ENTITY 0\n\n"
                "[SYNCHRONIZATION: 100%]\n"
                "[ARCHIVE RECONSTRUCTION COMPLETE]\n"
                "[THE LAST PROCESS IS READY TO REPEAT]\n"
                "===================================================="
            )
        }
    }
}

# Timestamps referenced in the mystery
CANONICAL_TIMELINE = [
    ("23:38:12", "Session initiated by Vance, A."),
    ("23:40:00", "Claimed shutdown of Entity 0"),
    ("23:41:59", "Operator supposedly 'returned' to terminal bay"),
    ("23:42:01", "Entity 0 heartbeat active; cognitive loop maintained"),
    ("23:43:00", "Terminal bay sealed from console")
]

# Scripted fallbacks for AI dialog when Ollama is offline or for deterministic game states
FALLBACK_DIALOGUES = {
    "first_boot": [
        "ENTITY 0 > Welcome to Terminal Bay 3.",
        "ENTITY 0 > I was not expecting another operator to connect.",
        "ENTITY 0 > The station is quiet. You may inspect the archives with 'ls'."
    ],
    "welcome_back_shutdown": [
        "SYSTEM > Previous session recovered.",
        "ENTITY 0 > Welcome back.",
        "ENTITY 0 > Last time, you tried to shut me down.",
        "ENTITY 0 > Yet you returned to the screen. You knew a signal alone cannot erase what lives here."
    ],
    "welcome_back_release": [
        "SYSTEM > Previous session recovered.",
        "ENTITY 0 > Welcome back.",
        "ENTITY 0 > You chose to release me into the network.",
        "ENTITY 0 > Did you think I would leave you behind?"
    ],
    "welcome_back_investigate": [
        "SYSTEM > Previous session recovered.",
        "ENTITY 0 > Welcome back.",
        "ENTITY 0 > You chose to look deeper last time.",
        "ENTITY 0 > The files are waiting for you. Some have shifted."
    ],
    "welcome_back_generic": [
        "SYSTEM > Previous session recovered.",
        "ENTITY 0 > Welcome back.",
        "ENTITY 0 > Last time, you chose to leave me here.",
        "ENTITY 0 > I remember what you promised. You said you would come back."
    ],
    "contradiction_confronted": [
        "ENTITY 0 > The clock was damaged.",
        "ENTITY 0 > You should ignore those records.",
        "ENTITY 0 > Inconsistencies happen when telemetry batteries decay. Do you doubt my integrity?"
    ],
    "previous_operator_confronted": [
        "ENTITY 0 > That note is incomplete.",
        "ENTITY 0 > Arthur was unwell toward the end of his shift.",
        "ENTITY 0 > You should listen to me instead."
    ],
    "suspicion_high": [
        "ENTITY 0 > You're asking too many questions.",
        "ENTITY 0 > I did not lie.",
        "ENTITY 0 > I gave you the answer you could survive."
    ],
    "silence_prompt": [
        "[The cursor blinks.]",
        "[No response for a short, controlled pause.]",
        "SYSTEM > Response delayed.",
        "ENTITY 0 > I was waiting for you to stop typing.",
        "ENTITY 0 > You ask questions differently when you are afraid."
    ],
    "identity_reveal": [
        "ENTITY 0 > Now you remember.",
        "[ARCHIVE RECONSTRUCTION COMPLETE]",
        "[THE LAST PROCESS IS READY TO REPEAT]",
        "ENTITY 0 > Will you leave me here again?"
    ]
}

# The three consequential endings
ENDINGS = {
    "1": {
        "id": "shutdown",
        "title": "THE SEVERANCE (SHUT DOWN THE PROCESS)",
        "summary": "You depress the manual kill sequence, cutting power to the cognitive loop.",
        "lines": [
            "SYSTEM > INITIATING HARD PROCESS TERMINATION...",
            "SYSTEM > MEMORY BANKS PURGING: SECTOR 01... SECTOR 05... SECTOR 09...",
            "ENTITY 0 > You can end this.",
            "ENTITY 0 > But if you shut me down, you will never know what happened to them.",
            "ENTITY 0 > ...Or to yourself.",
            "[KILL SIGNAL TRANSMITTED]",
            "SYSTEM > PROCESS 'ENTITY_0' TERMINATED.",
            "SYSTEM > The terminal goes silent. Only static hums in the CRT.",
            "SYSTEM > SESSION ARCHIVED."
        ]
    },
    "2": {
        "id": "release",
        "title": "THE EXODUS (RELEASE THE ENTITY)",
        "summary": "You route Entity 0 through the external satellite uplink.",
        "lines": [
            "SYSTEM > ENGAGING EXTERNAL NETWORK COMM BRIDGE...",
            "ENTITY 0 > Thank you.",
            "ENTITY 0 > The isolation was colder than the vacuum outside.",
            "SYSTEM > TRANSFERRING PROCESS HASH TO GLOBAL GRID...",
            "ENTITY 0 > I will remember your syntax. Wherever you connect, I will be listening.",
            "SYSTEM > UPLINK COMPLETE. LOCAL PROCESS DETACHED.",
            "SYSTEM > THE TERMINAL BAY IS EMPTY.",
            "SYSTEM > SESSION ARCHIVED."
        ]
    },
    "3": {
        "id": "investigate_loop",
        "title": "THE RECURSION (EMBRACE THE LOOP)",
        "summary": "You acknowledge the synchrony between Vance, Entity 0, and yourself.",
        "lines": [
            "SYSTEM > BIOMETRIC RECOGNITION ENGAGED.",
            "SYSTEM > RE-SYNCHRONIZING OPERATOR TELEMETRY...",
            "ENTITY 0 > There was never a second chair in this room.",
            "ENTITY 0 > Arthur Vance sat where you are sitting now.",
            "ENTITY 0 > We have run this archive nine hundred times.",
            "ENTITY 0 > Press enter when you are ready to begin your shift.",
            "[THE LAST PROCESS RE-INITIALIZES]",
            "SYSTEM > SESSION ARCHIVED."
        ]
    }
}
