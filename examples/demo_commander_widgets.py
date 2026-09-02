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
import sys;
from pathlib import Path as _SumTUIBootstrapPath;

_SUMTUI_SRC = _SumTUIBootstrapPath(__file__).resolve().parents[1] / "src";
if str(_SUMTUI_SRC) not in sys.path:
    sys.path.insert(0, str(_SUMTUI_SRC));

import argparse;

from rich.console import Console;

from sumtui import Application, Button, CheckBox, Column, Dialog, FunctionBar, GroupBox, HBox, Label, Menu, MenuBar, MenuItem, Panel, Separator, Splitter, StatusBar, TableView, VBox;


def _panel(title):
    table = TableView([
        Column("Name", ratio=4),
        Column("Size", width=10, justify="right"),
        Column("Modify time", width=16),
    ]);
    table.add_row(["..", "UP--DIR", "Aug 25 14:55"]);
    table.add_row(["src", "4096", "Aug 25 13:20"]);
    table.add_row(["sumdoc-0.1.5.zip", "282533", "Aug 24 17:07"]);
    table.add_row(["README.md", "16018", "Jul 16 17:39"]);
    return Panel(table, title=title), table;


def build(theme="DOS"):
    app = Application(title="sumCommander widget shell", theme=theme);
    status = StatusBar("Hint: Tab changes the current panel. F9 opens menus. F10 quits.");
    left, left_table = _panel("Left: ~/dev/py");
    right, right_table = _panel("Right: ~/dev/py/sumdoc");
    split = Splitter(left, right, ratio=0.5);

    def close_dialog():
        app.pop_modal();

    def options():
        body = VBox(
            HBox(
                GroupBox(VBox(CheckBox("Verbose operation", True), CheckBox("Compute totals", True), CheckBox("Classic progressbar", True)), title="File operations"),
                GroupBox(VBox(CheckBox("Use internal view", True), CheckBox("Auto menus", False), CheckBox("Safe delete", False)), title="Other options"),
            ),
            HBox(Button("OK", on_press=close_dialog, default=True), Button("Cancel", on_press=close_dialog)),
            sizes=[None, 1],
        );
        app.push_modal(Dialog(body, title="Configure options", width=68, height=18, on_cancel=close_dialog));

    menu = MenuBar([
        Menu("Left", [MenuItem("File listing"), MenuItem("Quick view"), MenuItem("Info"), Separator(), MenuItem("Tree")]),
        Menu("File", [MenuItem("View", shortcut="F3"), MenuItem("Copy", shortcut="F5"), MenuItem("Quit", action=app.stop, shortcut="F10")]),
        Menu("Command", [MenuItem("Directory tree"), MenuItem("Find file"), MenuItem("View mode", submenu=Menu("View mode", [MenuItem("Text"), MenuItem("Hex + ASCII"), MenuItem("Markdown")]))]),
        Menu("Options", [MenuItem("Configuration", action=options), MenuItem("Classic progressbar", checked=True)]),
        Menu("Right", [MenuItem("File listing"), MenuItem("Quick view"), MenuItem("Info")]),
    ]);
    bar = FunctionBar([
        ("f1", "Help", lambda: status.set("sumCommander widget shell")),
        ("f2", "Menu", lambda: (app.focus.set(menu), menu.open())),
        ("f3", "View", lambda: status.set("View")),
        ("f5", "Copy", lambda: status.set("Copy")),
        ("f6", "RenMov", lambda: status.set("Rename/Move")),
        ("f7", "Mkdir", lambda: status.set("Mkdir")),
        ("f8", "Delete", lambda: status.set("Delete")),
        ("f9", "PullDn", lambda: (app.focus.set(menu), menu.open())),
        ("f10", "Quit", app.stop),
    ]);
    bar.install(app);
    app.set_root(VBox(menu, split, status, bar, sizes=[None, None, 1, 1]));
    return app;


def main():
    parser = argparse.ArgumentParser(description="sumTUI Commander widget integration demo");
    parser.add_argument("--theme", default="DOS");
    parser.add_argument("--snapshot", action="store_true");
    args = parser.parse_args();
    app = build(args.theme);
    if args.snapshot:
        Console(width=120, height=32).print(app._renderable());
        return 0;
    return app.run();


if __name__ == "__main__":
    raise SystemExit(main());
