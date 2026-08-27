# sumdialog Bash examples

Every current `sumdialog` mode has a runnable Bash example in this directory.
Run them from the project root, for example:

```bash
bash examples/bash/sumdialog/01_info.sh
bash examples/bash/sumdialog/05_entry.sh
bash examples/bash/sumdialog/18_progress_percent.sh
```

Or use the dispatcher:

```bash
bash examples/bash/sumdialog_examples.sh list
bash examples/bash/sumdialog_examples.sh entry-picture
bash examples/bash/sumdialog_examples.sh progress-bytes
```

The dialog UI uses the controlling terminal. Returned values go to stdout, diagnostics go to stderr, and the shell exit status reports accept/cancel/timeout/error.

| Demo | What it covers |
| --- | --- |
| `01_info.sh` | `--info`, `--title`, `--text`, `--theme`, `--width`, `--height` |
| `02_warning.sh` | `--warning` |
| `03_error.sh` | `--error` |
| `04_question.sh` | `--question`, `--ok-label`, `--cancel-label`, exit status |
| `05_entry.sh` | `--entry`, command substitution, default value |
| `06_entry_secret.sh` | `--hidden`, `--mask` |
| `07_entry_picture.sh` | `--picture`, `--width`, `--overflow` |
| `08_entry_keys_timeout.sh` | `--keys`, `--case-sensitive`, `--default`, `--timeout` |
| `09_entry_multiline.sh` | multiline `--entry`, `--width`, `--height` |
| `10_file_selection.sh` | `--file-selection`, `--path` |
| `11_directory_selection.sh` | `--directory-selection`, `--path` |
| `12_list.sh` | `--list`, positional items, default selection, timeout |
| `13_radiolist.sh` | `--radiolist`, default selection |
| `14_checklist.sh` | `--checklist`, repeated `--selected`, `--separator` |
| `15_text_info.sh` | `--text-info`, `--filename`, stdin text |
| `16_markdown.sh` | `--markdown`, `--filename`, stdin Markdown |
| `17_custom_appearance.sh` | theme, dimensions, custom button labels |
| `18_progress_percent.sh` | `--progress`, percentage input, `--label`, `--width` |
| `19_progress_bytes.sh` | `--progress`, `--total`, byte pass-through |
| `20_exit_status.sh` | status codes and safe shell branching |

`--version` is demonstrated by the dispatcher `version` action.

<p align=center><b>- oOo -</b></p>
