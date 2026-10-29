import unittest
import tempfile
import shutil
from pathlib import Path
from the_last_process.safety import (
    sanitize_ai_output,
    sanitize_player_input,
    parse_and_validate_command
)
from the_last_process.memory import MemoryStore

class TestSafetyAndBoundaries(unittest.TestCase):
    def test_command_allowlisting(self):
        # Valid commands
        cmd, arg = parse_and_validate_command("ls")
        self.assertEqual(cmd, "ls")

        cmd, arg = parse_and_validate_command("read operator_log.txt")
        self.assertEqual(cmd, "read")
        self.assertEqual(arg, "operator_log.txt")

        # Aliases
        cmd, arg = parse_and_validate_command("cat departure.log")
        self.assertEqual(cmd, "read")
        self.assertEqual(arg, "departure.log")

        cmd, arg = parse_and_validate_command("dir")
        self.assertEqual(cmd, "ls")

        cmd, arg = parse_and_validate_command("exit")
        self.assertEqual(cmd, "quit")

    def test_path_traversal_prevention(self):
        # Path traversal characters in read argument are stripped to basename
        cmd, arg = parse_and_validate_command("read ../../secret.txt")
        self.assertEqual(cmd, "read")
        self.assertEqual(arg, "secret.txt")

        cmd, arg = parse_and_validate_command("read C:\\Windows\\System32\\cmd.exe")
        self.assertEqual(cmd, "read")
        self.assertEqual(arg, "cmd.exe")

    def test_denial_of_host_execution(self):
        # Shell injection strings must NOT be recognized as valid allowed commands
        cmd, _ = parse_and_validate_command("powershell.exe -Command Get-Process")
        self.assertIsNone(cmd)

        cmd, _ = parse_and_validate_command("rm -rf /")
        self.assertIsNone(cmd)

        cmd, _ = parse_and_validate_command("shutdown /s /t 0")
        self.assertEqual(cmd, "shutdown")
        # In the game, shutdown is mapped only to game narrative ending, never OS execution

    def test_ai_output_sanitization(self):
        # Strips ANSI escape sequences
        dirty_ansi = "\x1b[31;1mDangerous colored text\x1b[0m\x1b[2J"
        clean = sanitize_ai_output(dirty_ansi)
        self.assertEqual(clean, "Dangerous colored text")

        # Strips null bytes and control chars
        dirty_null = "Entity 0\x00\x07 speaks to you."
        clean_null = sanitize_ai_output(dirty_null)
        self.assertEqual(clean_null, "Entity 0 speaks to you.")

    def test_memory_isolation(self):
        temp_dir = Path(tempfile.mkdtemp())
        try:
            mem = MemoryStore(custom_dir=temp_dir)
            mem.increment_session()
            mem.record_clue("operator_log.txt")
            mem.record_choice("1", "shutdown")
            
            loaded = mem.load()
            self.assertEqual(loaded["session_count"], 2)
            self.assertEqual(loaded["last_choice"], "1")
            self.assertEqual(loaded["last_ending"], "shutdown")
            self.assertIn("operator_log.txt", loaded["discovered_clues"])

            # Reset save
            mem.reset_save()
            fresh = mem.load()
            self.assertEqual(fresh["session_count"], 1)
            self.assertEqual(fresh["discovered_clues"], [])
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    unittest.main()
