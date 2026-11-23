import os
import unittest

from kcr import registry
from kcr.model import Session


class SessionFromEntry(unittest.TestCase):
    def test_interactive_entry(self):
        entry = {"kind": "interactive", "sessionId": "x", "cwd": "/w", "name": "n", "startedAt": 5}
        self.assertEqual(registry.session_from_entry(entry), Session("x", "/w", "n", 5))

    def test_non_interactive_entry_is_skipped(self):
        self.assertIsNone(registry.session_from_entry({"kind": "sdk", "sessionId": "x", "cwd": "/w"}))


class IsLive(unittest.TestCase):
    def test_running_process_with_matching_start(self):
        pid = os.getpid()
        self.assertTrue(registry.is_live({"pid": pid, "procStart": registry.proc_start_ticks(pid)}))

    def test_reused_pid_does_not_count(self):
        self.assertFalse(registry.is_live({"pid": os.getpid(), "procStart": "0"}))

    def test_missing_process(self):
        self.assertFalse(registry.is_live({"pid": 2**22 + 12345, "procStart": "1"}))


if __name__ == "__main__":
    unittest.main()
