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
from sumtui import Application, FunctionBar, Panel, StatusBar, TextEditor, VBox;

editor = TextEditor("Select text and use Ctrl+C. Type something and use Ctrl+Z.\n", line_numbers=True);
status = StatusBar("Ctrl+C = Copy   Ctrl+Z = Undo   Ctrl+Y = Redo   F10 = Exit");
bar = FunctionBar([("f10", "Exit", lambda: app.stop())]);
app = Application(title="Captured control-key demo", theme="ZX", capture_control_keys=True);
app.unbind("ctrl+c");
app.set_root(VBox(Panel(editor, title="Editor"), status, bar, sizes=[None, 1, 1]));
bar.install(app);
app.focus.set(editor);
raise SystemExit(app.run());
