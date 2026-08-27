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
from rich.markdown import Markdown;
from rich.segment import Segment;
from rich.style import Style;

from ..events import Key;
from ._viewport import horizontal_delta, line_cell_length, slice_segments, text_cell_length;
from .base import Widget;


class MarkdownView(Widget):
    focusable = True;

    def __init__(self, markdown="", code_theme="vim", wrap=True, theme=None):
        super().__init__(theme=theme);
        self.markdown = str(markdown);
        self.code_theme = str(code_theme or "vim");
        self.wrap = bool(wrap);
        self.offset = 0;
        self.x_offset = 0;
        self.page_size = 1;
        self.page_width = 1;
        self.content_width = 1;

    @property
    def max_x_offset(self):
        return max(0, self.content_width - self.page_width);

    def set_text(self, markdown):
        self.markdown = str(markdown);
        self.offset = 0;
        self.x_offset = 0;
        return self;

    def _renderable(self):
        return Markdown(
            self.markdown,
            code_theme=self.code_theme,
            inline_code_theme=self.code_theme,
        );

    def _preferred_width(self, viewport_width):
        if self.wrap:
            return max(20, int(viewport_width));
        source_width = max([text_cell_length(line.expandtabs(4)) for line in self.markdown.splitlines()] or [20]);
        return max(20, int(viewport_width), source_width + 4);

    def _lines(self, console, width):
        segments = console.render(self._renderable(), console.options.update(width=max(20, int(width))));
        return list(Segment.split_lines(segments)) or [[]];

    def scroll(self, delta, line_count):
        old = self.offset;
        self.offset = max(0, min(max(0, int(line_count) - self.page_size), self.offset + int(delta)));
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
        horizontal = horizontal_delta(event, self.page_width);
        if horizontal is not None and not self.wrap:
            return self.scroll_horizontal(horizontal);
        self._pending_key = getattr(event, "key", "");
        return self._pending_key in (Key.UP, Key.DOWN, Key.PAGE_UP, Key.PAGE_DOWN, Key.HOME, Key.END);

    def __rich_console__(self, console, options):
        viewport_width = max(1, options.max_width);
        height = options.height or options.max_height or console.height;
        self.page_width = viewport_width;
        self.page_size = max(1, int(height));
        lines = self._lines(console, self._preferred_width(viewport_width));
        self.content_width = max([line_cell_length(line) for line in lines] or [viewport_width]);
        key = getattr(self, "_pending_key", "");
        if key == Key.UP:
            self.scroll(-1, len(lines));
        elif key == Key.DOWN:
            self.scroll(1, len(lines));
        elif key == Key.PAGE_UP:
            self.scroll(-self.page_size, len(lines));
        elif key == Key.PAGE_DOWN:
            self.scroll(self.page_size, len(lines));
        elif key == Key.HOME:
            self.offset = 0;
        elif key == Key.END:
            self.offset = max(0, len(lines) - self.page_size);
        self._pending_key = "";
        self.offset = max(0, min(self.offset, max(0, len(lines) - self.page_size)));
        self.x_offset = max(0, min(self.x_offset, self.max_x_offset));
        visible = lines[self.offset:self.offset + self.page_size];
        background = Style(bgcolor=self.theme.color("viewer_bg"));
        for line_index in range(self.page_size):
            line = visible[line_index] if line_index < len(visible) else [];
            pieces = slice_segments(line, self.x_offset, viewport_width);
            used = 0;
            for segment in pieces:
                used += segment.cell_length;
                yield Segment(segment.text, (segment.style or Style()) + background, segment.control);
            if used < viewport_width:
                yield Segment(" " * (viewport_width - used), background);
            if line_index + 1 < self.page_size:
                yield Segment.line();
