#!/usr/bin/env bash
# Removes the timer and the command. Snapshots stay in ~/.local/state/kcr.
set -euo pipefail

units="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"
systemctl --user disable --now kcr-snapshot.timer 2>/dev/null || true
rm -f "$units"/kcr-snapshot.{service,timer}
systemctl --user daemon-reload
rm -f "$HOME/.local/bin/kcr"
echo "Removed kcr and its timer."
