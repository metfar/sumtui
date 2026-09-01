#!/bin/bash
set -u
cat <<'TXT'
sumdialog status codes:
  0 accepted / Yes / OK
  1 cancel / No / Escape
  2 usage error
  3 timeout
  4 terminal/runtime error
TXT
set +e
sumdialog --question --text "Accept or cancel to inspect the status."
status=$?
set -e
case "$status" in
    0) printf '%s\n' "accepted" ;;
    1) printf '%s\n' "cancelled/no" ;;
    3) printf '%s\n' "timed out" ;;
    4) printf '%s\n' "terminal/runtime error" ;;
    *) printf 'other status: %s\n' "$status" ;;
esac
