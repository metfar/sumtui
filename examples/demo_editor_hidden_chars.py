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

_ROOT = Path(__file__).resolve().parents[1];
_SRC = _ROOT / "src";
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC));

from sumtui import Application, FunctionBar, Panel, TextEditor, VBox;


def main():
    text = "spaces here\tTAB\x00NUL\nsecond line\n";
    app = Application(title="Hidden characters", theme="DOS");
    editor = TextEditor(text, line_numbers=True);
    editor.show_spaces = True;
    editor.show_tabs = True;
    editor.show_line_endings = True;
    editor.show_control_chars = True;
    editor.line_end_marker = "↵";
    bar = FunctionBar([("f10", "Exit", app.stop)]);
    bar.install(app);
    app.set_root(VBox(Panel(editor, title="Hidden characters"), bar, sizes=[None, 1]));
    app.focus.set(editor);
    return app.run();


if __name__ == "__main__":
    raise SystemExit(main());
