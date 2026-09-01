#!/bin/bash
set -euo pipefail
file=${1:?usage: eol_convert.sh FILE}
sumeol --check "$file"
sumeol --to lf "$file"
sumeol --check "$file"
