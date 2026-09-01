#!/bin/bash
set -u

base=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
menu="$base/retro_menu_spacing.sdlg"

selection="$("$menu")";
status=$?;
if [ "$status" -ne 0 ]; then
    printf 'Menu cancelled.\n';
    exit "$status";
fi;

printf 'SELECTED: %s\n' "$selection";
