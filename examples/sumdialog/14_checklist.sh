#!/bin/bash
set -u
features=$(sumdialog --checklist --title "Languages" --text "Select several:" --selected Python --selected Bash --separator '|' Python BASIC SQL Bash sumX) || exit $?
printf 'Selected: %s\n' "$features"
