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
import sys;
from pathlib import Path as _SumTUIBootstrapPath;

_SUMTUI_SRC = _SumTUIBootstrapPath(__file__).resolve().parents[1] / "src";
if str(_SUMTUI_SRC) not in sys.path:
    sys.path.insert(0, str(_SUMTUI_SRC));

from sumtui import Application, CommandWindow, KeyEvent, TextEditor, TextView, Workspace, WorkspaceWindow;


def main():
    editor = TextEditor('print("Hello from a movable Code window")\n', line_numbers=True);
    output = TextView("Output window\n\nDrag a title to move.\nDrag the lower-right corner to resize.\nAlt+M = keyboard move; Alt+Z = keyboard resize.\nEnter accepts; Esc cancels.");
    command = CommandWindow(prompt="> ", on_submit=lambda line, view: view.write("command: " + line));

    code_window = WorkspaceWindow(editor, title="Code", name="code", left=1, top=1, width=58, height=16);
    output_window = WorkspaceWindow(output, title="Output", name="output", left=7, top=12, width=50, height=9);
    command_window = WorkspaceWindow(command, title="Command", name="command", left=48, top=3, width=34, height=10);
    workspace = Workspace(output_window, command_window, code_window);

    app = Application(title="sumTUI Workspace", mouse=True, capture_control_keys=True);
    app.set_root(workspace);
    app.bind("f6", workspace.next_window);
    app.bind("f11", workspace.toggle_maximize_active);
    app.bind("alt+m", workspace.begin_move_active);
    app.bind("alt+z", workspace.begin_resize_active);
    app.bind("ctrl+f4", workspace.close_active);
    app.bind("f10", app.stop);
    app.focus.set(editor);
    return app.run();


if __name__ == "__main__":
    raise SystemExit(main());
