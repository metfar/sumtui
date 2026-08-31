#!/usr/bin/env bash
# Open several source files in one sumIDE workspace for side-by-side study.
exec sumide "$(dirname "$0")/../hello.py" "$(dirname "$0")/../hello.R" "$(dirname "$0")/../hello.sh" "$(dirname "$0")/../hello.c" "$(dirname "$0")/../hello.cpp"
