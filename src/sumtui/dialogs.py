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
from dataclasses import dataclass;
from pathlib import Path;
import sys;
import time;

from rich.console import Console;

from .app import Application;
from .prompt import ACCEPTED, CANCELLED, TIMED_OUT, TERMINAL_ERROR, InputResult, InputSpec, controlling_terminal, read_input;
from .widgets import Button, CheckBox, Dialog, DirectoryDialog, FileDialog, HBox, Label, ListView, MarkdownView, RadioGroup, TextView, VBox;


@dataclass
class DialogResult:
    value: object = "";
    status: int = ACCEPTED;

    @property
    def accepted(self):
        return self.status == ACCEPTED;

    @property
    def cancelled(self):
        return self.status == CANCELLED;

    @property
    def timed_out(self):
        return self.status == TIMED_OUT;


def _dialog_size(text="", width=None, height=None, minimum_width=32, minimum_height=8):
    lines = str(text or "").splitlines() or [""];
    content_width = max([len(line) for line in lines] or [0]);
    resolved_width = max(int(minimum_width), int(width or min(92, max(36, content_width + 8))));
    resolved_height = max(int(minimum_height), int(height or min(28, max(8, len(lines) + 7))));
    return resolved_width, resolved_height;


def _run_application(app, reader):
    previous_stdin = sys.stdin;
    sys.stdin = reader;
    try:
        app.run();
    finally:
        sys.stdin = previous_stdin;


def _install_timeout(app, state, timeout, default_status=TIMED_OUT):
    if timeout is None:
        return None;
    deadline = time.monotonic() + max(0.0, float(timeout));
    def tick():
        if time.monotonic() < deadline:
            return False;
        if not state.get("done", False):
            state["status"] = int(default_status);
            state["done"] = True;
            app.stop();
        return True;
    app.add_idle(tick);
    return tick;


def show_message(text, title="Message", kind="info", theme="DOS", width=None, height=None,
                 timeout=None, ok_label="OK", cancel_label="Cancel", question=False):
    kind = str(kind or "info").strip().lower();
    prefixes = {"info": "", "warning": "Warning: ", "error": "Error: ", "question": ""};
    message = prefixes.get(kind, "") + str(text or "");
    resolved_width, resolved_height = _dialog_size(message, width=width, height=height);
    with controlling_terminal() as terminal:
        reader, writer = terminal;
        console = Console(file=writer, force_terminal=True);
        app = Application("sumdialog", theme=theme, console=console);
        state = {"status": CANCELLED, "done": False};
        def finish(status):
            if state["done"]:
                return True;
            state["status"] = int(status);
            state["done"] = True;
            app.stop();
            return True;
        if question:
            buttons = HBox(
                Button(ok_label or "Yes", on_press=lambda: finish(ACCEPTED), default=True),
                Button(cancel_label or "No", on_press=lambda: finish(CANCELLED)),
                ratios=[1, 1],
            );
        else:
            buttons = HBox(Button(ok_label or "OK", on_press=lambda: finish(ACCEPTED), default=True), ratios=[1]);
        body = VBox(Label(message), buttons, sizes=[None, 1]);
        root = Dialog(body, title=title, width=resolved_width, height=resolved_height, on_cancel=lambda: finish(CANCELLED), shadow=True);
        app.set_root(root);
        app.focus.set(buttons.children()[0]);
        _install_timeout(app, state, timeout);
        _run_application(app, reader);
        return DialogResult("", state["status"]);


def ask_question(text, title="Question", theme="DOS", width=None, height=None, timeout=None,
                 yes_label="Yes", no_label="No"):
    return show_message(
        text=text,
        title=title,
        kind="question",
        theme=theme,
        width=width,
        height=height,
        timeout=timeout,
        ok_label=yes_label,
        cancel_label=no_label,
        question=True,
    );


def read_entry(text="", title="Input", theme="DOS", width=None, height=1, picture="", overflow=False,
               hidden=False, mask=None, keys="", case_sensitive=False, default="", timeout=None):
    spec = InputSpec(
        prompt=text,
        width=width,
        height=height,
        picture=picture,
        overflow=overflow,
        hidden=hidden,
        mask=mask,
        keys=keys,
        case_sensitive=case_sensitive,
        default=default,
        timeout=timeout,
        dialog=True,
        title=title,
        theme=theme,
    ).normalize();
    result = read_input(spec);
    return DialogResult(result.value, result.status);


def choose_file(path=".", title="Open file", theme="DOS", width=76, height=24, directory=False):
    with controlling_terminal() as terminal:
        reader, writer = terminal;
        console = Console(file=writer, force_terminal=True);
        app = Application("sumdialog", theme=theme, console=console);
        state = {"status": CANCELLED, "value": "", "done": False};
        def finish(status, value=""):
            if state["done"]:
                return True;
            state["status"] = int(status);
            state["value"] = str(value or "");
            state["done"] = True;
            app.stop();
            return True;
        def accepted(value):
            return finish(ACCEPTED, str(Path(value)));
        def cancelled():
            return finish(CANCELLED, "");
        dialog_type = DirectoryDialog if directory else FileDialog;
        root = dialog_type(path=path, title=title, on_accept=accepted, on_cancel=cancelled, width=width, height=height, theme=theme);
        app.set_root(root);
        app.focus.set(root.table);
        _run_application(app, reader);
        return DialogResult(state["value"], state["status"]);


def choose_list(items, title="Select", text="", theme="DOS", width=60, height=18, default=None, timeout=None):
    values = [str(item) for item in list(items or [])];
    with controlling_terminal() as terminal:
        reader, writer = terminal;
        console = Console(file=writer, force_terminal=True);
        app = Application("sumdialog", theme=theme, console=console);
        state = {"status": CANCELLED, "value": "", "done": False};
        listing = None;
        def finish(status, value=""):
            if state["done"]:
                return True;
            state["status"] = int(status);
            state["value"] = str(value or "");
            state["done"] = True;
            app.stop();
            return True;
        def accept_current(*_args):
            value = listing.current_value if listing is not None else "";
            return finish(ACCEPTED, value);
        listing = ListView(values, title="Value", on_activate=lambda *_args: accept_current());
        if default in values:
            listing.select(values.index(default));
        buttons = HBox(Button("OK", on_press=accept_current, default=True), Button("Cancel", on_press=lambda: finish(CANCELLED, "")), ratios=[1, 1]);
        if text:
            content = VBox(Label(text), listing, buttons, sizes=[1, None, 1]);
        else:
            content = VBox(listing, buttons, sizes=[None, 1]);
        root = Dialog(content, title=title, width=width, height=height, on_cancel=lambda: finish(CANCELLED, ""), shadow=True);
        app.set_root(root);
        app.focus.set(listing);
        _install_timeout(app, state, timeout);
        _run_application(app, reader);
        return DialogResult(state["value"], state["status"]);


def choose_radio(items, title="Select", text="", theme="DOS", width=60, height=None, default=None, timeout=None):
    values = [str(item) for item in list(items or [])];
    selected = default if default in values else (values[0] if values else "");
    with controlling_terminal() as terminal:
        reader, writer = terminal;
        console = Console(file=writer, force_terminal=True);
        app = Application("sumdialog", theme=theme, console=console);
        state = {"status": CANCELLED, "value": "", "done": False};
        group = RadioGroup(values, value=selected);
        def finish(status):
            if state["done"]:
                return True;
            state["status"] = int(status);
            state["value"] = str(group.value or "") if status == ACCEPTED else "";
            state["done"] = True;
            app.stop();
            return True;
        buttons = HBox(Button("OK", on_press=lambda: finish(ACCEPTED), default=True), Button("Cancel", on_press=lambda: finish(CANCELLED)), ratios=[1, 1]);
        resolved_width, resolved_height = _dialog_size(text, width=width, height=height or max(10, len(values) + 8));
        if text:
            content = VBox(Label(text), group, buttons, sizes=[1, None, 1]);
        else:
            content = VBox(group, buttons, sizes=[None, 1]);
        root = Dialog(content, title=title, width=resolved_width, height=resolved_height, on_cancel=lambda: finish(CANCELLED), shadow=True);
        app.set_root(root);
        if group.buttons:
            app.focus.set(next((button for button in group.buttons if button.checked), group.buttons[0]));
        _install_timeout(app, state, timeout);
        _run_application(app, reader);
        return DialogResult(state["value"], state["status"]);


def choose_checklist(items, title="Select", text="", theme="DOS", width=60, height=None, selected=None,
                     separator="\n", timeout=None):
    values = [str(item) for item in list(items or [])];
    selected_values = set(str(item) for item in list(selected or []));
    with controlling_terminal() as terminal:
        reader, writer = terminal;
        console = Console(file=writer, force_terminal=True);
        app = Application("sumdialog", theme=theme, console=console);
        state = {"status": CANCELLED, "value": "", "done": False};
        boxes = [CheckBox(value, checked=(value in selected_values)) for value in values];
        def finish(status):
            if state["done"]:
                return True;
            state["status"] = int(status);
            if status == ACCEPTED:
                state["value"] = str(separator).join(box.label for box in boxes if box.checked);
            else:
                state["value"] = "";
            state["done"] = True;
            app.stop();
            return True;
        buttons = HBox(Button("OK", on_press=lambda: finish(ACCEPTED), default=True), Button("Cancel", on_press=lambda: finish(CANCELLED)), ratios=[1, 1]);
        if text:
            content = VBox(Label(text), *boxes, buttons, sizes=[1] + [1] * len(boxes) + [1]);
        else:
            content = VBox(*boxes, buttons, sizes=[1] * len(boxes) + [1]);
        resolved_width, resolved_height = _dialog_size(text, width=width, height=height or max(10, len(values) + 8));
        root = Dialog(content, title=title, width=resolved_width, height=resolved_height, on_cancel=lambda: finish(CANCELLED), shadow=True);
        app.set_root(root);
        if boxes:
            app.focus.set(boxes[0]);
        else:
            app.focus.set(buttons.children()[0]);
        _install_timeout(app, state, timeout);
        _run_application(app, reader);
        return DialogResult(state["value"], state["status"]);


def show_text(text, title="Text", theme="DOS", width=80, height=24, markdown=False):
    with controlling_terminal() as terminal:
        reader, writer = terminal;
        console = Console(file=writer, force_terminal=True);
        app = Application("sumdialog", theme=theme, console=console);
        state = {"status": CANCELLED, "done": False};
        def finish(status):
            if state["done"]:
                return True;
            state["status"] = int(status);
            state["done"] = True;
            app.stop();
            return True;
        viewer = MarkdownView(text) if markdown else TextView(text);
        buttons = HBox(Button("Close", on_press=lambda: finish(ACCEPTED), default=True), ratios=[1]);
        body = VBox(viewer, buttons, sizes=[None, 1]);
        root = Dialog(body, title=title, width=width, height=height, on_cancel=lambda: finish(CANCELLED), shadow=True);
        app.set_root(root);
        app.focus.set(viewer);
        _run_application(app, reader);
        return DialogResult("", state["status"]);
