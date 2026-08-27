#!/bin/bash
set -u
theme=$(sumdialog --radiolist --title "Theme" --text "Choose one:" --default "Ralesk's MC" "Ralesk's MC" DOS XBASE Light) || exit $?
printf 'Theme: %s\n' "$theme"
