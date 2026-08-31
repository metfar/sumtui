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
from rich.segment import Segment;
from rich.style import Style;

from ..events import Key;
from ._viewport import horizontal_delta, slice_segments, text_cell_length;
from .base import Widget;


class TextView(Widget):
    focusable = True;

    def __init__(self, text="", on_activate=None, theme=None):
        super().__init__(theme=theme);
        self.lines = self._split_text(text);
        self.offset = 0;
        self.x_offset = 0;
        self.page_size = 1;
        self.page_width = 1;
        self.content_width = self._measure_width();
        self.on_activate = on_activate;

    @staticmethod
    def _split_text(text):
        normalized = str(text).replace("\r\n", "\n").replace("\r", "\n");
        return normalized.split("\n");

    @property
    def text(self):
        return "\n".join(self.lines);

    @property
    def max_x_offset(self):
        return max(0, self.content_width - self.page_width);

    def _measure_width(self):
        return max([text_cell_length(line.expandtabs(4)) for line in self.lines] or [0]);

    def set_text(self, text):
        self.lines = self._split_text(text);
        self.offset = min(self.offset, max(0, len(self.lines) - 1));
        self.content_width = self._measure_width();
        self.x_offset = min(self.x_offset, self.max_x_offset);
        return self;

    def append_text(self, text):
        piece = str(text).replace("\r\n", "\n").replace("\r", "\n");
        if not piece:
            return self;
        self.set_text(self.text + piece);
        self.offset = max(0, len(self.lines) - self.page_size);
        return self;

    def scroll(self, delta):
        old = self.offset;
        max_offset = max(0, len(self.lines) - self.page_size);
        self.offset = max(0, min(max_offset, self.offset + int(delta)));
        return self.offset != old;

    def scroll_horizontal(self, delta):
        old = self.x_offset;
        if delta == "start":
            self.x_offset = 0;
        elif delta == "end":
            self.x_offset = self.max_x_offset;
        else:
            self.x_offset = max(0, min(self.max_x_offset, self.x_offset + int(delta)));
        return self.x_offset != old;

    def handle_event(self, event):
        key = getattr(event, "key", "");
        horizontal = horizontal_delta(event, self.page_width);
        if horizontal is not None:
            return self.scroll_horizontal(horizontal);
        if key == Key.UP:
            return self.scroll(-1);
        if key == Key.DOWN:
            return self.scroll(1);
        if key == Key.PAGE_UP:
            return self.scroll(-self.page_size);
        if key == Key.PAGE_DOWN:
            return self.scroll(self.page_size);
        if key == Key.HOME:
            old = self.offset;
            self.offset = 0;
            return self.offset != old;
        if key == Key.END:
            old = self.offset;
            self.offset = max(0, len(self.lines) - self.page_size);
            return self.offset != old;
        if key == Key.ENTER and self.on_activate is not None:
            self.on_activate();
            return True;
        return False;

    def __rich_console__(self, console, options):
        height = options.height or options.max_height or console.height;
        self.page_size = max(1, int(height));
        self.page_width = max(1, options.max_width);
        self.content_width = self._measure_width();
        max_offset = max(0, len(self.lines) - self.page_size);
        self.offset = max(0, min(self.offset, max_offset));
        self.x_offset = max(0, min(self.x_offset, self.max_x_offset));
        visible = self.lines[self.offset:self.offset + self.page_size];
        style = Style.parse(self.theme.style("viewer"));
        for index in range(self.page_size):
            line = visible[index].expandtabs(4) if index < len(visible) else "";
            pieces = slice_segments([Segment(line, style)], self.x_offset, self.page_width);
            used = sum(piece.cell_length for piece in pieces);
            yield from pieces;
            if used < self.page_width:
                yield Segment(" " * (self.page_width - used), style);
            if index + 1 < self.page_size:
                yield Segment.line();
