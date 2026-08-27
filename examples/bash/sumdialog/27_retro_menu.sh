#!/bin/bash
set -u

base=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
menu="$base/retro_menu.sdlg"

selection="$("$menu")";
status=$?;
if [ "$status" -ne 0 ]; then
    printf 'Menu cancelled.\n';
    exit "$status";
fi;

case "$selection" in
    enter)  printf 'ACTION: enter data\n' ;;
    list)   printf 'ACTION: list data\n' ;;
    search) printf 'ACTION: search data\n' ;;
    report) printf 'ACTION: report\n' ;;
    exit)   printf 'ACTION: exit\n' ;;
    *)      printf 'Unknown action: %s\n' "$selection" >&2; exit 2 ;;
esac;
