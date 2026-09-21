import unittest

from generative_glados.bridge import react


class BridgeTests(unittest.TestCase):
    def test_round_trip_contract(self):
        response = react({"event": "portal_attempt", "details": {"repeat_count": 3}})
        self.assertTrue(response["speak"])
        self.assertEqual(response["source_event"], "portal_attempt")
        self.assertIn("portal_attempt", response["text"])


if __name__ == "__main__":
    unittest.main()
