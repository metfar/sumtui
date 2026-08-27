#!/bin/bash
set -u
phone=$(sumdialog --entry --title "Phone" --text "Phone:" --picture "(999) 999-9999" --width 14) || exit $?
printf 'Phone: %s\n' "$phone"
identifier=$(sumdialog --entry --title "Overflow" --text "ID (mask plus optional overflow):" --picture "NNNNNNNN" --width 12 --overflow) || exit $?
printf 'ID: %s\n' "$identifier"
