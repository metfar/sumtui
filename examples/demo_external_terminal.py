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
import os;
import shutil;
import subprocess;
import sys;
from pathlib import Path as _SumTUIBootstrapPath;

_SUMTUI_SRC = _SumTUIBootstrapPath(__file__).resolve().parents[1] / "src";
if str(_SUMTUI_SRC) not in sys.path:
    sys.path.insert(0, str(_SUMTUI_SRC));

from sumtui import Application, Button, Label, VBox;


def main():
    app = Application("sumTUI external terminal", mouse=True);
    shell = os.environ.get("SHELL") or shutil.which("sh") or "/bin/sh";
    def open_shell():
        return app.run_external(lambda: subprocess.call([shell]));
    root = VBox(
        Label("Open a real interactive shell; type exit to return."),
        Button("Open shell", width=24, height=3, on_press=open_shell),
    );
    app.set_root(root);
    app.bind("f10", app.stop);
    return app.run();


if __name__ == "__main__":
    raise SystemExit(main());
