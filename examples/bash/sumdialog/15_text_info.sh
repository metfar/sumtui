#!/bin/bash
set -u
# File source:
sumdialog --text-info --title "Changelog" --filename "${1:-CHANGELOG.md}" --width 90 --height 26
# Stdin source:
printf 'line one\nline two\nline three\n' | sumdialog --text-info --title "stdin text"
