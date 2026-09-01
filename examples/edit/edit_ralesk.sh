#!/bin/bash
set -e
if [ "$#" -eq 0 ]; then
    set -- README.md
fi
exec sumedit --theme "Ralesk's MC" "$@"
