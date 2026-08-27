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

import sumtui.easy as st;


def build(theme="DOS"):
    st.screen("sumTUI first demo", theme=theme);
    status = st.statusbar("READY.");
    table = st.table([
        ("Name", None, 3, "left"),
        ("Size", 10, 1, "right"),
    ]);
    table.add_row(["README.md", "4 KiB"], value="README.md");
    table.add_row(["src/", "<DIR>"], value="src");
    table.add_row(["examples/", "<DIR>"], value="examples");
    table.on_change = lambda value, row: status.set("Selected: {}".format(value));
    body = st.panel(table, title="sumTUI");
    bar = st.functionbar([
        ("f1", "Help", lambda: status.set("Arrows move; F10 quits")),
        ("f10", "Quit", st.app().stop),
    ]);
    bar.install(st.app());
    st.root(st.vbox(body, bar, status, sizes=[None, 1, 1], ratios=[1, 1, 1]));
    return st.app();


def main():
    parser = argparse.ArgumentParser();
    parser.add_argument("--theme", default="DOS");
    parser.add_argument("--snapshot", action="store_true");
    args = parser.parse_args();
    app = build(args.theme);
    if args.snapshot:
        Console(width=80, height=24).print(app.root);
        return 0;
    return app.run();


if __name__ == "__main__":
    raise SystemExit(main());
