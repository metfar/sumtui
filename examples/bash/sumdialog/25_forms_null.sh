#!/bin/bash
set -u

first_name='';
last_name='';

while IFS= read -r -d '' name && IFS= read -r -d '' value; do
    printf -v "$name" '%s' "$value";
done < <(
    sumdialog --forms \
        --title "NUL-delimited result" \
        --add-entry first_name "First name" \
        --add-entry last_name "Last name" \
        --output null
);

printf 'NAME: %s %s\n' "$first_name" "$last_name";
