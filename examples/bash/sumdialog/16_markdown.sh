#!/bin/bash
set -u
# File source:
sumdialog --markdown --title "README" --filename "${1:-README.md}" --width 90 --height 26
# Stdin source:
printf '# Report\n\n- Bash\n- sumTUI\n- sumdialog\n' | sumdialog --markdown --title "Generated Markdown"
