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
from pathlib import Path;

ROOT = Path(__file__).resolve().parents[1];
SRC = ROOT / "src";
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC));

from rich.console import Console;

from sumtui import Application, CommandWindow, FunctionBar, Panel, StatusBar, VBox;


def build():
    app = Application("CommandWindow", theme="XBASE");
    status = StatusBar("Command window | Up/Down history | Ctrl+L clear | F10 quit");

    def submit(command, window):
        text = command.strip();
        if not text:
            return None;
        if text.upper() == "CLEAR":
            window.clear();
            return None;
        if text.startswith("?"):
            window.write("demo: {}".format(text[1:].strip()));
            return None;
        window.write("You entered: {}".format(text));
        return None;

    command = CommandWindow(on_submit=submit);
    command.write("sumTUI CommandWindow demo");
    command.write("Try: ? hello");
    bar = FunctionBar([("f1", "Help"), ("f10", "Quit", app.stop)]);
    bar.install(app);
    app.set_root(VBox(Panel(command, title="Command", content_style="command"), status, bar, sizes=[None, 1, 1]));
    app.bind("f10", app.stop);
    return app;


def main():
    app = build();
    if "--snapshot" in sys.argv:
        console = Console(width=100, height=24, force_terminal=False);
        console.print(app.root);
        return 0;
    return app.run();


if __name__ == "__main__":
    raise SystemExit(main());
