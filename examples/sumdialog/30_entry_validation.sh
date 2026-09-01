#!/bin/bash
set -u

answer=$(sumdialog --entry \
    --title "Validation" \
    --text "Continue? [S/N]" \
    --default N \
    --max-length 1 \
    --confirm \
    --valid-values S,N \
    --validation-error "Use S or N") || exit $?
printf 'Answer: %s\n' "$answer"

answer=$(sumdialog --entry \
    --title "PICTURE @M" \
    --text "Continue? [S/N]" \
    --default N \
    --picture "@M S,N") || exit $?
printf 'PICTURE answer: %s\n' "$answer"
