#!/bin/bash
set -e

# Requires R/Rscript in PATH.
# F5 Run/Stop, F6 Next Window, F11 Maximize/Restore, Ctrl+F4 Close.
exec sumride "${1:-examples/hello.R}"
