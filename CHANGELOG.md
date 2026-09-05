# 0.8.0a13

- Added a backward-compatible `KeyEvent.action` lifecycle field so graphical frontends can distinguish press from release.

# r20 coordinated release

- Aligned with SUM r20 architecture and package versions.

# Changelog

## 0.8.0a9 - 2026-09-02

- Added the terminal installer for the common conio-compatible API.
- Coordinated with sumUI r17 display/typography contracts.

## 0.8.0a8 - 2026-09-02
- Added common graphical-window PNG export to `Application`; the File menu in the shared editor/IDE shell exposes **Export graphical window as PNG...** when using the GUI backend.
- Updated coordinated contracts to sumUI 0.1.0a7 and optional graphical rendering to sumGUI 0.2.0a9.

## 0.8.0a7 - 2026-09-02
- ZX is now the fresh-install default theme across Application, sumedit, sumdialog and easy-mode helpers.
- Removed the retired third-party-derived editor colour scheme and its dedicated demos/documentation.
- Existing saved configurations that name a no-longer-installed theme fall back safely to ZX.
- Theme editor and example launchers now start on ZX.

## 0.8.0a5 - 2026-09-02

- Reworked `sumedit --gui`: it no longer launches a second simplified editor implementation. `sumedit` constructs one `EditApp` and selects the presentation backend only when the application starts.
- `Application.run(backend="gui")` hands the same live application/widget tree, focus model, commands, dialogs, editor, syntax highlighter, keybindings and theme to the installed sumGUI backend.
- Terminal mode remains the default and retains its existing keyboard **and mouse** support, including click, drag selection, wheel and scrollbar handling.
- The old `edit_gui` module is now only a compatibility launcher around the same `EditApp`; application behavior is no longer duplicated there.
- Updated the common UI baseline to sumUI 0.1.0a4 and the optional graphical backend to sumGUI 0.2.0a6.

## 0.8.0a4 - 2026-09-02

- Added `sumedit --gui [FILE]`, an optional Pygame/sumGUI frontend over the same `TextDocument` used by the terminal editor; plain `sumedit` remains terminal-first.
- The GUI editor keeps encoding/EOL-aware loading and saving, selection/clipboard-capable `TextArea`, scrollbars, basic undo/redo, Open/Save/Save As/Reload, and common keyboard shortcuts.
- Added the optional `gui` extra (`sumgui>=0.2.0a4`) without making Pygame a dependency of normal sumTUI installations.

## 0.8.0a3 - 2026-09-02

- Tightened text-chart presentation for the shared `ChartSpec`: Rich rendering no longer inserts an extra blank row between every rendered chart line.
- This makes `sumchart --backend=tui` output compact enough for shell pipelines, SSH sessions and future sumPY/sumR reports.

## 0.8.0a1

- Add the backend-neutral `sumui` dependency and expose `ChartSpec`, `ChartSeries`, `AxisSpec` and `GraphicsMode`.
- Add `ChartView` for terminal charts.
- Add ASCII/Unicode horizontal bar and pie renderers.
- Add ASCII/Unicode grid plots and a high-resolution Braille renderer for line/scatter charts.
- Keep chart data independent of pandas/NumPy while allowing adapters through `sumui`.
- Establish the same chart specification consumed by sumGUI.

## 0.7.7 - 2026-09-01

- Added reusable field validation to the common input layer. `TextInput`, `CommandWindow` screen fields, `InputSpec`, `read_entry()` and `FormFieldSpec` can now validate a complete value while keeping focus on invalid input.
- Added `--valid-values A,B,...` and `--validation-error TEXT` to `sumdialog --entry` and `suminput`; form mode adds `--form-valid-values NAME=A,B,...`, `--form-error NAME=TEXT` and `--form-case-sensitive NAME`.
- Added declarative `.sdlg` validation properties: `field:NAME.valid_values`, `field:NAME.validation_error` and `field:NAME.case_sensitive`.
- Added `PICTURE "@M value1,value2,..."` to the common input-mask engine. Choice masks filter keystrokes and validate the complete result; `@!` without a data mask remains a pass-through uppercase transform rather than creating a zero-length field.
- Validation composes with `CONFIRM`: with confirmation ON an invalid field remains active; with confirmation OFF an invalid full field stays editable and subsequent keys overwrite the final logical character until the value becomes valid.
- Message/question/warning/error dialogs now use semantic colors chosen from the active theme palette: cyan-like information, blue-like questions, yellow-like warnings and red-like errors. Text/title contrast is selected automatically, and form validation messages use the error style.
- Regression suite: 198 tests passing, with one optional SumDoc compatibility test skipped when SumDoc is not installed in the isolated test environment.

## 0.7.6 - 2026-09-01

- Exposed the common bounded-field confirmation policy through `sumdialog` and `suminput`. `--confirm` is ON by default; `--no-confirm` auto-submits a bounded standalone entry when its logical capacity is reached.
- Added `--max-length N` to `sumdialog --entry` and `suminput`, keeping logical field capacity independent of visible `--width`. With confirmation ON, further printable keys at the logical end overwrite the final logical character.
- Extended `FormFieldSpec` with `max_length` and `confirm`, so `sumdialog --forms` uses the same common `TextInput` behavior for entry/password/file/directory fields. CLI forms support repeatable `--form-max-length NAME=N` and `--form-no-confirm NAME`.
- Extended declarative `.sdlg` forms with `field:NAME.max_length=N` and `field:NAME.confirm=true|false`; normalized dumps include both properties.
- Kept `CONFIRM ON` semantics as the system default because explicit confirmation is safer and more practical for sustained data entry; `CONFIRM OFF` remains an opt-in auto-advance mode.
- Regression suite: 188 sumTUI tests passing with the separate sumIDE compatibility package available.

## 0.7.5 - 2026-09-01

- Unified bounded-field end-of-input behavior in the common widget layer. A field with a logical maximum now keeps accepting printable keys at its logical end by overwriting the final logical character rather than silently rejecting further input.
- Added `CommandWindow.begin_read(..., confirm=...)`: confirmation ON keeps a bounded READ field active at its logical end; confirmation OFF auto-advances to the next field and accepts on the last field.
- Added the equivalent `TextInput(confirm_at_limit=...)` policy so dialogs, forms and language frontends can share the same logical-limit semantics instead of reimplementing them.
- Logical limits remain independent of viewport width; PICTURE/input filters receive the actual logical replacement position when the final character is being overwritten.

## 0.7.4 - 2026-09-01

- Made Markdown document mapping an explicit always-available `sumedit` behavior: Markdown detection automatically relabels F2/menu mapping as a document outline; it is not a sumIDE-only option.
- Added an inheritable `CommandWindow` content style so command/screen surfaces embedded in colored dialogs can preserve the parent dialog background instead of painting default command-background cells over it.
- Reorganized shell examples by the sumTUI facility they demonstrate (`examples/edit`, `examples/suminput`, `examples/sumdialog`, `examples/theme`) and removed application-level IDE/`hello.*` examples, which now belong to sumIDE.
- Kept the reusable workspace geometry model, including mouse and keyboard resizing, as the common foundation used by the new sumIDE three-window default layout.

## 0.7.3 - 2026-09-01

- Moved ownership of Markdown ↔ `.helpdb` parsing/serialization and command-line conversion to `sumdoc` 0.2.1.
- Reduced `sumtui.helpdb` to the runtime data model and compiled-help reader needed by help viewers.
- Kept lazy compatibility bridges for callers of the former conversion API without adding SumDoc as a mandatory sumTUI dependency.
- Removed the `markdown2helpdb` and `helpdb2markdown` console entry points from sumTUI; the commands are now installed by SumDoc.
- Preserved Markdown rendering, code-example copying, topic/list scrollbars, and the F2 topic-map UI unchanged.

## 0.7.2 - 2026-09-01

- Added reusable `ListViewPane` / `TableViewPane` vertical-scrollbar wrappers for long topic and table lists.
- Added the common editable Markdown help corpus format in `sumtui.helpdb`.
- Added `markdown2helpdb` and `helpdb2markdown` command-line converters. Markdown remains the canonical editable source; `.helpdb` is an optional generated JSON interchange/cache format.


## 0.7.1 - 2026-09-01

- Added reusable fenced-code extraction/copy support to `MarkdownView`.
- Common text/help dialogs now provide a Copy button and `Ctrl+C` clipboard action.
- sumedit help/about dialogs use the same copyable-help convention.

## 0.7.0 - 2026-09-01

- Established the post-split editor foundation for the current Sum ecosystem: `sumTUI` owns reusable TUI/editor primitives and the standalone `sumedit`; application-level IDE behavior lives in the independent `sumIDE` project.
- Centralized `sumedit` preferences in a sectioned dialog instead of requiring direct JSON/menu-fragment editing.
- Added safe Vim modelines in the first/last configurable lines with a strict whitelist for `ts/sw/sts`, `et/noet`, `sr/nosr`, `syntax/ft`, `ff`, and `fenc`; modelines never execute Vim commands.
- Split indentation semantics into visual tab width, shift width and soft-tab width. Modern defaults are four columns; language-specific overrides belong to `sumIDE`.
- Added `Alt+W` forward word/whitespace deletion, `Ctrl+Alt+W` backward deletion, selected-block `Tab`/`Shift+Tab`, and whole-document tabs/spaces conversion.
- Reassigned the Window accelerator to `Alt+I`, permanently freeing `Alt+W` for editing.
- Kept `sumtui.tools.ide` as a compatibility bridge only; it now points users to `sumIDE >= 0.2.0`.
- This release incorporates and supersedes the 0.6.1/0.6.2 editor/IDE-split work while preserving the earlier changelog below.

## 0.6.2

- Extracted the application-level multi-language IDE into the independent `sumIDE` project. `sumTUI` now owns the reusable TUI/editor primitives and keeps `sumedit`; the old `sumtui.tools.ide` module is only a compatibility bridge when `sumIDE` is installed.
- Removed the `sumide`, `sumpyide`, `sumride`, `sumbashide`, `sumcide` and `sumcppide` console-script ownership from the `sumTUI` package.
- Added a sectioned **Options -> Preferences...** dialog to `sumedit`, centralizing General, Editor/Features, Editor/Indentation, Editor/Modelines, Files, Keybindings, Display and Advanced settings instead of exposing configuration only through JSON/menu fragments.
- Added safe Vim modeline parsing in the first/last configurable lines. Supported metadata: `ts/tabstop`, `sw/shiftwidth`, `sts/softtabstop`, `et/noet`, `sr/nosr`, `syntax/ft`, `ff/fileformat`, and `fenc/fileencoding`; arbitrary Vim commands are never executed.
- Split editor indentation semantics into visual tab width, shift/indent width and soft-tab width. Literal TAB insertion versus spaces is controlled independently by `expand_tabs`; `shiftround` is supported.
- Kept modern defaults at four columns; language-specific defaults belong to `sumIDE` (HTML uses two spaces there).

## 0.6.1

- Added editor word/whitespace deletion: **Alt+W** deletes forward through the next word boundary and **Ctrl+Alt+W** deletes one backward word/separator segment without crossing line boundaries.
- Reassigned the Window-menu accelerator from **Alt+W** to **Alt+I** so Alt+W remains a consistent editing command.
- Added block indentation: **Tab** indents all selected lines and **Shift+Tab** unindents them while preserving the selection; Shift+Tab also unindents the current line.
- Added whole-document **Tabs -> N spaces** and **N spaces -> Tabs** conversions using the configured tab width.
- Added regression coverage for forward/backward deletion, line-boundary safety, block indentation, tab/space conversion and the new Window accelerator. Regression suite: 177 tests.

## 0.6.0

- Promoted the common editor/workspace line to 0.6.0 and added optional integration with the separate `sumdiff` application without making `sumdiff` a dependency of the toolkit.
- Added `sumtui.compare_integration`: runtime detection and in-process terminal handoff to `sumdiff`, including live in-memory text overrides for unsaved buffers.
- `sumedit` and all `EditApp`-derived IDEs expose **File -> Compare with...**. Files saved inside `sumdiff` are reloaded into the originating editor on return.
- Multi-source `sumIDE` adds **Compare with open buffer** and **Compare all open documents**; two documents use Compare mode and three or more use Parallel Documents mode.
- The integration preserves the architectural direction: `sumdiff` depends on sumTUI, never the reverse.
- Added regression coverage for editor menu integration, live-buffer handoff data and N-document sumIDE launch selection. Regression suite: 171 tests.

## 0.5.29

- Workspace windows can persist geometry across application runs: left/top, width/height and maximized state are stored by stable window name and clamped to the current terminal on restore.
- Added `Workspace.layout_state()`, `load_layout()`, `save_layout()`, `reset_layout()` and `clear_saved_layout()` plus late-window restore support for multi-source sumIDE workspaces.
- sumIDE uses a `sumide` layout namespace in the sibling `workspaces.json` configuration file and automatically loads on run / saves on shutdown.
- Added **Window -> Reset Window Layout**, which restores each window to the geometry it had when the workspace was created and removes the persisted layout so the defaults remain in effect next launch.
- Added regression coverage for save/restore, maximized state, late-added windows and reset/clear behavior.

## 0.5.28

- Workspace windows can now be resized with the mouse by dragging the lower-right corner; resize tracking shares the existing z-order/drag machinery and respects workspace minimum/bounds constraints.
- Added keyboard geometry modes for terminals and Termux: **Alt+M** enters Move and **Alt+Z** enters Resize; plain arrows adjust one cell, Shift+arrows adjust five cells, Enter accepts, and Escape restores the original geometry.
- Active window titles show `[MOVE]` / `[SIZE]` while a keyboard geometry operation is in progress.
- Added a first-refusal `capture_event()` path so arrow keys in Move/Resize mode are consumed before TextEditor/Command controls move their own cursors.
- Window menus and sumedit/sumIDE shortcut documentation expose Move/Resize, and `demo_workspace.py` demonstrates mouse and keyboard sizing.
- Added regression coverage for lower-right-corner mouse resizing, keyboard Move/Resize commit/cancel, and capture precedence over editor navigation.

## 0.5.27

- F2 Program Map / Document Outline now opens preselected on the symbol/section containing the editor cursor. The common behavior applies to sumedit and sumIDE language profiles; downstream IDEs can reuse `symbol_index_for_line()`.
- Added a real Markdown preview to sumedit (`View -> Markdown Preview...`) using the current unsaved buffer.
- Markdown preview now renders pipe tables with Unicode box borders and left/center/right alignment instead of flattening them to loose columns.
- Added `MarkdownViewPane` with visible vertical/horizontal scrollbars for wide and long previews.
- Added integrated Markdown `Export HTML` and `Export PDF` actions from both File and Preview. HTML uses markdown-it-py table rendering plus a standalone styled document; PDF uses WeasyPrint when available and falls back to common external PDF backends.
- Added regression coverage for current-section F2 selection, bordered table rendering, preview creation, HTML export, and PDF export when a backend is available. Regression suite: 164 tests.

## 0.5.26

- Fixed the F2 Markdown document-outline dialog height calculation: the table header and dialog chrome consumed one more row than the previous formula allowed, so the final heading could be present in the symbol map but clipped from the visible list.
- Added regression coverage using a two-section Markdown document matching the reported structure, verifying that both `###` headings are parsed and rendered in the F2 outline at the same time.

## 0.5.25

- F2 / Program Map now becomes a Markdown document outline for `.md`, `.markdown`, `.mdown`, `.mkd`, and extensionless `README` files.
- Markdown outline entries recognize ATX levels `#` through `######` and Setext title/section underlines, show TITLE / SECTION / SUBSECTION hierarchy, and jump to the heading line.
- Heading-like text inside fenced code blocks is excluded from the outline, so embedded examples do not pollute document navigation.
- Renamed the generic Search-menu entry to `Program Map / Outline...`; code languages retain the existing Functions / Classes / Main map.
- Added `examples/markdown_outline.md` and regression coverage for Markdown detection, heading levels, Setext sections, and fenced-code exclusion. Regression suite: 156 tests.

## 0.5.24

- sumIDE now opens multiple source files at once, including mixed Python, R, Bash, C and C++ code in one movable workspace. `Ctrl+O` adds a Code window and the Window menu can switch between every source plus Output/Command.
- The active Code window owns its language profile, syntax, Program Map, direct-command prompt and Run/build behaviour.
- Added `Ctrl+F6` / `Run -> Compile current buffer` for C/C++. Persistent build output is `<stem>.run` on POSIX/Android and `<stem>.exe` on Windows; F5 remains compile-and-run through a temporary executable.
- C/C++ build command expansion now quotes paths appropriately for POSIX or Windows shells, with POSIX `cc`/`c++` and Windows `gcc`/`g++` defaults.
- Added Workspace activation callbacks so IDE hosts can synchronize document state when windows are selected by keyboard or mouse.
- Added `examples/bash/multilang_ide.sh` for comparative multi-language study.

## 0.5.23

- Fixed the C/C++ IDE **Build commands** dialog: it no longer passes an unsupported `width` argument to `Label`; the label column width is controlled by `HBox` as intended.
- Added a regression test that opens the Build commands dialog for both C and C++ profiles.

## 0.5.22

- F2 is now the reusable **Program Map / Symbols** action; the shared symbol mapper recognizes MAIN plus Python classes/functions/methods, R functions/classes, Bash functions, BASIC SUB/FUNCTION, xBase PROCEDURE/FUNCTION/classes, and C/C++ functions/classes/methods.
- Standardized editor/IDE shortcuts: Ctrl+S Save, Ctrl+O Open, Ctrl+F Find, Ctrl+X Cut, Ctrl+Q Quit; F5/Ctrl+R Run/Stop in runnable IDEs; F6/Ctrl+Tab Next Window; F11/Alt+Enter Maximize/Restore.
- Added explicit Alt menu accelerators suitable for Termux and other keyboards without function keys: Alt+F/E/S/V/O/W/R/H, plus Alt+P for Program Map.
- Added SAVE_AND_EXIT / FORGET_AND_EXIT / CANCEL confirmation before destructive operations on a modified Code buffer.
- Added visible `TextViewPane` and `CommandWindowPane` scrollbars for IDE Output/Command and switched streamed output to newline-preserving append semantics.
- Extended the generic IDE from Python/R to Python, R, Bash, C and C++; added `sumbashide`, `sumcide`, `sumcppide` and configurable C/C++ compile/run templates.
- Regression suite: 150 tests.

## 0.5.21

- Added `Application.run_external(callback)` for temporarily yielding the real terminal to an external interactive process and restoring the sumTUI alternate screen/input mode afterward.
- External-terminal requests made by IDE/background worker threads are marshalled to the application thread, avoiding concurrent reads from the controlling TTY.
- Added an external-shell example and regression coverage for direct and worker-thread terminal handoff. Regression suite: 145 tests.

## 0.5.20

- Added reusable overlapping IDE windows through public `Workspace` and `WorkspaceWindow`: movable terminal-cell geometry, mouse title dragging, z-order activation, persistent hide/reopen, F6 cycling, F11 maximize/restore, Ctrl+F4 close, and Alt+Arrow keyboard movement.
- Focus management can now refresh after workspace activation/visibility changes, and `MenuDesktop` forwards unhandled keyboard events to its body so active workspace-window controls retain their own shortcuts.
- `sumedit` gains a dynamic **Window** menu and the common IDE window-management actions while remaining a single-document editor when no workspace is installed.
- Added the shared `sumide` script IDE with separate Code, Output, and Command windows. `sumide` auto-detects Python/R, while `sumpyide` and `sumride` force the corresponding profile; Python direct mode keeps a persistent namespace and R direct mode uses a persistent R process when available.
- F5 runs/stops the current unsaved Python/R buffer in a subprocess; F6 cycles windows, F11 maximizes/restores, Ctrl+F4 closes, and the Window menu can reopen default windows.
- Added workspace and script-IDE examples and regression coverage. Regression suite: 143 tests.

## 0.5.19

- Documentation/example consistency pass after the multi-row Button and IDE-key changes: README now identifies 0.5.19, the sumdialog example index explicitly documents `--button-width` / `--button-height`, and every bundled README again ends with the required literal project footer.
- No widget/runtime behavior changed from 0.5.18; the 0.5.18 multi-row layout propagation, sumdialog geometry, sumedit dialog sizing, and F6 `Next Window` behavior remain the implementation being documented.
- Regression suite remains 135 tests.

## 0.5.18

- Completed the multi-row `Button` integration across the toolkit instead of limiting it to the primitive/demo: nested `HBox`/`VBox` containers now report useful preferred cross-axis geometry, so a row containing `Button(height=3)` asks its parent for three terminal rows automatically.
- Removed hard-coded one-row action areas from `sumdialog`, `sumedit`, file dialogs, input dialogs, and theme dialogs where the child button row can now size itself. Compact one-row buttons remain the default.
- Added `sumdialog --button-width` and `--button-height`; the same geometry is available through the Python dialog APIs and declarative `.sdlg` properties `button_width` / `button_height`. File-selection and entry dialogs use the same settings.
- `sumtui.easy.button()` now exposes width, height, horizontal alignment, and vertical alignment.
- The generic editor/IDE base reserves **F6 = Next Window** through a reusable `window.next` action. IDE flavours can return their editor/output work areas from `window_targets()` while retaining one common key convention.
- Updated Python, Bash, and declarative sumdialog examples to exercise 3-row buttons.
- Regression suite: 135 tests.

## 0.5.17

- `Button` now accepts both `width` and `height` in terminal cells. `height=1` keeps the existing compact appearance; taller buttons style the complete rectangular area and vertically center their label by default.
- Added `align` (`left`, `center`, `right`) and `valign` (`top`, `middle`, `bottom`) to button label placement. Width calculations use Rich terminal-cell width so wide Unicode text does not corrupt the requested geometry.
- Button mouse hit-testing now follows the actual visible rectangle instead of the complete cross-axis allocation supplied by a parent layout.
- `HBox` and `VBox` now consult `preferred_width()` / `preferred_height()` when an item has no explicit layout size. A `Button(width=24, height=3)` therefore consumes 24 columns in an `HBox` and three rows in a `VBox` automatically.
- Added common flow-layout geometry to `Widget`: `bounds`, `x`, `y`, `layout_width`, and `layout_height`, plus preferred-size hooks for gradual adoption by other controls.
- Updated the button demo to show two 24x3 controls and added regression coverage for multi-row rendering, mouse footprint, and preferred-size layout allocation.

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

## 0.5.9

- Added reliable terminal decoding for modified Home/End sequences, including xterm-style `Ctrl+Home`, `Ctrl+End`, `Shift+Home/End`, and legacy tilde variants. `TextEditor` already treated Ctrl+Home/End as document-edge navigation; the actual terminal input path now delivers those modifiers correctly.
- Confirmed and regression-tested selection extension with `Shift+Up`, `Shift+Down`, `Shift+PageUp`, and `Shift+PageDown`, including page-sized movement while keeping the original selection anchor.

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
