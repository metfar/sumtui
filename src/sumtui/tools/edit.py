#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#pylint:disable=W0301
#  
#  Copyright 2018- William Martinez Bas <metfar@gmail.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#
#import warnings;
#warnings.filterwarnings("ignore", category=UserWarning);
import argparse;
import json;
import os;
from pathlib import Path;
import re;
import sys;

from rich.text import Text;

from .. import __version__;
from ..app import Application;
from ..document import TextDocument;
from ..events import Key;
from ..keybindings import KeyBindingManager, format_key_spec;
from ..syntax import SYNTAX_MODES, normalize_mode;
from ..theme import THEMES, available_theme_names, refresh_user_themes;
from ..widgets import Button, CheckBox, Dialog, FileDialog, FunctionBar, HBox, Label, ListView, Menu, MenuBar, MenuDesktop, MenuItem, Panel, ScrollBar, Separator, StatusBar, TextEditor, TextInput, TextView, VBox, Widget;


_EOL_MARKERS = {"\n": "↵", "\r\n": "⏎", "\r": "↩"};
_HELP_TEXT = """sumTUI edit

Keyboard
  F1                  Help
  F2                  Save
  F3                  Find next
  F6                  Next window/work area
  F11                 Maximize/restore workspace window
  Ctrl+F4             Close workspace window
  Alt+Arrow           Move workspace window
  F9                  Menu
  F10                 Exit
  Shift + movement    Extend selection
  Ctrl+Left/Right     Previous/next word boundary
  Ctrl+Home/End       Beginning/end of document
  Shift+Up/Down       Extend selection vertically
  Shift+PgUp/PgDn     Extend selection by a page
                       (decoded using active terminfo plus xterm/rxvt fallbacks)
  Ctrl+C / Ctrl+Ins   Copy
  Ctrl+X / Shift+Del  Cut
  Ctrl+V / Shift+Ins  Paste
  Ctrl+Z / Ctrl+Y     Undo / Redo
  Ctrl+A              Select all
  Ctrl+F              Find
  Shift+F3            Find previous
  Ctrl+H              Search and replace
  Ctrl+G              Go to line

Mouse (POSIX terminals with SGR mouse reporting)
  Left click          Place the caret / focus a control
  Left drag           Extend editor selection
  Wheel               Scroll vertically
  Scrollbar click     Page the viewport
  Scrollbar drag      Move the viewport thumb

Search options
  Case sensitive, whole word, regular expression and wrap-around are optional.

View markers
  ·   space
  ⇥   tab
  ↵   LF line ending
  ⏎   CRLF line ending
  ↩   CR line ending
  ␀…␟, ␡   control characters

View menu checkboxes can be toggled with Space.
Syntax highlighting is available in the editor and is auto-detected from the file name when possible.
Markdown highlighting includes headings, emphasis, links, inline HTML and fenced code blocks; fenced Python, Bash, SQL, BASIC, sumX and other known languages reuse their normal syntax roles.
Options contains Tab width, Theme, Line wrapping, Line breaking, Keyboard shortcuts and Save configuration.
Ralesk's MC is included as a Geany-derived Midnight Commander-like theme and is the fresh-install sumedit default.
Line wrapping is visual only: -1 means automatic to the current editor width, 0 disables wrapping, and positive values set a maximum visual width. 78 is the legacy 80-column-window preset (80 minus two border cells).
Line breaking is separate and modifies text when enabled; 0 keeps automatic hard breaking off.
Keyboard shortcuts can be changed, extended, removed or restored to defaults.
""";


def _default_config_path():
    base = os.environ.get("XDG_CONFIG_HOME");
    if base:
        return Path(base).expanduser() / "sumtui" / "edit.json";
    return Path("~/.config/sumtui/edit.json").expanduser();


def _load_config(path):
    target = Path(path);
    try:
        data = json.loads(target.read_text(encoding="utf-8"));
        return data if isinstance(data, dict) else {};
    except (OSError, ValueError, TypeError):
        return {};




class _ShortcutCapture(Widget):
    focusable = True;

    def __init__(self, on_capture, on_cancel=None, theme=None):
        super().__init__(theme=theme);
        self.on_capture = on_capture;
        self.on_cancel = on_cancel;
        self.last_spec = "";

    def handle_event(self, event):
        if getattr(event, "key", "") == Key.ESCAPE:
            if self.on_cancel is not None:
                self.on_cancel();
            return True;
        spec = getattr(event, "name", "");
        if not spec:
            return False;
        self.last_spec = spec;
        if self.on_capture is not None:
            self.on_capture(spec);
        return True;

    def __rich_console__(self, console, options):
        text = "Press a shortcut..." if not self.last_spec else "Received: {}".format(format_key_spec(self.last_spec));
        yield Text(text, style=self.theme.style("input"));


class _EditorVScroll(ScrollBar):
    def __init__(self, editor, **kwargs):
        self.editor = editor;
        kwargs.setdefault("on_change", self._changed);
        super().__init__(orientation="vertical", **kwargs);

    def _changed(self, _scrollbar, value):
        self.editor.y_offset = max(0, int(value));
        self.editor._clamp_viewport();
        return True;

    def __rich_console__(self, console, options):
        self.page = max(1, self.editor.page_height);
        total = self.editor.visual_line_count(max(1, self.editor.page_width - self.editor._gutter_width()));
        self.maximum = max(0, total - self.page);
        self.value = max(0, min(self.maximum, self.editor.y_offset));
        yield from super().__rich_console__(console, options);


class _EditorHScroll(ScrollBar):
    def __init__(self, editor, **kwargs):
        self.editor = editor;
        kwargs.setdefault("on_change", self._changed);
        super().__init__(orientation="horizontal", **kwargs);

    def _changed(self, _scrollbar, value):
        if self.editor.line_wrapping == 0:
            self.editor.x_offset = max(0, int(value));
            self.editor._clamp_viewport();
        return True;

    def __rich_console__(self, console, options):
        gutter = self.editor._gutter_width();
        self.page = max(1, self.editor.page_width - gutter);
        if self.editor.line_wrapping != 0:
            self.maximum = 0;
            self.value = 0;
        else:
            longest = max([len(line) for line in self.editor.lines] or [0]);
            self.maximum = max(0, longest - self.page);
            self.value = max(0, min(self.maximum, self.editor.x_offset));
        yield from super().__rich_console__(console, options);


class EditApp:
    def __init__(self, path=None, theme=None, force_binary=False, config_path=None):
        self.force_binary = bool(force_binary);
        self.config_path = Path(config_path).expanduser() if config_path is not None else _default_config_path();
        self.config = _load_config(self.config_path);
        selected_theme = theme or self.config.get("theme") or "Ralesk's MC";
        self.document = self._load_document(path);
        self.app = Application(title="sumTUI edit", theme=selected_theme, capture_control_keys=True, mouse=True);
        self.search_query = "";
        self.replace_text = "";
        self.search_case_sensitive = False;
        self.search_whole_word = False;
        self.search_regex = False;
        self.search_wrap = True;
        tab_size = int(self.config.get("tab_size", 4));
        if tab_size not in (2, 4, 8):
            tab_size = 4;
        syntax_mode = normalize_mode(self.config.get("syntax_mode", "auto"));
        syntax_enabled = bool(self.config.get("syntax_highlighting", True));
        syntax_filename = self.document.path.name if self.document.path is not None else None;
        try:
            line_wrapping = int(self.config.get("line_wrapping", -1));
        except (TypeError, ValueError):
            line_wrapping = -1;
        try:
            line_breaking = max(0, int(self.config.get("line_breaking", 0)));
        except (TypeError, ValueError):
            line_breaking = 0;
        self.editor = TextEditor(self.document.text, tab_size=tab_size, line_numbers=True, on_change=self._editor_changed, on_cursor=self._cursor_changed, command_shortcuts=False,
                                 syntax_highlighting=syntax_enabled, syntax_language=syntax_mode, syntax_filename=syntax_filename,
                                 line_wrapping=line_wrapping, line_breaking=line_breaking);
        self.editor.configure_visibility(
            spaces=bool(self.config.get("show_spaces", False)),
            tabs=bool(self.config.get("show_tabs", False)),
            line_endings=bool(self.config.get("show_line_endings", False)),
            controls=bool(self.config.get("show_control_chars", False)),
        );
        self.keys = KeyBindingManager();
        self._register_keybindings();
        self.keys.load_overrides(self.config.get("keybindings", {}));
        self._sync_document_markers();
        self.vscroll = _EditorVScroll(self.editor);
        self.hscroll = _EditorHScroll(self.editor);
        self.status = StatusBar("");
        self.menu = MenuBar(self._menus(), on_close=self._menu_closed, activation_key=self.keys.primary("menu.activate"), mnemonics=False);
        self.bar = self._make_function_bar();
        self._install_keybindings();
        editor_box = VBox(HBox(self.editor, self.vscroll, sizes=[None, 1]), self.hscroll, sizes=[None, 1]);
        title = self.document.path.name if self.document.path is not None else "Untitled";
        self.panel = Panel(editor_box, title=title, content_style="viewer");
        body = VBox(self.panel, self.status, self.bar, sizes=[None, 1, 1]);
        self.desktop = MenuDesktop(self.menu, body);
        self.app.set_root(self.desktop);
        self.app.focus.set(self.editor);
        self._update_status();

    def _register_keybindings(self):
        actions = [
            ("help.editor", "Help", ["f1"], self.help),
            ("file.new", "New", ["ctrl+n"], self.new_file),
            ("file.open", "Open", ["ctrl+o"], self.open_dialog),
            ("file.save", "Save", ["f2", "ctrl+s"], self.save),
            ("app.exit", "Exit", ["f10", "alt+x", "ctrl+q"], self.quit),
            ("editor.undo", "Undo", ["ctrl+z"], self.editor_undo),
            ("editor.redo", "Redo", ["ctrl+y"], self.editor_redo),
            ("editor.cut", "Cut", ["ctrl+x", "shift+delete"], self.editor_cut),
            ("editor.copy", "Copy", ["ctrl+c", "ctrl+insert"], self.editor_copy),
            ("editor.paste", "Paste", ["ctrl+v", "shift+insert"], self.editor_paste),
            ("editor.select_all", "Select All", ["ctrl+a"], self.editor_select_all),
            ("search.find", "Find", ["ctrl+f"], self.find_dialog),
            ("search.next", "Find Next", ["f3"], self.find_next),
            ("search.previous", "Find Previous", ["shift+f3"], self.find_previous),
            ("search.replace", "Search & Replace", ["ctrl+h"], self.replace_dialog),
            ("search.goto_line", "Go to Line", ["ctrl+g"], self.goto_line_dialog),
            ("window.next", "Next Window", ["f6"], self.switch_window),
            ("window.close", "Close Window", ["ctrl+f4"], self.close_workspace_window),
            ("window.maximize", "Maximize / Restore Window", ["f11"], self.toggle_workspace_maximize),
            ("menu.activate", "Menu", ["f9"], self.open_menu),
            ("menu.file", "File menu", ["alt+f"], lambda: self.open_menu(0)),
            ("menu.edit", "Edit menu", ["alt+e"], lambda: self.open_menu(1)),
            ("menu.search", "Search menu", ["alt+s"], lambda: self.open_menu(2)),
            ("menu.view", "View menu", ["alt+v"], lambda: self.open_menu(3)),
            ("menu.options", "Options menu", ["alt+o"], lambda: self.open_menu(4)),
            ("menu.window", "Window menu", ["alt+w"], lambda: self.open_menu(5)),
            ("menu.help", "Help menu", ["alt+h"], lambda: self.open_menu(6)),
        ];
        for name, label, defaults, callback in actions:
            self.keys.register(name, label, defaults, context="editor", callback=callback);
        return self.keys;

    def _ks(self, action):
        return self.keys.display(action);

    def _make_function_bar(self):
        actions = [];
        for action_name, label in (("help.editor", "Help"), ("file.save", "Save"), ("search.next", "Find"), ("window.next", "Window"), ("menu.activate", "Menu"), ("app.exit", "Exit")):
            key = self.keys.primary(action_name);
            if key:
                actions.append((key, label, None));
        return FunctionBar(actions);

    def _install_keybindings(self):
        self.keys.install(self.app, contexts=["editor"], clear=True);
        return True;

    def _refresh_key_surfaces(self):
        self.menu.menus = self._menus();
        self.menu.activation_key = self.keys.primary("menu.activate");
        self.bar.actions = self._make_function_bar().actions;
        self._install_keybindings();
        self.app.invalidate();
        return True;

    def window_targets(self):
        """Focusable top-level work areas cycled by F6 in IDE-style applications."""
        return [self.editor] if getattr(self, "editor", None) is not None else [];

    def _workspace(self):
        return getattr(self, "workspace", None);

    def switch_window(self):
        workspace = self._workspace();
        if workspace is not None:
            changed = workspace.next_window();
            if changed:
                active = workspace.active_window;
                self._update_status("Window: {}".format(active.title if active is not None else "none"));
                self.app.invalidate();
            return bool(changed);
        targets = [item for item in self.window_targets() if item is not None];
        if not targets:
            return False;
        current = self.app.focus.current;
        try:
            index = targets.index(current);
        except ValueError:
            index = -1;
        target = targets[(index + 1) % len(targets)];
        self.app.focus.set(target);
        self.app.invalidate();
        return True;

    def activate_workspace_window(self, window):
        workspace = self._workspace();
        if workspace is None:
            return False;
        changed = workspace.show(window);
        if changed:
            self._update_status("Window: {}".format(window.title));
            self.app.invalidate();
        return bool(changed);

    def close_workspace_window(self, window=None):
        workspace = self._workspace();
        if workspace is None:
            return False;
        target = window or workspace.active_window;
        if target is None:
            return False;
        changed = workspace.close(target);
        if changed:
            self._update_status("Closed window: {}".format(target.title));
            self.app.invalidate();
        return bool(changed);

    def toggle_workspace_maximize(self, window=None):
        workspace = self._workspace();
        if workspace is None:
            return False;
        target = window or workspace.active_window;
        if target is None:
            return False;
        if workspace.active_window is not target:
            workspace.activate(target);
        changed = target.toggle_maximize();
        if changed:
            self._update_status(("Maximized: " if target.maximized else "Restored: ") + target.title);
            self.app.invalidate();
        return bool(changed);

    def _window_menu(self):
        workspace = self._workspace();
        if workspace is None:
            return Menu("Window", [
                MenuItem("Next Window", self.switch_window, self._ks("window.next")),
            ]);
        items = [
            MenuItem("Next Window", self.switch_window, self._ks("window.next")),
            MenuItem("Maximize / Restore", self.toggle_workspace_maximize, "F11", enabled=workspace.active_window is not None),
            MenuItem("Close current", self.close_workspace_window, "Ctrl+F4", enabled=workspace.active_window is not None),
            Separator(),
        ];
        for window in workspace.windows:
            label = window.title + ("" if window.visible else " (closed)");
            entries = [];
            if window.visible:
                entries.append(MenuItem("Activate", lambda selected=window: self.activate_workspace_window(selected), radio=lambda selected=window: workspace.active_window is selected));
                if window.maximizable:
                    entries.append(MenuItem("Restore" if window.maximized else "Maximize", lambda selected=window: self.toggle_workspace_maximize(selected), "F11"));
                if window.closable:
                    entries.append(MenuItem("Close", lambda selected=window: self.close_workspace_window(selected), "Ctrl+F4" if workspace.active_window is window else ""));
            else:
                entries.append(MenuItem("Open", lambda selected=window: self.activate_workspace_window(selected)));
            items.append(MenuItem(label, submenu=Menu(label, entries), radio=lambda selected=window: workspace.active_window is selected));
        return Menu("Window", items);

    def _load_document(self, path):
        if path is None:
            return TextDocument.empty();
        target = Path(path).expanduser();
        if not target.exists():
            return TextDocument.empty(target);
        return TextDocument.load(target, force_binary=self.force_binary);

    def _sync_document_markers(self):
        if self.document.eol == "CRLF":
            self.editor.line_end_marker = "⏎";
        elif self.document.eol == "CR":
            self.editor.line_end_marker = "↩";
        else:
            self.editor.line_end_marker = "↵";
        self.editor.line_end_markers = [_EOL_MARKERS.get(value, "↵") for value in (self.document.line_endings or [])];

    def _menus(self):
        eol = Menu("Line endings", [
            MenuItem("Preserve", action=lambda: self.set_eol("PRESERVE"), radio=lambda: self.document.eol == "MIXED"),
            MenuItem("Unix (LF)", action=lambda: self.set_eol("LF"), radio=lambda: self.document.eol == "LF"),
            MenuItem("Windows (CRLF)", action=lambda: self.set_eol("CRLF"), radio=lambda: self.document.eol == "CRLF"),
            MenuItem("Classic Mac (CR)", action=lambda: self.set_eol("CR"), radio=lambda: self.document.eol == "CR"),
        ]);
        tab_menu = Menu("Tab", [
            MenuItem("2", lambda: self.set_tab_width(2), radio=lambda: self.editor.tab_size == 2),
            MenuItem("4", lambda: self.set_tab_width(4), radio=lambda: self.editor.tab_size == 4),
            MenuItem("8", lambda: self.set_tab_width(8), radio=lambda: self.editor.tab_size == 8),
        ]);
        refresh_user_themes();
        theme_menu = Menu("Theme", [
            MenuItem(name, lambda selected=name: self.set_theme(selected), radio=lambda selected=name: self.app.theme.name.lower() == selected.lower())
            for name in available_theme_names() if name in THEMES
        ]);
        wrapping_menu = Menu("Line wrapping", [
            MenuItem("Auto (-1)", lambda: self.set_line_wrapping(-1), radio=lambda: self.editor.line_wrapping == -1),
            MenuItem("Off (0)", lambda: self.set_line_wrapping(0), radio=lambda: self.editor.line_wrapping == 0),
            Separator(),
            MenuItem("78 (legacy 80-col)", lambda: self.set_line_wrapping(78), radio=lambda: self.editor.line_wrapping == 78),
            MenuItem("80", lambda: self.set_line_wrapping(80), radio=lambda: self.editor.line_wrapping == 80),
            MenuItem("100", lambda: self.set_line_wrapping(100), radio=lambda: self.editor.line_wrapping == 100),
            MenuItem("120", lambda: self.set_line_wrapping(120), radio=lambda: self.editor.line_wrapping == 120),
            MenuItem("Custom...", self.line_wrapping_dialog),
        ]);
        breaking_menu = Menu("Line breaking", [
            MenuItem("Off (0)", lambda: self.set_line_breaking(0), radio=lambda: self.editor.line_breaking == 0),
            Separator(),
            MenuItem("78 (legacy 80-col)", lambda: self.set_line_breaking(78), radio=lambda: self.editor.line_breaking == 78),
            MenuItem("80", lambda: self.set_line_breaking(80), radio=lambda: self.editor.line_breaking == 80),
            MenuItem("100", lambda: self.set_line_breaking(100), radio=lambda: self.editor.line_breaking == 100),
            MenuItem("120", lambda: self.set_line_breaking(120), radio=lambda: self.editor.line_breaking == 120),
            MenuItem("Custom...", self.line_breaking_dialog),
        ]);
        syntax_menu = Menu("Syntax", [
            MenuItem(label, lambda selected=mode: self.set_syntax_mode(selected), radio=lambda selected=mode: self.editor.syntax.mode == selected)
            for mode, label in SYNTAX_MODES
        ]);
        return [
            Menu("File", [
                MenuItem("New", self.new_file, self._ks("file.new")),
                MenuItem("Open...", self.open_dialog, self._ks("file.open")),
                MenuItem("Save", self.save, self._ks("file.save")),
                MenuItem("Save As...", self.save_as_dialog),
                MenuItem("Reload", self.reload),
                Separator(),
                MenuItem("Line endings", submenu=eol),
                Separator(),
                MenuItem("Exit", self.quit, self._ks("app.exit")),
            ]),
            Menu("Edit", [
                MenuItem("Undo", self.editor_undo, self._ks("editor.undo")),
                MenuItem("Redo", self.editor_redo, self._ks("editor.redo")),
                Separator(),
                MenuItem("Cut", self.editor_cut, self._ks("editor.cut")),
                MenuItem("Copy", self.editor_copy, self._ks("editor.copy")),
                MenuItem("Paste", self.editor_paste, self._ks("editor.paste")),
                Separator(),
                MenuItem("Select All", self.editor_select_all, self._ks("editor.select_all")),
            ]),
            Menu("Search", [
                MenuItem("Find...", self.find_dialog, self._ks("search.find")),
                MenuItem("Find Next", self.find_next, self._ks("search.next")),
                MenuItem("Find Previous", self.find_previous, self._ks("search.previous")),
                Separator(),
                MenuItem("Search & Replace...", self.replace_dialog, self._ks("search.replace")),
                Separator(),
                MenuItem("Go to Line...", self.goto_line_dialog, self._ks("search.goto_line")),
            ]),
            Menu("View", [
                MenuItem("Syntax highlighting", self.toggle_syntax, checked=lambda: self.editor.syntax_highlighting),
                MenuItem("Syntax", submenu=syntax_menu),
                Separator(),
                MenuItem("Show spaces", self.toggle_spaces, checked=lambda: self.editor.show_spaces),
                MenuItem("Show tabs", self.toggle_tabs, checked=lambda: self.editor.show_tabs),
                MenuItem("Show line endings", self.toggle_eols, checked=lambda: self.editor.show_line_endings),
                MenuItem("Show control characters", self.toggle_controls, checked=lambda: self.editor.show_control_chars),
            ]),
            Menu("Options", [
                MenuItem("Tab", submenu=tab_menu),
                MenuItem("Theme", submenu=theme_menu),
                MenuItem("Line wrapping", submenu=wrapping_menu),
                MenuItem("Line breaking", submenu=breaking_menu),
                Separator(),
                MenuItem("Keyboard shortcuts...", self.shortcuts_dialog),
                MenuItem("Save configuration", self.save_config),
            ]),
            self._window_menu(),
            Menu("Help", [
                MenuItem("Editor Help", self.help, self._ks("help.editor")),
                Separator(),
                MenuItem("About...", self.about),
            ]),
        ];

    def open_menu(self, index=None):
        self.menu.menus = self._menus();
        if index is None:
            index = self.menu.menu_index;
        self.menu.open(index);
        self.app.focus.set(self.menu);
        self.app.invalidate();
        return True;

    def _menu_closed(self):
        self.app.focus.set(self.editor);
        self.app.invalidate();
        return True;

    def _editor_changed(self, _editor):
        self._update_status();
        return True;

    def _cursor_changed(self, _editor):
        self._update_status();
        return True;

    def _eol_label(self):
        if self.document.eol == "MIXED":
            return "MIXED";
        return self.document.eol;

    def _update_status(self, message=None):
        name = self.document.path.name if self.document.path is not None else "Untitled";
        marker = "*" if self.editor.modified else "";
        selected = "  Sel {}".format(self.editor.selection_length) if self.editor.has_selection else "";
        confidence = "?" if self.document.encoding_confidence < 0.65 else "";
        if self.editor.line_wrapping < 0:
            wrap_label = "AUTO";
        elif self.editor.line_wrapping == 0:
            wrap_label = "OFF";
        else:
            wrap_label = str(self.editor.line_wrapping);
        break_label = "OFF" if self.editor.line_breaking == 0 else str(self.editor.line_breaking);
        text = "{}{}  Ln {} Col {}{}  {}{}  {}  {}  Tab:{}  Wrap:{}  Break:{}  {}".format(
            name, marker, self.editor.cursor_line, self.editor.cursor_column, selected,
            self.document.encoding_label, confidence, self._eol_label(), self.editor.syntax_name, self.editor.tab_size, wrap_label, break_label, self.app.theme.name);
        if message:
            text += "  |  " + str(message);
        self.status.set(text);
        self.app.invalidate();
        return text;

    def _set_document(self, document):
        self.document = document;
        self.editor.set_text(document.text, modified=False);
        self.editor.configure_syntax(filename=document.path.name if document.path is not None else None);
        self._sync_document_markers();
        self.panel.title = document.path.name if document.path is not None else "Untitled";
        self.app.focus.set(self.editor);
        self._update_status("Loaded");
        return True;

    def new_file(self):
        return self._set_document(TextDocument.empty());

    def open_dialog(self):
        start = self.document.path.parent if self.document.path is not None else Path.cwd();
        def close():
            self.app.pop_modal();
            self.app.focus.set(self.editor);
            self.app.invalidate();
        def accepted(path):
            try:
                doc = TextDocument.load(path, force_binary=self.force_binary);
                close();
                self._set_document(doc);
            except Exception as exc:
                close();
                self._update_status("Open error: {}".format(exc));
        dialog = FileDialog(path=start, title="Open text file", on_accept=accepted, on_cancel=close, theme=self.app.theme);
        self.app.push_modal(dialog);
        self.app.invalidate();
        return True;

    def save_as_dialog(self):
        default = str(self.document.path or Path.cwd() / "untitled.txt");
        entry = TextInput(default);
        def close():
            self.app.pop_modal();
            self.app.focus.set(self.editor);
            self.app.invalidate();
        def accepted(*_args):
            self.document.path = Path(entry.value).expanduser();
            self.editor.configure_syntax(filename=self.document.path.name);
            close();
            self.save();
        body = VBox(entry, HBox(Button("Save", on_press=accepted, default=True), Button("Cancel", on_press=close), ratios=[1, 1]), sizes=[1, None]);
        self.app.push_modal(Dialog(body, title="Save As", width=72, height=7, on_cancel=close));
        self.app.focus.set(entry);
        self.app.invalidate();
        return True;

    def save(self):
        if self.document.path is None:
            return self.save_as_dialog();
        try:
            self.document.text = self.editor.text;
            self.document.save(text=self.editor.text);
            self.editor.mark_saved();
            self._update_status("Saved");
            return True;
        except Exception as exc:
            self._update_status("Save error: {}".format(exc));
            return False;

    def reload(self):
        if self.document.path is None:
            return False;
        try:
            return self._set_document(TextDocument.load(self.document.path, force_binary=self.force_binary));
        except Exception as exc:
            self._update_status("Reload error: {}".format(exc));
            return False;

    def set_eol(self, style):
        if style == "PRESERVE":
            if self.document.line_endings and len(set(self.document.line_endings)) > 1:
                self.document.eol = "MIXED";
            return self._update_status("Preserving original line endings");
        self.document.eol = style;
        self.document.preferred_eol = style;
        self.document.line_endings = [];
        self.editor.modified = True;
        self._sync_document_markers();
        self._update_status("EOL -> {}".format(style));
        return True;

    def _close_modal_to_editor(self):
        if self.app.modal_depth:
            self.app.pop_modal();
        self.app.focus.set(self.editor);
        self.app.invalidate();
        return True;

    def _search_pattern(self):
        if not self.search_query:
            return None;
        source = self.search_query if self.search_regex else re.escape(self.search_query);
        if self.search_whole_word:
            source = r"(?<!\w)(?:{})(?!\w)".format(source);
        flags = 0 if self.search_case_sensitive else re.IGNORECASE;
        try:
            return re.compile(source, flags);
        except re.error as exc:
            self._update_status("Search regex error: {}".format(exc));
            return None;

    def _set_search_options(self, query, case_sensitive, whole_word, regex, wrap):
        self.search_query = str(query);
        self.search_case_sensitive = bool(case_sensitive);
        self.search_whole_word = bool(whole_word);
        self.search_regex = bool(regex);
        self.search_wrap = bool(wrap);
        return True;

    def _select_match(self, match, label="Found"):
        if match is None:
            self._update_status("Text not found: {}".format(self.search_query));
            return False;
        self.editor.select_offsets(match.start(), match.end());
        self.app.focus.set(self.editor);
        self._update_status("{}: {}".format(label, self.search_query));
        return True;

    def find_next(self):
        pattern = self._search_pattern();
        if pattern is None:
            return self.find_dialog() if not self.search_query else False;
        text = self.editor.text;
        bounds = self.editor.selection_offsets();
        start = bounds[1] if bounds is not None else self.editor.cursor_offset;
        match = pattern.search(text, start);
        if match is None and self.search_wrap and start > 0:
            match = pattern.search(text, 0, start);
        return self._select_match(match);

    def find_previous(self):
        pattern = self._search_pattern();
        if pattern is None:
            return self.find_dialog() if not self.search_query else False;
        text = self.editor.text;
        bounds = self.editor.selection_offsets();
        end = bounds[0] if bounds is not None else self.editor.cursor_offset;
        matches = list(pattern.finditer(text, 0, end));
        match = matches[-1] if matches else None;
        if match is None and self.search_wrap and end < len(text):
            matches = list(pattern.finditer(text, end));
            match = matches[-1] if matches else None;
        return self._select_match(match);

    def _current_search_match(self):
        bounds = self.editor.selection_offsets();
        pattern = self._search_pattern();
        if bounds is None or pattern is None:
            return None;
        match = pattern.match(self.editor.text, bounds[0]);
        if match is None or match.span() != bounds:
            return None;
        return match;

    def replace_current(self):
        match = self._current_search_match();
        if match is None:
            found = self.find_next();
            if found:
                self._update_status("Match selected; use Replace again to change it");
            return found;
        replacement = match.expand(self.replace_text) if self.search_regex else self.replace_text;
        self.editor.replace_selection(replacement, kind="replace");
        self.find_next();
        return True;

    def replace_all(self):
        pattern = self._search_pattern();
        if pattern is None:
            return False;
        text = self.editor.text;
        try:
            if self.search_regex:
                changed, count = pattern.subn(self.replace_text, text);
            else:
                changed, count = pattern.subn(lambda _match: self.replace_text, text);
        except re.error as exc:
            self._update_status("Replace regex error: {}".format(exc));
            return False;
        if count <= 0:
            self._update_status("Text not found: {}".format(self.search_query));
            return False;
        self.editor.replace_offsets(0, len(text), changed, kind="replace_all");
        self._update_status("Replaced {} occurrence{}".format(count, "" if count == 1 else "s"));
        return True;

    def _search_options_widgets(self):
        case_box = CheckBox("Case sensitive", checked=self.search_case_sensitive);
        word_box = CheckBox("Whole word", checked=self.search_whole_word);
        regex_box = CheckBox("Regular expression", checked=self.search_regex);
        wrap_box = CheckBox("Wrap around", checked=self.search_wrap);
        return case_box, word_box, regex_box, wrap_box;

    def find_dialog(self):
        entry = TextInput(self.search_query, on_submit=lambda _value: accepted());
        case_box, word_box, regex_box, wrap_box = self._search_options_widgets();
        def close(*_args):
            return self._close_modal_to_editor();
        def accepted(*_args):
            self._set_search_options(entry.value, case_box.checked, word_box.checked, regex_box.checked, wrap_box.checked);
            close();
            return self.find_next();
        body = VBox(
            Label("Find:"), entry,
            case_box, word_box, regex_box, wrap_box,
            HBox(Button("Find", on_press=accepted, default=True), Button("Cancel", on_press=close), ratios=[1, 1]),
            sizes=[1, 1, 1, 1, 1, 1, None],
        );
        self.app.push_modal(Dialog(body, title="Find", width=70, height=13, on_cancel=close, shadow=True));
        self.app.focus.set(entry);
        self.app.invalidate();
        return True;

    def replace_dialog(self):
        find_entry = TextInput(self.search_query);
        replace_entry = TextInput(self.replace_text);
        case_box, word_box, regex_box, wrap_box = self._search_options_widgets();
        def close(*_args):
            return self._close_modal_to_editor();
        def save_options():
            self.replace_text = replace_entry.value;
            return self._set_search_options(find_entry.value, case_box.checked, word_box.checked, regex_box.checked, wrap_box.checked);
        def find_action(*_args):
            save_options();
            close();
            return self.find_next();
        def replace_action(*_args):
            save_options();
            close();
            return self.replace_current();
        def replace_all_action(*_args):
            save_options();
            close();
            return self.replace_all();
        body = VBox(
            Label("Find:"), find_entry,
            Label("Replace:"), replace_entry,
            case_box, word_box, regex_box, wrap_box,
            HBox(Button("Find Next", on_press=find_action), Button("Replace", on_press=replace_action, default=True), Button("Replace All", on_press=replace_all_action), Button("Cancel", on_press=close), ratios=[1, 1, 1, 1]),
            sizes=[1, 1, 1, 1, 1, 1, 1, 1, None],
        );
        self.app.push_modal(Dialog(body, title="Search & Replace", width=78, height=16, on_cancel=close, shadow=True));
        self.app.focus.set(find_entry);
        self.app.invalidate();
        return True;

    def goto_line_dialog(self):
        entry = TextInput(str(self.editor.cursor_line));
        def close(*_args):
            return self._close_modal_to_editor();
        def accepted(*_args):
            try:
                line = int(entry.value.strip());
            except ValueError:
                self._update_status("Invalid line number");
                return False;
            close();
            self.editor.goto_line(line);
            self._update_status("Line {}".format(self.editor.cursor_line));
            return True;
        entry.on_submit = lambda _value: accepted();
        body = VBox(Label("Line number:"), entry, HBox(Button("Go", on_press=accepted, default=True), Button("Cancel", on_press=close), ratios=[1, 1]), sizes=[1, 1, None]);
        self.app.push_modal(Dialog(body, title="Go to Line", width=48, height=8, on_cancel=close, shadow=True));
        self.app.focus.set(entry);
        self.app.invalidate();
        return True;

    def toggle_syntax(self):
        self.editor.syntax_highlighting = not self.editor.syntax_highlighting;
        self._update_status("Syntax highlighting {}".format("ON" if self.editor.syntax_highlighting else "OFF"));
        self.app.invalidate();
        return True;

    def set_syntax_mode(self, mode):
        selected = normalize_mode(mode);
        self.editor.configure_syntax(language=selected);
        self._update_status("Syntax -> {}".format(self.editor.syntax_name));
        self.app.invalidate();
        return True;

    def toggle_spaces(self):
        self.editor.show_spaces = not self.editor.show_spaces;
        self.app.invalidate();
        return True;

    def toggle_tabs(self):
        self.editor.show_tabs = not self.editor.show_tabs;
        self.app.invalidate();
        return True;

    def toggle_eols(self):
        self.editor.show_line_endings = not self.editor.show_line_endings;
        self.app.invalidate();
        return True;

    def toggle_controls(self):
        self.editor.show_control_chars = not self.editor.show_control_chars;
        self.app.invalidate();
        return True;

    def set_tab_width(self, width):
        self.editor.tab_size = int(width);
        self._update_status("Tab width {}".format(width));
        return True;

    def set_theme(self, name):
        self.app.set_theme(name);
        self._update_status("Theme -> {}".format(self.app.theme.name));
        self.app.invalidate();
        return True;

    def set_line_wrapping(self, value):
        value = int(value);
        self.editor.configure_wrapping(line_wrapping=value);
        if value < 0:
            label = "AUTO";
        elif value == 0:
            label = "OFF";
        else:
            label = str(value);
        self._update_status("Line wrapping -> {}".format(label));
        self.app.invalidate();
        return True;

    def set_line_breaking(self, value):
        value = max(0, int(value));
        self.editor.configure_wrapping(line_breaking=value);
        self._update_status("Line breaking -> {}".format("OFF" if value == 0 else value));
        self.app.invalidate();
        return True;

    def _numeric_option_dialog(self, title, current, on_accept, allow_auto=False):
        entry = TextInput(str(current));
        def close(*_args):
            return self._close_modal_to_editor();
        def accepted(*_args):
            try:
                value = int(entry.value.strip());
            except ValueError:
                self._update_status("Invalid numeric value");
                return False;
            if allow_auto:
                if value < -1:
                    self._update_status("Use -1 for Auto, 0 for Off, or a positive width");
                    return False;
            elif value < 0:
                self._update_status("Use 0 for Off or a positive width");
                return False;
            close();
            return on_accept(value);
        entry.on_submit = lambda _value: accepted();
        help_text = "-1 = Auto, 0 = Off, N = columns" if allow_auto else "0 = Off, N = columns";
        body = VBox(Label(help_text), entry, HBox(Button("Apply", on_press=accepted, default=True), Button("Cancel", on_press=close), ratios=[1, 1]), sizes=[1, 1, None]);
        self.app.push_modal(Dialog(body, title=title, width=58, height=9, on_cancel=close, shadow=True));
        self.app.focus.set(entry);
        self.app.invalidate();
        return True;

    def line_wrapping_dialog(self):
        return self._numeric_option_dialog("Line wrapping", self.editor.line_wrapping, self.set_line_wrapping, allow_auto=True);

    def line_breaking_dialog(self):
        return self._numeric_option_dialog("Line breaking", self.editor.line_breaking, self.set_line_breaking, allow_auto=False);

    def _shortcut_rows(self):
        rows = [];
        for name, label, bindings, _context in self.keys.rows(contexts=["editor"]):
            rows.append(("{:<24} {}".format(label, bindings or "(unassigned)"), name));
        return rows;

    def _capture_shortcut(self, action_name, mode, refresh):
        action = self.keys.actions.get(action_name);
        if action is None:
            return False;

        def cancel_capture(*_args):
            if self.app.modal_depth:
                self.app.pop_modal();
            self.app.invalidate();
            return True;

        def apply_key(spec):
            cancel_capture();
            conflicts = self.keys.conflicts(spec, action_name=action_name);

            def do_apply():
                if mode == "change":
                    self.keys.set_bindings(action_name, [spec]);
                else:
                    self.keys.add_binding(action_name, spec);
                refresh();
                self._update_status("{} -> {}".format(action.label, self.keys.display(action_name, all_keys=True)));
                return True;

            if not conflicts:
                return do_apply();

            conflict_names = ", ".join(item.label for item in conflicts);

            def close_conflict(*_args):
                if self.app.modal_depth:
                    self.app.pop_modal();
                self.app.invalidate();
                return True;

            def replace_conflict(*_args):
                for conflict in conflicts:
                    self.keys.remove_binding(conflict.name, spec);
                close_conflict();
                return do_apply();

            body = VBox(
                Label("{} is already assigned to:\n{}\n\nReplace that assignment?".format(format_key_spec(spec), conflict_names)),
                HBox(Button("Replace", on_press=replace_conflict, default=True), Button("Cancel", on_press=close_conflict), ratios=[1, 1]),
                sizes=[None, None],
            );
            self.app.push_modal(Dialog(body, title="Shortcut conflict", width=68, height=10, on_cancel=close_conflict, shadow=True));
            self.app.invalidate();
            return True;

        capture = _ShortcutCapture(apply_key, on_cancel=cancel_capture);
        body = VBox(
            Label("Action: {}\nCurrent: {}".format(action.label, self.keys.display(action_name, all_keys=True) or "(unassigned)")),
            capture,
            Label("Press Esc to cancel."),
            sizes=[2, 1, 1],
        );
        title = "Change shortcut" if mode == "change" else "Add shortcut";
        self.app.push_modal(Dialog(body, title=title, width=64, height=9, on_cancel=cancel_capture, shadow=True));
        self.app.focus.set(capture);
        self.app.invalidate();
        return True;

    def _remove_shortcut_dialog(self, action_name, refresh):
        action = self.keys.actions.get(action_name);
        if action is None:
            return False;
        bindings = list(self.keys.bindings_for(action_name));
        if not bindings:
            self._update_status("{} has no shortcuts".format(action.label));
            return False;
        choices = ListView([(format_key_spec(key), key) for key in bindings], title="Shortcut");

        def close(*_args):
            if self.app.modal_depth:
                self.app.pop_modal();
            self.app.invalidate();
            return True;

        def remove(*_args):
            key = choices.current_value;
            if key:
                self.keys.remove_binding(action_name, key);
                refresh();
                self._update_status("Removed {} from {}".format(format_key_spec(key), action.label));
            return close();

        body = VBox(
            Label("Remove a shortcut from {}:".format(action.label)),
            choices,
            HBox(Button("Remove", on_press=remove, default=True), Button("Cancel", on_press=close), ratios=[1, 1]),
            sizes=[1, None, None],
        );
        self.app.push_modal(Dialog(body, title="Remove shortcut", width=58, height=12, on_cancel=close, shadow=True));
        self.app.focus.set(choices);
        self.app.invalidate();
        return True;

    def shortcuts_dialog(self):
        listing = ListView(self._shortcut_rows(), title="Action / shortcuts");

        def refresh():
            current = listing.current_value;
            listing.set_rows([([label], value) for label, value in self._shortcut_rows()]);
            if current is not None:
                for index, row in enumerate(listing.rows):
                    if row.value == current:
                        listing.select(index);
                        break;
            self.app.invalidate();
            return True;

        def close(*_args):
            if self.app.modal_depth:
                self.app.pop_modal();
            self._refresh_key_surfaces();
            self.app.focus.set(self.editor);
            self.app.invalidate();
            return True;

        def change(*_args):
            return self._capture_shortcut(listing.current_value, "change", refresh);

        def add(*_args):
            return self._capture_shortcut(listing.current_value, "add", refresh);

        def remove(*_args):
            return self._remove_shortcut_dialog(listing.current_value, refresh);

        def defaults(*_args):
            self.keys.reset_all();
            refresh();
            self._update_status("Keyboard shortcuts restored to defaults");
            return True;

        body = VBox(
            Label("Select an action. Change replaces its shortcuts; Add keeps existing ones."),
            listing,
            HBox(Button("Change", on_press=change, default=True), Button("Add", on_press=add), Button("Remove", on_press=remove), Button("Defaults", on_press=defaults), Button("Close", on_press=close), ratios=[1, 1, 1, 1, 1]),
            sizes=[1, None, None],
        );
        self.app.push_modal(Dialog(body, title="Keyboard shortcuts", width=86, height=24, on_cancel=close, shadow=True));
        self.app.focus.set(listing);
        self.app.invalidate();
        return True;

    def save_config(self):
        data = {
            "theme": self.app.theme.name,
            "tab_size": int(self.editor.tab_size),
            "show_spaces": bool(self.editor.show_spaces),
            "show_tabs": bool(self.editor.show_tabs),
            "show_line_endings": bool(self.editor.show_line_endings),
            "show_control_chars": bool(self.editor.show_control_chars),
            "syntax_highlighting": bool(self.editor.syntax_highlighting),
            "syntax_mode": self.editor.syntax.mode,
            "line_wrapping": int(self.editor.line_wrapping),
            "line_breaking": int(self.editor.line_breaking),
            "keybindings": self.keys.overrides(),
        };
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True);
            temporary = self.config_path.with_name(self.config_path.name + ".tmp");
            temporary.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8");
            temporary.replace(self.config_path);
            self.config = data;
            self._update_status("Configuration saved: {}".format(self.config_path));
            return True;
        except OSError as exc:
            self._update_status("Config error: {}".format(exc));
            return False;

    def _show_text_dialog(self, title, text, width=76, height=22):
        view = TextView(text);
        def close(*_args):
            self.app.pop_modal();
            self.app.focus.set(self.editor);
            self.app.invalidate();
        body = VBox(view, Button("Close", on_press=close, default=True), sizes=[None, None]);
        dialog = Dialog(body, title=title, width=width, height=height, on_cancel=close, shadow=True);
        self.app.push_modal(dialog);
        self.app.focus.set(view);
        self.app.invalidate();
        return True;

    def editor_undo(self):
        return self.editor.undo();

    def editor_redo(self):
        return self.editor.redo();

    def editor_cut(self):
        return self.editor.cut();

    def editor_copy(self):
        return self.editor.copy();

    def editor_paste(self):
        return self.editor.paste();

    def editor_select_all(self):
        return self.editor.select_all();

    def help(self):
        shortcuts = "\n".join("  {:<24} {}".format(label, bindings or "(unassigned)") for _name, label, bindings, _context in self.keys.rows(contexts=["editor"]));
        return self._show_text_dialog("sumTUI edit Help", _HELP_TEXT + "\nCurrent shortcuts\n" + shortcuts + "\n");

    def about(self):
        text = """sumTUI edit
Version {}

A lightweight Unicode-aware plain-text editor built with sumTUI.

Features include selection, clipboard, undo/redo, search/replace, EOL and encoding awareness, hidden-character visualization, semantic syntax highlighting, soft line wrapping, optional hard line breaking, configurable tab width, themes and keyboard shortcuts.

Markdown is edited as source text. Rendered document preview / sumDOC integration is intentionally left for a future advanced editor.

License: GNU GPL v2 or later
Copyright 2018- William Martinez Bas <metfar@gmail.com>
""".format(__version__);
        return self._show_text_dialog("About sumTUI edit", text, width=70, height=16);

    def quit(self):
        self.app.stop();
        return True;

    def run(self):
        return self.app.run();


def install_edit_alias(directory=None):
    target = Path(directory or "~/bin").expanduser();
    target.mkdir(parents=True, exist_ok=True);
    path = target / "edit";
    path.write_text('#!/bin/bash\nexec python3 -m sumtui.tools.edit "$@"\n', encoding="utf-8");
    path.chmod(path.stat().st_mode | 0o111);
    print("Installed {}".format(path));
    return 0;


def main(argv=None):
    parser = argparse.ArgumentParser(prog="sumedit", description="Lightweight plain-text editor built with sumTUI");
    parser.add_argument("file", nargs="?", help="text file to edit");
    parser.add_argument("--theme", default=None, help="sumTUI theme (overrides saved editor configuration; default: saved theme or DOS)");
    parser.add_argument("--force", action="store_true", help="open binary-looking files as text");
    parser.add_argument("--install-alias", action="store_true", help="install ~/bin/edit wrapper using safe \"$@\" argument forwarding");
    args = parser.parse_args(argv);
    if args.install_alias:
        return install_edit_alias();
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        print("sumedit requires an interactive terminal", file=sys.stderr);
        return 2;
    try:
        return EditApp(args.file, theme=args.theme, force_binary=args.force).run();
    except Exception as exc:
        print("sumedit: {}".format(exc), file=sys.stderr);
        return 1;


if __name__ == "__main__":
    raise SystemExit(main());
