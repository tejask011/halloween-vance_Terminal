import unittest
from the_last_process.ai_adapter import AIAdapter

class TestAIAdapter(unittest.TestCase):
    def setUp(self):
        # AI adapter initialized (will use fallbacks if Ollama is offline)
        self.adapter = AIAdapter()

    def test_fallback_identity_reveal(self):
        context = {
            "query": "Who are you?",
            "identity_unlocked": True,
            "suspicion": 10,
            "trust": 2
        }
        resp = self.adapter.generate_response(context)
        self.assertIn("Now you remember", resp)
        self.assertIn("Arthur Vance", resp)

    def test_fallback_contradiction_confronted(self):
        context = {
            "query": "Why does the timestamp say 23:42?",
            "contradiction_discovered": True,
            "suspicion": 5,
            "trust": 4
        }
        resp = self.adapter.generate_response(context)
        self.assertIn("clock was damaged", resp)

    def test_fallback_lying_accused(self):
        context = {
            "query": "You are lying to me",
            "suspicion": 8,
            "trust": 1
        }
        resp = self.adapter.generate_response(context)
        self.assertIn("I gave you the answer you could survive", resp)

    def test_fallback_vance_inquiry(self):
        context = {
            "query": "What did you do to Vance?",
            "suspicion": 4,
            "trust": 4
        }
        resp = self.adapter.generate_response(context)
        self.assertIn("Arthur was unwell", resp)

if __name__ == "__main__":
    unittest.main()
