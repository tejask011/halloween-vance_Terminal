"""
Main entry point for THE LAST PROCESS.
"""

import argparse
import sys
from .cli import GameSession

def main():
    parser = argparse.ArgumentParser(
        description="THE LAST PROCESS - A safety-first, AI-powered terminal horror game."
    )
    parser.add_argument(
        "--theme",
        choices=["halloween", "amber", "green", "monochrome"],
        default="halloween",
        help="Terminal color theme (default: halloween)"
    )
    parser.add_argument(
        "--mute",
        action="store_true",
        help="Mute terminal audio effects"
    )
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Enable fast mode (disables teletype delay and suspense pauses)"
    )
    parser.add_argument(
        "--model",
        default="llama3.2",
        help="Ollama model to use for Entity 0 (default: llama3.2)"
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Wipe persistent memory before booting"
    )

    args = parser.parse_args()

    session = GameSession(theme=args.theme, fast_mode=args.fast, model=args.model, mute=args.mute)
    if args.reset:
        session.handle_reset()

    session.run()

if __name__ == "__main__":
    main()
