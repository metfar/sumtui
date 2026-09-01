# sumdialog Bash examples

Every current `sumdialog` mode has a runnable Bash example in this directory, including multi-field `--forms`, declarative `.sdlg` forms, retro button menus, and the interactive `--demo` launcher.
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
| `01_info.sh` | `--info`, `--title`, `--text`, `--theme`, dialog `--width`/`--height`, and multi-row `--button-width`/`--button-height` |
| `02_warning.sh` | `--warning` |
| `03_error.sh` | `--error` |
| `04_question.sh` | `--question`, `--ok-label`, `--cancel-label`, exit status |
| `05_entry.sh` | `--entry`, command substitution, default value, logical `--max-length`, and default `--confirm` behavior |
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
| `21_forms_personal_data.sh` | personal-data form; first/last name, born date default `1985-02-28`, height, OK/Cancel, shell output |
| `22_forms_components.sh` | entry/password/textarea/checkbox/combo/radio/list/file/directory fields |
| `23_forms_json.sh` | form result as JSON |
| `24_forms_shell_safety.sh` | apostrophes and shell-looking text preserved as data |
| `25_forms_null.sh` | NUL-delimited name/value transport without `eval` |
| `26_declarative_form.sh` | executes `project_form.sdlg` directly through `#!/usr/bin/env sumdialog`; also shows the `cat form.sdlg | sumdialog` equivalent |
| `27_retro_menu.sh` | executes `retro_menu.sdlg` and branches on the selected retro button value |
| `28_demo.sh` | launches `sumdialog --demo` with the Ralesk's MC theme |
| `29_retro_menu_separators.sh` | retro menu using blank spacing and a configurable full-width separator rule |
| `30_entry_validation.sh` | complete-value validation with `--valid-values`, custom validation error text, and the compact `PICTURE "@M ..."` choice mask |
| `project_form.sdlg` | declarative form containing entry/password/textarea/checkbox/combo/radio/list/file/directory fields |
| `retro_menu.sdlg` | classic vertical button menu with Entrar/Listar/Buscar/Reporte/Salir |
| `retro_menu_spacing.sdlg` | declarative `separator.blank`, `separator.blank=N`, and `separator.line="CHAR"` spacing/rules |

`--entry --max-length N` sets logical capacity independently from visual `--width`. `--confirm` is ON by default; `--no-confirm` auto-submits at the limit only after validation succeeds. `--valid-values A,B,...` plus `--validation-error TEXT` validate complete values, and `PICTURE "@M A,B,..."` provides a compact choice mask. Forms expose the same policy through `--form-valid-values`, `--form-error` and `.sdlg` `field:NAME.valid_values` / `field:NAME.validation_error`.

`--forms --output shell` emits validated Bash variable names and values protected with POSIX single-quote escaping. For example, `This is John's house` is reconstructed exactly after `eval`, while text such as `$(command)` remains data. `--output null` is available when a script wants to avoid `eval` entirely.

Declarative files may be piped or executed directly:

```bash
cat examples/bash/sumdialog/project_form.sdlg | sumdialog
./examples/bash/sumdialog/project_form.sdlg
```

Validate or inspect one without opening the UI:

```bash
sumdialog --check examples/bash/sumdialog/project_form.sdlg
sumdialog --dump examples/bash/sumdialog/project_form.sdlg
```

Retro menu separators may be empty spacing or full-width rules. For example:

```ini
separator.blank
separator.blank=2
separator.line
separator.line="="
```

The CLI equivalents are `--menu-blank [ROWS]`, `--menu-separator`, and `--menu-line [CHAR]`.

The retro menu returns only the selected action value on stdout, so Bash can use a normal `case` statement.

`--version` is demonstrated by the dispatcher `version` action.

<p align=center><b>- oOo -<b></p>
