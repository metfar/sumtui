#!/bin/bash
set -u
theme=$(sumdialog --radiolist --title "Theme" --text "Choose one:" --default ZX ZX DOS XBASE Light) || exit $?
printf 'Theme: %s\n' "$theme"
