import unittest

from kcr import snapshots
from tests.fixtures import session


class ShouldWrite(unittest.TestCase):
    def test_never_an_empty_snapshot(self):
        self.assertFalse(snapshots.should_write([], [session("a")]))

    def test_the_first_snapshot(self):
        self.assertTrue(snapshots.should_write([session("a")], None))

    def test_same_set_in_another_order_is_not_rewritten(self):
        self.assertFalse(snapshots.should_write([session("a"), session("b")], [session("b"), session("a")]))

    def test_changed_set(self):
        self.assertTrue(snapshots.should_write([session("a")], [session("a"), session("b")]))


class DefaultIndex(unittest.TestCase):
    def test_newest_from_before_the_boot(self):
        self.assertEqual(snapshots.default_index([300, 200, 100], booted_at=250), 1)

    def test_newest_when_all_are_after_the_boot(self):
        self.assertEqual(snapshots.default_index([300, 200], booted_at=100), 0)


if __name__ == "__main__":
    unittest.main()
