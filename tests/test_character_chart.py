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

from rich.console import Console;

from sumtui.events import Key, KeyEvent, MouseEvent;
from sumtui.tools.edit import EditApp;
from sumtui.widgets import CharacterChart;


def test_character_chart_is_16_by_16_and_pages_historical_codes():
    chart=CharacterChart(26);
    assert chart.columns == 16;
    assert chart.rows == 16;
    assert chart.page_start == 0;
    assert chart.selected_character == "→";
    assert chart.handle_event(KeyEvent(Key.PAGE_DOWN));
    assert chart.selected_code == 282;
    assert chart.page_start == 256;


def test_character_chart_reserved_cells_do_not_insert():
    inserted=[];
    chart=CharacterChart(512, on_insert=lambda value, code: inserted.append((code, value)));
    assert chart.selected_character is None;
    assert not chart.insert_selected();
    assert inserted == [];
    chart.set_code(656);
    assert chart.insert_selected();
    assert inserted == [(656, "¬")];


def test_character_chart_mouse_selects_grid_cell_and_render_contains_graphics():
    chart=CharacterChart(0);
    assert chart.handle_event(MouseEvent(chart.label_width + chart.cell_width * 10 + 1, 2, button="left", action="press"));
    assert chart.selected_code == 26;
    console=Console(width=80, record=True, color_system=None);
    console.print(chart);
    output=console.export_text();
    assert "→" in output;
    assert "┼" in output;
    assert "≡" in output;


def test_sumedit_character_chart_inserts_at_editor_caret(tmp_path):
    app=EditApp(config_path=tmp_path / "edit.json");
    app.editor.set_text("A", modified=False);
    app.editor.row=0;
    app.editor.column=1;
    assert app.character_chart_dialog();
    dialog=app.app.root;
    chart=dialog.child.items[0].widget;
    chart.set_code(26);
    assert chart.insert_selected();
    assert app.editor.text == "A→";
    assert app.editor.modified;
