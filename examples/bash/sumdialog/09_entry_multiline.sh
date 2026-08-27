#!/bin/bash
set -u
notes=$(sumdialog --entry --title "Notes" --text "Enter notes:" --width 60 --height 8) || exit $?
printf '%s\n' "--- notes ---"
printf '%s\n' "$notes"
