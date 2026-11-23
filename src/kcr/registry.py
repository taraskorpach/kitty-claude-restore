"""The sessions open right now, read from Claude Code's own registry.

Claude Code writes `<config>/sessions/<pid>.json` for every running session. A file can outlive
its process (a crash, a reboot) and pids get reused, so an entry counts only when a process with
that pid exists and started at the recorded moment (`procStart`, the kernel's start time).
"""

from __future__ import annotations

import json
from pathlib import Path

from .model import Session
from .paths import claude_config_dirs


def proc_start_ticks(pid: int) -> str | None:
    try:
        stat = Path(f"/proc/{pid}/stat").read_text()
    except OSError:
        return None
    return stat.rsplit(")", 1)[1].split()[19]  # field 22; the command name may contain spaces


def is_live(entry: dict) -> bool:
    pid = entry.get("pid")
    if not isinstance(pid, int):
        return False
    started = proc_start_ticks(pid)
    return started is not None and started == str(entry.get("procStart"))


def session_from_entry(entry: dict) -> Session | None:
    if entry.get("kind") != "interactive" or not entry.get("sessionId") or not entry.get("cwd"):
        return None
    return Session(
        session_id=entry["sessionId"],
        cwd=entry["cwd"],
        name=entry.get("name") or "",
        started_at=int(entry.get("startedAt") or 0),
    )


def live_sessions() -> list[Session]:
    found: dict[str, Session] = {}
    for config in claude_config_dirs():
        for file in (config / "sessions").glob("*.json"):
            try:
                entry = json.loads(file.read_text())
            except (OSError, ValueError):
                continue
            session = session_from_entry(entry)
            if session and is_live(entry):
                found[session.session_id] = session
    return sorted(found.values(), key=lambda s: s.started_at)
