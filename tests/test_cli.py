import tempfile
import unittest

from kcr.cli import to_restore, with_default_command
from tests.fixtures import session


class DefaultCommand(unittest.TestCase):
    def test_no_arguments_restores(self):
        self.assertEqual(with_default_command([]), ["restore"])

    def test_restore_options_alone(self):
        self.assertEqual(with_default_command(["--dry-run"]), ["restore", "--dry-run"])

    def test_named_command(self):
        self.assertEqual(with_default_command(["list"]), ["list"])


class ToRestore(unittest.TestCase):
    def test_open_sessions_are_skipped_and_missing_folders_reported(self):
        with tempfile.TemporaryDirectory() as here:
            kept, gone = to_restore(
                [session("open", here), session("closed", here), session("lost", "/no/such/folder")],
                open_now={"open"},
            )
        self.assertEqual([s.session_id for s in kept], ["closed"])
        self.assertEqual([s.session_id for s in gone], ["lost"])


if __name__ == "__main__":
    unittest.main()
