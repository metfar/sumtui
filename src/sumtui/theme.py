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
from dataclasses import dataclass, replace;


def _hex(color):
    return "#%02x%02x%02x" % tuple(color);


SPECTRUM_COLORS = [
    (0, 0, 0), (0, 0, 205), (205, 0, 0), (205, 0, 205),
    (0, 205, 0), (0, 205, 205), (205, 205, 0), (205, 205, 205),
    (22, 22, 22), (0, 0, 255), (255, 0, 0), (255, 0, 255),
    (0, 255, 0), (0, 255, 255), (255, 255, 0), (255, 255, 255),
];

C64_COLORS = [
    (0, 0, 0), (255, 255, 255), (136, 0, 0), (170, 255, 238),
    (204, 68, 204), (0, 204, 85), (0, 0, 170), (238, 238, 119),
    (221, 136, 85), (102, 68, 0), (255, 119, 119), (51, 51, 51),
    (119, 119, 119), (170, 255, 102), (0, 136, 255), (187, 187, 187),
];

MSX_COLORS = [
    (0, 0, 0), (0, 0, 0), (33, 200, 66), (94, 220, 120),
    (84, 85, 237), (125, 118, 252), (212, 82, 77), (66, 235, 245),
    (252, 85, 84), (255, 121, 120), (212, 193, 84), (230, 206, 128),
    (33, 176, 59), (201, 91, 186), (204, 204, 204), (255, 255, 255),
];

DOS_COLORS = [
    (0, 0, 0), (0, 0, 170), (0, 170, 0), (0, 170, 170),
    (170, 0, 0), (170, 0, 170), (170, 85, 0), (170, 170, 170),
    (85, 85, 85), (85, 85, 255), (85, 255, 85), (85, 255, 255),
    (255, 85, 85), (255, 85, 255), (255, 255, 85), (255, 255, 255),
];


@dataclass(frozen=True)
class Theme:
    name: str = "Dark";
    bg: tuple = (10, 30, 32);
    panel: tuple = (28, 48, 54);
    line: tuple = (55, 75, 85);
    text: tuple = (235, 245, 250);
    muted: tuple = (130, 150, 155);
    button: tuple = (140, 220, 40);
    button_alt: tuple = (60, 100, 120);
    button_text: tuple = (10, 25, 30);
    error: tuple = (255, 100, 100);
    cursor: tuple = (255, 255, 0);
    selection_bg: tuple = (60, 100, 120);
    selection_text: tuple = (255, 255, 255);
    title: tuple = (255, 255, 0);
    palette: tuple = tuple(SPECTRUM_COLORS);
    viewer_bg: tuple = (0, 0, 0);
    viewer_text: tuple = (238, 238, 238);
    command_bg: tuple = (0, 0, 0);
    command_text: tuple = (238, 238, 238);
    command_prompt: tuple = (255, 255, 85);
    style_overrides: tuple = ();

    def copy(self, **changes):
        return replace(self, **changes);

    def color(self, role):
        value = getattr(self, role);
        return _hex(value);

    def style(self, role):
        for override_role, override_style in self.style_overrides:
            if override_role == role:
                return override_style;
        if role == "screen":
            return "{} on {}".format(self.color("text"), self.color("bg"));
        if role == "panel":
            return "{} on {}".format(self.color("text"), self.color("panel"));
        if role == "border":
            return self.color("line");
        if role == "text":
            return self.color("text");
        if role == "muted":
            return self.color("muted");
        if role == "title":
            return "bold {}".format(self.color("title"));
        if role == "selection":
            return "bold {} on {}".format(self.color("selection_text"), self.color("selection_bg"));
        if role == "selection_unfocused":
            return "{} on {}".format(self.color("text"), self.color("button_alt"));
        if role == "function_key":
            return "bold {} on {}".format(self.color("button_text"), self.color("button"));
        if role == "function_label":
            return "{} on {}".format(self.color("text"), self.color("panel"));
        if role == "status":
            return "{} on {}".format(self.color("text"), self.color("button_alt"));
        if role == "error":
            return "bold {}".format(self.color("error"));
        if role == "cursor":
            return self.color("cursor");
        if role == "table_header":
            return "bold {} on {}".format(self.color("title"), self.color("panel"));
        if role == "dialog":
            return "{} on {}".format(self.color("text"), self.color("panel"));
        if role == "input":
            return "{} on {}".format(self.color("text"), self.color("panel"));
        if role == "input_focus":
            return "{} on {}".format(self.color("selection_text"), self.color("selection_bg"));
        if role == "input_border":
            return self.color("line");
        if role == "cursor_cell":
            return "bold {} on {}".format(self.color("button_text"), self.color("cursor"));
        if role == "button_control":
            return "bold {} on {}".format(self.color("button_text"), self.color("button"));
        if role == "button_focus":
            return "reverse bold {} on {}".format(self.color("button_text"), self.color("button"));
        if role == "control_focus":
            return "bold {} on {}".format(self.color("selection_text"), self.color("selection_bg"));
        if role == "disabled":
            return self.color("muted");
        if role == "progress_done":
            return self.color("button");
        if role == "progress_empty":
            return self.color("button_alt");
        if role == "slider_fill":
            return self.color("button");
        if role == "slider_empty":
            return self.color("button_alt");
        if role == "slider_handle":
            return "bold {}".format(self.color("cursor"));
        if role == "slider_handle_focus":
            return "reverse bold {}".format(self.color("cursor"));
        if role == "menu_bar":
            return "{} on {}".format(self.color("text"), self.color("button_alt"));
        if role == "menu_title":
            return "bold {} on {}".format(self.color("title"), self.color("button_alt"));
        if role == "menu_title_active":
            return "reverse bold {} on {}".format(self.color("title"), self.color("button_alt"));
        if role == "menu":
            return "{} on {}".format(self.color("text"), self.color("button_alt"));
        if role == "menu_selection":
            return "bold {} on {}".format(self.color("selection_text"), self.color("selection_bg"));
        if role == "menu_border":
            return self.color("line");
        if role == "scrollbar_track":
            return self.color("muted");
        if role == "scrollbar_thumb":
            return self.color("button");
        if role == "scrollbar_thumb_focus":
            return "reverse bold {}".format(self.color("button"));
        if role == "splitter":
            return self.color("line");
        if role == "splitter_focus":
            return "reverse bold {}".format(self.color("cursor"));
        if role == "editor_gutter":
            return "{} on {}".format(self.color("muted"), self.color("viewer_bg"));
        if role in ("editor_whitespace", "editor_space"):
            return self.color("muted");
        if role == "editor_tab":
            return "bold {}".format(self.color("title"));
        if role == "editor_eol":
            return "bold {}".format(self.color("button"));
        if role == "editor_control":
            return "bold {}".format(self.color("error"));
        if role == "syntax_keyword":
            return "bold {}".format(_hex(self.palette[11]));
        if role in ("syntax_function", "syntax_builtin"):
            return "bold {}".format(_hex(self.palette[14]));
        if role == "syntax_variable":
            return self.color("viewer_text");
        if role == "syntax_type":
            return "bold {}".format(_hex(self.palette[13]));
        if role == "syntax_string":
            return _hex(self.palette[10]);
        if role == "syntax_number":
            return _hex(self.palette[13]);
        if role == "syntax_comment":
            return "italic {}".format(self.color("muted"));
        if role == "syntax_operator":
            return "bold {}".format(self.color("viewer_text"));
        if role == "syntax_constant":
            return "bold {}".format(_hex(self.palette[14]));
        if role == "syntax_heading":
            return "bold underline {}".format(self.color("title"));
        if role == "syntax_strong":
            return "bold {}".format(self.color("viewer_text"));
        if role == "syntax_emphasis":
            return "italic {}".format(self.color("viewer_text"));
        if role == "syntax_deleted":
            return "strike {}".format(self.color("muted"));
        if role in ("syntax_tag", "syntax_markup"):
            return _hex(self.palette[11]);
        if role == "syntax_attribute":
            return _hex(self.palette[14]);
        if role == "syntax_label":
            return "bold {}".format(_hex(self.palette[13]));
        if role == "syntax_error":
            return "bold {}".format(self.color("error"));
        if role == "viewer":
            return "{} on {}".format(self.color("viewer_text"), self.color("viewer_bg"));
        if role == "command":
            return "{} on {}".format(self.color("command_text"), self.color("command_bg"));
        if role == "command_prompt":
            return "bold {} on {}".format(self.color("command_prompt"), self.color("command_bg"));
        if role == "command_echo":
            return "{} on {}".format(self.color("muted"), self.color("command_bg"));
        if role == "command_info":
            return "{} on {}".format(self.color("muted"), self.color("command_bg"));
        if role == "command_error":
            return "bold {} on {}".format(self.color("error"), self.color("command_bg"));
        if role == "command_field":
            return "{} on {}".format(self.color("selection_text"), self.color("selection_bg"));
        return self.color("text");


def make_theme(name="dark"):
    key = str(name).lower();
    if key in ("zx", "spectrum", "sinclair"):
        return Theme("ZX", (0, 0, 0), (0, 0, 90), (0, 255, 255), (255, 255, 255), (0, 205, 205), (255, 255, 0), (0, 0, 205), (0, 0, 0), (255, 80, 80), (255, 255, 0), (0, 0, 205), (255, 255, 255), (255, 255, 0), tuple(SPECTRUM_COLORS));
    if key in ("dos", "pc", "turbo"):
        return Theme("DOS", (0, 0, 0), (0, 0, 170), (170, 170, 170), (255, 255, 255), (170, 170, 170), (170, 170, 170), (0, 0, 170), (0, 0, 0), (255, 85, 85), (255, 255, 85), (0, 170, 170), (0, 0, 0), (255, 255, 85), tuple(DOS_COLORS));
    if key in ("rar", "rar-dos", "rar2"):
        return Theme("RAR", (0, 0, 170), (0, 0, 170), (170, 170, 170), (255, 255, 255), (170, 170, 170), (0, 170, 170), (0, 0, 170), (0, 0, 0), (255, 85, 85), (255, 255, 85), (0, 170, 170), (0, 0, 0), (255, 255, 85), tuple(DOS_COLORS));
    if key in ("dbase", "dbase3", "dbaseiii"):
        return Theme(name="DBASE", bg=(0, 0, 170), panel=(0, 0, 170), line=(170, 170, 170), text=(255, 255, 85), muted=(170, 170, 170), button=(170, 170, 170), button_alt=(0, 170, 170), button_text=(0, 0, 0), error=(255, 85, 85), cursor=(255, 255, 255), selection_bg=(170, 0, 0), selection_text=(255, 255, 255), title=(255, 255, 85), palette=tuple(DOS_COLORS));
    if key in ("fox", "foxpro"):
        return Theme(name="FOXPRO", bg=(0, 0, 170), panel=(0, 170, 170), line=(255, 255, 255), text=(0, 0, 0), muted=(85, 85, 85), button=(170, 170, 170), button_alt=(170, 0, 170), button_text=(0, 0, 0), error=(255, 255, 85), cursor=(255, 255, 255), selection_bg=(0, 0, 170), selection_text=(255, 255, 255), title=(255, 255, 85), palette=tuple(DOS_COLORS));
    if key in ("xbase", "sumx"):
        return Theme(name="XBASE", bg=(0, 0, 170), panel=(0, 170, 170), line=(170, 170, 170), text=(0, 0, 0), muted=(85, 85, 85), button=(170, 170, 170), button_alt=(0, 0, 170), button_text=(0, 0, 0), error=(255, 85, 85), cursor=(255, 255, 85), selection_bg=(0, 0, 170), selection_text=(255, 255, 255), title=(255, 255, 85), palette=tuple(DOS_COLORS));
    if key in ("c64", "commodore"):
        return Theme("C64", (64, 49, 141), (112, 94, 181), (170, 255, 238), (255, 255, 255), (187, 187, 187), (238, 238, 119), (0, 0, 170), (64, 49, 141), (255, 119, 119), (238, 238, 119), (170, 255, 238), (64, 49, 141), (238, 238, 119), tuple(C64_COLORS));
    if key == "msx":
        return Theme("MSX", (0, 0, 0), (33, 33, 96), (66, 235, 245), (255, 255, 255), (204, 204, 204), (94, 220, 120), (84, 85, 237), (0, 0, 0), (252, 85, 84), (255, 255, 255), (84, 85, 237), (255, 255, 255), (94, 220, 120), tuple(MSX_COLORS));
    if key in ("mc", "ralesk", "ralesk mc", "ralesk's mc", "ralesks mc"):
        # Adapted from Henrik Pauli's GPLv2+ Geany colorscheme "Ralesk's MC"
        # (Midnight Commander-like scheme).  Semantic roles are mapped rather
        # than copying Geany's lexer-specific configuration.
        overrides = (
            ("editor_gutter", "#111144 on #339933"),
            ("editor_space", "#3636a3"),
            ("editor_whitespace", "#3636a3"),
            ("editor_tab", "#3636a3"),
            ("editor_eol", "bold #c0c0c0"),
            ("editor_control", "bold #ff9999"),
            ("syntax_keyword", "bold #f4d432"),
            ("syntax_function", "#d3d7cf"),
            ("syntax_builtin", "#d3d7cf"),
            ("syntax_variable", "#c0c0c0"),
            ("syntax_type", "bold #ffffff"),
            ("syntax_string", "#33aa33"),
            ("syntax_number", "#3fcfcf"),
            ("syntax_comment", "italic #996600"),
            ("syntax_operator", "bold #ffff00"),
            ("syntax_constant", "bold #ffff00"),
            ("syntax_heading", "bold underline #f4d432"),
            ("syntax_strong", "bold #c0c0c0"),
            ("syntax_emphasis", "italic #c0c0c0"),
            ("syntax_deleted", "strike #808080"),
            ("syntax_tag", "bold #ffffff"),
            ("syntax_markup", "#f4d432"),
            ("syntax_attribute", "bold #f4d432"),
            ("syntax_label", "bold #c0c0c0"),
            ("syntax_error", "bold #ffffff on #ff0000"),
        );
        return Theme(name="Ralesk's MC", bg=(17, 17, 68), panel=(17, 17, 68), line=(51, 102, 153),
                     text=(192, 192, 192), muted=(128, 128, 128), button=(244, 212, 50),
                     button_alt=(51, 102, 153), button_text=(0, 0, 0), error=(255, 0, 0),
                     cursor=(204, 51, 255), selection_bg=(51, 102, 153), selection_text=(0, 0, 0),
                     title=(244, 212, 50), palette=tuple(DOS_COLORS), viewer_bg=(17, 17, 68),
                     viewer_text=(192, 192, 192), command_bg=(17, 17, 68), command_text=(192, 192, 192),
                     command_prompt=(244, 212, 50), style_overrides=overrides);
    if key == "light":
        return Theme("Light", (245, 245, 245), (255, 255, 255), (80, 80, 80), (20, 20, 20), (90, 90, 90), (70, 130, 220), (220, 220, 220), (255, 255, 255), (200, 40, 40), (0, 90, 180), (70, 130, 220), (255, 255, 255), (0, 90, 180), tuple(SPECTRUM_COLORS));
    return Theme("Dark", (10, 30, 32), (28, 48, 54), (55, 75, 85), (235, 245, 250), (130, 150, 155), (140, 220, 40), (60, 100, 120), (10, 25, 30), (255, 100, 100), (255, 255, 0), (60, 100, 120), (255, 255, 255), (255, 255, 0), tuple(SPECTRUM_COLORS));


THEMES = {
    "ZX": make_theme("ZX"),
    "DOS": make_theme("DOS"),
    "RAR": make_theme("RAR"),
    "DBASE": make_theme("DBASE"),
    "FOXPRO": make_theme("FOXPRO"),
    "XBASE": make_theme("XBASE"),
    "C64": make_theme("C64"),
    "MSX": make_theme("MSX"),
    "Ralesk's MC": make_theme("Ralesk's MC"),
    "Dark": make_theme("Dark"),
    "Light": make_theme("Light"),
};

DEFAULT_THEME = THEMES["Dark"];
