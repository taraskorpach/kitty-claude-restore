"""kcr: reopen the Claude Code sessions you had open, side by side in one kitty window.

snapshot   registry -> snapshots        which sessions were open (a systemd timer, every minute)
restore    snapshots -> kitty_session   one kitty window, one pane per session: claude --resume <id>
"""

APP = "kcr"
