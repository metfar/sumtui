#!/bin/bash
set -euo pipefail
file=${1:-README.md}
exec sumedit "$file"
