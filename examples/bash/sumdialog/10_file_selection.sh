#!/bin/bash
set -u
file=$(sumdialog --file-selection --title "Open file" --path "${1:-.}" --width 80 --height 24) || exit $?
printf 'Selected file: %s\n' "$file"
