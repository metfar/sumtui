# Changelog

## 0.5.16

- Added optional POSIX SGR mouse reporting to the core input backend and public `MouseEvent` dispatch. Applications opt in with `Application(..., mouse=True)` and gracefully keep keyboard operation when mouse reporting is unavailable.
- `sumedit` now supports left-click caret placement, click-drag text selection, mouse-wheel scrolling, and click/drag operation of its vertical and horizontal scrollbars. Wrapped editor rows remain mapped back to logical document offsets.
- Added mouse interaction across reusable controls used by `sumdialog`: buttons, text inputs, checkboxes, radio buttons, choices, lists/tables, scrollbars and modal dialogs. Form textareas now display a synchronized vertical scrollbar.
- List widgets can show an explicit selected-row marker; `sumdialog` list fields use it so the selected target remains visible even when another control owns focus.
- Fixed nested menu composition so each popup is overlaid independently. A taller submenu no longer creates a black rectangle below its shorter parent menu; the covered editor/background text is preserved wherever no popup actually exists.
- Added flexible retro menu separators: blank rows (`separator.blank`, optional height) and full-width rules (`separator.line`, optional character), with CLI counterparts `--menu-blank` and `--menu-line`; existing `separator` / `--menu-separator` remains the full-width line form.
- Added Bash/declarative separator examples and regression tests for SGR mouse decoding, editor mouse selection/routing, scrollbar mouse control, visible list selection, popup transparency and declarative separator parsing.

## 0.5.15

- Added declarative `.sdlg` input for `sumdialog`. A form may be piped (`cat form.sdlg | sumdialog`), passed as a filename (`sumdialog form.sdlg`), or executed directly with `#!/usr/bin/env sumdialog`; all paths build the same `FormFieldSpec` objects used by CLI `--forms`.
- Added `[form]` declarative syntax for entry/password/textarea/checkbox/combo/radio/list/file/directory fields, field defaults/required/width/height properties, standard form appearance/output settings, and literal non-shell evaluation of `$()`, backticks, variables and operators.
- Added `sumdialog --check FILE` for syntax/semantic validation and `sumdialog --dump FILE` for normalized JSON inspection of declarative definitions.
- Added reusable retro vertical button menus through public `MenuItemSpec` / `choose_menu()` plus CLI `--menu`, repeatable `--menu-button VALUE LABEL`, and ordered `--menu-separator`; the selected action value is returned on stdout for direct Bash `case` dispatch.
- Added declarative `[menu]` files with ordered `button:VALUE="Label"` entries and `separator` rows. The bundled example recreates a classic `MENU` with Entrar datos, Listar datos, Buscar datos, Reporte, and Salir.
- Added `sumdialog --demo`, an interactive retro launcher that executes examples of messages, question, entry, forms, list/radio/checklist, text/Markdown, animated progress, file/directory selection, and the retro button menu.
- Added Bash/declarative examples `26_declarative_form.sh`, `project_form.sdlg`, `27_retro_menu.sh`, `retro_menu.sdlg`, and `28_demo.sh`, and expanded regression coverage for the parser, menu ordering/output, direct declarative execution, and demo dispatch.

## 0.5.14

- Added `sumdialog --forms`, a reusable multi-field dialog built from the existing sumTUI controls. Initial field types are entry, password, textarea, checkbox, combo, radio, list, file selector, and directory selector.
- Added repeatable per-field defaults (`--form-default NAME=VALUE`) and required-field validation (`--required NAME`), plus custom OK/Cancel labels, theme, width/height, and timeout integration.
- Added structured form outputs for Bash and other consumers: `shell`, `values`, `lines`, `json`, and NUL-delimited `null`. Shell output validates variable identifiers and always uses POSIX single-quote escaping, preserving apostrophes exactly without allowing shell-looking values such as `$()` to become commands.
- Added public `FormFieldSpec` and `read_form()` APIs so Python and sumX/runtime clients can build the same forms without launching the CLI frontend.
- Added the canonical Bash personal-data example with `first_name`, `last_name`, `born_date` defaulting to `1985-02-28`, `height`, and OK/Cancel, plus examples covering all current form components, JSON output, shell-safety behavior, and NUL-delimited transport.
- Added regression tests for form parsing/defaults, safe apostrophe-preserving shell serialization, JSON booleans, variable-name validation, and Bash example syntax.

## 0.5.13

- Added a complete runnable Bash example suite for every current `sumdialog` mode: info, warning, error, question, entry, file/directory selection, list, radiolist, checklist, text-info, Markdown, and progress.
- Added focused Bash examples for entry masks/secrets, PICTURE, key filtering/default/timeout, multiline input, custom labels/sizing/themes, initial paths, checklist separators/preselection, percentage progress, and byte-pass-through progress.
- Reworked `examples/bash/sumdialog_examples.sh` into a small dispatcher so any demo can be launched by name, with `list` showing all available examples.
- Added `examples/bash/sumdialog/README.md` as an executable-oriented catalog and documented shell result/status conventions.
- Added regression checks that every documented `sumdialog` Bash script passes `bash -n`, and updated README references.

## 0.5.12

- Added `sumdialog`, a Zenity-style console dialog frontend built from existing sumTUI widgets. Initial modes are `--info`, `--warning`, `--error`, `--question`, `--entry`, `--file-selection`, `--directory-selection`, `--list`, `--radiolist`, `--checklist`, `--text-info`, `--markdown`, and `--progress`.
- Dialog UI uses the controlling terminal while stdout is reserved for returned values, preserving clean Bash command substitution and pipeline behavior. Exit statuses are shared with `suminput`: 0 accepted/Yes, 1 cancelled/No/Escape, 2 usage, 3 timeout, and 4 terminal/runtime error.
- `sumdialog --entry` reuses the existing `InputSpec` / `read_input` engine, including hidden/masked input, KEYS, PICTURE, WIDTH/HEIGHT, defaults and timeouts; `suminput` remains the compact compatibility frontend rather than becoming a separate implementation.
- `sumdialog --progress` delegates to the existing `sumprogress` engine, so percentage-input and pv-like byte pass-through behavior stay centralized.
- Added public Python dialog helpers (`DialogResult`, `show_message`, `ask_question`, `read_entry`, `choose_file`, `choose_list`, `choose_radio`, `choose_checklist`, `show_text`).
- Added Python/Bash examples, README documentation, console entry point, and regression tests for CLI dispatch, returned stdout values, question status, checklist separators, and progress delegation.

## 0.5.11

- Added `sumtheme`, a reusable interactive theme editor for sumTUI. It previews UI and syntax roles, lists built-in/user themes, keeps built-ins read-only, clones them into editable user themes, edits semantic Rich style roles, saves themes, reloads them, and deletes user themes.
- Added persistent user-theme discovery under `$XDG_CONFIG_HOME/sumtui/themes` or `~/.config/sumtui/themes`; user themes are available automatically to `sumedit`, sumX, and other applications using `make_theme()` / `THEMES`.
- Added public theme serialization APIs (`theme_to_dict`, `theme_from_dict`, `save_user_theme`, `load_theme_file`, `refresh_user_themes`) so applications can carry an effective theme without depending on a local theme file.
- `sumedit -> Options -> Theme` now includes discovered user themes as well as the built-in palettes.
- `InputSpec` can carry an explicit theme for modal input dialogs, allowing generated/runtime applications to keep their own visual identity.
- Added `sumtheme` as a console script plus Python/Bash examples and regression tests for user-theme round-tripping and the theme editor role registry.

## 0.5.10

- Fixed shifted vertical/page selection on a broader range of real terminals. POSIX input now reads the active terminfo capabilities (`kri`, `kind`, `kPRV`, `kNXT`, shifted Home/End/Left/Right) and feeds those sequences into the decoder, while retaining xterm and rxvt/urxvt fallback encodings.
- Added explicit rxvt/urxvt shifted cursor-key fallbacks (`CSI a/b/c/d`) plus shifted Home/End variants; existing xterm `CSI 1;2...` and shifted PageUp/PageDown sequences remain supported.
- `TextEditor` selection semantics are unchanged: Shift+Up/Down extends by visual/logical row and Shift+PageUp/PageDown extends by one page while preserving the original anchor. The fix is in the terminal-to-KeyEvent path.
- Added the `editor_gutter` semantic theme role. Ralesk's MC now reproduces its original Geany `margin_line_number=#114;#393`: dark-blue line numbers on a green gutter.
- Updated README/help and regression tests for terminal-specific shifted-key decoding and Ralesk's MC gutter styling.

## 0.5.9

- Added reliable terminal decoding for modified Home/End sequences, including xterm-style `Ctrl+Home`, `Ctrl+End`, `Shift+Home/End`, and legacy tilde variants. `TextEditor` already treated Ctrl+Home/End as document-edge navigation; the actual terminal input path now delivers those modifiers correctly.
- Confirmed and regression-tested selection extension with `Shift+Up`, `Shift+Down`, `Shift+PageUp`, and `Shift+PageDown`, including page-sized movement while keeping the original selection anchor.
- Added **Ralesk's MC** as a built-in sumTUI theme, adapted from Henrik Pauli's GPLv2+ Geany `mc.conf` colourscheme. Semantic roles preserve the familiar MC-like dark-blue background, yellow keywords/operators, green strings, brown comments, cyan numbers, white types, and blue selection.
- `sumedit` now uses Ralesk's MC as the default theme for a fresh configuration; existing saved theme preferences still win. The theme remains selectable alongside DOS, RAR, Dark, Light, and the other existing palettes.
- Updated editor help and README documentation for document-edge navigation, vertical/page selection, and the Ralesk's MC theme.

## 0.5.8

- Added soft line wrapping to `TextArea` / `TextEditor` as a non-mutating presentation layer. `line_wrapping=-1` follows the current visible editor width, `0` disables wrapping, and positive values provide fixed maximum visual widths.
- `sumedit` now defaults to automatic wrapping (`-1`) and exposes `Options -> Line wrapping` presets for Auto, Off, 78, 80, 100, 120, and Custom. The 78-column preset documents the legacy 80-column window convention (80 columns minus one border cell on each side).
- Wrapped continuation rows use `↪` in the line-number gutter, vertical scrolling tracks visual rows, and horizontal scrolling is disabled while wrapping is active. The underlying text, encoding, EOL model, selection offsets, and modified state are unchanged by soft wrapping.
- Added separate opt-in hard line breaking (`line_breaking`, default `0`/Off) with 78/80/100/120/Custom presets. Hard breaks entered while typing modify the document and remain part of the normal undo history.
- Wrapping/breaking settings are shown in the status bar and persisted by `Options -> Save configuration`.
- Added `examples/demo_editor_wrapping.py` and `examples/bash/edit_wrapping.sh`, plus regression tests for visual wrapping, the 78-column preset, persistence, hard-breaking behavior, and undo.

## 0.5.7

- Added semantic syntax highlighting directly to editable `TextArea` / `TextEditor` buffers. Highlighting is a presentation layer only: it never changes the underlying text, selection, encoding, or EOL model.
- `sumedit` enables syntax highlighting by default, auto-detects the language from filename/extension (plus selected exact names/shebangs), shows the detected language in the status bar, and adds `View -> Syntax highlighting` plus a manual `View -> Syntax` override menu. Syntax settings persist in editor configuration.
- Added stable cross-language semantic colour roles for keywords/commands, variables, functions/builtins, types, strings, numbers, comments, operators, constants, markup/headings, labels, and errors so classroom examples keep the same visual vocabulary across languages/themes.
- Markdown is now a first-class editable syntax mode, including headings, emphasis, links, inline HTML markup, and language-aware fenced code blocks. Fences can delegate to Python, Bash, SQL, BASIC, sumX/xBase, and other supported lexers while preserving the same semantic colours.
- Added broad editor modes for sumX/xBase, Python, shell, C/C++, R, Ruby, BASIC, Java, PHP, SQL, HTML, JavaScript, VBScript, CSS, JSON, YAML, TOML, INI/config, XML, and logs. BASIC extends Pygments QBasic highlighting with the requested Spectrum/extended vocabulary while retaining QBasic structured constructs.
- Added `examples/demo_editor_syntax.py` and `examples/bash/edit_markdown.sh`. The lightweight editor remains source-oriented; rendered Markdown/sumDOC preview is explicitly deferred to a possible future advanced editor.
- Corrected the canonical README closing marker to `<p align=center><b>- oOo -</b></p>`.
- Added regression tests for Markdown autodetection, fenced-code/inline-HTML semantic roles, Extended BASIC vocabulary, syntax preference persistence, and non-mutating editor highlighting.

## 0.5.6

- Added reusable `KeyBindingManager` / `KeyBindingAction` support with named actions, multiple shortcuts per action, context-aware conflict detection, default restoration, human-readable shortcut formatting, and JSON-friendly override persistence.
- `sumedit` now routes editor/file/search/menu/help actions through named key bindings instead of hard-coding their command shortcuts inside the editor widget.
- Added `Options -> Keyboard shortcuts...` with Change, Add, Remove, and Defaults actions. New shortcuts are captured from the real terminal key event; conflicting shortcuts are detected and can be reassigned explicitly.
- Menu shortcut labels and the bottom function bar are rebuilt from the active bindings, so the UI continues to document the user's customized keyboard.
- `Options -> Save configuration` now persists only shortcut overrides alongside theme/tab/visibility settings and reloads them on the next start.
- `TextArea`/`TextEditor` gained `command_shortcuts=False` for host applications that want to own Copy/Cut/Paste/Undo/Redo bindings while retaining normal cursor/word-navigation behavior.
- Modal applications using `capture_control_keys=True` no longer reinstall `Ctrl+C` as the application-stop binding while a dialog is open; captured control keys remain available to modal widgets.
- Added regression tests for key normalization/display, conflict detection, shortcut persistence, live dispatch, menu-label refresh, and the keyboard-shortcuts dialog.

## 0.5.5

- Added a full `Search` menu to `sumedit`: `Find...` (`Ctrl+F`), `Find Next` (`F3`), `Find Previous` (`Shift+F3`), `Search & Replace...` (`Ctrl+H`), and `Go to Line...` (`Ctrl+G`).
- Find/replace uses modal sumTUI dialogs and supports literal or regular-expression matching, optional case sensitivity, whole-word matching, wrap-around, Replace, and Replace All. Search matches become normal editor selections so the same selection/clipboard model remains in use.
- Added public `TextArea` helpers for selecting/replacing offset ranges and going to a line, so search and future language/editor clients do not need to mutate internal cursor state directly.
- Added `Application(capture_control_keys=True)` and matching POSIX backend support. `sumedit` uses it to disable terminal `ISIG` and XON/XOFF while active, allowing `Ctrl+C`, `Ctrl+Z`, `Ctrl+S`, and related control bytes to reach the editor instead of being intercepted by the terminal driver. The original termios state is restored exactly on every normal/error exit.
- `sumedit` now uses `Ctrl+O` for Open while F3 is reserved for Find Next.
- Added regression coverage for search navigation, replacement/Replace All undo, modal search dialogs, and POSIX terminal signal/flow-control restoration. Added Python and Bash examples for the control-key/editor path.

## 0.5.4

- Fixed `sumedit -> Help -> About...` and F1 Help modal rendering when dialogs use a shadow. `ModalOverlay` now resolves theme style strings to Rich `Style` objects before attaching them to shadow segments, fixing the reported `'str' object has no attribute 'render'` crash.
- Added regression coverage that opens About through the actual Help menu and flushes the rendered modal through a Rich Console, which reproduces the original failure path.

## 0.5.3

- `sumedit` F1 help now opens a real modal dialog instead of writing a transient status-line hint; Help also contains `About...`.
- Checked/radio `MenuItem` entries can be toggled with Space while the menu stays open, so View visibility flags can be changed naturally from the keyboard.
- `sumedit` Options now uses nested `Tab > 2/4/8` and `Theme > ...` menus and can save editor configuration under the XDG config directory (`~/.config/sumtui/edit.json` by default).
- Saved editor configuration is loaded on startup and currently preserves theme, tab width, and whitespace/control-visibility options; `--theme` remains an explicit per-run override.
- Hidden-character rendering now differentiates spaces, tabs, line endings, and control codes with separate theme roles. Tabs use `⇥`; LF uses `↵`, CRLF uses `⏎`, and classic CR uses `↩`; C0/DEL controls keep Unicode control-picture glyphs such as `␀` and `␡`.
- Added regression coverage for modal help, nested options, config round-tripping, hidden-character glyphs, and Space-toggle menu behavior.

## 0.5.2

- Added reusable `MenuDesktop`, which keeps `MenuBar` at one row and composites dropdowns over the client surface instead of letting editor/viewer panels clip them.
- Corrected `sumedit` keyboard convention: F9 opens/closes the menu and F10 exits.
- `sumedit` keeps File/Edit/View/Options/Help visible at the top while dropdown menus overlay the editing viewport.
- Added a runnable Python `examples/demo_menu_desktop.py` example and regression coverage for dropdown-over-client rendering.

## 0.5.1

- Added explicit `top`/`left` positioning to `Dialog` while preserving centered dialogs by default.
- Added optional DOS-style dialog shadows, `panel` metadata, and palette-backed `color_scheme` support for language/toolkit clients such as sumX `DEFINE WINDOW`.
- Added prompt-less `CommandWindow` rendering for reusable xBase-style coordinate windows and embedded screen editors.
- Extended `easy.dialog()` with the same position/shadow/panel/color-scheme options.
- Added runnable Python and Bash examples for positioned dialogs, `suminput`, and `sumeol`.
- Kept README examples and the project closing `- oOo -` mark up to date.


## 0.5.0

- Promoted the reusable editor, clipboard, EOL/encoding, modal-input and small CLI-tool infrastructure from the 0.4 alpha series to the 0.5 milestone.
- Keeps `sumedit`, `sumeol`, and `suminput` as lightweight reusable tools built from the same sumTUI components.
- No intentional API break from 0.4.0a17; this version marks the first consolidated 0.5 baseline for sumX 0.1.1.

## 0.4.0a17

- Added `suminput`, a controlling-terminal input tool that keeps stdout reserved for the returned value, so Bash command substitution works cleanly.
- `suminput` supports hidden input, arbitrary visual masks (including multi-character masks per typed character), DOS CHOICE-style `--keys`, case sensitivity, defaults, timeouts, shell-safe `--variable` output, centered dialogs, and GET-like `--width`, `--height`, and character `--picture` masks.
- Added reusable `InputSpec`, `InputResult`, and `InputMask` primitives.
- Extended `TextInput` with hidden/custom echo masks, character filters, display transforms/cursor mapping, and clear-on-first-edit behavior.
- `TextArea` can opt to leave Tab to application focus traversal, enabling multiline dialog inputs without changing source-editor Tab insertion.
- Added application idle callbacks for countdowns and other lightweight timer-driven UI updates.
- README documents the small-tools/fewer-mandatory-dependencies design goal and now ends with the project typography footer.
- Added regression coverage for input masks, secret echo, focus-aware textarea Tab behavior, and DOS-style `suminput` option spellings.

## 0.4.0a16

- Multiline `ScreenField`/GET editing now uses Enter for a real newline and Tab for next-field navigation; Tab on the final field accepts the READ, which works reliably on terminals that cannot distinguish Ctrl+Enter.
- Added `snapshot_screen_lines()` and `commit_screen_to_history()` so an absolute coordinate screen/GET form can be archived as ordinary, scrollable text after interaction finishes.
- Committed GET fields lose cursor/highlight styling and no longer remain live after READ/program completion.
- Added regression coverage for final-field Tab acceptance and screen-to-history archival.

## 0.4.0a14

- Added reusable multiline `TextArea` and source-oriented `TextEditor` widgets with cursor editing, line numbers, scrolling and modified-state tracking.
- Generalized `CommandWindow` `ScreenField`: WIDTH/HEIGHT are visible viewport dimensions and `max_length` is an independent logical limit.
- Added one-line horizontal GET scrolling and multiline textarea-style GET editing with soft wrapping, vertical scrolling and Ctrl+Enter accept.
- Added `CommandWindow.viewport_width` / `viewport_height` so host languages can discover the actual rendered workspace.
- Added `Application.size`, `.width`, and `.height` for current terminal dimensions and resize-aware applications.
- Generalized xterm modified-key decoding, including Ctrl+F9 / Alt+F9 used by IDE-style applications.
- Added regression tests for multiline editing, GET viewport dimensions and modified function keys.

## 0.4.0a13

- `CommandWindow` now uses unmodified `PageUp` / `PageDown` as the portable application-scrollback keys.
- `Shift+PageUp` / `Shift+PageDown` remain accepted aliases when a terminal actually forwards those modified keys.
- Documented the real-terminal limitation: common Linux terminal emulators reserve Shift+Page for emulator scrollback, so a full-screen TUI cannot reliably receive those keystrokes.
- The active scrollback hint now advertises `PgDn`, which is guaranteed to reach the application in normal terminal configurations.
- Added regression coverage for both plain Page keys and forwarded Shift+Page aliases.

## 0.4.0a12

- `CommandWindow` now has internal scrollback: `Shift+PageUp` moves to older command/output history and `Shift+PageDown` moves back toward the live prompt.
- POSIX ANSI input recognizes common Shift+PageUp/PageDown sequences; Windows uses the existing modifier-state path.
- While scrollback is active, the prompt is replaced by a small scrollback indicator and absolute `@ SAY`/`GET` screen overlays are hidden so old history remains readable.
- `BrowseForm` gained reusable `first()`, `previous()`, `next()`, `last()`, and wrap-around `find()` helpers.
- `RecordForm.set_values()` can reload an existing record without rebuilding controls, enabling edit/navigator dialogs.
- Added regression coverage for Shift+Page scrollback, modified-key decoding, record reload, and browser search/navigation.

## 0.4.0a11

- `RecordForm` fields gained data-entry navigation: Enter/Down advances and Up moves to the previous focusable field.
- Logical fields remain editable; Enter toggles the value and advances.
- RecordForm text/logical controls no longer consume Ctrl+End/Ctrl+Home, allowing host applications to bind classic xBase save/memo keys.
- Added regression tests for editing, field advance, and host-level Ctrl+End bindings.

## 0.4.0a10

- Added reusable `RecordForm` and `BrowseForm` data-form widgets.
- Added `FormField` descriptions and read-only fields for generated record forms.
- `TextInput` now accepts a visual `mask`, so empty fields may render classic xBase-style pictures such as `[XXXXXX]` or `[9990.00]`.
- `BrowseForm` uses `TableView` column headers as field names and keeps a `Rec n/N` status line.
- Added `demo_recordform.py` and `demo_browseform.py`.

## 0.4.0a9

- `ScreenField` READ cursors now use normal caret positions from `0` through `field.width`, including one visible position immediately after the last field cell.
- Typing the final character advances the caret outside the field, so `Backspace` from end-of-field deletes the actual last character instead of the previous one.
- `End` moves to the after-field caret position; Right can move from the final cell to that position, while Delete at the after-field position is a no-op.
- Added regression coverage for full-field typing, end-of-field Backspace, and rendering the caret one cell beyond the field.

## 0.4.0a8

- Fixed `Tab`/`Shift+Tab` in `CommandWindow` READ mode: the focused widget now gets first refusal on Tab before application-level focus traversal.
- `Tab` moves to the next active `ScreenField`; `Shift+Tab` moves to the previous field while READ is active.
- Fixed `Backspace` in fixed-width screen fields: it now deletes the character to the left, shifts the remaining text left, and pads the right edge instead of leaving stale trailing characters.
- Added regression tests for internal READ-field Tab navigation and deletion behavior.

## 0.4.0a7

- Added absolute-position editable `ScreenField` support to `CommandWindow`.
- Added `define_field()` and `begin_read()` for xBase-style `@ ... GET` / `READ` forms.
- `READ` mode supports Enter/Tab/Shift+Tab/Up/Down field navigation, cursor editing, Insert toggle, and Esc cancel.
- Added a dedicated `command_field` theme role while preserving the black command workspace.

## 0.4.0a6

- Added a persistent absolute-position screen layer to `CommandWindow`.
- Added `CommandWindow.write_at(row, column, text, style=...)` with zero-based workspace coordinates for xBase-style screen output.
- `CommandWindow.clear()` now clears both scrolling command history/output and the absolute screen layer; `clear_screen()` clears only the coordinate layer.
- The coordinate layer composes over scrolling command history while keeping the live prompt on the final row.
- Added regression tests for coordinate placement and clearing.

## 0.4.0a5

- Fixed `CommandWindow` rendering so the live input prompt/cursor is not clipped by `Panel`.
- Command history/output no longer consumes two terminal rows per logical line when rendered at full width.
- The input line is now always the final visible row of the command viewport.

## 0.4.0a4

Solid command-panel background fix after real-terminal sumX testing.

### Added

- `Panel(..., content_style=...)`, matching the dialog content-style mechanism, so a panel can own the complete style of its interior including padding and unused cells.

### Fixed

- `demo_commandwindow.py` now uses `content_style="command"`; the complete command workspace is black instead of drawing isolated black text rows over the XBASE cyan panel background.
- This specifically fixes the striped command-window appearance seen in sumX on a real terminal.

### Tested

- Regression coverage for a command-styled panel interior.
- Full compile, unit suite, CLI version/help/self-test and wheel import.

## 0.4.0a3

Viewer dialog background regression fix.

### Added

- `Dialog(..., content_style=...)` lets a modal choose a theme role for the complete panel interior, including otherwise-unused padding/background cells.

### Fixed

- The RAR-style F3 viewer now uses `content_style="viewer"`, so the complete dialog interior is black instead of exposing the surrounding blue dialog background between syntax-highlighted spans or in unused viewport space.
- The fix applies equally in normal and F11-maximized viewer geometry.

### Tested

- Regression coverage for dialog content-style selection.
- Existing viewer horizontal scrolling and F11 maximize/restore tests.
- Full compile, unit suite, CLI version/help/self-test and wheel import.

## 0.4.0a2

Viewer viewport and dialog-window polish.

### Added

- Horizontal scrolling for `TextView`, `SyntaxView`, and `HexView`; long text/source/hex rows are no longer permanently clipped by the visible width.
- `MarkdownView(..., wrap=False)` for an unwrapped horizontally scrollable Markdown viewport while preserving wrapped Markdown as the default.
- Horizontal navigation: Left/Right by one terminal cell, Shift+Left/Right by roughly one viewport, Ctrl+Left/Right to the horizontal edge.
- Optional `Dialog(maximizable=True)` support with F11 maximize/restore. Maximized modal dialogs occupy the complete terminal window and restore to their original configured geometry.

### Changed

- The RAR-style F3 viewer dialog is maximizable and advertises horizontal scrolling/F11 in its footer.
- Viewer clipping is cell-aware through Rich segments, so wide Unicode characters and syntax styles survive horizontal slicing.

### Tested

- Horizontal navigation and clipping for text, syntax and hex viewers.
- F11 modal maximize/restore dispatch through a focused child control.
- Full project compile, unit suite, demo snapshots, CLI version/help/self-test and wheel import.

## 0.4.0a1

sumX-oriented console foundation.

### Added

- `CommandWindow`, a dBASE/FoxPro-style command history + editable prompt widget.
- DBASE, FOXPRO and hybrid XBASE themes.
- `demo_commandwindow.py`.
- Viewer/command theme roles with a black content background.

### Changed

- `TextView`, `SyntaxView`, `MarkdownView` and `HexView` fill their content region with the viewer background instead of inheriting the surrounding blue panel.
- Pygments is now an explicit dependency because `SyntaxView` imports it directly.


## 0.3.0a2

Field/dialog and viewer polish after real-terminal testing.

### Fixed

- `FileDialog` rows now render as real `Name / Size / Type` cells instead of Python list/path representations.
- `FileDialog._activate()` now follows the `TableView` callback contract `(value, row)`; Enter no longer raises `TypeError`.
- `TableView.set_rows()` now also accepts convenient `(cells, value)` pairs.
- Fixed constrained `HBox`/`VBox` rendering so fixed-height dialogs no longer clip their bottom controls; FileDialog/DirectoryDialog buttons are visible.
- `MenuBar` drop-down width now accounts for marker, label, shortcut, submenu arrow and borders, keeping shortcuts such as `Quit  F10` on one line.
- `MenuBar` advertises a dynamic preferred height, avoiding the large unused area seen in the first menu demo.

### Added

- `SyntaxView`, with filename/extension lexer detection through Pygments and a Vim-style syntax theme by default.
- Syntax highlighting works for Python, shell, C, JSON, TOML, Markdown, HTML and the other filename types known to Pygments.
- `sumprogress` command:
  - percentage-stream mode (`--percent-input`);
  - pv-like byte pass-through mode (`--total SIZE`), with progress written to stderr and data preserved on stdout.
- `sumtui.easy.syntaxview()` and `sumtui.easy.radiobutton()` helpers.
- `demo_syntaxview.py`.

### Changed

- `MarkdownView` now preserves Rich styles instead of flattening rendered Markdown back to monochrome text; fenced/inline code uses the Vim Pygments theme by default.
- `demo_radiobutton.py` now demonstrates the individual primitive, while `demo_radiogroup.py` demonstrates mutual exclusion and grouped arrow navigation.
- `demo_rar_browser.py` now chooses `SyntaxView` automatically for text files and `HexView` for binary files. Syntax type is inferred from the filename extension.
- Source-tree demos bootstrap `src/` before importing `sumtui`, so development demos do not accidentally test an older installed copy.

### Tested

- 35 unit tests.
- 33 demo snapshots.
- FileDialog Enter/activation regression.
- Menu shortcut one-line regression.
- SyntaxView filename detection/rendering.
- `sumprogress` percentage and byte pass-through modes.

## 0.3.0a1

Commander-oriented widget expansion.

### Added

- `MenuBar`, `Menu`, `MenuItem`, `Separator` and nested submenus.
- Checked/radio menu item rendering.
- `ContextMenu`.
- `GroupBox`.
- `ListView`.
- `TreeNode` and `TreeView`.
- `ScrollBar` with optional keyboard interaction.
- `Splitter` with keyboard-adjustable ratio.
- `MarkdownView` using Rich Markdown rendering.
- `HexView` with hexadecimal + ASCII display and lazy file reads.
- `FileDialog` and `DirectoryDialog`.
- Additional theme roles for menus, scrollbars and splitters.
- Easy-API helpers for the new widgets.
- One demo program for each widget family.

### Changed

- Modal dialogs are composited over the previous application screen instead of replacing it visually.
- `Application.invalidate()` and the interactive Live renderer now render the complete modal stack.
- Public exports and documentation expanded for the Commander-oriented widget set.

## 0.2.0a3

- Arrow-key navigation across radio buttons.
- Arrow-key focus movement across consecutive checkboxes without toggling values.

## 0.2.0a2

- Visible inverted focus state for buttons.
- Added `Slider`; `ProgressBar` remains display-only.

## 0.2.0a1

- Dialog and form-control alpha.

## 0.1.0a1

- Initial Rich-rendered alpha with table/browser-oriented core widgets.

## 0.4.0a16

- TextEditor now supports Shift selection, Ctrl+Left/Right word navigation, Ctrl+C/Ctrl+Insert copy, Ctrl+X/Shift+Delete cut, Ctrl+V/Shift+Insert paste, Ctrl+Z undo, Ctrl+Y redo, and Ctrl+A select-all.
- Added an internal text clipboard with optional synchronization to the Python `clipboard` package/system clipboard.
- Added optional whitespace/control-code visualization in TextEditor.
- Added `sumtui.document` with encoding detection, LF/CRLF/CR detection, mixed-EOL preservation, safe writes, and EOL conversion.
- Added `sumedit`, a lightweight generic plain-text editor with menus, status bar, horizontal/vertical scrollbars, EOL/encoding status and visibility toggles.
- `sumedit --install-alias` installs a safe `$HOME/bin/edit` wrapper using `"$@"`.
- Added `sumeol` line-ending inspector/converter plus optional `$HOME/bin` compatibility wrappers for dos2unix/unix2dos/mac2unix/unix2mac.
