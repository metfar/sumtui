#!/bin/bash
set -u

form_data="$(
    sumdialog --forms \
        --title "Personal information" \
        --text "Please enter your personal data" \
        --add-entry first_name "First name" \
        --add-entry last_name "Last name" \
        --add-entry born_date "Born date" \
        --add-entry height "Height" \
        --form-default born_date=1985-02-28 \
        --required first_name \
        --required last_name \
        --ok-label "OK" \
        --cancel-label "Cancel" \
        --output shell
)";
status=$?;

if [ "$status" -ne 0 ]; then
    printf 'Form cancelled.\n';
    exit "$status";
fi;

# sumdialog emits validated variable names and POSIX-safe single-quoted values.
# After eval, the variables contain the exact natural text entered by the user.
eval "$form_data";

full_name="${first_name} ${last_name}";

printf 'NAME: %s\n' "$full_name";
printf 'FIRST NAME: %s\n' "$first_name";
printf 'LAST NAME: %s\n' "$last_name";
printf 'BORN DATE: %s\n' "$born_date";
printf 'HEIGHT: %s\n' "$height";
