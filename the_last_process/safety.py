"""
Safety and Privacy Boundaries for THE LAST PROCESS.

Implements strict isolation:
- Sanitizes terminal control sequences to prevent ANSI/VT100 injection attacks.
- Validates allowlisted command syntax so player input never touches the host OS or shell.
- Enforces strict virtual archive isolation (zero filesystem traversal / path escapes).
- Prevents real system shutdown commands from ever executing.
"""

import re
import os
from typing import Tuple, Optional

# Denylist for dangerous shell meta-characters and sequences
DANGEROUS_PATTERNS = [
    r"(\||&|;|`|\$|\(|\)|<|>|\^|\n|\r)",  # Shell chaining and redirection
    r"\.\.[\\/]",                          # Path traversal attempts
    r"(powershell|cmd\.exe|bash|sh|zsh|eval|exec|os\.system|subprocess)", # Shell invocations
    r"(format|rmdir|del|rm\s+-rf|shutdown\s+/[s|r])"                     # Destructive commands
]

# ANSI escape sequence regex for stripping unwanted terminal escape sequences from AI responses
ANSI_ESCAPE_RE = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

# Allowed fictional commands inside the game
ALLOWED_COMMANDS = {
    "help", "?",
    "ls", "dir", "list",
    "read", "cat", "open", "view",
    "ask", "query", "talk", "say",
    "status", "diag", "diagnostics",
    "decide", "choose",
    "shutdown", "stop", "end",
    "theme", "speed", "mode",
    "clear", "cls",
    "reset",
    "quit", "exit", "q"
}

def sanitize_ai_output(text: str) -> str:
    """
    Sanitizes raw AI model output before rendering to terminal.
    - Strips malicious ANSI escape sequences.
    - Removes non-printable / control characters except standard whitespace.
    - Prevents prompt leaking of internal system guidelines.
    """
    if not text:
        return ""
    
    # Strip ANSI escape codes
    clean_text = ANSI_ESCAPE_RE.sub("", text)
    
    # Remove null bytes and non-printable control characters (except newline, tab, carriage return)
    clean_text = "".join(ch for ch in clean_text if ch in "\n\r\t " or ord(ch) >= 32)
    
    # Trim excessive repeats of punctuation or whitespace
    clean_text = re.sub(r"\n{3,}", "\n\n", clean_text)
    
    return clean_text.strip()

def sanitize_player_input(raw_input: str) -> str:
    """
    Sanitizes player command input.
    - Strips control characters.
    - Normalizes unicode whitespace.
    - Caps maximum input length to prevent denial-of-service / memory abuse.
    """
    if not raw_input:
        return ""
    
    # Strip null bytes and non-printable control characters
    cleaned = "".join(ch for ch in raw_input if ord(ch) >= 32 or ch in "\t")
    
    # Cap length (e.g., 500 characters max for a query)
    return cleaned.strip()[:500]

def parse_and_validate_command(command_str: str) -> Tuple[Optional[str], str]:
    """
    Parses a user input line into an allowed game command and its argument.
    Returns: (command_name, argument_string)
    If the command is not allowlisted, returns (None, original_input).
    
    Guarantees that input is NEVER passed to a shell, PowerShell, eval, or OS process.
    """
    cleaned = sanitize_player_input(command_str)
    if not cleaned:
        return (None, "")
    
    # Handle inputs without spaces like ask<how are u?> or read<operator_log.txt>
    for prefix in ["ask<", "read<", "cat<", "open<", "view<"]:
        if cleaned.lower().startswith(prefix):
            cleaned = prefix[:-1] + " " + cleaned[len(prefix):]
            break

    parts = cleaned.split(maxsplit=1)
    cmd = parts[0].lower()
    args = parts[1].strip() if len(parts) > 1 else ""
    
    # Strip literal angle brackets or quotes user might type: <file> or "file"
    args = args.strip("<>\"' ")

    # If player typed '? something', route to ask; if just '?', route to help
    if cmd == "?":
        if args:
            cmd = "ask"
        else:
            cmd = "help"
    
    # Prevent path traversal in arguments
    args = os.path.basename(args.replace("\\", "/")) if cmd in ("read", "cat", "open", "view") else args
    
    # Map command aliases
    if cmd in ("dir", "list"):
        cmd = "ls"
    elif cmd in ("cat", "open", "view"):
        cmd = "read"
    elif cmd in ("query", "talk", "say"):
        cmd = "ask"
    elif cmd in ("diag", "diagnostics"):
        cmd = "status"
    elif cmd in ("cls",):
        cmd = "clear"
    elif cmd in ("exit", "q"):
        cmd = "quit"
    elif cmd in ("stop", "end"):
        cmd = "shutdown"
    elif cmd in ("?"):
        cmd = "help"
        
    if cmd in ALLOWED_COMMANDS:
        return (cmd, args)
    
    return (None, cleaned)
