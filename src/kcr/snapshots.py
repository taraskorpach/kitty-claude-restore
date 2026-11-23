"""Snapshots: which sessions were open, over time.

Written only when the set of sessions changes, and never empty: during a shutdown the timer can
fire after Claude Code is gone, and an empty snapshot would bury the one worth restoring.
The default for a restore is the newest snapshot from before this boot, so a session started
after the reboot cannot replace what was open when the machine went down.
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict
from pathlib import Path

from .model import Session
from .paths import snapshot_dir
from .registry import live_sessions

KEEP = 30


def list_snapshots() -> list[Path]:
    return sorted(snapshot_dir().glob("*.json"), reverse=True)


def read_sessions(path: Path) -> list[Session]:
    return [Session(**s) for s in json.loads(path.read_text())["sessions"]]


def taken_at(path: Path) -> int:
    return int(json.loads(path.read_text()).get("taken_at") or 0)


def should_write(current: list[Session], latest: list[Session] | None) -> bool:
    if not current:
        return False
    if latest is None:
        return True
    return {s.session_id for s in current} != {s.session_id for s in latest}


def take() -> Path | None:
    current = live_sessions()
    existing = list_snapshots()
    if not should_write(current, read_sessions(existing[0]) if existing else None):
        return None
    snapshot_dir().mkdir(parents=True, exist_ok=True)
    path = snapshot_dir() / f"{time.strftime('%Y%m%d-%H%M%S')}.json"
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps({"taken_at": int(time.time()), "sessions": [asdict(s) for s in current]}, indent=2))
    tmp.replace(path)
    for old in list_snapshots()[KEEP:]:
        old.unlink(missing_ok=True)
    return path


def boot_time() -> int:
    for line in Path("/proc/stat").read_text().splitlines():
        if line.startswith("btime "):
            return int(line.split()[1])
    return 0


def default_index(times_newest_first: list[int], booted_at: int) -> int:
    for index, taken in enumerate(times_newest_first):
        if taken < booted_at:
            return index
    return 0


def select(index: int | None) -> tuple[int, Path] | None:
    snapshots = list_snapshots()
    if index is None and snapshots:
        index = default_index([taken_at(p) for p in snapshots], boot_time())
    if index is None or not 0 <= index < len(snapshots):
        return None
    return index, snapshots[index]
