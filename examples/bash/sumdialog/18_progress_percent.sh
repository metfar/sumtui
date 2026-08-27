#!/bin/bash
set -u
{
    printf '0\n'; sleep 0.15
    printf '20\n'; sleep 0.15
    printf '50\n'; sleep 0.15
    printf '80\n'; sleep 0.15
    printf '100\n'
} | sumdialog --progress --percent-input --label "Percentage demo" --width 52
