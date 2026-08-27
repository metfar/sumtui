#!/bin/bash
set -u
secret=$(sumdialog --entry --hidden --title "Secret" --text "Password:") || exit $?
printf 'Hidden value length: %s\n' "${#secret}"
pin=$(sumdialog --entry --mask "***" --width 12 --title "PIN" --text "PIN:") || exit $?
printf 'Masked value length: %s\n' "${#pin}"
