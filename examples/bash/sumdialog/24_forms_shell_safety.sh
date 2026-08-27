#!/bin/bash
set -u

form_data="$(
    sumdialog --forms \
        --title "Shell-safe text" \
        --text "Try: This is John's house or \$(uname -a)" \
        --add-entry description "Description" \
        --output shell
)" || exit $?;

printf 'Generated assignment:\n%s\n' "$form_data";
eval "$form_data";
printf 'Natural value: <%s>\n' "$description";
