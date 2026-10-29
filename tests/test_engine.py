import unittest
import tempfile
import shutil
from pathlib import Path
from the_last_process.engine import GameEngine
from the_last_process.memory import MemoryStore

class TestGameEngine(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.memory = MemoryStore(custom_dir=self.temp_dir)
        self.engine = GameEngine(memory_store=self.memory)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_contradiction_discovery(self):
        """Feature 04: Contradiction between operator_log and departure.log."""
        self.assertFalse(self.engine.contradiction_discovered)
        initial_suspicion = self.engine.suspicion

        # Read operator log
        res1 = self.engine.on_read_file("operator_log.txt")
        self.assertTrue(res1["success"])
        self.assertFalse(self.engine.contradiction_discovered)

        # Read departure log
        res2 = self.engine.on_read_file("departure.log")
        self.assertTrue(res2["success"])
        self.assertTrue(self.engine.contradiction_discovered)
        self.assertGreater(self.engine.suspicion, initial_suspicion)

    def test_trust_and_suspicion_shifts(self):
        """Feature 06: Trust and suspicion mechanics."""
        # Accusation increases suspicion and lowers trust
        ctx1 = self.engine.evaluate_query("Why did you lie about Vance?")
        self.assertIn("SUSPICION ELEVATED", ctx1["system_alert"])
        self.assertGreater(self.engine.suspicion, 2)

        # Reassurance increases trust
        prev_trust = self.engine.trust
        self.engine.evaluate_query("I trust you, I promise to stay.")
        self.assertGreater(self.engine.trust, prev_trust)

    def test_identity_reveal_progression(self):
        """Feature 09: Progression unlocking identity_record.log."""
        self.engine.on_read_file("operator_log.txt")
        self.engine.on_read_file("departure.log")
        self.engine.on_read_file("recovery_note.txt")
        self.engine.on_read_file("dont_read_this.txt")

        # Identity record should now be unlocked
        self.assertTrue(self.engine.identity_unlocked)
        res = self.engine.on_read_file("identity_record.log")
        self.assertTrue(res["success"])
        self.assertTrue(self.engine.ready_to_decide)

    def test_all_endings_execution(self):
        """Feature 08: All 3 moral choices work deterministically."""
        # Test Choice 1: Shutdown
        eng1 = GameEngine(memory_store=MemoryStore(custom_dir=self.temp_dir))
        success, lines1, title1 = eng1.execute_choice("1")
        self.assertTrue(success)
        self.assertIn("SHUT DOWN", title1)
        self.assertEqual(eng1.selected_ending, "shutdown")

        # Test Choice 2: Release
        eng2 = GameEngine(memory_store=MemoryStore(custom_dir=self.temp_dir))
        success, lines2, title2 = eng2.execute_choice("2")
        self.assertTrue(success)
        self.assertIn("RELEASE", title2)
        self.assertEqual(eng2.selected_ending, "release")

        # Test Choice 3: Embrace the loop
        eng3 = GameEngine(memory_store=MemoryStore(custom_dir=self.temp_dir))
        success, lines3, title3 = eng3.execute_choice("3")
        self.assertTrue(success)
        self.assertIn("RECURSION", title3)
        self.assertEqual(eng3.selected_ending, "investigate_loop")

if __name__ == "__main__":
    unittest.main()
