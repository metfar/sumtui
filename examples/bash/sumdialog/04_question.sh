#!/bin/bash
set -u
if sumdialog --question --title "Confirm" --text "Continue with the operation?" --ok-label "Continue" --cancel-label "Stop"; then
    printf '%s\n' "User accepted"
else
    status=$?
    printf 'User declined/cancelled; status=%s\n' "$status"
fi
