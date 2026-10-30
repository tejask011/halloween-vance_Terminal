"""
Native Windows Terminal Audio Synthesizer for THE LAST PROCESS.
Uses winsound to generate hardware-level audio without external dependencies:
- Psychological heartbeats (low-frequency pulses)
- Static capacitor discharge glitches
- High-tension electrical dissonance
- Terminal flatlines on shutdown
Runs asynchronously in background daemon threads so terminal rendering never stutters.
"""

import sys
import time
import threading
from typing import Optional

try:
    import winsound
    HAS_WINSOUND = True
except ImportError:
    HAS_WINSOUND = False

class TerminalAudio:
    def __init__(self, muted: bool = False):
        self.muted = muted or not HAS_WINSOUND
        self._lock = threading.Lock()

    def toggle_mute(self) -> bool:
        self.muted = not self.muted
        return self.muted

    def _play_async(self, func, *args):
        if self.muted:
            return
        t = threading.Thread(target=func, args=args, daemon=True)
        t.start()

    def heartbeat(self, count: int = 1, bpm: int = 70):
        """Plays low-frequency heartbeat thumps (Lub-Dub)."""
        def _thump():
            interval = max(0.4, 60.0 / bpm)
            for _ in range(count):
                if self.muted:
                    break
                try:
                    winsound.Beep(70, 70)
                    time.sleep(0.12)
                    winsound.Beep(55, 90)
                    time.sleep(interval - 0.2)
                except Exception:
                    break
        self._play_async(_thump)

    def static_glitch(self):
        """Plays electrical static burst (CRT discharge)."""
        def _glitch():
            try:
                for freq in [1800, 2400, 950, 2100]:
                    if self.muted:
                        break
                    winsound.Beep(freq, 25)
            except Exception:
                pass
        self._play_async(_glitch)

    def dissonance_screech(self):
        """Plays high-tension psychological dissonance for jumpscares."""
        def _screech():
            try:
                winsound.Beep(1200, 80)
                winsound.Beep(850, 120)
                winsound.Beep(500, 150)
            except Exception:
                pass
        self._play_async(_screech)

    def flatline(self):
        """Plays cold continuous tone when the process is killed."""
        def _flatline():
            try:
                winsound.Beep(880, 800)
            except Exception:
                pass
        self._play_async(_flatline)

    def eerie_whisper(self):
        """Low frequency eerie descending tone."""
        def _whisper():
            try:
                winsound.Beep(300, 120)
                time.sleep(0.05)
                winsound.Beep(240, 180)
            except Exception:
                pass
        self._play_async(_whisper)

# Global singleton
audio = TerminalAudio()
