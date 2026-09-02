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
from sumtui import Application, FunctionBar, Menu, MenuBar, MenuDesktop, MenuItem, Panel, TextEditor, VBox;


def main():
    app = Application("MenuDesktop demo", theme="ZX");
    editor = TextEditor("# F9 opens the menu\nPRINT \"Hello\"\n", line_numbers=True);
    menu = None;

    def close_menu():
        app.focus.set(editor);
        app.invalidate();
        return True;

    def open_menu(index=None):
        if index is None:
            index = menu.menu_index;
        menu.open(index);
        app.focus.set(menu);
        app.invalidate();
        return True;

    menu = MenuBar([
        Menu("File", [MenuItem("Exit", app.stop, "F10")]),
        Menu("Edit", [MenuItem("Select All", editor.select_all, "Ctrl+A")]),
        Menu("Help", [MenuItem("About", lambda: True)]),
    ], on_close=close_menu);
    bar = FunctionBar([("f9", "Menu", open_menu), ("f10", "Exit", app.stop)]);
    bar.install(app);
    body = VBox(Panel(editor, title="demo.txt", content_style="viewer"), bar, sizes=[None, 1]);
    app.set_root(MenuDesktop(menu, body));
    app.focus.set(editor);
    return app.run();


if __name__ == "__main__":
    raise SystemExit(main());
