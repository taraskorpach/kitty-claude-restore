# kitty-claude-restore

`kcr` reopens the Claude Code sessions you had open before a reboot, each resumed to its exact
conversation, side by side in one [kitty](https://sw.kovidgoyal.net/kitty/) window. Linux.

```
$ kcr
restoring 4 session(s) from [0] 20261123-125546:
  app-61       ~/code/app/.claude/worktrees/ios  (91e30670-…)
  app-50       ~/code/app                        (acd253e4-…)
  …
```

```
┌──────┬──────┬──────┬──────┐
│      │      │      │      │
│  1   │  2   │  3   │  4   │   each pane: claude --resume <its session>, in its folder
│      │      │      │      │
└──────┴──────┴──────┴──────┘
```

## Why

`claude --continue` only knows the most recent session per folder, so several parallel sessions
in one repo cannot be told apart after a reboot; reopening them means `claude --resume`, picking
each conversation from a list, and splitting the window again.

## Install

Requirements: Linux with systemd, Python 3.9+, kitty, Claude Code. No Python packages, no change
to your kitty config or shell rc.

```sh
git clone https://github.com/taraskorpach/kitty-claude-restore
cd kitty-claude-restore
make install     # or ./install.sh
```

`make install` builds `~/.local/bin/kcr` (a single-file zipapp of `src/`), installs and starts the
snapshot timer, and takes a first snapshot. `make uninstall` removes both; snapshots stay.

## Use

After a reboot:

```sh
kcr                     # reopen what was open before the reboot, in a new kitty window
kcr --dry-run           # what would open, and the kitty session it would use
kcr list                # snapshots, newest first
kcr --snapshot 2        # an older one
kcr --layout grid       # another kitty layout (default: horizontal, one row)
```

`kcr` runs from any terminal.

## How it works

1. **Snapshot.** A systemd user timer runs `kcr snapshot` every minute. It reads Claude Code's
   registry of running sessions (`~/.claude/sessions/<pid>.json`) and keeps the interactive ones
   whose process is alive: the pid and its kernel start time must match, so a reused pid never
   counts. A snapshot is written only when the set changes and never empty, so the timer firing
   during a shutdown cannot bury the last good one. The last 30 are kept in
   `~/.local/state/kcr/snapshots/`.
2. **Choose.** `kcr` takes the newest snapshot from before this boot, so a session you started
   after the reboot cannot replace what was open when the machine went down. Sessions open again
   are skipped; a session whose folder is gone (a deleted git worktree) is listed with its
   `claude --resume` command instead.
3. **Open.** `kcr` writes a [kitty session file](https://sw.kovidgoyal.net/kitty/overview/#startup-sessions)
   (one tab, the layout, one `launch` per session with its folder) and runs
   `kitty --session <file> --detach`. Each pane starts your shell interactively, so PATH and
   aliases from your rc are there, runs `claude --resume <id>`, and stays a normal shell after
   you quit Claude.

### Code map

| Module | Responsibility |
|---|---|
| `src/kcr/registry.py` | the sessions open right now, from Claude Code's registry |
| `src/kcr/snapshots.py` | writing, rotating and choosing snapshots |
| `src/kcr/kitty_session.py` | the kitty session file and opening it |
| `src/kcr/cli.py` | commands and options |

## Limits

- What Claude was doing at the moment of the reboot (a half-written reply, a running command) is
  not resumed; the conversation comes back up to its last saved message.
- A session started less than a minute before the reboot may not be in the snapshot yet.

## Development

```sh
make test       # python3 -m unittest, no dependencies
python3 src     # run from the source tree
```

## License

MIT
