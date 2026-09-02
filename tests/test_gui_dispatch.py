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

import sys;
import types;

from sumtui.tools import edit;


def test_sumedit_gui_dispatches_before_terminal_requirement(monkeypatch):
    calls = [];
    module = types.ModuleType("sumtui.tools.edit_gui");
    module.run_gui_editor = lambda path=None, force_binary=False, theme=None: calls.append((path, force_binary, theme)) or 0;
    monkeypatch.setitem(sys.modules, "sumtui.tools.edit_gui", module);
    rc = edit.main(["--gui", "--force", "--theme", "dark", "example.py"]);
    assert rc == 0;
    assert calls == [("example.py", True, "dark")];
