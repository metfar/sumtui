#!/bin/bash
set -u

sumdialog --forms \
    --title "JSON result" \
    --add-entry name "Name" \
    --add-checkbox active "Active" \
    --form-default active=true \
    --output json
