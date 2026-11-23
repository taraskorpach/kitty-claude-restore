"""The one record kcr keeps per Claude Code session."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Session:
    session_id: str
    cwd: str
    name: str
    started_at: int  # epoch milliseconds, as Claude Code records it

    def label(self) -> str:
        return self.name or self.session_id[:8]

    def describe(self) -> str:
        cwd = self.cwd.replace(str(Path.home()), "~", 1)
        return f"  {self.label():<12} {cwd}  ({self.session_id})"
