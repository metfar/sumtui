#!/bin/bash
set -euo pipefail
answer=$(suminput --dialog --keys YN --default N --timeout N,10 "Continue?") || status=$?
status=${status:-0}
printf 'answer=%s status=%s\n' "$answer" "$status"
