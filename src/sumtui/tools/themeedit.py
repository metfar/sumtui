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
import sys;
from pathlib import Path;

from rich.text import Text;

from .. import __version__;
from ..app import Application;
from ..theme import BUILTIN_THEME_NAMES, THEME_EDIT_ROLES, THEMES, available_theme_names, refresh_user_themes, save_user_theme, user_theme_dir;
from ..widgets import Button, Dialog, FunctionBar, HBox, Label, ListView, Menu, MenuBar, MenuDesktop, MenuItem, Panel, Separator, StatusBar, TextInput, VBox, Widget;


class ThemePreview(Widget):
    def __rich_console__(self, console, options):
        lines = [];
        title = Text("sumTUI theme preview", style=self.theme.style("title"));
        lines.append(title);
        lines.append(Text("Menu  Dialog  Buttons  Editor  Syntax", style=self.theme.style("menu_bar")));
        source = Text();
        source.append("IF ", style=self.theme.style("syntax_keyword"));
        source.append("total", style=self.theme.style("syntax_variable"));
        source.append(" >= ", style=self.theme.style("syntax_operator"));
        source.append("1000", style=self.theme.style("syntax_number"));
        source.append(" THEN ", style=self.theme.style("syntax_keyword"));
        source.append("PRINT", style=self.theme.style("syntax_builtin"));
        source.append(" ");
        source.append('"Total"', style=self.theme.style("syntax_string"));
        source.append("  # comment", style=self.theme.style("syntax_comment"));
        lines.append(source);
        markdown = Text();
        markdown.append("# Heading", style=self.theme.style("syntax_heading"));
        markdown.append("  **strong**", style=self.theme.style("syntax_strong"));
        markdown.append("  `code`", style=self.theme.style("syntax_markup"));
        lines.append(markdown);
        lines.append(Text(" 28 ", style=self.theme.style("editor_gutter")) + Text("line number gutter and editor text", style=self.theme.style("viewer")));
        lines.append(Text("[ Button ]", style=self.theme.style("button_control")) + Text("  ") + Text(" selected ", style=self.theme.style("selection")));
        lines.append(Text("Status / hints", style=self.theme.style("status")));
        width = max(1, options.max_width);
        height = max(1, options.height or options.max_height or len(lines));
        for index in range(height):
            line = lines[index] if index < len(lines) else Text("");
            line = line.copy();
            line.pad_right(max(0, width - line.cell_len));
            yield line;
            if index + 1 < height:
                yield "\n";


class ThemeEditorApp:
    def __init__(self, theme=None):
        refresh_user_themes();
        selected = theme if theme in THEMES else ("Ralesk's MC" if "Ralesk's MC" in THEMES else next(iter(THEMES)));
        self.app = Application("sumTUI Theme Editor", theme=selected, capture_control_keys=True, mouse=True);
        self.current_name = selected;
        self.status = StatusBar("");
        self.preview = ThemePreview();
        self.theme_list = ListView([], title="Themes", on_change=self._theme_changed, on_activate=lambda *_args: self._focus_roles());
        self.role_list = ListView([], title="Semantic roles", on_activate=self._edit_role);
        self.menu = MenuBar([], on_close=self._close_menu, activation_key="f9");
        self.bar = FunctionBar([
            ("f2", "Save", self.save),
            ("f4", "Clone", self.clone_dialog),
            ("f9", "Menu", self.open_menu),
            ("f10", "Exit", self.quit),
        ]);
        self._build_menu();
        self._reload_theme_list();
        self._reload_roles();
        body = HBox(Panel(self.theme_list, title="Themes"), Panel(self.role_list, title="Roles"), Panel(self.preview, title="Preview"), ratios=[2, 3, 5]);
        root = VBox(body, self.status, self.bar, sizes=[None, 1, 1]);
        self.app.set_root(MenuDesktop(self.menu, root));
        self.bar.install(self.app);
        self.app.bind("f9", self.open_menu);
        self.app.bind("f10", self.quit);
        self.app.bind("f2", self.save);
        self.app.bind("f4", self.clone_dialog);
        self.app.focus.set(self.theme_list);
        self._update_status();

    def _build_menu(self):
        self.menu.menus = [
            Menu("File", [
                MenuItem("Clone theme...", self.clone_dialog, "F4"),
                MenuItem("Save", self.save, "F2"),
                MenuItem("Delete user theme", self.delete_current),
                Separator(),
                MenuItem("Exit", self.quit, "F10"),
            ]),
            Menu("Theme", [
                MenuItem("Edit selected role...", self.edit_current_role, "Enter"),
                MenuItem("Reset selected role", self.reset_current_role),
                MenuItem("Reload user themes", self.reload_themes),
            ]),
            Menu("Preview", [
                MenuItem("Apply selected theme", self.apply_current),
            ]),
            Menu("Help", [
                MenuItem("About...", self.about),
            ]),
        ];

    def _reload_theme_list(self):
        self.theme_list.clear();
        names = available_theme_names();
        for name in names:
            suffix = " [built-in]" if name in BUILTIN_THEME_NAMES else " [user]";
            self.theme_list.add_item(name + suffix, value=name);
        if self.current_name in names:
            self.theme_list.select(names.index(self.current_name));
        return True;

    def _reload_roles(self):
        self.role_list.clear();
        theme = THEMES[self.current_name];
        for role in THEME_EDIT_ROLES:
            self.role_list.add_item("{:<24} {}".format(role, theme.style(role)), value=role);
        return True;

    def _theme_changed(self, value, _row):
        if value not in THEMES:
            return False;
        self.current_name = value;
        self.app.set_theme(THEMES[value]);
        self._reload_roles();
        self._update_status();
        self.app.invalidate();
        return True;

    def _focus_roles(self):
        self.app.focus.set(self.role_list);
        return True;

    def _update_status(self, message=None):
        kind = "built-in/read-only" if self.current_name in BUILTIN_THEME_NAMES else "user/editable";
        text = message or "{}  {}  {}".format(self.current_name, kind, user_theme_dir());
        self.status.set(text);
        return True;

    def open_menu(self):
        self.menu.open(self.menu.menu_index);
        self.app.focus.set(self.menu);
        self.app.invalidate();
        return True;

    def _close_menu(self):
        self.app.focus.set(self.theme_list);
        self.app.invalidate();
        return True;

    def _close_modal(self, focus=None):
        self.app.pop_modal();
        self.app.focus.set(focus or self.role_list);
        self.app.invalidate();
        return True;

    def _message(self, title, text):
        def close(*_args):
            return self._close_modal(self.theme_list);
        body = VBox(Label(text), Button("OK", on_press=close, default=True), sizes=[None, None]);
        self.app.push_modal(Dialog(body, title=title, width=70, height=10, on_cancel=close, shadow=True));
        return True;

    def clone_dialog(self):
        entry = TextInput("{} Copy".format(self.current_name), width=42);
        def close(*_args):
            return self._close_modal(self.theme_list);
        def accept(*_args):
            name = entry.value.strip();
            if not name:
                return False;
            if name in BUILTIN_THEME_NAMES:
                self._update_status("Choose a different name; built-in themes are read-only");
                return False;
            source = THEMES[self.current_name];
            clone = source.copy(name=name);
            THEMES[name] = clone;
            self.current_name = name;
            path = save_user_theme(clone);
            close();
            self._reload_theme_list();
            self._reload_roles();
            self.app.set_theme(clone);
            self._update_status("Cloned -> {}".format(path));
            return True;
        body = VBox(Label("New theme name:"), entry, HBox(Button("Clone", on_press=accept, default=True), Button("Cancel", on_press=close)), sizes=[1, 1, None]);
        self.app.push_modal(Dialog(body, title="Clone theme", width=58, height=9, on_cancel=close, shadow=True));
        self.app.focus.set(entry);
        return True;

    def _ensure_editable(self):
        if self.current_name in BUILTIN_THEME_NAMES:
            self._message("Built-in theme", "Built-in themes are read-only. Use Theme > Clone theme... first.");
            return False;
        return True;

    def _edit_role(self, role, _row=None):
        if not self._ensure_editable():
            return False;
        theme = THEMES[self.current_name];
        entry = TextInput(theme.style(role), width=62);
        def close(*_args):
            return self._close_modal(self.role_list);
        def accept(*_args):
            style = entry.value.strip();
            overrides = dict(tuple(theme.style_overrides or ()));
            if style:
                overrides[str(role)] = style;
            else:
                overrides.pop(str(role), None);
            updated = theme.copy(style_overrides=tuple(overrides.items()));
            THEMES[self.current_name] = updated;
            self.app.set_theme(updated);
            close();
            self._reload_roles();
            self._update_status("{} -> {}".format(role, updated.style(role)));
            return True;
        body = VBox(
            Label("Role: {}".format(role)),
            Label("Rich style (examples: bold #f4d432, #c0c0c0 on #111144):"),
            entry,
            HBox(Button("Apply", on_press=accept, default=True), Button("Cancel", on_press=close)),
            sizes=[1, 1, 1, None],
        );
        self.app.push_modal(Dialog(body, title="Edit role", width=78, height=11, on_cancel=close, shadow=True));
        self.app.focus.set(entry);
        return True;

    def edit_current_role(self):
        role = self.role_list.current_value;
        if role is None:
            return False;
        return self._edit_role(role);

    def reset_current_role(self):
        if not self._ensure_editable():
            return False;
        role = self.role_list.current_value;
        if role is None:
            return False;
        theme = THEMES[self.current_name];
        overrides = dict(tuple(theme.style_overrides or ()));
        overrides.pop(str(role), None);
        updated = theme.copy(style_overrides=tuple(overrides.items()));
        THEMES[self.current_name] = updated;
        self.app.set_theme(updated);
        self._reload_roles();
        self._update_status("Reset role {}".format(role));
        self.app.invalidate();
        return True;

    def save(self):
        if not self._ensure_editable():
            return False;
        path = save_user_theme(THEMES[self.current_name]);
        self._update_status("Saved {}".format(path));
        self.app.invalidate();
        return True;

    def delete_current(self):
        if self.current_name in BUILTIN_THEME_NAMES:
            return self._message("Built-in theme", "Built-in themes cannot be deleted.");
        directory = user_theme_dir();
        removed = False;
        for path in directory.glob("*.json") if directory.exists() else []:
            try:
                import json;
                data = json.loads(path.read_text(encoding="utf-8"));
                if str(data.get("name", "")).casefold() == self.current_name.casefold():
                    path.unlink();
                    removed = True;
            except (OSError, ValueError, TypeError):
                continue;
        old = self.current_name;
        refresh_user_themes();
        self.current_name = "Ralesk's MC" if "Ralesk's MC" in THEMES else next(iter(THEMES));
        self.app.set_theme(THEMES[self.current_name]);
        self._reload_theme_list();
        self._reload_roles();
        self._update_status("Deleted {}".format(old) if removed else "No saved file found for {}".format(old));
        self.app.invalidate();
        return True;

    def reload_themes(self):
        refresh_user_themes();
        if self.current_name not in THEMES:
            self.current_name = "Ralesk's MC" if "Ralesk's MC" in THEMES else next(iter(THEMES));
        self.app.set_theme(THEMES[self.current_name]);
        self._reload_theme_list();
        self._reload_roles();
        self._update_status("User themes reloaded");
        self.app.invalidate();
        return True;

    def apply_current(self):
        self.app.set_theme(THEMES[self.current_name]);
        self._update_status("Previewing {}".format(self.current_name));
        self.app.invalidate();
        return True;

    def about(self):
        return self._message("About sumtheme", "sumtheme {}\n\nInteractive theme editor for sumTUI.\nBuilt-in themes are read-only; clone one to create a user theme.\nUser themes live in {}.\n\nGNU GPL v2 or later.".format(__version__, user_theme_dir()));

    def quit(self):
        self.app.stop();
        return True;

    def run(self):
        return self.app.run();


def main(argv=None):
    parser = argparse.ArgumentParser(prog="sumtheme", description="Interactive sumTUI theme editor");
    parser.add_argument("--theme", default=None, help="theme to preview initially");
    parser.add_argument("--list", action="store_true", help="list built-in and user themes and exit");
    parser.add_argument("--dir", action="store_true", help="print the user theme directory and exit");
    args = parser.parse_args(argv);
    refresh_user_themes();
    if args.dir:
        print(user_theme_dir());
        return 0;
    if args.list:
        for name in available_theme_names():
            print("{}\t{}".format(name, "built-in" if name in BUILTIN_THEME_NAMES else "user"));
        return 0;
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        print("sumtheme requires an interactive terminal (use --list for non-interactive use)", file=sys.stderr);
        return 2;
    return ThemeEditorApp(theme=args.theme).run();


if __name__ == "__main__":
    raise SystemExit(main());
