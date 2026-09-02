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
import datetime;
import os;
import shlex;
from pathlib import Path;

from rich.console import Console;

from sumtui import Application, Button, CheckBox, Choice, Column, Dialog, FunctionBar, HBox, HexView, Label, Panel, RadioGroup, StatusBar, SyntaxView, TableRow, TableView, TextInput, TextView, VBox, __version__;


class RarBrowserDemo:
    def __init__(self, path=".", theme="DOS"):
        self.path = Path(path).expanduser().resolve();
        self.app = Application(title="sumTUI RAR-style browser", theme=theme);
        self.status = StatusBar("Ready");
        self.info = Label("");
        self.table = TableView([
            Column("Name", ratio=4),
            Column("Size", width=11, justify="right"),
            Column("Date", width=10),
            Column("Time", width=8),
        ], on_change=self._selection_changed, on_activate=self._activate);
        self.left = Panel(self.table, title=str(self.path));
        self.right = Panel(self.info, title="sumTUI");
        self.body = HBox(self.left, self.right, ratios=[3, 1]);
        self.functions = FunctionBar([
            ("f1", "Help", self.help),
            ("f2", "Add", self.add_dialog),
            ("f3", "View", self.view),
            ("f4", "Fresh", self.refresh),
            ("f5", "Extract", self.extract_dialog),
            ("f9", "Theme", self.cycle_theme),
            ("f10", "Quit", self.app.stop),
        ]);
        self.root = VBox(self.body, self.functions, self.status, sizes=[None, 1, 1]);
        self.app.set_root(self.root);
        self.functions.install(self.app);
        self.app.bind("backspace", self.go_up);
        self.themes = ["DOS", "ZX", "XBASE", "C64", "Dark", "Light"];
        self.theme_index = self.themes.index(self.app.theme.name) if self.app.theme.name in self.themes else 0;
        self.refresh();

    def _rows(self):
        rows = [];
        if self.path.parent != self.path:
            rows.append(TableRow(("..", "<DIR>", "", ""), value=self.path.parent));
        entries = sorted(os.scandir(self.path), key=lambda entry: (not entry.is_dir(follow_symlinks=False), entry.name.lower()));
        for entry in entries:
            try:
                stat = entry.stat(follow_symlinks=False);
            except OSError:
                continue;
            stamp = datetime.datetime.fromtimestamp(stat.st_mtime);
            if entry.is_symlink():
                kind = "<LINK>";
            elif entry.is_dir(follow_symlinks=False):
                kind = "<DIR>";
            else:
                kind = format_size(stat.st_size);
            rows.append(TableRow((entry.name, kind, stamp.strftime("%Y-%m-%d"), stamp.strftime("%H:%M:%S")), value=Path(entry.path)));
        return rows;

    def refresh(self):
        try:
            self.table.set_rows(self._rows());
            self.left.title = str(self.path);
            self.status.set("{} entries".format(len(self.table.rows)));
            self._selection_changed(self.table.current_value, self.table.current_row);
        except OSError as exc:
            self.status.set("Error: {}".format(exc));
        return True;

    def _selection_changed(self, value, row):
        if value is None:
            self.info.set_text("sumTUI {}\n\nNo selection".format(__version__));
            return None;
        path = Path(value);
        lines = ["sumTUI {}".format(__version__), "Rich renderer", "Portable input", "", path.name or str(path)];
        try:
            if path.is_symlink():
                lines.extend(["", "Symbolic link", "Target:", os.readlink(path)]);
            elif path.is_dir():
                lines.extend(["", "Directory"]);
            else:
                stat = path.stat();
                lines.extend(["", "File", "Size: {}".format(format_size(stat.st_size))]);
        except OSError as exc:
            lines.extend(["", "Error: {}".format(exc)]);
        self.info.set_text("\n".join(lines));
        return None;

    def _activate(self, value, row):
        if value is None:
            return None;
        path = Path(value);
        if path.is_dir():
            self.path = path.resolve();
            self.refresh();
        else:
            self.view();
        return None;

    def go_up(self):
        if self.path.parent != self.path:
            self.path = self.path.parent;
            self.refresh();
        return True;

    def help(self):
        self.status.set("Arrows/PgUp/PgDn navigate; Enter opens; Backspace up; F2 Add; F5 Extract; F10 quits");
        return True;

    def _field(self, label, control, width=19):
        return HBox(Label(label), control, sizes=[width, None]);

    def add_dialog(self):
        current = self.table.current_value;
        source = Path(current) if current is not None else self.path;
        default_name = "{}.rar".format(source.name) if source.name else "archive.rar";
        archive = TextInput(default_name, width=40);
        fmt = Choice([("RAR5", "5"), ("RAR4", "4")], value="5", width=16);
        compression = Choice([
            ("0 - Store", 0), ("1 - Fastest", 1), ("2 - Fast", 2),
            ("3 - Normal", 3), ("4 - Good", 4), ("5 - Maximum", 5),
        ], value=5, width=22);
        solid = CheckBox("Solid archive (-s)", checked=True);
        links = CheckBox("Preserve symbolic/hard links (-sn)", checked=True);
        portable = CheckBox("Portable link manifest", checked=True);
        restore = RadioGroup([
            ("Recreate symbolic links", "links"),
            ("Materialize copies", "copies"),
            ("Links, materialize on failure", "auto"),
        ], value="auto");
        preview = TextView("");

        def command():
            args = ["rar", "a", "-ma{}".format(fmt.value), "-m{}".format(compression.value)];
            if solid.checked:
                args.append("-s");
            if links.checked:
                args.append("-sn");
            args.extend([archive.value, str(source)]);
            return " ".join(shlex.quote(item) for item in args);

        def update(*_args):
            extra = "portable={} restore={}".format("yes" if portable.checked else "no", restore.value);
            preview.set_text("Command preview:\n{}\n{}".format(command(), extra));
            return True;

        archive.on_change = update;
        fmt.on_change = update;
        compression.on_change = update;
        solid.on_change = update;
        links.on_change = update;
        portable.on_change = update;
        restore.on_change = update;

        def cancel():
            self.app.pop_modal();
            self.status.set("Add cancelled");

        def accept():
            cmd = command();
            self.app.pop_modal();
            self.status.set("Preview only: {}".format(cmd));

        buttons = HBox(
            Button("Add", on_press=accept, default=True, width=12),
            Button("Cancel", on_press=cancel, width=12),
            sizes=[14, 14],
        );
        body = VBox(
            self._field("Archive", archive),
            self._field("Format", fmt),
            self._field("Compression", compression),
            solid,
            links,
            portable,
            Label("Portable restore", style="title"),
            restore,
            preview,
            buttons,
            sizes=[1, 1, 1, 1, 1, 1, 1, 3, 3, 1],
        );
        dialog = Dialog(body, title="Add to archive", width=78, height=24, on_cancel=cancel);
        update();
        self.app.push_modal(dialog);
        return True;

    def extract_dialog(self):
        current = self.table.current_value;
        archive = Path(current) if current is not None else Path("archive.rar");
        destination = TextInput(str(self.path), width=44);
        overwrite = Choice([("Ask", "ask"), ("Overwrite", "overwrite"), ("Skip", "skip")], value="ask", width=18);
        portable = CheckBox("Restore portable links", checked=True);
        verify = CheckBox("Test archive before extraction", checked=False);
        restore = RadioGroup([
            ("Recreate symbolic links", "links"),
            ("Materialize copies", "copies"),
            ("Links, materialize on failure", "auto"),
        ], value="auto");

        def cancel():
            self.app.pop_modal();
            self.status.set("Extract cancelled");

        def accept():
            mode = {"ask": "", "overwrite": "-o+", "skip": "-o-"}[overwrite.value];
            args = ["rar", "x"];
            if mode:
                args.append(mode);
            args.extend([str(archive), destination.value]);
            self.app.pop_modal();
            self.status.set("Preview only: {}".format(" ".join(shlex.quote(item) for item in args)));

        buttons = HBox(
            Button("Extract", on_press=accept, default=True, width=12),
            Button("Cancel", on_press=cancel, width=12),
            sizes=[14, 14],
        );
        body = VBox(
            Label("Archive: {}".format(archive.name), style="title"),
            self._field("Destination", destination),
            self._field("Overwrite", overwrite),
            verify,
            portable,
            Label("Portable restore", style="title"),
            restore,
            buttons,
            sizes=[1, 1, 1, 1, 1, 1, 3, 1],
        );
        dialog = Dialog(body, title="Extract", width=74, height=19, on_cancel=cancel);
        self.app.push_modal(dialog);
        return True;

    def view(self):
        value = self.table.current_value;
        if value is None:
            return True;
        path = Path(value);
        if path.is_dir():
            self.status.set("Directory: {}".format(path));
            return True;

        def close():
            self.app.pop_modal();

        try:
            if _is_probably_text(path):
                viewer = SyntaxView.from_file(path, syntax_theme="vim", line_numbers=True);
                mode = "{} / {}".format(viewer.lexer, viewer.syntax_theme);
            else:
                viewer = HexView.from_file(path);
                mode = "hex + ASCII";
        except (OSError, UnicodeError, ValueError) as exc:
            viewer = TextView("Cannot display {}\n\n{}".format(path, exc));
            mode = "error";
        buttons = HBox(Button("Close", on_press=close, default=True, width=12), sizes=[14]);
        body = VBox(viewer, Label("Viewer: {} | arrows scroll | Shift+Left/Right page | F11 maximize/restore".format(mode), style="muted"), buttons, sizes=[None, 1, 1]);
        dialog = Dialog(body, title=path.name, width=100, height=28, on_cancel=close, maximizable=True, content_style="viewer");
        self.app.push_modal(dialog);
        return True;

    def cycle_theme(self):
        self.theme_index = (self.theme_index + 1) % len(self.themes);
        theme = self.themes[self.theme_index];
        self.app.set_theme(theme);
        self.status.set("Theme: {}".format(theme));
        return True;

    def run(self):
        return self.app.run();


def _is_probably_text(path, sample_size=8192):
    with open(path, "rb") as handle:
        data = handle.read(max(1, int(sample_size)));
    if not data:
        return True;
    if b"\x00" in data:
        return False;
    control = sum(1 for byte in data if byte < 32 and byte not in (9, 10, 12, 13));
    return control / max(1, len(data)) < 0.02;


def format_size(size):
    value = float(size);
    for suffix in ("B", "KiB", "MiB", "GiB", "TiB"):
        if value < 1024.0 or suffix == "TiB":
            if suffix == "B":
                return "{} {}".format(int(value), suffix);
            return "{:.1f} {}".format(value, suffix);
        value /= 1024.0;
    return "{} B".format(size);


def main():
    parser = argparse.ArgumentParser(description="sumTUI RAR-DOS-style filesystem browser demo");
    parser.add_argument("path", nargs="?", default=".");
    parser.add_argument("--theme", default="DOS");
    parser.add_argument("--snapshot", action="store_true");
    parser.add_argument("--snapshot-add", action="store_true");
    args = parser.parse_args();
    demo = RarBrowserDemo(args.path, args.theme);
    if args.snapshot_add:
        demo.add_dialog();
        Console(width=120, height=32).print(demo.app.root);
        return 0;
    if args.snapshot:
        Console(width=120, height=32).print(demo.root);
        return 0;
    return demo.run();


if __name__ == "__main__":
    raise SystemExit(main());
