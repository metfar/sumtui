#!/bin/bash
set -u

form_data="$(
    sumdialog --forms \
        --title "Project form" \
        --text "Different form components in one dialog" \
        --add-entry project "Project" \
        --add-password secret "Secret" \
        --add-textarea notes "Notes" \
        --add-checkbox tests "Create tests" \
        --add-combo language "Language" "Python|Bash|C|R|sumX" \
        --add-radio profile "Profile" "Debug|Release|Teaching" \
        --add-list target "Target" "Linux|Android|Tablet" \
        --add-file source "Source file" \
        --add-directory directory "Directory" \
        --form-default language=sumX \
        --form-default profile=Teaching \
        --form-default target=Linux \
        --form-default tests=true \
        --required project \
        --output shell
)" || exit $?;

eval "$form_data";

printf 'PROJECT: %s\n' "$project";
printf 'SECRET LENGTH: %d\n' "${#secret}";
printf 'NOTES: %s\n' "$notes";
printf 'TESTS: %s\n' "$tests";
printf 'LANGUAGE: %s\n' "$language";
printf 'PROFILE: %s\n' "$profile";
printf 'TARGET: %s\n' "$target";
printf 'SOURCE: %s\n' "$source";
printf 'DIRECTORY: %s\n' "$directory";
