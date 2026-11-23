#!/usr/bin/env bash
# Builds `kcr` (a zipapp of src/) into ~/.local/bin and starts the snapshot timer.
set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
bin="$HOME/.local/bin"
units="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"

mkdir -p "$bin" "$units"
python3 -m zipapp "$here/src" --python "/usr/bin/env python3" --output "$bin/kcr"
install -m 644 "$here"/systemd/kcr-snapshot.{service,timer} "$units/"
systemctl --user daemon-reload
systemctl --user enable --now kcr-snapshot.timer
"$bin/kcr" snapshot || true

command -v kitty >/dev/null || echo "Note: kitty is not on PATH; kcr opens its sessions in kitty."
