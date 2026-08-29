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
import os;
import tempfile;

from rich.console import Console;

from sumtui import Application, BrowseForm, Button, CheckBox, Choice, Column, ContextMenu, Dialog, DirectoryDialog, FileDialog, FormField, FunctionBar, GroupBox, HBox, HexView, Label, ListView, MarkdownView, SyntaxView, Menu, MenuBar, MenuItem, Panel, ProgressBar, RadioButton, RadioGroup, RecordForm, ScrollBar, Separator, Slider, Splitter, StatusBar, TableView, TextInput, TextView, TreeNode, TreeView, VBox;


def _app(title, widget, theme="RAR", height=None):
    app = Application(title=title, theme=theme);
    if height is not None:
        widget = Panel(widget, title=title);
    app.set_root(widget);
    app.bind("f10", app.stop);
    return app;


def build(name, theme="RAR"):
    name = str(name).lower();
    if name == "label":
        return _app("Label", VBox(Label("Normal label"), Label("Title label", style="title")), theme);
    if name == "panel":
        return _app("Panel", Panel(Label("Panel content"), title="Panel", subtitle="F10 Quit"), theme);
    if name == "groupbox":
        return _app("GroupBox", GroupBox(VBox(CheckBox("First", True), CheckBox("Second", False)), title="Options"), theme);
    if name == "statusbar":
        return _app("StatusBar", VBox(Panel(TextView("Status bar stays at the bottom."), title="Main"), StatusBar("READY."), sizes=[None, 1]), theme);
    if name == "button":
        status = StatusBar("Buttons are 24x3 cells; Tab moves focus; Enter/Space presses");
        first = Button("One", width=24, height=3, on_press=lambda: status.set("One pressed"));
        second = Button("Two", width=24, height=3, on_press=lambda: status.set("Two pressed"));
        return _app("Button", VBox(first, second, status, sizes=[None, None, 1]), theme);
    if name == "textinput":
        return _app("TextInput", VBox(Label("Edit with arrows, Home/End and Backspace"), TextInput("sumTUI", width=40)), theme);
    if name == "checkbox":
        return _app("CheckBox", VBox(CheckBox("Classic progress bar", True), CheckBox("Follow symlinks", False), CheckBox("Safe delete", True)), theme);
    if name == "radiobutton":
        standalone = RadioButton("Standalone primitive", value="standalone", checked=True);
        return _app("RadioButton", VBox(Label("RadioButton is the individual control."), standalone, Label("Use RadioGroup for mutual exclusion and arrow navigation.")), theme);
    if name == "radiogroup":
        group = RadioGroup([("Text", "text"), ("Hex + ASCII", "hex"), ("Markdown", "md")], value="text");
        return _app("RadioGroup", GroupBox(group, title="Mutually exclusive view mode"), theme);
    if name == "choice":
        return _app("Choice", Choice([("Maximum", 5), ("Normal", 3), ("Store", 0)], value=5, width=24), theme);
    if name == "combobox":
        return _app("ComboBox", Choice([("UTF-8", "utf8"), ("Latin-1", "latin1"), ("ASCII", "ascii")], value="utf8", width=24), theme);
    if name == "slider":
        progress = ProgressBar(50, maximum=100, label="Progress", width=50);
        slider = Slider(0, 100, 50, step=5, label="Slider", width=50, on_change=lambda _w, value: progress.set(value));
        return _app("Slider + ProgressBar", VBox(slider, progress), theme);
    if name == "progressbar":
        return _app("ProgressBar", VBox(ProgressBar(25, label="Copy", width=50), ProgressBar(73, label="Extract", width=50)), theme);
    if name == "tableview":
        table = TableView([Column("Name", ratio=3), Column("Size", width=10, justify="right"), Column("Type", width=12)]);
        table.add_row(["src", "", "Directory"]); table.add_row(["README.md", "12 KiB", "Markdown"]); table.add_row(["archive.rar", "2.4 GiB", "RAR"]);
        return _app("TableView", table, theme);
    if name == "browseform":
        form = BrowseForm(["id", "name", "balance"], [[1, "Ana", "12.50"], [2, "Luis", "7.25"], [3, "Bea", "31.00"]]);
        return _app("BrowseForm", Panel(form, title="customers"), theme);
    if name == "recordform":
        form = RecordForm([
            FormField("id", value="<auto>", width=8, readonly=True),
            FormField("name", width=20, max_length=20, mask="X" * 20),
            FormField("amount", width=7, max_length=7, mask="9990.00"),
            FormField("active", kind="logical", value=True),
        ]);
        return _app("RecordForm", Panel(form, title="Append: customers"), theme);
    if name == "listview":
        return _app("ListView", ListView([("View", "view"), ("Copy", "copy"), ("Move", "move"), ("Delete", "delete")], title="Command"), theme);
    if name == "treeview":
        root = TreeNode("/"); home = root.add(TreeNode("home")); home.add(TreeNode("wmartinez")); root.add(TreeNode("mnt")); root.expanded = True; home.expanded = True;
        return _app("TreeView", TreeView([root]), theme);
    if name == "textview":
        text = "Text viewer\n\nUp/Down scroll vertically.\nLeft/Right scroll horizontally.\nShift+Left/Right scroll a horizontal page.\nCtrl+Left/Right jump to the horizontal edge.\n\n0123456789 " * 12;
        return _app("TextView", TextView(text), theme);
    if name == "markdownview":
        return _app("MarkdownView", MarkdownView("# sumTUI\n\n**Markdown** rendered with styles preserved.\n\n- Text\n- Lists\n- `inline code`\n\n```python\ndef hello():\n    print('sumTUI')\n```", code_theme="vim"), theme);
    if name == "syntaxview":
        code = "#!/usr/bin/env python3\n\ndef hello(name):\n    # Pygments detects syntax from the filename and long source lines can scroll horizontally.\n    print(f'Hello {name} -- this deliberately long line demonstrates the horizontal source viewport without truncating the code.')\n";
        return _app("SyntaxView", SyntaxView(code, filename="demo.py", syntax_theme="vim", line_numbers=True), theme);
    if name == "hexview":
        data = b"Rar!\\x1a\\x07\\x01\\x00sumTUI hex viewer\\x00" + bytes(range(64));
        return _app("HexView", HexView(data=data, bytes_per_row=16), theme);
    if name == "scrollbar":
        return _app("ScrollBar", HBox(ScrollBar(35, maximum=100, page=20, orientation="vertical", interactive=True), TextView("Standalone interactive scrollbar\nUse arrows, PgUp/PgDn, Home/End."), sizes=[2, None]), theme);
    if name == "splitter":
        splitter = Splitter(Panel(TextView("Left panel"), title="Left"), Panel(TextView("Right panel"), title="Right"), ratio=0.5);
        return _app("Splitter", splitter, theme);
    if name == "menubar":
        status = StatusBar("F9 opens the menu; arrows navigate; Enter selects");
        menus = [Menu("Left", [MenuItem("File listing", lambda: status.set("File listing")), MenuItem("Quick view", lambda: status.set("Quick view")), Separator(), MenuItem("Encoding", submenu=Menu("Encoding", [MenuItem("UTF-8", lambda: status.set("UTF-8")), MenuItem("Latin-1", lambda: status.set("Latin-1"))]))]), Menu("File", [MenuItem("View", lambda: status.set("View"), "F3"), MenuItem("Quit", None, "F10")]), Menu("Options", [MenuItem("Classic progressbar", lambda: status.set("Toggle"), checked=True)])];
        bar = MenuBar(menus);
        app = _app("MenuBar", VBox(bar, Panel(TextView("Multi-level drop-down menu"), title="Demo"), status, sizes=[None, None, 1]), theme);
        app.bind("f9", lambda: (app.focus.set(bar), bar.open()));
        return app;
    if name == "contextmenu":
        menu = ContextMenu([MenuItem("View"), MenuItem("Copy"), MenuItem("Move"), Separator(), MenuItem("Delete")], title="Context");
        return _app("ContextMenu", menu, theme);
    if name == "dialog":
        app = Application(title="Dialog", theme=theme); status = StatusBar("F2 opens dialog; F11 maximizes/restores it"); base = VBox(Panel(TextView("The base remains visible behind the modal."), title="Main"), status, sizes=[None, 1]); app.set_root(base);
        def close(): app.pop_modal();
        def show(): app.push_modal(Dialog(VBox(Label("Real modal compositing"), Label("F11 Maximize / Restore"), Button("Close", on_press=close)), title="Dialog", width=44, height=10, on_cancel=close, maximizable=True));
        app.bind("f2", show); app.bind("f10", app.stop); return app;
    if name == "functionbar":
        status = StatusBar("FunctionBar installs key bindings"); app = Application(title="FunctionBar", theme=theme); bar = FunctionBar([("f1", "Help", lambda: status.set("Help")), ("f3", "View", lambda: status.set("View")), ("f10", "Quit", app.stop)]); bar.install(app); app.set_root(VBox(Panel(TextView("Press F1/F3/F10"), title="FunctionBar"), bar, status, sizes=[None, 1, 1])); return app;
    if name == "layout":
        return _app("HBox / VBox", VBox(HBox(Panel(Label("A"), title="A"), Panel(Label("B"), title="B")), StatusBar("HBox nested inside VBox"), sizes=[None, 1]), theme);
    if name == "filedialog":
        app = Application(title="FileDialog", theme=theme); dialog = FileDialog(path=".", on_accept=lambda path: app.stop(), on_cancel=app.stop, theme=app.theme); app.set_root(dialog); return app;
    if name == "directorydialog":
        app = Application(title="DirectoryDialog", theme=theme); dialog = DirectoryDialog(path=".", on_accept=lambda path: app.stop(), on_cancel=app.stop, theme=app.theme); app.set_root(dialog); return app;
    raise ValueError("unknown demo: {}".format(name));


def run(name):
    parser = argparse.ArgumentParser(description="sumTUI {} demo".format(name));
    parser.add_argument("--theme", default="RAR");
    parser.add_argument("--snapshot", action="store_true");
    args = parser.parse_args();
    app = build(name, args.theme);
    if args.snapshot:
        Console(width=100, height=30).print(app._renderable());
        return 0;
    return app.run();
