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
from dataclasses import dataclass, field;

from rich.segment import Segment;
from rich.style import Style;

from ..events import Key, MouseEvent;
from ._viewport import horizontal_delta, slice_segments, text_cell_length;
from .base import Widget;


@dataclass
class TreeNode:
    label: str;
    value: object = None;
    children: list = field(default_factory=list);
    expanded: bool = False;

    def add(self, node):
        self.children.append(node);
        return node;


class TreeView(Widget):
    focusable = True;

    def __init__(self, roots=None, on_change=None, on_activate=None, theme=None, select_leaves_only=False):
        super().__init__(theme=theme);
        self.roots = list(roots or []);
        self.selected = 0;
        self.offset = 0;
        self.x_offset = 0;
        self.page_size = 1;
        self.page_width = 1;
        self.content_width = 1;
        self.on_change = on_change;
        self.on_activate = on_activate;
        self.select_leaves_only = bool(select_leaves_only);
        self._normalize_selection();

    def _flatten(self):
        rows = [];
        def visit(node, depth):
            rows.append((node, depth));
            if node.expanded:
                for child in node.children:
                    visit(child, depth + 1);
        for root in self.roots:
            visit(root, 0);
        return rows;

    def set_roots(self, roots):
        self.roots = list(roots or []);
        self.selected = 0;
        self.offset = 0;
        self.x_offset = 0;
        self._normalize_selection();
        self._changed();
        return self;

    def _selectable(self, row):
        node = row[0];
        return not (self.select_leaves_only and bool(node.children));

    def _normalize_selection(self):
        rows = self._flatten();
        if not rows:
            self.selected = 0;
            return False;
        self.selected = max(0, min(int(self.selected), len(rows) - 1));
        if self._selectable(rows[self.selected]):
            return True;
        for index in range(self.selected + 1, len(rows)):
            if self._selectable(rows[index]):
                self.selected = index;
                return True;
        for index in range(self.selected - 1, -1, -1):
            if self._selectable(rows[index]):
                self.selected = index;
                return True;
        return False;

    @property
    def current(self):
        rows = self._flatten();
        return rows[self.selected][0] if rows and 0 <= self.selected < len(rows) else None;

    @property
    def max_x_offset(self):
        return max(0, int(self.content_width) - int(self.page_width));

    def _changed(self):
        if self.on_change is not None and self.current is not None:
            self.on_change(self.current);

    def _ensure_visible(self):
        rows = self._flatten();
        page = max(1, int(self.page_size));
        if self.selected < self.offset:
            self.offset = self.selected;
        elif self.selected >= self.offset + page:
            self.offset = self.selected - page + 1;
        self.offset = max(0, min(self.offset, max(0, len(rows) - page)));

    def select(self, index):
        rows = self._flatten();
        if not rows:
            self.selected = 0;
            return False;
        value = max(0, min(len(rows) - 1, int(index)));
        if not self._selectable(rows[value]):
            return False;
        old = self.selected;
        self.selected = value;
        self._ensure_visible();
        if self.selected != old:
            self._changed();
            return True;
        return False;

    def select_value(self, value):
        rows = self._flatten();
        for index, (node, _depth) in enumerate(rows):
            if node.value == value and self._selectable(rows[index]):
                self.select(index);
                return True;
        return False;

    def move(self, delta):
        rows = self._flatten();
        if not rows:
            return False;
        step = -1 if int(delta) < 0 else 1;
        remaining = max(1, abs(int(delta)));
        index = self.selected;
        moved = False;
        while remaining > 0:
            candidate = index + step;
            found = None;
            while 0 <= candidate < len(rows):
                if self._selectable(rows[candidate]):
                    found = candidate;
                    break;
                candidate += step;
            if found is None:
                break;
            index = found;
            remaining -= 1;
            moved = True;
        if moved and index != self.selected:
            self.selected = index;
            self._ensure_visible();
            self._changed();
            return True;
        return False;

    def scroll_vertical(self, delta):
        rows = self._flatten();
        old = self.offset;
        self.offset = max(0, min(max(0, len(rows) - self.page_size), self.offset + int(delta)));
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

    def _toggle_branch_at(self, index):
        rows = self._flatten();
        if not (0 <= int(index) < len(rows)):
            return False;
        node = rows[int(index)][0];
        if not node.children:
            return False;
        node.expanded = not node.expanded;
        self._normalize_selection();
        self._ensure_visible();
        return True;

    def handle_event(self, event):
        rows = self._flatten();
        if isinstance(event, MouseEvent):
            if event.action in ("scroll_up", "scroll_down"):
                amount = -3 if event.action == "scroll_up" else 3;
                if event.shift:
                    return self.scroll_horizontal(amount);
                return self.scroll_vertical(amount);
            if event.action == "press" and event.button == "left":
                if self._focus_manager is not None:
                    self._focus_manager.set(self);
                row_y = int(event.y);
                index = self.offset + row_y;
                if 0 <= row_y < self.page_size and index < len(rows):
                    node = rows[index][0];
                    if self.select_leaves_only and node.children:
                        return self._toggle_branch_at(index) or True;
                    self.select(index);
                    return True;
                return True;
            return False;
        horizontal = horizontal_delta(event, self.page_width);
        if horizontal is not None and self.select_leaves_only:
            return self.scroll_horizontal(horizontal);
        key = getattr(event, "key", "");
        if key == Key.UP:
            return self.move(-1);
        if key == Key.DOWN:
            return self.move(1);
        if key == Key.PAGE_UP:
            return self.move(-max(1, self.page_size));
        if key == Key.PAGE_DOWN:
            return self.move(max(1, self.page_size));
        if key == Key.HOME and rows:
            for index, row in enumerate(rows):
                if self._selectable(row):
                    return self.select(index) or True;
        if key == Key.END and rows:
            for index in range(len(rows) - 1, -1, -1):
                if self._selectable(rows[index]):
                    return self.select(index) or True;
        node = self.current;
        if node is None:
            return False;
        if not self.select_leaves_only and key == Key.RIGHT:
            if node.children and not node.expanded:
                node.expanded = True;
                return True;
            return self.move(1);
        if not self.select_leaves_only and key == Key.LEFT:
            if node.expanded:
                node.expanded = False;
                return True;
            current_depth = rows[self.selected][1];
            if current_depth > 0:
                for index in range(self.selected - 1, -1, -1):
                    if rows[index][1] == current_depth - 1:
                        self.selected = index;
                        self._ensure_visible();
                        self._changed();
                        return True;
        if key == Key.ENTER:
            if node.children:
                node.expanded = not node.expanded;
                self._normalize_selection();
                self._ensure_visible();
                return True;
            if self.on_activate is not None:
                self.on_activate(node);
                return True;
        return False;

    def __rich_console__(self, console, options):
        rows = self._flatten();
        height = options.height or options.max_height or console.height;
        self.page_size = max(1, int(height));
        self.page_width = max(1, int(options.max_width));
        self._normalize_selection();
        self._ensure_visible();
        rendered = [];
        for node, depth in rows:
            branch = "▼ " if node.children and node.expanded else ("▶ " if node.children else "  ");
            rendered.append("  " * depth + branch + str(node.label));
        self.content_width = max([text_cell_length(line) for line in rendered] or [1]);
        self.x_offset = max(0, min(self.x_offset, self.max_x_offset));
        visible = list(enumerate(rendered[self.offset:self.offset + self.page_size], start=self.offset));
        for line_index in range(self.page_size):
            if line_index < len(visible):
                absolute_index, line = visible[line_index];
                style_name = "selection" if self.focused else "selection_unfocused";
                style = self.theme.style(style_name) if absolute_index == self.selected else self.theme.style("text");
                pieces = slice_segments([Segment(line,Style.parse(style))],self.x_offset,self.page_width);
                used = 0;
                for piece in pieces:
                    used += piece.cell_length;
                    yield piece;
                if used < self.page_width:
                    yield Segment(" " * (self.page_width - used),Style.parse(self.theme.style("panel")));
            else:
                yield Segment(" " * self.page_width,Style.parse(self.theme.style("panel")));
            if line_index + 1 < self.page_size:
                yield Segment.line();
