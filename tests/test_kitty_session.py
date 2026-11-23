import shlex
import unittest

from kcr import kitty_session
from tests.fixtures import session


class Render(unittest.TestCase):
    def test_one_tab_one_row_one_pane_per_session(self):
        text = kitty_session.render([session("a"), session("b")], shell="/usr/bin/zsh")
        lines = text.splitlines()
        self.assertEqual(lines[:2], ["new_tab claude", "layout horizontal"])
        self.assertEqual(len([line for line in lines if line.startswith("launch ")]), 2)

    def test_pane_resumes_in_its_folder_and_stays_a_shell(self):
        line = kitty_session.render([session("a")], shell="/usr/bin/zsh").splitlines()[2]
        self.assertEqual(shlex.split(line), [
            "launch", "--cwd=/work/a", "--title=a",
            "/usr/bin/zsh", "-ic", "claude --resume a; exec /usr/bin/zsh",
        ])

    def test_folders_with_spaces_and_quotes_survive(self):
        line = kitty_session.render([session("a", cwd="/w/My Work/it's")]).splitlines()[2]
        self.assertIn("--cwd=/w/My Work/it's", shlex.split(line))

    def test_layout_can_be_chosen(self):
        self.assertIn("layout grid", kitty_session.render([session("a")], layout="grid"))


if __name__ == "__main__":
    unittest.main()
