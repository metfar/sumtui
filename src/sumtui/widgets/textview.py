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
from rich.console import Group;
from rich.panel import Panel as RichPanel;
from rich.segment import Segment;
from rich.style import Style;
from rich.text import Text;

from ..events import Key, MouseEvent;
from ..clipboard import clipboard, trim_selected_text;
from ._viewport import horizontal_delta, line_cell_length, slice_segments, text_cell_length;
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
        self.cursor = (0, 0);
        self.selection_anchor = None;
        self.selection_cursor = None;
        self.mouse_selecting = False;
        self.context_menu_open = False;
        self.context_menu_index = 0;
        self.context_menu_x = 0;
        self.context_menu_y = 0;
        self._context_menu_bounds = None;

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

    def _clamp_position(self, line, column):
        if not self.lines:
            return (0, 0);
        line = max(0, min(len(self.lines) - 1, int(line)));
        column = max(0, min(len(self.lines[line]), int(column)));
        return (line, column);

    def _event_position(self, event):
        return self._clamp_position(self.offset + int(event.y), self.x_offset + int(event.x));

    @property
    def has_selection(self):
        return self.selection_anchor is not None and self.selection_cursor is not None and self.selection_anchor != self.selection_cursor;

    def clear_selection(self):
        self.selection_anchor = None;
        self.selection_cursor = None;
        return True;

    def select_all(self):
        last_line = max(0, len(self.lines) - 1);
        self.selection_anchor = (0, 0);
        self.selection_cursor = (last_line, len(self.lines[last_line]) if self.lines else 0);
        self.cursor = self.selection_cursor;
        return True;

    def _selection_bounds(self):
        if not self.has_selection:
            return None;
        start, end = sorted((self.selection_anchor, self.selection_cursor));
        return start, end;

    @property
    def selected_text(self):
        bounds = self._selection_bounds();
        if bounds is None:
            return "";
        (line1, col1), (line2, col2) = bounds;
        if line1 == line2:
            return self.lines[line1][col1:col2];
        parts = [self.lines[line1][col1:]];
        parts.extend(self.lines[index] for index in range(line1 + 1, line2));
        parts.append(self.lines[line2][:col2]);
        return "\n".join(parts);

    def copy_selection(self):
        if not self.has_selection:
            return False;
        clipboard.copy_text(trim_selected_text(self.selected_text));
        return True;

    def _context_menu_items(self):
        return [
            ("Copy", "Ctrl+C / Ctrl+Ins", self.has_selection, self.copy_selection),
            ("Select all", "Ctrl+A", True, self.select_all),
        ];

    def _first_context_menu_index(self):
        for index, (_label, _shortcut, enabled, _action) in enumerate(self._context_menu_items()):
            if enabled:
                return index;
        return 0;

    def open_context_menu(self, x=0, y=0):
        self.context_menu_open = True;
        self.context_menu_x = max(0, int(x));
        self.context_menu_y = max(0, int(y));
        self.context_menu_index = self._first_context_menu_index();
        self._context_menu_bounds = None;
        return True;

    def close_context_menu(self):
        changed = self.context_menu_open;
        self.context_menu_open = False;
        self._context_menu_bounds = None;
        return changed;

    def _move_context_menu(self, delta):
        items = self._context_menu_items();
        choices = [index for index, (_label, _shortcut, enabled, _action) in enumerate(items) if enabled];
        if not choices:
            return False;
        try:
            position = choices.index(self.context_menu_index);
        except ValueError:
            position = 0;
        self.context_menu_index = choices[(position + int(delta)) % len(choices)];
        return True;

    def _activate_context_menu(self, index=None):
        items = self._context_menu_items();
        target = self.context_menu_index if index is None else int(index);
        if target < 0 or target >= len(items):
            return False;
        _label, _shortcut, enabled, action = items[target];
        if not enabled:
            return False;
        result = bool(action());
        self.close_context_menu();
        return result;

    def _context_menu_hit(self, event):
        if self._context_menu_bounds is None:
            return None;
        left, top, width, height = self._context_menu_bounds;
        x = int(event.x);
        y = int(event.y);
        if not (left <= x < left + width and top <= y < top + height):
            return None;
        row = y - top - 1;
        items = self._context_menu_items();
        if 0 <= row < len(items):
            return row;
        return -1;

    def _context_menu_renderable(self):
        rows = [];
        items = self._context_menu_items();
        content_width = max([len(label) + len(shortcut) + 3 for label, shortcut, _enabled, _action in items] or [12]);
        for index, (label, shortcut, enabled, _action) in enumerate(items):
            gap = max(1, content_width - len(label) - len(shortcut));
            row = Text(label + (" " * gap) + shortcut);
            if not enabled:
                row.stylize(self.theme.style("disabled"));
            elif index == self.context_menu_index:
                row.stylize(self.theme.style("menu_selection"));
            else:
                row.stylize(self.theme.style("menu"));
            rows.append(row);
        return RichPanel(
            Group(*rows),
            padding=(0, 0),
            border_style=self.theme.style("menu_border"),
            style=self.theme.style("menu"),
            width=content_width + 2,
        );

    @staticmethod
    def _overlay_line(base_line, overlay_line, left, width):
        left = max(0, int(left));
        width = max(1, int(width));
        overlay_width = min(width - left, line_cell_length(overlay_line));
        if overlay_width <= 0:
            return base_line;
        prefix = slice_segments(base_line, 0, left);
        middle = slice_segments(overlay_line, 0, overlay_width);
        suffix_start = left + overlay_width;
        suffix = slice_segments(base_line, suffix_start, max(0, width - suffix_start));
        return prefix + middle + suffix;

    def _move_cursor(self, line_delta=0, column_delta=0, select=False):
        line, column = self.cursor;
        if line_delta:
            line = max(0, min(len(self.lines) - 1, line + int(line_delta)));
            column = min(column, len(self.lines[line]));
        if column_delta:
            column += int(column_delta);
            while column < 0 and line > 0:
                line -= 1; column = len(self.lines[line]);
            while line < len(self.lines) - 1 and column > len(self.lines[line]):
                column -= len(self.lines[line]) + 1; line += 1;
            column = max(0, min(len(self.lines[line]), column));
        new = (line, column);
        if select:
            if self.selection_anchor is None:
                self.selection_anchor = self.cursor;
            self.selection_cursor = new;
        else:
            self.selection_anchor = None; self.selection_cursor = None;
        self.cursor = new;
        return True;

    def handle_event(self, event):
        if isinstance(event, MouseEvent):
            if event.action == "press" and event.button == "right":
                if self._focus_manager is not None:
                    self._focus_manager.set(self);
                self.mouse_selecting = False;
                return self.open_context_menu(event.x, event.y);
            if self.context_menu_open:
                if event.action in ("scroll_up", "scroll_down"):
                    return self._move_context_menu(-1 if event.action == "scroll_up" else 1);
                if event.action == "press" and event.button == "left":
                    hit = self._context_menu_hit(event);
                    if hit is None:
                        self.close_context_menu();
                        return True;
                    if hit >= 0:
                        self.context_menu_index = hit;
                        return self._activate_context_menu(hit);
                    return True;
                if event.action in ("move", "drag"):
                    hit = self._context_menu_hit(event);
                    if hit is not None and hit >= 0:
                        items = self._context_menu_items();
                        if items[hit][2]:
                            self.context_menu_index = hit;
                    return True;
                return True;
            if event.button == "left" and event.action == "press":
                self.close_context_menu();
                pos = self._event_position(event);
                self.cursor = pos;
                self.selection_anchor = pos;
                self.selection_cursor = pos;
                self.mouse_selecting = True;
                return True;
            if self.mouse_selecting and event.action in ("move", "drag"):
                self.cursor = self._event_position(event);
                self.selection_cursor = self.cursor;
                return True;
            if event.button == "left" and event.action == "release":
                if self.mouse_selecting:
                    self.cursor = self._event_position(event);
                    self.selection_cursor = self.cursor;
                    self.mouse_selecting = False;
                    return True;
            if event.button == "wheel" and event.action == "scroll_up":
                return self.scroll(-3);
            if event.button == "wheel" and event.action == "scroll_down":
                return self.scroll(3);
        key = getattr(event, "key", "");
        ctrl = bool(getattr(event, "ctrl", False));
        shift = bool(getattr(event, "shift", False));
        if ctrl and key in ("c", Key.INSERT):
            self.close_context_menu();
            return self.copy_selection();
        if ctrl and key == "a":
            self.close_context_menu();
            return self.select_all();
        if self.context_menu_open:
            if key == Key.ESCAPE:
                return self.close_context_menu();
            if key == Key.UP:
                return self._move_context_menu(-1);
            if key == Key.DOWN:
                return self._move_context_menu(1);
            if key == Key.ENTER:
                return self._activate_context_menu();
            return True;
        if shift and key == Key.LEFT:
            return self._move_cursor(column_delta=-1, select=True);
        if shift and key == Key.RIGHT:
            return self._move_cursor(column_delta=1, select=True);
        if shift and key == Key.UP:
            return self._move_cursor(line_delta=-1, select=True);
        if shift and key == Key.DOWN:
            return self._move_cursor(line_delta=1, select=True);
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
        selection_style = Style.parse(self.theme.style("selection"));
        bounds = self._selection_bounds();
        output_lines = [];
        for index in range(self.page_size):
            absolute_line = self.offset + index;
            raw_line = visible[index] if index < len(visible) else "";
            line = raw_line.expandtabs(4);
            segments = [Segment(line, style)];
            if bounds is not None and absolute_line < len(self.lines):
                (line1, col1), (line2, col2) = bounds;
                if line1 <= absolute_line <= line2:
                    start = col1 if absolute_line == line1 else 0;
                    end = col2 if absolute_line == line2 else len(raw_line);
                    start = max(0, min(len(line), start));
                    end = max(start, min(len(line), end));
                    segments = [];
                    if start: segments.append(Segment(line[:start], style));
                    if end > start: segments.append(Segment(line[start:end], selection_style));
                    if end < len(line): segments.append(Segment(line[end:], style));
            pieces = slice_segments(segments, self.x_offset, self.page_width);
            used = sum(piece.cell_length for piece in pieces);
            output_line = list(pieces);
            if used < self.page_width:
                output_line.append(Segment(" " * (self.page_width - used), style));
            output_lines.append(output_line);
        if self.context_menu_open and output_lines:
            menu = self._context_menu_renderable();
            requested_width = max(1, int(getattr(menu, "width", 1) or 1));
            menu_width = min(self.page_width, requested_width);
            menu_lines = console.render_lines(menu, options.update(width=menu_width), pad=True, new_lines=False);
            menu_height = min(len(output_lines), len(menu_lines));
            left = max(0, min(self.context_menu_x, max(0, self.page_width - menu_width)));
            top = max(0, min(self.context_menu_y, max(0, len(output_lines) - menu_height)));
            self._context_menu_bounds = (left, top, menu_width, menu_height);
            for row in range(menu_height):
                output_lines[top + row] = self._overlay_line(output_lines[top + row], menu_lines[row], left, self.page_width);
        else:
            self._context_menu_bounds = None;
        for index, output_line in enumerate(output_lines):
            yield from output_line;
            if index + 1 < len(output_lines):
                yield Segment.line();
