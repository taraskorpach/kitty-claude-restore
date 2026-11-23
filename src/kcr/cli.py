"""Command line: `kcr` restores; `snapshot` and `list` serve it."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import APP, kitty_session, snapshots
from .model import Session
from .paths import session_file
from .registry import live_sessions

SUBCOMMANDS = {"restore", "snapshot", "list"}


def with_default_command(argv: list[str]) -> list[str]:
    if argv and (argv[0] in SUBCOMMANDS or argv[0] in ("-h", "--help")):
        return argv
    return ["restore", *argv]


def to_restore(snapshot: list[Session], open_now: set[str]) -> tuple[list[Session], list[Session]]:
    """(sessions to open, sessions whose folder is gone); already-open sessions are skipped."""
    closed = [s for s in snapshot if s.session_id not in open_now]
    return [s for s in closed if Path(s.cwd).is_dir()], [s for s in closed if not Path(s.cwd).is_dir()]


def cmd_restore(args: argparse.Namespace) -> int:
    chosen = snapshots.select(args.snapshot)
    if chosen is None:
        print(f"no such snapshot; see `{APP} list`", file=sys.stderr)
        return 1
    index, path = chosen
    sessions, gone = to_restore(snapshots.read_sessions(path), {s.session_id for s in live_sessions()})
    for session in gone:
        print(f"skipped, folder is gone: {session.label()}  (claude --resume {session.session_id})")
    if not sessions:
        print("nothing to restore: every session in that snapshot is open or gone")
        return 0
    print(f"restoring {len(sessions)} session(s) from [{index}] {path.stem}:")
    print("\n".join(s.describe() for s in sessions))
    text = kitty_session.render(sessions, args.layout, kitty_session.user_shell())
    if args.dry_run:
        print("\n" + text, end="")
        return 0
    kitty_session.open_window(text, session_file())
    return 0


def cmd_snapshot(_: argparse.Namespace) -> int:
    path = snapshots.take()
    if path:
        print(f"saved {path}")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    found = snapshots.list_snapshots()
    if not found:
        print(f"no snapshots yet: run `{APP} snapshot` or install the timer")
        return 1
    for index, path in enumerate(found[: args.limit]):
        print(f"[{index}] {path.stem}")
        print("\n".join(s.describe() for s in snapshots.read_sessions(path)))
    return 0


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog=APP, description="Reopen the Claude Code sessions you had open, side by side in one kitty window. With no command, restores.")
    sub = root.add_subparsers(dest="command", required=True)

    restore = sub.add_parser("restore", help="reopen a snapshot's sessions (the default command)")
    restore.add_argument("--snapshot", type=int, default=None, help="index from `list` (default: the newest from before this boot)")
    restore.add_argument("--layout", default=kitty_session.DEFAULT_LAYOUT, help="kitty layout: horizontal (default, one row), grid, vertical, tall, fat")
    restore.add_argument("--dry-run", action="store_true", help="print the kitty session instead of opening it")
    restore.set_defaults(func=cmd_restore)

    sub.add_parser("snapshot", help="record the open sessions (the timer runs this)").set_defaults(func=cmd_snapshot)
    listing = sub.add_parser("list", help="saved snapshots, newest first")
    listing.add_argument("--limit", type=int, default=5)
    listing.set_defaults(func=cmd_list)
    return root


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(with_default_command(sys.argv[1:] if argv is None else argv))
    try:
        return args.func(args)
    except RuntimeError as error:
        print(f"{APP}: {error}", file=sys.stderr)
        return 1
