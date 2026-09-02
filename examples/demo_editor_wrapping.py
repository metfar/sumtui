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


TEXT = """This is one logical line. With line_wrapping=-1 it follows the visible editor width without inserting line endings or modifying the text buffer. Resize the terminal to see it adapt automatically.\n\nThe legacy fixed preset is 78 columns: 80 columns minus one border cell on each side.""";


def main():
    editor = TextEditor(TEXT, line_numbers=True, line_wrapping=-1);
    app = Application(root=Panel(editor, title="Automatic line wrapping", content_style="viewer"), title="sumTUI wrapping demo", theme="ZX", capture_control_keys=True);
    app.focus.set(editor);
    return app.run();


if __name__ == "__main__":
    raise SystemExit(main());
