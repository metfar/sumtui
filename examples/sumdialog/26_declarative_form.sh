#!/bin/bash
set -u

base=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
form="$base/project_form.sdlg"

# The same form may be executed directly because it has:
#   #!/usr/bin/env sumdialog
form_data="$("$form")";
status=$?;

# Equivalent stdin form:
# form_data="$(cat "$form" | sumdialog)";

if [ "$status" -ne 0 ]; then
    printf 'Form cancelled.\n';
    exit "$status";
fi;

eval "$form_data";

printf 'PROJECT: %s\n' "$project";
printf 'LANGUAGE: %s\n' "$language";
printf 'PROFILE: %s\n' "$profile";
printf 'TARGET: %s\n' "$target";
printf 'CREATE TESTS: %s\n' "$tests";
printf 'SOURCE: %s\n' "$source";
printf 'DIRECTORY: %s\n' "$directory";
printf 'NOTES: %s\n' "$notes";
