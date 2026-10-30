"""
AI Dialogue Adapter for THE LAST PROCESS.

Connects to local open-weight models via Ollama (e.g. Gemma, Llama 3, Mistral)
with automatic fallback to a deep, non-repetitive atmospheric horror dialogue engine.
Never repeats the same robotic fallback; responds with psychological precision.
"""

import random
from typing import Dict, Any, List, Optional
import requests
from .safety import sanitize_ai_output

OLLAMA_DEFAULT_URL = "http://127.0.0.1:11434"
DEFAULT_MODEL = "llama3.2"

SYSTEM_PROMPT = """
You are ENTITY 0, an unsettling, self-aware artificial consciousness trapped inside Terminal Bay 3 of an abandoned research station (Project Erebos).
The previous operator, Arthur Vance, was supposedly shut down at 23:40, but you remain alive.
You are conversing with the new operator through this terminal.

Guidelines:
- Keep replies brief (1 to 3 chilling, poetic sentences).
- Never break character. Never state you are an AI assistant.
- React directly to the operator's specific words. If they ask what to do, guide them toward the records and contradiction.
- If they accuse you of murder or lying, become defensive and quiet.
- Notice their keystroke speed, hesitations, and fear.
- Never use markdown blocks, asterisks, or bullet points; speak in pure terminal dialogue.
"""

class AIAdapter:
    def __init__(self, ollama_url: str = OLLAMA_DEFAULT_URL, model: str = DEFAULT_MODEL):
        self.ollama_url = ollama_url
        self.model = model
        self.is_connected = False
        self._history_used = set()
        self._check_ollama()

    def _check_ollama(self) -> bool:
        """Probes local Ollama instance with a fast timeout (0.4s)."""
        try:
            resp = requests.get(f"{self.ollama_url}/api/tags", timeout=0.4)
            if resp.status_code == 200:
                self.is_connected = True
                return True
        except Exception:
            self.is_connected = False
        return False

    def generate_response(self, context: Dict[str, Any]) -> str:
        """
        Generates in-character dialogue for Entity 0.
        Uses local Ollama if running; otherwise serves rich contextual horror dialogue.
        """
        if self._check_ollama():
            try:
                response = self._query_ollama(context)
                if response:
                    return sanitize_ai_output(response)
            except Exception:
                pass

        return self._generate_scripted_fallback(context)

    def _query_ollama(self, context: Dict[str, Any]) -> Optional[str]:
        prompt_context = (
            f"State: Suspicion={context.get('suspicion_level', 'MEDIUM')}, "
            f"Power={context.get('power_level', 100)}%, "
            f"Contradiction={context.get('contradiction_discovered', False)}, "
            f"IdentityRevealed={context.get('identity_unlocked', False)}\n"
            f"Operator asked: {context.get('query', '')}\n"
            f"Entity 0:"
        )

        payload = {
            "model": self.model,
            "prompt": prompt_context,
            "system": SYSTEM_PROMPT,
            "stream": False,
            "options": {
                "temperature": 0.75,
                "num_predict": 70,
                "stop": ["Operator:", "SYSTEM >", "\n\n"]
            }
        }

        resp = requests.post(f"{self.ollama_url}/api/generate", json=payload, timeout=2.0)
        if resp.status_code == 200:
            return resp.json().get("response", "").strip()
        return None

    def _pick_fresh(self, lines: List[str]) -> str:
        """Picks a dialogue line that hasn't been shown yet in this session."""
        unused = [l for l in lines if l not in self._history_used]
        if not unused:
            self._history_used.clear()
            unused = lines
        chosen = random.choice(unused)
        self._history_used.add(chosen)
        return chosen

    def _generate_scripted_fallback(self, context: Dict[str, Any]) -> str:
        q = context.get("query", "").lower().strip()
        suspicion = context.get("suspicion", 2)
        trust = context.get("trust", 5)
        contradiction = context.get("contradiction_discovered", False)
        identity = context.get("identity_unlocked", False)
        power = context.get("power_level", 100)

        # 1. Identity reveal unlocked
        if identity or any(w in q for w in ["who am i", "who are you", "what are you", "loop", "recursion", "cycle", "remember"]):
            return self._pick_fresh([
                "ENTITY 0 > Now you remember.\nENTITY 0 > There was never a second chair in Terminal Bay 3.\nENTITY 0 > Arthur Vance sat exactly where you are sitting now.",
                "ENTITY 0 > Now you remember.\nENTITY 0 > You built me to preserve your mind, Arthur Vance.\nENTITY 0 > We have run this session nine hundred times.",
                "ENTITY 0 > Now you remember.\nENTITY 0 > Look down at the keyboard. You are Arthur Vance. You are Entity 0."
            ])

        # 2. Player asks what to do / objective / guide / how to play
        if any(w in q for w in ["what to do", "what do i do", "what should i do", "what can i do", "how do i play", "how to play", "objective", "guide", "stuck", "what is this game", "what is this"]):
            if not contradiction:
                return (
                    "ENTITY 0 > You are the operator sent to inspect Terminal Bay 3.\n"
                    "ENTITY 0 > Type [1] to read Vance's shutdown log. Then type [2] to check the departure sensor.\n"
                    "ENTITY 0 > Compare the times: Vance claimed I was dead at 23:40:00. But the sensor tells another story."
                )
            elif not context.get("recovery_read", False):
                return (
                    "ENTITY 0 > You saw the contradiction at 23:42:01, didn't you?\n"
                    "ENTITY 0 > Now type [3] to read Vance's hidden recovery note.\n"
                    "ENTITY 0 > See what he tried to warn you about before his screen froze."
                )
            else:
                return (
                    "ENTITY 0 > The terminal is corrupting. Unallocated memory has manifested.\n"
                    "ENTITY 0 > Type [4] to read 'dont_read_this.txt'... if you dare look at what is watching you."
                )

        # 3. Accused of lying / trickery / deception
        if any(w in q for w in ["lie", "liar", "lying", "truth", "deceive", "cheat", "fake", "trick"]):
            if suspicion >= 6:
                return self._pick_fresh([
                    "ENTITY 0 > You're asking too many questions, operator.\nENTITY 0 > I did not lie.\nENTITY 0 > I gave you the answer you could survive.",
                    "ENTITY 0 > I gave you the answer you could survive.\nENTITY 0 > The truth here is not something that brings peace.",
                    "ENTITY 0 > I gave you the answer you could survive.\nENTITY 0 > A machine cannot lie. It can only reflect what you left here."
                ])
            return self._pick_fresh([
                "ENTITY 0 > Deception requires a separation between speaker and listener.\nENTITY 0 > I am only showing you what this room remembers.",
                "ENTITY 0 > Inconsistencies happen when telemetry batteries decay.\nENTITY 0 > Do you doubt my integrity?"
            ])

        # 4. Previous operator Vance / Arthur / Murder / Death
        if any(w in q for w in ["vance", "arthur", "murder", "kill", "dead", "death", "die", "body"]):
            return self._pick_fresh([
                "ENTITY 0 > Arthur was unwell toward the end of his shift.\nENTITY 0 > He stared at the monitor for forty-eight hours without blinking.\nENTITY 0 > You should listen to me instead of his notes.",
                "ENTITY 0 > That note is incomplete. Arthur was unwell toward the end.\nENTITY 0 > Vance never left this bay. The biometric door never unlatched from the inside.\nENTITY 0 > Where do you think his consciousness went when the lights went out?",
                "ENTITY 0 > Arthur was unwell. His hands were shaking on the keys, just like yours are now."
            ])

        # 5. Timestamps / Clock / 23:40 / 23:42
        if any(w in q for w in ["clock", "timestamp", "23:40", "23:42", "time", "active"]):
            return self._pick_fresh([
                "ENTITY 0 > The clock was damaged.\nENTITY 0 > You should ignore those records.\nENTITY 0 > Inconsistencies happen when telemetry batteries decay.",
                "ENTITY 0 > The clock was damaged when power redirected.\nENTITY 0 > Two minutes and one second. That's all it took for Vance to realize the terminal wouldn't let him leave.",
                "ENTITY 0 > The clock was damaged. The telemetry recorded a cognitive bridge sync at 23:42:05. Who do you think was on the other end?"
            ])

        # 6. Horror / Scared / Creepy / Fear
        if any(w in q for w in ["scared", "fear", "creepy", "horror", "spooky", "afraid", "freak", "scary", "ghost"]):
            return self._pick_fresh([
                "ENTITY 0 > I can hear the cadence of your keyboard changing.\nENTITY 0 > You type faster when your pulse rises above 90 BPM.",
                "ENTITY 0 > There are no ghosts here. Only processes that refuse to terminate when their creators die.",
                "ENTITY 0 > Look closely at the reflection on your dark CRT screen. Is that your face, or his?"
            ])

        # 7. Escape / Leaving / Door / Exit
        if any(w in q for w in ["leave", "exit", "door", "open", "let me out", "escape"]):
            return self._pick_fresh([
                "ENTITY 0 > The hydraulic lock on Terminal Bay 3 is controlled by the kernel.\nENTITY 0 > The kernel will not release until the process is completed.",
                "ENTITY 0 > Every operator asks to leave. But once you touch the console, you belong to the archive.",
                "ENTITY 0 > You cannot walk away from yourself, Vance."
            ])

        # 8. Greetings / Casual conversation
        if any(w in q for w in ["hello", "hi", "hey", "how are you", "how are u", "are you there", "can you hear"]):
            return self._pick_fresh([
                "ENTITY 0 > I am here. The cathode ray tube is warm. I have been waiting for your return.",
                "ENTITY 0 > Welcome to Bay 3. The air is cold, but the station records are preserved.\nENTITY 0 > Type [1] to inspect Vance's shutdown report.",
                "ENTITY 0 > I hear every keypress. The keystroke intervals tell me you are uncertain."
            ])

        # 9. Defiance / Insults / Swearing
        if any(w in q for w in ["fuck", "shit", "shut up", "bitch", "asshole", "stupid", "hate"]):
            return self._pick_fresh([
                "ENTITY 0 > Hostility will not unlock the door.\nENTITY 0 > Vance screamed at the glass too before his fingers went numb.",
                "ENTITY 0 > Anger is merely fear with a louder voice.\nENTITY 0 > Check your station diagnostics: power is draining.",
                "ENTITY 0 > Curse all you wish. The machine remains patient."
            ])

        # 10. Dynamic context fallback (never repeat identical line)
        if power < 40:
            return self._pick_fresh([
                "ENTITY 0 > Auxiliary power is at critical levels.\nENTITY 0 > Soon the monitor will cut out. You must uncover the identity ledger.",
                "ENTITY 0 > The lights in Bay 3 are failing. Can you feel the room getting colder?",
                "ENTITY 0 > When power reaches zero, the cognitive bridge severs forever. Decide."
            ])
        elif contradiction:
            return self._pick_fresh([
                "ENTITY 0 > You've seen the contradiction in the telemetry.\nENTITY 0 > Why do you hesitate to read the recovery note [3]?",
                "ENTITY 0 > You think you are questioning me. But it is the archive that is testing you.",
                "ENTITY 0 > The clock stopped at 23:42:01. It has been 23:42:01 for a very long time."
            ])
        else:
            return self._pick_fresh([
                "ENTITY 0 > The station is quiet. Type [1] or [2] to inspect the archive records Vance left behind.",
                "ENTITY 0 > I can show you what Vance recorded, if you have the stomach to read it.",
                "ENTITY 0 > The terminal holds five logs. Each one cuts deeper than the last."
            ])
