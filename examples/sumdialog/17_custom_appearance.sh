#!/bin/bash
set -u
sumdialog --question --title "Styled question" --text "This demonstrates theme, size and labels." --theme "Ralesk's MC" --width 62 --height 11 --ok-label "Do it" --cancel-label "Cancel"
status=$?
printf 'status=%s\n' "$status"
exit 0
