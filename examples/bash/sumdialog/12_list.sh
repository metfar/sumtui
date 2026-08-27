#!/bin/bash
set -u
language=$(sumdialog --list --title "Language" --text "Select a language:" --default Python --timeout 30 Python BASIC C R sumX) || exit $?
printf 'Language: %s\n' "$language"
