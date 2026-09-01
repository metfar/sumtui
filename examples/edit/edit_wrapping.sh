#!/bin/bash
set -euo pipefail

file="${1:-README.md}"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
mkdir -p "$tmp/sumtui"
cat > "$tmp/sumtui/edit.json" <<'JSON'
{
  "line_wrapping": 78,
  "line_breaking": 0
}
JSON
XDG_CONFIG_HOME="$tmp" sumedit "$file"
