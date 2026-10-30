# THE LAST PROCESS
### *A safety-first, AI-powered terminal horror game*
> **Submission for Hacktoberfest 2026 Week 4 DEV Challenge: "Ghost in the Machine"**

---


<img width="645" height="142" alt="image" src="https://github.com/user-attachments/assets/d4ea1cda-9bb1-4d6b-b412-2fa0ca7535c1" />



## 🌌 Overview

**THE LAST PROCESS** is an atmospheric, retro terminal horror experience powered by open-source, local AI inference (via **Ollama** running models like **Gemma 2**, **Llama 3.2**, or **Mistral**) with 100% offline deterministic fallback support.

You sit down at an abandoned monitor in Terminal Bay 3 of Project Erebos. The previous operator, Arthur Vance, reportedly logged off and initiated a hard system shutdown at 23:40 on October 26th. 

Yet the machine is humming. **Entity 0** is still active. And as you investigate the virtual archive, the logs begin to contradict each other, timestamps warp, the terminal itself begins to lie, and the boundary between operator and entity dissolves.

---

## ⚡ The 9 Core Features

1. **Persistent Memory Between Sessions**: Tracks `session_count`, past endings, and choices in an isolated local file. When you reboot the game, Entity 0 remembers:
   ```
   [SESSION 0002]
   SYSTEM > Previous session recovered.
   ENTITY 0 > Welcome back.
   ENTITY 0 > Last time, you tried to shut me down.
   ENTITY 0 > Yet you returned to the screen.
   ```
2. **Clue Files That Change When Reread**: Records mutate dynamically as you uncover more evidence. For example, `operator_log.txt` shifts:
   - *First read:* `23:40 — Entity 0 was shut down.`
   - *After reading `departure.log`:* `23:40 — The operator ATTEMPTED to shut down Entity 0.`
   - *After reading `recovery_note.txt`:* `23:40 — The operator was instructed to report that Entity 0 had been shut down.`
3. **Silence and Delayed-Response Events**: Controlled typewriter pauses, blinking cursor suspense, and `SYSTEM > Response delayed.` events when Entity 0 watches you hesitate.
4. **Contradictory Timestamps**: Explicit temporal paradoxes in telemetry records (e.g., claimed shutdown at 23:40:00 vs. active cognitive heartbeat at 23:42:01) trigger entity defensiveness.
5. **The Terminal Appears to Lie**: The terminal engine manifests phantom counts (`SYSTEM > 4 ARCHIVE ENTRIES FOUND.` when only 3 are visible), eventually materializing unallocated memory pointers like `dont_read_this.txt`.
6. **Trust and Suspicion Mechanics**: Bounded state indices (0–10) track player interrogation tone, unlocking new reactive dialogue trees and end-game branching.
7. **Messages from the Previous Operator**: Fragmented forensic notes (`recovery_note.txt`) warning: *"If you are reading this, do not trust Entity 0. It will tell you I left. I did not leave."*
8. **Consequential Moral Choice**: Three narrative conclusions:
   - `[1] SHUT DOWN THE PROCESS` — Hard memory purge.
   - `[2] RELEASE THE ENTITY` — Uplink Entity 0 into the open network.
   - `[3] EMBRACE THE LOOP` — Synchronize operator identities into the repeating cycle.
9. **Hidden Identity Reveal**: Exposing `identity_record.log` uncovers the ultimate twist: Vance, Entity 0, and the player are bound in an endless archive loop.

---

<img width="968" height="766" alt="image" src="https://github.com/user-attachments/assets/00410c0d-f4f4-44fc-83c1-ec672074d6d6" />

## 🛡️ Safety & Privacy Boundaries

Designed from the ground up under strict safety principles:
- **Zero Real Filesystem Access**: All files (`operator_log.txt`, `departure.log`, etc.) are virtual memory objects. The game never scans or touches host directories.
- **No Shell Execution**: Player input is strictly filtered through an allowlisted command parser. Input is never sent to `bash`, `cmd`, `PowerShell`, or `eval()`.
- **Fictional Shutdown Only**: The `shutdown` command only terminates the in-game process; it never executes host OS system shutdown routines.
- **Sanitized AI Output**: Strips ANSI injection codes, control sequences, and null bytes before terminal rendering.
- **Full Player Accessibility**: Instant quit (`quit`/`exit`), save-reset (`reset`), and reduced-motion/fast-mode (`speed` or `--fast`).

---

## 🚀 Quickstart & How to Play (100% Pure Terminal CLI)

No web server or localhost needed. Everything runs natively inside your terminal with real hardware audio synthesis, ASCII surveillance cameras, and interactive controls!

### 1. Requirements & Setup
```bash
# Clone or navigate to the repository
cd DEV4

# Install Python requirements
pip install -r requirements.txt
```

### 2. Launching the Game
```bash
# Standard launch (Halloween theme with hardware heartbeat audio & CRT effects)
python run.py

# Launch in Fast Mode (instant text rendering without typewriter delay)
python run.py --fast

# Launch with sound muted
python run.py --mute

# Custom theme (halloween, green, amber, monochrome)
python run.py --theme green
```

---

## 🎮 How to Play (No Long Typing Required!)

The game features an interactive **Terminal HUD**:
* **Press `1`**: Inspect Vance's shutdown report (`operator_log.txt`).
* **Press `2`**: Inspect departure sensor logs (`departure.log`) and expose the 23:42:01 timestamp paradox!
* **Press `3`**: Read Vance's hidden recovery scratchpad (`recovery_note.txt`).
* **Press `4`**: Breach unallocated memory (`dont_read_this.txt`) — triggers the jumpscare anomaly!
* **Press `5`**: Decrypt the master biometric identity ledger (`identity_record.log`).
* **Press `C`**: Access CCTV Surveillance Cameras in Terminal Bay 3.
* **Press `S`**: Check station diagnostics, auxiliary power, and heart rate monitor.
* **Press `M`**: Toggle hardware audio effects on/off.
* **Type freely**: Ask Entity 0 anything directly (e.g. *"why did you lie?"*, *"what happened to Vance?"*, *"what should I do?"*).
* **Press `K` or `decide`**: Execute the final consequential choice when power collapses!
| `speed` | Toggle teletype delays / fast-mode |
| `clear` | Clear terminal screen |
| `reset` | Wipe save state and reset back to Session 0001 |
| `quit` / `exit` | Disconnect safely from Terminal Bay 3 |

---

## 🧪 Testing

Run the automated test suite covering all 9 features, file mutations, safety boundaries, and AI fallbacks:
```bash
python -m unittest discover tests
```

---

## 📜 Architecture

```
the_last_process/
├── __init__.py
├── cli.py             # Main interactive loop, command parser, boot flow
├── ui.py              # Atmospheric CRT themes, teletype cadence, blinking cursor
├── engine.py          # State machine: suspicion, trust, contradiction triggers
├── archive.py         # Virtual archive & dynamic clue mutation engine
├── story_data.py      # Canon lore, timestamps, operator logs, dialogue trees
├── ai_adapter.py      # Ollama local inference client + offline fallback engine
├── memory.py          # Persistent session memory with save isolation & reset
└── safety.py          # Command allowlisting, ANSI sanitization, sandbox guard
```

---

## 🎃 Hacktoberfest Week 4: Ghost in the Machine
Built for Hacktoberfest 2026, celebrating open-source AI, local open-weight models, and eerie terminal storytelling.
