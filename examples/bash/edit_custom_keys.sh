#!/bin/bash
set -eu

TMP_CONFIG="$(mktemp -d)"
trap 'rm -rf "$TMP_CONFIG"' EXIT
mkdir -p "$TMP_CONFIG/sumtui"
cat > "$TMP_CONFIG/sumtui/edit.json" <<'JSON'
{
  "theme": "DOS",
  "keybindings": {
    "editor.copy": ["alt+c"],
    "editor.paste": ["alt+v"]
  }
}
JSON

XDG_CONFIG_HOME="$TMP_CONFIG" sumedit "${1:-README.md}"
