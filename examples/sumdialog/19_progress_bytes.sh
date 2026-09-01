#!/bin/bash
set -u
src=$(mktemp)
dst=$(mktemp)
trap 'rm -f "$src" "$dst"' EXIT
# 1 MiB deterministic demo payload; sumdialog passes bytes through stdout.
dd if=/dev/zero of="$src" bs=1024 count=1024 status=none
cat "$src" | sumdialog --progress --total 1M --label "Copy demo" > "$dst"
cmp "$src" "$dst"
printf 'Byte pass-through verified: %s bytes\n' "$(wc -c < "$dst")"
