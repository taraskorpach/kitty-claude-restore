"""Opening the sessions in kitty through a session file (`kitty --session`).

A session file describes one tab: its layout and one `launch` per pane, each with its own folder
and command. kitty builds the whole window from it, so kcr needs no remote control, no change to
your kitty config and nothing in your shell rc. Each pane runs your shell interactively (so PATH
and aliases from your rc are there), resumes the session, and stays a normal shell after you quit
Claude.
"""

from __future__ import annotations

import os
import shlex
import shutil
import subprocess
from pathlib import Path

from .model import Session

DEFAULT_LAYOUT = "horizontal"  # every pane side by side, equal widths


def pane_command(session: Session, shell: str) -> list[str]:
    resume = f"claude --resume {shlex.quote(session.session_id)}; exec {shlex.quote(shell)}"
    return [shell, "-ic", resume]


def render(sessions: list[Session], layout: str = DEFAULT_LAYOUT, shell: str = "/bin/sh") -> str:
    lines = ["new_tab claude", f"layout {layout}"]
    for session in sessions:
        options = [f"--cwd={session.cwd}", f"--title={session.label()}"]
        lines.append("launch " + shlex.join([*options, *pane_command(session, shell)]))
    return "\n".join(lines) + "\n"


def user_shell() -> str:
    return os.environ.get("SHELL") or "/bin/sh"


def open_window(session_text: str, path: Path) -> None:
    kitty = shutil.which("kitty")
    if kitty is None:
        raise RuntimeError("kitty is not on PATH")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(session_text)
    subprocess.run([kitty, "--session", str(path), "--detach"], check=True)
