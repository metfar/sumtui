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


def main():
    editor = TextEditor('PRINT "Hello from TextEditor"\n', line_numbers=True);
    status = StatusBar("TextEditor demo");
    app = Application("TextEditor demo");
    bar = FunctionBar([("f10", "Quit", app.stop)]);
    bar.install(app);
    app.set_root(VBox(Panel(editor, title="demo.prg", content_style="viewer"), status, bar, sizes=[None, 1, 1]));
    app.focus.set(editor);
    return app.run();


if __name__ == "__main__":
    raise SystemExit(main());
