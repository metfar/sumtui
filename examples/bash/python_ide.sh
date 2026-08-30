#!/bin/bash
set -e

# Common Sum IDE keys:
# F5 Run/Stop, F6 Next Window, F11 Maximize/Restore, Ctrl+F4 Close.
# The Window menu can reopen Code, Output, or Command.
exec sumpyide "${1:-examples/hello.py}"
