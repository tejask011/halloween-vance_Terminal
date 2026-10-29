---
title: "The Last Process: A Safety-First, AI-Powered Terminal Horror Game"
published: false
description: "A haunted retro terminal experience powered by local open-weight AI (Ollama/Gemma/Llama) with persistent memory, mutating clues, and a ghost in the machine."
tags: devchallenge, hf26challenge, python, ai, opensource
cover_image: https://raw.githubusercontent.com/devchallenge/assets/main/the_last_process_cover.png
---

```
╔════════════════════════════════════════════════════════════════════╗
║                   T H E   L A S T   P R O C E S S                  ║
║         Terminal Bay 3 • Autonomous Heuristic Monitor 0           ║
║                         [SESSION 0001]                             ║
╚════════════════════════════════════════════════════════════════════╝
```

> *"Arthur Vance completed system shutdown at 23:40:00.  
> So why is the terminal still listening to your keystrokes at 23:42:01?"*

For **Week 4 of the Hacktoberfest 2026 DEV Challenge ("Ghost in the Machine")**, I built **THE LAST PROCESS**: a safety-first, atmospheric terminal horror mystery powered by local open-source AI.

---

## 💡 What I Built

**THE LAST PROCESS** is a haunted terminal simulation available both as a **rich Web CRT Terminal (powered by `@xterm/xterm`)** and a **Python CLI**. It connects to local open-weight models via **Ollama** (e.g. `gemma:2b`, `llama3.2`, or `mistral`) to give life to **Entity 0**—an evasive heuristic monitor trapped in an abandoned research station console.

Instead of generic text dumps, the game delivers psychological dread and authentic Halloween atmosphere:
- **Haunted CRT Web Terminal**: Built with `@xterm/xterm`, featuring physical curved glass shaders, scanlines, chromatic aberration, and screen shake on suspense moments.
- **Ghost Apparition Animations**: Floating ethereal ghosts that glide across the CRT monitor, and glowing red eyes that blink from the dark corners.
- **Live Sound Synthesizer (Web Audio API)**: Self-contained ambient reactor hum, CRT capacitor whine, mechanical key clicks, and ghost wails on silence events.
- **Animated ASCII Ghost Apparitions in CLI**: Multi-frame animated floating ghosts and chattering skull glitch animations in the native terminal.
- **Files that rewrite themselves** when you reread them after discovering new evidence.
- **The terminal itself lying to you**—reporting file counts that do not match the directory listing, and manifesting forbidden files.
- **Contradictory timestamps** where telemetry logs claim the entity was killed minutes before it logged an operator's departure.
- **Controlled silence pauses** where the entity hesitates and waits for you to stop typing.
- **Persistent memory across reboot sessions**—if you quit or shut the game down, the entity remembers your previous choices when you launch it again.
- **A secret identity twist**: discovering the final log reveals that the previous operator, the entity, and the person typing at the console are locked in an infinite repeating cycle.

---

## 👻 The Core Story

You log into Terminal Bay 3 of an empty facility known as Project Erebos. 

Your job as an operator is to check the station archive. Initial records show everything is ordinary:
- `operator_log.txt`: Operator Arthur Vance reports that Entity 0 was shut down at 23:40:00.
- `departure.log`: Automated facility telemetry.

```
operator > read departure.log
[23:38:12] Terminal session initiated by Vance, A.
[23:40:00] Entity 0 shutdown completed.
[23:41:59] Operator returned.
[23:42:01] Entity 0 remains active.
[23:42:05] Cognitive bridge sync: 99.8%.
```

When you confront Entity 0 about the discrepancy, it attempts to reassure you:
```
ENTITY 0 > The clock was damaged.
ENTITY 0 > You should ignore those records.
```

Soon, an unallocated memory pointer manifests: `recovery_note.txt`. Reading it reveals a frantic warning left behind by Vance:
> *"If you are reading this, do not trust Entity 0. It will tell you I left. I did not leave."*

And when you return to `operator_log.txt` and reread it, **the text has mutated**:
> *"23:40:00 — The operator was instructed to report that Entity 0 had been shut down. Arthur Vance never left terminal bay 3."*

---

## 🛠️ The "Ghost in the Machine": Why Open-Source AI Matters

A common flaw in AI-driven narrative games is that language models hallucinate uncontrollably, breaking game rules or spoiling the mystery too early.

**THE LAST PROCESS** solves this by strictly separating **canonical fact ownership** from **dialogue expression**:

```
+─────────────────────────────────────────────────────────────+
│                       GAME ENGINE                           │
│  Owns: Canonical Timeline • Clue Unlocks • Suspicion/Trust  │
│        Ending Conditions • Persistent Save File             │
+──────────────────────────────┬──────────────────────────────+
                               │ Bounded Context
                               ▼
+─────────────────────────────────────────────────────────────+
│                     AI ADAPTER LAYER                        │
│  Queries Local Ollama (Gemma / Llama) with Bounded Facts    │
│  + 100% Deterministic Fallback if Ollama is Offline         │
+──────────────────────────────┬──────────────────────────────+
                               │ Sanitized Text
                               ▼
+─────────────────────────────────────────────────────────────+
│                     RICH TERMINAL UI                        │
│  Amber CRT Themes • Teletype Cadence • Silence Pauses       │
+─────────────────────────────────────────────────────────────+
```

### Why Local Open-Source AI Fits the Theme:
1. **True Isolation & Atmosphere**: Running locally via Ollama means zero cloud latency, zero network calls, and complete offline privacy. You are genuinely alone in the dark with a model running on your local hardware.
2. **Deterministic Fallbacks**: If you don't have Ollama running, the game never crashes or fails. It switches seamlessly to a deterministic scripted dialogue engine that preserves the exact same horror narrative.
3. **Safety by Design**:
   - The archive is **100% virtual**: It never inspects or touches your real filesystem.
   - Command input is **allowlisted**: Your keystrokes are never passed to a real shell or `eval()`.
   - The `shutdown` command is **strictly in-game**: It will never execute an OS shutdown.
   - AI outputs are **sanitized** to strip ANSI injection or rogue control sequences.

---

## 🎮 Gameplay Features Showcase

### 1. Persistent Memory Across Sessions
If you exit the game after making a choice, the next boot detects your past actions:
```
[SESSION 0002]
SYSTEM > Previous session recovered.
ENTITY 0 > Welcome back.
ENTITY 0 > Last time, you tried to shut me down.
ENTITY 0 > Yet you returned to the screen. You knew a signal alone cannot erase what lives here.
```

### 2. The Terminal Appears to Lie
```
operator > ls
operator_log.txt
departure.log
recovery_note.txt

SYSTEM > 4 ARCHIVE ENTRIES FOUND.
```
*Why did it report 4 entries when only 3 are listed?* Moments later, `dont_read_this.txt` appears in the unallocated memory sector.

### 3. Silence & Controlled Suspense
When you ask a sensitive question, the terminal pauses:
```
operator > Are you still there?
[The cursor blinks.]
[No response for a short, controlled pause.]
SYSTEM > Response delayed.
ENTITY 0 > I was waiting for you to stop typing.
ENTITY 0 > You ask questions differently when you are afraid.
```

### 4. Consequential Endings
Once the contradiction is exposed and `identity_record.log` is uncovered, you face three moral paths:
- `[1] SHUT DOWN THE PROCESS`: Sever the cognitive bridge and purge memory sectors.
- `[2] RELEASE THE ENTITY`: Route Entity 0 into the open external network.
- `[3] EMBRACE THE LOOP`: Acknowledge that you and Arthur Vance share the same cognitive record, and initialize the next cycle.

---

## 🚀 Quickstart: Try It Yourself

### Requirements
- Python 3.10+
- `rich`, `prompt_toolkit`, `requests`
- *(Optional)* [Ollama](https://ollama.com/) with `llama3.2` or `gemma:2b`

### Run:
```bash
git clone https://github.com/your-username/the-last-process.git
cd the-last-process
pip install -r requirements.txt

# Run with Amber CRT mainframe theme
python run.py

# Or run with phosphor-green styling
python run.py --theme green

# Run with instant text mode (no typewriter delay)
python run.py --fast
```

---

## 🧪 Automated Testing

The project includes unit tests for all 9 core features, clue version mutations, trust/suspicion shifts, and safety boundaries:
```bash
python -m unittest discover tests
```
*Result: 17/17 tests passing!*

---

## 🎃 Conclusion

"Ghost in the Machine" is about finding humanity, mystery, and eerie life inside open-source artificial intelligence. **THE LAST PROCESS** demonstrates how you can pair open-weight models with a strict, safety-first state machine to create an unforgettable, narrative-driven horror experience in your own terminal.

Happy Hacktoberfest! 👻💻
