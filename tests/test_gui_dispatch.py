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


def test_sumedit_gui_dispatches_same_application_to_gui_backend(monkeypatch):
    calls = [];
    class FakeEditApp:
        def __init__(self, path=None, theme=None, force_binary=False):
            calls.append(("init", path, force_binary, theme));
        def run(self, backend="tui"):
            calls.append(("run", backend));
            return 0;
    monkeypatch.setattr(edit, "EditApp", FakeEditApp);
    rc = edit.main(["--gui", "--force", "--theme", "dark", "example.py"]);
    assert rc == 0;
    assert calls == [("init", "example.py", True, "dark"), ("run", "gui")];


def test_application_gui_backend_receives_same_application_instance(monkeypatch):
    from sumtui.app import Application;
    from sumtui.widgets import Label;

    received = [];
    package = types.ModuleType("sumgui");
    package.__path__ = [];
    backend = types.ModuleType("sumgui.application_backend");
    backend.run_application = lambda application: received.append(application) or 37;
    monkeypatch.setitem(sys.modules, "sumgui", package);
    monkeypatch.setitem(sys.modules, "sumgui.application_backend", backend);
    application = Application(root=Label("same application"));
    assert application.run(backend="gui") == 37;
    assert received == [application];
