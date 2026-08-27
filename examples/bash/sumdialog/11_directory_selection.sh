#!/bin/bash
set -u
dir=$(sumdialog --directory-selection --title "Choose directory" --path "${1:-.}" --width 80 --height 24) || exit $?
printf 'Selected directory: %s\n' "$dir"
