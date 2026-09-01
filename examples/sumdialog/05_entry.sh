#!/bin/bash
set -u
name=$(sumdialog --entry --title "User" --text "Name:" --default "Ada") || exit $?
printf 'Name: %s\n' "$name"

last=$(sumdialog --entry --title "Bounded field" --text "Type several letters; the last one remains:" --width 20 --max-length 1 --confirm) || exit $?
printf 'Last character: %s\n' "$last"
