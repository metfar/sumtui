#!/bin/bash
set -u
set +e
answer=$(sumdialog --entry --title "Choice" --text "Continue?" --keys YN --case-sensitive --default N --timeout N,10)
status=$?
set -e
printf 'Answer=%s status=%s\n' "$answer" "$status"
# Status 3 means the timeout fired; the default value is still printed to stdout.
exit 0
