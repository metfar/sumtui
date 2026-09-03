#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#pylint:disable=W0301

from sumui import DialogSpec as CommonDialogSpec;
from sumtui import FormFieldSpec, InputSpec, TUI_BACKEND, dialog_spec_to_common, field_spec_to_common, input_spec_to_common;
from sumtui.dialogspec import DialogSpec;


def test_tui_backend_capabilities():
    assert TUI_BACKEND.name == "tui";
    assert TUI_BACKEND.charts is True;
    assert TUI_BACKEND.terminal_cells is True;
    assert TUI_BACKEND.graphics is False;


def test_field_spec_roundtrip_to_common():
    spec = FormFieldSpec("answer", "Answer", max_length=1, confirm=True, valid_values=("S", "N"));
    common = field_spec_to_common(spec);
    assert common.name == "answer";
    assert common.confirm is True;
    assert common.valid_values == ("S", "N");


def test_input_spec_roundtrip_to_common():
    common = input_spec_to_common(InputSpec(prompt="Answer", max_length=1, confirm=True, valid_values=("S", "N")));
    assert common.prompt == "Answer";
    assert common.max_length == 1;
    assert common.confirm is True;


def test_dialog_spec_is_serializable_for_other_backends():
    local = DialogSpec(kind="form", fields=[FormFieldSpec("answer", "Answer", max_length=1, confirm=True)]);
    common = dialog_spec_to_common(local);
    assert isinstance(common, CommonDialogSpec);
    restored = CommonDialogSpec.from_json(common.to_json());
    assert restored.fields[0].name == "answer";


def test_sumtui_installs_terminal_conio_backend():
    import io;
    from sumui import conio;
    from sumtui.conio import install;
    out = io.StringIO();
    backend = install(stdin=io.StringIO("K"), stdout=out);
    assert conio.backend() is backend;
    conio.gotoxy(3, 2);
    conio.cputs("X");
    assert conio.wherex() == 4;
    assert "\x1b[2;3H" in out.getvalue();
