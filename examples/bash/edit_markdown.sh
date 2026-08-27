#!/bin/bash
# Open Markdown source with automatic semantic highlighting.
# Pass another Markdown file as $1 if desired.
exec sumedit "${1:-README.md}"
