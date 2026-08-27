#!/bin/bash
set -u

base=$(CDPATH= cd -- "$(dirname -- "$0")/sumdialog" && pwd)

usage() {
    cat <<'TXT'
Usage: bash examples/bash/sumdialog_examples.sh NAME [args...]

Names:
  list, version
  info, warning, error, question
  entry, entry-secret, entry-picture, entry-keys-timeout, entry-multiline
  file, directory, listbox, radio, checklist
  text, markdown, appearance
  progress-percent, progress-bytes, exit-status
  forms-personal, forms-components, forms-json, forms-shell-safety, forms-null
  declarative-form, retro-menu, demo
TXT
}

name=${1:-list}
if [ "$#" -gt 0 ]; then shift; fi
case "$name" in
    list) usage ;;
    version) sumdialog --version ;;
    info) exec bash "$base/01_info.sh" "$@" ;;
    warning) exec bash "$base/02_warning.sh" "$@" ;;
    error) exec bash "$base/03_error.sh" "$@" ;;
    question) exec bash "$base/04_question.sh" "$@" ;;
    entry) exec bash "$base/05_entry.sh" "$@" ;;
    entry-secret) exec bash "$base/06_entry_secret.sh" "$@" ;;
    entry-picture) exec bash "$base/07_entry_picture.sh" "$@" ;;
    entry-keys-timeout) exec bash "$base/08_entry_keys_timeout.sh" "$@" ;;
    entry-multiline) exec bash "$base/09_entry_multiline.sh" "$@" ;;
    file) exec bash "$base/10_file_selection.sh" "$@" ;;
    directory) exec bash "$base/11_directory_selection.sh" "$@" ;;
    listbox) exec bash "$base/12_list.sh" "$@" ;;
    radio) exec bash "$base/13_radiolist.sh" "$@" ;;
    checklist) exec bash "$base/14_checklist.sh" "$@" ;;
    text) exec bash "$base/15_text_info.sh" "$@" ;;
    markdown) exec bash "$base/16_markdown.sh" "$@" ;;
    appearance) exec bash "$base/17_custom_appearance.sh" "$@" ;;
    progress-percent) exec bash "$base/18_progress_percent.sh" "$@" ;;
    progress-bytes) exec bash "$base/19_progress_bytes.sh" "$@" ;;
    exit-status) exec bash "$base/20_exit_status.sh" "$@" ;;
    forms-personal) exec bash "$base/21_forms_personal_data.sh" "$@" ;;
    forms-components) exec bash "$base/22_forms_components.sh" "$@" ;;
    forms-json) exec bash "$base/23_forms_json.sh" "$@" ;;
    forms-shell-safety) exec bash "$base/24_forms_shell_safety.sh" "$@" ;;
    forms-null) exec bash "$base/25_forms_null.sh" "$@" ;;
    declarative-form) exec bash "$base/26_declarative_form.sh" "$@" ;;
    retro-menu) exec bash "$base/27_retro_menu.sh" "$@" ;;
    demo) exec bash "$base/28_demo.sh" "$@" ;;
    *) usage >&2; exit 2 ;;
esac
