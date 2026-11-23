"""Where kcr reads and writes: XDG locations, overridable through the usual variables.

Snapshots live in state, which survives a reboot; the kitty session file kcr hands to kitty is
throwaway, so it lives in the runtime dir.
"""

from __future__ import annotations

import os
from pathlib import Path

from . import APP


def snapshot_dir() -> Path:
    state = os.environ.get("XDG_STATE_HOME") or str(Path.home() / ".local/state")
    return Path(state) / APP / "snapshots"


def session_file() -> Path:
    runtime = os.environ.get("XDG_RUNTIME_DIR") or f"/tmp/{APP}-{os.getuid()}"
    return Path(runtime) / APP / "restore.kitty-session"


def claude_config_dirs() -> list[Path]:
    dirs = [Path.home() / ".claude"]
    extra = os.environ.get("CLAUDE_CONFIG_DIR")
    if extra and Path(extra) not in dirs:
        dirs.append(Path(extra))
    return dirs
