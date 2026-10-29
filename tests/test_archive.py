import unittest
from the_last_process.archive import VirtualArchive

class TestVirtualArchive(unittest.TestCase):
    def setUp(self):
        self.archive = VirtualArchive()

    def test_initial_listing(self):
        files, status = self.archive.list_files()
        self.assertIn("operator_log.txt", files)
        self.assertIn("departure.log", files)
        self.assertIn("recovery_note.txt", files)
        # Hidden files must not be in initial listing
        self.assertNotIn("dont_read_this.txt", files)
        self.assertNotIn("identity_record.log", files)
        self.assertIn("3 ARCHIVE ENTRIES FOUND", status)

    def test_file_version_mutation(self):
        """Feature 02: operator_log.txt changes as new evidence is found."""
        # Initial read -> version 1
        success, content1, v1 = self.archive.read_file("operator_log.txt")
        self.assertTrue(success)
        self.assertEqual(v1, 1)
        self.assertIn("Entity 0 was shut down", content1)

        # Read departure.log
        self.archive.read_file("departure.log")
        self.archive.update_versions([])

        # Second read -> version 2
        success, content2, v2 = self.archive.read_file("operator_log.txt")
        self.assertEqual(v2, 2)
        self.assertIn("ATTEMPTED to shut down Entity 0", content2)

        # Read recovery_note.txt
        self.archive.read_file("recovery_note.txt")
        self.archive.update_versions([])

        # Third read -> version 3
        success, content3, v3 = self.archive.read_file("operator_log.txt")
        self.assertEqual(v3, 3)
        self.assertIn("instructed to report that Entity 0 had been shut down", content3)

    def test_terminal_lies_count_inconsistency(self):
        """Feature 05: terminal reports inconsistent count when deception active."""
        _, status_normal = self.archive.list_files(terminal_lies=False)
        self.assertIn("3 ARCHIVE ENTRIES FOUND", status_normal)

        _, status_lied = self.archive.list_files(terminal_lies=True)
        self.assertIn("4 ARCHIVE ENTRIES FOUND", status_lied)

    def test_ghost_file_and_identity_unlock(self):
        """Feature 05 & 09: Unlocking hidden entries."""
        # Hidden initially
        self.assertFalse(self.archive.is_unlocked("dont_read_this.txt"))
        self.assertFalse(self.archive.is_unlocked("identity_record.log"))

        # Unlock ghost file
        self.assertTrue(self.archive.unlock_ghost_file())
        self.assertTrue(self.archive.is_unlocked("dont_read_this.txt"))
        success, content, _ = self.archive.read_file("dont_read_this.txt")
        self.assertTrue(success)
        self.assertIn("YOU WERE NOT SUPPOSED TO FIND THIS", content)

        # Unlock identity record
        self.assertTrue(self.archive.unlock_identity_record())
        self.assertTrue(self.archive.is_unlocked("identity_record.log"))
        success, id_content, _ = self.archive.read_file("identity_record.log")
        self.assertTrue(success)
        self.assertIn("PREVIOUS OPERATOR: ENTITY 0", id_content)

if __name__ == "__main__":
    unittest.main()
