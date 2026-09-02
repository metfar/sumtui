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

from sumtui import Application, Button, CheckBox, Choice, Dialog, HBox, Label, ProgressBar, Slider, RadioGroup, TextInput, TextView, VBox;


def field(label, control, label_width=18):
    return HBox(Label(label), control, sizes=[label_width, None]);


def build(theme="DOS"):
    app = Application(title="sumTUI controls demo", theme=theme);
    status = TextView("Use Tab/Shift+Tab to move focus. Slider: arrows/Home/End.");
    name = TextInput("archive.rar", placeholder="archive name", width=34);
    password = TextInput("", placeholder="optional", password=True, width=34);
    compression = Choice([
        ("0 - Store", 0), ("1 - Fastest", 1), ("2 - Fast", 2),
        ("3 - Normal", 3), ("4 - Good", 4), ("5 - Maximum", 5),
    ], value=5, width=22);
    solid = CheckBox("Solid archive", checked=True);
    links = CheckBox("Preserve links (-sn)", checked=True);
    restore = RadioGroup([
        ("Recreate symbolic links", "links"),
        ("Materialize copies", "copies"),
        ("Links, materialize on failure", "auto"),
    ], value="auto");
    progress = ProgressBar(63, label="Progress", width=46);

    def slider_changed(widget, value):
        progress.set(value);
        status.set_text("Slider value: {}. ProgressBar is display-only.".format(int(value)));

    slider = Slider(0, 100, 63, step=1, on_change=slider_changed, label="Slider", width=46);

    def close():
        app.stop();

    buttons = HBox(
        Button("OK", on_press=close, default=True, width=12),
        Button("Cancel", on_press=close, width=12),
        sizes=[14, 14],
    );
    body = VBox(
        field("Archive", name),
        field("Password", password),
        field("Compression", compression),
        solid,
        links,
        Label("Restore policy", style="title"),
        restore,
        slider,
        progress,
        status,
        buttons,
        sizes=[1, 1, 1, 1, 1, 1, 3, 1, 1, 2, 1],
    );
    dialog = Dialog(body, title="sumTUI 0.2 controls", width=68, height=23, on_cancel=close);
    app.set_root(dialog);
    return app;


def main():
    parser = argparse.ArgumentParser(description="sumTUI form controls demo");
    parser.add_argument("--theme", default="DOS");
    parser.add_argument("--snapshot", action="store_true");
    args = parser.parse_args();
    app = build(args.theme);
    if args.snapshot:
        Console(width=90, height=28).print(app.root);
        return 0;
    return app.run();


if __name__ == "__main__":
    raise SystemExit(main());
