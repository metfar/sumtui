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

import json;
from pathlib import Path;

import pytest;

from sumtui import theme as theme_module;
from sumtui.themeio import create_theme, delete_theme, export_theme, import_theme, read_theme, search_themes, theme_records, update_theme;


@pytest.fixture
def isolated_themes(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"));
    theme_module.refresh_user_themes();
    yield tmp_path;
    theme_module.refresh_user_themes();


def test_crud_list_search_hide_and_delete(isolated_themes):
    path = create_theme("Science Dark", base="Dark");
    assert path.exists();
    assert read_theme("Science Dark").name == "Science Dark";
    assert [item.name for item in search_themes("science")] == ["Science Dark"];
    theme_module.set_theme_hidden("Science Dark", True);
    assert "Science Dark" not in theme_module.available_theme_names();
    assert any(item.name == "Science Dark" and item.hidden for item in theme_records(include_hidden=True));
    theme_module.set_theme_hidden("Science Dark", False);
    updated = update_theme("Science Dark", title="Science Night", colors={"bg": "#101820"}, styles={"syntax_keyword": "bold #abcdef"});
    assert updated.exists();
    assert read_theme("Science Night").bg == (16, 24, 32);
    assert read_theme("Science Night").style("syntax_keyword") == "bold #abcdef";
    deleted = delete_theme("Science Night");
    assert not deleted.exists();
    assert not any(item.name == "Science Night" for item in theme_records(include_hidden=True));


def test_import_sum_json_and_export_roundtrip(isolated_themes):
    source = isolated_themes / "portable.json";
    source.write_text(json.dumps({"format": 1, "name": "Portable", "colors": {"bg": "#112233", "text": "#ddeeff"}}), encoding="utf-8");
    imported = import_theme(source, title="Portable SUM");
    assert imported.exists();
    target = isolated_themes / "exported.sumtheme.json";
    export_theme("Portable SUM", target=target, kind="sum");
    payload = json.loads(target.read_text(encoding="utf-8"));
    assert payload["name"] == "Portable SUM";
    assert payload["colors"]["bg"] == "#112233";


def test_import_gtk_kde_and_terminal(isolated_themes):
    gtk = isolated_themes / "gtk.css";
    gtk.write_text("""@define-color theme_bg_color #1e1e1e;\n@define-color theme_fg_color #f6f5f4;\n@define-color accent_bg_color #e95420;\n@define-color accent_fg_color #ffffff;\n@define-color borders #5e5c64;\n@define-color error_color #c01c28;\n""", encoding="utf-8");
    import_theme(gtk, kind="gtk", title="Yaru-ish");
    yaru = read_theme("Yaru-ish");
    assert yaru.bg == (30, 30, 30);
    assert yaru.button == (233, 84, 32);

    kde = isolated_themes / "breeze.colors";
    kde.write_text("""[General]\nName=Breeze Test\n[Colors:Window]\nBackgroundNormal=35,38,41\nForegroundNormal=239,240,241\n[Colors:View]\nBackgroundNormal=24,27,30\nForegroundNormal=239,240,241\n[Colors:Selection]\nBackgroundNormal=61,174,233\nForegroundNormal=255,255,255\n[Colors:Button]\nBackgroundNormal=49,54,59\nForegroundNormal=239,240,241\n""", encoding="utf-8");
    import_theme(kde, kind="kde");
    assert read_theme("Breeze Test").selection_bg == (61, 174, 233);

    terminal = isolated_themes / "terminal.theme";
    terminal.write_text("""[Scheme]\nName=Terminal Test\nColorForeground=#eeeeee\nColorBackground=#111111\nColorCursor=#ffcc00\nColorSelection=#334455\nColorPalette=#000000;#aa0000;#00aa00;#aaaa00;#0000aa;#aa00aa;#00aaaa;#aaaaaa\n""", encoding="utf-8");
    import_theme(terminal, kind="terminal");
    assert read_theme("Terminal Test").cursor == (255, 204, 0);


def test_export_target_formats(isolated_themes):
    create_theme("Portable", base="Dark");
    terminal = export_theme("Portable", isolated_themes / "portable.theme", kind="terminal");
    kde = export_theme("Portable", isolated_themes / "portable.colors", kind="kde");
    gtk = export_theme("Portable", isolated_themes / "PortableGtk", kind="gtk");
    assert "ColorBackground=" in terminal.read_text(encoding="utf-8");
    assert "[Colors:Window]" in kde.read_text(encoding="utf-8");
    assert (gtk / "gtk-3.0" / "gtk.css").exists();
    assert (gtk / "gtk-4.0" / "gtk.css").exists();


def test_builtin_delete_is_refused(isolated_themes):
    with pytest.raises(ValueError): delete_theme("Dark");


def test_theme_record_scope_distinguishes_user_and_imported(isolated_themes):
    create_theme("Local Theme", base="Dark");
    source = isolated_themes / "external.json";
    source.write_text(json.dumps({"format": 1, "name": "External Theme", "colors": {"bg": "#010203"}}), encoding="utf-8");
    import_theme(source, kind="sum");
    records = {item.name: item for item in theme_records(include_hidden=True)};
    assert records["Local Theme"].scope == "user";
    assert records["External Theme"].scope == "imported";


def test_sumtheme_cli_crud_search_import_export_and_hide(isolated_themes, capsys):
    from sumtui.tools.themeedit import main;
    assert main(["--create", "CLI Theme", "--base", "Dark"]) == 0;
    capsys.readouterr();
    assert main(["--update", "CLI Theme", "--set", "bg=#123456", "--title", "CLI Night"]) == 0;
    capsys.readouterr();
    assert main(["--search", "night", "--json"]) == 0;
    searched = capsys.readouterr().out;
    assert '"name": "CLI Night"' in searched;
    target = isolated_themes / "cli-night.json";
    assert main(["--export", "CLI Night", "--output", str(target)]) == 0;
    capsys.readouterr();
    assert json.loads(target.read_text(encoding="utf-8"))["colors"]["bg"] == "#123456";
    assert main(["--hide", "CLI Night"]) == 0;
    capsys.readouterr();
    assert "CLI Night" not in theme_module.available_theme_names();
    assert main(["--unhide", "CLI Night"]) == 0;
    capsys.readouterr();
    assert "CLI Night" in theme_module.available_theme_names();
    assert main(["--delete", "CLI Night"]) == 0;
    capsys.readouterr();
    assert not any(item.name == "CLI Night" for item in theme_records(include_hidden=True));


def test_import_konsole_terminal_scheme(isolated_themes):
    source = isolated_themes / "science.colorscheme";
    source.write_text("""[General]\nDescription=Science Console\n[Background]\nColor=16,24,32\n[Foreground]\nColor=230,235,240\n[Cursor]\nColor=255,180,0\n[Color0]\nColor=0,0,0\n[Color1]\nColor=170,0,0\n[Color2]\nColor=0,170,0\n[Color3]\nColor=170,170,0\n[Color4]\nColor=0,0,170\n[Color5]\nColor=170,0,170\n[Color6]\nColor=0,170,170\n[Color7]\nColor=170,170,170\n""", encoding="utf-8");
    import_theme(source, kind="terminal");
    theme = read_theme("Science Console");
    assert theme.bg == (16, 24, 32);
    assert theme.cursor == (255, 180, 0);
    assert tuple(theme.palette[2]) == (0, 170, 0);
