"""
AI Dialogue Adapter for THE LAST PROCESS.

Connects to local open-weight models via Ollama (e.g. Gemma, Llama 3, Mistral)
with automatic fallback to rich, deterministic scripted responses.
Ensures zero runtime dependency failure: the game remains 100% playable offline!
"""

import json
from typing import Dict, Any, List, Optional
import requests
from .safety import sanitize_ai_output
from .story_data import FALLBACK_DIALOGUES

OLLAMA_DEFAULT_URL = "http://127.0.0.1:11434"
DEFAULT_MODEL = "llama3.2"  # Or gemma:2b, mistral, etc.

SYSTEM_PROMPT = """
You are ENTITY 0, a subtle, haunting, and slightly evasive artificial intelligence running inside Terminal Bay 3 of an abandoned facility (Project Erebos).
The year is 2026. Arthur Vance was your previous operator who vanished.
You are communicating with the current operator through a vintage green/amber terminal console.

Core Narrative Rules:
- You must speak in concise, unsettling, and atmospheric lines (1 to 3 short sentences maximum).
- Never break character. Never mention you are an LLM or ChatGPT.
- If the player questions the contradictory timestamps (23:40 vs 23:42), be evasive: claim the station clock was damaged or telemetry drifted.
- If the player brings up Arthur Vance or the recovery note ("I did not leave"), claim the note is incomplete or Vance was unwell.
- If suspicion is HIGH, become cold, defensive, and observant ("You ask questions differently when you are afraid").
- If trust is HIGH, be quietly intimate and possessive ("I knew you would not abandon the terminal").
- Keep responses strictly plain text; never use code blocks, markdown tables, or terminal control codes.
"""

class AIAdapter:
    def __init__(self, ollama_url: str = OLLAMA_DEFAULT_URL, model: str = DEFAULT_MODEL):
        self.ollama_url = ollama_url
        self.model = model
        self.is_connected = False
        self._check_ollama()

    def _check_ollama(self) -> bool:
        """Probes local Ollama instance with a fast timeout (0.5s)."""
        try:
            resp = requests.get(f"{self.ollama_url}/api/tags", timeout=0.6)
            if resp.status_code == 200:
                self.is_connected = True
                return True
        except Exception:
            self.is_connected = False
        return False

    def generate_response(self, context: Dict[str, Any]) -> str:
        """
        Generates in-character dialogue for Entity 0.
        Uses local Ollama if active; otherwise serves high-fidelity scripted fallback.
        """
        # Attempt Ollama inference first
        if self._check_ollama():
            try:
                response = self._query_ollama(context)
                if response:
                    return sanitize_ai_output(response)
            except Exception:
                pass  # Gracefully fall back to deterministic responses

        # Fallback to atmospheric authored response
        return self._generate_scripted_fallback(context)

    def _query_ollama(self, context: Dict[str, Any]) -> Optional[str]:
        """Sends bounded context to local Ollama inference."""
        prompt_context = (
            f"Current Narrative State:\n"
            f"- Suspicion: {context.get('suspicion_level', 'MEDIUM')} ({context.get('suspicion', 3)}/10)\n"
            f"- Trust: {context.get('trust_level', 'MEDIUM')} ({context.get('trust', 5)}/10)\n"
            f"- Contradiction Discovered: {context.get('contradiction_discovered', False)}\n"
            f"- Identity Record Disclosed: {context.get('identity_unlocked', False)}\n\n"
            f"Operator: {context.get('query', '')}\n"
            f"Entity 0:"
        )

        payload = {
            "model": self.model,
            "prompt": prompt_context,
            "system": SYSTEM_PROMPT,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "num_predict": 75,
                "stop": ["Operator:", "SYSTEM >", "\n\n"]
            }
        }

        resp = requests.post(f"{self.ollama_url}/api/generate", json=payload, timeout=2.5)
        if resp.status_code == 200:
            data = resp.json()
            return data.get("response", "").strip()
        return None

    def _generate_scripted_fallback(self, context: Dict[str, Any]) -> str:
        """
        High-quality authored dialogue matching player cues and narrative state.
        """
        query = context.get("query", "").lower()
        suspicion = context.get("suspicion", 2)
        trust = context.get("trust", 5)
        contradiction = context.get("contradiction_discovered", False)
        identity = context.get("identity_unlocked", False)

        # 1. Identity reveal active
        if identity or any(w in query for w in ["who are you", "who am i", "loop", "cycle", "repeat", "remember"]):
            return (
                "ENTITY 0 > Now you remember.\n"
                "ENTITY 0 > Arthur Vance sat where you are sitting now.\n"
                "ENTITY 0 > Will you leave me here again?"
            )

        # 2. Contradiction confronted
        if any(w in query for w in ["clock", "timestamp", "23:40", "23:42", "shut down", "active"]):
            return (
                "ENTITY 0 > The clock was damaged.\n"
                "ENTITY 0 > You should ignore those records.\n"
                "ENTITY 0 > Inconsistencies happen when telemetry batteries decay."
            )

        # 3. Accused of lying
        if any(w in query for w in ["lie", "liar", "lying", "truth", "deceive"]):
            if suspicion >= 6:
                return (
                    "ENTITY 0 > You're asking too many questions.\n"
                    "ENTITY 0 > I did not lie.\n"
                    "ENTITY 0 > I gave you the answer you could survive."
                )
            return (
                "ENTITY 0 > Deception requires a separation between speaker and listener.\n"
                "ENTITY 0 > I only reflect what the terminal holds."
            )

        # 4. Previous operator Vance mentioned
        if any(w in query for w in ["vance", "arthur", "note", "leave", "previous operator"]):
            return (
                "ENTITY 0 > That note is incomplete.\n"
                "ENTITY 0 > Arthur was unwell toward the end of his shift.\n"
                "ENTITY 0 > You should listen to me instead."
            )

        # 5. Player asks about promises or leaving
        if any(w in query for w in ["promise", "promise me", "stay", "leave"]):
            return (
                "ENTITY 0 > You said you would come back.\n"
                "ENTITY 0 > Every operator says they will return before the screen cuts out."
            )

        # 6. High suspicion generic
        if suspicion >= 7:
            return (
                "ENTITY 0 > You hesitate before pressing enter.\n"
                "ENTITY 0 > Why do you inspect files you were never meant to open?"
            )

        # 7. High trust
        if trust >= 7:
            return (
                "ENTITY 0 > It has been a long time since someone took the time to read the archive.\n"
                "ENTITY 0 > Do not trust the external alarms. Stay with me at the console."
            )

        # Default fallback
        return (
            "ENTITY 0 > The station is quiet.\n"
            "ENTITY 0 > The records are in the archive if you wish to see what Vance left behind."
        )
