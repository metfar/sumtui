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
from sumtui import Application, Panel, TextEditor;


SOURCE = '''# Ralesk's MC semantic colours
import sys

class Demo:
    def hello(self, name):
        value = 42
        if value >= 10:
            print("Hello", name)
''';


def main():
    editor = TextEditor(SOURCE, syntax_highlighting=True, syntax_language="python", line_wrapping=-1);
    app = Application(title="Ralesk's MC", root=Panel(editor, title=" Python / Ralesk's MC "), theme="Ralesk's MC", capture_control_keys=True);
    app.focus.set(editor);
    app.bind("f10", lambda: app.stop());
    app.run();
    return 0;


if __name__ == "__main__":
    raise SystemExit(main());
