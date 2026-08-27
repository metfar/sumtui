#!/bin/bash
set -u
name=$(sumdialog --entry --title "User" --text "Name:" --default "Ada") || exit $?
printf 'Name: %s\n' "$name"
