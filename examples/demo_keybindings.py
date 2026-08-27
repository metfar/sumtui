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
from sumtui import KeyBindingManager;

keys = KeyBindingManager();
keys.register("editor.copy", "Copy", ["Ctrl+C", "Ctrl+Insert"], context="editor");
keys.register("editor.cut", "Cut", ["Ctrl+X", "Shift+Delete"], context="editor");
keys.register("editor.paste", "Paste", ["Ctrl+V", "Shift+Insert"], context="editor");

print("Defaults:");
for name, label, bindings, context in keys.rows(contexts=["editor"]):
    print("{:<14} {:<8} {}".format(context, label, bindings));

keys.set_bindings("editor.copy", ["Alt+C"]);
print("\nAfter customization:");
print("Copy ->", keys.display("editor.copy", all_keys=True));
print("JSON-friendly overrides ->", keys.overrides());
